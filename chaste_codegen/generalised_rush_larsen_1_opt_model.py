from sympy import Derivative

from chaste_codegen._lookup_tables import _DEFAULT_LOOKUP_PARAMETERS, LookupTables
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.generalised_rush_larsen_1_model import GeneralisedRushLarsenFirstOrderModel


class GeneralisedRushLarsenFirstOrderModelOpt(GeneralisedRushLarsenFirstOrderModel):
    """ Holds template and information specific for the GeneralisedRushLarsenOpt model type"""

    def __init__(self, model, file_name, **kwargs):
        self._lookup_tables = LookupTables(model, lookup_params=kwargs.get('lookup_table', _DEFAULT_LOOKUP_PARAMETERS))

        super().__init__(model, file_name, **kwargs)
        self._vars_for_template['model_type'] = 'GeneralizedRushLarsenFirstOrderOpt'
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
        super()._add_printers(lookup_table_function=self._lookup_tables.print_lut_expr)

    def _format_ionic_vars(self):
        """ Format equations and dependant equations ionic derivatives"""
        with self._lookup_tables.method_being_printed('GetIIonic'):
            return super()._format_ionic_vars()

    def format_derivative_equation(self, eq, modifiers_with_defining_eqs):
        """ Format an individual derivative equation"""
        formatted_eq = None
        if isinstance(eq.lhs, Derivative) and eq.lhs.args[0] is self._model.membrane_voltage_var:
            formatted_eq = super().format_derivative_equation(eq, modifiers_with_defining_eqs)

        elif eq in self._derivative_eqs_excl_voltage:  # Indicate use of lookup table
            with self._lookup_tables.method_being_printed('ComputeOneStepExceptVoltage'):
                formatted_eq = super().format_derivative_equation(eq, modifiers_with_defining_eqs)

        if eq in self._derivative_eqs_voltage:  # Indicate use of lookup table
            with self._lookup_tables.method_being_printed('UpdateTransmembranePotential'):
                formatted_eq = super().format_derivative_equation(eq, modifiers_with_defining_eqs)

        assert formatted_eq is not None, ('Derivative equation should be dvdt or in _derivative_eqs_voltage '
                                          'or in _derivative_eqs_excl_voltage')
        return formatted_eq

    def _format_derived_quant_eqs(self):
        """ Format equations for derived quantities based on current settings"""
        with self._lookup_tables.method_being_printed('ComputeDerivedQuantities'):
            return super()._format_derived_quant_eqs()

    def eq_in_evaluate_y_derivative(self, eq, used_equations):
        """Indicate if the lhs of equation eq appears in used_equations"""
        super().eq_in_evaluate_y_derivative(eq, used_equations)
        if eq['in_evaluate_y_derivative'][-1]:
            # Reprint to indicate use of lookup table
            with self._lookup_tables.method_being_printed('ComputeOneStepExceptVoltage' +
                                                          str(len(eq['in_evaluate_y_derivative']) - 1)):
                modifiers_with_defining_eqs = \
                    set((eq.lhs for eq in self._derivative_equations)) | self._model.state_vars
                eq['rhs'] = self._print_rhs_with_modifiers(eq['sympy_lhs'], eq['sympy_rhs'],
                                                           modifiers_with_defining_eqs)

    def eq_in_evaluate_partial_derivative(self, eq, used_jacobian_vars):
        """Indicate if the lhs of equation eq appears in used_jacobian_vars"""
        super().eq_in_evaluate_partial_derivative(eq, used_jacobian_vars)
        if eq['in_evaluate_partial_derivative'][-1]:
            # Reprint to indicate use of lookup table
            with self._lookup_tables.method_being_printed('EvaluatePartialDerivative' +
                                                          str(len(eq['in_evaluate_partial_derivative']) - 1)):
                eq['rhs'] = self._printer.doprint(eq['sympy_rhs'])
