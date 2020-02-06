import chaste_codegen as cg
from chaste_codegen._partial_eval import partial_eval
# todo lookuptables


class OptChasteModel(cg.NormalChasteModel):
    """ Holds information specific for the Optimised model type. Builds on Normal model type"""
    def _get_stimulus(self):
        """ Get the partially evaluated stimulus currents in the model"""
        stim_param, return_stim_eqs = super()._get_stimulus()
        return stim_param, partial_eval(return_stim_eqs, stim_param)

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the partially evaluated equations defining the ionic derivatives and all dependant equations"""
        return partial_eval(super()._get_extended_equations_for_ionic_vars(),
                            [eq.lhs for eq in self._equations_for_ionic_vars])

    def _get_derivative_equations(self):
        """ Get partially evaluated equations defining the derivatives including V (self._membrane_voltage_var)"""
        return partial_eval(super()._get_derivative_equations(),
                            self._y_derivatives)