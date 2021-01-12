from math import isclose

from sympy import (
    Abs,
    Add,
    Eq,
    Float,
    I,
    Mul,
    Piecewise,
    Pow,
    Wild,
    log,
    solveset,
)
from chaste_codegen._optimize import optimize_expr
from chaste_codegen._math_functions import exp_


def _get_U(expr, V, U_offset, exp_function):
    Z = Wild('Z', real=True)
    X = Wild('X', real=True, include=[V])
    Y = Wild('Y', real=True)

    def check_bottom_match(m):
        return m is not None and X in m and Z in m and Z != 0

    def check_top_match(m, sp):
        return m is not None and Z in m and Z != 0 and (sp == m[Y] or (isinstance(sp, Float) and isinstance(m[Y], Float) and isclose(m[Y], sp)))

    (vs, ve, U, sp) = None, None, None, None
    # the denominator is all args where a **-1
    numerator = set(a for a in expr.args if not isinstance(a, Pow) or a.args[1] != -1.0)
    denominator = set(a.args[0] for a in expr.args if isinstance(a, Pow) and a.args[1] == -1.0)

    if len(denominator) > 0 and len(numerator) > 0:
        # U might be on top, try numerator / denominator and denominator / numerator
        for denom, num in ((denominator, numerator), (numerator, denominator)):
            found_on_top = False
            for d in denom:
                if d.has(exp_function):
                    find_U = d.match(exp_function(X) * -Z + 1.0)
                    if not check_bottom_match(find_U):
                        find_U = d.match(exp_function(X) * Z - 1.0)
                    if check_bottom_match(find_U):
                        u = (find_U[X] + log(find_U[Z]))
                        try:
                            sp = tuple(filter(lambda s: not s.has(I), solveset(u, V)))
                            if sp:
                                find_v_low = solveset(u + U_offset, V)
                                find_v_up = solveset(u - U_offset, V)
                                find_v_low = tuple(find_v_low)
                                find_v_up = tuple(find_v_up)
                                if find_v_low and find_v_up:
                                    (vs, ve, U, sp) = (find_v_low[-1], find_v_up[-1], u, sp[-1])
                        except TypeError:
                            pass  # Result could be 'ConditionSet' which is not iterable and not Real

                    if vs is not None:  # check top
                        for n in num:
                            match = n.match(Z * V - Z * Y)
                            found_on_top = check_top_match(match, sp)
                            if not found_on_top:
                                match = n.match(exp_function(Z * V - Z * Y))
                                found_on_top = check_top_match(match, sp)
                                if not found_on_top:
                                    match = n.match(Z * V - Z * sp)
                                    found_on_top = match is not None and Z in match and Z != 0
                                    if not found_on_top:
                                        match = n.match(exp_function(Z * V - Z * sp))
                                        found_on_top = match is not None and Z in match and Z != 0
                            if found_on_top:
                                break
                        break
            if vs is not None and found_on_top: #found U, no need to try further
                break
            else:
                (vs, ve, U, sp) = None, None, None, None
    return (vs, ve, U, sp)


def _generate_piecewise(vs, ve, sp, ex, V):
    """Generates a piecewsie for expression ex based on the singularity point sp and vmin (vs) and vmax (ve) """
    def f(Vx, e):
        return e.xreplace({V: Vx})

    if vs is None:
        return ex

    return Piecewise(*[(f(vs, ex) + ((V - vs) / (ve - vs)) * (f(ve, ex) - f(vs, ex)),
                        Abs(V - sp) < Abs((ve - vs) / 2)), (ex, True)])


def _new_expr_parts(expr, V, U_offset, exp_function):
    """Removes suitable singularities and replaces it with a piecewise, returning (vs, ve, sp, has_singularity)"""
    if not expr.has(exp_function):
        return (None, None, None, expr, False)

    if isinstance(expr, Mul):  # 1 * A --> A
        expr = Mul(*[a for a in expr.args if not a == 1.0])

    if isinstance(expr, Add):  # A+B
        new_expr_parts = []
        for a in expr.args:
            new_expr_parts.append(_new_expr_parts(a, V, U_offset, exp_function))

        # For multiple parts with the same singularity point pick the widest range
        range = [item for (vs, ve, _, _, _) in new_expr_parts for item in (vs, ve)]
        if len(new_expr_parts) > 1 and len(set([sp for (_, _, sp, _, _) in new_expr_parts])) == 1 \
                and all(isinstance(b, Float) for b in range):
            sp = new_expr_parts[0][2]
            vs, ve = min(range), max(range)
            new_expr = (vs, ve, sp, expr, True)
        else:
            expr_parts = []
            is_piecewise = False
            for vs, ve, sp, ex, has_piecewise in new_expr_parts:
                is_piecewise = is_piecewise or has_piecewise or vs is not None
                expr_parts.append(_generate_piecewise(vs, ve, sp, ex, V))
            new_expr = (None, None, None, Add(*expr_parts), is_piecewise)

    elif isinstance(expr, Pow) and expr.args[1] == -1.0 and len(expr.args) == 2:  # 1/A
        new_expr = _new_expr_parts(expr.args[0], V, U_offset, exp_function)
        vs, ve, sp, ex, has_piecewise = new_expr
        has_piecewise = has_piecewise or vs is not None
        new_expr = (None, None, None, 1.0 / _generate_piecewise(vs, ve, sp, ex, V), has_piecewise)

    elif isinstance(expr, Mul):
        (vs, ve, U, sp) = _get_U(expr, V, U_offset, exp_function)
        if vs is not None:
            new_expr = (vs, ve, sp, expr, True)
        else:
            expr_parts = []
            is_piecewise = False
            for sub_ex in expr.args:
                vs, ve, sp, ex, has_piecewise = _new_expr_parts(sub_ex, V, U_offset, exp_function)
                has_piecewise = is_piecewise = is_piecewise or has_piecewise or vs is not None
                expr_parts.append(_generate_piecewise(vs, ve, sp, ex, V))
            new_expr = (None, None, None, Mul(*expr_parts), is_piecewise)

    else:  # Different type of equation e.g a number
        return (None, None, None, expr, False)

    return new_expr


def _new_expr(expr, V, U_offset, exp_function):
    """Removes suitable singularities and replaces it with a piecewise.
    :param: expr the expression to analyse ().
    :param: V the volatge variable
    :param: U_offset determins the offset either side of U for which the fix is used
    :param: exp_function the function representing exp
    :param: optimize whether or not to apply optimisations to the new expression
    :return: expr with singularities fixes if appropriate
    """
    if not expr.has(exp_function):
        return False, expr
    (vs, ve, sp, ex, has_piecewise) = _new_expr_parts(expr, V, U_offset, exp_function)
    ex = _generate_piecewise(vs, ve, sp, ex, V)
    return has_piecewise or vs is not None, ex


def fix_singularities(equations, V, remove_unused_eqs=True, U_offset=1e-7, exp_function=exp_, optimize=True):
#    :param: U_offset determins the offset either side of U for which the fix is used (default 1e-7)
#    :param: exp_function: the function representing exp (default: exp_)
    unprocessed_eqs = {}
    for i, eq in enumerate(equations):
        if not isinstance(eq.rhs, Piecewise):
            unprocessed_eqs[eq.lhs] = eq.rhs.xreplace(unprocessed_eqs)
            changed, new_ex = _new_expr(unprocessed_eqs[eq.lhs], V, U_offset=1e-7, exp_function=exp_)
            if changed:
                equations[i] = Eq(eq.lhs, optimize_expr(new_ex) if optimize else new_ex)
                unprocessed_eqs.pop(eq.lhs)

