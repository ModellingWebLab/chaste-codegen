#
# Tests the basics of chaste_codegen
#
# import pytest
import logging
import pytest
from chaste_codegen import _exp, _abs, _acos, _cos, _sqrt, _sin
from sympy import Symbol, sign


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


@pytest.fixture(scope='module')
def x():
    return Symbol('x', real=True)


@pytest.fixture(scope='module')
def expr(x):
    return 5 * x + 6 + 25 * x ** 2


def test__exp(x, expr):
    x = Symbol('x', real=True)
    assert _exp(x).is_real
    assert _exp(x).diff() == _exp(x)
    assert _exp(expr).diff() == expr.diff() * _exp(expr)


def test__abs(x, expr):
    assert _abs(x).is_real
    assert _abs(x).diff() == sign(x)
    assert _abs(expr).diff() == expr.diff() * sign(expr)


def test__acos(x, expr):
    assert _acos(x).is_real
    assert _acos(x).diff() == -1 / _sqrt(1 - x ** 2)
    assert _acos(expr).diff() == expr.diff() * (-1 / _sqrt(1 - expr ** 2))


def test__cos(x, expr):
    assert _cos(x).is_real
    assert _cos(x).diff() == -_sin(x)
    assert _cos(expr).diff() == expr.diff() * - _sin(expr)


def test__sqrt(x, expr):
    assert _sqrt(x).is_real
    assert _sqrt(x).diff() == 1 / (2 * _sqrt(x))
    assert _sqrt(expr).diff() == expr.diff() * 1 / (2 * _sqrt(expr))


def test__sin(x, expr):
    assert _sin(x).is_real
    assert _sin(x).diff() == _cos(x)
    assert _sin(expr).diff() == expr.diff() * _cos(expr)
