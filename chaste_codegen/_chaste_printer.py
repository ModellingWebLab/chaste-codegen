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


C_MAX_INT = 2147483647
C_MIN_INT = -2147483647


class ChastePrinter(Printer):
    """
    Converts Sympy expressions to strings for use in Chaste code generation.


    Expressions are generated in terms of the CHASTE_MATH name space, it is then the job
    of the Jinja template to ensure CHASTE_MATH points to the correct C++ namespace
    using the appropriate #include. E.g., #include "ChasteCpuMacros.hpp" converts these
    namespaced calls to std library calls


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
        'abs_': 'CHASTE_MATH::Abs',
        'acos_': 'CHASTE_MATH::Acos',
        'cos_': 'CHASTE_MATH::Cos',
        'exp_': 'CHASTE_MATH::Exp',
        'sqrt_': 'CHASTE_MATH::Sqrt',
        'sin_': 'CHASTE_MATH::Sin',

        'Abs': 'CHASTE_MATH::Abs',
        'acos': 'CHASTE_MATH::Acos',
        'acosh': 'CHASTE_MATH::Acosh',
        'asin': 'CHASTE_MATH::Asin',
        'asinh': 'CHASTE_MATH::Asinh',
        'atan': 'CHASTE_MATH::Atan',
        'atan2': 'CHASTE_MATH::Atan2',
        'atanh': 'CHASTE_MATH::Atanh',
        'ceiling': 'CHASTE_MATH::Ceil',
        'cos': 'CHASTE_MATH::Cos',
        'cosh': 'CHASTE_MATH::Cosh',
        'exp': 'CHASTE_MATH::Exp',
        'expm1': 'CHASTE_MATH::Expm1',
        'factorial': 'CHASTE_MATH::Factorial',
        'floor': 'CHASTE_MATH::Floor',
        'log': 'CHASTE_MATH::Log',
        'log10': 'CHASTE_MATH::Log10',
        'log1p': 'CHASTE_MATH::Log1p',
        'log2': 'CHASTE_MATH::Log2',
        'sin': 'CHASTE_MATH::Sin',
        'sinh': 'CHASTE_MATH::Sinh',
        'sqrt': 'CHASTE_MATH::Sqrt',
        'tan': 'CHASTE_MATH::Tan',
        'tanh': 'CHASTE_MATH::Tanh',

        'sign': 'CHASTE_MATH::Sign',
        
        'GetIntracellularAreaStimulus': 'CHASTE_STIM',
        'HeartConfig::Instance()->GetCapacitance': 'CHASTE_CAP',
        'GetExperimentalVoltageAtTimeT': 'CHASTE_EXP_VOLT'
    }

    _extra_trig_names = {
        'sec': 'CHASTE_MATH::Sec',
        'csc': 'CHASTE_MATH::Csc',
        'cot': 'CHASTE_MATH::Cot',
        'sech': 'CHASTE_MATH::Sech',
        'csch': 'CHASTE_MATH::Csch',
        'coth': 'CHASTE_MATH::Coth',
    }

    _extra_inverse_trig_names = {
        'asec': 'CHASTE_MATH::Asec',
        'acsc': 'CHASTE_MATH::Acsc',
        'acot': 'CHASTE_MATH::Acot',
        'asech': 'CHASTE_MATH::Asech',
        'acsch': 'CHASTE_MATH::Acsch',
        'acoth': 'CHASTE_MATH::Acoth',
    }

    _literal_names = {
        'e': 'CHASTE_MATH::E',
        'nan': 'CHASTE_MATH::NaN',
        'pi': 'CHASTE_MATH::Pi',
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
        """ Handles Pow(), handles just ordinary powers without division."""
        p = precedence(expr)
        if expr.exp == 0.5:
            return 'CHASTE_MATH::Sqrt(' + self._bracket(expr.base, p) + ')'
        return 'CHASTE_MATH::Pow(' + self._bracket(expr.base, p) + ', ' + self._bracket(expr.exp, p) + ')'

    def _print_ternary(self, cond, expr):
        parts = ''
        parts += '('
        parts += self._print(cond)
        parts += ') ? ('
        parts += self._print(expr)
        parts += ') : ('
        return parts

    def _print_IntegerConstant(self, expr):
        return self._print_int(float(expr))

    def _print_float(self, expr):
        """
        Handles ``float``s. All constants must be wrapped with a macro so that
        generated code that ends up in a device kernel can easily be cast between 
        float and double as this has huge performance implications on device
        """
        # print integers as int if they are between min & max int in c++
        if expr.is_integer() and C_MIN_INT < expr < C_MAX_INT:
            return cxxcode(int(expr), standard='C++11')
        else:
            num_str = cxxcode(float(expr), standard='C++11')
            return f'CHASTE_CONST({num_str})'

    def _print_int(self, expr):
        """ Handles ``ints``s. """
        return self._print_float(float(expr))

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
