from chaste_codegen._lookup_tables import _DEFAULT_LOOKUP_PARAMETERS, LookupTables
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.model_with_conversions import get_equations_for
from chaste_codegen.rush_larsen_model import RushLarsenModel


class RushLarsenOptModel(RushLarsenModel):
    """ Holds template and information specific for the RushLarsen model type"""

    def __init__(self, model, file_name, **kwargs):
        self._lookup_tables = LookupTables(model, lookup_params=kwargs.get('lookup_table', _DEFAULT_LOOKUP_PARAMETERS))

        super().__init__(model, file_name, **kwargs)
        self._vars_for_template['model_type'] = 'RushLarsenOpt'
        self._vars_for_template['lookup_parameters'] = self._lookup_tables.print_lookup_parameters(self._printer)

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
        super()._add_printers(lookup_table_function=self._lookup_tables.print_lut_expr)

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

    def _get_formatted_alpha_beta(self):
        """Gets the information for r_alpha_or_tau, r_beta_or_inf in the c++ output and formatted equations

        Rearranges in the form (inf-x)/tau
        """
        with self._lookup_tables.method_being_printed('EvaluateEquations'):
            return super()._get_formatted_alpha_beta()

    def format_deriv_eqs_EvaluateEquations(self, deriv_eqs_EvaluateEquations):
        """ Format derivative equations beloning to EvaluateEquations, to update what equation belongs were"""
        voltage_eqs = set(get_equations_for(self._model, [d for d in self._model.y_derivatives
                                                          if d.args[0] is self._model.membrane_voltage_var]))
        other_eqs = set(get_equations_for(self._model, [d for d in self._model.y_derivatives
                                                        if d.args[0] is not self._model.membrane_voltage_var]))
        voltage_eqs -= set(other_eqs)
        self._derivative_eqs_voltage |= voltage_eqs
        return super().format_deriv_eqs_EvaluateEquations(deriv_eqs_EvaluateEquations)
