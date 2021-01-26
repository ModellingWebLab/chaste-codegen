from cellmlmanip.model import Variable
from sympy import (
    Derivative,
    Eq,
    Float,
    Piecewise,
    cse,
    piecewise_fold,
)


def get_usage_count(equations):
    """Counts the amount of times the lhs for each eq is used on the rhs in the set of equations following it.
    :param: equations set of equations to check usage for.
           *Please note:* only counts usages of variables after they have been defined.
    :return: {var1: usage, var2: usage, ...}
    """
    usage_count = {}
    for eq in equations:
        usage_count.setdefault(eq.lhs, 0)
        for var in eq.rhs.atoms(Variable):
            usage_count.setdefault(var, 0)
            usage_count[var] += 1
    return usage_count


def fold_piecewises(expr):
    """Performs a piecewise_fold on the sympy expression, using a work-around to prevent errors with complex nesting.
    :param: expr the expression to piecewise_fold.
    :return: (equivalent to) piecewise_fold(expr)
    """
    # Since piecewise_fold hangs with some complicated nestings, due to simplification we use the following workaround:
    # First extract common terms, perform piecewise_fold, re-insert the common terms
    # see: https://github.com/sympy/sympy/issues/20850
    common_terms, expr = cse(expr)
    expr = piecewise_fold(expr[0])
    for term, ex in reversed(common_terms):
        expr = expr.xreplace({term: ex})
    return expr


def partial_eval(equations, required_lhs, keep_multiple_usages=True):
    """Partially evaluate the list of equations given.

    :param equations: the equations to partially evaluate
    :param required_lhs: variables which which the defining equation is kept and not substituted
    :param keep_multiple_usages: if a variable is used multiple times keep its defining equation
    :return: the equations wit defining equations substituted in to create a minimal set of equations
    """

    assert all(map(lambda eq: isinstance(eq, Eq), equations)), "Expecting equations to be a collection of equations"
    assert all(map(lambda v: isinstance(v, Variable) or isinstance(v, Derivative), required_lhs)), \
        "Expecting required_lhs to be a collection of variables or derivatives"

    evaluated_eqs = []
    # count usage of variables on rhs of equations
    if keep_multiple_usages:
        usage_count = get_usage_count(equations)

    # subs in all constants and expressions only used once
    subs_dict = {}
    for eq in equations:
        new_rhs = eq.rhs.xreplace(subs_dict)
        # only apply piecewise_fold if needed to speed things up
        if eq.rhs.has(Piecewise):
            new_rhs = fold_piecewises(new_rhs)
        if eq.lhs not in required_lhs and \
                (not keep_multiple_usages or isinstance(new_rhs, Float) or usage_count[eq.lhs] <= 1):
            subs_dict[eq.lhs] = new_rhs
        else:
            if not keep_multiple_usages:
                subs_dict[eq.lhs] = new_rhs
            evaluated_eqs.append(Eq(eq.lhs, new_rhs))

    return evaluated_eqs

