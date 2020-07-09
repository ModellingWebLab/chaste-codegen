import logging
import os

import pytest
from chaste_codegen.model_with_conversions import load_model
from cellmlmanip.rdf import create_rdf_node

import chaste_codegen as cg
from chaste_codegen._rdf import (
    BQBIOL,
    OXMETA,
    PRED_IS,
    PRED_IS_VERSION_OF,
    get_variables_transitively,
)


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.fixture(scope='session')
def s_model():
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'Shannon2004.cellml')
    return load_model(model_folder)


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
    assert str(all_currents) == ("[_cell$i_Stim, _INa$i_Na, _IKr$i_Kr, _IKs$i_Ks, _Itos$i_tos, _IK1$i_K1, _ICaL$i_CaL,"
                                 " _INaCa$i_NaCa, _Jrel_SR$j_rel_SR]")
