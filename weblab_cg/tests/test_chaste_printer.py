#
# Tests conversion of sympy expressions to C++ code for Chaste code generation.
#
import weblab_cg as cg
import logging
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

    def test_abs(self, printer, x, y):
        assert printer.doprint(sp.Abs(x + y)) == 'fabs(x + y)'
        assert printer.doprint(sp.Abs(3.2, evaluate=False)) == 'fabs(3.2)'
        assert printer.doprint(sp.Abs(-3, evaluate=False)) == 'fabs(-3)'

