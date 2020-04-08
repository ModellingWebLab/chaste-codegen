import sympy as sp

from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._linearity_check import get_non_linear_state_vars, subst_deriv_eqs_non_linear_vars
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class BackwardEulerModel(ChasteModel):
    """ Holds template and information specific for the Backwards Euler model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'backward_euler_model.hpp'
        self._cpp_template = 'backward_euler_model.cpp'
        # get deriv eqs and substitute in all variables other than state vars
        self._derivative_equations = \
            partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
        self._non_linear_state_vars = get_non_linear_state_vars(self._derivative_equations, self._membrane_voltage_var,
                                                                self._state_vars, self._printer)

        self._jacobian_equations, self._jacobian_matrix = \
            get_jacobian(self._non_linear_state_vars,
                         [d for d in self._derivative_equations if d.lhs.args[0] in self._non_linear_state_vars])

        self._vars_for_template['state_vars'], self._vars_for_template['nonlinear_state_vars'], \
            self._vars_for_template['residual_equations'], self._vars_for_template['y_derivative_equations'] = \
            self._update_state_vars()
        self._vars_for_template['linear_deriv_eqs'], self._vars_for_template['linear_equations'] = \
            self._format_rearranged_linear_derivs()
        self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
            format_jacobian(self._jacobian_equations, self._jacobian_matrix, self._printer,
                            swap_inner_outer_index=False, skip_0_entries=False)

    def _format_rearranged_linear_derivs(self):
        """Formats the rearranged linear derivative expressions"""
        def rearrange_expr(expr, var):  # expr already in piecewise_fold form
            """Rearrange an expression into the form g + h*var."""
            if isinstance(expr, sp.Piecewise):
                # The tests have to move into both components of gh:
                # "if C1 then (a1,b1) elif C2 then (a2,b2) else (a0,b0)"
                # maps to "(if C1 then a1 elif C2 then a2 else a0,
                #           if C1 then b1 elif C2 then b2 else b0)"
                # Note that no test is a function of var.
                # First rearrange child expressions
                cases = [p[0] for p in expr.args]

                cases_ghs = [rearrange_expr(c, var) for c in cases]
                # Now construct the new expression
                conds = [e[1] for e in expr.args]

                def piecewise_branch(i):
                    pieces_i = zip(map(lambda gh: gh[i], cases_ghs), conds)
                    pieces_i = [p for p in pieces_i if p[0] is not None]  # Remove cases that are None
                    new_expr = None
                    if pieces_i:
                        new_expr = sp.Piecewise(*pieces_i)
                    return new_expr
                gh = (piecewise_branch(0), piecewise_branch(1))

            else:
                h = sp.Wild('h', exclude=[var])
                g = sp.Wild('g', exclude=[var])
                match = expr.expand().match(g + h * var)
                gh = (None, None)
                if match is not None:
                    gh = (match[g], match[h])
            return gh

        def print_rearrange_expr(expr, var):
            """Print out the rearanged expression"""
            expr = sp.piecewise_fold(expr)
            gh = rearrange_expr(expr, var)
            return {'state_var_index': self._state_vars.index(var),
                    'var': self._printer.doprint(var),
                    'g': self._printer.doprint(gh[0] if gh[0] is not None else 0.0),
                    'h': self._printer.doprint(gh[1] if gh[1] is not None else 0.0)}

        # Substitute non-linear bits into derivative equations, so that we can pattern match
        linear_derivs_eqs = subst_deriv_eqs_non_linear_vars(self._y_derivatives, self._non_linear_state_vars,
                                                            self._membrane_voltage_var,
                                                            self._state_vars, self._get_equations_for)

        # sort the linear derivatives
        linear_derivs = sorted([eq for eq in linear_derivs_eqs if isinstance(eq.lhs, sp.Derivative)],
                               key=lambda d: self._get_var_display_name(d.lhs.args[0]))
        formatted_expr = [print_rearrange_expr(d.rhs, d.lhs.args[0]) for d in linear_derivs]

        # remove eqs for which the lhs doesn't appear in other equations (e.g. derivatives)
        # to prevent unused variable comple errors
        used_vars = set()
        for eq in linear_derivs_eqs:
            used_vars.update(self._model.find_variables_and_derivatives([eq.rhs]))
        linear_derivs_eqs = [eq for eq in linear_derivs_eqs if eq.lhs in used_vars]

        return formatted_expr, self._format_derivative_equations(linear_derivs_eqs)

    def _update_state_vars(self):
        """Update the state vars, savings residual and jacobian info for outputing"""
        formatted_state_vars = self._vars_for_template['state_vars']
        residual_equations = []
        formatted_derivative_eqs = self._vars_for_template['y_derivative_equations']
        jacobian_symbols = set()
        residual_eq_symbols = set()

        for eq in self._jacobian_equations:
            jacobian_symbols.update(eq[1].free_symbols)
        for eq in self._jacobian_matrix:
            jacobian_symbols.update(eq.free_symbols)

        non_linear_derivs = [eq.lhs for eq in self._derivative_equations if isinstance(eq.lhs, sp.Derivative)
                             and eq.lhs.args[0] in self._non_linear_state_vars]
        non_linear_eqs = self._model.get_equations_for(non_linear_derivs)
        for eq in non_linear_eqs:
            residual_eq_symbols.update(eq.rhs.free_symbols)
        non_linear_eqs = [self._printer.doprint(eq.lhs) for eq in non_linear_eqs]
        for d in formatted_derivative_eqs:
            d['linear'] = d['lhs'] not in non_linear_eqs

        formatted_nonlinear_state_vars = \
            [s for s in formatted_state_vars if s['sympy_var'] in self._non_linear_state_vars]
        # order by name
        formatted_nonlinear_state_vars = sorted(formatted_nonlinear_state_vars, key=lambda d: d['var'])
        for sv in formatted_nonlinear_state_vars:
            sv['linear'] = False
            sv['in_jacobian'] = sv['sympy_var'] in jacobian_symbols
            sv['in_residual_eqs'] = sv['sympy_var'] in residual_eq_symbols

        for i, sv in enumerate(formatted_state_vars):
            sv['linear'] = sv['sympy_var'] not in self._non_linear_state_vars
            sv['in_jacobian'] = sv['sympy_var'] in jacobian_symbols
            sv['in_residual_eqs'] = sv['sympy_var'] in residual_eq_symbols
            if not sv['linear']:
                residual_equations.append({'residual_index': formatted_nonlinear_state_vars.index(sv),
                                           'state_var_index': i, 'var': self._vars_for_template['y_derivatives'][i]})

        return formatted_state_vars, formatted_nonlinear_state_vars, residual_equations, formatted_derivative_eqs
