from chaste_codegen._lookup_tables import LookupTables
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.normal_chaste_model import NormalChasteModel


class OptChasteModel(NormalChasteModel):
    """ Holds information specific for the Optimised model type. Builds on Normal model type"""

    def __init__(self, model, file_name, **kwargs):
        self._lookup_tables = LookupTables(model)

        super().__init__(model, file_name, **kwargs)
        self._vars_for_template['model_type'] = 'NormalOpt'
        self._vars_for_template['lookup_parameters'] = self._lookup_tables.print_lookup_parameters(self._printer)

    def _get_stimulus(self):
        """ Get the partially evaluated stimulus currents in the model"""
        return_stim_eqs = super()._get_stimulus()
        return_stim_eqs = partial_eval(return_stim_eqs, self._model.stimulus_params | self._model.modifiable_parameters)
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

    def _add_printers(self):
        """ Initialises Printers for outputting chaste code. """
        super()._add_printers()
        self._printer.lookup_tables = self._lookup_tables

    def _format_ionic_vars(self):
        """ Format equations and dependant equations ionic derivatives"""
        with self._lookup_tables.method_being_printed('GetIIonic'):
            return super()._format_ionic_vars()

    def _format_derivative_equations(self, derivative_equations):
        """ Format derivative equations for chaste output"""
        with self._lookup_tables.method_being_printed('EvaluateYDerivatives'):
            return super()._format_derivative_equations(derivative_equations)

    def _format_derived_quant_eqs(self):
        """ Format equations for derived quantities based on current settings"""
        with self._lookup_tables.method_being_printed('ComputeDerivedQuantities'):
            return super()._format_derived_quant_eqs()
