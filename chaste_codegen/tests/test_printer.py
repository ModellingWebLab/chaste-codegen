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
        return cg.ChastePrinter()

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
        assert printer.doprint(sp.Not(x)) == '!(x)'
        assert printer.doprint(sp.Not(sp.Eq(x, y))) == 'x != y'
        assert printer.doprint(sp.Not(sp.Eq(x, y) | sp.Eq(x, z))) == '!((x == y) || (x == z))'

    def test_and(self, printer, x, y):
        assert printer.doprint(sp.sympify('x & y')) == '(x) && (y)'

    def test_booleans(self, printer, x):
        assert printer.doprint(sp.Eq(x, x)) == printer.doprint(True) == 'true'
        assert printer.doprint(sp.Ne(x, x)) == printer.doprint(False) == 'false'

    def test_or(self, printer, x, y, z):
        assert printer.doprint(sp.Or(sp.Eq(x, y), sp.Eq(x, z))) \
            == printer.doprint(sp.Eq(x, y) | sp.Eq(x, z)) == '(x == y) || (x == z)'

    def test_pow(self, printer, x, y):
        assert printer.doprint(sp.sympify('x ** y')) == 'CHASTE_MATH::Pow(x, y)'
        assert printer.doprint(sp.sympify('Pow(x,y)')) == 'CHASTE_MATH::Pow(x, y)'
        assert printer.doprint(sp.sympify('x ** (1/2)')) == 'CHASTE_MATH::Sqrt(x)'
        assert printer.doprint(sp.sympify('x ** (-1/2)')) == '1 / CHASTE_MATH::Sqrt(x)'
        assert printer.doprint(1 / x) == '1 / x'
        assert printer.doprint(sp.Pow(x, 0.5)) == 'CHASTE_MATH::Sqrt(x)'

    def test_piecewise_expressions(self, printer, x, y, z):
        # Piecewise expressions
        conditionalexp_r = sp.Piecewise((0, x > 0), (1, True))
        assert printer.doprint(conditionalexp_r) == '((x > 0) ? (0) : (1))'
        conditionalexp_r = sp.Piecewise((0, x > 0), (1, x > 1), (2, True))
        assert printer.doprint(conditionalexp_r) == '((x > 0) ? (0) : ((x > 1) ? (1) : (2)))'

    def testabs_(self, printer, x, y):
        assert printer.doprint(sp.Abs(x + y)) == 'CHASTE_MATH::Abs(x + y)'
        assert printer.doprint(sp.Abs(sp.Float('3.2', 17), evaluate=False)) \
            == 'CHASTE_MATH::Abs(CHASTE_CONST(3.2000000000000002))'
        assert printer.doprint(sp.Abs(-3, evaluate=False)) == 'CHASTE_MATH::Abs(-3)'

    def test_trig_functions(self, printer, x):
        # Trig functions
        assert printer.doprint(sp.acos(x)) == 'CHASTE_MATH::Acos(x)'
        assert printer.doprint(sp.acosh(x)) == 'CHASTE_MATH::Acosh(x)'
        assert printer.doprint(sp.asin(x)) == 'CHASTE_MATH::Asin(x)'
        assert printer.doprint(sp.asinh(x)) == 'CHASTE_MATH::Asinh(x)'
        assert printer.doprint(sp.atan(x)) == 'CHASTE_MATH::Atan(x)'
        assert printer.doprint(sp.atanh(x)) == 'CHASTE_MATH::Atanh(x)'
        assert printer.doprint(sp.ceiling(x)) == 'CHASTE_MATH::Ceil(x)'
        assert printer.doprint(sp.cos(x)) == 'CHASTE_MATH::Cos(x)'
        assert printer.doprint(sp.cosh(x)) == 'CHASTE_MATH::Cosh(x)'
        assert printer.doprint(sp.exp(x)) == 'CHASTE_MATH::Exp(x)'
        assert printer.doprint(sp.factorial(x)) == 'CHASTE_MATH::Factorial(x)'
        assert printer.doprint(sp.floor(x)) == 'CHASTE_MATH::Floor(x)'
        assert printer.doprint(sp.log(x)) == 'CHASTE_MATH::Log(x)'
        assert printer.doprint(sp.sin(x)) == 'CHASTE_MATH::Sin(x)'
        assert printer.doprint(sp.sinh(x)) == 'CHASTE_MATH::Sinh(x)'
        assert printer.doprint(sp.tan(x)) == 'CHASTE_MATH::Tan(x)'
        assert printer.doprint(sp.tanh(x)) == 'CHASTE_MATH::Tanh(x)'

        # extra trig functions
        assert printer.doprint(sp.sec(x)) == '1 / CHASTE_MATH::Cos(x)'
        assert printer.doprint(sp.csc(x)) == '1 / CHASTE_MATH::Sin(x)'
        assert printer.doprint(sp.cot(x)) == '1 / CHASTE_MATH::Tan(x)'
        assert printer.doprint(sp.asec(x)) == 'CHASTE_MATH::Acos(1 / x)'
        assert printer.doprint(sp.acsc(x)) == 'CHASTE_MATH::Asin(1 / x)'
        assert printer.doprint(sp.acot(x)) == 'CHASTE_MATH::Atan(1 / x)'
        assert printer.doprint(sp.sech(x)) == '1 / CHASTE_MATH::Cosh(x)'
        assert printer.doprint(sp.csch(x)) == '1 / CHASTE_MATH::Sinh(x)'
        assert printer.doprint(sp.coth(x)) == '1 / CHASTE_MATH::Tanh(x)'
        assert printer.doprint(sp.asech(x)) == 'CHASTE_MATH::Acosh(1 / x)'
        assert printer.doprint(sp.acsch(x)) == 'CHASTE_MATH::Asinh(1 / x)'
        assert printer.doprint(sp.acoth(x)) == 'CHASTE_MATH::Atanh(1 / x)'

    def test_custom_math_functions(self, printer, x):
        assert printer.doprint(acos_(x)) == 'CHASTE_MATH::Acos(x)'
        assert printer.doprint(cos_(x)) == 'CHASTE_MATH::Cos(x)'
        assert printer.doprint(exp_(x)) == 'CHASTE_MATH::Exp(x)'
        assert printer.doprint(sin_(x)) == 'CHASTE_MATH::Sin(x)'
        assert printer.doprint(sqrt_(x)) == 'CHASTE_MATH::Sqrt(x)'
        assert printer.doprint(abs_(x)) == 'CHASTE_MATH::Abs(x)'

    def test_numbers(self, printer, x):
        # Number types
        assert printer.doprint(1) == '1'                  # int
        assert printer.doprint(1.2) == 'CHASTE_CONST(1.2)'              # float, short format
        assert printer.doprint(math.pi) == 'CHASTE_CONST(3.1415926535897931)'  # float, long format
        assert printer.doprint(1.436432635636e-123) == 'CHASTE_CONST(1.436432635636e-123)'
        assert printer.doprint(x - x) == '0'              # Zero
        assert printer.doprint(x / x) == '1'              # One
        assert printer.doprint(-x / x) == '-1'            # Negative one
        assert printer.doprint(5 * (x / x)) == '5'        # Sympy integer
        assert printer.doprint(5.5 * (x / x)) == 'CHASTE_CONST(5.5)'        # Sympy float
        assert printer.doprint(sp.Rational(5, 7)) == '5 / 7'  # Sympy rational

        # Special numbers
        assert printer.doprint(sp.pi) == 'CHASTE_CONST(CHASTE_MATH::Pi)'
        assert printer.doprint(sp.E) == 'CHASTE_CONST(CHASTE_MATH::E)'

        # large ints
        assert printer.doprint(8034023767017108950029959168) == 'CHASTE_CONST(8.034023767017109e+27)'
        assert printer.doprint(-8034023767017108950029959168) == '-CHASTE_CONST(8.034023767017109e+27)'

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
        assert printer.doprint(x**2 + 3 * y**2) == 'CHASTE_MATH::Pow(x, 2) + 3 * CHASTE_MATH::Pow(y, 2)'
        assert printer.doprint(x**(2 + 3 * y**2)) == 'CHASTE_MATH::Pow(x, (2 + 3 * CHASTE_MATH::Pow(y, 2)))'
        assert printer.doprint(x**-1 * y**-1) == '1 / (x * y)'
        assert printer.doprint(x / y / z) == 'x / (y * z)'
        assert printer.doprint(x / y * z) == 'x * z / y'
        assert printer.doprint(x / (y * z)) == 'x / (y * z)'
        assert printer.doprint(x * y**(-2 / (3 * x / x))) == 'x / CHASTE_MATH::Pow(y, (2 / 3))'

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
        assert printer.doprint(expr) == '((x < 0) ? (x < y) : (y < 0))'
