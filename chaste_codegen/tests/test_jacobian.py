import logging
import os

import pytest
import sympy as sp
from cellmlmanip import load_model
from cellmlmanip.printer import Printer

import chaste_codegen as cg
from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._partial_eval import partial_eval


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.fixture
def hh_model(scope='session'):
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
    return load_model(model_folder)


@pytest.fixture
def state_vars(hh_model, scope='session'):
    return hh_model.get_state_variables()


@pytest.fixture
def derivatives_eqs(hh_model, scope='session'):
    return hh_model.get_equations_for(hh_model.get_derivatives())


@pytest.fixture
def jacobian(state_vars, derivatives_eqs, scope='session'):
    lhs_to_keep = [eq.lhs for eq in derivatives_eqs if len(eq.lhs.args) > 0 and eq.lhs.args[0] in state_vars]

    derivatives_eqs = partial_eval(derivatives_eqs, lhs_to_keep, keep_multiple_usages=False)

    return get_jacobian(state_vars, derivatives_eqs)


def test_get_jacobian_empty_state_var():
    with pytest.raises(AssertionError, match='Expecting state_vars and derivative_equations not to be empty'):
        get_jacobian([], [])


def test_get_jacobian_no_partial_eval(state_vars, derivatives_eqs):
    with pytest.raises(AssertionError, match="Expecting derivative equations to be reduced to the minimal set defining"
                                             " the state vars: the lhs is a state var for every eq"):
        get_jacobian(state_vars, derivatives_eqs)


def test_get_and_format_jacobian(jacobian):
    jacobian_equations, jacobian_matrix = jacobian

    assert str(jacobian_equations) == ("[(x0, 120.0*_sodium_channel_m_gate$m**3.0), (x1, _membrane$V - 40.0), "
                                       "(x2, exp_(-0.055555555555555556*_membrane$V - 4.1666666666666667)), "
                                       "(x3, 1.0 - _sodium_channel_m_gate$m), (x4, -0.1*_membrane$V), "
                                       "(x5, exp_(x4 - 5.0)), (x6, x5 - 1.0), (x7, 0.10000000000000001/x6), "
                                       "(x8, _membrane$V + 50.0), (x9, exp_(-0.05*_membrane$V - 3.75)), "
                                       "(x10, exp_(x4 - 4.5)), (x11, x10 + 1.0), "
                                       "(x12, 1.0 - _potassium_channel_n_gate$n), (x13, exp_(x4 - 6.5)), "
                                       "(x14, x13 - 1.0), (x15, 0.01/x14), (x16, exp_(0.0125*_membrane$V + 0.9375)), "
                                       "(x17, _membrane$V + 65.0)]")
    assert str(jacobian_matrix) == ("Matrix([[-x0*_sodium_channel_h_gate$h - 36.0*_potassium_channel_n_gate$n**4.0 "
                                    "- 0.29999999999999999, -360.0*x1*_sodium_channel_m_gate$m**2.0"
                                    "*_sodium_channel_h_gate$h, -x0*x1, -144.0*_potassium_channel_n_gate$n**3.0*"
                                    "(_membrane$V + 87.0)], [0.22222222222222222*x2*_sodium_channel_m_gate$m - "
                                    "0.010000000000000001*x3*x5*x8/x6**2 - x3*x7, -4.0*x2 + x7*x8, 0, 0], "
                                    "[-0.1*x10*_sodium_channel_h_gate$h/x11**2 - 0.05*x9*(0.070000000000000007 "
                                    "- 0.070000000000000007*_sodium_channel_h_gate$h), 0, -0.070000000000000007*x9"
                                    " - 1.0/x11, 0], [-0.001*x12*x13*x17/x14**2 - x12*x15 - "
                                    "0.0015625*x16*_potassium_channel_n_gate$n, 0, 0, x15*x17 - 0.125*x16]])")


def test_format_wrong_params2():
    with pytest.raises(AssertionError, match='Expecting list of equation tuples'):
        format_jacobian([1, 2], [], None, None)


def test_format_wrong_params1():
    with pytest.raises(AssertionError, match='Expecting a non-empty jacobian as a matrix'):
        format_jacobian([], [], None, None)


def test_format_wrong_params3(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    print(jacobian_equations)
    with pytest.raises(AssertionError, match='Expecting a non-empty jacobian as a matrix'):
        format_jacobian(jacobian_equations, [], None, None)


def test_format_wrong_params4(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    with pytest.raises(AssertionError, match='Expecting a non-empty jacobian as a matrix'):
        format_jacobian(jacobian_equations, sp.Matrix([]), None, None)


def test_format_wrong_params5(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    with pytest.raises(AssertionError, match='Expecting printer to be a cellmlmanip.printer.Printer'):
        format_jacobian(jacobian_equations, sp.Matrix([jacobian_matrix]), None, None)


def test_format_wrong_params6(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    with pytest.raises(AssertionError, match=r"Expecting print_rhs to be a callable"):
        format_jacobian(jacobian_equations, sp.Matrix([jacobian_matrix]), Printer(), None)


def test_format_jacobian(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    equations, jacobian = format_jacobian(jacobian_equations, sp.Matrix([jacobian_matrix]), Printer(),
                                          lambda x, y: str(x) + str(y))
    assert str(equations) == ("[{'lhs': 'x0', 'rhs': 'x0120.0*_sodium_channel_m_gate$m**3.0', 'sympy_lhs': x0}, "
                              "{'lhs': 'x1', 'rhs': 'x1_membrane$V - 40.0', 'sympy_lhs': x1}, {'lhs': 'x2', 'rhs':"
                              " 'x2exp_(-0.055555555555555556*_membrane$V - 4.1666666666666667)', 'sympy_lhs': x2},"
                              " {'lhs': 'x3', 'rhs': 'x31.0 - _sodium_channel_m_gate$m', 'sympy_lhs': x3}, "
                              "{'lhs': 'x4', 'rhs': 'x4-0.1*_membrane$V', 'sympy_lhs': x4}, {'lhs': 'x5', 'rhs': "
                              "'x5exp_(x4 - 5.0)', 'sympy_lhs': x5}, {'lhs': 'x6', 'rhs': 'x6x5 - 1.0', "
                              "'sympy_lhs': x6}, {'lhs': 'x7', 'rhs': 'x70.10000000000000001/x6', 'sympy_lhs': x7},"
                              " {'lhs': 'x8', 'rhs': 'x8_membrane$V + 50.0', 'sympy_lhs': x8}, {'lhs': 'x9', 'rhs': "
                              "'x9exp_(-0.05*_membrane$V - 3.75)', 'sympy_lhs': x9}, {'lhs': 'x10', 'rhs': "
                              "'x10exp_(x4 - 4.5)', 'sympy_lhs': x10}, {'lhs': 'x11', 'rhs': 'x11x10 + 1.0', "
                              "'sympy_lhs': x11}, {'lhs': 'x12', 'rhs': 'x121.0 - _potassium_channel_n_gate$n', "
                              "'sympy_lhs': x12}, {'lhs': 'x13', 'rhs': 'x13exp_(x4 - 6.5)', 'sympy_lhs': x13}, "
                              "{'lhs': 'x14', 'rhs': 'x14x13 - 1.0', 'sympy_lhs': x14}, {'lhs': 'x15', 'rhs': "
                              "'x150.01/x14', 'sympy_lhs': x15}, {'lhs': 'x16', 'rhs': "
                              "'x16exp_(0.0125*_membrane$V + 0.9375)', 'sympy_lhs': x16}, {'lhs': 'x17', 'rhs': "
                              "'x17_membrane$V + 65.0', 'sympy_lhs': x17}]")

    assert str(jacobian) == ("[{'i': 0, 'j': 0, 'entry': '-0.3 - 36.0 * potassium_channel_n_gate$n**4.0 - x0 * "
                             "sodium_channel_h_gate$h'}, {'i': 1, 'j': 0, 'entry': '-x3 * x7 + 0.2222222222222222 "
                             "* x2 * sodium_channel_m_gate$m - 0.01 * x3 * x5 * x8 / x6**2'}, {'i': 2, 'j': 0, "
                             "'entry': '-0.05 * x9 * (0.07 - 0.07 * sodium_channel_h_gate$h) - 0.1 * x10 * "
                             "sodium_channel_h_gate$h / x11**2'}, {'i': 3, 'j': 0, 'entry': '-x12 * x15 - 0.0015625 "
                             "* x16 * potassium_channel_n_gate$n - 0.001 * x12 * x13 * x17 / x14**2'}, {'i': 0, 'j':"
                             " 1, 'entry': '-360.0 * x1 * sodium_channel_m_gate$m**2.0 * sodium_channel_h_gate$h'},"
                             " {'i': 1, 'j': 1, 'entry': '-4.0 * x2 + x7 * x8'}, {'i': 0, 'j': 2, 'entry': '-x0 * "
                             "x1'}, {'i': 2, 'j': 2, 'entry': '-1.0 / x11 - 0.07 * x9'}, {'i': 0, 'j': 3, 'entry':"
                             " '-144.0 * potassium_channel_n_gate$n**3.0 * (87.0 + membrane$V)'}, {'i': 3, 'j': 3,"
                             " 'entry': '-0.125 * x16 + x15 * x17'}]")
