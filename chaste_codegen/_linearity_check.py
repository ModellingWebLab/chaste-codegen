from enum import Enum
from functools import lru_cache

from cellmlmanip.model import Variable
from sympy import (
    Add,
    Derivative,
    Eq,
    Function,
    Mul,
    Piecewise,
    Pow,
    log,
)
from sympy.codegen.cfunctions import log2, log10
from sympy.core.relational import Relational
from sympy.functions.elementary.hyperbolic import HyperbolicFunction, InverseHyperbolicFunction
from sympy.functions.elementary.trigonometric import InverseTrigonometricFunction, TrigonometricFunction
from sympy.logic.boolalg import BooleanFunction

import chaste_codegen as cg


class KINDS(Enum):
    NONE = 1
    LINEAR = 2
    NONLINEAR = 3


@lru_cache(maxsize=128)
def _check_expr(expr, state_var, membrane_voltage_var, state_vars):
    """Check the kind of expression given (NONE, LINEAR or NONLINEAR)

    Determines whether it has a linear dependence on the dependent variable.
    We also require it to not depend on any other state variable, except V.

    :param expr: the expression to check
    :param state_var: the (dependant) state variable we're currently checking against for linearity
    :param membrane_voltage_var: the variable representing Voltage
    :param state_vars: the state variables in the model the expression comes from
    :return: the kind of expr (NONE, LINEAR or NONLINEAR)
    """
    @lru_cache(maxsize=128)
    def max_kind(state_var, operands):
        result = KINDS.NONE
        for op in operands:
            res = _check_expr(op, state_var, membrane_voltage_var, state_vars)
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
            isinstance(expr, Function('GetIntracellularAreaStimulus', real=True)):
        # constant, V or GetIntracellularAreaStimulus(time)
        result = KINDS.NONE
    elif expr in state_vars:
        result = KINDS.NONLINEAR

    elif isinstance(expr, Piecewise):
        # If any conditions have a dependence, then we're
        # non-linear  Otherwise, all the pieces must be the same
        # (and that's what we are) or we're non-linear.
        for cond in expr.args:
            if _check_expr(cond[1], state_var, membrane_voltage_var, state_vars) != KINDS.NONE:
                result = KINDS.NONLINEAR
                break
        else:
            # Conditions all OK
            for e in expr.args:
                res = _check_expr(e[0], state_var, membrane_voltage_var, state_vars)
                if result is not None and res != result:
                    # We have a difference
                    result = KINDS.NONLINEAR
                    break
                result = res
    elif isinstance(expr, Mul):
        # Linear iff only 1 linear operand
        result = KINDS.NONE
        lin = 0
        for op in operands:
            res = _check_expr(op, state_var, membrane_voltage_var, state_vars)
            if res == KINDS.LINEAR:
                lin += 1
            elif res == KINDS.NONLINEAR:
                lin += 2
            if lin > 1:
                result = KINDS.NONLINEAR
                break
            elif lin == 1:
                result = KINDS.LINEAR
    elif isinstance(expr, Add) or isinstance(expr, BooleanFunction) or\
            isinstance(expr, Relational):
        # linear if any operand linear, and non-linear
        result = max_kind(state_var, operands)
    elif isinstance(expr, Pow):
        if state_var not in expr.free_symbols:
            result = max_kind(state_var, operands)
        elif len(expr.args) == 2 and expr.args[1] == -1:  # x/y divide is represented as x * pow(y, -1)
            # Linear iff only numerator linear
            result = _check_expr(expr.args[0], state_var, membrane_voltage_var, state_vars)
        else:
            result = KINDS.NONLINEAR
    elif isinstance(expr, (log, log10, log2)) or\
            isinstance(expr, (cg.RealFunction, TrigonometricFunction, HyperbolicFunction, InverseTrigonometricFunction,
                              InverseHyperbolicFunction)):
        if state_var not in expr.free_symbols:
            result = _check_expr(expr.args[0], state_var, membrane_voltage_var, state_vars)
        else:
            result = KINDS.NONLINEAR
    return result


def get_non_linear_state_vars(derivative_equations, membrane_voltage_var, state_vars):
    """Returns the state vars whose derivative expressions are non linear"""

    assert all(map(lambda eq: isinstance(eq, Eq), derivative_equations)), (
        "Expecting derivative_equations to be a collection of equations")
    assert isinstance(membrane_voltage_var, Variable), "membrane_voltage_var should be a cellmlmanip.Variable"
    assert all(map(lambda v: isinstance(v, Variable), state_vars)), "state_vars should be cellmlmanip Variables"
    assert len(state_vars) > 0 and len(derivative_equations) > 0, ("Expecting state_vars and derivative_equations "
                                                                   "not to be empty")

    return set([eq.lhs.args[0] for eq in derivative_equations
                if isinstance(eq.lhs, Derivative) and
                eq.lhs.args[0] != membrane_voltage_var and
                _check_expr(eq.rhs, eq.lhs.args[0], membrane_voltage_var, tuple(state_vars)) != KINDS.LINEAR])


def subst_deriv_eqs_non_linear_vars(y_derivatives, non_linear_state_vars, membrane_voltage_var, state_vars,
                                    get_equations_for_func):
    """Substitutes variables in the derivative equation for their definition if the definition is non-linear

    The derivative equations contain variables defined in other equations alpha = ..., (e.g. dv/dt = alpha +..
    To be able to rearrange these in h + g*var form (or alpha*(1-x) - beta*x or (inf-x)/tau),
    we need to substitute the rhs definition for those variables. This leads to some c++ floating point precision.
    However we know that the rhs definitions for which the rhs definition only contain V will wholly end up in h
    Leaving those variable in sees them as linear in the statevar and means they end up in h*var
    Therefore we will only substitute in definitions for equations we know contain state vars (other than V)
    This way we reduce the complexity of equations matched and reduce the chance of floating point errors"""

    assert isinstance(membrane_voltage_var, Variable), "membrane_voltage_var should be a cellmlmanip.Variable"
    assert all(map(lambda eq: isinstance(eq, Derivative), y_derivatives)), "Expecting y_derivatives to be Derivatives"
    assert all(map(lambda eq: isinstance(eq, Variable), non_linear_state_vars)), ("Expecting non_linear_state_vars all"
                                                                                  " to be cellmlmanip.Variable")
    assert all(map(lambda eq: isinstance(eq, Variable), state_vars)), ("Expecting state_vars all to be cellmlmanip."
                                                                       "Variable")
    assert callable(get_equations_for_func), 'Expecting get_equations_for_func to be a callable'

    # get the state vars for which derivative is linear
    linear_sv = filter(lambda d: d.args[0] not in non_linear_state_vars and not d.args[0] == membrane_voltage_var,
                       y_derivatives)

    non_lin_sym = set(state_vars)  # state vars and lhs of equations containing state vars
    linear_derivs_eqs = []
    subs_dict = {}
    for eq in get_equations_for_func(linear_sv):
        # Substitute variables into the derivative where their definition contains a statevar
        if isinstance(eq.lhs, Derivative):
            linear_derivs_eqs.append(Eq(eq.lhs, eq.rhs.xreplace(subs_dict)))
        elif not (eq.rhs.free_symbols - set([membrane_voltage_var])).intersection(non_lin_sym):
            # if the equation doesn't contain any statevars (except V)
            # or other variables whose definition contains a statevar just add this equation to the list
            linear_derivs_eqs.append(eq)
        else:
            # if the rhs has a statevar (or a varible whose def has a statevar) add to dictionary for substitution
            non_lin_sym.add(eq.lhs)
            subs_dict[eq.lhs] = eq.rhs.xreplace(subs_dict)
    return linear_derivs_eqs
