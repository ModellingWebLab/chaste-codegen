from ._printer import Printer
from sympy.printing.precedence import precedence


class ChastePrinter(Printer):
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
    _function_names = {
        'Abs': 'fabs',
        'acos': 'acos',
        'acosh': 'acosh',
        'asin': 'asin',
        'asinh': 'asinh',
        'atan': 'atan',
        'atan2': 'atan2',
        'atanh': 'atanh',
        'ceiling': 'ceil',
        'cos': 'cos',
        'cosh': 'cosh',
        'sqrt': 'sqrt',
        'e': 'e',
        'exp': 'exp',
        'expm1': 'expm1',
        'factorial': 'factorial',
        'floor': 'floor',
        'log': 'log',
        'log10': 'log10',
        'log1p': 'log1p',
        'log2': 'log2',
        'nan': 'NAN',
        'pi': 'M_PI',
        'sin': 'sin',
        'sinh': 'sinh',
        'sqrt': 'sqrt',
        'tan': 'tan',
        'tanh': 'tanh',

        'GetIntracellularAreaStimulus': 'GetIntracellularAreaStimulus',
        'HeartConfig::Instance()->GetCapacitance': 'HeartConfig::Instance()->GetCapacitance'
    }

    def __init__(self, symbol_function=None, derivative_function=None):
        super().__init__(symbol_function, derivative_function)

    def _print_And(self, expr):
        """ Handles logical And. """
        my_prec = precedence(expr)
        return ' && '.join(['(' + self._bracket(x, my_prec) + ')' for x in expr.args])

    def _print_BooleanFalse(self, expr):
        """ Handles False """
        return 'false'

    def _print_BooleanTrue(self, expr):
        """ Handles True """
        return 'true'

    def _print_Or(self, expr):
        """ Handles logical Or. """
        my_prec = precedence(expr)
        return ' || '.join(['(' + self._bracket(x, my_prec) + ')' for x in expr.args])

    def _print_ordinary_pow(self, expr):
        """ Handles Pow(), hanles just ordinary powers without division "

        for C++ printing we need to writea x**y as pow(x, y) with lowercase p"""
        p = precedence(expr)
        return 'pow(' + self._bracket(expr.base, p) + ', ' + self._bracket(expr.exp, p) + ')'

    def _print_ternary(self, cond, expr):
        parts = ''
        parts += '('
        parts += self._print(cond)
        parts += ') ? ('
        parts += self._print(expr)
        parts += ') : ('
        return parts
