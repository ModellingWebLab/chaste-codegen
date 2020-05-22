import sympy as sp


class RealFunction(sp.Function):
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
        return sp.sign(self.args[0])


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
MATH_FUNC_SYMPY_MAPPING = {abs_: sp.Abs, acos_: sp.acos, cos_: sp.cos, exp_: sp.exp, sin_: sp.sin, sqrt_: sp.sqrt}
