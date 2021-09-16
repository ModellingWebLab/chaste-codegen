#
#
# Tests conversion of sympy expressions to C++ code for Chaste code generation.
#
import logging
import math

import pytest
import sympy as sp

import chaste_codegen as cg
from chaste_codegen import (
    abs_,
    acos_,
    cos_,
    exp_,
    sin_,
    sqrt_,
)


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


class TestChastePrinter(object):

    @pytest.fixture(scope="class")
    def printer(self):
        return cg.LabviewPrinter()

    @pytest.fixture(scope="class")
    def x(self):
        return sp.symbols('x')

    @pytest.fixture(scope="class")
    def y(self):
        return sp.symbols('y')

    @pytest.fixture(scope="class")
    def z(self):
        return sp.symbols('z')

    def test_not(self, printer, x, y, z):
        assert printer.doprint(sp.Not(x)) == '~(x)'
        assert printer.doprint(sp.Not(sp.Eq(x, y))) == 'x ~= y'
        assert printer.doprint(sp.Not(sp.Eq(x, y) | sp.Eq(x, z))) == '~((x == y) || (x == z))'

    def test_and(self, printer, x, y):
        assert printer.doprint(sp.sympify('x & y')) == '(x) && (y)'

    def test_booleans(self, printer, x):
        assert printer.doprint(sp.Eq(x, x)) == printer.doprint(True) == 'true'
        assert printer.doprint(sp.Ne(x, x)) == printer.doprint(False) == 'false'

    def test_or(self, printer, x, y, z):
        assert printer.doprint(sp.Or(sp.Eq(x, y), sp.Eq(x, z))) \
            == printer.doprint(sp.Eq(x, y) | sp.Eq(x, z)) == '(x == y) || (x == z)'

    def test_pow(self, printer, x, y):
        assert printer.doprint(sp.sympify('x ** y')) == 'pow(x, y)'
        assert printer.doprint(sp.sympify('Pow(x,y)')) == 'pow(x, y)'
        assert printer.doprint(sp.sympify('x ** (1/2)')) == 'sqrt(x)'
        assert printer.doprint(sp.sympify('x ** (-1/2)')) == '1 / sqrt(x)'
        assert printer.doprint(1 / x) == '1 / x'

    def test_piecewise_expressions(self, printer, x, y, z):
        # Piecewise expressions
        conditionalexp_r = sp.Piecewise((0, x > 0), (1, True))
        assert printer.doprint(conditionalexp_r) == '((x > 0) ? (0) : (1))'
        conditionalexp_r = sp.Piecewise((0, x > 0), (1, x > 1), (2, True))
        assert printer.doprint(conditionalexp_r) == '((x > 0) ? (0) : ((x > 1) ? (1) : (2)))'

    def testabs_(self, printer, x, y):
        assert printer.doprint(sp.Abs(x + y)) == 'abs(x + y)'
        assert printer.doprint(sp.Abs(sp.Float('3.2', 17), evaluate=False)) == 'abs(3.2000000000000002)'
        assert printer.doprint(sp.Abs(-3, evaluate=False)) == 'abs(-3)'

    def test_trig_functions(self, printer, x):
        # Trig functions
        assert printer.doprint(sp.acos(x)) == 'acos(x)'
        assert printer.doprint(sp.acosh(x)) == 'acosh(x)'
        assert printer.doprint(sp.asin(x)) == 'asin(x)'
        assert printer.doprint(sp.asinh(x)) == 'asinh(x)'
        assert printer.doprint(sp.atan(x)) == 'atan(x)'
        assert printer.doprint(sp.atanh(x)) == 'atanh(x)'
        assert printer.doprint(sp.ceiling(x)) == 'ceil(x)'
        assert printer.doprint(sp.cos(x)) == 'cos(x)'
        assert printer.doprint(sp.cosh(x)) == 'cosh(x)'
        assert printer.doprint(sp.exp(x)) == 'exp(x)'
        assert printer.doprint(sp.factorial(x)) == 'factorial(x)'
        assert printer.doprint(sp.floor(x)) == 'floor(x)'
        assert printer.doprint(sp.log(x)) == 'log(x)'
        assert printer.doprint(sp.sin(x)) == 'sin(x)'
        assert printer.doprint(sp.sinh(x)) == 'sinh(x)'
        assert printer.doprint(sp.tan(x)) == 'tan(x)'
        assert printer.doprint(sp.tanh(x)) == 'tanh(x)'

        # extra trig functions
        assert printer.doprint(sp.sec(x)) == '1 / cos(x)'
        assert printer.doprint(sp.csc(x)) == '1 / sin(x)'
        assert printer.doprint(sp.cot(x)) == '1 / tan(x)'
        assert printer.doprint(sp.asec(x)) == 'acos(1 / x)'
        assert printer.doprint(sp.acsc(x)) == 'asin(1 / x)'
        assert printer.doprint(sp.acot(x)) == 'atan(1 / x)'
        assert printer.doprint(sp.sech(x)) == '1 / cosh(x)'
        assert printer.doprint(sp.csch(x)) == '1 / sinh(x)'
        assert printer.doprint(sp.coth(x)) == '1 / tanh(x)'
        assert printer.doprint(sp.asech(x)) == 'acosh(1 / x)'
        assert printer.doprint(sp.acsch(x)) == 'asinh(1 / x)'
        assert printer.doprint(sp.acoth(x)) == 'atanh(1 / x)'

    def test_custom_math_functions(self, printer, x):
        assert printer.doprint(acos_(x)) == 'acos(x)'
        assert printer.doprint(cos_(x)) == 'cos(x)'
        assert printer.doprint(exp_(x)) == 'exp(x)'
        assert printer.doprint(sin_(x)) == 'sin(x)'
        assert printer.doprint(sqrt_(x)) == 'sqrt(x)'
        assert printer.doprint(abs_(x)) == 'abs(x)'

    def test_numbers(self, printer, x):
        # Number types
        assert printer.doprint(1) == '1'                  # int
        assert printer.doprint(1.2) == '1.2'              # float, short format
        assert printer.doprint(math.pi) == '3.1415926535897931'  # float, long format
        assert printer.doprint(1.436432635636e-123) == '1.436432635636e-123'
        assert printer.doprint(x - x) == '0'              # Zero
        assert printer.doprint(x / x) == '1'              # One
        assert printer.doprint(-x / x) == '-1'            # Negative one
        assert printer.doprint(5 * (x / x)) == '5'        # Sympy integer
        assert printer.doprint(5.5 * (x / x)) == '5.5'        # Sympy float
        assert printer.doprint(sp.Rational(5, 7)) == '5 / 7'  # Sympy rational

        # Special numbers
        assert printer.doprint(sp.pi) == 'pi'
        assert printer.doprint(sp.E) == 'exp(1)'

    def test_unsupported_function(self, printer, x):
        f = sp.Function('f')
        with pytest.raises(ValueError) as err:
            printer.doprint(f(1))
        assert str(err.value) == 'Unsupported function: f'

    def test_multiplication(self, printer, x, y, z):

        # Multiplication and division
        assert printer.doprint(x * y) == 'x * y'
        assert printer.doprint(x * y * z) == 'x * y * z'
        assert printer.doprint(x / y) == 'x / y'
        assert printer.doprint(2 * z) == '2 * z'
        assert printer.doprint(z * 5) == '5 * z'
        assert printer.doprint(4 / z) == '4 / z'
        assert printer.doprint(z / 3) == 'z / 3'
        assert printer.doprint(1 / x) == '1 / x'  # Uses pow
        assert printer.doprint(1 / (x * y)) == '1 / (x * y)'
        assert printer.doprint(1 / -(x * y)) == '-1 / (x * y)'
        assert printer.doprint(x + (y + z)) == 'x + y + z'
        assert printer.doprint(x * (y + z)) == 'x * (y + z)'
        assert printer.doprint(x * y * z) == 'x * y * z'
        assert printer.doprint(x + y > x * z), 'x + y > x * z'
        assert printer.doprint(x**2 + 3 * y**2) == 'pow(x, 2) + 3 * pow(y, 2)'
        assert printer.doprint(x**(2 + 3 * y**2)) == 'pow(x, (2 + 3 * pow(y, 2)))'
        assert printer.doprint(x**-1 * y**-1) == '1 / (x * y)'
        assert printer.doprint(x / y / z) == 'x / (y * z)'
        assert printer.doprint(x / y * z) == 'x * z / y'
        assert printer.doprint(x / (y * z)) == 'x / (y * z)'
        assert printer.doprint(x * y**(-2 / (3 * x / x))) == 'x / pow(y, (2 / 3))'

        # Sympy issue #14160
        d = sp.Mul(
            -2,
            x,
            sp.Pow(sp.Mul(y, y, evaluate=False), -1, evaluate=False),
            evaluate=False
        )
        assert printer.doprint(d) == '-2 * x / (y * y)'

    def test_ITE(self, printer, x, y):
        expr = sp.ITE(x < 0.0, x < y, y < 0.0)
        assert printer.doprint(expr) == '((x < 0.0) ? (x < y) : (y < 0.0))'
