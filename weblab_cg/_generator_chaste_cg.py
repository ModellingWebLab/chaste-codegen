import logging
import time
import sympy as sp
import weblab_cg as cg
from pint import errors


class ChasteModel(object):
    """ Holds information about a cellml model for which chaste code is to be generated.

    It also holds relevant formatted equations and derivatives.
    Please Note: this calass cannot generate chaste code directly, instead use a subclass fo the model type
    """
    # TODO: variable conversion via cellmlmanip
    # TODO: look into explicit unit conversion rules vs hard coding?
    #       https://chaste.cs.ox.ac.uk/trac/wiki/FunctionalCuration/ProtocolSyntax#Modelinterface
    # TODO: script to call generator from command line
    # TODO: Model types Opt, Analytic_j, Numerical_j, BE

    _MEMBRANE_VOLTAGE_INDEX = 0
    _CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX = 1
    _OXMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#'
    _PYCMLMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/pycml#'

    _UNIT_DEFINITIONS = {'uA_per_cm2': [{'prefix': 'micro', 'units': 'ampere'},
                                        {'exponent': '-2', 'prefix': 'centi', 'units': 'metre'}],
                         'uA_per_uF': [{'prefix': 'micro', 'units': 'ampere'},
                                       {'exponent': '-1', 'prefix': 'micro', 'units': 'farad'}],
                         'uA': [{'prefix': 'micro', 'units': 'ampere'}],
                         'uF': [{'prefix': 'micro', 'units': 'farad'}],
                         'uF_per_mm2': [{'prefix': 'micro', 'units': 'farad'}, {
                             'units': 'metre', 'prefix': 'milli', 'exponent': '-2'}],
                         'millisecond': [{'prefix': 'milli', 'units': 'second'}],
                         'millimolar': [{'units': 'mole', 'prefix': 'milli'}, {'units': 'litre', 'exponent': '-1'}],
                         'millivolt': [{'prefix': 'milli', 'units': 'volt'}]}

    _STIM_UNITS = {'membrane_stimulus_current': ['uA_per_cm2', 'uA', 'uA_per_uF'],
                   'membrane_stimulus_current_period': ['millisecond'],
                   'membrane_stimulus_current_duration': ['millisecond'],
                   'membrane_stimulus_current_amplitude': ['uA_per_cm2', 'uA_per_uF', 'uA'],
                   'membrane_stimulus_current_offset': ['millisecond'],
                   'membrane_stimulus_current_end': ['millisecond'],
                   'membrane_capacitance': ['uF', 'uF_per_mm2']}

    _STIM_RHS_MULTIPLIER = {'membrane_stimulus_current_amplitude':
                            {'uA_per_uF': ' * HeartConfig::Instance()->GetCapacitance()',
                             'uA': ' * HeartConfig::Instance()->GetCapacitance()'}}
    _STIM_CONVERSION_RULES = \
        {'membrane_stimulus_current_amplitude':
            {'uA':
                lambda self,
                current_units,
                factor, eq:
                (getattr(self._model.units.ureg, self._STIM_UNITS['membrane_stimulus_current_amplitude'][0]),
                 factor / self._membrane_capacitance_factor,
                 sp.Eq(eq.lhs, eq.rhs / self._membrane_capacitance.lhs),
                 [{'lhs': self._printer.doprint(self._membrane_capacitance.lhs),
                   'rhs': self._printer.doprint(self._membrane_capacitance.rhs),
                   'units': str(self._model.units.summarise_units(self._membrane_capacitance.lhs))}]
                 )}}

    def __init__(self, model, class_name, file_name):
        """ Initialise a ChasteModel instance
        Arguments

        ``model``
            A :class:`cellmlmanip.Model` object.
        ``output_path``
            The path to store the generated model code at.
            (Just the path, excluding the file name as file name will be determined by the model_name)
        ``class_name``
            The name of the class to be generated.
        ``file_name``
            The name you want to give your generated files WITHOUT the .hpp and .cpp extension
            (e.g. aslanidi_model_2009 leads to aslanidi_model_2009.cpp and aslanidi_model_2009.hpp)
        """
        self.class_name = class_name
        self.file_name = file_name
        self.dynamically_loadable = False
        self.generated_hpp = ''
        self.generated_cpp = ''

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        # Store parameters for future reference
        self._model = model
        self._is_self_excitatory = False

        self._add_units()

        self._in_interface = []
        self._modifiable_parameters = self._get_modifiable_parameters()
        self._time_variable = self._model.get_free_variable_symbol()
        self._in_interface.append(self._time_variable)

        self._membrane_voltage_var = self._get_membrane_voltage_var()
        self._cytosolic_calcium_concentration_var = self._get_cytosolic_calcium_concentration_var()
        self._use_get_intracellular_calcium_concentration = self._get_use_get_intracellular_calcium_concentration()
        self._state_vars = self._get_state_variables()
        self._in_interface.extend(self._state_vars)
        self._state_var_conversion_factors, self._state_var_subs = self._get_state_var_conversion()

        self._membrane_stimulus_current = self._get_membrane_stimulus_current()
        self._membrane_capacitance, self._membrane_capacitance_factor = self._get_membrane_capacitance()
        self._default_stimulus = self._get_stimulus()

        self._ionic_derivs = self._get_ionic_derivs()
        self._equations_for_ionic_vars, self._desired_current_units, self._use_capacitance_i_ionic, \
            self._membrane_stimulus_current_factor = self._get_equations_for_ionic_vars()
        self._extended_equations_for_ionic_vars = self._get_extended_equations_for_ionic_vars()

        self._y_derivatives = self._get_y_derivatives()
        self._y_derivatives_voltage = self._get_y_derivatives_voltage()
        self._y_derivatives_excl_voltage = self._get_y_derivatives_excl_voltage()
        self._derivative_eqs_voltage = self._get_derivative_eqs_voltage()
        self._derivative_eqs_exlc_voltage = self._get_derivative_eqs_exlc_voltage()
        self._derivative_equations = self._get_derivative_equations()

        self._add_printers()
        self._formatted_modifiable_parameters = self._format_modifiable_parameters()
        self._formatted_state_vars = self._format_state_variables()
        self._formatted_default_stimulus = self._format_default_stimulus()
        self._formatted_equations_for_ionic_vars = self._format_equations_for_ionic_vars()
        self._formatted_extended_equations_for_ionic_vars = self._format_extended_equations_for_ionic_vars()
        self._formatted_y_derivatives = self._format_y_derivatives()
        self._formatted_derivative_eqs = self._format_derivative_equations()
        self._free_variable, self._ode_system_information, self._named_attributes = self._format_ode_system_info()

    def generate_chaste_code(self):
        """ Generate chaste code
        Please Note: not implemented, use a subclass for the relevant model type
        """
        raise NotImplementedError("Should not be called directly, use the specific model types instead!")

    def _add_printers(self):
        """ Initialises Printers for outputting chaste code. """
        def get_symbol_name(s):
            s_name = str(s).replace('$', '__')
            if not s_name.startswith('_'):
                s_name = '_' + s_name
            return s_name
        # Printer for printing chaste regular variable assignments (var_ prefix)
        # Print variables in interface as var_chaste_interface
        # (state variables, time, lhs of default_stimulus eqs, i_ionic and lhs of y_derivatives)
        # Print modifiable parameters as mParameters[index]
        self._printer = \
            cg.ChastePrinter(lambda symbol:
                             ('var_chaste_interface_'
                              if symbol in self._in_interface else 'var') + get_symbol_name(symbol)
                             if symbol not in self._modifiable_parameters
                             else 'mParameters[' + str(self._modifiable_parameters.index(symbol)) + ']',
                             lambda deriv: 'd_dt_chaste_interface_' +
                                           (get_symbol_name(deriv.expr)
                                            if isinstance(deriv, sp.Derivative) else get_symbol_name(deriv)))

        # Printer for printing variable in comments e.g. for ode system information
        self._name_printer = cg.ChastePrinter(lambda symbol: get_symbol_name(symbol)[1:])

    def _add_units(self):
        """ Add needed units to the model to allow converting time, voltage and calcium in specific units."""
        for unit_name in self._UNIT_DEFINITIONS:
            try:
                self._model.units.add_custom_unit(unit_name, self._UNIT_DEFINITIONS[unit_name])
            except AssertionError:
                pass  # Unit already exists, but that is not a problem

    def _get_modifiable_parameters(self):
        return self._model.get_symbols_by_rdf((self._PYCMLMETA,
                                              'modifiable-parameter'), 'yes')

    def _get_membrane_voltage_var(self):
        """ Find the membrane_voltage variable"""
        return self._model.get_symbol_by_ontology_term(self._OXMETA, "membrane_voltage")

    def _get_cytosolic_calcium_concentration_var(self):
        """ Find the cytosolic_calcium_concentration variable if it exists"""
        try:
            return self._model.get_symbol_by_ontology_term(self._OXMETA, "cytosolic_calcium_concentration")
        except KeyError:
            self._logger.info(self._model.name + ' has no cytosolic_calcium_concentration')
            return None

    def _get_use_get_intracellular_calcium_concentration(self):
        """ Get wether or not the model has cytosolic_calcium_concentration"""
        try:
            self._model.get_symbol_by_ontology_term(self._OXMETA, "cytosolic_calcium_concentration")
            return True
        except KeyError:
            return False

    def _get_state_variables(self):
        """ Sort the state variables, in similar order to pycml to prevent breaking existing code"""
        return sorted(self._model.get_state_symbols(),
                      key=lambda state_var: self._state_var_key_order(state_var))

    def _get_state_var_conversion(self):
        """ Get conversion factors and substitution dictionary for state variables in Chaste"""
        def sv_conv(sv):
            try:
                return round(self._model.units.get_conversion_factor(self._get_desired_units(sv),
                             from_unit=self._model.units.summarise_units(sv)), 14)
            except errors.DimensionalityError:
                return 1.0

        state_var_factors = {sv: sv_conv(sv) for sv in self._state_vars if sv_conv(sv) != 1.0}
        state_var_subs = {sv: 1 / fac * sv for sv, fac in state_var_factors.items()}
        return state_var_factors, state_var_subs

    def _perform_state_var_conv(self, eq):
        """ Perform state_var conversion in eq for converted state_vars"""
        return eq.subs(self._state_var_subs)

    def _get_membrane_stimulus_current(self):
        """ Find the membrane_stimulus_current variable if it exists"""
        try:
            return self._model.get_symbol_by_ontology_term(self._OXMETA, 'membrane_stimulus_current')
        except KeyError:
            self._logger.info(self._model.name + ' has no membrane_stimulus_current')
            self._is_self_excitatory = len(list(self._model.get_rdf_annotations(subject=self._model.rdf_identity,
                                                predicate=(self._PYCMLMETA, 'is-self-excitatory'), object_='yes'))) > 0
            return None

    def _get_membrane_capacitance(self):
        """ Find membrane_capacitance if the model has it"""
        equation, capacitance_factor = None, 1.0
        # add membrane_capacitance if the model has it
        try:
            # add membrane_capacitance factor
            membrane_capacitance = self._model.get_symbol_by_ontology_term(self._OXMETA, "membrane_capacitance")
            if membrane_capacitance is not None:
                current_units = self._model.units.summarise_units(membrane_capacitance)
                units_to_try = [getattr(self._model.units.ureg, u) for u in self._STIM_UNITS['membrane_capacitance']]
                for desired_units in units_to_try:
                    if current_units.dimensionality == desired_units.dimensionality:
                        capacitance_factor = \
                            self._model.units.get_conversion_factor(desired_units, from_unit=current_units)
                        initial_value = self._model.get_initial_value(membrane_capacitance)
                        equation = sp.Eq(membrane_capacitance, initial_value)
                        break
        except KeyError:
            pass  # no membrane_capacitance
        return equation, capacitance_factor

    def _get_stimulus(self):
        """ Store the stimulus currents in the model"""
        default_stimulus = dict()
        if self._membrane_stimulus_current is not None:
            # Get remaining stimulus current variables If they have metadata use that as key, ortherwise use the name
            # Exclude _membrane_stimulus_current itself so we can treat it seperately
            for eq in self._model.get_equations_for([self._membrane_stimulus_current]):
                if eq.lhs != self._membrane_stimulus_current:
                    ontology_terms = self._model.get_ontology_terms_by_symbol(eq.lhs, self._OXMETA)
                    key = ontology_terms[0] if len(ontology_terms) > 0 else eq.lhs
                    default_stimulus[key] = eq
        return default_stimulus

    def _get_ionic_derivs(self):
        """ Getting the derivative symbols that define V (self._membrane_voltage_var)"""
        # use the RHS of the ODE defining V
        return [x for x in self._model.get_derivative_symbols() if x.args[0] == self._membrane_voltage_var]

    def _get_equations_for_ionic_vars(self):
        """ Get the equations defining the ionic derivatives"""
        # figure out the currents (by finding variables with the same units as the stimulus)
        # Only equations with the same (lhs) units as the STIMULUS_CURRENT are kept.
        # Also exclude membrane_stimulus_current variable itself, and default_stimulus equations (if model has those)
        # Manually recurse down the equation graph (bfs style) if no currents are found
        equations_for_ionic_vars, desired_current_units, stimulus_current_factor = [], None, 1.0
        units_to_try = [getattr(self._model.units.ureg, u) for u in self._STIM_UNITS['membrane_stimulus_current']]
        if self._membrane_stimulus_current is not None:
            membrane_stimulus_units = self._model.units.summarise_units(self._membrane_stimulus_current)
            units_to_try = [u for u in units_to_try if u.dimensionality == membrane_stimulus_units.dimensionality]

        for units in units_to_try:
            if len(equations_for_ionic_vars) > 0:
                break
            equations, old_equations = self._ionic_derivs, None
            while len(equations_for_ionic_vars) == 0 and old_equations != equations:
                old_equations = equations
                equations = self._model.get_equations_for(equations, recurse=False)
                equations_for_ionic_vars = [eq for eq in equations
                                            if ((self._membrane_stimulus_current is None)
                                                or (eq.lhs != self._membrane_stimulus_current
                                                and eq not in self._default_stimulus.values()))
                                            and self._model.units.summarise_units(eq.lhs).dimensionality
                                            == units.dimensionality
                                            and eq.lhs not in self._modifiable_parameters
                                            and eq.lhs not in self._ionic_derivs]
                equations = [eq.lhs for eq in equations]
            desired_current_units = units
        if self._membrane_stimulus_current is not None:
            stimulus_current_factor = \
                self._model.units.get_conversion_factor(desired_current_units, from_unit=membrane_stimulus_units)
        # Reverse topological order is more similar (though not necessarily identical) to pycml
        equations_for_ionic_vars.reverse()
        return equations_for_ionic_vars, desired_current_units, \
            str(desired_current_units) != self._STIM_UNITS['membrane_stimulus_current'][0], stimulus_current_factor

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the equations defining the ionic derivatives and all dependant equations"""
        # Remove equations where lhs is a modifiable parameter or stimulus vars
        extended_equations_for_ionic_vars = \
            [eq for eq in
                self._model.get_equations_for([ionic_var_eq.lhs for ionic_var_eq in self._equations_for_ionic_vars])
                if eq.lhs not in self._modifiable_parameters
                and eq.lhs not in [st.lhs for st in self._default_stimulus.values()]]
        if self._use_capacitance_i_ionic and self._membrane_capacitance is not None \
                and self._membrane_capacitance.lhs not in [eq.lhs for eq in extended_equations_for_ionic_vars]:
            extended_equations_for_ionic_vars.insert(0, self._membrane_capacitance)
        return extended_equations_for_ionic_vars

    def _get_y_derivatives(self):
        """ Get derivatives for state variables"""
        return sorted(self._model.get_derivative_symbols(),
                      key=lambda state_var: self._state_var_key_order(state_var))

    def _get_y_derivatives_voltage(self):
        """ Get derivatives for V (self._membrane_voltage_var)"""
        return [deriv for deriv in self._y_derivatives if deriv.args[0] == self._membrane_voltage_var]

    def _get_y_derivatives_excl_voltage(self):
        """ Get derivatives for state variables, excluding V (self._membrane_voltage_var)"""
        return [deriv for state_var in self._state_vars for deriv in self._y_derivatives
                if deriv.args[0] == state_var and deriv.args[0] != self._membrane_voltage_var]

    def _get_derivative_eqs_voltage(self):
        """ Get equations defining the derivatives for V (self._membrane_voltage_var)"""
        # Sort the derivative equations to get the derivaives themselves last
        # Remove equations where lhs is a modifiable parameter
        return [eq for eq in sorted(self._model.get_equations_for(self._y_derivatives_voltage), key=lambda deriv:
                                    isinstance(deriv.lhs, sp.Derivative)) if eq.lhs not in self._modifiable_parameters]

    def _get_derivative_eqs_exlc_voltage(self):
        """ Get equations defining the derivatives excluding V (self._membrane_voltage_var)"""
        # Sort the derivative equations to get the derivaives themselves last
        # Remove equations where lhs is a modifiable parameter
        return [eq for eq in sorted(self._model.get_equations_for(self._y_derivatives_excl_voltage), key=lambda deriv:
                                    isinstance(deriv.lhs, sp.Derivative)) if eq.lhs not in self._modifiable_parameters]

    def _get_derivative_equations(self):
        """ Get equations defining the derivatives including  V (self._membrane_voltage_var)"""
        # Sort the derivative equations to get the derivaives themselves last
        return [eq for eq in sorted(self._model.get_equations_for(self._y_derivatives), key=lambda deriv:
                                    isinstance(deriv.lhs, sp.Derivative)) if eq.lhs not in self._modifiable_parameters]

    def _format_modifiable_parameters(self):
        return [{'units': self._model.units.summarise_units(param),
                 'comment_name': self._name_printer.doprint(param), 'name': str(param).split("$")[-1],
                 'initial_value': self._model.get_initial_value(param)} for param in self._modifiable_parameters]

    def _format_state_variables(self):
        """ Get equations defining the derivatives including  V (self._membrane_voltage_var)"""
        # Filter unused state vars for ionic variables
        ionic_var_symbols = set()
        for eq in self._extended_equations_for_ionic_vars:
            ionic_var_symbols.update(eq.rhs.free_symbols)

        y_deriv_symbols = set()
        for eq in self._derivative_equations:
            y_deriv_symbols.update(eq.rhs.free_symbols)

        return [{'var': self._printer.doprint(var),
                 'initial_value': str(self._model.get_initial_value(var) * self._state_var_conversion_factors[var])
                if var in self._state_var_conversion_factors else str(self._model.get_initial_value(var)),
                 'units': str(self._model.units.summarise_units(var)),
                 'in_ionic': var in ionic_var_symbols,
                 'in_y_deriv': var in y_deriv_symbols}
                for var in self._state_vars]

    def _format_default_stimulus(self):
        """ Format eqs for stimulus_current for outputting to chaste code"""
        formatted_default_stimulus = dict()
        for key, eq in self._default_stimulus.items():
            # exclude (equations for) variables that don't have annotation
            if self._model.has_ontology_annotation(eq.lhs, self._OXMETA):
                formatted_default_stimulus[key] = []
                factor = 1.0
                rhs_multiplier = ''
                current_units = self._model.units.summarise_units(eq.lhs)
                units = None
                if key in self._STIM_UNITS:
                    units_to_try = [getattr(self._model.units.ureg, u) for u in self._STIM_UNITS[key]]
                    rhs_multiplier = ''
                    for i in range(len(units_to_try)):
                        if units_to_try[i].dimensionality == current_units.dimensionality:
                            units = units_to_try[i]
                            factor = self._model.units.get_conversion_factor(units, from_unit=current_units)
                            # Check if there is a rhs multiplier for this key and unit combo (e.g. for the amplitude:
                            if key in self._STIM_RHS_MULTIPLIER and str(units) in self._STIM_RHS_MULTIPLIER[key]:
                                rhs_multiplier = self._STIM_RHS_MULTIPLIER[key][str(units)]
                            if key in self._STIM_CONVERSION_RULES and str(units) in self._STIM_CONVERSION_RULES[key]:
                                additional_eqs = []

                                # Apply conversion rules if we have any
                                units, factor, eq, additional_eqs = \
                                    self._STIM_CONVERSION_RULES['membrane_stimulus_current_amplitude']['uA'](
                                        self, current_units, factor, eq)
                                formatted_default_stimulus[key].extend(additional_eqs)
                            break
                rhs = eq.rhs if factor == 1.0 else factor * eq.rhs
                self._in_interface.append(eq.lhs)
                formatted_default_stimulus[key].append({'lhs': self._printer.doprint(eq.lhs),
                                                        'rhs': self._printer.doprint(rhs) + rhs_multiplier,
                                                        'units': str(units if units is not None else current_units)
                                                        })
        return formatted_default_stimulus

    def _format_equations_for_ionic_vars(self):
        """ Format equations ionic derivatives"""
        return [{'var': self._printer.doprint(eq.lhs),
                 'units': str(self._model.units.summarise_units(eq.lhs)),
                 'conversion_factor':
                     self._model.units.get_conversion_factor(self._desired_current_units,
                                                             from_unit=self._model.units.summarise_units(eq.lhs))}
                for eq in self._equations_for_ionic_vars]

    def _format_extended_equations_for_ionic_vars(self):
        """ Format equations and dependant equations ionic derivatives"""

        def print_rhs(eq):
            """ Print the rhs, set _membrane_stimulus_current to 0.0"""
            if eq.lhs != self._membrane_stimulus_current:
                return self._printer.doprint(self._perform_state_var_conv(eq.rhs))
            else:
                return 0.0
        # Format the state ionic variables
        formated_extended_equations_for_ionic_vars = \
            [{'lhs': self._printer.doprint(eq.lhs), 'rhs': print_rhs(eq),
              'units': self._model.units.summarise_units(eq.lhs)} for eq in self._extended_equations_for_ionic_vars]

        ionic_rhs = '(' if self._use_capacitance_i_ionic else ''
        ionic_rhs += '(' if self._use_capacitance_i_ionic and self._membrane_capacitance is not None else ''
        for i in range(len(self._formatted_equations_for_ionic_vars)):
            if i != 0:
                ionic_rhs += ' + '
            if self._formatted_equations_for_ionic_vars[i]['conversion_factor'] != 1.0:
                ionic_rhs += str(self._formatted_equations_for_ionic_vars[i]['conversion_factor']) + ' * '
            ionic_rhs += self._formatted_equations_for_ionic_vars[i]['var']
        if self._use_capacitance_i_ionic:
            if self._membrane_capacitance is not None:
                ionic_rhs += ') / '
                factor = self._membrane_capacitance_factor
                if factor != 1.0:
                    ionic_rhs += '(' + str(factor) + ' * '
                ionic_rhs += self._printer.doprint(self._membrane_capacitance.lhs)
                if factor != 1.0:
                    ionic_rhs += ')'
            ionic_rhs += ')'
            ionic_rhs = '(' + str(sp.simplify(ionic_rhs)) + ')'  # simplify
            ionic_rhs += ' * HeartConfig::Instance()->GetCapacitance()'
        i_ionic = sp.sympify('_i_ionic')
        self._in_interface.append(i_ionic)
        formated_extended_equations_for_ionic_vars.append(
            {'lhs': self._printer.doprint(i_ionic),
             'rhs': ionic_rhs, 'units': 'uA_per_cm2'})
        return formated_extended_equations_for_ionic_vars

    def _format_y_derivatives(self):
        """ Format y_derivatives for writing to chaste output"""
        self._in_interface.extend(self._y_derivatives)
        return [self._printer.doprint(deriv) for deriv in self._y_derivatives]

    def _get_desired_units(self, term):
        """ Helper function to return units we should convert variables to, to work in chaste.

        V in mV, time in ms and cytosolic_calcium_concentration in millimolar)
        """
        units = self._model.units.summarise_units(term)
        # Time in ms
        if term == self._time_variable:
            units = self._model.units.ureg.millisecond
        # calcium in millimolar (cytosolic_calcium_concentration)
        elif term == self._cytosolic_calcium_concentration_var:
            units = self._model.units.ureg.millimolar
        # voltage in mV
        elif term == self._membrane_voltage_var:
            units = self._model.units.ureg.millivolt
        return units

    def _format_derivative_equations(self):
        """Format derivative equations for chaste output"""
        # exclude ionic currents
        equations = []
        d_eqs = [eq for eq in self._derivative_equations
                 if eq not in self._default_stimulus.values()]

        subs_dict = {eq.lhs: eq.rhs for eq in d_eqs}
        negate_stimulus = False
        # loop through equations backwards as derivatives are last
        for i in range(len(d_eqs) - 1, - 1, - 1):
            is_voltage = False
            factor = 1.0
            units = self._model.units.summarise_units(d_eqs[i].lhs)
            rhs_divider = ''
            in_membrane_voltage = d_eqs[i] not in self._derivative_eqs_exlc_voltage
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
                    is_voltage = True
                    for s in d_eqs[i].rhs.free_symbols:
                        if self._desired_current_units.dimensionality == \
                                self._model.units.summarise_units(s).dimensionality:
                            subs_dict[s] = 0  # other currents = 0
                        else:
                            subs_dict[s] = 1  # other variables = 1
                    subs_dict[self._membrane_stimulus_current] = 1  # stimulus current = 1
                    negate_stimulus = d_eqs[i].rhs.subs(subs_dict) > 0.0
                # Convert voltage to mV, time to mS and calcium to millimolar
                dividend_unit = self._get_desired_units(d_eqs[i].lhs.args[0])
                divisor_unit = self._get_desired_units(d_eqs[i].lhs.args[1][0])
                units = dividend_unit / divisor_unit
                units_from = self._model.units.summarise_units(d_eqs[i].lhs)
                try:
                    factor = self._model.units.get_conversion_factor(units, from_unit=units_from)
                except errors.DimensionalityError:
                    factor = 1.0
            if d_eqs[i].lhs == self._membrane_stimulus_current:
                factor = 1.0
                # strip out var from time variable name as printing will add it back later
                GetIntracellularAreaStimulus = sp.Function('GetIntracellularAreaStimulus')
                area = GetIntracellularAreaStimulus(self._time_variable)
                if negate_stimulus:
                    area = -area

                if self._use_capacitance_i_ionic:
                    rhs_divider = '/ HeartConfig::Instance()->GetCapacitance()'
                if self._use_capacitance_i_ionic and self._membrane_capacitance is not None:
                    stim_current_eq_rhs = area * self._membrane_capacitance.lhs
                    fac = self._membrane_capacitance_factor / self._membrane_stimulus_current_factor
                    if fac != 1.0:
                        stim_current_eq_rhs *= fac
                else:
                    stim_current_eq_rhs = area
                    fac = 1 / self._membrane_stimulus_current_factor
                    if fac != 1.0:
                        stim_current_eq_rhs *= fac

                d_eqs[i] = sp.Eq(d_eqs[i].lhs, sp.simplify(stim_current_eq_rhs))

            # Format the equation and put it at the front of the result list to keep order (we're looping backwards)
            equations.insert(0, {'lhs': d_eqs[i].lhs,
                                 'factor': factor,
                                 'rhs': self._perform_state_var_conv(d_eqs[i].rhs),
                                 'units': units,
                                 'rhs_divider': rhs_divider,
                                 'in_membrane_voltage': in_membrane_voltage,
                                 'is_voltage': is_voltage})

        for i in range(len(equations)):
            if equations[i]['factor'] != 1.0:
                for j in range(i + 1, len(equations)):
                    equations[j]['rhs'] =\
                        equations[j]['rhs'].subs({equations[i]['lhs']:
                                                 (1 / equations[i]['factor'] * equations[i]['lhs'])})
        for i in range(len(equations)):
            if equations[i]['factor'] != 1.0:
                equations[i]['rhs'] = sp.simplify(equations[i]['factor'] * equations[i]['rhs'])
            equations[i]['rhs'] = \
                self._printer.doprint(equations[i]['rhs']) + equations[i]['rhs_divider']
            equations[i]['lhs'] = self._printer.doprint(equations[i]['lhs'])

        return equations

    def _format_ode_system_info(self):
        """ Format general ode system info for chaste output"""
        ontology_terms = self._model.get_ontology_terms_by_symbol(self._time_variable, namespace_uri=self._OXMETA)
        name = ontology_terms[0] if len(ontology_terms) > 0 else self._name_printer.doprint(self._time_variable)
        free_variable = {'name': name,
                         'units': self._get_desired_units(self._time_variable),
                         'system_name': self._model.name,
                         'var_name': self._printer.doprint(self._time_variable)}
        system_info = \
            [{'name': self._model.get_ontology_terms_by_symbol(var, self._OXMETA)[0]
              if self._model.has_ontology_annotation(var, self._OXMETA) else self._name_printer.doprint(var),
              'initial_value': str(self._model.get_initial_value(var))
                if var not in self._state_var_conversion_factors
                else str(self._state_var_conversion_factors[var] * self._model.get_initial_value(var)),
              'units': self._get_desired_units(var)}
             for var in self._state_vars]

        named_attributes = []
        named_attrs = self._model.get_rdf_annotations(subject=self._model.rdf_identity,
                                                      predicate=(self._PYCMLMETA, 'named-attribute'))
        for s, p, attr in named_attrs:
            name = self._model.get_rdf_value(subject=attr, predicate=(self._PYCMLMETA, 'name'))
            value = self._model.get_rdf_value(subject=attr, predicate=(self._PYCMLMETA, 'value'))
            named_attributes.append({'name': name, 'value': value})

        named_attributes = sorted(named_attributes, key=lambda a: a['name'])
        return free_variable, system_info, named_attributes

    def _state_var_key_order(self, var):
        """Returns a key to order state variables in the same way as pycml does"""
        if isinstance(var, sp.Derivative):
            var = var.args[0]
        if var == self._membrane_voltage_var:
            return self._MEMBRANE_VOLTAGE_INDEX
        elif var == self._cytosolic_calcium_concentration_var:
            return self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX
        else:
            return self._MEMBRANE_VOLTAGE_INDEX + self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX + 1


class NormalChasteModel(ChasteModel):
    """ Holds information specific for the Normal model type"""

    def __init__(self, model, class_name, file_name):
        super().__init__(model, class_name, file_name)

    def generate_chaste_code(self):
        """ Generates and stores chaste code for the Normal model"""

        # Generate hpp for model
        template = cg.load_template('chaste', 'normal_model.hpp')
        self.generated_hpp = template.render({
            'model_name': self._model.name,
            'class_name': self.class_name,
            'dynamically_loadable': self.dynamically_loadable,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'default_stimulus_equations': self._formatted_default_stimulus,
            'use_get_intracellular_calcium_concentration': self._use_get_intracellular_calcium_concentration,
            'free_variable': self._free_variable})

        # Generate cpp for model
        template = cg.load_template('chaste', 'normal_model.cpp')
        self.generated_cpp = template.render({
            'model_name': self._model.name,
            'file_name': self.file_name,
            'class_name': self.class_name,
            'dynamically_loadable': self.dynamically_loadable,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'default_stimulus_equations': self._formatted_default_stimulus,
            'use_get_intracellular_calcium_concentration': self._use_get_intracellular_calcium_concentration,
            'membrane_voltage_index': self._MEMBRANE_VOLTAGE_INDEX,
            'cytosolic_calcium_concentration_index': self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX,
            'state_vars': self._formatted_state_vars,
            'ionic_interface_vars': self._formatted_equations_for_ionic_vars,
            'ionic_vars': self._formatted_extended_equations_for_ionic_vars,
            'y_derivative_equations': self._formatted_derivative_eqs,
            'y_derivatives': self._formatted_y_derivatives,
            'use_capacitance_i_ionic': self._use_capacitance_i_ionic,
            'free_variable': self._free_variable,
            'ode_system_information': self._ode_system_information,
            'modifiable_parameters': self._formatted_modifiable_parameters,
            'named_attributes': self._named_attributes})


class OptChasteModel(ChasteModel):
    pass


class Analytic_jChasteModel(ChasteModel):
    pass


class Numerical_jChasteModel(ChasteModel):
    pass


class BEOptChasteModel(ChasteModel):
    pass
