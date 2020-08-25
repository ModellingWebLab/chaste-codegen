from chaste_codegen._lookup_tables import _DEFAULT_LOOKUP_PARAMETERS, LookupTables
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.cvode_chaste_model import CvodeChasteModel


class OptCvodeChasteModel(CvodeChasteModel):
    """ Holds information specific for the Cvode Optimised model type. Builds on Cvode model type"""

    def __init__(self, model, file_name, **kwargs):
        self._lookup_tables = LookupTables(model, lookup_params=kwargs.get('lookup_table', _DEFAULT_LOOKUP_PARAMETERS))

        super().__init__(model, file_name, **kwargs)
        self._vars_for_template['model_type'] += 'Opt'
        self._vars_for_template['lookup_parameters'] = self._lookup_tables.print_lookup_parameters(self._printer)

    def _get_stimulus(self):
        """ Get the partially evaluated stimulus currents in the model"""
        return_stim_eqs = super()._get_stimulus()
        return partial_eval(return_stim_eqs, self._model.stimulus_params | self._model.modifiable_parameters)

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
        super()._add_printers(self._lookup_tables.print_lut_expr)

    def _print_jacobian(self):
        with self._lookup_tables.method_being_printed('EvaluateAnalyticJacobian'):
            return super()._print_jacobian()

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
