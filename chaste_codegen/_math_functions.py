import sympy as sp


class _RealFunction(sp.Function):
    def _eval_is_real(self):
        return self.args[0].is_real


class _exp(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        if argindex == 1:
            return self
        else:
            raise sp.function.ArgumentIndexError(self, argindex)


class _abs(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        if argindex == 1:
            return sp.sign(self.args[0])
        else:
            raise sp.function.ArgumentIndexError(self, argindex)


class _acos(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        if argindex == 1:
            return -1 / _sqrt(1 - self.args[0]**2)
        else:
            raise sp.function.ArgumentIndexError(self, argindex)


class _cos(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        if argindex == 1:
            return -sp._sin(self.args[0])
        else:
            raise sp.function.ArgumentIndexError(self, argindex)


class _sqrt(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        if argindex == 1:
            return 1 / (2 * _sqrt(self.args[0]))
        else:
            raise sp.function.ArgumentIndexError(self, argindex)


class _sin(_RealFunction):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        if argindex == 1:
            return (_cos(self.args[0]))
        else:
            raise sp.function.ArgumentIndexError(self, argindex)

