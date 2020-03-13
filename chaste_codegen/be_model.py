import chaste_codegen as cg
import time
import sympy as sp
from cellmlmanip.model import VariableDummy
from chaste_codegen._partial_eval import partial_eval
from enum import Enum
from sympy.logic.boolalg import (BooleanTrue, BooleanFalse)
from sympy.codegen.cfunctions import (log10, log2)



#todo: Factor, partial eval or not?
class BeModel(cg.ChasteModel):
    """ Holds template and information specific for the Backwards Euler model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, use_analytic_jacobian=True, **kwargs)
            # get deriv eqs and substitute in all variables other than state vars
        self._derivative_equations = \
            partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
        self._non_linear_state_vars = self._get_non_linear_state_vars()
        self._jacobian_equations, self._jacobian_matrix = self._get_jacobian()
        self._formatted_state_vars, self._formatted_nonlinear_state_vars, self._formatted_residual_equations, self._formatted_derivative_eqs = \
            self._update_state_vars()
        self._formatted_rearranged_linear_derivs = self._format_rearranged_linear_derivs()
        self._formatted_jacobian_equations, self._formatted_jacobian_matrix_entries = self._format_jacobian()

    def _get_non_linear_state_vars(self):

        class KINDS(Enum):
            none = 1
            Linear = 2
            Nonlinear = 3

        def max_kind(state_var, operands):
            result = KINDS.none
            for op in operands:
                res = check_expr(op, state_var)
                if res == KINDS.Nonlinear:
                    return KINDS.Nonlinear
                elif res == KINDS.Linear:
                    result = res
            return result

        def check_expr(expr, state_var):
            result = None
            operands = expr.args
            # No need to recurse as we're doing this with partially evaluated derivative equations!
            if expr is state_var:
                result = KINDS.Linear
            elif expr is self._membrane_voltage_var or len(expr.free_symbols) == 0 or isinstance(expr, sp.Function('GetIntracellularAreaStimulus', real=True)): # constant, V or GetIntracellularAreaStimulus(time)
                result = KINDS.none
            elif expr in self._state_vars:
                result = KINDS.Nonlinear

            elif isinstance(expr, sp.Piecewise):
                # If any conditions have a dependence, then we're
                # nonlinear.  Otherwise, all the pieces must be the same
                # (and that's what we are) or we're nonlinear.
                for cond in expr.args:
                    if check_expr(cond[1], state_var) != KINDS.none:
                        result = KINDS.Nonlinear
                        break
                else:
                    # Conditions all OK
                    for e in expr.args:
                        res = check_expr(e[0], state_var)
                        if result is not None and res != result:
                            # We have a difference
                            result = KINDS.Nonlinear
                            break
                        result = res
            elif isinstance(expr, sp.Mul):
                # Linear iff only 1 linear operand
                result = KINDS.none
                lin = 0
                for op in operands:
                    res = check_expr(op, state_var)
                    if res == KINDS.Linear: lin += 1
                    elif res == KINDS.Nonlinear: lin += 2
                    if lin > 1:
                        result = KINDS.Nonlinear
                        break
                    elif lin == 1:
                        result = KINDS.Linear
            elif isinstance(expr, sp.Add) or isinstance(expr, sp.boolalg.BooleanFunction) or isinstance(expr, sp.relational.Relational):
                # Linear if any operand linear, and none non-linear
                result = max_kind(state_var, operands)
            elif isinstance(expr, sp.Pow):
                if state_var not in expr.free_symbols:
                    result = max_kind(state_var, operands)
                elif len(expr.args) == 2 and expr.args[1] == -1: # x/y divide is represented as x * pow(y, -1)
                    result = check_expr(expr.args[0], state_var) # Linear iff only numerator linear
                else:
                    result = KINDS.Nonlinear
            elif isinstance(expr, sp.log) or isinstance(expr, log10) or isinstance(expr, log2) or isinstance(expr, cg.RealFunction) or isinstance(expr, sp.functions.elementary.trigonometric.TrigonometricFunction) or isinstance(expr, sp.functions.elementary.hyperbolic.HyperbolicFunction) or isinstance(expr, sp.functions.elementary.trigonometric.InverseTrigonometricFunction) or isinstance(expr, sp.functions.elementary.hyperbolic.InverseHyperbolicFunction):
                if state_var not in expr.free_symbols:
                    result = check_expr(expr.args[0], state_var)
                else:
                    result = KINDS.Nonlinear
            else:
                assert False, 'Not implemented expression type: ' + str(type(expr))           
            return result

        return [eq.lhs.args[0] for eq in self._derivative_equations
                if isinstance(eq.lhs, sp.Derivative) and
                eq.lhs.args[0] != self._membrane_voltage_var and
                check_expr(eq.rhs, eq.lhs.args[0]) != KINDS.Linear]

    def _format_rearranged_linear_derivs(self):
        def rearrange_expr(expr, var): #expr already in piecewise_fold form
            """Rearrange an expression into the form g + h*var."""
            if isinstance(expr, sp.Piecewise,):
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
                    pieces_i = zip(map(lambda gh: gh[i], cases_ghs),
                                conds)
                    pieces_i = [p for p in pieces_i if p[0] is not None] # Remove cases that are None
                    if pieces_i:
                        new_expr = sp.Piecewise(*pieces_i)
                    else:
                        new_expr = None
                    return new_expr
                gh = (piecewise_branch(0), piecewise_branch(1))

            else:
                h = sp.Wild('h', exclude=[var])
                g = sp.Wild('g', exclude=[var])
                match = expr.expand().match(g + h*var)
                gh = (match[g], match[h]) if match is not None else None
            return gh

        def print_rearrange_expr(expr, var):
            expr = sp.piecewise_fold(expr)
            gh = rearrange_expr(expr, var)
            return {'state_var_index': self._state_vars.index(var), 'var': self._printer.doprint(var), 'g': self._printer.doprint(gh[0]) , 'h': self._printer.doprint(gh[1])}

        linear_derivs = [eq for eq in self._derivative_equations if isinstance(eq.lhs, sp.Derivative) and eq.lhs.args[0] not in self._non_linear_state_vars and not eq.lhs.args[0] == self._membrane_voltage_var]
        linear_derivs = sorted(linear_derivs, key=lambda d: self._get_var_display_name(d.lhs.args[0]))
        formatted_expr =  [print_rearrange_expr(d.rhs, d.lhs.args[0]) for d in linear_derivs]
        return formatted_expr

    def _get_jacobian(self):
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
        formatted_state_vars = self._formatted_state_vars
        residual_equations = []
        formatted_derivative_eqs = self._formatted_derivative_eqs
        jacobian_symbols = set()
        residual_eq_symbols = set()

        for eq in self._jacobian_equations:
            jacobian_symbols.update(eq[1].free_symbols)
        for eq in self._jacobian_matrix:
            jacobian_symbols.update(eq.free_symbols)

        non_linear_derivs = [eq.lhs for eq in self._derivative_equations if isinstance(eq.lhs, sp.Derivative) and eq.lhs.args[0] in self._non_linear_state_vars]
        non_linear_eqs = self._model.get_equations_for(non_linear_derivs)
        for eq in non_linear_eqs:
            residual_eq_symbols.update(eq.rhs.free_symbols)
        non_linear_eqs = [self._printer.doprint(eq.lhs) for eq in non_linear_eqs]
        for i, d in enumerate(formatted_derivative_eqs):
            formatted_derivative_eqs[i]['linear'] = d['lhs'] not in non_linear_eqs



        formatted_nonlinear_state_vars = \
            [s for s in formatted_state_vars if s['sympy_var'] in self._non_linear_state_vars]
        # order by name
        formatted_nonlinear_state_vars = sorted(formatted_nonlinear_state_vars, key=lambda d: d['var'])
        for i, sv in enumerate(formatted_nonlinear_state_vars):
            formatted_nonlinear_state_vars[i]['linear'] = False
            formatted_nonlinear_state_vars[i]['in_jacobian'] = sv['sympy_var'] in jacobian_symbols
            formatted_nonlinear_state_vars[i]['in_residual_eqs'] = sv['sympy_var'] in residual_eq_symbols

        for i, sv in enumerate(formatted_state_vars):
            formatted_state_vars[i]['linear'] = sv['sympy_var'] not in self._non_linear_state_vars
            formatted_state_vars[i]['in_jacobian'] = sv['sympy_var'] in jacobian_symbols
            formatted_state_vars[i]['in_residual_eqs'] = sv['sympy_var'] in residual_eq_symbols
            if not formatted_state_vars[i]['linear']:
                residual_equations.append({'residual_index': formatted_nonlinear_state_vars.index(sv),
                                           'state_var_index': i, 'var': self._formatted_y_derivatives[i]})



        return formatted_state_vars, formatted_nonlinear_state_vars, residual_equations, formatted_derivative_eqs

    def _format_jacobian(self):
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
            'y_derivatives': self._formatted_y_derivatives,
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
            'linear_deriv_eqs': self._formatted_rearranged_linear_derivs})
