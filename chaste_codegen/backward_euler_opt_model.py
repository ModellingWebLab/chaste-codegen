from sympy import Eq

from chaste_codegen._lookup_tables import DEFAULT_LOOKUP_PARAMETERS, LookupTables
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.backward_euler_model import BackwardEulerModel


class BackwardEulerOptModel(BackwardEulerModel):
    """ Holds information specific for the Optimised Backward Euler model type."""

    def __init__(self, model, file_name, **kwargs):
        self._lookup_tables = LookupTables(model, lookup_params=kwargs.get('lookup_table', DEFAULT_LOOKUP_PARAMETERS))

        super().__init__(model, file_name, **kwargs)
        self._update_formatted_deriv_eq()
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

    def _pre_print_hook(self):
        """ Retreives out linear and non-linear derivatives and the relevant jacobian for it.
            And calculates lookup tables for the jacobian."""
        super()._pre_print_hook()
        # calculate lookup tables for the jacobians created by the Backward Euler
        self._lookup_tables.calc_lookup_tables((Eq(lhs, rhs) for lhs, rhs in self._jacobian_equations))

    def _get_non_linear_eqs(self):
        """Get derivative eqs for non linear state vars"""
        non_linear_eqs = super()._get_non_linear_eqs()
        non_linear_eqs = partial_eval(non_linear_eqs, self._model.y_derivatives)
        return non_linear_eqs

    def _update_formatted_deriv_eq(self):
        """Update derivatibve equation information for lookup table printing"""
        for eq in self._vars_for_template['y_derivative_equations']:
            if not eq['linear']:
                with self._lookup_tables.method_being_printed('ComputeResidual'):
                    eq['rhs'] = self._printer.doprint(eq['sympy_rhs'])
            if eq['in_membrane_voltage']:
                with self._lookup_tables.method_being_printed('UpdateTransmembranePotential'):
                    eq['rhs'] = self._printer.doprint(eq['sympy_rhs'])

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

    def format_linear_deriv_eqs(self, linear_deriv_eqs):
        """ Format linear derivative equations beloning, to update what belongs were"""
        with self._lookup_tables.method_being_printed('ComputeOneStepExceptVoltage'):
            return super().format_linear_deriv_eqs(linear_deriv_eqs)

    def format_jacobian(self):
        """Format the jacobian to update what belongs were"""
        with self._lookup_tables.method_being_printed('ComputeJacobian'):
            return super().format_jacobian()
