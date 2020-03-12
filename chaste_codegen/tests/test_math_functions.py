#
# Tests the basics of chaste_codegen
#
# import pytest
import logging
import pytest
from chaste_codegen import exp_, abs_, acos_, cos_, sqrt_, sin_
from sympy import Symbol, sign


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


@pytest.fixture(scope='module')
def x():
    return Symbol('x', real=True)


@pytest.fixture(scope='module')
def expr(x):
    return 5 * x + 6 + 25 * x ** 2


def test_exp_(x, expr):
    x = Symbol('x', real=True)
    assert exp_(x).is_real
    assert exp_(x).diff() == exp_(x)
    assert exp_(expr).diff() == expr.diff() * exp_(expr)


def test_abs_(x, expr):
    assert abs_(x).is_real
    assert abs_(x).diff() == sign(x)
    assert abs_(expr).diff() == expr.diff() * sign(expr)


def test_acos_(x, expr):
    assert acos_(x).is_real
    assert acos_(x).diff() == -1 / sqrt_(1 - x ** 2)
    assert acos_(expr).diff() == expr.diff() * (-1 / sqrt_(1 - expr ** 2))


def test_cos_(x, expr):
    assert cos_(x).is_real
    assert cos_(x).diff() == -sin_(x)
    assert cos_(expr).diff() == expr.diff() * - sin_(expr)


def test_sqrt_(x, expr):
    assert sqrt_(x).is_real
    assert sqrt_(x).diff() == 1 / (2 * sqrt_(x))
    assert sqrt_(expr).diff() == expr.diff() * 1 / (2 * sqrt_(expr))


def test_sin_(x, expr):
    assert sin_(x).is_real
    assert sin_(x).diff() == cos_(x)
    assert sin_(expr).diff() == expr.diff() * cos_(expr)
