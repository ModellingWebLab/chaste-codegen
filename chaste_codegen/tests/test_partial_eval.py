import os

import pytest
from sympy import Eq, Symbol

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
        partial_eval([Eq(Symbol('x'), 2.0)], [3])


def test_partial_eval(hh_model):
    derivatives_eqs = hh_model.derivative_equations
    lhs_to_keep = hh_model.y_derivatives
    assert len(derivatives_eqs) == 18, str(len(derivatives_eqs))
    derivatives_eqs = partial_eval(derivatives_eqs, lhs_to_keep, keep_multiple_usages=False)
    assert len(derivatives_eqs) == 4, str(len(derivatives_eqs))
    expected = open(os.path.join(TESTS_FOLDER, 'test_partial_eval_derivatives_eqs.txt'), 'r').read()
    assert str(derivatives_eqs) == expected, str(derivatives_eqs)


def test_partial_eval2(fr_model):
    derivatives_eqs = fr_model.derivative_equations
    lhs_to_keep = fr_model.y_derivatives
    assert len(derivatives_eqs) == 163, str(len(derivatives_eqs))
    derivatives_eqs = partial_eval(derivatives_eqs, lhs_to_keep, keep_multiple_usages=False)
    assert len(derivatives_eqs) == 25, str(len(derivatives_eqs))
    expected = open(os.path.join(TESTS_FOLDER, 'test_partial_eval_derivatives_eqs2.txt'), 'r').read()
    assert str(derivatives_eqs) == expected, str(derivatives_eqs)
