import logging
import os

import pytest
from cellmlmanip import load_model

import chaste_codegen as cg
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


def test_wrong_params():
    with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
        partial_eval(None, None)


def test_wrong_params2():
    with pytest.raises(AssertionError, match="Equations to be a collection of equations"):
        partial_eval([1], [2])


def test_wrong_params3(derivatives_eqs):
    with pytest.raises(AssertionError, match="Expecting required_lhs to be a collection of variables or Derivatives"):
        partial_eval(derivatives_eqs, [2])


def test_partial_eval(state_vars, derivatives_eqs):
    lhs_to_keep = [eq.lhs for eq in derivatives_eqs if len(eq.lhs.args) > 0 and eq.lhs.args[0] in state_vars]
    assert len(derivatives_eqs) == 22
    derivatives_eqs = partial_eval(derivatives_eqs, lhs_to_keep, keep_multiple_usages=False)
    len(derivatives_eqs) == 4
    assert str(derivatives_eqs) == \
        ("[Eq(Derivative(_potassium_channel_n_gate$n, _environment$time), -0.125*_potassium_channel_n_gate$n*exp_(0.01"
         "25*_membrane$V + 0.9375) - 0.01*(1.0 - _potassium_channel_n_gate$n)*(_membrane$V + 65.0)/(exp_(-0.1*_membran"
         "e$V - 6.5) - 1.0)), Eq(Derivative(_sodium_channel_h_gate$h, _environment$time), -1.0*_sodium_channel_h_gate$"
         "h/(exp_(-0.1*_membrane$V - 4.5) + 1.0) + 0.070000000000000007*(1.0 - _sodium_channel_h_gate$h)*exp_(-0.05*_m"
         "embrane$V - 3.75)), Eq(Derivative(_sodium_channel_m_gate$m, _environment$time), -4.0*_sodium_channel_m_gate$"
         "m*exp_(-0.055555555555555556*_membrane$V - 4.1666666666666667) - 0.10000000000000001*(1.0 - _sodium_channel_"
         "m_gate$m)*(_membrane$V + 50.0)/(exp_(-0.1*_membrane$V - 5.0) - 1.0)), Eq(Derivative(_membrane$V, _environmen"
         "t$time), -36.0*_potassium_channel_n_gate$n**4.0*(_membrane$V + 87.0) - 120.0*_sodium_channel_m_gate$m**3.0*_"
         "sodium_channel_h_gate$h*(_membrane$V - 40.0) - 0.29999999999999999*_membrane$V - 1.0*Piecewise((-20.0, (_env"
         "ironment$time >= 10.0) & (_environment$time <= 10.5)), (0, True)) - 19.316099999999999)]")
