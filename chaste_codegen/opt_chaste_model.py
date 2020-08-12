from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.normal_chaste_model import NormalChasteModel


class OptChasteModel(NormalChasteModel):
    """ Holds information specific for the Optimised model type. Builds on Normal model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._vars_for_template['model_type'] = 'NormalOpt'

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
