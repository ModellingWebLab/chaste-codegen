from sympy import (
    Float,
    Pow,
    Wild,
    log,
)
from sympy.codegen.cfunctions import log10
from sympy.codegen.rewriting import ReplaceOptim, log1p_opt, optimize


# Optimisations to be applied to equations
_V, _W = Wild('V'), Wild('W')
# log(x)/log(10) --> log10(x)
_LOG10_OPT = ReplaceOptim(_V * log(_W) / log(10), _V * log10(_W), cost_function=lambda expr: expr.count(
    lambda e: (  # cost function prevents turning log(x) into log(10) * log10(x) as we want normal log in that case
        e.is_Pow and e.exp.is_negative  # division
        or (isinstance(e, (log, log10)) and not e.args[0].is_number))))
# For P^n make sure n is passed as int if it is actually a whole number
_POW_OPT = ReplaceOptim(lambda p: p.is_Pow and (isinstance(p.exp, Float) or isinstance(p.exp, float))
                        and float(p.exp).is_integer(),
                        lambda p: Pow(p.base, int(float(p.exp))))
_LOG_OPTIMS = (_LOG10_OPT, log1p_opt)


def optimize_expr_for_c_output(expr):
    """Returns expression optimised for c++ export with regards to powers and logarithms

    :param expr: the expression to apply power and log optimisations to.
    :return: The expression with the optimisations applied.
    """
    optims = tuple()
    if expr.has(log):
        optims += (_LOG_OPTIMS)
    if expr.has(Pow):
        optims += (_POW_OPT, )
    if len(optims) > 0:
        return optimize(expr, optims)
    return expr

