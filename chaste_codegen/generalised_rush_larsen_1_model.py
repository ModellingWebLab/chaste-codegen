from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class GeneralisedRushLarsenModelFirstOrder(ChasteModel):
    """ Holds template and information specific for the GeneralisedRushLarsen model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'generalised _rush_larsen_model_1.hpp'
        self._cpp_template = 'generalised_rush_larsen_model_1.cpp'
        self._jacobian_equations, self._jacobian_matrix = self._get_jacobian()
        self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
            format_jacobian(self._jacobian_equations, self._jacobian_matrix, self._printer, skip_0_entries=False)
        self._map_state_vars_and_eqs()

    def _get_jacobian(self):
        derivative_eqs_for_jacobian = \
            partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
        return get_jacobian(self._state_vars, derivative_eqs_for_jacobian)

    def _map_state_vars_and_eqs(self):
        equations = []
        for i, deriv in enumerate(self._y_derivatives):
            equations = self._get_equations_for([deriv])
            # Get all used variables
            used_vars = set()
            for eq in equations:
                used_vars.update(eq.rhs.free_symbols)

            # get all the variables used in matrix entry and all varibles used to thefine them
            jacobian_diagional_entry = self._jacobian_matrix[i, i]
            used_jacobian_vars = list(jacobian_diagional_entry.free_symbols)
            for var in used_jacobian_vars:
                var_def = [eq[1] for eq in self._jacobian_equations if eq[0] == var]
                if len(var_def) > 0:
                    for new_var in var_def[0].free_symbols:
                        if new_var not in used_jacobian_vars:
                            used_jacobian_vars.append(new_var)

            for sv in self._formatted_state_vars:
                sv.setdefault('in_evaluate_y_derivative', []).append(sv['sympy_var'] in used_vars)
                sv.setdefault('in_evaluate_partial_derivative', []).append(sv['sympy_var'] in used_jacobian_vars)

            for eq in self._vars_for_template['y_derivative_equations']:
                eq.setdefault('in_evaluate_y_derivative', []).append(eq['sympy_lhs'] in [eq.lhs for eq in equations])

            for je in self._vars_for_template['jacobian_equations']:
                je.setdefault('in_evaluate_partial_derivative', []).append(je['sympy_lhs'] in used_jacobian_vars)
        pass
