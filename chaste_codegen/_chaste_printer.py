from cellmlmanip.printer import Printer
from sympy import (
    Mul,
    Not,
    Piecewise,
    Pow,
    Rational,
    S,
)
from sympy.core.mul import _keep_coeff
from sympy.printing import cxxcode
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
    ``lookup_table_function``
        A function that prints lookup table expressions or returns None if the expression is not in the lookup table.

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
    _extra_trig_names = {
        'sec': 'cos',
        'csc': 'sin',
        'cot': 'tan',
        'sech': 'cosh',
        'csch': 'sinh',
        'coth': 'tanh',
    }
    _extra_inverse_trig_names = {
        'asec': 'acos',
        'acsc': 'asin',
        'acot': 'atan',
        'asech': 'acosh',
        'acsch': 'asinh',
        'acoth': 'atanh',
    }

    _literal_names = {
        'e': 'e',
        'nan': 'NAN',
        'pi': 'M_PI',
    }

    def __init__(self, symbol_function=None, derivative_function=None, lookup_table_function=lambda e: None):
        super().__init__(symbol_function, derivative_function)
        self.lookup_table_function = lookup_table_function

    def _print(self, expr, **kwargs):
        """Internal dispatcher.

        Here we intercept lookup table expressions if we have lookup tables.
        Otherwise the base class method is used.
        """
        printed_expr = self.lookup_table_function(expr)
        if printed_expr:
            return printed_expr
        return super()._print(expr, **kwargs)

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
        if expr.exp == 0.5:
            return 'sqrt(' + self._bracket(expr.base, p) + ')'
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

    def _print_ITE(self, expr):
        """ Handles ITE (if then else) objects by rewriting them as Piecewise """
        return self._print_Piecewise(expr.rewrite(Piecewise))

    def _print_Mul(self, expr):
        """
        Handles multiplication & division, with n terms.

        Division is specified as a power: ``x / y --> x * y**-1``.
        Subtraction is specified as ``x - y --> x + (-1 * y)``.
        """
        # This method is mostly copied from sympy.printing.Str

        # Check overall sign of multiplication
        sign = ''
        c, e = expr.as_coeff_Mul()
        if c < 0:
            expr = _keep_coeff(-c, e)
            sign = '-'

        # Collect all pows with more than one base element and exp = -1
        pow_brackets = []

        # Gather terms for numerator and denominator
        a, b = [], []
        for item in Mul.make_args(expr):
            if item != 1.0:  # In multiplications remove 1.0 * ...
                # Check if this is a negative power and it's not in a lookup table, so we can write it as a division
                if (item.is_commutative and item.is_Pow and item.exp.is_Rational and item.exp.is_negative
                        and not self.lookup_table_function(item)):
                    if item.exp != -1:
                        # E.g. x * y**(-2 / 3) --> x / y**(2 / 3)
                        # Add as power
                        b.append(Pow(item.base, -item.exp, evaluate=False))
                    else:
                        # Add without power
                        b.append(Pow(item.base, -item.exp))

                        # Check if it's a negative power that needs brackets
                        # Sympy issue #14160
                        if (len(item.args[0].args) != 1 and isinstance(item.base, Mul)):
                            pow_brackets.append(item)

                # Split Rationals over a and b, ignoring any 1s
                elif item.is_Rational:
                    if item.p != 1:
                        a.append(Rational(item.p))
                    if item.q != 1:
                        b.append(Rational(item.q))

                else:
                    a.append(item)

        # Replace empty numerator with one
        a = a or [S.One]

        # Convert terms to code
        my_prec = precedence(expr)
        a_str = [self._bracket(x, my_prec) for x in a]
        b_str = [self._bracket(x, my_prec) for x in b]

        # Fix brackets for Pow with exp -1 with more than one Symbol
        for item in pow_brackets:
            assert item.base in b, "item.base should be kept in b for powers"
            b_str[b.index(item.base)] = '(' + b_str[b.index(item.base)] + ')'

        # Combine numerator and denomenator and return
        a_str = sign + ' * '.join(a_str)
        if len(b) == 0:
            return a_str
        b_str = ' * '.join(b_str)
        return a_str + ' / ' + (b_str if len(b) == 1 else '(' + b_str + ')')

    def _print_Not(self, expr):
        return '!(' + self._print(Not(expr)) + ')'
