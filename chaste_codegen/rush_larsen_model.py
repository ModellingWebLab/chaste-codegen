import sympy as sp

from chaste_codegen._linearity_check import get_non_linear_state_vars, subst_deriv_eqs_non_linear_vars
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class RushLarsenModel(ChasteModel):
    """ Holds template and information specific for the RushLarsen model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'rush_larsen_model.hpp'
        self._cpp_template = 'rush_larsen_model.cpp'

        self._derivative_equations = \
            partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
        self._non_linear_state_vars = \
            get_non_linear_state_vars(self._derivative_equations, self._membrane_voltage_var,
                                      self._state_vars, self._printer)

        self._vars_for_template['derivative_alpha_beta'], self._vars_for_template['derivative_alpha_beta_eqs'], \
            self._vars_in_derivative_alpha_beta = self._get_formatted_alpha_beta()
        self._update_state_vars()
        self._vars_for_template['derivative_alpha_beta_eqs'] = \
            self._format_derivative_equations(self._vars_for_template['derivative_alpha_beta_eqs'])

    def _get_formatted_alpha_beta(self):
        """Gets the information for r_alpha_or_tau, r_beta_or_inf in the c++ output and formatted equations"""
        def match_alpha_beta(expr, x):  # expr already in piecewise_fold form
            """Match alpha*(1-x) - beta*x"""
            a, b = None, None
            alpha = sp.Wild('alpha', exclude=[x])
            beta = sp.Wild('beta', exclude=[x])
            match = expr.expand().match((alpha - x * alpha) - beta * x)
            if match is not None:
                a, b = match[alpha], match[beta]
            return {'alpha': a, 'beta': b}

        def match_inf_tau(expr, x):  # expr already in piecewise_fold form
            """Match (inf-x)/tau"""
            i, t = None, None
            inf = sp.Wild('inf', exclude=[x])
            tau = sp.Wild('tau', exclude=[x])
            match = expr.expand().match(inf / tau - x / tau)
            if match is not None:
                i, t = match[inf], match[tau]
            return {'inf': i, 'tau': t}

        derivative_alpha_beta, vars_in_derivative_alpha_beta = [], set()

        # Substitute non-linear bits into derivative equations, so that we can pattern match
        linear_derivs_eqs = subst_deriv_eqs_non_linear_vars(self._y_derivatives, self._non_linear_state_vars,
                                                            self._membrane_voltage_var, self._state_vars,
                                                            self._get_equations_for)

        for deriv in self._y_derivatives:
            ab = {'alpha': None}
            it = {'tau': None}
            # get match if possible (deiv is linear)
            if deriv.args[0] not in self._non_linear_state_vars and deriv.args[0] is not self._membrane_voltage_var:
                eq = [e for e in linear_derivs_eqs if e.lhs == deriv][0]
                ab = match_alpha_beta(eq.rhs, eq.lhs.args[0])
                if ab['alpha'] is None:
                    it = match_inf_tau(eq.rhs, eq.lhs.args[0])

            # check if there was a match
            if ab['alpha'] is not None or it['tau'] is not None:
                eq = [e for e in linear_derivs_eqs if e.lhs == deriv][0]
                r_alpha_or_tau = ab['alpha'] if ab['alpha'] is not None else it['tau']
                r_beta_or_inf = ab['beta'] if ab['beta'] is not None else it['inf']
                derivative_alpha_beta.append({'type': 'alphabeta' if ab['alpha'] is not None else 'inftau',
                                              'r_alpha_or_tau': self._printer.doprint(r_alpha_or_tau),
                                              'r_beta_or_inf': self._printer.doprint(r_beta_or_inf)})
                vars_in_derivative_alpha_beta.update(r_alpha_or_tau.free_symbols | r_beta_or_inf.free_symbols)
            else:
                derivative_alpha_beta.append({'type': 'non_linear', 'deriv': self._printer.doprint(deriv)})
                vars_in_derivative_alpha_beta.add(deriv)

        deriv_eqs_EvaluateEquations = self._get_equations_for(vars_in_derivative_alpha_beta)
        return derivative_alpha_beta, deriv_eqs_EvaluateEquations, vars_in_derivative_alpha_beta

    def _update_state_vars(self):
        """Updates formatting of state vars to make sure the correct ones are included in the output"""
        # Get all used variables for derivative eqs
        deriv_variables = set()
        for eq in self._vars_for_template['derivative_alpha_beta_eqs']:
            deriv_variables.update(eq.rhs.free_symbols)

        for sv in self._formatted_state_vars:
            sv['in_ab'] = sv['sympy_var'] in deriv_variables
