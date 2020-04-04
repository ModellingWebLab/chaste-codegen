import sympy as sp

from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.rush_larsen_model import RushLarsenModel


class RushLarsenOptModel(RushLarsenModel):
    """ Holds template and information specific for the RushLarsen model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the partially evaluated equations defining the ionic derivatives and all dependant equations"""
        return partial_eval(super()._get_extended_equations_for_ionic_vars(),
                            [eq.lhs for eq in self._equations_for_ionic_vars])

    def _update_state_vars(self):
        """Updates formatting of state vars to make sure the correct ones are included in the output"""
        self._vars_for_template['derivative_alpha_beta_eqs'] = \
            partial_eval(self._vars_for_template['derivative_alpha_beta_eqs'], self._vars_in_derivative_alpha_beta,
                         keep_multiple_usages=False)
        # Get all used variables for derivative eqs
        deriv_variables = set()
        for eq in self._vars_for_template['derivative_alpha_beta_eqs']:
            deriv_variables.update(eq.rhs.free_symbols)

        for sv in self._formatted_state_vars:
            sv['in_ab'] = sv['sympy_var'] in deriv_variables

    def _format_alpha_beta_eqs(self):
        """Formats the equations for the evaluateequations part (with alpha_beta or inf_tau)"""
        return [{'lhs': self._printer.doprint(eqs.lhs),
                 'rhs': self._printer.doprint(eqs.rhs),
                 'units': self._model.units.format(self._model.units.evaluate_units(eqs.lhs)),
                 'in_eqs_excl_voltage': not isinstance(eqs.lhs, sp.Derivative) or
                 eqs.lhs.args[0] != self._membrane_voltage_var,
                 'is_voltage': isinstance(eqs.lhs, sp.Derivative) and eqs.lhs.args[0] == self._membrane_voltage_var}
                for eqs in self._vars_for_template['derivative_alpha_beta_eqs']]
