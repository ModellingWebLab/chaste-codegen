#
# Tests the basics of chaste_codegen
#
# import pytest
import logging

import pytest
from sympy import (
    Abs,
    Symbol,
    acos,
    cos,
    exp,
    pi,
    sign,
    sin,
    sqrt,
)

from chaste_codegen import (
    abs_,
    acos_,
    cos_,
    exp_,
    sin_,
    sqrt_,
    subs_math_func_placeholders,
)


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


@pytest.fixture(scope='module')
def x():
    return Symbol('x', real=True)


@pytest.fixture(scope='module')
def expr(x):
    return 5 * x + 6 + 25 * x ** 2


def test_exp_(x, expr):
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


def test_substitute_math_func_(x, expr):
    expr2 = (expr * exp_(x) + abs_(1 - 2) + acos_(0) * sin_(pi / 2) * cos_(0)) / sqrt_(x)
    expr_placeholders_replaced = subs_math_func_placeholders(expr2)
    assert expr_placeholders_replaced == (expr * exp(x) + Abs(1 - 2) + acos(0) * sin(pi / 2) * cos(0)) / sqrt(x)
