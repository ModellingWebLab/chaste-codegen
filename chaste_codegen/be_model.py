import time

import sympy as sp

import chaste_codegen as cg
from chaste_codegen._linearity_check import get_non_linear_state_vars, derives_eqs_partial_eval_non_linear
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.chaste_model import ChasteModel


class BeModel(ChasteModel):
    """ Holds template and information specific for the Backwards Euler model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, use_analytic_jacobian=True, **kwargs)
        # get deriv eqs and substitute in all variables other than state vars
        self._derivative_equations = \
            partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
        self._non_linear_state_vars = \
            get_non_linear_state_vars(self._derivative_equations, self._membrane_voltage_var, self._state_vars, self._printer)

        self._jacobian_equations, self._jacobian_matrix = self._get_jacobian()
        self._formatted_state_vars, self._formatted_nonlinear_state_vars, self._formatted_residual_equations, \
            self._formatted_derivative_eqs = self._update_state_vars()
        self._formatted_rearranged_linear_derivs, self._formatted_linear_equations = \
            self._format_rearranged_linear_derivs()
        self._formatted_jacobian_equations, self._formatted_jacobian_matrix_entries = self._format_jacobian()

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
        linear_derivs_eqs = derives_eqs_partial_eval_non_linear(self._y_derivatives, self._non_linear_state_vars, self._membrane_voltage_var, self._state_vars, self._get_equations_for)

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

    def _get_jacobian(self):
        """"Get the jacobian for the non-linear state vars """
        if len(self._non_linear_state_vars) == 0:
            return [], sp.Matrix([])
        state_var_matrix = sp.Matrix(self._non_linear_state_vars)
        # get derivatives for non-linear state vars
        derivative_eqs = [d for d in self._derivative_equations if d.lhs.args[0] in self._non_linear_state_vars]
        # sort by state var
        derivative_eqs = sorted(derivative_eqs, key=lambda d: self._non_linear_state_vars.index(d.lhs.args[0]))
        # we're only interested in the rhs
        derivative_eqs = [eq.rhs for eq in derivative_eqs]
        derivative_eq_matrix = sp.Matrix(derivative_eqs)
        jacobian_matrix = derivative_eq_matrix.jacobian(state_var_matrix)
        # update state variables
        jacobian_equations, jacobian_matrix = sp.cse(jacobian_matrix, order='none')
        return jacobian_equations, sp.Matrix(jacobian_matrix)

    def _update_state_vars(self):
        """Update the state vars, savings residual and jacobian info for outputing"""
        formatted_state_vars = self._formatted_state_vars
        residual_equations = []
        formatted_derivative_eqs = self._formatted_derivative_eqs
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
                                           'state_var_index': i, 'var': self._formatted_y_derivatives[i]})

        return formatted_state_vars, formatted_nonlinear_state_vars, residual_equations, formatted_derivative_eqs

    def _format_jacobian(self):
        """Format the jacobian for outputting"""
        assert isinstance(self._jacobian_matrix, sp.Matrix), 'Expecting a jacobian as a matrix'
        equations = [{'lhs': self._printer.doprint(eq[0]), 'rhs': self._printer.doprint(eq[1])}
                     for eq in self._jacobian_equations]
        rows, cols = self._jacobian_matrix.shape
        jacobian = []
        for i in range(rows):
            for j in range(cols):
                matrix_entry = self._jacobian_matrix[i, j]
                jacobian.append({'i': i, 'j': j, 'entry': self._printer.doprint(matrix_entry)})
        return equations, jacobian

    def generate_chaste_code(self):
        """ Generates and stores chaste code for the BE model"""
        # Generate hpp for model
        template = cg.load_template('be_model.hpp')
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
            'derived_quantities': self._formatted_derived_quant,
            'nonlinear_state_vars': self._formatted_nonlinear_state_vars})

        # Generate cpp for model
        template = cg.load_template('be_model.cpp')
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
            'y_derivative_equations': self._formatted_derivative_eqs,
            'use_capacitance_i_ionic': self._current_unit_and_capacitance['use_capacitance'],
            'free_variable': self._free_variable,
            'ode_system_information': self._ode_system_information,
            'modifiable_parameters': self._formatted_modifiable_parameters,
            'named_attributes': self._named_attributes,
            'use_verify_state_variables': self._use_verify_state_variables,
            'derived_quantities': self._formatted_derived_quant,
            'derived_quantity_equations': self._formatted_quant_eqs,
            'jacobian_equations': self._formatted_jacobian_equations,
            'jacobian_entries': self._formatted_jacobian_matrix_entries,
            'nonlinear_state_vars': self._formatted_nonlinear_state_vars,
            'residual_equations': self._formatted_residual_equations,
            'linear_deriv_eqs': self._formatted_rearranged_linear_derivs,
            'linear_equations': self._formatted_linear_equations})
