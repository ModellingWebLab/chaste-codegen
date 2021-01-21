import os

import pytest

from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.tests.conftest import TESTS_FOLDER


@pytest.fixture(scope='session')
def state_vars(hh_model):
    return hh_model.get_state_variables(sort=False)


@pytest.fixture(scope='session')
def derivatives_eqs(hh_model):
    return hh_model.get_equations_for(hh_model.get_derivatives(sort=False))


def test_wrong_params():
    with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
        partial_eval(None, None)


def test_wrong_params2():
    with pytest.raises(AssertionError, match="Expecting equations to be a collection of equations"):
        partial_eval([1], [2])


def test_wrong_params3(derivatives_eqs):
    with pytest.raises(AssertionError, match="Expecting required_lhs to be a collection of variables or derivatives"):
        partial_eval(derivatives_eqs, [2])


def test_partial_eval(state_vars, derivatives_eqs):
    lhs_to_keep = [eq.lhs for eq in derivatives_eqs if len(eq.lhs.args) > 0 and eq.lhs.args[0] in state_vars]
    assert len(derivatives_eqs) == 22, str(len(derivatives_eqs))
    derivatives_eqs = partial_eval(derivatives_eqs, lhs_to_keep, keep_multiple_usages=False)
    assert len(derivatives_eqs) == 4, str(len(derivatives_eqs))
    expected = open(os.path.join(TESTS_FOLDER, 'test_partial_eval_derivatives_eqs.txt'), 'r').read()
    assert str(derivatives_eqs) == expected, str(derivatives_eqs)
