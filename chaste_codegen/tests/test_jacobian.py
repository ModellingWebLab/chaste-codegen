import collections
import logging
import os

import pytest
import sympy as sp
from cellmlmanip import load_model

import chaste_codegen as cg
from chaste_codegen._chaste_printer import ChastePrinter
from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._partial_eval import partial_eval
from sympy.codegen.rewriting import ReplaceOptim, optimize
from sympy import (Eq, Float, Function, Pow, Matrix)


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.fixture(scope='session')
def hh_model():
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
    return load_model(model_folder)


@pytest.fixture(scope='session')
def state_vars(hh_model):
    return hh_model.get_state_variables(sort=False)


@pytest.fixture(scope='session')
def derivatives_eqs(hh_model):
    OXMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#'  # oxford metadata uri prefix
    POW_OPT = ReplaceOptim(lambda p: p.is_Pow and (isinstance(p.exp, Float) or isinstance(p.exp, float))
                            and float(p.exp).is_integer(),
                            lambda p: Pow(p.base, int(float(p.exp))))
    deriv_eqs = hh_model.get_equations_for(hh_model.get_derivatives(sort=False))
    area = Function('GetIntracellularAreaStimulus')(hh_model.get_free_variable())
    stim = hh_model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current'))
    deriv_eqs = [eq if eq.lhs is not stim else Eq(eq.lhs, area) for eq in deriv_eqs]
    return [Eq(eq.lhs, optimize(eq.rhs, (POW_OPT, ))) for eq in deriv_eqs]


@pytest.fixture(scope='session')
def jacobian(state_vars, derivatives_eqs, hh_model):
    lhs_to_keep = [eq.lhs for eq in derivatives_eqs if len(eq.lhs.args) > 0 and eq.lhs.args[0] in state_vars]

    derivatives_eqs = partial_eval(derivatives_eqs, lhs_to_keep, keep_multiple_usages=False)

    return get_jacobian(state_vars, derivatives_eqs)


def test_get_jacobian_no_partial_eval(state_vars, derivatives_eqs):
    with pytest.raises(AssertionError, match="Expecting derivative equations to be reduced to the minimal set defining"
                                             " the state vars: the lhs is a state var for every eq"):
        get_jacobian(state_vars, derivatives_eqs)


def test_get_jacobian(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    assert str(jacobian_equations) == ("[(x0, 120.0*_sodium_channel_m_gate$m**3), (x1, _membrane$V - 40.0), (x2, exp_(-0.055555555555555556*_membrane$V - 4.1666666666666667)), (x3, 1.0 - _sodium_channel_m_gate$m), (x4, -0.1*_membrane$V), (x5, exp_(x4 - 5.0)), (x6, x5 - 1.0), (x7, 0.10000000000000001/x6), (x8, _membrane$V + 50.0), (x9, exp_(-0.05*_membrane$V - 3.75)), (x10, exp_(x4 - 4.5)), (x11, x10 + 1.0), (x12, 1.0 - _potassium_channel_n_gate$n), (x13, exp_(x4 - 6.5)), (x14, x13 - 1.0), (x15, 0.01/x14), (x16, exp_(0.0125*_membrane$V + 0.9375)), (x17, _membrane$V + 65.0)]")
    assert str(jacobian_matrix) == ("Matrix([[-x0*_sodium_channel_h_gate$h - 36.0*_potassium_channel_n_gate$n**4 - 0.29999999999999999, -360.0*x1*_sodium_channel_m_gate$m**2*_sodium_channel_h_gate$h, -x0*x1, -144.0*_potassium_channel_n_gate$n**3*(_membrane$V + 87.0)], [0.22222222222222222*x2*_sodium_channel_m_gate$m - 0.010000000000000001*x3*x5*x8/x6**2 - x3*x7, -4.0*x2 + x7*x8, 0, 0], [-0.1*x10*_sodium_channel_h_gate$h/x11**2 - 0.05*x9*(0.070000000000000007 - 0.070000000000000007*_sodium_channel_h_gate$h), 0, -0.070000000000000007*x9 - 1.0/x11, 0], [-0.001*x12*x13*x17/x14**2 - x12*x15 - 0.0015625*x16*_potassium_channel_n_gate$n, 0, 0, x15*x17 - 0.125*x16]])")


def test_format_wrong_params2():
    with pytest.raises(AssertionError, match='Expecting list of equation tuples'):
        format_jacobian([1, 2], [], ChastePrinter(), None)


def test_format_wrong_params1():
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
        format_jacobian(jacobian_equations, Matrix([jacobian_matrix]), None, None)


def test_format_wrong_params5(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    with pytest.raises(AssertionError, match=r"Expecting print_rhs to be a callable"):
        format_jacobian(jacobian_equations, Matrix([jacobian_matrix]), ChastePrinter(), None)


def test_format_jacobian(jacobian):
    jacobian_equations, jacobian_matrix = jacobian
    equations, jacobian = format_jacobian(jacobian_equations, Matrix([jacobian_matrix]), cg.ChastePrinter(),
                                          lambda x, y: str(y))
    # order dictionary for printing
    equations = [collections.OrderedDict([('lhs', eq['lhs']), ('rhs', eq['rhs']), ('sympy_lhs', eq['sympy_lhs'])])
                 for eq in equations]
    # order dictionary for printing
    jacobian = [collections.OrderedDict([('i', jac['i']), ('j', jac['j']), ('entry', jac['entry'])])
                for jac in jacobian]
    print(equations)
    print(jacobian)
    assert str(equations) == \
        ("[OrderedDict([('lhs', 'x0'), ('rhs', '120.0*_sodium_channel_m_gate$m**3'), ('sympy_lhs', x0)]), OrderedDict([('lhs', 'x1'), ('rhs', '_membrane$V - 40.0'), ('sympy_lhs', x1)]), OrderedDict([('lhs', 'x2'), ('rhs', 'exp_(-0.055555555555555556*_membrane$V - 4.1666666666666667)'), ('sympy_lhs', x2)]), OrderedDict([('lhs', 'x3'), ('rhs', '1.0 - _sodium_channel_m_gate$m'), ('sympy_lhs', x3)]), OrderedDict([('lhs', 'x4'), ('rhs', '-0.1*_membrane$V'), ('sympy_lhs', x4)]), OrderedDict([('lhs', 'x5'), ('rhs', 'exp_(x4 - 5.0)'), ('sympy_lhs', x5)]), OrderedDict([('lhs', 'x6'), ('rhs', 'x5 - 1.0'), ('sympy_lhs', x6)]), OrderedDict([('lhs', 'x7'), ('rhs', '0.10000000000000001/x6'), ('sympy_lhs', x7)]), OrderedDict([('lhs', 'x8'), ('rhs', '_membrane$V + 50.0'), ('sympy_lhs', x8)]), OrderedDict([('lhs', 'x9'), ('rhs', 'exp_(-0.05*_membrane$V - 3.75)'), ('sympy_lhs', x9)]), OrderedDict([('lhs', 'x10'), ('rhs', 'exp_(x4 - 4.5)'), ('sympy_lhs', x10)]), OrderedDict([('lhs', 'x11'), ('rhs', 'x10 + 1.0'), ('sympy_lhs', x11)]), OrderedDict([('lhs', 'x12'), ('rhs', '1.0 - _potassium_channel_n_gate$n'), ('sympy_lhs', x12)]), OrderedDict([('lhs', 'x13'), ('rhs', 'exp_(x4 - 6.5)'), ('sympy_lhs', x13)]), OrderedDict([('lhs', 'x14'), ('rhs', 'x13 - 1.0'), ('sympy_lhs', x14)]), OrderedDict([('lhs', 'x15'), ('rhs', '0.01/x14'), ('sympy_lhs', x15)]), OrderedDict([('lhs', 'x16'), ('rhs', 'exp_(0.0125*_membrane$V + 0.9375)'), ('sympy_lhs', x16)]), OrderedDict([('lhs', 'x17'), ('rhs', '_membrane$V + 65.0'), ('sympy_lhs', x17)])]")

    assert str(jacobian) == \
        ("[OrderedDict([('i', 0), ('j', 0), ('entry', '-0.29999999999999999 - 36.0 * pow(potassium_channel_n_gate$n, 4) - x0 * sodium_channel_h_gate$h')]), OrderedDict([('i', 1), ('j', 0), ('entry', '-x3 * x7 + 0.22222222222222221 * x2 * sodium_channel_m_gate$m - 0.01 * x3 * x5 * x8 / pow(x6, 2)')]), OrderedDict([('i', 2), ('j', 0), ('entry', '-0.050000000000000003 * x9 * (0.070000000000000007 - 0.070000000000000007 * sodium_channel_h_gate$h) - 0.10000000000000001 * x10 * sodium_channel_h_gate$h / pow(x11, 2)')]), OrderedDict([('i', 3), ('j', 0), ('entry', '-x12 * x15 - 0.0015625000000000001 * x16 * potassium_channel_n_gate$n - 0.001 * x12 * x13 * x17 / pow(x14, 2)')]), OrderedDict([('i', 0), ('j', 1), ('entry', '-360.0 * x1 * pow(sodium_channel_m_gate$m, 2) * sodium_channel_h_gate$h')]), OrderedDict([('i', 1), ('j', 1), ('entry', '-4.0 * x2 + x7 * x8')]), OrderedDict([('i', 0), ('j', 2), ('entry', '-x0 * x1')]), OrderedDict([('i', 2), ('j', 2), ('entry', '-1.0 / x11 - 0.070000000000000007 * x9')]), OrderedDict([('i', 0), ('j', 3), ('entry', '-144.0 * pow(potassium_channel_n_gate$n, 3) * (87.0 + membrane$V)')]), OrderedDict([('i', 3), ('j', 3), ('entry', '-0.125 * x16 + x15 * x17')])]")
