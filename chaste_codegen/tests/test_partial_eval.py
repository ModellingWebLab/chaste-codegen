import os

import pytest
from sympy import Eq, Piecewise, symbols

from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.tests.conftest import TESTS_FOLDER


def test_wrong_params():
    with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
        partial_eval(None, None)


def test_wrong_params2():
    with pytest.raises(AssertionError, match="Expecting equations to be a collection of equations"):
        partial_eval([1], [2])


def test_wrong_params3():
    with pytest.raises(AssertionError, match="Expecting required_lhs to be a collection of variables or derivatives"):
        partial_eval([Eq(symbols('x'), 2.0)], [3])


def test_partial_eval(n_model):
    derivatives_eqs = n_model.derivative_equations
    lhs_to_keep = n_model.y_derivatives
    assert len(derivatives_eqs) == 20, str(len(derivatives_eqs))
    derivatives_eqs = partial_eval(derivatives_eqs, lhs_to_keep, keep_multiple_usages=False)
    assert len(derivatives_eqs) == 4, str(len(derivatives_eqs))

    expected = open(os.path.join(TESTS_FOLDER, 'test_partial_eval_derivatives_eqs.txt'), 'r').read()
    assert str(derivatives_eqs) == expected, str(derivatives_eqs)


def test_partial_eval_piecewise():
    x, y, z = symbols('x, y, z')
    eqs = [Eq(x, 25), Eq(y, 26), Eq(z, Piecewise((1.2, x < y), (x, True)))]
    partial_eval_eqs = partial_eval(eqs, [z])
    assert partial_eval_eqs == [Eq(z, 1.2)]
