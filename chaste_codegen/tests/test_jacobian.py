import collections
import os

import pytest
import sympy as sp

from chaste_codegen._chaste_printer import ChastePrinter
from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen.tests.conftest import TESTS_FOLDER


@pytest.fixture(scope='session')
def state_vars(hh_model):
    return hh_model.get_state_variables()


@pytest.fixture(scope='session')
def derivatives_eqs(hh_model):
    return hh_model.get_equations_for(hh_model.get_derivatives())


@pytest.fixture(scope='session')
def jacobian(state_vars, derivatives_eqs):
    lhs_to_keep = [eq.lhs for eq in derivatives_eqs if len(eq.lhs.args) > 0 and eq.lhs.args[0] in state_vars]

    derivatives_eqs = partial_eval(derivatives_eqs, lhs_to_keep, keep_multiple_usages=False)

    return get_jacobian(state_vars, derivatives_eqs)


def test_get_jacobian_no_partial_eval(state_vars, derivatives_eqs):
    with pytest.raises(AssertionError, match="Expecting derivative equations to be reduced to the minimal set defining"
                                             " the state vars: the lhs is a state var for every eq"):
        get_jacobian(state_vars, derivatives_eqs)


def test_get_jacobian(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    expected = open(os.path.join(TESTS_FOLDER, 'test_jacobian_equations_1.txt'), 'r').read()
    # exclude x5 due to - sign difference between sympy 1.9 and 1.10
    eqs = [sp.Eq(*eq) for eq in jacobian_equations]
    required = [e.lhs for e in eqs if not str(e.lhs).endswith('x5')]
    part_eval_jacobian_equations = partial_eval(eqs, required, keep_multiple_usages=False)

    assert str(part_eval_jacobian_equations) == expected, str(jacobian_equations)
    expected = open(os.path.join(TESTS_FOLDER, 'test_jacobian_matrix_1.txt'), 'r').read()
    assert str(jacobian_matrix) == expected, str(jacobian_matrix)


def test_format_wrong_params1():
    with pytest.raises(AssertionError, match='Expecting list of equation tuples'):
        format_jacobian([1, 2], [], ChastePrinter(), None)


def test_format_wrong_params2():
    with pytest.raises(AssertionError, match='Expecting a jacobian as a matrix'):
        format_jacobian([], [], ChastePrinter(), None)


def test_format_wrong_params3(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    print(jacobian_equations)
    with pytest.raises(AssertionError, match='Expecting a jacobian as a matrix'):
        format_jacobian(jacobian_equations, [], ChastePrinter(), None)


def test_format_wrong_params4(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    with pytest.raises(AssertionError, match='Expecting printer to be a cellmlmanip.printer.Printer'):
        format_jacobian(jacobian_equations, sp.Matrix([jacobian_matrix]), None, None)


def test_format_wrong_params5(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    with pytest.raises(AssertionError, match=r"Expecting print_rhs to be a callable"):
        format_jacobian(jacobian_equations, sp.Matrix([jacobian_matrix]), ChastePrinter(), None)


def test_format_jacobian(jacobian):
    jacobian_equations, jacobian_matrix = jacobian

    # exclude x5 due to - sign difference between sympy 1.9 and 1.10
    eqs = [sp.Eq(*eq) for eq in jacobian_equations]
    required = [e.lhs for e in eqs if not str(e.lhs).endswith('x3')]
    part_eval_jacobian_equations = partial_eval(eqs, required, keep_multiple_usages=False)
    jacobian_equations = [(e.lhs, e.rhs) for e in part_eval_jacobian_equations]

    equations, jacobian = format_jacobian(jacobian_equations, sp.Matrix([jacobian_matrix]), ChastePrinter(),
                                          lambda x, y: str(x) + str(y))
    # order dictionary for printing
    equations = [collections.OrderedDict([('lhs', eq['lhs']), ('rhs', eq['rhs']), ('sympy_lhs', eq['sympy_lhs'])])
                 for eq in equations]
    # order dictionary for printing
    jacobian = [collections.OrderedDict([('i', jac['i']), ('j', jac['j']), ('entry', jac['entry'])])
                for jac in jacobian]

    expected = open(os.path.join(TESTS_FOLDER, 'test_jacobian_equations_2.txt'), 'r').read()
    assert str(equations) == expected, str(equations)
    expected = open(os.path.join(TESTS_FOLDER, 'test_jacobian_matrix_2.txt'), 'r').read()
    assert str(jacobian) == expected, str(jacobian)
