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
        return_stim_eqs = partial_eval(return_stim_eqs, self._model.stimulus_params | self._model.modifiable_parameters)
        self._lookup_tables.calc_lookup_tables(return_stim_eqs)
        return return_stim_eqs

    def _get_extended_ionic_vars(self):
        """ Get the partially evaluated equations defining the ionic derivatives and all dependant equations"""
        extended_ionic_vars = partial_eval(super()._get_extended_ionic_vars(), self._model.ionic_vars)
        self._lookup_tables.calc_lookup_tables(extended_ionic_vars)
        return extended_ionic_vars

    def _get_derivative_equations(self):
        """ Get partially evaluated equations defining the derivatives including V (self._model.membrane_voltage_var)"""
        derivative_equations = partial_eval(super()._get_derivative_equations(), self._model.y_derivatives)
        self._lookup_tables.calc_lookup_tables(derivative_equations)
        return derivative_equations
