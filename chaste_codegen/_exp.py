import sympy as sp


class _exp(sp.Function):

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        if argindex == 1:
            return self
        else:
            raise sp.function.ArgumentIndexError(self, argindex)

    def _eval_is_real(self):
        return self.args[0].is_real
