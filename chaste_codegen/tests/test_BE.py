import logging
import os
import chaste_codegen as cg
import pytest
import cellmlmanip
import chaste_codegen.tests.chaste_test_utils as test_utils

# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_dymaic_BE(tmp_path):
    """ Check generation of Cvode models against reference"""
    LOGGER.info('Converting: BE: aslanidi_model_2009\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'aslanidi_model_2009.cellml')
    chaste_model = cellmlmanip.load_model(model_file)
    chaste_model = cg.BeModel(chaste_model, 'dynamic_aslanidi_model_2009',
                              class_name='Dynamicaslanidi_model_2009FromCellMLBackwardEuler',
                              dynamically_loadable=True)
    chaste_model.generate_chaste_code()
    expected_hpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'BE', 'dynamic_aslanidi_model_2009.hpp')
    expected_cpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'BE', 'dynamic_aslanidi_model_2009.cpp')
    # Compare against reference
    test_utils.compare_model_against_reference('BE', chaste_model, tmp_path, expected_hpp_path,
                                               expected_cpp_path)

