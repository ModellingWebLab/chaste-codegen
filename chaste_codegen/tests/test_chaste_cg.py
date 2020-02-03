import logging
import os
import chaste_codegen as cg
import pytest
import cellmlmanip
from chaste_codegen.tests.chaste_test_utils import (
    load_chaste_models,
    compare_model_against_reference)


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

models = []

def model_types():
    return ['Normal', 'Opt']

def get_models():
    """ Load all models if they haven't been loaded yet"""
    try:
        return models
    except UnboundLocalError:
        models = load_chaste_models(model_types=model_types())
        return models

def chaste_normal_models():
    """ Load all Normal models"""
    return [model for model in get_models() if 'Normal' in model['reference_models'].keys()]

def chaste_opt_models():
    """ Load all Opt models"""
    return [model for model in get_models() if 'Opt' in model['reference_models'].keys()]
    
class TestChasteCG(object):
    """ Tests chaste_codegen against reference models generated with chaste_codegen and tested in chaste."""
    @pytest.mark.chaste
    @pytest.mark.parametrize(('model'), chaste_normal_models())
    def test_Normal(self, tmp_path, model):
        """ Check generation of Normal models against reference"""
        LOGGER.info('Converting: Normal: ' + model['class_name'] + '\n')
        # Generate chaste code
        chaste_model = cg.NormalChasteModel(model['model'], model['model_name_from_file'],
                                            class_name=model['class_name'])
        chaste_model.generate_chaste_code()
        # Comprare against referene
        compare_model_against_reference('Normal', chaste_model, tmp_path)

    @pytest.mark.chaste
    @pytest.mark.parametrize(('model'), chaste_opt_models())
    def test_Opt(self, tmp_path, model):
        """ Check generation of Opt models against reference"""
        # Note: currently only implemented partia eval
        LOGGER.info('Converting: Opt: ' + model['class_name'] + '\n')
        # Generate chaste code
        chaste_model = cg.OptChasteModel(model['model'], model['model_name_from_file'],
                                         class_name=model['class_name'],
                                         pe=True)
        chaste_model.generate_chaste_code()
        # Comprare against referene
        compare_model_against_reference('Opt', chaste_model, tmp_path)

    @pytest.mark.chaste
    def test_dymaic_model(self, tmp_path):
        tmp_path = str(tmp_path)
        LOGGER.info('Converting: Normal Dynamichodgkin_huxley_squid_axon_model_1952_modified\n')
        model_file = \
            os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
        chaste_model = cellmlmanip.load_model(model_file)
        chaste_model = cg.NormalChasteModel(chaste_model,
                                            'dynamic_hodgkin_huxley_squid_axon_model_1952_modified',
                                            class_name='Dynamichodgkin_huxley_squid_axon_model_1952_modifiedFromCellML',
                                            dynamically_loadable=True)
        chaste_model.generate_chaste_code()

        # Comprare against referene
        compare_model_against_reference('Normal', chaste_model, tmp_path)

    @pytest.mark.chaste
    def test_expose_annotated_variables(self, tmp_path):
        tmp_path = str(tmp_path)
        LOGGER.info('Testing expose_annotated_variables option\n')
        model_file = \
            os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'matsuoka_model_2003.cellml')
        chaste_model = cellmlmanip.load_model(model_file)

        chaste_model = cg.NormalChasteModel(chaste_model,
                                            'expose_annotated_variables_cellmatsuoka_model_2003',
                                            class_name='Cellmatsuoka_model_2003FromCellML',
                                            expose_annotated_variables=True)

        chaste_model.generate_chaste_code()

        # Comprare against referene
        compare_model_against_reference('Normal', chaste_model, tmp_path)

    @pytest.mark.chaste
    def test_missing_capacitance(self, tmp_path):
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

    @pytest.mark.chaste
    def test_wrong_units_time(self, capsys, tmp_path):
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

    @pytest.mark.chaste
    def test_wrong_units_voltage(self, capsys, tmp_path):
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
