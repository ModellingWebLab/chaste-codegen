import sympy as sp

from chaste_codegen._linearity_check import get_non_linear_state_vars, subst_deriv_eqs_non_linear_vars
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class GeneralisedRushLarsenModelFirstOrder(ChasteModel):
    """ Holds template and information specific for the GeneralisedRushLarsen model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'generalised _rush_larsen_model_1.hpp'
        self._cpp_template = 'generalised_rush_larsen_model_1.cpp'
        self._map_state_vars_and_eqs()

    def _map_state_vars_and_eqs(self):
        equations = []
        for i, deriv in enumerate(self._y_derivatives):
            equations = self._get_equations_for([deriv])
            # Get all used variables
            used_eqs = set([eq.lhs for eq in equations])
#            for eq in equations:
#                used_vars.update(eq.rhs.free_symbols)
            for sv in self._formatted_state_vars:
                sv.setdefault('in_evaluate_y_derivative', []).append(sv['sympy_var'] in used_eqs)

            for eq in self._vars_for_template['y_derivative_equations']:
                eq.setdefault('in_evaluate_y_derivative', []).append(eq['sympy_lhs'] in used_eqs)
        return []