from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.cvode_chaste_model import CvodeChasteModel


class OptCvodeChasteModel(CvodeChasteModel):
    """ Holds information specific for the Cvode Optimised model type. Builds on Cvode model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._vars_for_template['model_type'] += 'Opt'

    def _get_stimulus(self):
        """ Get the partially evaluated stimulus currents in the model"""
        return_stim_eqs = super()._get_stimulus()
        return partial_eval(return_stim_eqs, self._model.stimulus_params | self._model.modifiable_parameters)

    def _get_extended_ionic_vars(self):
        """ Get the partially evaluated equations defining the ionic derivatives and all dependant equations"""
        return partial_eval(super()._get_extended_ionic_vars(), self._model.ionic_vars)

    def _get_derivative_equations(self):
        """ Get partially evaluated equations defining the derivatives including V (self._model.membrane_voltage_var)"""
        return partial_eval(super()._get_derivative_equations(),
                            self._model.y_derivatives)
