from math import isclose

import networkx as nx
from cellmlmanip.model import Quantity
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

from chaste_codegen._math_functions import exp_
from chaste_codegen._optimize import optimize_expr_for_c_output


_ONE = Quantity('1.0', 'dimensionless')  # Dummy representing 1.0


def _generate_piecewise(vs, ve, sp, ex, V):
    """Generates a piecewsie for expression ex based on the singularity point sp and vmin (vs) and vmax (ve) """
    def f(Vx, e):
        return e.xreplace({V: Vx})

    if vs is None:  # This shouldn't be apiecewise
        return ex

    return Piecewise(*[(f(vs, ex) + ((V - vs) / (ve - vs)) * (f(ve, ex) - f(vs, ex)),
                        Abs(V - sp) < Abs((ve - vs) / 2)), (ex, True)])


def _get_U(expr, V, U_offset, exp_function):
    W = Wild('Y', real=True)
    X = Wild('X', real=True, include=[V])
    Y = Wild('Y', real=True)
    Z = Wild('Z', real=True)

    def float_dummies(expr):
        if expr is None:
            return expr
        try:
            return expr.xreplace({Quantity(f, 'dimensionless') for f in expr.atoms(Float)})
        except AttributeError:
            return Quantity(str(expr), 'dimensionless')

    def check_bottom_match(m):
        return m is not None and X in m and Z in m and Z != 0

    def is_float(expr):
        try:
            float(str(expr))
            return True
        except ValueError:
            return False

    def check_top_match(m, sp):
        if m and Y in m:
            m[Y] = m[Y].xreplace({s: Float(str(s)) for s in m[Y].free_symbols if is_float(str(s))})
            sp = sp.xreplace({s: Float(str(s)) for s in sp.free_symbols if is_float(str(s))})
        return m is not None and Z in m and Z != 0 \
            and (sp == m[Y] or (isinstance(sp, Float) and isinstance(m[Y], Float) and isclose(m[Y], sp)))

    one_dict = {v: _ONE for v in expr.free_symbols if str(v) in ('1.0', '1')}
    one_dict.update({v: - _ONE for v in expr.free_symbols if str(v) in ('-1.0', '1')})
    expr = expr.xreplace(one_dict)

    (vs, ve, sp) = None, None, None
    # the denominator is all args where a **-1
    numerator = set(a for a in expr.args if not isinstance(a, Pow) or a.args[1] != -1.0)
    denominator = set(a.args[0] for a in expr.args if isinstance(a, Pow) and a.args[1] == -1.0)

    if len(denominator) > 0 and len(numerator) > 0:
        # U might be on top, try numerator / denominator and denominator / numerator
        for denom, num in ((denominator, numerator), (numerator, denominator)):
            found_on_top = False
            for d in denom:
                if d.has(exp_function):
                    find_U = d.match(exp_function(X) * -Z + _ONE)
                    if not check_bottom_match(find_U):
                        find_U = d.match(exp_function(X) * Z - _ONE)
                    if not check_bottom_match(find_U):
                        find_U = d.match(exp_function(X) * -Z + W)
                        if find_U and Y in find_U and find_U[W] != _ONE:
                            find_U = None
                    if not check_bottom_match(find_U):
                        find_U = d.match(exp_function(X) * Z - W)
                        if find_U and Y in find_U and find_U[W] != _ONE:
                            find_U = None

                    if check_bottom_match(find_U):
                        u = (find_U[X] + log(find_U[Z]))
                        # We need to replace dummies by numbers to be able to find th singularity point
                        u = u.xreplace({s: float(str(s)) for s in u.free_symbols if is_float(str(s))})
                        try:
                            sp = tuple(filter(lambda s: not s.has(I), solveset(u, V)))
                            if sp:
                                find_v_low = solveset(u + U_offset, V)
                                find_v_up = solveset(u - U_offset, V)
                                find_v_low = tuple(find_v_low)
                                find_v_up = tuple(find_v_up)
                                if find_v_low and find_v_up:
                                    assert len(find_v_low) == len(find_v_up) == len(sp) == 1, \
                                        'Expecting exactly 1 solution for singularity point'
                                    (vs, ve, sp) = (find_v_low[0], find_v_up[0], sp[0])
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
            if vs is not None and found_on_top:  # found U, no need to try further
                break
            else:
                (vs, ve, sp) = None, None, None

    # Put dummies back in and return the singularity point and range bundries
    return (float_dummies(vs), float_dummies(ve), float_dummies(sp))


def _new_expr_parts(expr, V, U_offset, exp_function):
    """Removes suitable singularities and replaces it with a piecewise, returning (vs, ve, sp, has_singularity)"""
    if not expr.has(exp_function):
        return (None, None, None, expr, False)

    if isinstance(expr, Mul):  # 1 * A --> A (remove unneeded 1 *)
        expr = Mul(*[a for a in expr.args if not a == _ONE])

    if isinstance(expr, Add):  # A + B + ..
        # The expression is an addition, find singularities in each argument
        new_expr_parts = []
        for a in expr.args:
            new_expr_parts.append(_new_expr_parts(a, V, U_offset, exp_function))

        # If all arguments have the same singularity point, return 1 singularity with the widest range
        range = [item for (vs, ve, _, _, _) in new_expr_parts for item in (vs, ve)]
        if len(new_expr_parts) > 1 and len(set([sp for (_, _, sp, _, _) in new_expr_parts])) == 1 \
                and all(isinstance(b, Quantity) for b in range):
            sp = new_expr_parts[0][2]
            vs, ve = min(range), max(range)
            new_expr = (vs, ve, sp, expr, True)
        else:  # Singularity points differ, so create each piecewise seperately and add them up
            expr_parts = []
            is_piecewise = False
            for vs, ve, sp, ex, has_piecewise in new_expr_parts:
                is_piecewise = is_piecewise or has_piecewise or vs is not None
                expr_parts.append(_generate_piecewise(vs, ve, sp, ex, V))
            new_expr = (None, None, None, Add(*expr_parts), is_piecewise)

    elif isinstance(expr, Pow) and expr.args[1] == -1.0 and len(expr.args) == 2:  # 1/A
        # Find singularities in A and adjust result to represent 1 / A
        new_expr = _new_expr_parts(expr.args[0], V, U_offset, exp_function)
        vs, ve, sp, ex, has_piecewise = new_expr
        has_piecewise = has_piecewise or vs is not None
        new_expr = (None, None, None, 1.0 / _generate_piecewise(vs, ve, sp, ex, V), has_piecewise)

    elif isinstance(expr, Mul):  # A * B * ...
        (vs, ve, sp) = _get_U(expr, V, U_offset, exp_function)
        if vs is not None:
            new_expr = (vs, ve, sp, expr, True)
        else:  # Couldn't find singularity, try the expression's arguments
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


def new_expr(expr, V, U_offset, exp_function):
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


def fix_singularity_equations(model, V, modifiable_parameters, U_offset=1e-7, exp_function=exp_, optimize=True):
    """Finds singularities in the GHK equations in the model and replaces them with a piecewise.
    :param: the cellmlmanip model the model to analyse.
    :param: V the volatge variable
    :param: modifiable_parameters the variables which are modifiable in the model,
            their defining equations are excluded form the analysis
    :param: U_offset determins the offset either side of U for which the fix is used
    :param: exp_function the function representing exp
    :param: optimize whether or not to apply optimisations to the new expression
    """
    unprocessed_eqs = {}
    # iterate over sorted variables in the model
    for variable in nx.lexicographical_topological_sort(model.graph, key=str):

        # Get equation
        eq = model.graph.nodes[variable]['equation']

        # Skip variables that have no equation or equations defining parameters or where rhs is a Piecewise
        if eq is not None and not isinstance(eq.rhs, Piecewise) and eq.lhs not in modifiable_parameters:
            unprocessed_eqs[eq.lhs] = eq.rhs.xreplace(unprocessed_eqs)  # store partially evaluated version of the rhs
            # evaluate singularities
            changed, new_ex = new_expr(unprocessed_eqs[eq.lhs], V, U_offset=U_offset, exp_function=exp_function)
            if changed:  # update equation if the rhs has a singularity that can be fixed
                model.remove_equation(eq)
                model.add_equation(Eq(eq.lhs, optimize_expr_for_c_output(new_ex) if optimize else new_ex))
                unprocessed_eqs.pop(eq.lhs)
