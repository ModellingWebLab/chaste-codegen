from enum import Enum

import sympy as sp
from sympy.codegen.cfunctions import log2, log10

import chaste_codegen as cg


class KINDS(Enum):
    NONE = 1
    LINEAR = 2
    NONLINEAR = 3


def check_expr(expr, state_var, membrane_voltage_var, state_vars):
    def max_kind(state_var, operands):
        result = KINDS.NONE
        for op in operands:
            res = check_expr(op, state_var, membrane_voltage_var, state_vars)
            if res == KINDS.NONLINEAR:
                return KINDS.NONLINEAR
            elif res == KINDS.LINEAR:
                result = res
        return result
    result = None
    operands = expr.args
    # No need to recurse as we're doing this with partially evaluated derivative equations!
    if expr is state_var:
        result = KINDS.LINEAR
    elif expr is membrane_voltage_var or len(expr.free_symbols) == 0 or\
            isinstance(expr, sp.Function('GetIntracellularAreaStimulus', real=True)):
        # constant, V or GetIntracellularAreaStimulus(time)
        result = KINDS.NONE
    elif expr in state_vars:
        result = KINDS.NONLINEAR

    elif isinstance(expr, sp.Piecewise):
        # If any conditions have a dependence, then we're
        # non-linear  Otherwise, all the pieces must be the same
        # (and that's what we are) or we're non-linear.
        for cond in expr.args:
            if check_expr(cond[1], state_var, membrane_voltage_var, state_vars) != KINDS.NONE:
                result = KINDS.NONLINEAR
                break
        else:
            # Conditions all OK
            for e in expr.args:
                res = check_expr(e[0], state_var, membrane_voltage_var, state_vars)
                if result is not None and res != result:
                    # We have a difference
                    result = KINDS.NONLINEAR
                    break
                result = res
    elif isinstance(expr, sp.Mul):
        # Linear iff only 1 linear operand
        result = KINDS.NONE
        lin = 0
        for op in operands:
            res = check_expr(op, state_var, membrane_voltage_var, state_vars)
            if res == KINDS.LINEAR:
                lin += 1
            elif res == KINDS.NONLINEAR:
                lin += 2
            if lin > 1:
                result = KINDS.NONLINEAR
                break
            elif lin == 1:
                result = KINDS.LINEAR
    elif isinstance(expr, sp.Add) or isinstance(expr, sp.boolalg.BooleanFunction) or\
            isinstance(expr, sp.relational.Relational):
        # linear if any operand linear, and non-linear
        result = max_kind(state_var, operands)
    elif isinstance(expr, sp.Pow):
        if state_var not in expr.free_symbols:
            result = max_kind(state_var, operands)
        elif len(expr.args) == 2 and expr.args[1] == -1:  # x/y divide is represented as x * pow(y, -1)
            # Linear iff only numerator linear
            result = check_expr(expr.args[0], state_var, membrane_voltage_var, state_vars)
        else:
            result = KINDS.NONLINEAR
    elif isinstance(expr, sp.log) or isinstance(expr, log10) or isinstance(expr, log2) or\
            isinstance(expr, cg.RealFunction) or\
            isinstance(expr, sp.functions.elementary.trigonometric.TrigonometricFunction) or\
            isinstance(expr, sp.functions.elementary.hyperbolic.HyperbolicFunction) or\
            isinstance(expr, sp.functions.elementary.trigonometric.InverseTrigonometricFunction) or\
            isinstance(expr, sp.functions.elementary.hyperbolic.InverseHyperbolicFunction):
        if state_var not in expr.free_symbols:
            result = check_expr(expr.args[0], state_var, membrane_voltage_var, state_vars)
        else:
            result = KINDS.NONLINEAR
    return result
