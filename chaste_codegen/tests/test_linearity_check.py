import logging
import os

import pytest
from cellmlmanip import load_model
from cellmlmanip.printer import Printer

import chaste_codegen as cg
from chaste_codegen._linearity_check import KINDS, get_non_linear_state_vars, subst_deriv_eqs_non_linear_vars


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
OXMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#'  # oxford metadata uri prefix


@pytest.fixture(scope='session')
def hn_model():
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'hilgemann_noble_model_1987.cellml')
    return load_model(model_folder)


@pytest.fixture(scope='session')
def state_vars(hn_model):
    return hn_model.get_state_variables()


@pytest.fixture(scope='session')
def derivatives_eqs(hn_model):
    return hn_model.get_equations_for(hn_model.get_derivatives())


@pytest.fixture(scope='session')
def membrane_voltage_var(hn_model):
    return hn_model.get_variable_by_ontology_term((OXMETA, 'membrane_voltage'))


@pytest.fixture(scope='session')
def non_linear_state_vars(derivatives_eqs, membrane_voltage_var, state_vars):
    return get_non_linear_state_vars(derivatives_eqs, membrane_voltage_var, state_vars)


@pytest.fixture(scope='session')
def y_derivatives(hn_model):
    return hn_model.get_derivatives()


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
    assert str(non_linear_state_vars) == \
        ("[_calcium_release$ProdFrac, _intracellular_calcium_concentration$Ca_Calmod, "
         "_intracellular_calcium_concentration$Ca_Trop, _intracellular_calcium_concentration$Ca_i, "
         "_intracellular_calcium_concentration$Ca_rel, _intracellular_calcium_concentration$Ca_up, "
         "_intracellular_potassium_concentration$K_i, _intracellular_sodium_concentration$Na_i]")


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


def test_subst_deriv_eqs_non_linear_vars(hn_model, y_derivatives, non_linear_state_vars, membrane_voltage_var,
                                         state_vars):
    deq = subst_deriv_eqs_non_linear_vars(y_derivatives, non_linear_state_vars, membrane_voltage_var, state_vars,
                                          hn_model.get_equations_for)
    assert str(deq) == ("[Eq(_Na_Ca_exchanger$d_NaCa, 0.0001), Eq(_Na_Ca_exchanger$gamma, 0.5), Eq(_Na_Ca_exchanger$k_"
                        "NaCa, 0.01), Eq(_Na_Ca_exchanger$n_NaCa, 3.0), Eq(_calcium_background_current$g_b_Ca, 0.00500"
                        "00000000000001), Eq(_extracellular_calcium_concentration$Cab, 2.0), Eq(_extracellular_calcium"
                        "_concentration$K_diff, 0.00050000000000000001), Eq(_extracellular_sodium_concentration$Na_o, "
                        "140.0), Eq(_fast_sodium_current_m_gate$delta_m, 1.0000000000000001e-5), Eq(_intracellular_cal"
                        "cium_concentration$V_e_ratio, 0.40000000000000002), Eq(_intracellular_calcium_concentration$l"
                        "ength, 0.080000000000000002), Eq(_intracellular_calcium_concentration$radius, 0.0800000000000"
                        "00002), Eq(_intracellular_calcium_concentration$V_Cell, 3.1415926540000001*_intracellular_cal"
                        "cium_concentration$radius**2.0*_intracellular_calcium_concentration$length), Eq(_intracellula"
                        "r_calcium_concentration$Ve, _intracellular_calcium_concentration$V_Cell*_intracellular_calciu"
                        "m_concentration$V_e_ratio), Eq(_membrane$F, 96485.341499999995), Eq(_membrane$R, 8314.4719999"
                        "999998), Eq(_membrane$T, 310.0), Eq(_membrane$RTONF, _membrane$R*_membrane$T/_membrane$F), Eq"
                        "(_calcium_release$VoltDep, exp_(0.080000000000000002*_membrane$V - 3.2000000000000001)), Eq(D"
                        "erivative(_calcium_release$ActFrac, _environment$time), -_calcium_release$ActFrac*(500.0*(_in"
                        "tracellular_calcium_concentration$Ca_i/(_intracellular_calcium_concentration$Ca_i + 0.0005000"
                        "0000000000001))**2.0 + 60.0) + (600.0*_calcium_release$VoltDep + 500.0*(_intracellular_calciu"
                        "m_concentration$Ca_i/(_intracellular_calcium_concentration$Ca_i + 0.00050000000000000001))**2"
                        ".0)*(-_calcium_release$ActFrac - _calcium_release$ProdFrac + 1.0)), Eq(_fast_sodium_current_h"
                        "_gate$alpha_h, 20.0*exp_(-0.125*_membrane$V - 9.375)), Eq(_fast_sodium_current_h_gate$beta_h,"
                        " 2000.0/(320.0*exp_(-0.10000000000000001*_membrane$V - 7.5000000000000004) + 1.0)), Eq(Deriva"
                        "tive(_fast_sodium_current_h_gate$h, _environment$time), _fast_sodium_current_h_gate$alpha_h*("
                        "1.0 - _fast_sodium_current_h_gate$h) - _fast_sodium_current_h_gate$beta_h*_fast_sodium_curren"
                        "t_h_gate$h), Eq(_fast_sodium_current_m_gate$E0_m, _membrane$V + 41.0), Eq(_fast_sodium_curren"
                        "t_m_gate$alpha_m, Piecewise((2000.0, _fast_sodium_current_m_gate$delta_m > abs_(_fast_sodium_"
                        "current_m_gate$E0_m)), (200.0*_fast_sodium_current_m_gate$E0_m/(1.0 - exp_(-0.100000000000000"
                        "01*_fast_sodium_current_m_gate$E0_m)), True))), Eq(_fast_sodium_current_m_gate$beta_m, 8000.0"
                        "*exp_(-0.056000000000000001*_membrane$V - 3.6960000000000001)), Eq(Derivative(_fast_sodium_cu"
                        "rrent_m_gate$m, _environment$time), _fast_sodium_current_m_gate$alpha_m*(1.0 - _fast_sodium_c"
                        "urrent_m_gate$m) - _fast_sodium_current_m_gate$beta_m*_fast_sodium_current_m_gate$m), Eq(_sec"
                        "ond_inward_calcium_current$P_si, 5.0), Eq(_second_inward_calcium_current_d_gate$E0_d, _membra"
                        "ne$V + 19.0), Eq(_second_inward_calcium_current_d_gate$delta_d, 0.0001), Eq(_second_inward_ca"
                        "lcium_current_d_gate$alpha_d, Piecewise((120.0, _second_inward_calcium_current_d_gate$delta_d"
                        " > abs_(_second_inward_calcium_current_d_gate$E0_d)), (30.0*_second_inward_calcium_current_d_"
                        "gate$E0_d/(1.0 - exp_(-0.25*_second_inward_calcium_current_d_gate$E0_d)), True))), Eq(_second"
                        "_inward_calcium_current_d_gate$beta_d, Piecewise((120.0, _second_inward_calcium_current_d_gat"
                        "e$delta_d > abs_(_second_inward_calcium_current_d_gate$E0_d)), (12.0*_second_inward_calcium_c"
                        "urrent_d_gate$E0_d/(exp_(0.1*_second_inward_calcium_current_d_gate$E0_d) - 1.0), True))), Eq"
                        "(Derivative(_second_inward_calcium_current_d_gate$d, _environment$time), _second_inward_calc"
                        "ium_current_d_gate$alpha_d*(1.0 - _second_inward_calcium_current_d_gate$d) - _second_inward_"
                        "calcium_current_d_gate$beta_d*_second_inward_calcium_current_d_gate$d), Eq(_second_inward_cal"
                        "cium_current_f_Ca_gate$E0_f, _membrane$V + 34.0), Eq(_second_inward_calcium_current_f_Ca_gate"
                        "$beta_f_Ca, 12.0/(exp_(-0.25*_second_inward_calcium_current_f_Ca_gate$E0_f) + 1.0)), Eq(_seco"
                        "nd_inward_calcium_current_f_Ca_gate$delta_f, 0.0001), Eq(_second_inward_calcium_current_f_Ca_"
                        "gate$alpha_f_Ca, Piecewise((25.0, _second_inward_calcium_current_f_Ca_gate$delta_f > abs_(_se"
                        "cond_inward_calcium_current_f_Ca_gate$E0_f)), (6.25*_second_inward_calcium_current_f_Ca_gate$"
                        "E0_f/(exp_(0.25*_second_inward_calcium_current_f_Ca_gate$E0_f) - 1.0), True))), Eq(Derivative"
                        "(_second_inward_calcium_current_f_Ca_gate$f_Ca, _environment$time), -_second_inward_calcium_c"
                        "urrent_f_Ca_gate$alpha_f_Ca*_second_inward_calcium_current_f_Ca_gate$f_Ca + _second_inward_ca"
                        "lcium_current_f_Ca_gate$beta_f_Ca*(120.0*_intracellular_calcium_concentration$Ca_i*(1.0 - _se"
                        "cond_inward_calcium_current_f_Ca_gate$f_Ca)/(_intracellular_calcium_concentration$Ca_i + 0.00"
                        "1) + (1.0 - _second_inward_calcium_current_f_Ca_gate$f_Ca)*(-_intracellular_calcium_concentra"
                        "tion$Ca_i/(_intracellular_calcium_concentration$Ca_i + 0.001) + 1.0))), Eq(Derivative(_extrac"
                        "ellular_calcium_concentration$Ca_o, _environment$time), _extracellular_calcium_concentration$"
                        "K_diff*(-_extracellular_calcium_concentration$Ca_o + _extracellular_calcium_concentration$Cab"
                        ") - 0.5*(_Na_Ca_exchanger$k_NaCa*(-_extracellular_sodium_concentration$Na_o**_Na_Ca_exchanger"
                        "$n_NaCa*_intracellular_calcium_concentration$Ca_i*exp_(_membrane$V*(_Na_Ca_exchanger$gamma - "
                        "1.0)*(_Na_Ca_exchanger$n_NaCa - 2.0)/_membrane$RTONF) + _intracellular_sodium_concentration$N"
                        "a_i**_Na_Ca_exchanger$n_NaCa*_extracellular_calcium_concentration$Ca_o*exp_(_Na_Ca_exchanger$"
                        "gamma*_membrane$V*(_Na_Ca_exchanger$n_NaCa - 2.0)/_membrane$RTONF))/((144.92753623188406*_int"
                        "racellular_calcium_concentration$Ca_i + 1.0)*(_Na_Ca_exchanger$d_NaCa*(_extracellular_sodium_"
                        "concentration$Na_o**_Na_Ca_exchanger$n_NaCa*_intracellular_calcium_concentration$Ca_i + _intr"
                        "acellular_sodium_concentration$Na_i**_Na_Ca_exchanger$n_NaCa*_extracellular_calcium_concentra"
                        "tion$Ca_o) + 1.0)) + _calcium_background_current$g_b_Ca*(-0.5*_membrane$RTONF*log(_extracellu"
                        "lar_calcium_concentration$Ca_o/_intracellular_calcium_concentration$Ca_i) + _membrane$V) + 4."
                        "0*_second_inward_calcium_current$P_si*_second_inward_calcium_current_d_gate$d*(1.0 - _second_"
                        "inward_calcium_current_f_Ca_gate$f_Ca)*(_membrane$V - 50.0)*(-_extracellular_calcium_concentr"
                        "ation$Ca_o*exp_(-2.0*(_membrane$V - 50.0)/_membrane$RTONF) + _intracellular_calcium_concentra"
                        "tion$Ca_i*exp_(100.0/_membrane$RTONF))*(-_intracellular_calcium_concentration$Ca_i/(_intracel"
                        "lular_calcium_concentration$Ca_i + 0.001) + 1.0)/(_membrane$RTONF*(1.0 - exp_(-2.0*(_membrane"
                        "$V - 50.0)/_membrane$RTONF))))/(_intracellular_calcium_concentration$Ve*_membrane$F))]")
