import os

import pytest
from cellmlmanip import load_model

from chaste_codegen import DATA_DIR, load_model_with_conversions


cellml_folder = os.path.join(DATA_DIR, 'tests', 'cellml')


@pytest.fixture(scope='session')
def s_model():
    return load_model(os.path.join(cellml_folder, 'Shannon2004.cellml'))


@pytest.fixture(scope='session')
def be_model():
    return load_model(os.path.join(cellml_folder, 'beeler_reuter_model_1977.cellml'))


@pytest.fixture(scope='session')
def hh_model():
    model_name = os.path.join(cellml_folder, 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
    return load_model_with_conversions(model_name, fix_singularities=False)
