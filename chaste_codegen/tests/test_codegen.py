import logging
import os
import sys

import cellmlmanip
import pytest

import chaste_codegen as cg
import chaste_codegen.tests.chaste_test_utils as test_utils


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def get_models(ref_folder='chaste_reference_models', type='Normal'):
    """ Load all models if they haven't been loaded yet"""
    return test_utils.load_chaste_models(model_types=[type], reference_folder=ref_folder)


chaste_normal_models = get_models(ref_folder='chaste_reference_models', type='Normal')
chaste_opt_models = get_models(ref_folder='chaste_reference_models', type='Opt')
chaste_cvode_models = get_models(ref_folder='chaste_reference_models', type='Cvode')
chaste_cvode_models_with_jacobians = get_models(ref_folder='chaste_reference_models', type='Cvode_with_jacobian')
chaste_BE = get_models(ref_folder='chaste_reference_models', type='BE')
chaste_RL = get_models(ref_folder='chaste_reference_models', type='RL')
chaste_RLopt = get_models(ref_folder='chaste_reference_models', type='RLopt')


@pytest.mark.parametrize(('model'), chaste_RLopt)
def test_RLopt(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLRushLarsen'
    LOGGER.info('Converting: RLopt: ' + class_name + '\n')
    # Generate chaste code
    chaste_model = cg.RlOptModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                                 class_name=class_name)

    chaste_model.generate_chaste_code()
    # Compare against reference
    test_utils.compare_model_against_reference('RLopt', chaste_model,
                                               tmp_path, model['expected_hpp_path'],
                                               model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_RL)
def test_RL(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLRushLarsen'
    LOGGER.info('Converting: RL: ' + class_name + '\n')
    # Generate chaste code
    chaste_model = cg.RlModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                              class_name=class_name)

    chaste_model.generate_chaste_code()
    # Compare against reference
    test_utils.compare_model_against_reference('RL', chaste_model,
                                               tmp_path, model['expected_hpp_path'],
                                               model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_BE)
def test_BE(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLBackwardEuler'
    LOGGER.info('Converting: BE: ' + class_name + '\n')
    # Generate chaste code
    chaste_model = cg.BeModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                              class_name=class_name)

    chaste_model.generate_chaste_code()
    # Compare against reference
    test_utils.compare_model_against_reference('BE', chaste_model,
                                               tmp_path, model['expected_hpp_path'],
                                               model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_cvode_models_with_jacobians)
def test_Cvode_jacobian(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLCvode'
    LOGGER.info('Converting: Cvode: ' + class_name + ' with jacobian\n')
    # Generate chaste code
    chaste_model = cg.CvodeChasteModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                                       class_name=class_name, use_analytic_jacobian=True)
    chaste_model.generate_chaste_code()
    # check if we are python 3.5 (< 3.6) and there is a different version of the reference
    expected_cpp_path = model['expected_cpp_path']
    assert sys.version_info.major == 3
    if sys.version_info.minor < 6 and os.path.isfile(expected_cpp_path + '_3.5'):
        expected_cpp_path += '_3.5'

    # Compare against reference
    test_utils.compare_model_against_reference('Cvode_with_jacobian', chaste_model,
                                               tmp_path, model['expected_hpp_path'],
                                               expected_cpp_path)


@pytest.mark.parametrize(('model'), chaste_cvode_models)
def test_Cvode(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    # Note: currently only implemented partia eval
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLCvode'
    LOGGER.info('Converting: Cvode: ' + class_name + '\n')
    # Generate chaste code
    chaste_model = cg.CvodeChasteModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                                       class_name=class_name)
    chaste_model.generate_chaste_code()
    # Compare against reference
    test_utils.compare_model_against_reference('Cvode', chaste_model, tmp_path, model['expected_hpp_path'],
                                               model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_normal_models)
def test_Normal(tmp_path, model):
    """ Check generation of Normal models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellML'
    LOGGER.info('Converting: Normal: ' + class_name + '\n')
    # Generate chaste code
    chaste_model = cg.NormalChasteModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                                        class_name=class_name)
    chaste_model.generate_chaste_code()
    # Compare against reference
    test_utils.compare_model_against_reference('Normal', chaste_model, tmp_path, model['expected_hpp_path'],
                                               model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_opt_models)
def test_Opt(tmp_path, model):
    """ Check generation of Opt models against reference"""
    # Note: currently only implemented partia eval
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellML'
    LOGGER.info('Converting: Opt: ' + class_name + '\n')
    # Generate chaste code
    chaste_model = cg.OptChasteModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                                     class_name=class_name)
    chaste_model.generate_chaste_code()
    # Compare against reference
    test_utils.compare_model_against_reference('Opt', chaste_model, tmp_path, model['expected_hpp_path'],
                                               model['expected_cpp_path'])


def test_dymaic_model(tmp_path):
    tmp_path = str(tmp_path)
    LOGGER.info('Converting: Normal Dynamic luo_rudy_1994\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'luo_rudy_1994.cellml')
    chaste_model = cellmlmanip.load_model(model_file)
    chaste_model = cg.NormalChasteModel(chaste_model,
                                        'dynamic_luo_rudy_1994',
                                        class_name='Dynamicluo_rudy_1994FromCellML',
                                        dynamically_loadable=True)
    chaste_model.generate_chaste_code()
    expected_hpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Normal', 'dynamic_luo_rudy_1994.hpp')
    expected_cpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Normal', 'dynamic_luo_rudy_1994.cpp')
    # Compare against reference
    test_utils.compare_model_against_reference('Normal', chaste_model, tmp_path, expected_hpp_path,
                                               expected_cpp_path)


def test_dymaic_cvode(tmp_path):
    tmp_path = str(tmp_path)
    LOGGER.info('Converting: CVODE Dynamic luo_rudy_1994\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'luo_rudy_1994.cellml')
    chaste_model = cellmlmanip.load_model(model_file)
    chaste_model = cg.CvodeChasteModel(chaste_model,
                                       'dynamic_luo_rudy_1994',
                                       class_name='Dynamicluo_rudy_1994FromCellMLCvode',
                                       dynamically_loadable=True)
    chaste_model.generate_chaste_code()
    expected_hpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Cvode', 'dynamic_luo_rudy_1994.hpp')
    expected_cpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Cvode', 'dynamic_luo_rudy_1994.cpp')
    # Compare against reference
    test_utils.compare_model_against_reference('Cvode', chaste_model, tmp_path, expected_hpp_path,
                                               expected_cpp_path)


def test_dynamic_BE(tmp_path):
    tmp_path = str(tmp_path)
    LOGGER.info('Converting: BE Dynamic luo_rudy_1994\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'luo_rudy_1994.cellml')
    chaste_model = cellmlmanip.load_model(model_file)
    chaste_model = cg.BeModel(chaste_model,
                              'dynamic_luo_rudy_1994',
                              class_name='Dynamicluo_rudy_1994FromCellMLBackwardEuler',
                              dynamically_loadable=True)
    chaste_model.generate_chaste_code()
    expected_hpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'BE', 'dynamic_luo_rudy_1994.hpp')
    expected_cpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'BE', 'dynamic_luo_rudy_1994.cpp')
    # Compare against reference
    test_utils.compare_model_against_reference('BE', chaste_model, tmp_path, expected_hpp_path,
                                               expected_cpp_path)


def test_dynamic_RL(tmp_path):
    tmp_path = str(tmp_path)
    LOGGER.info('Converting: RL Dynamic luo_rudy_1994\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'luo_rudy_1994.cellml')
    chaste_model = cellmlmanip.load_model(model_file)
    chaste_model = cg.RlModel(chaste_model,
                              'dynamic_luo_rudy_1994',
                              class_name='Dynamicluo_rudy_1994FromCellMLRushLarsen',
                              dynamically_loadable=True)
    chaste_model.generate_chaste_code()
    expected_hpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'RL', 'dynamic_luo_rudy_1994.hpp')
    expected_cpp_path = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'RL', 'dynamic_luo_rudy_1994.cpp')
    # Compare against reference
    test_utils.compare_model_against_reference('RL', chaste_model, tmp_path, expected_hpp_path,
                                               expected_cpp_path)


def testexpose_annotated_variables(tmp_path):
    tmp_path = str(tmp_path)
    LOGGER.info('Testing expose_annotated_variables option\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'aslanidi_model_2009.cellml')
    chaste_model = cellmlmanip.load_model(model_file)

    chaste_model = cg.NormalChasteModel(chaste_model,
                                        'expose_annotated_variables_cellaslanidi_model_2009',
                                        class_name='Cellaslanidi_model_2009FromCellML',
                                        expose_annotated_variables=True)

    chaste_model.generate_chaste_code()
    expected_hpp_path = os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Normal',
                                     'expose_annotated_variables_cellaslanidi_model_2009.hpp')
    expected_cpp_path = os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Normal',
                                     'expose_annotated_variables_cellaslanidi_model_2009.cpp')
    # Compare against reference
    test_utils.compare_model_against_reference('Normal', chaste_model, tmp_path,
                                               expected_hpp_path, expected_cpp_path)


def test_missing_capacitance(tmp_path):
    tmp_path = str(tmp_path)
    LOGGER.info('Testing missing capacitance\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'pandit_model_2001_epi_old_no_capacitance.cellml')
    chaste_model = cellmlmanip.load_model(model_file)

    with pytest.raises(AssertionError) as error:
        chaste_model = cg.NormalChasteModel(chaste_model,
                                            'pandit_model_2001_epi_old_no_capacitance',
                                            class_name='pandit_model_2001_epi_old_no_capacitance')
    assert str(error.value) == \
        'Membrane capacitance is required to be able to apply conversion to stimulus current!'


def test_wrong_units_time(capsys, tmp_path):
    tmp_path = str(tmp_path)
    LOGGER.info('Testing wrong units for time\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'test_wrong_units_time_odes.cellml')
    chaste_model = cellmlmanip.load_model(model_file)

    with pytest.raises(AssertionError) as error:
        chaste_model = cg.NormalChasteModel(chaste_model,
                                            'test_wrong_units_time_odes',
                                            class_name='test_wrong_units_time_odes')
    warning = 'Incorrect definition of time variable (time needs to be dimensionally equivalent to second)'
    assert str(error.value) == warning


def test_wrong_units_voltage(capsys, tmp_path):
    tmp_path = str(tmp_path)
    LOGGER.info('Testing wrong units for time\n')
    model_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'test_wrong_units_voltage.cellml')
    chaste_model = cellmlmanip.load_model(model_file)

    with pytest.raises(AssertionError) as error:
        chaste_model = cg.NormalChasteModel(chaste_model,
                                            'test_wrong_units_voltage',
                                            class_name='test_wrong_units_voltage')
    warning = \
        'Incorrect definition of membrane_voltage variable '\
        '(units of membrane_voltage needs to be dimensionally equivalent to Volt)'
    assert str(error.value) == warning
