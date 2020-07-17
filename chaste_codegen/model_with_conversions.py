import logging

import cellmlmanip
from cellmlmanip.model import DataDirectionFlow
from cellmlmanip.rdf import create_rdf_node
from cellmlmanip.units import UnitStore
from pint import DimensionalityError
from sympy import (
    Derivative,
    Eq,
    Expr,
    Float,
    Function,
    Pow,
    Wild,
    log,
    simplify,
    sympify,
)
from sympy.codegen.cfunctions import log10
from sympy.codegen.rewriting import ReplaceOptim, log1p_opt, optimize

from chaste_codegen import LOGGER
from chaste_codegen._rdf import OXMETA, PYCMLMETA, get_variables_transitively

from ._math_functions import MATH_FUNC_SYMPY_MAPPING


MEMBRANE_VOLTAGE_INDEX = 0  # default index for voltage in state vector
CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX = 1  # default index for cytosolic calcium concentration in state vector

# Optimisations to be applied to equations
_V, _W = Wild('V'), Wild('W')
# log(x)/log(10) --> log10(x)
_LOG10_OPT = ReplaceOptim(_V * log(_W) / log(10), _V * log10(_W), cost_function=lambda expr: expr.count(
    lambda e: (  # cost function prevents turning log(x) into log(10) * log10(x) as we want normal log in that case
        e.is_Pow and e.exp.is_negative  # division
        or (isinstance(e, (log, log10)) and not e.args[0].is_number))))
# For P^n make sure n is passed as int if it is actually a whole number
_POW_OPT = ReplaceOptim(lambda p: p.is_Pow and (isinstance(p.exp, Float) or isinstance(p.exp, float))
                        and float(p.exp).is_integer(),
                        lambda p: Pow(p.base, int(float(p.exp))))


def load_model_with_conversions(model_file, use_modifiers=True, quiet=False):
    if quiet:
        LOGGER.setLevel(logging.ERROR)
    model = cellmlmanip.load_model(model_file)
    add_conversions(model, use_modifiers)
    return model


def add_conversions(model, use_modifiers=True):
    # Add units needed for conversions
    model.conversion_units, model.stimulus_units = _add_units(model)

    # Add conversion rules for working with stimulus current & amplitude
    _add_conversion_rules(model)

    model.time_variable = _get_time_variable(model)
    model.state_vars = set(model.get_state_variables(sort=False))
    model.membrane_voltage_var = _get_membrane_voltage_var(model)
    model.cytosolic_calcium_concentration_var = _get_cytosolic_calcium_concentration_var(model)

    # Conversions of V or cytosolic_calcium_concentration could have changed the state vars so a new call is needed
    model.state_vars = set(model.get_state_variables(sort=False))

    # Retrieve stimulus current parameters so we can exclude these from modifiers etc.
    model.membrane_stimulus_current_orig = _get_membrane_stimulus_current(model)
    model.modifiable_parameters = _get_modifiable_parameters(model)
    model.membrane_capacitance = _get_membrane_capacitance(model)
    model.stimulus_params, model.stimulus_equations = _get_stimulus(model)

    # update modifiable_parameters remove stimulus params
    # couldn't do this earlier as we didn't have stimulus params yet
    # but we need  pre- conversion modifiers as the conversion moves metadata
    model.modifiable_parameters -= model.stimulus_params

    # From now on conversion with missing capacitance is allowed
    if model.membrane_capacitance is None:
        model.membrane_capacitance = 1

    model.modifiers, model.modifier_names = _get_modifiers(model) if use_modifiers else ()

    model.y_derivatives = _get_y_derivatives(model)
    # Convert currents
    model.membrane_stimulus_current_converted, model.stimulus_units = _convert_membrane_stimulus_current(model)
    _convert_other_currents(model)

    # Get derivs and eqs
    model.ionic_derivs = _get_ionic_derivs(model)
    model.i_ionic_lhs, model.equations_for_ionic_vars = _get_equations_for_ionic_vars(model)
    model.extended_equations_for_ionic_vars = _get_extended_equations_for_ionic_vars(model)
    model.derivative_equations = _get_derivative_equations(model)


def set_is_metadata(model, variable, metadata_tag, ontology=PYCMLMETA):
    """Adds the metadata tag in the given ontology with the value object_value"""
    model.add_cmeta_id(variable)
    model.rdf.add((variable.rdf_identity, create_rdf_node((ontology, metadata_tag)), create_rdf_node('yes')))


def annotate_if_not_statevar(model, var):
    """ If it is not a state var, annotates var as modifiable parameter or derived quantity as appropriate"""
    if var not in model.state_vars:
        if model.is_constant(var):
            set_is_metadata(model, var, 'modifiable-parameter')
        else:  # not constant
            set_is_metadata(model, var, 'derived-quantity')


def get_equations_for(model, variables, recurse=True, filter_modifiable_parameters_lhs=True, optimise=True):
    """Returns equations excluding once where lhs is a modifiable parameter

    :param variables: the variables to get defining equations for.
    :param recurse: recurse and get defining equations for all variables in the defining equations?
    :param filter_modifiable_parameters_lhs: remove equations where the lhs is a modifiable paramater?
    :return: List of equations defining vars,
            with optimisations around using log10, and powers of whole numbers applied to rhs
            as well as modifiable parameters filtered out is required.
    """
    equations = [eq for eq in model.get_equations_for(variables, recurse=recurse)
                 if not filter_modifiable_parameters_lhs or eq.lhs not in model.modifiable_parameters]
    if optimise:
        for i, eq in enumerate(equations):
            optims = tuple()
            if len(eq.rhs.atoms(log)) > 0:
                optims += (_LOG10_OPT, log1p_opt)
            if len(eq.rhs.atoms(Pow)) > 0:
                optims += (_POW_OPT, )
            if len(optims) > 0:
                equations[i] = Eq(eq.lhs, optimize(eq.rhs, optims))
    return equations


def state_var_key_order(model, var):
    """Returns a key to order state variables in the same way as pycml does"""
    if isinstance(var, Derivative):
        var = var.args[0]
    if var == model.membrane_voltage_var:
        return MEMBRANE_VOLTAGE_INDEX
    elif var == model.cytosolic_calcium_concentration_var and\
            model.cytosolic_calcium_concentration_var.units.dimensionality == \
            model.conversion_units.get_unit('millimolar').dimensionality:
        return CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX
    else:
        order = var.order_added
        if order >= MEMBRANE_VOLTAGE_INDEX:
            order += MEMBRANE_VOLTAGE_INDEX
        if order >= CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX:
            order += CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX
        return order


def _add_units(model):
    """ Add needed units to the model to allow converting time, voltage and calcium in specific units
        as well as units for converting membrane_stimulus_current, capacitance etc.

        :return: unit_store, (default units stimulus could have)"""
    units = UnitStore(model.units)

    uA_per_cm2 = units.add_unit('uA_per_cm2', 'ampere / 1e6 / (meter * 1e-2)**2')
    uA_per_uF = units.add_unit('uA_per_uF', 'ampere / 1e6 / (farad * 1e-6)')
    uA = units.add_unit('uA', 'ampere / 1e6')
    units.add_unit('uF', 'farad / 1e6')
    units.add_unit('millisecond', 'second / 1e3')
    units.add_unit('millimolar', 'mole / 1e3 / litre')
    units.add_unit('millivolt', 'volt / 1e3')

    return units, (uA_per_cm2, uA, uA_per_uF)


def _add_conversion_rules(model):
    """ Add conversion rules to allow converting stimulus current & amplitude"""
    # add 'HeartConfig::Instance()->GetCapacitance' call for use in conversions
    model._config_capacitance_call = Function('HeartConfig::Instance()->GetCapacitance', real=True)()

    model.units.add_conversion_rule(
        from_unit=model.conversion_units.get_unit('uA_per_uF'), to_unit=model.conversion_units.get_unit('uA_per_cm2'),
        rule=lambda ureg,
        rhs: rhs * model.conversion_units.Quantity(model._config_capacitance_call,
                                                   model.conversion_units.get_unit('uA_per_cm2') /
                                                   model.conversion_units.get_unit('uA_per_uF')))

    model.units.add_conversion_rule(
        from_unit=model.conversion_units.get_unit('uA'), to_unit=model.conversion_units.get_unit('uA_per_cm2'),
        rule=lambda ureg,
        rhs: rhs * model.conversion_units.Quantity(model._config_capacitance_call / model.membrane_capacitance,
                                                   model.conversion_units.get_unit('uA_per_cm2') /
                                                   model.conversion_units.get_unit('uA')))


def _get_time_variable(model):
    """ Get the variable representing time (the free variable) and convert to milliseconds"""
    time_variable = model.get_free_variable()
    # Annotate as quantity and not modifiable parameter
    set_is_metadata(model, time_variable, 'derived-quantity')
    try:
        # If the variable is in units that can be converted to millisecond, perform conversion
        return model.convert_variable(model.get_free_variable(), model.conversion_units.get_unit('millisecond'),
                                      DataDirectionFlow.INPUT)
    except DimensionalityError:
        warning = 'Incorrect definition of time variable: time needs to be dimensionally equivalent to second'
        raise ValueError(warning)


def _get_membrane_voltage_var(model):
    """ Find the membrane_voltage variable"""
    try:
        # Get and convert V
        voltage = model.get_variable_by_ontology_term((OXMETA, 'membrane_voltage'))
        voltage = model.convert_variable(voltage, model.conversion_units.get_unit('millivolt'),
                                         DataDirectionFlow.INPUT)
    except KeyError:
        raise KeyError('Voltage not tagged in the model!')
    except DimensionalityError:
        raise ValueError('Incorrect definition of membrane_voltage variable: '
                         'units of membrane_voltage need to be dimensionally equivalent to Volt')
    annotate_if_not_statevar(model, voltage)  # If V is not state var annotate as appropriate.
    return voltage


def _get_cytosolic_calcium_concentration_var(model):
    """ Find the cytosolic_calcium_concentration variable if it exists"""
    try:
        calcium = model.get_variable_by_ontology_term((OXMETA, 'cytosolic_calcium_concentration'))
        calcium = model.convert_variable(calcium, model.conversion_units.get_unit('millimolar'),
                                         DataDirectionFlow.INPUT)
    except KeyError:
        LOGGER.info(model.name + ' has no cytosolic_calcium_concentration')
        return None
    except DimensionalityError:
        pass  # Conversion is optional
    annotate_if_not_statevar(model, calcium)  # If not state var annotate as appropriate
    return calcium


def _get_membrane_stimulus_current(model):
    """ Find the membrane_stimulus_current variable if it exists"""
    try:  # get membrane_stimulus_current
        return model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current'))
    except KeyError:
        LOGGER.info(model.name + ' has no membrane_stimulus_current')
        return None


def _get_modifiable_parameters(model):
    """ Get all modifiable parameters, either annotated as such or with other annotation.

    Stimulus currents are ignored and the result is sorted by display name"""
    tagged = set(model.get_variables_by_rdf((PYCMLMETA, 'modifiable-parameter'), 'yes', sort=False))
    annotated = set(filter(lambda q: model.has_ontology_annotation(q, OXMETA), model.variables()))

    return (tagged | annotated) -\
        set(model.get_derived_quantities(sort=False) + [model.time_variable]) - model.state_vars


def _get_membrane_capacitance(model):
    """ Find membrane_capacitance if the model has it and convert it to uF if necessary"""
    try:
        capacitance = model.get_variable_by_ontology_term((OXMETA, 'membrane_capacitance'))
        return model.convert_variable(capacitance, model.conversion_units.get_unit('uF'), DataDirectionFlow.OUTPUT)
    except KeyError:
        LOGGER.info(model.name + ' has no capacitance tagged')
        return None
    except DimensionalityError:
        LOGGER.info(model.name + ' has capacitance in incompatible units, skipping')
        return None


def _get_stimulus(model):
    """ Store the stimulus currents in the model"""
    stim_params_orig, stim_params = set(), set()
    try:  # Get required stimulus parameters
        ampl = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_amplitude'))
        duration = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_duration'))
        period = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_period'))

        stim_params_orig.update((ampl, duration, period))  # originals ones
        stim_params.add(model.convert_variable(ampl, model.conversion_units.get_unit('uA_per_cm2'),
                                               DataDirectionFlow.INPUT))
        stim_params.add(model.convert_variable(duration, model.conversion_units.get_unit('millisecond'),
                                               DataDirectionFlow.INPUT))
        stim_params.add(model.convert_variable(period, model.conversion_units.get_unit('millisecond'),
                                               DataDirectionFlow.INPUT))
    except KeyError:
        LOGGER.info(model.name + ' has no default stimulus params tagged')
        return set(), []
    except TypeError as e:
        if str(e) == "unsupported operand type(s) for /: 'HeartConfig::Instance()->GetCapacitance' and 'NoneType'":
            raise KeyError("Membrane capacitance is required to be able to apply conversion to stimulus current!")

    try:  # Get optional stimulus parameter
        offset = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_offset'))
        if offset is not None:
            stim_params_orig.add(offset)  # originals one
            stim_params.add(model.convert_variable(offset, model.conversion_units.get_unit('millisecond'),
                            DataDirectionFlow.INPUT))
    except KeyError:
        pass  # Optional Parameter

    try:  # Get optional stimulus parameter
        end = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_end'))
        if end is not None:
            stim_params_orig.add(end)  # originals one
            stim_params.add(model.convert_variable(end, model.conversion_units.get_unit('millisecond'),
                            DataDirectionFlow.INPUT))
    except KeyError:
        pass  # Optional Parameter

    return_stim_eqs = get_equations_for(model, stim_params, filter_modifiable_parameters_lhs=False)
    return stim_params | stim_params_orig, return_stim_eqs


def _get_modifiers(model):
    """ Get the variables that can be used as modifiers.

    These are all variables with annotation (including state vars)
    except the stimulus current and time (the free variable)
    """
    modifiers = set()
    modifiers = set(filter(lambda m: m not in (model.membrane_stimulus_current_orig, model.time_variable) and
                           model.has_ontology_annotation(m, OXMETA), model.variables()))
    modifiers -= model.stimulus_params
    return tuple(sorted(modifiers, key=lambda m: model.get_display_name(m, OXMETA))), \
        {m: model.get_display_name(m, OXMETA) for m in modifiers}


def _get_y_derivatives(model):
    """ Get derivatives for state variables"""
    derivatives = model.get_derivatives(sort=False)
    derivatives.sort(key=lambda state_var: state_var_key_order(model, state_var))
    return derivatives


def _convert_membrane_stimulus_current(model):
    """ Find the membrane_stimulus_current and convert it to uA_per_cm2, using GetIntracellularAreaStimulus"""
    if model.membrane_stimulus_current_orig is None:
        return None, model.stimulus_units
    # get derivative equations
    d_eqs = get_equations_for(model, model.y_derivatives, filter_modifiable_parameters_lhs=False, optimise=False)

    # get dv/dt
    deriv_eq_only = filter(lambda eq: isinstance(eq.lhs, Derivative) and
                           eq.lhs.args[0] == model.membrane_voltage_var, d_eqs)
    dvdt = next(deriv_eq_only, None)
    assert dvdt is not None and next(deriv_eq_only, None) is None, 'Expecting exactly 1 dv/dt equation'

    # Assign temporary values to variables in order to check the stimulus sign.
    # This will process defining expressions in a breadth first search until the stimulus
    # current is found.  Each variable that doesn't have its definitions processed will
    # be given a value as follows:
    # - stimulus current = 1
    # - other currents = 0
    # - other variables = 1
    # The stimulus current is then negated from the sign expected by Chaste if evaluating
    # dV/dt gives a positive value.
    negate_stimulus = False
    voltage_rhs = dvdt.rhs
    variables = list(voltage_rhs.free_symbols)
    for variable in variables:
        if model.membrane_stimulus_current_orig != variable:
            if model.membrane_stimulus_current_orig.units.dimensionality == variable.units.dimensionality:
                if isinstance(voltage_rhs, Expr):
                    voltage_rhs = voltage_rhs.xreplace({variable: 0.0})  # other currents = 0
            else:
                # For other variables see if we need to follow their definitions first
                rhs = next(map(lambda eq: eq.rhs, filter(lambda eq: eq.lhs == variable, d_eqs)), None)

                if rhs is not None and not isinstance(rhs, Float):
                    voltage_rhs = voltage_rhs.xreplace({variable: rhs})  # Update definition
                    variables.extend(rhs.free_symbols)
                else:
                    if isinstance(voltage_rhs, Expr):
                        voltage_rhs = voltage_rhs.xreplace({variable: 1.0})  # other variables = 1
    if isinstance(voltage_rhs, Expr):
        voltage_rhs = voltage_rhs.xreplace({model.membrane_stimulus_current_orig: 1.0})  # stimulus = 1
        # plug in math functions for sign calculation
        voltage_rhs = voltage_rhs.subs(MATH_FUNC_SYMPY_MAPPING)
    negate_stimulus = voltage_rhs > 0.0

    membrane_stimulus_current_converted = model.convert_variable(model.membrane_stimulus_current_orig,
                                                                 model.conversion_units.get_unit('uA_per_cm2'),
                                                                 DataDirectionFlow.INPUT)

    # Replace stim = ... with stim = +/-GetIntracellularAreaStimulus(t)
    GetIntracellularAreaStimulus = Function('GetIntracellularAreaStimulus', real=True)(model.time_variable)
    if negate_stimulus:
        GetIntracellularAreaStimulus = -GetIntracellularAreaStimulus

    # Get stimulus defining equation
    eq = model.get_definition(membrane_stimulus_current_converted)
    model.remove_equation(eq)
    model.add_equation(Eq(membrane_stimulus_current_converted, GetIntracellularAreaStimulus))

    # Stimulus current can't be a modifiable parameter
    model.modifiable_parameters -= set((model.membrane_stimulus_current_orig, membrane_stimulus_current_converted))
    # Annotate the converted stimulus current as derived quantity
    set_is_metadata(model, membrane_stimulus_current_converted, 'derived-quantity')
    return membrane_stimulus_current_converted, \
        (model.membrane_stimulus_current_orig.units, membrane_stimulus_current_converted.units)


def _convert_other_currents(model):
    """ Try to convert other currents (apart from stimulus current) to uA_per_cm2

    Currents are terms tagged with a term that is both `CellMembraneCurrentRelated` and an `IonicCurrent`
    according to the OXMETA ontology (https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#).
    Only variables in units convertible to Chaste's current units are converted,
    so currents in unusual units (e.g. dimensionless) are skipped.
    """
    current_related = set(get_variables_transitively(model,
                          (OXMETA, 'CellMembraneCurrentRelated')))
    all_currents = set(get_variables_transitively(model, (OXMETA, 'IonicCurrent')))
    currents = current_related.intersection(all_currents) - set([model.membrane_stimulus_current_converted])
    for current in currents:
        try:
            model.convert_variable(current, model.conversion_units.get_unit('uA_per_cm2'), DataDirectionFlow.OUTPUT)
        except DimensionalityError:
            pass  # conversion is optional, convert only if possible


def _get_ionic_derivs(model):
    """ Getting the derivatives that define V (model.membrane_voltage_var)"""
    # use the RHS of the ODE defining V
    return set(filter(lambda x: x.args[0] == model.membrane_voltage_var, model.get_derivatives(sort=False)))


def _get_equations_for_ionic_vars(model):
    """ Get the equations defining the ionic derivatives"""
    # figure out the currents (by finding variables with the same units as the stimulus)
    # Only equations with the same (lhs) units as the STIMULUS_CURRENT are kept.
    # Also exclude membrane_stimulus_current variable itself, and default_stimulus equations (if model has those)
    # Manually recurse down the equation graph (bfs style) if no currents are found

    # If we don't have a stimulus_current we look for a set of default unit dimensions
    equations_for_ionic_vars = []
    for unit in model.stimulus_units:
        if len(equations_for_ionic_vars) > 0:
            break
        equations_for_ionic_vars, equations, old_equations = [], model.ionic_derivs, None
        while len(equations_for_ionic_vars) == 0 and old_equations != equations:
            old_equations = equations
            equations = get_equations_for(model, equations, recurse=False, filter_modifiable_parameters_lhs=False,
                                          optimise=False)
            equations_for_ionic_vars = [eq for eq in equations
                                        if (eq.lhs != model.membrane_stimulus_current_orig
                                            and eq.lhs not in model.stimulus_params)
                                        and model.units.evaluate_units(eq.lhs).dimensionality ==
                                        unit.dimensionality
                                        and eq.lhs not in model.ionic_derivs]

            equations = [eq.lhs for eq in equations]

    # create the const double var_chaste_interface__i_ionic = .. equation
    i_ionic_lhs = model.add_variable(name='_i_ionic', units=model.conversion_units.get_unit('uA_per_cm2'))
    i_ionic_rhs = sympify(0.0, evaluate=False)

    # convert and sum up all lhs for all ionic equations
    for var in reversed(equations_for_ionic_vars):
        factor = model.units.get_conversion_factor(from_unit=model.units.evaluate_units(var.lhs),
                                                   to_unit=model.conversion_units.get_unit('uA_per_cm2'))
        i_ionic_rhs += factor * var.lhs
    i_ionic_rhs = simplify(i_ionic_rhs)  # clean up equation

    i_ionic_eq = Eq(i_ionic_lhs, i_ionic_rhs)
    model.add_equation(i_ionic_eq)
    equations_for_ionic_vars.append(i_ionic_eq)

    # Update equations to include i_ionic_eq & defining eqs, set stimulus current to 0
    return i_ionic_lhs, equations_for_ionic_vars


def _get_extended_equations_for_ionic_vars(model):
    """ Get the equations defining the ionic derivatives and all dependant equations"""
    # Update equations to include i_ionic_eq & defining eqs, set stimulus current to 0
    return [eq if eq.lhs != model.membrane_stimulus_current_orig else Eq(eq.lhs, 0.0)
            for eq in get_equations_for(model, [eq.lhs for eq in model.equations_for_ionic_vars])
            if eq.lhs != model.membrane_stimulus_current_converted]


def _get_derivative_equations(model):
    """ Get equations defining the derivatives including V (model.membrane_voltage_var)"""
    # Remove equations where lhs is a modifiable parameter or default stimulus
    return [eq for eq in get_equations_for(model, model.y_derivatives)
            if eq.lhs not in model.stimulus_params]
