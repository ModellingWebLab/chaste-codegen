from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.cvode_chaste_model import CvodeChasteModel


class OptCvodeChasteModel(CvodeChasteModel):
    """ Holds information specific for the Optimised model type. Builds on Normal model type"""

    def _get_stimulus(self):
        """ Get the partially evaluated stimulus currents in the model"""
        return_stim_eqs = super()._get_stimulus()
        return partial_eval(return_stim_eqs, self._model.stimulus_params | self._model.modifiable_parameters)

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the partially evaluated equations defining the ionic derivatives and all dependant equations"""
        return partial_eval(super()._get_extended_equations_for_ionic_vars(),
                            set(map(lambda eq: eq.lhs, self._model.equations_for_ionic_vars)))

    def _get_derivative_equations(self):
        """ Get partially evaluated equations defining the derivatives including V (self._model.membrane_voltage_var)"""
        return partial_eval(super()._get_derivative_equations(),
                            self._model.y_derivatives)
