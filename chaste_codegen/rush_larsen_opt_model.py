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

    def _format_alpha_beta_eqs(self):
        self._formatted_alpha_beta_eqs = \
            partial_eval(self._formatted_alpha_beta_eqs, self._vars_in_derivative_alpha_beta)
        return super()._format_alpha_beta_eqs()
