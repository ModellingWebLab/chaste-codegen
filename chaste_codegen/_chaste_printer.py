from cellmlmanip.printer import Printer
from sympy import Mul
from sympy.printing.cxxcode import cxxcode
from sympy.printing.precedence import precedence


class ChastePrinter(Printer):
    """
    Converts Sympy expressions to strings for use in Chaste code generation.

    To use, create a :class:`ChastePrinter` instance, and call its method
    :meth:`doprint()` with a Sympy expression argument.

    Arguments:

    ``symbol_function``
        A function that converts symbols to strings (variable names).
    ``derivative_function``
        A function that converts derivatives to strings.

    """
    _function_names = {
        'abs_': 'fabs',
        'acos_': 'acos',
        'cos_': 'cos',
        'exp_': 'exp',
        'sqrt_': 'sqrt',
        'sin_': 'sin',

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
        'exp': 'exp',
        'expm1': 'expm1',
        'factorial': 'factorial',
        'floor': 'floor',
        'log': 'log',
        'log10': 'log10',
        'log1p': 'log1p',
        'log2': 'log2',
        'sin': 'sin',
        'sinh': 'sinh',
        'sqrt': 'sqrt',
        'tan': 'tan',
        'tanh': 'tanh',

        'sign': 'Signum',
        'GetIntracellularAreaStimulus': 'GetIntracellularAreaStimulus',
        'HeartConfig::Instance()->GetCapacitance': 'HeartConfig::Instance()->GetCapacitance',
        'GetExperimentalVoltageAtTimeT': 'GetExperimentalVoltageAtTimeT'
    }

    _literal_names = {
        'e': 'e',
        'nan': 'NAN',
        'pi': 'M_PI',
    }

    def __init__(self, symbol_function=None, derivative_function=None):
        super().__init__(symbol_function, derivative_function)

    def _print_Function(self, expr):
        """ Handles function calls. """

        # Check if function is known to python math
        name = expr.func.__name__
        # Convert arguments
        args = self._bracket_args(expr.args, 0)

        if name in self._function_names:
            name = self._function_names[name]
        else:
            raise ValueError('Unsupported function: ' + str(name))

        return name + '(' + args + ')'

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
        """ Handles Pow(), handles just ordinary powers without division.
        For C++ printing we need to write ``x**y`` as ``pow(x, y)`` with lowercase ``p``."""
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

    def _print_float(self, expr):
        """ Handles ``float``s. """
        return cxxcode(expr, standard='C++11')

    def _print_Mul(self, expr):
        # In multiplications remove 1.0 * ...
        if 1.0 in expr.args:
            expr = Mul(*[a for a in expr.args if a != 1.0])
        return super()._print_Mul(expr)
