from cellmlmanip.model import Variable
from sympy import (
    Derivative,
    Eq,
    Float,
    Piecewise,
    piecewise_fold,
)


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
        usage_count = {}
        for eq in equations:
            usage_count.setdefault(eq.lhs, 0)
            for var in eq.rhs.atoms(Variable):
                usage_count.setdefault(var, 0)
                usage_count[var] += 1
    # subs in all constants and expressions only used once
    subs_dict = {}
    for i, eq in enumerate(equations):
        new_rhs = eq.rhs.xreplace(subs_dict)
        # only apply piecewise_fold if needed to speed things up
        if len(eq.rhs.atoms(Piecewise)) > 0:
            new_rhs = piecewise_fold(new_rhs)
        new_eq = Eq(eq.lhs, new_rhs)
        if new_eq.lhs not in required_lhs and \
                (not keep_multiple_usages or isinstance(new_eq.rhs, Float) or usage_count[new_eq.lhs] <= 1):
            subs_dict[new_eq.lhs] = new_eq.rhs
        else:
            if not keep_multiple_usages:
                subs_dict[new_eq.lhs] = new_eq.rhs
            evaluated_eqs.append(new_eq)
    return evaluated_eqs
