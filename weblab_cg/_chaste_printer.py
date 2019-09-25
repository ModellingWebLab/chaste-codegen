from ._printer import WebLabPrinter, _math_functions
import sympy

from sympy.printing.precedence import precedence


class ChastePrinter(WebLabPrinter):
    """
    Converts Sympy expressions to strings for use in Chaste code generation, based on the WeblabPrinter.

    To use, create a :class:`ChastePrinter` instance, and call its method
    :meth:`doprint()` with a Sympy expression argument.

    Arguments:

    ``symbol_function``
        A function that converts symbols to strings (variable names).
    ``derivative_function``
        A function that converts derivatives to strings.

    """

    def __init__(self, symbol_function=None, derivative_function=None):
        super().__init__(symbol_function, derivative_function)

        # Do not use the math. prefix for functions, as chaste c++ files include an include for this
        self._prefix = ''

        # Make sure we can output a call to GetIntracellularAreaStimulus
        _math_functions.add('GetIntracellularAreaStimulus')

    def _print_Pow(self, expr):
        """ Handles Pow(), which includes all division
        only ordinary power is different, the rest is handed back up to the parent class (WebLabPrinter) """
        # Square root or ((only if communicative) 1/sqrt or ordinary devision )
        if expr.exp is sympy.S.Half or (expr.is_commutative and
                                        (-expr.exp is sympy.S.Half or -expr.exp is sympy.S.One)):
            return super()._print_Pow(expr)
        else:
            # Ordinary power
            p = precedence(expr)
            return 'pow(' + self._bracket(expr.base, p) + ', ' + self._bracket(expr.exp, p) + ')'
