from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.generalised_rush_larsen_1_model import GeneralisedRushLarsenFirstOrderModel


class GeneralisedRushLarsenFirstOrderModelOpt(GeneralisedRushLarsenFirstOrderModel):
    """ Holds template and information specific for the GeneralisedRushLarsenOpt model type"""

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the partially evaluated equations defining the ionic derivatives and all dependant equations"""
        return partial_eval(super()._get_extended_equations_for_ionic_vars(),
                            set(map(lambda eq: eq.lhs, self._equations_for_ionic_vars)))

    def _get_derivative_equations(self):
        """ Get partially evaluated equations defining the derivatives including V (self._membrane_voltage_var)"""
        return partial_eval(super()._get_derivative_equations(),
                            self._y_derivatives)
