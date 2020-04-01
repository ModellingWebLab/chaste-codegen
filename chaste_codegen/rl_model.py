import time

import sympy as sp

import chaste_codegen as cg
from chaste_codegen._linearity_check import get_non_linear_state_vars, derives_eqs_partial_eval_non_linear
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class RlModel(ChasteModel):
    """ Holds template and information specific for the Backwards Euler model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, use_analytic_jacobian=True, **kwargs)
        self._derivative_equations = \
            partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
        self._non_linear_state_vars = \
            get_non_linear_state_vars(self._derivative_equations, self._membrane_voltage_var, self._state_vars, self._printer)

        self._derivative_alpha_beta, self._formatted_alpha_beta_eqs = self._get_formatted_Alpha_Beta()
        pass

    def _get_formatted_Alpha_Beta(self):
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
        
        derivative_alpha_beta, derivative_alpha_beta_eqs = [], set()
        
        # Substitute non-linear bits into derivative equations, so that we can pattern match
        linear_derivs_eqs = derives_eqs_partial_eval_non_linear(self._y_derivatives, self._non_linear_state_vars, self._membrane_voltage_var, self._state_vars, self._get_equations_for)

        for deriv in self._y_derivatives:
            if deriv.args[0] in self._non_linear_state_vars or deriv.args[0] is self._membrane_voltage_var:
                derivative_alpha_beta.append({'type': 'non_linear', 'deriv': self._printer.doprint(deriv) })
                derivative_alpha_beta_eqs.add(deriv)
            else:
                eq = [e for e in linear_derivs_eqs if e.lhs == deriv][0]
                ab = match_alpha_beta(eq.rhs, eq.lhs.args[0])
                it = match_inf_tau(eq.rhs, eq.lhs.args[0])
                rAlphaOrTau = ab['alpha'] if ab['alpha'] else it['tau']
                rBetaOrInf = ab['beta'] if ab['alpha'] else it['inf']
                derivative_alpha_beta.append({'type': 'alphabeta' if ab['alpha'] else 'inftau', 'rAlphaOrTau': rAlphaOrTau, 'rBetaOrInf': rBetaOrInf})
                derivative_alpha_beta_eqs.update(rAlphaOrTau.free_symbols | rBetaOrInf.free_symbols)

        formatted_eqs = self._format_derivative_equations(self._get_equations_for(derivative_alpha_beta_eqs))
        return derivative_alpha_beta, formatted_eqs

    def generate_chaste_code(self):
        """ Generates and stores chaste code for the Normal model"""

        # Generate hpp for model
        template = cg.load_template('rl_model.hpp')
        self.generated_hpp = template.render({
            'converter_version': cg.__version__,
            'model_name': self._model.name,
            'class_name': self.class_name,
            'dynamically_loadable': self._dynamically_loadable,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'default_stimulus_equations': self._formatted_default_stimulus,
            'use_get_intracellular_calcium_concentration':
                self._cytosolic_calcium_concentration_var in self._state_vars,
            'free_variable': self._free_variable,
            'use_verify_state_variables': self._use_verify_state_variables,
            'derived_quantities': self._formatted_derived_quant})

        # Generate cpp for model
        template = cg.load_template('rl_model.cpp')
        self.generated_cpp = template.render({
            'converter_version': cg.__version__,
            'model_name': self._model.name,
            'file_name': self.file_name,
            'class_name': self.class_name,
            'header_ext': self._header_ext,
            'dynamically_loadable': self._dynamically_loadable,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'default_stimulus_equations': self._formatted_default_stimulus,
            'use_get_intracellular_calcium_concentration':
                self._cytosolic_calcium_concentration_var in self._state_vars,
            'membrane_voltage_index': self._MEMBRANE_VOLTAGE_INDEX,
            'cytosolic_calcium_concentration_index':
                self._state_vars.index(self._cytosolic_calcium_concentration_var)
                if self._cytosolic_calcium_concentration_var in self._state_vars
                else self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX,
            'state_vars': self._formatted_state_vars,
            'ionic_vars': self._formatted_extended_equations_for_ionic_vars,
#            'y_derivative_equations': self._formatted_derivative_eqs,
#            'y_derivatives': self._formatted_y_derivatives,
            'use_capacitance_i_ionic': self._current_unit_and_capacitance['use_capacitance'],
            'free_variable': self._free_variable,
            'ode_system_information': self._ode_system_information,
            'modifiable_parameters': self._formatted_modifiable_parameters,
            'named_attributes': self._named_attributes,
            'use_verify_state_variables': self._use_verify_state_variables,
            'derived_quantities': self._formatted_derived_quant,
            'derived_quantity_equations': self._formatted_quant_eqs,
            'derivative_alpha_beta': self._derivative_alpha_beta,
            'derivative_alpha_beta': self._formatted_alpha_beta_eqs})
