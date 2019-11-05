#
# Methods to convert sympy expressions to Cython code.
#
# Should work with SymPy 1.1.1, but also later versions.
#
# ----------------------------------------------------------------------------
#
# Parts of this code were adapted from:
#
#  https://github.com/sympy/sympy/blob/master/sympy/printing/printer.py
#  https://github.com/sympy/sympy/blob/master/sympy/printing/str.py
#
# Which came with the following license:
#
# Copyright (c) 2006-2018 SymPy Development Team
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   a. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   b. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#   c. Neither the name of SymPy nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
import sympy
import sympy.printing

from sympy.printing.precedence import precedence


class WebLabPrinter(sympy.printing.printer.Printer):
    """
    Converts Sympy expressions to strings for use in Web Lab Cython model code.

    To use, create a :class:`WebLabPrinter` instance, and call its method
    :meth:`doprint()` with a Sympy expression argument.

    Arguments:

    ``symbol_function``
        A function that converts symbols to strings (variable names).
    ``derivative_function``
        A function that converts derivatives to strings.

    """
    # List of functions handled by python's `math` module
    _math_functions = {
        'acos',
        'acosh',
        'asin',
        'asinh',
        'atan',
        'atan2',
        'atanh',
        'ceil',     # called ceiling in sympy
        'cos',
        'cosh',
        'exp',
        'expm1',
        'factorial',
        'floor',
        'log',
        'log10',
        'log1p',
        'log2',
        'sin',
        'sinh',
        'tan',
        'tanh',
    }

    def __init__(self, symbol_function=None, derivative_function=None):
        super(WebLabPrinter, self).__init__(None)

        # Prefix for functions
        self._prefix = 'math.'

        # Symbol and derivative handling (default)
        if symbol_function is None:
            self._symbol_function = lambda x: str(x)
        else:
            self._symbol_function = symbol_function

        if derivative_function is None:
            self._derivative_function = lambda x: str(x)
        else:
            self._derivative_function = derivative_function

    def _bracket(self, expr, parent_precedence):
        """
        Converts ``expr`` to string, and adds parentheses around the result, if
        and only if ``precedence(expr) < parent_precedence``.
        """
        if precedence(expr) < parent_precedence:
            return '(' + self._print(expr) + ')'
        return self._print(expr)

    def _bracket_args(self, args, parent_precedence):
        """
        Applies :meth:`_bracket()` to a list of expressions, and joins them
        with a comma.
        """
        return ', '.join([self._bracket(x, parent_precedence) for x in args])

    def emptyPrinter(self, expr):
        """
        Called by :class:`Printer` as a last resort for unknown expressions.
        """
        raise ValueError(
            'Unsupported expression type (' + str(type(expr)) + '): '
            + str(expr))

    def _print_Add(self, expr):
        """ Handles addition & subtraction, with n terms. """
        # This method is based on sympy.printing.Str

        parts = []
        my_prec = precedence(expr)
        for term in expr.args:
            # Don't use _bracket() here because we want to check the sign
            t = self._print(term)

            # Add sign
            s = '+'
            if t.startswith('-'):
                s = '-'
                t = t[1:]
            parts.append(s)

            # Add remaining term
            parts.append('(' + t + ')' if precedence(term) < my_prec else t)

        # Concatenate and return
        if parts[0] == '+':
            # Ignore leading plus
            return ' '.join(parts[1:])
        else:
            # No space after first minus
            return parts[0] + ' '.join(parts[1:])

    def _print_And(self, expr):
        """ Handles logical And. """
        my_prec = precedence(expr)
        return ' and '.join([self._bracket(x, my_prec) for x in expr.args])

    def _print_bool(self, expr):
        """ Handles False """
        if expr:
            return self._print_BooleanTrue(expr)
        else:
            return self._print_BooleanFalse(expr)

    def _print_BooleanFalse(self, expr):
        """ Handles False """
        return 'False'

    def _print_BooleanTrue(self, expr):
        """ Handles True """
        return 'True'

    def _print_Derivative(self, expr):
        """ Handles Derivative objects. """
        return self._derivative_function(expr)

    def _print_Exp1(self, expr):
        """ Handles the sympy E object """
        return self._prefix + 'e'

    def _print_float(self, expr):
        """ Handles Python floats """
        return str(expr)
        # Print short format if it doesn't change the value, else long format
        # short = str(expr)
        # if float(short) == expr:
        #    return short
        # return '{: .17e}'.format(expr)

    def _print_Float(self, expr):
        """ Handles Sympy Float objects """
        return self._print_float(float(expr))

    def _print_Function(self, expr):
        """ Handles function calls. """

        # Check if function is known to python math
        name = expr.func.__name__
        if name == 'ceiling':
            name = 'ceil'
        if name not in WebLabPrinter._math_functions:
            raise ValueError('Unsupported function: ' + str(name))

        # Convert arguments and return
        args = self._bracket_args(expr.args, 0)
        return self._prefix + name + '(' + args + ')'

    # def _print_Infinity(self, expr):
    #    return 'float(\'inf\')'

    def _print_int(self, expr):
        """ Handles python ints """
        return str(expr)

    def _print_Integer(self, expr):
        """
        Handles Sympy Integer objects, including special ones like Zero, One,
        and NegativeOne.
        """
        return str(expr.p)

    def _print_Mul(self, expr):
        """
        Handles multiplication & division, with n terms.

        Division is specified as a power: ``x / y --> x * y**-1``.
        Subtraction is specified as ``x - y --> x + (-1 * y)``.
        """
        # This method is mostly copied from sympy.printing.Str

        # Check overall sign of multiplication
        from sympy.core.mul import _keep_coeff
        sign = ''
        c, e = expr.as_coeff_Mul()
        if c < 0:
            expr = _keep_coeff(-c, e)
            sign = '-'

        # Collect all pows with more than one base element and exp = -1
        pow_brackets = []

        # Gather terms for numerator and denominator
        a, b = [], []
        for item in sympy.Mul.make_args(expr):

            # Check if this is a negative power that we can write as a division
            negative_power = (
                item.is_commutative and item.is_Pow
                and item.exp.is_Rational and item.exp.is_negative)
            if negative_power:
                if item.exp != -1:
                    # E.g. x * y**(-2 / 3) --> x / y**(2 / 3)
                    # Add as power
                    b.append(sympy.Pow(item.base, -item.exp, evaluate=False))
                else:
                    # Add without power
                    b.append(sympy.Pow(item.base, -item.exp))

                    # Check if it's a negative power that needs brackets
                    # Sympy issue #14160
                    if (len(item.args[0].args) != 1
                            and isinstance(item.base, sympy.Mul)):
                        pow_brackets.append(item)

            # Split Rationals over a and b, ignoring any 1s
            elif item.is_Rational:
                if item.p != 1:
                    a.append(sympy.Rational(item.p))
                if item.q != 1:
                    b.append(sympy.Rational(item.q))

            else:
                a.append(item)

        # Replace empty numerator with one
        a = a or [sympy.S.One]

        # Convert terms to code
        my_prec = precedence(expr)
        a_str = [self._bracket(x, my_prec) for x in a]
        b_str = [self._bracket(x, my_prec) for x in b]

        # Fix brackets for Pow with exp -1 with more than one Symbol
        for item in pow_brackets:
            if item.base in b:
                b_str[b.index(item.base)] = \
                    '(' + b_str[b.index(item.base)] + ')'

        # Combine numerator and denomenator and return
        a_str = sign + ' * '.join(a_str)
        if len(b) == 0:
            return a_str
        b_str = ' * '.join(b_str)
        return a_str + ' / ' + (b_str if len(b) == 1 else '(' + b_str + ')')

    # def _print_NaN(self, expr):
    #    return 'float(\'nan\')'

    # def _print_NegativeInfinity(self, expr):
    #    return 'float(\'-inf\')'

    def _print_Or(self, expr):
        """ Handles logical Or. """
        my_prec = precedence(expr)
        return ' or '.join([self._bracket(x, my_prec) for x in expr.args])

    def _print_Pi(self, expr):
        """ Handles pi """
        return self._prefix + 'pi'

    def _print_Piecewise(self, expr):
        """
        Handles Piecewise functions.

        Sympy's piecewise is defined as a list of tuples ``(expr, cond)`` and
        evaluated by returning the first ``expr`` whose ``cond`` is true. If
        none of the conditions hold a value error is raised.
        """
        from sympy.logic.boolalg import BooleanTrue

        # Assign NaN if no conditions hold
        # If a condition `True` is found, use its expression instead
        other = 'float(\'nan\')'

        parts = ['(']
        brackets = 1
        for e, c in expr.args:
            # Check if boolean True (if found, stop evaluating further)
            if isinstance(c, BooleanTrue):
                other = self._print(e)
                break
            # Sympy filters these out:
            # elif isinstance(c, BooleanFalse):
            #    continue

            # Add e-if-c-else-? statement
            parts.append('(')
            parts.append(self._print(e))
            parts.append(') if (')
            parts.append(self._print(c))
            parts.append(') else (')
            brackets += 1
        parts.append(other)
        parts.append(')' * brackets)
        return ''.join(parts)

    def _print_Pow(self, expr):
        """ Handles Pow(), which includes all division """
        p = precedence(expr)

        # Handle square root
        if expr.exp is sympy.S.Half:
            return self._prefix + 'sqrt(' + self._print(expr.base) + ')'

        # Division, only if commutative (following sympy implementation)
        if expr.is_commutative:
            # 1 / sqrt()
            if -expr.exp is sympy.S.Half:
                return (
                    '1 / ' + self._prefix
                    + 'sqrt(' + self._print(expr.base) + ')')

            # Ordinary division
            if -expr.exp is sympy.S.One:
                return '1 / ' + self._bracket(expr.base, p)

        # Ordinary power
        return self._bracket(expr.base, p) + '**' + self._bracket(expr.exp, p)

    def _print_Rational(self, expr):
        """ Handles rationals (int divisions, stored symbollicaly) """
        return str(expr.p) + ' / ' + str(expr.q)

    def _print_Relational(self, expr):
        """ Handles equality and inequalities. """

        op = expr.rel_op
        ops = {'==', '!=', '<', '<=', '>', '>='}
        if op not in ops:   # pragma: no cover
            raise ValueError('Unsupported relational: "' + str(op) + '".')

        # Note: Nested relationals (x == (y == z)) should get brackets, so
        # using slightly increased parent precedence here
        my_prec = precedence(expr) + 1
        lhs = self._bracket(expr.lhs, my_prec)
        rhs = self._bracket(expr.rhs, my_prec)
        return lhs + ' ' + op + ' ' + rhs

    def _print_Symbol(self, expr):
        """ Handles sympy Symbol objects """
        return self._symbol_function(expr)

