import sympy as sp


class _RealFunction(sp.Function):
    def _eval_is_real(self):
        return self.args[0].is_real


class _exp(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return self


class _abs(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return sp.sign(self.args[0])


class _acos(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return -1 / _sqrt(1 - self.args[0]**2)


class _cos(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return -_sin(self.args[0])


class _sqrt(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return 1 / (2 * _sqrt(self.args[0]))


class _sin(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        assert argindex == 1
        return (_cos(self.args[0]))

