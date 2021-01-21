import pytest
from cellmlmanip.printer import Printer

from chaste_codegen._linearity_check import KINDS, get_non_linear_state_vars, subst_deriv_eqs_non_linear_vars
from chaste_codegen._rdf import OXMETA


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
    assert str(non_linear_state_vars) == \
        ("[_Ca_buffer$Ca_Calsequestrin, _Ca_buffer$Ca_SL, _Ca_buffer$Ca_SLB_SL, _Ca_buffer$Ca_SLB_jct, _Ca_buffer$Ca_S"
         "LHigh_SL, _Ca_buffer$Ca_SLHigh_jct, _Ca_buffer$Ca_SR, _Ca_buffer$Ca_jct, _Ca_buffer$Cai, _ICaL_fCa_gate$fCaB"
         "_SL, _ICaL_fCa_gate$fCaB_jct, _Jrel_SR$I, _Jrel_SR$O, _Jrel_SR$R, _Na_buffer$Na_SL, _Na_buffer$Na_SL_buf, _N"
         "a_buffer$Na_jct, _Na_buffer$Na_jct_buf, _Na_buffer$Nai, _cytosolic_Ca_buffer$Ca_Calmodulin, _cytosolic_Ca_bu"
         "ffer$Ca_Myosin, _cytosolic_Ca_buffer$Ca_SRB, _cytosolic_Ca_buffer$Ca_TroponinC, _cytosolic_Ca_buffer$Ca_Trop"
         "oninC_Ca_Mg, _cytosolic_Ca_buffer$Mg_Myosin, _cytosolic_Ca_buffer$Mg_TroponinC_Ca_Mg, _indo_fluo_Ca_buffer_n"
         "ot_connected$Ca_Fluo3_Cytosol, _indo_fluo_Ca_buffer_not_connected$Ca_Fluo3_SL, _indo_fluo_Ca_buffer_not_conn"
         "ected$Ca_Fluo3_jct, _indo_fluo_Ca_buffer_not_connected$Ca_Indo1_Cytosol, _indo_fluo_Ca_buffer_not_connected$"
         "Ca_Indo1_SL, _indo_fluo_Ca_buffer_not_connected$Ca_Indo1_jct]")


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
    assert str(deq) == \
        ("[Eq(_INa$perc_reduced_inact_for_IpNa, 0), Eq(_INa$shift_INa_inact, 0), Eq(_ICaL_d_gate$d_infinity, 1.0/(exp_"
         "(-0.16666666666666667*_cell$V - 2.4166666666666667) + 1.0)), Eq(_ICaL_d_gate$tau_d, 28.571428571428569*_ICaL"
         "_d_gate$d_infinity*(1.0 - exp_(-0.16666666666666667*_cell$V - 2.4166666666666667))/(_cell$V + 14.5)), Eq(Der"
         "ivative(_ICaL_d_gate$d, _environment$time), (-_ICaL_d_gate$d + _ICaL_d_gate$d_infinity)/_ICaL_d_gate$tau_d),"
         " Eq(_ICaL_f_gate$f_infinity, 1.0/(exp_(0.27777777777777777*_cell$V + 9.7388888888888893) + 1.0) + 0.59999999"
         "999999998/(exp_(2.5 - 0.05*_cell$V) + 1.0)), Eq(_ICaL_f_gate$tau_f, 1.0/(0.019699999999999999*exp_(-0.238778"
         "82250000001*(0.06896551724137931*_cell$V + 1)**2.0) + 0.02)), Eq(Derivative(_ICaL_f_gate$f, _environment$tim"
         "e), (-_ICaL_f_gate$f + _ICaL_f_gate$f_infinity)/_ICaL_f_gate$tau_f), Eq(_IKr_Xr_gate$Xr_infinity, 1.0/(exp_("
         "-0.13333333333333333*_cell$V - 6.6666666666666667) + 1.0)), Eq(_IKr_Xr_gate$tau_Xr, 1.0/(0.00060999999999999"
         "997*(_cell$V + 10.0)/(exp_(0.14499999999999999*_cell$V + 1.4499999999999999) - 1.0) + 0.0013799999999999999*"
         "(_cell$V + 7.0)/(1.0 - exp_(-0.123*_cell$V - 0.86099999999999999)))), Eq(Derivative(_IKr_Xr_gate$Xr, _enviro"
         "nment$time), (-_IKr_Xr_gate$Xr + _IKr_Xr_gate$Xr_infinity)/_IKr_Xr_gate$tau_Xr), Eq(_IKs_Xs_gate$Xs_infinity"
         ", 1.0/(exp_(0.08982035928143713 - 0.059880239520958086*_cell$V) + 1.0)), Eq(_IKs_Xs_gate$tau_Xs, 1.0/(0.0001"
         "3100000000000001*(_cell$V + 30.0)/(exp_(0.068699999999999997*_cell$V + 2.0609999999999999) - 1.0) + 7.189999"
         "9999999999e-5*(_cell$V + 30.0)/(1.0 - exp_(-0.14799999999999999*_cell$V - 4.4399999999999998)))), Eq(Derivat"
         "ive(_IKs_Xs_gate$Xs, _environment$time), (-_IKs_Xs_gate$Xs + _IKs_Xs_gate$Xs_infinity)/_IKs_Xs_gate$tau_Xs),"
         " Eq(_INa_h_gate$alpha_h, Piecewise((0.13500000000000001*exp_(0.14705882352941177*_INa$shift_INa_inact - 0.14"
         "705882352941177*_cell$V - 11.764705882352941), _cell$V < -40.0), (0, True))), Eq(_INa_h_gate$beta_h, Piecewi"
         "se((310000.0*exp_(-0.34999999999999998*_INa$shift_INa_inact + 0.34999999999999998*_cell$V) + 3.5600000000000"
         "001*exp_(-0.079000000000000001*_INa$shift_INa_inact + 0.079000000000000001*_cell$V), _cell$V < -40.0), (7.69"
         "2307692307692/(exp_(0.090090090090090093*_INa$shift_INa_inact - 0.090090090090090093*_cell$V - 0.96036036036"
         "03604) + 1.0), True))), Eq(_INa_h_gate$h_infinity, 0.01*_INa$perc_reduced_inact_for_IpNa + _INa_h_gate$alpha"
         "_h*(1.0 - 0.01*_INa$perc_reduced_inact_for_IpNa)/(_INa_h_gate$alpha_h + _INa_h_gate$beta_h)), Eq(_INa_h_gate"
         "$tau_h, 1.0/(_INa_h_gate$alpha_h + _INa_h_gate$beta_h)), Eq(Derivative(_INa_h_gate$h, _environment$time), (-"
         "_INa_h_gate$h + _INa_h_gate$h_infinity)/_INa_h_gate$tau_h), Eq(_INa_j_gate$alpha_j, Piecewise((1.0*(_cell$V "
         "+ 37.780000000000001)*(-127140.0*exp_(-0.24440000000000001*_INa$shift_INa_inact + 0.24440000000000001*_cell$"
         "V) - 3.4740000000000003e-5*exp_(0.043909999999999998*_INa$shift_INa_inact - 0.043909999999999998*_cell$V))/("
         "exp_(-0.311*_INa$shift_INa_inact + 0.311*_cell$V + 24.640530000000001) + 1.0), _cell$V < -40.0), (0, True)))"
         ", Eq(_INa_j_gate$beta_j, Piecewise((0.1212*exp_(0.01052*_INa$shift_INa_inact - 0.01052*_cell$V)/(exp_(0.1378"
         "0000000000001*_INa$shift_INa_inact - 0.13780000000000001*_cell$V - 5.5312920000000003) + 1.0), _cell$V < -40"
         ".0), (0.29999999999999999*exp_(2.5349999999999999e-7*_INa$shift_INa_inact - 2.5349999999999999e-7*_cell$V)/("
         "exp_(0.10000000000000001*_INa$shift_INa_inact - 0.10000000000000001*_cell$V - 3.2000000000000002) + 1.0), Tr"
         "ue))), Eq(_INa_j_gate$j_infinity, 0.01*_INa$perc_reduced_inact_for_IpNa + _INa_j_gate$alpha_j*(1.0 - 0.01*_I"
         "Na$perc_reduced_inact_for_IpNa)/(_INa_j_gate$alpha_j + _INa_j_gate$beta_j)), Eq(_INa_j_gate$tau_j, 1.0/(_INa"
         "_j_gate$alpha_j + _INa_j_gate$beta_j)), Eq(Derivative(_INa_j_gate$j, _environment$time), (-_INa_j_gate$j + _"
         "INa_j_gate$j_infinity)/_INa_j_gate$tau_j), Eq(_INa_m_gate$alpha_m, 0.32000000000000001*(_cell$V + 47.1300000"
         "00000003)/(1.0 - exp_(-0.10000000000000001*_cell$V - 4.7130000000000005))), Eq(_INa_m_gate$beta_m, 0.0800000"
         "00000000002*exp_(-0.090909090909090909*_cell$V)), Eq(_INa_m_gate$m_infinity, _INa_m_gate$alpha_m/(_INa_m_gat"
         "e$alpha_m + _INa_m_gate$beta_m)), Eq(_INa_m_gate$tau_m, 1.0/(_INa_m_gate$alpha_m + _INa_m_gate$beta_m)), Eq("
         "Derivative(_INa_m_gate$m, _environment$time), (-_INa_m_gate$m + _INa_m_gate$m_infinity)/_INa_m_gate$tau_m), "
         "Eq(_Itof_X_gate$X_tof_infinity, 1.0/(exp_(-0.066666666666666667*_cell$V - 0.2) + 1.0)), Eq(_Itof_X_gate$tau_"
         "X_tof, 3.5*exp_(-0.0011111111111111111*_cell$V**2.0) + 1.5), Eq(Derivative(_Itof_X_gate$X_tof, _environment$"
         "time), (-_Itof_X_gate$X_tof + _Itof_X_gate$X_tof_infinity)/_Itof_X_gate$tau_X_tof), Eq(_Itof_Y_gate$Y_tof_in"
         "finity, 1.0/(exp_(0.1*_cell$V + 3.35) + 1.0)), Eq(_Itof_Y_gate$tau_Y_tof, 20.0 + 20.0/(exp_(0.1*_cell$V + 3."
         "35) + 1.0)), Eq(Derivative(_Itof_Y_gate$Y_tof, _environment$time), (-_Itof_Y_gate$Y_tof + _Itof_Y_gate$Y_tof"
         "_infinity)/_Itof_Y_gate$tau_Y_tof), Eq(_Itos_R_gate$R_tos_infinity, 1.0/(exp_(0.1*_cell$V + 3.35) + 1.0)), E"
         "q(_Itos_R_gate$tau_R_tos, 220.0 + 2800.0/(exp_(0.1*_cell$V + 6.0) + 1.0)), Eq(Derivative(_Itos_R_gate$R_tos,"
         " _environment$time), (-_Itos_R_gate$R_tos + _Itos_R_gate$R_tos_infinity)/_Itos_R_gate$tau_R_tos), Eq(_Itos_X"
         "_gate$X_tos_infinity, 1.0/(exp_(-0.066666666666666667*_cell$V - 0.2) + 1.0)), Eq(_Itos_X_gate$tau_X_tos, 0.5"
         " + 9.0/(exp_(0.066666666666666667*_cell$V + 0.2) + 1.0)), Eq(Derivative(_Itos_X_gate$X_tos, _environment$tim"
         "e), (-_Itos_X_gate$X_tos + _Itos_X_gate$X_tos_infinity)/_Itos_X_gate$tau_X_tos), Eq(_Itos_Y_gate$Y_tos_infin"
         "ity, 1.0/(exp_(0.1*_cell$V + 3.35) + 1.0)), Eq(_Itos_Y_gate$tau_Y_tos, 30.0 + 3000.0/(exp_(0.1*_cell$V + 6.0"
         ") + 1.0)), Eq(Derivative(_Itos_Y_gate$Y_tos, _environment$time), (-_Itos_Y_gate$Y_tos + _Itos_Y_gate$Y_tos_i"
         "nfinity)/_Itos_Y_gate$tau_Y_tos)]")
