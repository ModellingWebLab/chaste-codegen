import sympy as sp

from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class CvodeChasteModel(ChasteModel):
    """ Holds template and information specific for the CVODE model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'cvode_model.hpp'
        self._cpp_template = 'cvode_model.cpp'

        self._use_analytic_jacobian = kwargs.get('use_analytic_jacobian', False)  # store if jacobians are needed
        if self._use_analytic_jacobian:
            # get deriv eqs and substitute in all variables other than state vars
            self._derivative_equations = \
                partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
            self._jacobian_equations, self._jacobian_matrix = self._get_jacobian()
            self._formatted_state_vars = self._update_state_vars()
            self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
                self._format_jacobian()
        else:
            self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
                [], sp.Matrix()

    def _print_modifiable_parameters(self, symbol):
        return 'NV_Ith_S(mParameters, ' + str(self._modifiable_parameters.index(symbol)) + ')'

    def _get_jacobian(self):
        jacobian_equations, jacobian_matrix = [], []
        state_var_matrix = sp.Matrix(self._state_vars)
        # sort by state var
        derivative_eqs = sorted(self._derivative_equations, key=lambda d: self._state_vars.index(d.lhs.args[0]))
        # we're only interested in the rhs
        derivative_eqs = [eq.rhs for eq in derivative_eqs]
        derivative_eq_matrix = sp.Matrix(derivative_eqs)
        jacobian_matrix = derivative_eq_matrix.jacobian(state_var_matrix)
        jacobian_equations, jacobian_matrix = sp.cse(jacobian_matrix, order='none')
        return jacobian_equations, sp.Matrix(jacobian_matrix)

    def _update_state_vars(self):
        jacobian_symbols = set()
        for eq in self._jacobian_equations:
            jacobian_symbols.update(eq[1].free_symbols)
        for en in self._jacobian_matrix:
            jacobian_symbols.update(en.free_symbols)
        formatted_state_vars = self._formatted_state_vars
        for sv in formatted_state_vars:
            sv['in_jacobian'] = sv['sympy_var'] in jacobian_symbols
        return formatted_state_vars

    def _format_jacobian(self):
        assert isinstance(self._jacobian_matrix, sp.Matrix), 'Expecting a jacobian as a matrix'
        equations = [{'lhs': self._printer.doprint(eq[0]), 'rhs': self._printer.doprint(eq[1])}
                     for eq in self._jacobian_equations]
        rows, cols = self._jacobian_matrix.shape
        jacobian = []
        for j in range(cols):
            for i in range(rows):
                matrix_entry = self._jacobian_matrix[i, j]
                if matrix_entry != 0:
                    jacobian.append({'i': i, 'j': j, 'entry': self._printer.doprint(matrix_entry)})
        return equations, jacobian
