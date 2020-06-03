from sympy import Matrix

from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class CvodeChasteModel(ChasteModel):
    """ Holds template and information specific for the CVODE model type"""
    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'cvode_model.hpp'
        self._cpp_template = 'cvode_model.cpp'
        self._vars_for_template['base_class'] = 'AbstractCvodeCell'
        self._vars_for_template['vector_decl'] = "N_Vector"  # indicate how to declare state vars and values

        self._use_analytic_jacobian = kwargs.get('use_analytic_jacobian', False)  # store if jacobians are needed
        if self._use_analytic_jacobian:
            # get deriv eqs and substitute in all variables other than state vars
            self._derivative_equations = \
                partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
            self._jacobian_equations, self._jacobian_matrix = get_jacobian(self._state_vars, self._derivative_equations)
            self._formatted_state_vars = self._update_state_vars()
            self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
                format_jacobian(self._jacobian_equations, self._jacobian_matrix, self._printer,
                                self._print_rhs_with_modifiers)
        else:
            self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
                [], Matrix()

    def _print_modifiable_parameters(self, symbol):
        return 'NV_Ith_S(mParameters, ' + str(self._modifiable_parameters.index(symbol)) + ')'

    def _format_rY_entry(self, index):
        return 'NV_Ith_S(rY, ' + str(index) + ')'

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
