from sympy import (
    Abs,
    Function,
    acos,
    cos,
    exp,
    sign,
    sin,
    sqrt,
)


class RealFunction(Function):
    def _eval_is_real(self):
        return self.args[0].is_real


class exp_(RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return self


class abs_(RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return sign(self.args[0])


class acos_(RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return -1 / sqrt_(1 - self.args[0]**2)


class cos_(RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return -sin_(self.args[0])


class sqrt_(RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return 1 / (2 * sqrt_(self.args[0]))


class sin_(RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return (cos_(self.args[0]))


# MATH_FUNC_SYMPY_MAPPING provides a mapping from our specified math functions back to sympy versions.
# This can be used to put sympy function into an expression or evaluation. e.g. `expr.subs(MATH_FUNC_SYMPY_MAPPING)`.
MATH_FUNC_SYMPY_MAPPING = {abs_: Abs, acos_: acos, cos_: cos, exp_: exp, sin_: sin, sqrt_: sqrt}


def subs_math_func_placeholders(expr):
    """ Substitutes the placeholder math functions in expr for their corresponding Sympy functions
    :param expr: sympy expression

    Example:
    >> str(expr)
    '2.0 * exp_(V)'
    >> subs_math_func_placeholders(expr)
    '2.0 * exp(V)'

    :return: expr with all placeholder functions replaced by sympy functions.
    """
    for placeholder_func, sympy_func in MATH_FUNC_SYMPY_MAPPING.items():
        expr = expr.replace(placeholder_func, sympy_func)
    return expr
