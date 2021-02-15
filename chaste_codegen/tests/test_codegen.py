import os

import cellmlmanip
import pytest
import sympy as sp
from cellmlmanip.rdf import create_rdf_node

import chaste_codegen as cg
from chaste_codegen import (
    LOGGER,
    CodegenError,
    add_conversions,
    load_model_with_conversions,
)
from chaste_codegen._rdf import OXMETA
from chaste_codegen.tests.conftest import (
    CELLML_FOLDER,
    TESTS_FOLDER,
    cache_model,
    compare_model_against_reference,
    load_chaste_models,
)


def get_models(ref_folder='chaste_reference_models', type='Normal'):
    """ Load all models if they haven't been loaded yet"""
    return load_chaste_models(model_types=[type], reference_folder=ref_folder)


chaste_normal_models = get_models(ref_folder='chaste_reference_models', type='Normal')
chaste_opt_models = get_models(ref_folder='chaste_reference_models', type='Opt')
chaste_cvode_models = get_models(ref_folder='chaste_reference_models', type='Cvode')
chaste_cvode_models_with_jacobians = get_models(ref_folder='chaste_reference_models', type='Cvode_with_jacobian')
chaste_cvode_opt_models = get_models(ref_folder='chaste_reference_models', type='Cvode_opt')
chaste_cvode_opt_models_with_jacobians = get_models(ref_folder='chaste_reference_models',
                                                    type='Cvode_opt_with_jacobian')
chaste_BE = get_models(ref_folder='chaste_reference_models', type='BE')
chaste_BEopt = get_models(ref_folder='chaste_reference_models', type='BEopt')
chaste_RL = get_models(ref_folder='chaste_reference_models', type='RL')
chaste_RLopt = get_models(ref_folder='chaste_reference_models', type='RLopt')
chaste_GRL1 = get_models(ref_folder='chaste_reference_models', type='GRL1')
chaste_GRL1Opt = get_models(ref_folder='chaste_reference_models', type='GRL1Opt')
chaste_GRL2 = get_models(ref_folder='chaste_reference_models', type='GRL2')
chaste_GRL2Opt = get_models(ref_folder='chaste_reference_models', type='GRL2Opt')
chaste_CVODE_DATA_CLAMP = get_models(ref_folder='chaste_reference_models', type='CVODE_DATA_CLAMP')
chaste_CVODE_DATA_CLAMP_OPT = get_models(ref_folder='chaste_reference_models', type='CVODE_DATA_CLAMP_OPT')


cg.__version__ = "(version omitted as unimportant)"
cg.chaste_model.TIME_STAMP = "(date omitted as unimportant)"


@pytest.mark.parametrize(('model'), chaste_cvode_opt_models_with_jacobians)
def test_Cvode_opt_jacobian(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLCvodeOpt'
    LOGGER.info('Converting: Cvode opt with jacobian: ' + class_name + ' with jacobian\n')
    # Generate chaste code
    with cg.OptCvodeChasteModel(cache_model(model['model']), model['model_name_from_file'], class_name=class_name,
                                use_analytic_jacobian=True) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_cvode_opt_models)
def test_Cvode_opt(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLCvodeOpt'
    LOGGER.info('Converting: Cvode opt: ' + class_name + '\n')
    # Generate chaste code
    with cg.OptCvodeChasteModel(cache_model(model['model']), model['model_name_from_file'],
                                class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_CVODE_DATA_CLAMP)
def test_CVODE_DATA_CLAMP(tmp_path, model):
    """ Check generation of CVODE with Data Clamp models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLCvodeDataClamp'
    LOGGER.info('Converting: CVODE with Data Clamp: ' + class_name + '\n')
    # Generate chaste code
    with cg.CvodeChasteModel(cache_model(model['model']), model['model_name_from_file'], class_name=class_name,
                             cvode_data_clamp=True) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_CVODE_DATA_CLAMP_OPT)
def test_CVODE_DATA_CLAMP_OPT(tmp_path, model):
    """ Check generation of CVODE with Data Clamp opt models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLCvodeDataClampOpt'
    LOGGER.info('Converting: CVODE with Data Clamp opt: ' + class_name + '\n')
    # Generate chaste code
    with cg.OptCvodeChasteModel(cache_model(model['model']), model['model_name_from_file'], class_name=class_name,
                                cvode_data_clamp=True) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_GRL2Opt)
def test_GRL2Opt(tmp_path, model):
    """ Check generation of Generalised Rush Larsen Second order Opt models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLGRL2Opt'
    LOGGER.info('Converting: Generalised Rush Larsen: ' + class_name + '\n')
    # Generate chaste code
    with cg.GeneralisedRushLarsenSecondOrderModelOpt(cache_model(model['model']), model['model_name_from_file'],
                                                     class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_GRL2)
def test_GRL2(tmp_path, model):
    """ Check generation of Generalised Rush Larsen Second order models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLGRL2'
    LOGGER.info('Converting: Generalised Rush Larsen: ' + class_name + '\n')
    # Generate chaste code
    with cg.GeneralisedRushLarsenSecondOrderModel(cache_model(model['model']), model['model_name_from_file'],
                                                  class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_GRL1Opt)
def test_GRL1Opt(tmp_path, model):
    """ Check generation of Generalised Rush Larsen First order Opt models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLGRL1Opt'
    LOGGER.info('Converting: Generalised Rush Larsen: ' + class_name + '\n')
    # Generate chaste code
    with cg.GeneralisedRushLarsenFirstOrderModelOpt(cache_model(model['model']), model['model_name_from_file'],
                                                    class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_GRL1)
def test_GRL1(tmp_path, model):
    """ Check generation of Generalised Rush Larsen First order models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLGRL1'
    LOGGER.info('Converting: Generalised Rush Larsen: ' + class_name + '\n')
    # Generate chaste code
    with cg.GeneralisedRushLarsenFirstOrderModel(cache_model(model['model']), model['model_name_from_file'],
                                                 class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_RLopt)
def test_RLopt(tmp_path, model):
    """ Check generation of Rush Larsen Opt models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLRushLarsenOpt'
    LOGGER.info('Converting: RushLarsen Opt: ' + class_name + '\n')
    # Generate chaste code
    with cg.RushLarsenOptModel(cache_model(model['model']), model['model_name_from_file'],
                               class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_RL)
def test_RL(tmp_path, model):
    """ Check generation of Rush Larsen models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLRushLarsen'
    LOGGER.info('Converting: RushLarsen: ' + class_name + '\n')
    # Generate chaste code
    with cg.RushLarsenModel(cache_model(model['model']), model['model_name_from_file'],
                            class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_BEopt)
def test_BEopt(tmp_path, model):
    """ Check generation of Backwards Euler opt models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLBackwardEuler'
    LOGGER.info('Converting: BE opt: ' + class_name + '\n')
    # Generate chaste code
    with cg.BackwardEulerOptModel(cache_model(model['model']), model['model_name_from_file'],
                                  class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_BE)
def test_BE(tmp_path, model):
    """ Check generation of Backwards Euler models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLBackwardEulerNoLut'
    LOGGER.info('Converting: BE: ' + class_name + '\n')
    # Generate chaste code
    with cg.BackwardEulerModel(cache_model(model['model']), model['model_name_from_file'],
                               class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_cvode_models_with_jacobians)
def test_Cvode_jacobian(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLCvode'
    LOGGER.info('Converting: Cvode: ' + class_name + ' with jacobian\n')
    # Generate chaste code
    with cg.CvodeChasteModel(cache_model(model['model']), model['model_name_from_file'],
                             class_name=class_name, use_analytic_jacobian=True) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_cvode_models)
def test_Cvode(tmp_path, model):
    """ Check generation of Cvode models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLCvode'
    LOGGER.info('Converting: Cvode: ' + class_name + '\n')
    # Generate chaste code
    with cg.CvodeChasteModel(cache_model(model['model']), model['model_name_from_file'],
                             class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_normal_models)
def test_Normal(tmp_path, model):
    """ Check generation of Normal models against reference"""
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellML'
    LOGGER.info('Converting: Normal: ' + class_name + '\n')
    # Generate chaste code
    with cg.NormalChasteModel(cache_model(model['model']), model['model_name_from_file'],
                              class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


@pytest.mark.parametrize(('model'), chaste_opt_models)
def test_Opt(tmp_path, model):
    """ Check generation of Opt models against reference"""
    # Note: currently only implemented partial eval
    class_name = 'Cell' + model['model_name_from_file'] + 'FromCellMLOpt'
    LOGGER.info('Converting: Opt: ' + class_name + '\n')
    # Generate chaste code
    with cg.OptChasteModel(cache_model(model['model']), model['model_name_from_file'],
                           class_name=class_name) as chaste_model:
        chaste_model.generate_chaste_code()
        # Compare against reference
        compare_model_against_reference(chaste_model, tmp_path, model['expected_hpp_path'], model['expected_cpp_path'])


def test_chaste_model_base_class(tmp_path):
    """ Check the base class ChasteModel behaves as expected"""
    LOGGER.info('Testing ChasteModel base class\n')
    model_file = \
        os.path.join(CELLML_FOLDER, 'luo_rudy_1994.cellml')

    with cg.ChasteModel(cache_model(model_file), 'luo_rudy_1994',
                        class_name='Cellluo_rudy_1994FromCellML') as chaste_model:
        chaste_model._hpp_template = 'normal_model.hpp'
        chaste_model._cpp_template = 'normal_model.cpp'
        chaste_model._vars_for_template['base_class'] = 'AbstractCardiacCell'
        chaste_model._vars_for_template['model_type'] = 'Normal'
        chaste_model.generate_chaste_code()

        reference = os.path.join(TESTS_FOLDER, 'chaste_reference_models', 'Normal')

        compare_model_against_reference(chaste_model, tmp_path, os.path.join(reference, 'luo_rudy_1994.hpp'),
                                        os.path.join(reference, 'luo_rudy_1994.cpp'))


def test_missing_V():
    LOGGER.info('Testing missing Voltage metadata tag\n')
    model_file = \
        os.path.join(CELLML_FOLDER, 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
    chaste_model = cellmlmanip.load_model(model_file)

    # Remove membrane_voltage metadata tag
    voltage = chaste_model.get_variable_by_ontology_term((OXMETA, 'membrane_voltage'))
    chaste_model.rdf.remove((voltage.rdf_identity, None, None))

    with pytest.raises(CodegenError, match='Voltage not tagged in the model!'):
        add_conversions(chaste_model)


def test_missing_capacitance():
    LOGGER.info('Testing missing capacitance\n')
    model_file = \
        os.path.join(CELLML_FOLDER, 'pandit_clark_giles_demir_2001_epicardial_cell.cellml')
    chaste_model = cellmlmanip.load_model(model_file)

    # Remove capacitance metadata tag
    capacitance = chaste_model.get_variable_by_ontology_term((OXMETA, 'membrane_capacitance'))
    chaste_model.rdf.remove((capacitance.rdf_identity, None, None))

    with pytest.raises(CodegenError, match='Membrane capacitance is required to be able to apply conversion '
                                           'to stimulus current!'):
        add_conversions(chaste_model)


def test_no_time():
    LOGGER.info('Testing missing time\n')
    model_file = \
        os.path.join(CELLML_FOLDER, '..', '..', 'test_no_odes.cellml')

    chaste_model = cellmlmanip.load_model(model_file)

    with pytest.raises(CodegenError, match=r"The model has no free variable \(time\)!"):
        add_conversions(chaste_model)


def test_wrong_units_time():
    LOGGER.info('Testing wrong units for time\n')
    model_file = \
        os.path.join(CELLML_FOLDER, '..', '..', 'test_wrong_units_time_odes.cellml')

    with pytest.raises(CodegenError, match=(r"Incorrect definition of free variable \(time\): "
                                            "time needs to be dimensionally equivalent to second!")):
        load_model_with_conversions(model_file)


def test_wrong_units_voltage():
    LOGGER.info('Testing wrong units for Voltage\n')
    model_file = \
        os.path.join(CELLML_FOLDER, '..', '..', 'test_wrong_units_voltage.cellml')

    with pytest.raises(CodegenError, match=("Incorrect definition of membrane_voltage variable: "
                                            "units of membrane_voltage need to be dimensionally equivalent to Volt")):
        load_model_with_conversions(model_file)


def test_other_current_in_wrong_units():
    LOGGER.info('Testing that conversion of currents in inconvertible units gets skipped\n')
    model_file = \
        os.path.join(CELLML_FOLDER, 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
    chaste_model = cellmlmanip.load_model(model_file)

    PRED_IS = create_rdf_node(('http://biomodels.net/biology-qualifiers/', 'is'))  # is_a for tagging variables
    chaste_model.units.add_unit('uA', 'ampere / 1e6')  # add uA unit to model

    # add new variable to tags membrane_sodium_potassium_pump_current and membrane_potassium_pump_current
    membrane_sodium_potassium_pump_current = \
        chaste_model.add_variable('current1', 'dimensionless', cmeta_id='membrane_sodium_potassium_pump_current')
    membrane_potassium_pump_current = chaste_model.add_variable('current2', 'uA',
                                                                cmeta_id='membrane_potassium_pump_current')

    # tag new variables
    chaste_model.rdf.add((membrane_sodium_potassium_pump_current.rdf_identity, PRED_IS,
                          create_rdf_node((OXMETA, 'membrane_sodium_potassium_pump_current'))))
    chaste_model.rdf.add((membrane_potassium_pump_current.rdf_identity, PRED_IS,
                          create_rdf_node((OXMETA, 'membrane_potassium_pump_current'))))

    # add initial value equations
    chaste_model.add_equation(sp.Eq(membrane_sodium_potassium_pump_current, 0.0))
    chaste_model.add_equation(sp.Eq(membrane_potassium_pump_current, 0.0))

    # check we can get our new variables by rdf tag
    assert membrane_sodium_potassium_pump_current == \
        chaste_model.get_variable_by_ontology_term((OXMETA, 'membrane_sodium_potassium_pump_current'))
    assert membrane_potassium_pump_current == \
        chaste_model.get_variable_by_ontology_term((OXMETA, 'membrane_potassium_pump_current'))

    add_conversions(chaste_model)
    # generate code
    generated_model = cg.NormalChasteModel(chaste_model, 'test_other_current_in_wrong_units',
                                           class_name='test_other_current_in_wrong_units')

    # re-retrieve (possibly converted) vars
    membrane_sodium_potassium_pump_current == \
        chaste_model.get_variable_by_ontology_term((OXMETA, 'membrane_sodium_potassium_pump_current'))
    membrane_potassium_pump_current = \
        chaste_model.get_variable_by_ontology_term((OXMETA, 'membrane_potassium_pump_current'))

    # check the model derived quantities has membrane_potassium_pump_current and membrane_sodium_potassium_pump_current
    assert membrane_sodium_potassium_pump_current in generated_model._derived_quant
    assert membrane_potassium_pump_current in generated_model._derived_quant

    # check units only converted where possible
    assert str(membrane_sodium_potassium_pump_current.units) == 'dimensionless'
    assert membrane_potassium_pump_current.units == generated_model._model.conversion_units.get_unit('uA_per_cm2')


def test_stimulus_not_tagged():
    """ Check untagged stimulus with time in it throws an error"""
    LOGGER.info('Testing untagged stimulus\n')
    model_file = \
        os.path.join(CELLML_FOLDER, 'luo_rudy_1994.cellml')

    chaste_model = cellmlmanip.load_model(model_file)

    # Remove membrane_stimulus_current metadata tag
    stim = chaste_model.get_variable_by_ontology_term((OXMETA, 'membrane_stimulus_current'))
    chaste_model.rdf.remove((stim.rdf_identity, None, None))

    with pytest.raises(CodegenError, match='Ionic variables should not be a function of time. '
                                           'This is often caused by missing membrane_stimulus_current tag.'):
        add_conversions(chaste_model)
