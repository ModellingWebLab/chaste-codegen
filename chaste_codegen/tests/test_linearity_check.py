import os

import pytest
from cellmlmanip.printer import Printer

from chaste_codegen._linearity_check import KINDS, get_non_linear_state_vars, subst_deriv_eqs_non_linear_vars
from chaste_codegen._rdf import OXMETA
from chaste_codegen.tests.conftest import TESTS_FOLDER


@pytest.fixture(scope='session')
def state_vars(s_model):
    return s_model.get_state_variables(sort=False)


@pytest.fixture(scope='session')
def derivatives_eqs(s_model):
    return s_model.get_equations_for(s_model.get_derivatives(sort=False))


@pytest.fixture(scope='session')
def membrane_voltage_var(s_model):
    return s_model.get_variable_by_ontology_term((OXMETA, 'membrane_voltage'))


@pytest.fixture(scope='session')
def non_linear_state_vars(derivatives_eqs, membrane_voltage_var, state_vars):
    return get_non_linear_state_vars(derivatives_eqs, membrane_voltage_var, state_vars)


@pytest.fixture(scope='session')
def y_derivatives(s_model):
    return s_model.get_derivatives()


def test_kinds():
    assert str([{k: k.value} for k in KINDS]) ==  \
        '[{<KINDS.NONE: 1>: 1}, {<KINDS.LINEAR: 2>: 2}, {<KINDS.NONLINEAR: 3>: 3}]'


def test_wrong_params_get_non_linear_state_vars1():
    with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
        get_non_linear_state_vars(None, None, None)


def test_wrong_params_get_non_linear_state_vars2(derivatives_eqs, membrane_voltage_var):
    with pytest.raises(AssertionError, match="Expecting state_vars and derivative_equations not to be empty"):
        get_non_linear_state_vars(derivatives_eqs, membrane_voltage_var, [])


def test_get_non_linear_state_vars(non_linear_state_vars):
    non_linear_state_vars = sorted(non_linear_state_vars, key=lambda s: Printer().doprint(s))
    expected = open(os.path.join(TESTS_FOLDER, 'test_linearity_check_non_linear_state_vars.txt'), 'r').read()
    assert str(non_linear_state_vars) == expected, str(non_linear_state_vars)


def test_wrong_params_subst_deriv_eqs3():
    with pytest.raises(AssertionError, match="membrane_voltage_var should be a cellmlmanip.Variable"):
        subst_deriv_eqs_non_linear_vars([1], [1, 2], None, [1, 2], None)


def test_wrong_params_subst_deriv_eqs4(membrane_voltage_var):
    with pytest.raises(AssertionError, match="Expecting y_derivatives to be Derivatives"):
        subst_deriv_eqs_non_linear_vars([1], [1, 2], membrane_voltage_var, [1, 2], None)


def test_wrong_params_subst_deriv_eqs5(y_derivatives, membrane_voltage_var):
    with pytest.raises(AssertionError, match="Expecting non_linear_state_vars all to be cellmlmanip.Variable"):
        subst_deriv_eqs_non_linear_vars(y_derivatives, [1, 2], membrane_voltage_var, [1, 2], None)


def test_wrong_params_subst_deriv_eqs6(y_derivatives, membrane_voltage_var, non_linear_state_vars):
    with pytest.raises(AssertionError, match="Expecting state_vars all to be cellmlmanip.Variable"):
        subst_deriv_eqs_non_linear_vars(y_derivatives, non_linear_state_vars, membrane_voltage_var, [1, 2], None)


def test_wrong_params_subst_deriv_eqs7(y_derivatives, membrane_voltage_var, non_linear_state_vars, state_vars):
    with pytest.raises(AssertionError, match="Expecting get_equations_for_func to be a callable"):
        subst_deriv_eqs_non_linear_vars(y_derivatives, non_linear_state_vars, membrane_voltage_var, state_vars, None)


def test_subst_deriv_eqs_non_linear_vars(s_model, y_derivatives, non_linear_state_vars, membrane_voltage_var,
                                         state_vars):
    deq = subst_deriv_eqs_non_linear_vars(y_derivatives, non_linear_state_vars, membrane_voltage_var, state_vars,
                                          s_model.get_equations_for)

    expected = open(os.path.join(TESTS_FOLDER, 'test_linearity_check_deq.txt'), 'r').read()
    assert str(deq) == expected, str(deq)
