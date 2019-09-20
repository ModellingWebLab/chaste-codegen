#
# Functions related to generating model code for Chaste.
#

# TODO: apply unit conversions
# y derivatives msthematics
# Unit conversion for state variables voltage, time, cytosolic_calcium_concentration state vars
# capacitance in UseCellMLDefaultStimulus, using oxmeta see aslanidi_model_2009
# GetIntracellularAreaStimulus with conversion & different time unit see jafri_rice_winslow_1998 (-), or aslanidi_model_2009
# * period     // millisecond done, to check
# * duration   // millisecond, to check
# * amplitude  // uA_per_cm2, to check
# * offset     // millisecond, to check
# * end     // millisecond, to check

import logging
import os
import time
import sympy as sp
import enum
import weblab_cg as cg
from pint import errors
import copy

logging.getLogger().setLevel(logging.INFO)


class ChasteModel(object):
    _MEMBRANE_VOLTAGE_INDEX = 0
    _CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX = 1
    _OXMETA = "https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#"

    _UNIT_DEFINITIONS = {'uA_per_cm2': [{'prefix': 'micro', 'units': 'ampere'}, {'exponent': '-2', 'prefix': 'centi', 'units': 'metre'}],
                         'uA_per_uF': [{'prefix': 'micro', 'units': 'ampere'}, {'exponent': '-1', 'prefix': 'micro', 'units': 'farad'}],
                         'millisecond': [{'prefix': 'milli', 'units': 'second'}],
                         'millimolar': [{'units': 'mole', 'prefix': 'milli'}, {'units': 'litre', 'exponent': '-1'}],
                         'millivolt': [{'prefix': 'milli', 'units': 'volt'}]}

    _STIMULUS_CURRENT = "membrane_stimulus_current"
    _STIMULUS_UNITS = {'membrane_stimulus_current_period': 'millisecond', 'membrane_stimulus_current_duration': 'millisecond', 
                       'membrane_stimulus_current_amplitude': 'uA_per_cm2', 'membrane_stimulus_current_offset': 'millisecond',
                       'membrane_stimulus_current_end': 'millisecond'}
    _STIMULUS_SECONDARY_UNITS = {'membrane_stimulus_current_amplitude': 'uA_per_uF'}
    _STIMULUS_RHS_MULTIPLIER = {'membrane_stimulus_current_amplitude': ' * HeartConfig::Instance()->GetCapacitance()'}

    def __init__(self, model, model_name_for_filename, class_name):
        """Initialise a ChasteModel instance
        Arguments

        ``model``
            A :class:`cellmlmanip.Model` object.
        ``output_path``
            The path to store the generated model code at.
            (Just the path, excluding the file name as file name will be determined by the model_name)
        ``model_name_for_filename``
            The model name as you want it to apear in generated cpp and hpp files.
        """
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)        

        # Store parameters for future reference
        self._model = model
        self._model_name_for_filename = model_name_for_filename
        self._class_name = class_name

        self._add_units()

        self._membrane_voltage_var = self._get_membrane_voltage_var()
        self._cytosolic_calcium_concentration_var = self._get_cytosolic_calcium_concentration_var()
        self._state_vars = self._get_state_variables()
        self._default_stimulus = self._get_stimulus_currents()
        self._desired_ionic_current_units = self._get_stimulus_currents_desired_units()
        self._equations_for_ionic_vars = self._get_equations_for_ionic_vars()
        self._extended_equations_for_ionic_vars = self._get_extended_equations_for_ionic_vars()

        self._y_derivatives_voltage = self._get_y_derivatives_voltage()
        self._y_derivatives_excl_voltage = self._get_y_derivatives_excl_voltage()
        self._y_derivatives = self._get_y_derivatives()
        self._derivative_eqs_exlc_voltage = self._get__derivative_eqs_exlc_voltage()
        self._derivative_eqs_voltage = self._get__derivative_eqs_voltage()
        self._use_get_intracellular_calcium_concentration = self._get_use_get_intracellular_calcium_concentration()

        self._add_printers()
        self._format_state_variables()
        self._format_stimulus_currents()
        self._format_equations_for_ionic_vars()
        self._format_y_derivatives()
        self._format_derivative_equations()
        self._format_system_info()

    def _add_printers(self):
        # Initialise Printers for outputting chaste code
        # Printer for printing chaste state variable assignments (var_chaste_interface prefix)
        self._var_chaste_interface_printer = cg.ChastePrinter(lambda symbol: 'var_chaste_interface_' + str(symbol).replace('$','__'),
                                                              lambda deriv: 'd_dt_chaste_interface_' + (str(deriv.expr).replace('$','__')
                                                              if isinstance(deriv, sp.Derivative) else str(deriv).replace('$','__')))

        # Printer for printing chaste regular variable assignments (var_ prefix)
        self._var_printer = cg.ChastePrinter(lambda symbol: 'var' + str(symbol).replace('$','__'),
                                             lambda deriv: 'd_dt' + (str(deriv.expr).replace('$','__')
                                             if isinstance(deriv, sp.Derivative) else str(deriv).replace('$','__')))

        # Printer for printing chaste regular variable assignments without the var_ prefix
        self._name_printer = cg.ChastePrinter(lambda symbol: str(symbol)[1:].replace('$','__'))

    def _add_units(self):
        # Add all neded units to the model (for conversion) if they don't yet exist
        for unit_name in self._UNIT_DEFINITIONS:
            self._model.units.add_preferred_custom_unit_name(unit_name, self._UNIT_DEFINITIONS[unit_name])

    def _get_membrane_voltage_var(self):
        return self._model.get_symbol_by_ontology_term(self._OXMETA, "membrane_voltage")

    def _get_cytosolic_calcium_concentration_var(self):
        try:
            return self._model.get_symbol_by_ontology_term(self._OXMETA, "cytosolic_calcium_concentration")
        except KeyError:
            self._logger.debug(self._model.name + ' has no cytosolic_calcium_concentration')
            return None

    def _get_state_variables(self):
        # function used to order state variables in the same way as pycml does (for easy comparison)
        def state_var_key_order(membrane_voltage_var, cai_var, var):
            if var == membrane_voltage_var:
                return self._MEMBRANE_VOLTAGE_INDEX
            elif var == cai_var:
                return self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX
            else:
                return self._MEMBRANE_VOLTAGE_INDEX + self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX + 1

        # Sort the state variables, to make sure they have similar order to pycml
        return sorted(self._model.get_state_symbols(),
                      key=lambda state_var: state_var_key_order(self._membrane_voltage_var,
                                                                self._cytosolic_calcium_concentration_var, state_var))

    def _get_stimulus_currents(self):
        # Store the stimulus current
        default_stimulus = dict()
        try:
            default_stimulus['membrane_stimulus_current'] = self._model.get_symbol_by_ontology_term(self._OXMETA, self._STIMULUS_CURRENT)
        except KeyError:
            self._logger.debug(self._model.name + ' has no membrane_stimulus_current')
            self._membrane_stimulus_current_units = None
            return default_stimulus # The model has no membrane_stimulus_current, so we cant get further membrane_stimulus information
        finally:
            # Get stimulus current units
            self._membrane_stimulus_current_units = self._model.units.summarise_units(default_stimulus['membrane_stimulus_current'])
            
            # Get remaining stimulus current variables If they have metadata use that as key, ortherwise use the name
            for eq in self._model.get_equations_for([default_stimulus['membrane_stimulus_current']], sort_by_input_symbols=True):
                ontology_terms = self._model.get_ontology_terms_by_symbol(eq.lhs, self._OXMETA)
                key = ontology_terms[0] if len(ontology_terms) > 0 else eq.lhs
                default_stimulus[key] = eq
            return default_stimulus

    def _get_stimulus_currents_desired_units(self):
        # Get stimulus current and set up dictionary to store in other stimulus current variables 
        try:
            self._model.units.get_conversion_factor(1 * self._membrane_stimulus_current_units, self._model.units.ureg.uA_per_cm2)
            self._use_capacitance_i_ionic = False
            return self._model.units.ureg.uA_per_cm2
        except errors.DimensionalityError:
            self._use_capacitance_i_ionic = True
            return self._model.units.ureg.uA_per_uF

    def _get_equations_for_ionic_vars(self):
        # Getting the equations for const definitions for GetIIonic
        # use the RHS of the ODE defining V
        ionic_derivatives = [x for x in self._model.get_derivative_symbols() if x.args[0] == self._membrane_voltage_var]
        # figure out the currents (by finding variables with the same units
        # as the stimulus) (without lexicographical_sort
        # Only equations with the same (lhs) units as the STIMULUS_CURRENTt are keps.
        # Also exclude the membrane_stimulus_current variable itself, and default_stimulus equations (if he model has those)
        equations_for_ionic_vars = [eq for eq in self._model.get_equations_for(ionic_derivatives, sort_by_input_symbols=True)
                                    if ((not 'membrane_stimulus_current' in self._default_stimulus)
                                    or (eq != self._default_stimulus['membrane_stimulus_current'] and eq not in self._default_stimulus.values()))
                                    and self._model.units.summarise_units(eq.lhs) == self._membrane_stimulus_current_units]
        # reverse toplological order is more similar (though not necessarily identical) to pycml
        equations_for_ionic_vars.reverse()
        return equations_for_ionic_vars

    def _get_extended_equations_for_ionic_vars(self):
        return self._model.get_equations_for([ionic_var_eq.lhs for ionic_var_eq in self._equations_for_ionic_vars], sort_by_input_symbols=True)

    def _get_y_derivatives_voltage(self):
        # Get derivatives for state variables in the same order as the state variables, buth excluding voltage and voltage only (voltage is treated seperately)
        return [deriv for deriv in self._model.get_derivative_symbols() if deriv.args[0] == self._membrane_voltage_var]

    def _get_y_derivatives_excl_voltage(self):
        # Get derivatives for state variables in the same order as the state variables, buth excluding voltage and voltage only (voltage is treated seperately)
        return [deriv for state_var in self._state_vars for deriv in self._model.get_derivative_symbols() if deriv.args[0] == state_var and deriv.args[0] != self._membrane_voltage_var]

    def _get_y_derivatives(self):
        # Get derivatives for state variables in the same order as the state variables, buth excluding voltage and voltage only (voltage is treated seperately)
        return self._y_derivatives_voltage + self._y_derivatives_excl_voltage

    def _get__derivative_eqs_exlc_voltage(self):       
        # Get equations for the derivatives, excluding default_stimulus equations and y derivatives themselves (they will be treated seperately)
        return [deriv for deriv in self._model.get_equations_for(self._y_derivatives_excl_voltage, sort_by_input_symbols=True) if not deriv.lhs in self._y_derivatives_excl_voltage]

    def _get__derivative_eqs_voltage(self):
        # Get equations for the derivatives, excluding default_stimulus equations and y derivatives themselves (they will be treated seperately)
        return [deriv for deriv in self._model.get_equations_for(self._y_derivatives_voltage, sort_by_input_symbols=True) if not deriv.lhs in self._y_derivatives_voltage]

    def _get_derivative_equations(self):
        return self._derivative_eqs_voltage + _derivative_eqs_exlc_voltage

    def _get_use_get_intracellular_calcium_concentration(self):
        # Check if the model has cytosolic_calcium_concentration,
        # if so we need to add GetIntracellularCalciumConcentration, otherwise leave blank
        try:
            self._model.get_symbol_by_ontology_term(self._OXMETA, "cytosolic_calcium_concentration")
            return True
        except KeyError:
            return False

    def _format_derivative_equations(self):
        def format_deriv_eq(deriv, in_membrane_voltatge):
            return {'lhs': self._var_printer.doprint(deriv.lhs),
                    'rhs': self._var_printer.doprint(deriv.rhs),
                    'units': str(self._model.units.summarise_units(deriv.lhs)),
                    'in_membrane_voltatge': in_membrane_voltatge}
        self._fomatted_derivative_eqs = [format_deriv_eq(deriv, False) for deriv in self._derivative_eqs_exlc_voltage]
        self._fomatted_derivative_eqs.extend([format_deriv_eq(deriv, True) for deriv in self._derivative_eqs_voltage])       

    def _format_y_derivatives(self):
        # Format y_derivatives for writing to chaste output
        self._formatted_y_derivatives = [self._var_chaste_interface_printer.doprint(deriv) for deriv in self._y_derivatives]

    def _format_equations_for_ionic_vars(self):
        self._formatted_equations_for_ionic_vars = [{'lhs': self._var_chaste_interface_printer.doprint(eq.lhs),
                                                     'rhs': self._var_printer.doprint(eq.lhs),
                                                     'units': str(self._model.units.summarise_units(eq.lhs)),
                                                     'conversion_factor': self._model.units.get_conversion_factor(1 * self._model.units.summarise_units(eq.lhs), self._desired_ionic_current_units)} 
                                                     for eq in self._equations_for_ionic_vars]
                                                             
        # Format the state ionic variables
        self._formatted_extended_equations_for_ionic_vars = []
        # Only write equations once
        used_symbols = []
        # Some symbols will need substituting while printing ionic variables
        ionic_subs_dict = {}        
        for eq_ionic in self._extended_equations_for_ionic_vars:
            # Check if interface link vars are needed
            for v in self._model.get_symbols(eq_ionic.rhs):
                if v in self._state_vars:
                    #used_symbols.append(v)
                    # Link variable names start with the first bit of the equation they relate to (the component) followed by the variable name they are linking
                    link_var_name = eq_ionic.lhs.name.split('$')[0] + '$' + v.name.split('$')[1]
                    link_var = sp.Dummy(link_var_name)
                    ionic_subs_dict[v] = link_var
                    if link_var not in used_symbols:
                        used_symbols.append(link_var)
                        self._formatted_extended_equations_for_ionic_vars.append({
                                             'lhs': self._var_printer.doprint(link_var),
                                             'rhs': self._var_chaste_interface_printer.doprint(v),
                                             'units': str(self._model.units.summarise_units(v))
                                            })
            self._formatted_extended_equations_for_ionic_vars.append({
                                         'lhs': self._var_printer.doprint(eq_ionic.lhs),
                                         'rhs': self._var_printer.doprint(eq_ionic.rhs.subs(ionic_subs_dict)),
                                         'units': str(self._model.units.summarise_units(eq_ionic.lhs))
                                        })

    def _format_stimulus_currents(self):   
        self._formatted_default_stimulus = dict()   
        for key in self._default_stimulus:
            formatted_equations = []
            eq = self._default_stimulus[key]            
            units = getattr(self._model.units.ureg, self._STIMULUS_UNITS[key]) if key in self._STIMULUS_UNITS else None
            rhs_multiplier = ''            
            secondary_units = getattr(self._model.units.ureg, self._STIMULUS_SECONDARY_UNITS[key])  if key in self._STIMULUS_SECONDARY_UNITS else None
            secondary_unit_rhs_multiplier = self._STIMULUS_RHS_MULTIPLIER[key] if key in self._STIMULUS_RHS_MULTIPLIER else None
            factor = None
            current_units = self._model.units.summarise_units(eq.lhs)
            if units is not None:
                try:
                    # Try unit conversion -- ultimately this should be sorted in cellmlmanip?
                    if current_units != units:
                        factor = self._model.units.get_conversion_factor(1 * current_units, units)
                except errors.DimensionalityError:
                    # some variables such as stimmulus amplitude might be in different units and need multiplying e.g. with capacitance
                    if secondary_units is not None and current_units != secondary_units:
                        factor = self._model.units.get_conversion_factor(1 * current_units, secondary_units)
                        # Just so we can get the correct comment in the output
                        units = secondary_units
                    rhs_multiplier = secondary_unit_rhs_multiplier
            # Add intermediate conversion equation
            if factor is not None:
                converter_var = sp.Dummy(eq.lhs.name + '_converter')
                formatted_equations.append({'lhs': self._var_printer.doprint(eq.lhs),
                                            'rhs': self._var_printer.doprint(eq.rhs),
                                            'units': str(current_units)})
                formatted_equations.append({'lhs': self._var_chaste_interface_printer.doprint(converter_var),
                                                'rhs': self._var_printer.doprint(eq.lhs),
                                                'units': str(current_units)})
            if factor is not None:
                rhs = self._var_chaste_interface_printer.doprint(factor) + ' * ' + self._var_chaste_interface_printer.doprint(converter_var)
            else:
                rhs = self._var_chaste_interface_printer.doprint(eq.rhs)
            formatted_equations.append({'lhs': self._var_chaste_interface_printer.doprint(eq.lhs),
                                        'rhs': rhs + rhs_multiplier,
                                        'units': str(units if not units is None else current_units)
                                        })
            self._formatted_default_stimulus[key] = formatted_equations

    def _format_state_variables(self):
        def format_state_var(var, in_ionic, in_y_deriv):
            return {'var': self._var_chaste_interface_printer.doprint(var),
                    'initial_value': str(self._model.get_initial_value(var)),
                    'units': str(self._model.units.summarise_units(var)),
                    'in_ionic': in_ionic,
                    'in_y_deriv': in_y_deriv}

        # Filter unused state vars for ionic variables
        used_vars_ionic = self._get_symbols(self._extended_equations_for_ionic_vars)       
        used_y_deriv = self._get_symbols(self._model.get_equations_for(self._y_derivatives))

        # Format the state variables Keep order, add ones used in getIonic first
        self._formatted_state_vars=[]
        for var in self._state_vars:
            if var in used_vars_ionic:
                self._formatted_state_vars.append(format_state_var(var, in_ionic=True, in_y_deriv=var in used_y_deriv))

        # Now add the ones used in y derivatives only
        for var in self._state_vars:
            if var not in used_vars_ionic and var in used_y_deriv:
                self._formatted_state_vars.append(format_state_var(var, in_ionic=False, in_y_deriv=True))                

    def _format_system_info(self):
        self._free_variable = {'name': self._name_printer.doprint(self._model.get_free_variable_symbol()),
                              'units': self._model.units.summarise_units(self._model.get_free_variable_symbol()),
                              'system_name': self._model.name}
        self._ode_system_information =[{'name': self._model.get_ontology_terms_by_symbol(var, self._OXMETA)[0] if self._model.has_ontology_annotation(var, self._OXMETA) else self._name_printer.doprint(var),
                                       'initial_value': str(self._model.get_initial_value(var)),
                                       'units': str(self._model.units.summarise_units(var))}
                                        for var in self._state_vars]

    def _get_symbols(self, exprs: list) -> set:
        symbols = set()
        for exp in exprs:
            symbols = symbols.union(self._model.get_symbols(exp.rhs))
        return symbols
                
    def write_chaste_code(self, output_path):
        raise NotImplementedError("Chatse models should not be written directly, instead use of of the specific model types!")

class NormalChasteModel(ChasteModel):
    def __init__(self, model, model_name_for_filename, class_name):
        super().__init__(model, model_name_for_filename, class_name)

    def write_chaste_code(self, output_path):
        # Get full OS path to output models to and create it if it doesn't exist
        output_path = os.path.join(output_path)
        try:
            os.makedirs(output_path)
        except FileExistsError:
            pass

        hhp_file_path = os.path.join(output_path, self._model_name_for_filename + ".hpp")
        cpp_file_path = os.path.join(output_path, self._model_name_for_filename + ".cpp")        

        # Generate hpp for model
        template = cg.load_template('chaste', 'normal_model.hpp')
        with open(hhp_file_path, 'w') as f:
            f.write(template.render({
                'model_name_from_file': self._model_name_for_filename,
                'class_name': self._class_name,
                'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'default_stimulus_equations': self._formatted_default_stimulus,
                'use_get_intracellular_calcium_concentration': self._use_get_intracellular_calcium_concentration,
            }))

        # Generate cpp for model
        template = cg.load_template('chaste', 'normal_model.cpp')
        with open(cpp_file_path, 'w') as f:
            f.write(template.render({
                'model_name_from_file': self._model_name_for_filename,
                'class_name': self._class_name,
                'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'default_stimulus_equations': self._formatted_default_stimulus,
                'use_get_intracellular_calcium_concentration': self._use_get_intracellular_calcium_concentration,
                'membrane_voltage_index': self._MEMBRANE_VOLTAGE_INDEX,
                'cytosolic_calcium_concentration_index': self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX,
                'state_vars': self._formatted_state_vars,
                'ionic_interface_vars': self._formatted_equations_for_ionic_vars,
                'ionic_vars': self._formatted_extended_equations_for_ionic_vars,
                'y_derivative_equations': self._formatted_extended_equations_for_ionic_vars,
                'y_derivatives': self._formatted_y_derivatives,
                'use_capacitance_i_ionic': self._use_capacitance_i_ionic,
                'free_variable': self._free_variable,
                'ode_system_information': self._ode_system_information
            }))


class OptChasteModel(ChasteModel):
    def __init__(self, model, model_name_for_filename, class_name):
        super().__init__(model, model_name_for_filename, class_name)

    def write_chaste_code(self, output_path):
        raise NotImplementedError("TODO Not yet implemented!")

class Analytic_jChasteModel(ChasteModel):
    def __init__(self, model, model_name_for_filename, class_name):
        super().__init__(model, model_name_for_filename, class_name)

    def write_chaste_code(self, output_path):
        raise NotImplementedError("TODO Not yet implemented!")

class Numerical_jChasteModel(ChasteModel):
    def __init__(self, model, model_name_for_filename, class_name):
        super().__init__(model, model_name_for_filename, class_name)

    def write_chaste_code(self, output_path):
        raise NotImplementedError("TODO Not yet implemented!")

class BEOptChasteModel(ChasteModel):
    def __init__(self, model, model_name_for_filename, class_name):
        super().__init__(model, model_name_for_filename, class_name)

    def write_chaste_code(self, output_path):
        raise NotImplementedError("TODO Not yet implemented!")
