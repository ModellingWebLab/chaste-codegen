#
# Tests conversion of sympy expressions to C++ code for Chaste code generation.
#
import chaste_codegen as cg
import logging
import math
import pytest
import sympy as sp


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
        conditional_expr = sp.Piecewise((0, x > 0), (1, True))
        assert printer.doprint(conditional_expr) == '((x > 0) ? (0) : (1))'
        conditional_expr = sp.Piecewise((0, x > 0), (1, x > 1), (2, True))
        assert printer.doprint(conditional_expr) == '((x > 0) ? (0) : ((x > 1) ? (1) : (2)))'

    def test_abs(self, printer, x, y):
        assert printer.doprint(sp.Abs(x + y)) == 'fabs(x + y)'
        assert printer.doprint(sp.Abs(sp.Float('3.2', 17), evaluate=False)) == 'fabs(3.2000000000000002)'
        assert printer.doprint(sp.Abs(-3, evaluate=False)) == 'fabs(-3)'

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
        assert printer.doprint(sp._exp(x)) == 'exp(x)'
        assert printer.doprint(sp.factorial(x)) == 'factorial(x)'
        assert printer.doprint(sp.floor(x)) == 'floor(x)'
        assert printer.doprint(sp.log(x)) == 'log(x)'
        assert printer.doprint(sp.sin(x)) == 'sin(x)'
        assert printer.doprint(sp.sinh(x)) == 'sinh(x)'
        assert printer.doprint(sp.tan(x)) == 'tan(x)'
        assert printer.doprint(sp.tanh(x)) == 'tanh(x)'

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
        assert printer.doprint(sp.pi) == 'M_PI'
        assert printer.doprint(sp.E) == 'e'
