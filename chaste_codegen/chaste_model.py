import logging
import time
from collections import OrderedDict

from chaste_codegen._partial_eval import partial_eval
import sympy as sp
import pint
from cellmlmanip.model import DataDirectionFlow, Variable
from cellmlmanip.rdf import create_rdf_node
from cellmlmanip.units import UnitStore
from pint import DimensionalityError
from sympy.codegen.cfunctions import log10
from sympy.codegen.rewriting import (
    ReplaceOptim,
    Wild,
    log,
    optimize,
    optims_c99,
)

import chaste_codegen as cg


class ChasteModel(object):
    """ Holds information about a cellml model for which chaste code is to be generated.

    It also holds relevant formatted equations and derivatives.
    Please Note: this calass cannot generate chaste code directly, instead use a subclass of the model type
    """
    _MEMBRANE_VOLTAGE_INDEX = 0  # default index for voltage in state vector
    _CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX = 1  # default index for cytosolic calcium concentration in state vector
    _OXMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#'  # oxford metadata uri prefix
    _PYCMLMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/pycml#'  # pycml metadata uri

    # _STIM_UNITS encodes units that are possible units to try and convert to.
    # Indexed by metadata tag then by unit.
    # For membrane_stimulus_current also encodes whether to use model capacitance and/or _HEARTCONFIG_GETCAPACITANCE
    _STIM_UNITS = {'membrane_stimulus_current':
                   [{'units': 'uA_per_cm2', 'use_capacitance': False},
                    {'units': 'uA', 'use_capacitance': True},
                    {'units': 'uA_per_uF', 'use_capacitance': False}]}

    # Indicates error checks that should be carried out as assert <condition>, <message>
    # before conversion rules can be applied. There should be one for every conversion rule

    _V = Wild('V')
    _W = Wild('W')
    _LOG10_OPT = ReplaceOptim(_V * log(_W) / log(10), _V * log10(_W), cost_function=lambda expr: expr.count(
        lambda e: (  # division & eval of transcendentals are expensive floating point operations...
            e.is_Pow and e.exp.is_negative  # division
            or (isinstance(e, (log, log10)) and not e.args[0].is_number))))
    _POW_OPT = ReplaceOptim(lambda p: p.is_Pow and (isinstance(p.exp, sp.Float) or isinstance(p.exp, float))
                            and float(p.exp).is_integer(),
                            lambda p: sp.Pow(p.base, int(float(p.exp))))
    _OPTIMS = optims_c99 + (_LOG10_OPT, _POW_OPT, )

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
        self._units = self._add_units()
        # add 'HeartConfig::Instance()->GetCapacitance' call for use in conversions
        self._config_capacitance = self._units.Quantity(
            sp.Function('HeartConfig::Instance()->GetCapacitance', real=True)(),
            self.uA_per_cm2 / self.uA_per_uF)

        # in_interface may have already been set by child class
        self._in_interface = getattr(self, '_in_interface', [])

        self._time_variable = self._get_time_variable()
        self._state_vars = self._model.get_state_variables()

        self._membrane_voltage_var = self._get_membrane_voltage_var()
        self._cytosolic_calcium_concentration_var = self._get_cytosolic_calcium_concentration_var()

        # Sort the state variables, in similar order to pycml to prevent breaking existing code.
        # V and cytosolic_calcium_concentration need to be set for the sorting
        # Conversions of V or cytosolic_calcium_concentration could have changed the state vars so a new call is needed
        self._state_vars = sorted(self._model.get_state_variables(),
                                  key=lambda state_var: self._state_var_key_order(state_var))

        self._in_interface.extend(self._state_vars)

        self._modifiers = self._get_modifiers()
        self._modifiable_parameters = self._get_modifiable_parameters()
        self._in_interface.append(self._time_variable)

        # get capacitance and update stimulus current
        self._membrane_stimulus_current = self._get_membrane_stimulus_current()
        self._original_membrane_stimulus_current = self._membrane_stimulus_current
        self._membrane_capacitance = self._get_membrane_capacitance()
        self._stimulus_params, self._stimulus_equations = self._get_stimulus()
        self._in_interface.extend(self._stimulus_params)

        self._ionic_derivs = self._get_ionic_derivs()
        self._equations_for_ionic_vars, self._current_unit_and_capacitance, self._membrane_stimulus_current_factor = \
            self._get_equations_for_ionic_vars()
        self._extended_equations_for_ionic_vars = self._get_extended_equations_for_ionic_vars()

        self._y_derivatives = self._get_y_derivatives()
        self._derivative_equations = self._get_derivative_equations()
        self._derivative_eqs_excl_voltage = self._get_derivative_eqs_excl_voltage()
        self._derivative_eqs_voltage = self._get_derivative_eqs_voltage()

        self._derived_quant = self._get_derived_quant()
        self._derived_quant_eqs = self._get_derived_quant_eqs()

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
             'use_capacitance_i_ionic': self._current_unit_and_capacitance['use_capacitance'],

             'modifiable_parameters': self._format_modifiable_parameters(),
             'state_vars': self._formatted_state_vars,
             'use_verify_state_variables': self._use_verify_state_variables,
             'default_stimulus_equations': self._format_default_stimulus(),
             'ionic_vars': self._format_extended_equations_for_ionic_vars(),
             'y_derivatives': self._format_y_derivatives(),
             'y_derivative_equations': self._format_derivative_equations(self._derivative_equations),
             'free_variable': self._format_free_variable(),
             'ode_system_information': self._format_system_info(),
             'named_attributes': self._format_named_attributes(),
             'derived_quantities': self._format_derived_quant(),
             'derived_quantity_equations': self._format_derived_quant_eqs()}

    def get_equations_for(self, variables, recurse=True, filter_modifiable_parameters_lhs=True):
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
        return [sp.Eq(eq.lhs, optimize(eq.rhs, self._OPTIMS)) for eq in equations]

    def _add_units(self):
        """ Add needed units to the model to allow converting time, voltage and calcium in specific units
            as well as units for converting membrane_stimulus_current."""
        units = self._model.units
        unit_definitions = {'uA_per_cm2': 'ampere / 1e6 / (meter * 1e-2)**2',
                            'uA_per_uF': 'ampere / 1e6 / (farad * 1e-6)',
                            'uA': 'ampere / 1e6',
                            'uF': 'farad / 1e6',
                            'uF_per_mm2': 'farad / 1e6 / (meter * 1e-3)**2',
                            'millisecond': 'second / 1e3',
                            'millimolar': 'mole / 1e3 / litre',
                            'millivolt': 'volt / 1e3'}
        for unit_name, unit_defn in unit_definitions.items():
            try:
                units.add_unit(unit_name, unit_defn)
            except ValueError:
                pass  # already exists
        self.uA_per_cm2 = units.get_unit('uA_per_cm2')
        self.uA_per_uF = units.get_unit('uA_per_uF')
        self.uA = units.get_unit('uA')
        self.uF = units.get_unit('uF')
        self.uF_per_mm2 = units.get_unit('uF_per_mm2')
        self.millisecond = units.get_unit('millisecond')
        self.millimolar = units.get_unit('millimolar')
        self.millivolt = units.get_unit('millivolt')
        return units

    def _get_converted_var(self, tag, units, conversion_optional=False, optional=False):
        '''Retreive variable by tag and convert to desired units'''
        try:
            var = self._model.get_variable_by_ontology_term((self._OXMETA, tag))
        except KeyError:
            if not optional:
                raise
            else:
                return None
        try:
            return self._model.convert_variable(var, units, DataDirectionFlow.INPUT)
        except DimensionalityError:
            if not conversion_optional:
                raise
            else:
                return var

    def _get_initial_value(self, var):
        """Returns the initial value of a variable if it has one, 0 otherwise"""
        # state vars have an initial value parameter defined
        initial_value = 0
        if var in self._state_vars:
            initial_value = getattr(var, 'initial_value', 0)
        else:
            eqs = self._model.get_equations_for([var])
            # If there is a defining equation, there should be just 1 equation and it should be of the form var = value
            if len(eqs) == 1 and isinstance(eqs[0].rhs, sp.numbers.Float):
                initial_value = eqs[0].rhs
        return initial_value

    def _set_is_metadata(self, variable, metadata_tag, ontology=_PYCMLMETA, object_value='yes'):
        """Adds the metadata tag in the given ontology with the value object_value"""
        self._model.add_cmeta_id(variable)
        self._model.rdf.add((variable.rdf_identity, create_rdf_node((ontology, metadata_tag)),
                            create_rdf_node(object_value)))

    def _state_var_key_order(self, var):
        """Returns a key to order state variables in the same way as pycml does"""
        if isinstance(var, sp.Derivative):
            var = var.args[0]
        if var == self._membrane_voltage_var:
            return self._MEMBRANE_VOLTAGE_INDEX
        elif var == self._cytosolic_calcium_concentration_var and \
                self._model.units.evaluate_units(self._cytosolic_calcium_concentration_var).dimensionality == \
                self.millimolar.dimensionality:
            return self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX
        else:
            return self._MEMBRANE_VOLTAGE_INDEX + self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX + 1

    def _get_time_variable(self):
        time_variable = self._model.get_free_variable()
        # Add derived quantity metadata tag
        self._set_is_metadata(time_variable, 'derived-quantity')
        try:
            # If the variable is in units that can be converted to millisecond, perform conversion
            return self._model.convert_variable(self._model.get_free_variable(), self.millisecond, DataDirectionFlow.INPUT)
        except DimensionalityError:
            warning = 'Incorrect definition of time variable (time needs to be dimensionally equivalent to second)'
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
            voltage = self._get_converted_var('membrane_voltage', self.millivolt)
        except KeyError:
            raise ValueError('Voltag not tagged in the model')
        except DimensionalityError:
            raise ValueError('Incorrect definition of membrane_voltage variable '\
                      '(units of membrane_voltage need to be dimensionally equivalent to Volt)')
        self._annotate_if_not_statevar(voltage)  # If V is not state var annotate as appropriate.
        return voltage

    def _get_cytosolic_calcium_concentration_var(self):
        """ Find the cytosolic_calcium_concentration variable if it exists"""
        try:
            cytosolic_calcium_concentration = self._get_converted_var('cytosolic_calcium_concentration',
                                                                      self.millimolar, conversion_optional=True)
            self._annotate_if_not_statevar(cytosolic_calcium_concentration)  # If not state var annotate as appropriate
        except KeyError:
            self._logger.info(self._model.name + ' has no cytosolic_calcium_concentration')
            return None
        return cytosolic_calcium_concentration

    def _get_modifiers(self):
        """ Get the variables that can be used as modifiers, if use_modifiers is switched on.

        These are all variables with annotation (including state vars)
        except the stimulus current and time (the free variable)"""
        modifiers = []
        if self.use_modifiers:
            modifiers = [m for m in self._model.variables()
                         if self._model.has_ontology_annotation(m, self._OXMETA)
                         and not self._model.get_ontology_terms_by_variable(m, self._OXMETA)[-1].
                         startswith('membrane_stimulus_current')
                         and not m == self._time_variable]

        return sorted(modifiers, key=lambda m: self._model.get_display_name(m, self._OXMETA))

    def _get_modifiable_parameters(self):
        """ Get all modifiable parameters, either annotated as such or with other annotation.

        Stimulus currents are ignored and the result is sorted by display name"""
        tagged = self._model.get_variables_by_rdf((self._PYCMLMETA, 'modifiable-parameter'), 'yes')
        annotated = [q for q in self._model.variables()
                     if self._model.has_ontology_annotation(q, self._OXMETA)]
        currents = [var for var in annotated if self._model.get_ontology_terms_by_variable(var, self._OXMETA)[-1]
                    .startswith('membrane_stimulus_current')]

        parameters = set(tagged + annotated) -\
            set(currents + self._model.get_derived_quantities() + self._state_vars + [self._time_variable])
        return sorted(parameters, key=lambda v: self._model.get_display_name(v, self._OXMETA))

    def _get_membrane_stimulus_current(self):
        """ Find the membrane_stimulus_current variable if it exists"""
        try:
            return self._model.get_variable_by_ontology_term((self._OXMETA, 'membrane_stimulus_current'))
        except KeyError:
            self._logger.info(self._model.name + ' has no membrane_stimulus_current')
            self._is_self_excitatory = len(list(self._model.get_rdf_annotations(subject=self._model.rdf_identity,
                                                predicate=(self._PYCMLMETA, 'is-self-excitatory'), object_='yes'))) > 0
            return None

    def _get_membrane_capacitance(self):
        """ Find membrane_capacitance if the model has it"""
        equation = None

        # get capacitance and convert if necessary
        try:
            self._model.units.add_conversion_rule(from_unit=self.uF, to_unit=self.uA / self.uA_per_cm2,
                                                  rule=lambda ureg, rhs: rhs / self._config_capacitance)
            # Convert if necessary
            return self._get_converted_var('membrane_capacitance', self.uA / self.uA_per_cm2)
        except KeyError:
            self._logger.info(self._model.name + ' has no capacitance')
            return None

    def _get_stimulus(self):
        """ Store the stimulus currents in the model"""
        # add conversion rule (for amplitude) from uA_per_uF to uA_per_cm2 by multiplying by 'HeartConfig::Instance()->GetCapacitance' call
        self._model.units.add_conversion_rule(from_unit=self.uA_per_uF, to_unit=self.uA_per_cm2,
                                              rule=lambda ureg, rhs: rhs * self._config_capacitance)

        # add conversion rule (for amplitude) from uA to uA_per_cm2 by deviding by (converted) capacitance in the model
        if self._membrane_capacitance is not None:  # Can only do this if the model has a capacitance
            self._model.units.add_conversion_rule(from_unit=self.uA, to_unit=self.uA_per_cm2,
                                                  rule=lambda ureg,
                                                  rhs: rhs / self._units.Quantity(self._membrane_capacitance, self._membrane_capacitance.units))

        stim_param = []
        try: # Get required stimulus parameters
            stim_param.append(self._get_converted_var('membrane_stimulus_current_amplitude', self.uA_per_cm2))
            stim_param.append(self._get_converted_var('membrane_stimulus_current_duration', self.millisecond))
            stim_param.append(self._get_converted_var('membrane_stimulus_current_period', self.millisecond))
        except KeyError:
            self._logger.info(self._model.name + 'has no default stimulus params tagged')
            return [], []

        # Get optional stimulus params
        stim_param.append(self._get_converted_var('membrane_stimulus_current_offset', self.millisecond, optional=True))
        stim_param.append(self._get_converted_var('membrane_stimulus_current_end', self.millisecond, optional=True))

        # Remove empty (optional) params
        stim_param = [p for p in stim_param if p is not None]
        return_stim_eqs = self.get_equations_for(stim_param, filter_modifiable_parameters_lhs=False)
        return stim_param, return_stim_eqs

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
        equations_for_ionic_vars, desired_units_and_capacitance, stimulus_current_factor = [], None, 1.0
        units_to_try = self._STIM_UNITS['membrane_stimulus_current']
        if self._membrane_stimulus_current is not None:
            membrane_stimulus_units = self._model.units.evaluate_units(self._membrane_stimulus_current)
            units_to_try = \
                [u for u in units_to_try
                 if self._units.get_unit(u['units']).dimensionality == membrane_stimulus_units.dimensionality]

        for unit_cap in units_to_try:
            if len(equations_for_ionic_vars) > 0:
                break
            equations, old_equations = self._ionic_derivs, None
            while len(equations_for_ionic_vars) == 0 and old_equations != equations:
                old_equations = equations
                equations = self.get_equations_for(equations, recurse=False)
                equations_for_ionic_vars = [eq for eq in equations
                                            if ((self._membrane_stimulus_current is None)
                                                or (eq.lhs != self._membrane_stimulus_current
                                                and eq.lhs not in self._stimulus_params))
                                            and self._model.units.evaluate_units(eq.lhs).dimensionality
                                            == self._units.get_unit(unit_cap['units']).dimensionality
                                            and eq.lhs not in self._ionic_derivs]
                equations = [eq.lhs for eq in equations]
            desired_units_and_capacitance = unit_cap.copy()
        if self._membrane_stimulus_current is not None:
            stimulus_current_factor = \
                self._model.units.get_conversion_factor(from_unit=membrane_stimulus_units,
                                                        to_unit=self._units.get_unit(
                                                            desired_units_and_capacitance['units']))
            if stimulus_current_factor != 1.0:
                warning = 'converting stimulus current from ' + str(membrane_stimulus_units) + ' to ' + \
                    str(desired_units_and_capacitance['units'])
                self._logger.info(warning)

        desired_units_and_capacitance['use_capacitance'] = desired_units_and_capacitance['use_capacitance'] \
            and self._membrane_capacitance is not None

        return equations_for_ionic_vars, desired_units_and_capacitance, stimulus_current_factor

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the equations defining the ionic derivatives and all dependant equations"""

        # create the const double var_chaste_interface__i_ionic = .. equation
        i_ionic_lhs = self._model.add_variable(name='_i_ionic', units=self.uA_per_cm2)
        i_ionic_rhs = sp.sympify(0.0, evaluate=False)

        # add i_ionic to interface for printing
        self._in_interface.append(i_ionic_lhs)
        # sum up all lhs * conversion_factor for all ionic equations
        for var in self._equations_for_ionic_vars:
            current_unit = self._model.units.evaluate_units(var.lhs)
            factor = self._model.units.get_conversion_factor(
                from_unit=current_unit, to_unit=self._units.get_unit(self._current_unit_and_capacitance['units']))
            if factor != 1.0:
                warning = 'converting ' + str(var.lhs) + ' in GetIIonic current from ' + str(current_unit) + ' to ' +\
                    str(self._current_unit_and_capacitance['units'])
                self._logger.info(warning)

            i_ionic_rhs = (factor * var.lhs if factor != 1.0 else var.lhs) + i_ionic_rhs

        # check if we need to convert using capacitance
        if self._current_unit_and_capacitance['use_capacitance']:
            i_ionic_rhs /= self._membrane_capacitance


        i_ionic_eq = sp.Eq(i_ionic_lhs, i_ionic_rhs)
        self._model.add_equation(i_ionic_eq)
        self._equations_for_ionic_vars.append(i_ionic_eq)

        # Remove equations where lhs is a modifiable parameter or stimulus vars
        extended_eqs = self._equations_for_ionic_vars
        changed = True
        while changed:
            new_eqs = self.get_equations_for([v.lhs for v in extended_eqs
                                              if v.lhs not in
                                              (self._membrane_stimulus_current,
                                               self._original_membrane_stimulus_current)], recurse=False)
            changed = new_eqs != extended_eqs
            extended_eqs = new_eqs

        # set _membrane_stimulus_current to 0.0
        return [eq if eq.lhs not in (self._membrane_stimulus_current, self._original_membrane_stimulus_current)
                else sp.Eq(eq.lhs, 0.0) for eq in extended_eqs]

    def _get_y_derivatives(self):
        """ Get derivatives for state variables"""
        return sorted(self._model.get_derivatives(),
                      key=lambda state_var: self._state_var_key_order(state_var))

    def _get_derivative_equations(self):
        """ Get equations defining the derivatives including V (self._membrane_voltage_var)"""
        def get_deriv_eqs():
            """ Get equations defining the derivatives"""
            # Remove equations where lhs is a modifiable parameter or default stimulus
            return [eq for eq in self.get_equations_for(self._y_derivatives)
                    if eq.lhs not in self._stimulus_params]

        d_eqs = get_deriv_eqs()
        # If there is a _membrane_stimulus_current set, convert it.
        if self._membrane_stimulus_current is not None:
            negate_stimulus = False
            # loop through equations backwards as derivatives are last
            for i in range(len(d_eqs) - 1, - 1, - 1):
                if isinstance(d_eqs[i].lhs, sp.Derivative):
                    # This is dV/dt
                    # Assign temporary values to variables in order to check the stimulus sign.
                    # This will process defining expressions in a breadth first search until the stimulus
                    # current is found.  Each variable that doesn't have its definitions processed will
                    # be given a value as follows:
                    # - stimulus current = 1
                    # - other currents = 0
                    # - other variables = 1
                    # The stimulus current is then negated from the sign expected by Chaste if evaluating
                    # dV/dt gives a positive value.
                    if d_eqs[i].lhs.args[0] == self._membrane_voltage_var:
                        voltage_rhs = d_eqs[i].rhs
                        variables = list(voltage_rhs.free_symbols)
                        for variable in variables:
                            if self._membrane_stimulus_current != variable:
                                if self._units.get_unit(self._current_unit_and_capacitance['units']).dimensionality == \
                                        self._model.units.evaluate_units(variable).dimensionality:
                                    if isinstance(voltage_rhs, sp.expr.Expr):
                                        voltage_rhs = voltage_rhs.xreplace({variable: 0.0})  # other currents = 0
                                else:
                                    # For other variables see if we need to follow their definitions first
                                    rhs = None
                                    if variable in [eq.lhs for eq in d_eqs]:
                                        rhs = [eq.rhs for eq in d_eqs if eq.lhs == variable][-1]

                                    if rhs is not None and not isinstance(rhs, sp.numbers.Float):
                                        voltage_rhs = voltage_rhs.xreplace({variable: rhs})  # Update definition
                                        variables.extend(rhs.free_symbols)
                                    else:
                                        if isinstance(voltage_rhs, sp.expr.Expr):
                                            voltage_rhs = voltage_rhs.xreplace({variable: 1.0})  # other variables = 1
                        if isinstance(voltage_rhs, sp.expr.Expr):
                            voltage_rhs = voltage_rhs.xreplace({self._membrane_stimulus_current: 1.0})  # stimulus = 1
                        negate_stimulus = voltage_rhs > 0.0

            # Set GetIntracellularAreaStimulus calculaion
            GetIntracellularAreaStimulus = sp.Function('GetIntracellularAreaStimulus', real=True)
            area = GetIntracellularAreaStimulus(self._time_variable)
            if negate_stimulus:
                area = -area

            # add converter equation
            converter_var = self._model.add_variable(name=self._membrane_stimulus_current.name + '_converter',
                                                     units=self.uA_per_cm2, cmeta_id=None)
            # move metadata tag
            self._model.transfer_cmeta_id(self._membrane_stimulus_current, converter_var)
            # add new equation for converter_var
            self._model.add_equation(sp.Eq(converter_var, area))

            # determine capacitance stuff
            stim_current_eq_rhs = converter_var
            if self._current_unit_and_capacitance['use_capacitance']:
                stim_current_eq_rhs *= self._membrane_capacitance
            fac = 1 / self._membrane_stimulus_current_factor
            if fac != 1.0:
                stim_current_eq_rhs *= fac

            # Get stimulus defining equation
            eq = [e for e in self._model.equations if e.lhs == self._membrane_stimulus_current][-1]
            # remove old equation
            self._model.remove_equation(eq)
            # add eq self._membrane_stimulus_current = area to model
            self._model.add_equation(sp.Eq(self._membrane_stimulus_current, stim_current_eq_rhs))

            # update self._membrane_stimulus_current
            self._membrane_stimulus_current = self._get_membrane_stimulus_current()

        return get_deriv_eqs()

    def _get_derivative_eqs_excl_voltage(self):
        """ Get equations defining the derivatives excluding V (self._membrane_voltage_var)"""
        # stat with derivatives without voltage and add all equations used
        eqs = []
        deriv_and_eqs = set([deriv for deriv in self._y_derivatives if deriv.args[0] != self._membrane_voltage_var])
        num_derivatives = -1
        while num_derivatives < len(deriv_and_eqs):
            num_derivatives = len(deriv_and_eqs)
            eqs = [eq for eq in self._derivative_equations if eq.lhs in deriv_and_eqs]
            for eq in eqs:
                for s in self._model.find_variables_and_derivatives([eq.rhs]):
                    deriv_and_eqs.add(s)
        return eqs

    def _get_derivative_eqs_voltage(self):
        """ Get equations defining the derivatives for V only (self._membrane_voltage_var)"""
        # start with derivatives for V only and add all equations used
        eqs = []
        derivatives = set([deriv for deriv in self._y_derivatives if deriv.args[0] == self._membrane_voltage_var])
        num_derivatives = -1
        while num_derivatives < len(derivatives):
            num_derivatives = len(derivatives)
            eqs = [eq for eq in self._derivative_equations if eq.lhs in derivatives]
            for eq in eqs:
                for s in self._model.find_variables_and_derivatives([eq.rhs]):
                    derivatives.add(s)
        return eqs

    def _get_derived_quant(self):
        """ Get all derived quantities

        Stimulus currents are ignored and the result is sorted by display name"""
        tagged = self._model.get_variables_by_rdf((self._PYCMLMETA, 'derived-quantity'), 'yes')
        annotated = [q for q in self._model.get_derived_quantities()
                     if self._model.has_ontology_annotation(q, self._OXMETA)]
        derived_quant = tagged + annotated
        if self._membrane_stimulus_current is not None and len(self._stimulus_equations) > 0:
            derived_quant += [self._membrane_stimulus_current]

        return sorted(set(derived_quant), key=lambda v: self._model.get_display_name(v, self._OXMETA))

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
                             else self._print_modifiable_parameters(variable),
                             lambda deriv: 'd_dt_chaste_interface_' +
                                           (get_variable_name(deriv.expr)
                                            if isinstance(deriv, sp.Derivative) else get_variable_name(deriv)))

        # Printer for printing variable in comments e.g. for ode system information
        self._name_printer = cg.ChastePrinter(lambda variable: get_variable_name(variable))

    def _print_rhs_with_modifiers(self, modifier, eq):
        """ Print modifiable parameters in the correct format for the model type"""
        if modifier in self._modifiers:
            return self._format_modifier(modifier) + '->Calc(' + self._printer.doprint(eq) + ', ' +\
                self._printer.doprint(self._time_variable) + ')'
        return self._printer.doprint(eq)

    def _format_modifier(self, var):
        return 'mp_' + self._model.get_display_name(var) + '_modifier'

    def _format_modifiers(self):
        """ Format the modifiers for printing to chaste code"""
        return [{'name': self._model.get_display_name(param),
                 'modifier': self._format_modifier(param)}
                for param in self._modifiers]

    def _print_modifiable_parameters(self, variable):
        """ Print modifiable parameters in the correct format for the model type"""
        return 'mParameters[' + str(self._modifiable_parameters.index(variable)) + ']'

    def _format_modifiable_parameters(self):
        """ Format the modifiable parameter for printing to chaste code"""
        return [{'units': self._model.units.format(self._model.units.evaluate_units(param)),
                 'comment_name': self._name_printer.doprint(param),
                 'name': self._model.get_display_name(param, self._OXMETA),
                 'initial_value': self._printer.doprint(self._get_initial_value(param))}
                for param in self._modifiable_parameters]

    def _format_rY_entry(self, index):
        return 'rY[' + str(index) + ']'

    def _format_rY_lookup(self, index, var, use_modifier=True):
        entry = self._format_rY_entry(index)
        if use_modifier and var in self._modifiers:
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
                range_annotation = list(self._model.get_rdf_annotations(subject='#' + subject.cmeta_id,
                                                                        predicate=(self._PYCMLMETA, annotation_tag)))
                assert len(range_annotation) < 2, 'Expecting 0 or 1 range annotation'
                if len(range_annotation) == 1:
                    return float(range_annotation[0][2])
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
        derived_quant_variables = set()
        for eq in self._derived_quant_eqs:
            derived_quant_variables.update(eq.rhs.free_symbols)

        formatted_state_vars = \
            [{'var': self._printer.doprint(var[1]),
              'annotated_var_name': self._model.get_display_name(var[1], self._OXMETA),
              'rY_lookup': self._format_rY_lookup(var[0], var[1]),
              'rY_lookup_no_modifier': self._format_rY_lookup(var[0], var[1], use_modifier=False),
              'initial_value': str(self._get_initial_value(var[1])),
              'modifier': self._format_modifier(var[1]) if var[1] in self._modifiers else None,
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

        use_verify_state_variables = \
            len([eq for eq in formatted_state_vars if eq['range_low'] != '' or eq['range_high'] != '']) > 0
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

    def _format_extended_equations_for_ionic_vars(self):
        """ Format equations and dependant equations ionic derivatives"""
        # Format the state ionic variables
        return [{'lhs': self._printer.doprint(eq.lhs), 'rhs': self._printer.doprint(eq.rhs),
                 'units': self._model.units.format(self._model.units.evaluate_units(eq.lhs))}
                for eq in self._extended_equations_for_ionic_vars]

    def _format_y_derivatives(self):
        """ Format y_derivatives for writing to chaste output"""
        self._in_interface.extend(self._y_derivatives)
        return [self._printer.doprint(deriv) for deriv in self._y_derivatives]

    def _format_derivative_equations(self, derivative_equations):
        """Format derivative equations for chaste output"""
        # exclude ionic currents
        return [{'lhs': self._printer.doprint(eq.lhs),
                 'rhs': self._print_rhs_with_modifiers(eq.lhs, eq.rhs),
                 'sympy_lhs': eq.lhs,
                 'units': self._model.units.format(self._model.units.evaluate_units(eq.lhs)),
                 'in_eqs_excl_voltage': eq in self._derivative_eqs_excl_voltage,
                 'in_membrane_voltage': eq in self._derivative_eqs_voltage,
                 'is_voltage': isinstance(eq.lhs, sp.Derivative) and eq.lhs.args[0] == self._membrane_voltage_var}
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

        return sorted(named_attributes, key=lambda a: a['name'])

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
