#
# Tests conversion of sympy expressions to weblab cython code.
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
        assert printer.doprint(sp.sympify('x & y')) == 'x && y'

    def test_booleans(self, printer, x):
        assert printer.doprint(sp.Eq(x, x)) == printer.doprint(True) == 'true'
        assert printer.doprint(sp.Ne(x, x)) == printer.doprint(False) == 'false'

    def test_or(self, printer, x, y, z):
        assert printer.doprint(sp.Or(sp.Eq(x, y), sp.Eq(x, z))) \
            == printer.doprint(sp.Eq(x, y) | sp.Eq(x, z)) == 'x == y || x == z'

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
