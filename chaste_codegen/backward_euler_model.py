from functools import partial

from sympy import (
    Derivative,
    Piecewise,
    Wild,
    piecewise_fold,
)

from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._linearity_check import get_non_linear_state_vars, subst_deriv_eqs_non_linear_vars
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen._rdf import OXMETA
from chaste_codegen.chaste_model import ChasteModel, get_variable_name
from chaste_codegen.model_with_conversions import get_equations_for


class BackwardEulerModel(ChasteModel):
    """ Holds template and information specific for the Backwards Euler model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._templates = ['backward_euler_model.hpp', 'backward_euler_model.cpp']
        self._vars_for_template['base_class'] = 'AbstractBackwardEulerCardiacCell'
        self._vars_for_template['model_type'] = 'BackwardEuler'

        self._vars_for_template['linear_deriv_eqs'] = [{'state_var_index': deq['state_var_index'],
                                                        'var': self._printer.doprint(deq['var']),
                                                        'g': self._printer.doprint(deq['g']),
                                                        'h': self._printer.doprint(deq['h'])}
                                                       for deq in self._linear_deriv_eqs]

        self._vars_for_template['linear_equations'] = self.format_linear_deriv_eqs(self._linear_equations)

        self._vars_for_template['nonlinear_state_vars'] = self.format_nonlinear_state_vars()
        self._vars_for_template['residual_equations'] = self.format_residual_equations()

        self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
            self.format_jacobian()

    def _pre_print_hook(self):
        """ Retreives out linear and non-linear derivatives and the relevant jacobian for it."""
        super()._pre_print_hook()
        # get deriv eqs and substitute in all variables other than state vars
        derivative_equations = \
            partial_eval(self._derivative_equations, self._model.y_derivatives, keep_multiple_usages=False)
        self._non_linear_state_vars = \
            sorted(get_non_linear_state_vars(derivative_equations, self._model.membrane_voltage_var,
                   self._model.state_vars), key=lambda s: get_variable_name(s, s in self._in_interface))
        # Pick the formatted equations that are for non-linear derivatives

        self._non_linear_eqs = self._get_non_linear_eqs()

        self._jacobian_equations, self._jacobian_matrix = \
            get_jacobian(self._non_linear_state_vars,
                         [d for d in derivative_equations if d.lhs.args[0] in self._non_linear_state_vars])

        self._linear_deriv_eqs, self._linear_equations, self._vars_in_one_step = \
            self._rearrange_linear_derivs()

    def _get_non_linear_eqs(self):
        """Get derivative eqs for non linear state vars"""
        non_linear_derivs = (eq.lhs for eq in self._derivative_equations if eq.lhs in self._model.y_derivatives
                             and eq.lhs.args[0] in self._non_linear_state_vars)
        non_linear_deriv_eqs = tuple(e.lhs for e in self._model.get_equations_for(non_linear_derivs))
        return tuple(eq for eq in self._derivative_equations if eq.lhs in non_linear_deriv_eqs)

    def _rearrange_linear_derivs(self):
        """Formats the rearranged linear derivative expressions

        Rearranged in the form expr = g + h*var.
        """
        def rearrange_expr(expr, var):  # expr already in piecewise_fold form
            """Rearrange an expression into the form g + h*var."""
            if isinstance(expr, Piecewise):
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
                        new_expr = Piecewise(*pieces_i)
                    return new_expr
                gh = (piecewise_branch(0), piecewise_branch(1))

            else:
                h = Wild('h', exclude=[var])
                g = Wild('g', exclude=[var])
                match = expr.expand().match(g + h * var)
                gh = (None, None)
                if match is not None:
                    gh = (match[g], match[h])
            return gh

        # Substitute non-linear bits into derivative equations, so that we can pattern match
        linear_derivs_eqs = subst_deriv_eqs_non_linear_vars(self._model.y_derivatives, self._non_linear_state_vars,
                                                            self._model.membrane_voltage_var,
                                                            self._model.state_vars,
                                                            partial(get_equations_for, self._model))

        # sort the linear derivatives
        linear_derivs = sorted([eq for eq in linear_derivs_eqs if isinstance(eq.lhs, Derivative)],
                               key=lambda d: self._model.get_display_name(d.lhs.args[0], OXMETA))
        rearranged_expr = [(rearrange_expr(piecewise_fold(d.rhs), d.lhs.args[0]), d.lhs.args[0]) for d in linear_derivs]
        formatted_expr = [{'state_var_index': self._state_vars.index(var),
                           'var': var,
                           'g': gh[0] if gh[0] is not None else 0.0,
                           'h': gh[1] if gh[1] is not None else 0.0} for gh, var in rearranged_expr]

        # remove eqs for which the lhs doesn't appear in other equations (e.g. derivatives)
        # to prevent unused variable compile errors
        used_vars = self._model.find_variables_and_derivatives([eq.rhs for eq in linear_derivs_eqs])
        linear_derivs_eqs = [eq for eq in linear_derivs_eqs if eq.lhs in used_vars]

        for r_expr in rearranged_expr:
            # add variables used in g, h and the derivative var
            used_vars.update(self._model.find_variables_and_derivatives(r_expr[0]))
            used_vars.add(r_expr[1])

        return formatted_expr, linear_derivs_eqs, used_vars

    def _format_state_variables(self):
        formatted_state_vars, use_verify_state_variables = super()._format_state_variables()

        jacobian_symbols = set()
        non_linear_eq_symbols = set()

        # get symbols in jacobian
        for eq in self._jacobian_equations:
            jacobian_symbols.update(eq[1].free_symbols)
        for eq in self._jacobian_matrix:
            jacobian_symbols.update(eq.free_symbols)

        # store symbols used in non-linear equations
        for eq in self._non_linear_eqs:
            non_linear_eq_symbols.update(eq.rhs.free_symbols)

        for sv in formatted_state_vars:
            sv['in_non_linear_eq'] = sv['sympy_var'] in non_linear_eq_symbols
            sv['linear'] = sv['sympy_var'] not in self._non_linear_state_vars
            sv['in_jacobian'] = sv['sympy_var'] in jacobian_symbols
            sv['in_residual_eqs'] = sv['sympy_var'] in non_linear_eq_symbols
            sv['in_one_step_except_v'] = sv['sympy_var'] in self._vars_in_one_step
        return (formatted_state_vars, use_verify_state_variables)

    def format_derivative_equation(self, eq, modifiers_with_defining_eqs):
        formatted_derivative_equation = super().format_derivative_equation(eq, modifiers_with_defining_eqs)
        formatted_derivative_equation['linear'] = \
            formatted_derivative_equation['sympy_lhs'] not in (e.lhs for e in self._non_linear_eqs)
        return formatted_derivative_equation

    def format_nonlinear_state_vars(self):
        formatted_nonlinear_state_vars = []
        for sv in self._vars_for_template['state_vars']:
            if sv['sympy_var'] in self._non_linear_state_vars:
                formatted_nonlinear_state_vars.append(sv)

        # order by name
        formatted_nonlinear_state_vars.sort(key=lambda d: d['var'])
        return formatted_nonlinear_state_vars

    def format_linear_deriv_eqs(self, linear_deriv_eqs):
        """ Format linear derivative equations beloning, to update what belongs were"""
        return self._format_derivative_equations(self._linear_equations)

    def format_residual_equations(self):
        """Update the state vars, savings residual and jacobian info for outputing"""
        residual_equations = [{'residual_index': self._vars_for_template['nonlinear_state_vars'].index(sv),
                               'state_var_index': i,
                               'var': self._vars_for_template['y_derivatives'][i]}
                              for i, sv in enumerate(self._formatted_state_vars) if not sv['linear']]
        return residual_equations

    def format_jacobian(self):
        """Format the jacobian to allow opt model to update what belongs were"""
        modifiers_with_defining_eqs = set((eq[0] for eq in self._jacobian_equations)) | self._model.state_vars
        return format_jacobian(self._jacobian_equations, self._jacobian_matrix, self._printer,
                               partial(self._print_rhs_with_modifiers,
                                       modifiers_with_defining_eqs=modifiers_with_defining_eqs),
                               swap_inner_outer_index=False,
                               skip_0_entries=False)
