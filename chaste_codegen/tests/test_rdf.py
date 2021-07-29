import os

import pytest
from cellmlmanip.rdf import create_rdf_node

from chaste_codegen import DATA_DIR, CodegenError, load_model_with_conversions
from chaste_codegen._rdf import (
    BQBIOL,
    OXMETA,
    PRED_IS,
    PRED_IS_VERSION_OF,
    get_variables_transitively,
)


TESTS_FOLDER = os.path.join(DATA_DIR, 'tests')


def test_namespaces():
    assert OXMETA == 'https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#'
    assert BQBIOL == 'http://biomodels.net/biology-qualifiers/'

    assert PRED_IS == create_rdf_node((BQBIOL, 'is'))
    assert PRED_IS_VERSION_OF == create_rdf_node((BQBIOL, 'isVersionOf'))


def test_wrong_params1(s_model):
    with pytest.raises(AssertionError, match="Expecting term to be a namespace tuple"):
        get_variables_transitively(s_model, None)


def test_wrong_params2():
    with pytest.raises(AssertionError, match="Expecting model to be a cellmlmanip Model"):
        get_variables_transitively(None, (OXMETA, 'IonicCurrent'))


def test_rdf(s_model):
    all_currents = get_variables_transitively(s_model, (OXMETA, 'IonicCurrent'))
    assert str(sorted(all_currents, key=str)) == \
        ('[_ICaL$i_CaL_converted, _ICab$i_Cab_converted, _ICap$i_Cap_converted, _IClb$i_Clb_converted, '
         '_IK1$i_K1_converted, _IKr$i_Kr_converted, _IKs$i_Ks_converted, _INa$i_Na_converted, _INaCa$i_NaCa_converted,'
         ' _INab$i_Nab_converted, _Itof$i_tof_converted, _Itos$i_tos_converted, _Jrel_SR$j_rel_SR, '
         '_cell$i_Stim_converted]'), str(sorted(all_currents, key=str))


def test_rdf_error():
    model_name = os.path.join(TESTS_FOLDER, 'rdf_error_TenTusscher2006Epi.cellml')
    with pytest.raises(CodegenError, match='does not refer to any existing variable in the model.'):
        load_model_with_conversions(model_name)
