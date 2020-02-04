import logging
import os
import chaste_codegen as cg
import pytest
import cellmlmanip
import chaste_codegen.tests.chaste_test_utils as test_utils


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

def get_models():
    """ Load all models if they haven't been loaded yet"""
    if not test_utils.models:
        test_utils.models = test_utils.load_chaste_models(model_types=['Normal', 'Opt'], reference_folder='cronjob_reference_models')
    return test_utils.models
 
 
def chaste_normal_models():
    """ Load all Normal models"""
    return [model for model in get_models() if model['model_type'] == 'Normal']


def chaste_opt_models():
    """ Load all Opt models"""
    return [model for model in get_models() if model['model_type'] == 'Opt']

@pytest.mark.slow
@pytest.mark.parametrize(('model'), chaste_normal_models())
def test_Normal(tmp_path, model):
    """ Check generation of Normal models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellML'
    LOGGER.info('Converting: Normal: ' + class_name + '\n')
    # Generate chaste code
    chaste_model = cg.NormalChasteModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                                        class_name=class_name)
    chaste_model.generate_chaste_code()
    # Comprare against referene
    test_utils.compare_model_against_reference('Normal', chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])

@pytest.mark.slow
@pytest.mark.parametrize(('model'), chaste_opt_models())
def test_Opt(tmp_path, model):
    """ Check generation of Opt models against reference"""
    # Note: currently only implemented partia eval
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellML'
    LOGGER.info('Converting: Opt: ' + class_name + '\n')
    # Generate chaste code
    chaste_model = cg.OptChasteModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                                     class_name=class_name,
                                     pe=True)
    chaste_model.generate_chaste_code()
    # Comprare against referene
    test_utils.compare_model_against_reference('Opt', chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])