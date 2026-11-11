from sympy import Dummy, Function

from chaste_codegen._device_printer import DEVICE_INPUTS, ChasteDevicePrinter
from chaste_codegen.chaste_model import get_variable_name
from chaste_codegen.normal_chaste_model import NormalChasteModel


class NormalDeviceModel(NormalChasteModel):
    """ Holds template and information for device code of the Normal model type, generated alongside its CPU code"""

    DEFAULT_EXTENSIONS = ('Device.hpp', )

    def __init__(self, model, file_name, **kwargs):
        # Modifiers are host objects
        kwargs['use_modifiers'] = False
        super().__init__(model, file_name, **kwargs)
        self._templates = ['normal_model_device.hpp']
        self._vars_for_template['device_arguments'] = self._format_device_arguments()

    def _add_printers(self, lookup_table_function=lambda e: None):
        """ Initialises Printers for outputting device code. """
        self._printer = \
            ChasteDevicePrinter(lambda variable:
                                get_variable_name(variable, variable in self._in_interface)
                                if variable not in self._model.modifiable_parameters
                                else self._print_modifiable_parameters(variable),
                                lambda deriv: get_variable_name(deriv),
                                lookup_table_function)

        # Printer for printing variable in comments e.g. for ode system information
        self._name_printer = ChasteDevicePrinter(lambda variable: get_variable_name(variable))

    def _print_modifiable_parameters(self, variable):
        """ Print modifiable parameters as entries of the parameters argument """
        return 'pParameters[' + self._modifiable_parameter_lookup[variable] + ']'

    def _format_rY_lookup(self, index, var, use_modifier=True):
        """ Formatting of rY lookup for printing, using the fixedVoltage argument when the voltage is clamped """
        entry = self._format_rY_entry(index)
        if var == self._model.membrane_voltage_var:
            entry = '(setVoltageDerivativeToZero ? fixedVoltage : ' + entry + ')'
        return entry

    def _print_rhs_with_modifiers(self, modifier, eq, modifiers_with_defining_eqs=set()):
        """ Print the right hand side of an equation; device code has no modifiers """
        return self._printer.doprint(eq)

    def _format_device_arguments(self):
        """ Find which arguments of the device functions are used, so unused ones can be left unnamed """
        used_symbols = set()
        used_inputs = set()
        for eq in self._derivative_equations:
            calls = {call for call in eq.rhs.atoms(Function) if call.func.__name__ in DEVICE_INPUTS}
            used_inputs.update(DEVICE_INPUTS[call.func.__name__] for call in calls)
            # Arguments of these calls, e.g. the time for the stimulus, are not printed
            used_symbols.update(eq.rhs.xreplace({call: Dummy() for call in calls}).free_symbols)

        used_state_vars = [var['sympy_var'] for var in self._formatted_state_vars if var['in_y_deriv']]
        return {'time': self._model.time_variable in used_symbols,
                'state_vars': len(used_state_vars) > 0,
                'parameters': any(param in used_symbols for param in self._modifiable_parameters),
                'stimulus': 'stimulus' in used_inputs,
                'capacitance': 'capacitance' in used_inputs,
                'fixed_voltage': self._model.membrane_voltage_var in used_state_vars}
