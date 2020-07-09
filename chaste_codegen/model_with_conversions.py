import logging
import time

import cellmlmanip
from cellmlmanip.model import DataDirectionFlow, Model
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

import chaste_codegen as cg
from chaste_codegen._rdf import (get_variables_transitively, PYCMLMETA, OXMETA)

from ._math_functions import MATH_FUNC_SYMPY_MAPPING



def load_model(model_file):
    model = cellmlmanip.load_model(model_file)
    add_conversions(model)
    return model

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


def add_conversions(model):
    # Logging
    model.logger = logging.getLogger(__name__)#or use cellmlmanips?
    model.logger.setLevel(logging.INFO)

    # Add units needed for conversions
    model.conversion_units, model.stimulus_units = add_units(model)

    # Add conversion rules for working with stimulus current & amplitude
    add_conversion_rules(model)
        
    model.time_variable = get_time_variable(model)
    model.state_vars = set(model.get_state_variables(sort=False))
        
    model.membrane_voltage_var = get_membrane_voltage_var(model)
    model.cytosolic_calcium_concentration_var = get_cytosolic_calcium_concentration_var(model)

    # Conversions of V or cytosolic_calcium_concentration could have changed the state vars so a new call is needed
    model.state_vars = set(model.get_state_variables(sort=False))
    
    # Retrieve stimulus current parameters so we can exclude these from modifiers etc.
    model.membrane_stimulus_current_orig = get_membrane_stimulus_current(model)

    model.modifiable_parameters = get_modifiable_parameters(model)
    
    model.membrane_capacitance = get_membrane_capacitance(model)
    model.stimulus_params, model.stimulus_equations = get_stimulus(model)

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

def add_units(model):
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

def add_conversion_rules(model):
    """ Add conversion rules to allow converting stimulus current & amplitude"""
    # add 'HeartConfig::Instance()->GetCapacitance' call for use in conversions
    model._config_capacitance_call = Function('HeartConfig::Instance()->GetCapacitance', real=True)()

    model.units.add_conversion_rule(
        from_unit=model.conversion_units.get_unit('uA_per_uF'), to_unit=model.conversion_units.get_unit('uA_per_cm2'),
        rule=lambda ureg,
        rhs: rhs * model.conversion_units.Quantity(model._config_capacitance_call,
                                       model.conversion_units.get_unit('uA_per_cm2') / model.conversion_units.get_unit('uA_per_uF')))

    model.units.add_conversion_rule(
        from_unit=model.conversion_units.get_unit('uA'), to_unit=model.conversion_units.get_unit('uA_per_cm2'),
        rule=lambda ureg,
        rhs: rhs * model.conversion_units.Quantity(model._config_capacitance_call / model.membrane_capacitance,
                                       model.conversion_units.get_unit('uA_per_cm2') / model.conversion_units.get_unit('uA')))

def get_time_variable(model):
    """ Get the variable representing time (the free variable) and convert to milliseconds"""
    time_variable = model.get_free_variable()
    # Annotate as quantity and not modifiable parameter
    set_is_metadata(model, time_variable, 'derived-quantity')
    try:
        # If the variable is in units that can be converted to millisecond, perform conversion
        return model.convert_variable(model.get_free_variable(), model.conversion_units.get_unit('millisecond'), DataDirectionFlow.INPUT)
    except DimensionalityError:
        warning = 'Incorrect definition of time variable: time needs to be dimensionally equivalent to second'
        raise ValueError(warning)

def get_membrane_voltage_var(model):
    """ Find the membrane_voltage variable"""
    try:
        # Get and convert V
        voltage = model.get_variable_by_ontology_term((OXMETA, 'membrane_voltage'))
        voltage = model.convert_variable(voltage, model.conversion_units.get_unit('millivolt'), DataDirectionFlow.INPUT)
    except KeyError:
        raise KeyError('Voltage not tagged in the model!')
    except DimensionalityError:
        raise ValueError('Incorrect definition of membrane_voltage variable: '
                         'units of membrane_voltage need to be dimensionally equivalent to Volt')
    annotate_if_not_statevar(model, voltage)  # If V is not state var annotate as appropriate.
    return voltage

def get_cytosolic_calcium_concentration_var(model):
    """ Find the cytosolic_calcium_concentration variable if it exists"""
    try:
        calcium = model.get_variable_by_ontology_term((OXMETA, 'cytosolic_calcium_concentration'))
        calcium = model.convert_variable(calcium, model.conversion_units.get_unit('millimolar'), DataDirectionFlow.INPUT)
    except KeyError:
        model.logger.info(model.name + ' has no cytosolic_calcium_concentration')
        return None
    except DimensionalityError:
        pass  # Conversion is optional
    annotate_if_not_statevar(model, calcium)  # If not state var annotate as appropriate
    return calcium

def get_membrane_stimulus_current(model):
    """ Find the membrane_stimulus_current variable if it exists"""
    #model.is_self_excitatory = False
    try:  # get membrane_stimulus_current
        return model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current'))
    except KeyError:
        model.logger.info(model.name + ' has no membrane_stimulus_current')
        #model.is_self_excitatory = \
            #next(model.get_rdf_annotations(subject=model.rdf_identity,
                 #predicate=(PYCMLMETA, 'is-self-excitatory'), object_='yes'), None) is not None
        #print(model.is_self_excitatory)
        #assert False
        return None

def get_modifiable_parameters(model):
    """ Get all modifiable parameters, either annotated as such or with other annotation.

    Stimulus currents are ignored and the result is sorted by display name"""
    tagged = set(model.get_variables_by_rdf((PYCMLMETA, 'modifiable-parameter'), 'yes', sort=False))
    annotated = set(filter(lambda q: model.has_ontology_annotation(q, OXMETA), model.variables()))

    return (tagged | annotated) -\
        set(model.get_derived_quantities(sort=False) + [model.time_variable]) - model.state_vars


def get_membrane_capacitance(model):
    """ Find membrane_capacitance if the model has it and convert it to uF if necessary"""
    try:
        capacitance = model.get_variable_by_ontology_term((OXMETA, 'membrane_capacitance'))
        return model.convert_variable(capacitance, model.conversion_units.get_unit('uF'), DataDirectionFlow.OUTPUT)
    except KeyError:
        model.logger.info(model.name + ' has no capacitance tagged')
        return None
    except DimensionalityError:
        model.logger.info(model.name + ' has capacitance in incompatible units, skipping')
        return None


def get_stimulus(model):
    """ Store the stimulus currents in the model"""
    stim_params_orig, stim_params = set(), set()
    try:  # Get required stimulus parameters
        ampl = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_amplitude'))
        duration = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_duration'))
        period = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_period'))

        stim_params_orig.update((ampl, duration, period))  # originals ones
        stim_params.add(model.convert_variable(ampl, model.conversion_units.get_unit('uA_per_cm2'), DataDirectionFlow.INPUT))
        stim_params.add(model.convert_variable(duration, model.conversion_units.get_unit('millisecond'), DataDirectionFlow.INPUT))
        stim_params.add(model.convert_variable(period, model.conversion_units.get_unit('millisecond'), DataDirectionFlow.INPUT))
    except KeyError:
        model.logger.info(model.name + 'has no default stimulus params tagged')
        return set(), []
    except TypeError as e:
        if str(e) == "unsupported operand type(s) for /: 'HeartConfig::Instance()->GetCapacitance' and 'NoneType'":
            raise KeyError("Membrane capacitance is required to be able to apply conversion to stimulus current!")

    try:  # Get optional stimulus parameter
        offset = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_offset'))
        if offset is not None:
            stim_params_orig.add(offset)  # originals one
            stim_params.add(model.convert_variable(offset, model.conversion_units.get_unit('millisecond'), DataDirectionFlow.INPUT))
    except KeyError:
        pass  # Optional Parameter

    try:  # Get optional stimulus parameter
        end = model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current_end'))
        if end is not None:
            stim_params_orig.add(end)  # originals one
            stim_params.add(model.convert_variable(end, model.conversion_units.get_unit('millisecond'), DataDirectionFlow.INPUT))
    except KeyError:
        pass  # Optional Parameter

    return_stim_eqs = get_equations_for(model, stim_params, filter_modifiable_parameters_lhs=False)
    return stim_params | stim_params_orig, return_stim_eqs