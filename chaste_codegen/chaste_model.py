import logging
import time

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

import chaste_codegen as cg
from chaste_codegen._rdf import get_variables_transitively

from ._math_functions import MATH_FUNC_SYMPY_MAPPING


class ChasteModel(object):
    """ Holds information about a cellml model for which chaste code is to be generated.

    It also holds relevant formatted equations and derivatives.
    Please Note: this calass cannot generate chaste code directly, instead use a subclass of the model type
    """
    _MEMBRANE_VOLTAGE_INDEX = 0  # default index for voltage in state vector
    _CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX = 1  # default index for cytosolic calcium concentration in state vector
    _OXMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#'  # oxford metadata uri prefix
    _PYCMLMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/pycml#'  # pycml metadata uri

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

    def __init__(self, model, file_name, **kwargs):
        """ Initialise a ChasteModel instance
        Arguments

        ``model``
            A :class:`cellmlmanip.Model` object.
        ``file_name``
            The name you want to give your generated files WITHOUT the .hpp and .cpp extension
            (e.g. aslanidi_model_2009 leads to aslanidi_model_2009.cpp and aslanidi_model_2009.hpp)
        """

        # Logging
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        # Store default options
        self.file_name = file_name
        self.generated_hpp = ''
        self.generated_cpp = ''
        self._hpp_template = ''
        self._cpp_template = ''

        self._is_self_excitatory = False
        self.use_modifiers = kwargs.get('use_modifiers', False)

        # Store parameters for future reference
        self._model = model

        # Add units needed for conversions
        self.units, self._stimulus_units = self._add_units()

        # Add conversion rules for working with stimulus current & amplitude
        self._add_conversion_rules()

        # in_interface may have already been set by child class
        self._in_interface = set()

        self._time_variable = self._get_time_variable()
        self._state_vars = set(self._model.get_state_variables())

        self._membrane_voltage_var = self._get_membrane_voltage_var()
        self._cytosolic_calcium_concentration_var = self._get_cytosolic_calcium_concentration_var()

        # Sort the state variables, in similar order to pycml to prevent breaking existing code.
        # V and cytosolic_calcium_concentration need to be set for the sorting
        # Conversions of V or cytosolic_calcium_concentration could have changed the state vars so a new call is needed
        self._state_vars = set(self._model.get_state_variables())

        self._in_interface.update(self._state_vars)

        # Retrieve stimulus current parameters so we can exclude these from modifiers etc.
        self._membrane_stimulus_current_orig = self._get_membrane_stimulus_current()

        self._modifiable_parameters = set(self._get_modifiable_parameters())
        self._in_interface.add(self._time_variable)

        self._membrane_capacitance = self._get_membrane_capacitance()
        self._stimulus_params, self._stimulus_equations = self._get_stimulus()

        # update modifiable_parameters and modifiers to remove stimulus params
        # couldn't do this earlier as we didn't have stimulus params yet
        # but we need  pre- conversion modifiers / params as the conversion moves metadata
        self._modifiers_set = self._get_modifiers()
        self._modifiers = sorted(self._modifiers_set, key=lambda m: self._model.get_display_name(m, self._OXMETA))
        self._modifiable_parameters = self._modifiable_parameters - self._stimulus_params

        self._y_derivatives = self._get_y_derivatives()

        # get capacitance and update stimulus current
        self._in_interface.update(self._stimulus_params)
        self._membrane_stimulus_current_converted, self._stimulus_units = self._convert_membrane_stimulus_current()
        # If we don't have a capacitance, update capacitance to allow converting i_ionic
        if self._membrane_capacitance is None:
            self._membrane_capacitance = 1

        self._convert_other_currents()

        self._ionic_derivs = self._get_ionic_derivs()
        self._equations_for_ionic_vars = self._get_equations_for_ionic_vars()
        self._extended_equations_for_ionic_vars = self._get_extended_equations_for_ionic_vars()

        self._derivative_equations = self._get_derivative_equations()
        self._derivative_eqs_excl_voltage = self._get_derivative_eqs_excl_voltage()
        self._derivative_eqs_voltage = self._get_derivative_eqs_voltage()

        self._derived_quant = self._get_derived_quant()
        self._derived_quant_eqs = self._get_derived_quant_eqs()

        # Sort before printing
        # the state variables, in similar order to pycml to prevent breaking existing code.
        self._state_vars = sorted(self._model.get_state_variables(),
                                  key=lambda state_var: self._state_var_key_order(state_var))
        self._modifiable_parameters = sorted(self._modifiable_parameters,
                                             key=lambda v: self._model.get_display_name(v, self._OXMETA))
        self._modifiable_parameter_lookup = {p: str(i) for i, p in enumerate(self._modifiable_parameters)}

        # Printing
        self._add_printers()
        self._formatted_state_vars, self._use_verify_state_variables = self._format_state_variables()

        # dict of variables to pass to the jinja2 templates
        self._vars_for_template = \
            {'base_class': '',
             # indicate how to declare state vars and values
             'vector_decl': 'std::vector<double>&',
             'converter_version': cg.__version__,
             'model_name': self._model.name,
             'file_name': self.file_name,
             'class_name': kwargs.get('class_name', 'ModelFromCellMl'),
             'header_ext': kwargs.get('header_ext', '.hpp'),
             'dynamically_loadable': kwargs.get('dynamically_loadable', False),
             'modifiers': self._format_modifiers(),
             'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
             'use_get_intracellular_calcium_concentration':
                 self._cytosolic_calcium_concentration_var in self._state_vars,
             'membrane_voltage_index': self._MEMBRANE_VOLTAGE_INDEX,
             'cytosolic_calcium_concentration_index':
                 self._state_vars.index(self._cytosolic_calcium_concentration_var)
                 if self._cytosolic_calcium_concentration_var in self._state_vars
                 else self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX,

             'modifiable_parameters': self._format_modifiable_parameters(),
             'state_vars': self._formatted_state_vars,
             'use_verify_state_variables': self._use_verify_state_variables,
             'default_stimulus_equations': self._format_default_stimulus(),
             'ionic_vars': self._format_equations_for_ionic_vars(),
             'y_derivatives': self._format_y_derivatives(),
             'y_derivative_equations': self._format_derivative_equations(self._derivative_equations),
             'free_variable': self._format_free_variable(),
             'ode_system_information': self._format_system_info(),
             'named_attributes': self._format_named_attributes(),
             'derived_quantities': self._format_derived_quant(),
             'derived_quantity_equations': self._format_derived_quant_eqs()}

    def get_equations_for(self, variables, recurse=True, filter_modifiable_parameters_lhs=True, optimise=True):
        """Returns equations excluding once where lhs is a modifiable parameter

        :param variables: the variables to get defining equations for.
        :param recurse: recurse and get defining equations for all variables in the defining equations?
        :param filter_modifiable_parameters_lhs: remove equations where the lhs is a modifiable paramater?
        :return: List of equations defining vars,
                 with optimisations around using log10, and powers of whole numbers applied to rhs
                 as well as modifiable parameters filtered out is required.
        """
        equations = [eq for eq in self._model.get_equations_for(variables, recurse=recurse)
                     if not filter_modifiable_parameters_lhs or eq.lhs not in self._modifiable_parameters]
        if optimise:
            for i, eq in enumerate(equations):
                optims = tuple()
                if len(eq.rhs.atoms(log)) > 0:
                    optims += (self._LOG10_OPT, log1p_opt)
                if len(eq.rhs.atoms(Pow)) > 0:
                    optims += (self._POW_OPT, )
                if len(optims) > 0:
                    equations[i] = Eq(eq.lhs, optimize(eq.rhs, optims))
        return equations

    def _get_initial_value(self, var):
        """Returns the initial value of a variable if it has one, 0 otherwise"""
        # state vars have an initial value parameter defined
        initial_value = 0
        if var in self._state_vars:
            initial_value = getattr(var, 'initial_value', 0)
        else:
            eqs = self.get_equations_for((var,), filter_modifiable_parameters_lhs=False, optimise=False)
            # If there is a defining equation, there should be just 1 equation and it should be of the form var = value
            if len(eqs) == 1 and isinstance(eqs[0].rhs, Float):
                initial_value = eqs[0].rhs
        return initial_value

    def _set_is_metadata(self, variable, metadata_tag, ontology=_PYCMLMETA):
        """Adds the metadata tag in the given ontology with the value object_value"""
        self._model.add_cmeta_id(variable)
        self._model.rdf.add((variable.rdf_identity, create_rdf_node((ontology, metadata_tag)),
                            create_rdf_node('yes')))

    def _state_var_key_order(self, var):
        """Returns a key to order state variables in the same way as pycml does"""
        if isinstance(var, Derivative):
            var = var.args[0]
        if var == self._membrane_voltage_var:
            return self._MEMBRANE_VOLTAGE_INDEX
        elif var == self._cytosolic_calcium_concentration_var and \
                self._model.units.evaluate_units(self._cytosolic_calcium_concentration_var).dimensionality == \
                self.units.get_unit('millimolar').dimensionality:
            return self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX
        else:
            return self._MEMBRANE_VOLTAGE_INDEX + self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX + 1

    def _add_units(self):
        """ Add needed units to the model to allow converting time, voltage and calcium in specific units
            as well as units for converting membrane_stimulus_current, capacitance etc.

            :return: unit_store, (default units stimulus could have)"""
        units = UnitStore(self._model.units)

        uA_per_cm2 = units.add_unit('uA_per_cm2', 'ampere / 1e6 / (meter * 1e-2)**2')
        uA_per_uF = units.add_unit('uA_per_uF', 'ampere / 1e6 / (farad * 1e-6)')
        uA = units.add_unit('uA', 'ampere / 1e6')
        units.add_unit('uF', 'farad / 1e6')
        units.add_unit('millisecond', 'second / 1e3')
        units.add_unit('millimolar', 'mole / 1e3 / litre')
        units.add_unit('millivolt', 'volt / 1e3')

        return units, (uA_per_cm2, uA, uA_per_uF)

    def _add_conversion_rules(self):
        """ Add conversion rules to allow converting stimulus current & amplitude"""
        # add 'HeartConfig::Instance()->GetCapacitance' call for use in conversions
        self._config_capacitance_call = Function('HeartConfig::Instance()->GetCapacitance', real=True)()

        self._model.units.add_conversion_rule(
            from_unit=self.units.get_unit('uA_per_uF'), to_unit=self.units.get_unit('uA_per_cm2'),
            rule=lambda ureg,
            rhs: rhs * self.units.Quantity(self._config_capacitance_call,
                                           self.units.get_unit('uA_per_cm2') / self.units.get_unit('uA_per_uF')))

        self._model.units.add_conversion_rule(
            from_unit=self.units.get_unit('uA'), to_unit=self.units.get_unit('uA_per_cm2'),
            rule=lambda ureg,
            rhs: rhs * self.units.Quantity(self._config_capacitance_call / self._membrane_capacitance,
                                           self.units.get_unit('uA_per_cm2') / self.units.get_unit('uA')))

    def _get_time_variable(self):
        """ Get the variable representing time (the free variable) and convert to milliseconds"""
        time_variable = self._model.get_free_variable()
        # Annotate as quantity and not modifiable parameter
        self._set_is_metadata(time_variable, 'derived-quantity')
        try:
            # If the variable is in units that can be converted to millisecond, perform conversion
            return self._model.convert_variable(self._model.get_free_variable(), self.units.get_unit('millisecond'),
                                                DataDirectionFlow.INPUT)
        except DimensionalityError:
            warning = 'Incorrect definition of time variable: time needs to be dimensionally equivalent to second'
            raise ValueError(warning)

    def _annotate_if_not_statevar(self, var):
        """ If it is not a state var, annotates var as modifiable parameter or derived quantity as appropriate"""
        if var not in self._state_vars:
            if self._model.is_constant(var):
                self._set_is_metadata(var, 'modifiable-parameter')
            else:  # not constant
                self._set_is_metadata(var, 'derived-quantity')

    def _get_membrane_voltage_var(self):
        """ Find the membrane_voltage variable"""
        try:
            # Get and convert V
            voltage = self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_voltage'))
            voltage = self._model.convert_variable(voltage, self.units.get_unit('millivolt'), DataDirectionFlow.INPUT)
        except KeyError:
            raise KeyError('Voltage not tagged in the model!')
        except DimensionalityError:
            raise ValueError('Incorrect definition of membrane_voltage variable: '
                             'units of membrane_voltage need to be dimensionally equivalent to Volt')
        self._annotate_if_not_statevar(voltage)  # If V is not state var annotate as appropriate.
        return voltage

    def _get_cytosolic_calcium_concentration_var(self):
        """ Find the cytosolic_calcium_concentration variable if it exists"""
        try:
            calcium = self._model.get_variable_by_ontology_term((self._OXMETA, 'cytosolic_calcium_concentration'))
            calcium = self._model.convert_variable(calcium, self.units.get_unit('millimolar'), DataDirectionFlow.INPUT)
        except KeyError:
            self._logger.info(self._model.name + ' has no cytosolic_calcium_concentration')
            return None
        except DimensionalityError:
            pass  # Conversion is optional
        self._annotate_if_not_statevar(calcium)  # If not state var annotate as appropriate
        return calcium

    def _get_modifiers(self):
        """ Get the variables that can be used as modifiers, if use_modifiers is switched on.

        These are all variables with annotation (including state vars)
        except the stimulus current and time (the free variable)
        """
        modifiers = set()
        if self.use_modifiers:
            modifiers = set(filter(lambda m: m not in (self._membrane_stimulus_current_orig, self._time_variable) and
                                   self._model.has_ontology_annotation(m, self._OXMETA), self._model.variables()))
        return modifiers - self._stimulus_params

    def _get_modifiable_parameters(self):
        """ Get all modifiable parameters, either annotated as such or with other annotation.

        Stimulus currents are ignored and the result is sorted by display name"""
        tagged = set(self._model.get_variables_by_rdf((self._PYCMLMETA, 'modifiable-parameter'), 'yes'))
        annotated = set(filter(lambda q: self._model.has_ontology_annotation(q, self._OXMETA), self._model.variables()))

        return (tagged | annotated) -\
            set(self._model.get_derived_quantities() + [self._time_variable]) - self._state_vars

    def _get_membrane_stimulus_current(self):
        """ Find the membrane_stimulus_current variable if it exists"""
        try:  # get membrane_stimulus_current
            return self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_stimulus_current'))
        except KeyError:
            self._logger.info(self._model.name + ' has no membrane_stimulus_current')
            self._is_self_excitatory = \
                next(self._model.get_rdf_annotations(subject=self._model.rdf_identity,
                     predicate=(self._PYCMLMETA, 'is-self-excitatory'), object_='yes'), None) is not None
            return None

    def _convert_membrane_stimulus_current(self):
        """ Find the membrane_stimulus_current and convert it to uA_per_cm2, using GetIntracellularAreaStimulus"""
        if self._membrane_stimulus_current_orig is None:
            return None, self._stimulus_units
        # get derivative equations
        d_eqs = self.get_equations_for(self._y_derivatives, filter_modifiable_parameters_lhs=False, optimise=False)

        # get dv/dt
        deriv_eq_only = filter(lambda eq: isinstance(eq.lhs, Derivative) and
                               eq.lhs.args[0] == self._membrane_voltage_var, d_eqs)
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
            if self._membrane_stimulus_current_orig != variable:
                if self._membrane_stimulus_current_orig.units.dimensionality == variable.units.dimensionality:
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
            voltage_rhs = voltage_rhs.xreplace({self._membrane_stimulus_current_orig: 1.0})  # stimulus = 1
            # plug in math functions for sign calculation
            voltage_rhs = voltage_rhs.subs(MATH_FUNC_SYMPY_MAPPING)
        negate_stimulus = voltage_rhs > 0.0

        membrane_stimulus_current_converted = self._model.convert_variable(self._membrane_stimulus_current_orig,
                                                                           self.units.get_unit('uA_per_cm2'),
                                                                           DataDirectionFlow.INPUT)

        # Replace stim = ... with stim = +/-GetIntracellularAreaStimulus(t)
        GetIntracellularAreaStimulus = Function('GetIntracellularAreaStimulus', real=True)(self._time_variable)
        if negate_stimulus:
            GetIntracellularAreaStimulus = -GetIntracellularAreaStimulus

        # Get stimulus defining equation
        eq = self._model.get_definition(membrane_stimulus_current_converted)
        self._model.remove_equation(eq)
        self._model.add_equation(Eq(membrane_stimulus_current_converted, GetIntracellularAreaStimulus))

        # Annotate the converted stimulus current as derived quantity
        self._set_is_metadata(membrane_stimulus_current_converted, 'derived-quantity')
        return membrane_stimulus_current_converted, \
            (self._membrane_stimulus_current_orig.units, membrane_stimulus_current_converted.units)

    def _convert_other_currents(self):
        """ Try to convert other currents (apart from stimulus current) to uA_per_cm2

        Currents are terms tagged with a term that is both `CellMembraneCurrentRelated` and an `IonicCurrent`
        according to the OXMETA ontology (https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#).
        Only variables in units convertible to Chaste's current units are converted,
        so currents in unusual units (e.g. dimensionless) are skipped.
        """
        current_related = set(get_variables_transitively(self._model,
                              (self._OXMETA, 'CellMembraneCurrentRelated')))
        all_currents = set(get_variables_transitively(self._model, (self._OXMETA, 'IonicCurrent')))
        currents = current_related.intersection(all_currents) - set([self._membrane_stimulus_current_converted])
        for current in currents:
            try:
                self._model.convert_variable(current, self.units.get_unit('uA_per_cm2'), DataDirectionFlow.OUTPUT)
            except DimensionalityError:
                pass  # conversion is optional, convert only if possible

    def _get_membrane_capacitance(self):
        """ Find membrane_capacitance if the model has it and convert it to uF if necessary"""
        try:
            capacitance = self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_capacitance'))
            return self._model.convert_variable(capacitance, self.units.get_unit('uF'), DataDirectionFlow.OUTPUT)
        except KeyError:
            self._logger.info(self._model.name + ' has no capacitance tagged')
            return None
        except DimensionalityError:
            self._logger.info(self._model.name + ' has capacitance in incompatible units, skipping')
            return None

    def _get_stimulus(self):
        """ Store the stimulus currents in the model"""
        stim_params_orig, stim_params = set(), set()
        try:  # Get required stimulus parameters
            ampl = self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_stimulus_current_amplitude'))
            duration = self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_stimulus_current_duration'))
            period = self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_stimulus_current_period'))

            stim_params_orig.update((ampl, duration, period))  # originals ones
            stim_params.add(self._model.convert_variable(ampl, self.units.get_unit('uA_per_cm2'),
                                                         DataDirectionFlow.INPUT))
            stim_params.add(self._model.convert_variable(duration, self.units.get_unit('millisecond'),
                                                         DataDirectionFlow.INPUT))
            stim_params.add(self._model.convert_variable(period, self.units.get_unit('millisecond'),
                                                         DataDirectionFlow.INPUT))
        except KeyError:
            self._logger.info(self._model.name + 'has no default stimulus params tagged')
            return set(), []
        except TypeError as e:
            if str(e) == "unsupported operand type(s) for /: 'HeartConfig::Instance()->GetCapacitance' and 'NoneType'":
                raise KeyError("Membrane capacitance is required to be able to apply conversion to stimulus current!")

        try:  # Get optional stimulus parameter
            offset = self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_stimulus_current_offset'))
            if offset is not None:
                stim_params_orig.add(offset)  # originals one
                stim_params.add(self._model.convert_variable(offset, self.units.get_unit('millisecond'),
                                                             DataDirectionFlow.INPUT))
        except KeyError:
            pass  # Optional Parameter

        try:  # Get optional stimulus parameter
            end = self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_stimulus_current_end'))
            if end is not None:
                stim_params_orig.add(end)  # originals one
                stim_params.add(self._model.convert_variable(end, self.units.get_unit('millisecond'),
                                                             DataDirectionFlow.INPUT))
        except KeyError:
            pass  # Optional Parameter

        return_stim_eqs = self.get_equations_for(stim_params, filter_modifiable_parameters_lhs=False)
        return stim_params | stim_params_orig, return_stim_eqs

    def _get_ionic_derivs(self):
        """ Getting the derivatives that define V (self._membrane_voltage_var)"""
        # use the RHS of the ODE defining V
        return [x for x in self._model.get_derivatives() if x.args[0] == self._membrane_voltage_var]

    def _get_equations_for_ionic_vars(self):
        """ Get the equations defining the ionic derivatives"""
        # figure out the currents (by finding variables with the same units as the stimulus)
        # Only equations with the same (lhs) units as the STIMULUS_CURRENT are kept.
        # Also exclude membrane_stimulus_current variable itself, and default_stimulus equations (if model has those)
        # Manually recurse down the equation graph (bfs style) if no currents are found

        # If we don't have a stimulus_current we look for a set of default unit dimensions
        equations_for_ionic_vars = []
        for unit in self._stimulus_units:
            if len(equations_for_ionic_vars) > 0:
                break
            equations_for_ionic_vars, equations, old_equations = [], self._ionic_derivs, None
            while len(equations_for_ionic_vars) == 0 and old_equations != equations:
                old_equations = equations
                equations = self.get_equations_for(equations, recurse=False, filter_modifiable_parameters_lhs=False,
                                                   optimise=False)
                equations_for_ionic_vars = [eq for eq in equations
                                            if (eq.lhs != self._membrane_stimulus_current_orig
                                                and eq.lhs not in self._stimulus_params)
                                            and self._model.units.evaluate_units(eq.lhs).dimensionality ==
                                            unit.dimensionality
                                            and eq.lhs not in self._ionic_derivs]

                equations = [eq.lhs for eq in equations]

        # create the const double var_chaste_interface__i_ionic = .. equation
        i_ionic_lhs = self._model.add_variable(name='_i_ionic', units=self.units.get_unit('uA_per_cm2'))
        i_ionic_rhs = sympify(0.0, evaluate=False)

        # add i_ionic to interface for printing
        self._in_interface.add(i_ionic_lhs)
        # convert and sum up all lhs for all ionic equations
        for var in reversed(equations_for_ionic_vars):
            factor = self._model.units.get_conversion_factor(from_unit=self._model.units.evaluate_units(var.lhs),
                                                             to_unit=self.units.get_unit('uA_per_cm2'))
            i_ionic_rhs += factor * var.lhs
        i_ionic_rhs = simplify(i_ionic_rhs)  # clean up equation

        i_ionic_eq = Eq(i_ionic_lhs, i_ionic_rhs)
        self._model.add_equation(i_ionic_eq)
        equations_for_ionic_vars.append(i_ionic_eq)

        # Update equations to include i_ionic_eq & defining eqs, set stimulus current to 0
        return equations_for_ionic_vars

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the equations defining the ionic derivatives and all dependant equations"""
        # Update equations to include i_ionic_eq & defining eqs, set stimulus current to 0
        return [eq if eq.lhs != self._membrane_stimulus_current_orig else Eq(eq.lhs, 0.0)
                for eq in self.get_equations_for([eq.lhs for eq in self._equations_for_ionic_vars])
                if eq.lhs != self._membrane_stimulus_current_converted]

    def _get_y_derivatives(self):
        """ Get derivatives for state variables"""
        derivatives = self._model.get_derivatives()
        derivatives.sort(key=lambda state_var: self._state_var_key_order(state_var))
        return derivatives

    def _get_derivative_equations(self):
        """ Get equations defining the derivatives including V (self._membrane_voltage_var)"""
        # Remove equations where lhs is a modifiable parameter or default stimulus
        return [eq for eq in self.get_equations_for(self._y_derivatives)
                if eq.lhs not in self._stimulus_params]

    def _get_derivative_eqs_excl_voltage(self):
        """ Get equations defining the derivatives excluding V (self._membrane_voltage_var)"""
        # stat with derivatives without voltage and add all equations used
        eqs = set()
        deriv_and_eqs = set(filter(lambda deriv: deriv.args[0] != self._membrane_voltage_var, self._y_derivatives))
        num_derivatives = -1
        while num_derivatives < len(deriv_and_eqs):
            num_derivatives = len(deriv_and_eqs)
            eqs = set(filter(lambda eq: eq.lhs in deriv_and_eqs, self._derivative_equations))
            for eq in eqs:
                deriv_and_eqs.update(self._model.find_variables_and_derivatives((eq.rhs, )))
        return eqs

    def _get_derivative_eqs_voltage(self):
        """ Get equations defining the derivatives for V only (self._membrane_voltage_var)"""
        # start with derivatives for V only and add all equations used
        eqs = set()
        derivatives = set(filter(lambda deriv: deriv.args[0] == self._membrane_voltage_var, self._y_derivatives))
        num_derivatives = -1
        while num_derivatives < len(derivatives):
            num_derivatives = len(derivatives)
            eqs = set(filter(lambda eq: eq.lhs in derivatives, self._derivative_equations))
            for eq in eqs:
                derivatives.update(self._model.find_variables_and_derivatives((eq.rhs, )))
        return eqs

    def _get_derived_quant(self):
        """ Get all derived quantities

        Stimulus currents are ignored and the result is sorted by display name"""
        tagged = set(self._model.get_variables_by_rdf((self._PYCMLMETA, 'derived-quantity'), 'yes'))
        # Get annotated derived quantities excluding stimulus current params
        annotated = set(filter(lambda q: q not in self._stimulus_params
                               and self._model.has_ontology_annotation(q, self._OXMETA),
                               self._model.get_derived_quantities()))

        return sorted(tagged | annotated, key=lambda v: self._model.get_display_name(v, self._OXMETA))

    def _get_derived_quant_eqs(self):
        """ Get the defining equations for derived quantities"""
        return self.get_equations_for(self._derived_quant)

    def _add_printers(self):
        """ Initialises Printers for outputting chaste code. """
        def get_variable_name(s, interface=False):
            """Get the correct variable name based on the variable and whether it should be in the chaste_interface."""
            s_name = str(s).replace('$', '__')

            prefix = 'var_chaste_interface_' if interface else 'var'
            if not s_name.startswith('_'):
                s_name = '_' + s_name
            return prefix + s_name
        # Printer for printing chaste regular variable assignments (var_ prefix)
        # Print variables in interface as var_chaste_interface
        # (state variables, time, lhs of default_stimulus eqs, i_ionic and lhs of y_derivatives)
        # Print modifiable parameters as mParameters[index]
        self._printer = \
            cg.ChastePrinter(lambda variable:
                             get_variable_name(variable, variable in self._in_interface)
                             if variable not in self._modifiable_parameters
                             else self._print_modifiable_parameterss(variable),
                             lambda deriv: 'd_dt_chaste_interface_' +
                                           (get_variable_name(deriv.expr)
                                            if isinstance(deriv, Derivative) else get_variable_name(deriv)))

        # Printer for printing variable in comments e.g. for ode system information
        self._name_printer = cg.ChastePrinter(lambda variable: get_variable_name(variable))

    def _print_rhs_with_modifiers(self, modifier, eq):
        """ Print modifiable parameters in the correct format for the model type"""
        if modifier in self._modifiers_set:
            return self._format_modifier(modifier) + '->Calc(' + self._printer.doprint(eq) + ', ' +\
                self._printer.doprint(self._time_variable) + ')'
        return self._printer.doprint(eq)

    def _format_modifier(self, var):
        """ Formatting of modifier for printing"""
        return 'mp_' + self._model.get_display_name(var) + '_modifier'

    def _format_modifiers(self):
        """ Format the modifiers for printing to chaste code"""
        return [{'name': self._model.get_display_name(param),
                 'modifier': self._format_modifier(param)}
                for param in self._modifiers]

    def _print_modifiable_parameterss(self, variable):
        """ Print modifiable parameters in the correct format for the model type"""
        return 'mParameters[' + self._modifiable_parameter_lookup[variable] + ']'

    def _format_modifiable_parameters(self):
        """ Format the modifiable parameter for printing to chaste code"""
        return [{'units': self._model.units.format(self._model.units.evaluate_units(param)),
                 'comment_name': self._name_printer.doprint(param),
                 'name': self._model.get_display_name(param, self._OXMETA),
                 'initial_value': self._printer.doprint(self._get_initial_value(param))}
                for param in self._modifiable_parameters]

    def _format_rY_entry(self, index):
        """ Formatting of rY entry for printing"""
        return 'rY[' + str(index) + ']'

    def _format_rY_lookup(self, index, var, use_modifier=True):
        """ Formatting of rY lookup for printing"""
        entry = self._format_rY_entry(index)
        if use_modifier and var in self._modifiers_set:
            entry = self._format_modifier(var) +\
                '->Calc(' + entry + ', ' + self._printer.doprint(self._time_variable) + ')'
        if var == self._membrane_voltage_var:
            entry = '(mSetVoltageDerivativeToZero ? this->mFixedVoltage : ' + entry + ')'
        return entry

    def _format_state_variables(self):
        """ Get equations defining the derivatives including  V (self._membrane_voltage_var)"""
        def get_range_annotation(subject, annotation_tag):
            """ Get range-low and range-high annotation for to verify state variables. """
            if subject.cmeta_id is not None:
                range_annotation = self._model.get_rdf_annotations(subject='#' + subject.cmeta_id,
                                                                   predicate=(self._PYCMLMETA, annotation_tag))
                annotation = next(range_annotation, None)
                assert next(range_annotation, None) is None, 'Expecting 0 or 1 range annotation'
                if annotation is not None:
                    return float(annotation[2])
            return ''

        # Get all used variables for eqs for ionic variables to be able to indicate if a state var is used
        ionic_var_variables = set()
        for eq in self._extended_equations_for_ionic_vars:
            ionic_var_variables.update(eq.rhs.free_symbols)

        # Get all used variables for y derivs to be able to indicate if a state var is used
        y_deriv_variables = set()
        for eq in self._derivative_equations:
            y_deriv_variables.update(eq.rhs.free_symbols)

        # Get all used variables for y derivs to be able to indicate if a state var is used
        voltage_deriv_variables = set()
        for eq in self._derivative_eqs_voltage:
            voltage_deriv_variables.update(eq.rhs.free_symbols)

        # Get all used variables for derivatives_excl_voltage to be able to indicate if a state var is used
        deriv_excl_voltage_variables = set()
        for eq in self._derivative_eqs_excl_voltage:
            deriv_excl_voltage_variables.update(eq.rhs.free_symbols)

        # Get all used variables for eqs for derived quantities variables to be able to indicate if a state var is used
        derived_quant_variables = set(filter(lambda q: q in self._state_vars, self._derived_quant))
        for eq in self._derived_quant_eqs:
            derived_quant_variables.update(eq.rhs.free_symbols)

        formatted_state_vars = \
            [{'var': self._printer.doprint(var[1]),
              'annotated_var_name': self._model.get_display_name(var[1], self._OXMETA),
              'rY_lookup': self._format_rY_lookup(var[0], var[1]),
              'rY_lookup_no_modifier': self._format_rY_lookup(var[0], var[1], use_modifier=False),
              'initial_value': str(self._get_initial_value(var[1])),
              'modifier': self._format_modifier(var[1]) if var[1] in self._modifiers_set else None,
              'units': self._model.units.format(self._model.units.evaluate_units(var[1])),
              'in_ionic': var[1] in ionic_var_variables,
              'in_y_deriv': var[1] in y_deriv_variables,
              'in_deriv_excl_voltage': var[1] in deriv_excl_voltage_variables,
              'in_voltage_deriv': var[1] in voltage_deriv_variables,
              'in_derived_quant': var[1] in derived_quant_variables,
              'range_low': get_range_annotation(var[1], 'range-low'),
              'range_high': get_range_annotation(var[1], 'range-high'),
              'sympy_var': var[1],
              'state_var_index': self._state_vars.index(var[1])}
             for var in enumerate(self._state_vars)]

        use_verify_state_variables = next(filter(lambda eq: eq['range_low'] != '' or eq['range_high'] != '',
                                                 formatted_state_vars), None) is not None
        return formatted_state_vars, use_verify_state_variables

    def _format_default_stimulus(self):
        """ Format eqs for stimulus_current for outputting to chaste code"""
        default_stim = {'equations':
                        [{'lhs': self._printer.doprint(eq.lhs),
                          'rhs': self._printer.doprint(eq.rhs),
                          'units': self._model.units.format(self._model.units.evaluate_units(eq.lhs)),
                          'lhs_modifiable': eq.lhs in self._modifiable_parameters}
                         for eq in self._stimulus_equations]}
        for param in self._stimulus_params:
            default_stim[self._model.get_display_name(param, self._OXMETA)] = self._printer.doprint(param)

        return default_stim

    def _format_equations_for_ionic_vars(self):
        """ Format equations and dependant equations ionic derivatives"""
        # Format the state ionic variables
        return [{'lhs': self._printer.doprint(eq.lhs), 'rhs': self._printer.doprint(eq.rhs),
                 'units': self._model.units.format(self._model.units.evaluate_units(eq.lhs))}
                for eq in self._extended_equations_for_ionic_vars]

    def _format_y_derivatives(self):
        """ Format y_derivatives for writing to chaste output"""
        self._in_interface.update(self._y_derivatives)
        return [self._printer.doprint(deriv) for deriv in self._y_derivatives]

    def _format_derivative_equations(self, derivative_equations):
        """ Format derivative equations for chaste output"""
        # exclude ionic currents
        return [{'lhs': self._printer.doprint(eq.lhs),
                 'rhs': self._print_rhs_with_modifiers(eq.lhs, eq.rhs),
                 'sympy_lhs': eq.lhs,
                 'units': self._model.units.format(self._model.units.evaluate_units(eq.lhs)),
                 'in_eqs_excl_voltage': eq in self._derivative_eqs_excl_voltage,
                 'in_membrane_voltage': eq in self._derivative_eqs_voltage,
                 'is_voltage': isinstance(eq.lhs, Derivative) and eq.lhs.args[0] == self._membrane_voltage_var}
                for eq in derivative_equations]

    def _format_free_variable(self):
        """ Format free variable for chaste output"""
        return {'name': self._model.get_display_name(self._time_variable, self._OXMETA),
                'units': self._model.units.format(self._model.units.evaluate_units(self._time_variable)),
                'system_name': self._model.name,
                'var_name': self._printer.doprint(self._time_variable)}

    def _format_system_info(self):
        """ Format general ode system info for chaste output"""
        return [{'name': self._model.get_display_name(var[1], self._OXMETA),
                 'initial_value': str(self._get_initial_value(var[1])),
                 'units': self._model.units.format(self._model.units.evaluate_units(var[1])),
                 'rY_lookup': self._format_rY_entry(var[0])}
                for var in enumerate(self._state_vars)]

    def _format_named_attributes(self):
        """ Format named attributes for chaste output"""
        named_attributes = []
        named_attrs = self._model.get_rdf_annotations(subject=self._model.rdf_identity,
                                                      predicate=(self._PYCMLMETA, 'named-attribute'))
        for s, p, attr in named_attrs:
            name = self._model.get_rdf_value(subject=attr, predicate=(self._PYCMLMETA, 'name'))
            value = self._model.get_rdf_value(subject=attr, predicate=(self._PYCMLMETA, 'value'))
            named_attributes.append({'name': name, 'value': value})

        named_attributes.sort(key=lambda a: a['name'])
        return named_attributes

    def _format_derived_quant(self):
        return [{'units': self._model.units.format(self._model.units.evaluate_units(quant)),
                 'var': self._printer.doprint(quant),
                 'name': self._model.get_display_name(quant, self._OXMETA)}
                for quant in self._derived_quant]

    def _format_derived_quant_eqs(self):
        """ Format equations for derived quantities based on current settings"""
        return [{'lhs': self._printer.doprint(eq.lhs),
                 'rhs': self._print_rhs_with_modifiers(eq.lhs, eq.rhs),
                 'sympy_lhs': eq.lhs,
                 'units': self._model.units.format(str(self._model.units.evaluate_units(eq.lhs)))}
                for eq in self._derived_quant_eqs]

    def generate_chaste_code(self):
        """ Generates and stores chaste code"""

        # Generate hpp for model
        template = cg.load_template(self._hpp_template)
        self.generated_hpp = template.render(self._vars_for_template)

        # Generate cpp for model
        template = cg.load_template(self._cpp_template)
        self.generated_cpp = template.render(self._vars_for_template)
