from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.rush_larsen_model import RushLarsenModel


class RushLarsenOptModel(RushLarsenModel):
    """ Holds template and information specific for the RushLarsen model type"""

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the partially evaluated equations defining the ionic derivatives and all dependant equations"""
        return partial_eval(super()._get_extended_equations_for_ionic_vars(),
                            [eq.lhs for eq in self._equations_for_ionic_vars])

    def _update_state_vars(self):
        """Updates formatting of state vars to make sure the correct ones are included in the output"""
        # First apply partial eval to derivative_alpha_beta_eqs and _derivative_eqs_excl_voltage
        self._vars_for_template['derivative_alpha_beta_eqs'] = \
            partial_eval(self._vars_for_template['derivative_alpha_beta_eqs'], self._vars_in_derivative_alpha_beta,
                         keep_multiple_usages=False)
        self._derivative_eqs_excl_voltage = partial_eval(self._derivative_eqs_excl_voltage,
                                                         self._vars_in_derivative_alpha_beta,
                                                         keep_multiple_usages=False)
        # Then call _update_state_vars in super class
        super()._update_state_vars()
