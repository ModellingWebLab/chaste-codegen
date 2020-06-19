from sympy import Derivative

from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class GeneralisedRushLarsenFirstOrderModel(ChasteModel):
    """ Holds template and information specific for the GeneralisedRushLarsen model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'generalised_rush_larsen_model.hpp'
        self._cpp_template = 'generalised_rush_larsen_model_1.cpp'
        self._vars_for_template['base_class'] = 'AbstractGeneralizedRushLarsenCardiacCell'
        self._jacobian_equations, self._jacobian_matrix = self._get_jacobian()
        self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
            format_jacobian(self._jacobian_equations, self._jacobian_matrix, self._printer,
                            self._print_rhs_with_modifiers, skip_0_entries=False)
        self._map_state_vars_and_eqs()

    def _get_jacobian(self):
        """Retrieve jacobian matrix"""
        derivative_eqs_for_jacobian = \
            partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
        return get_jacobian(self._state_vars, derivative_eqs_for_jacobian)

    def _map_state_vars_and_eqs(self):
        """Map state vars, derivative equations and jacobian entries to state vars for output

        Specifically updates self._formatted_state_vars and self._vars_for_template['jacobian_equations']
        and self._vars_for_template['jacobian_equations']
        to add in_evaluate_y_derivative and in_evaluate_partial_derivative arrays
        indicating whether they're used in the derivative or jacobian for the relevant state vars.
        """

        def get_used_eqs_and_state_vars(eq_to_expand, equations):
            """ Returns used equations and state vars for a given equation

            :param eq_to_expand: list containing equations to recurse over and expand definitions for
                       note: expecting equations in [(lhs, rhs)] form.
            :param equations: set of equations to look for definitions in.
            :return: set of equations and set of used state vars.
            """
            used_state_vars = set()
            for eq in eq_to_expand:
                for v in eq[1].atoms(Derivative) | eq[1].free_symbols:
                    if v in self._state_vars:
                        used_state_vars.add(v)
                    elif v not in [e[0] for e in eq_to_expand]:
                        eq_to_expand.extend(filter(lambda e: e[0] == v, equations))
            return set(eq_to_expand), used_state_vars

        for i, deriv in enumerate(self._y_derivatives):
            equations, used_state_vars = \
                get_used_eqs_and_state_vars([(d.lhs, d.rhs) for d in self._derivative_equations if d.lhs == deriv],
                                            set(map(lambda e: (e.lhs, e.rhs), self._derivative_equations)))

            # get all the variables used in jacobian matrix entry and all variables used to define them
            used_jacobian_vars, used_jacobian_state_vars = \
                get_used_eqs_and_state_vars([(None, self._jacobian_matrix[i, i])], set(self._jacobian_equations))

            for sv in self._formatted_state_vars:
                sv.setdefault('in_evaluate_y_derivative', []).append(sv['sympy_var'] in used_state_vars)
                sv.setdefault('in_evaluate_partial_derivative', []).append(sv['sympy_var'] in used_jacobian_state_vars)

            for eq in self._vars_for_template['y_derivative_equations']:
                eq.setdefault('in_evaluate_y_derivative', []).append(eq['sympy_lhs'] in [eq[0] for eq in equations])

            for je in self._vars_for_template['jacobian_equations']:
                je.setdefault('in_evaluate_partial_derivative', []).append(je['sympy_lhs']
                                                                           in [v[0] for v in used_jacobian_vars
                                                                           if v[0] is not None])
