import sys
import logging
import os
import re
import weblab_cg as cg
import pytest
from unittest import mock
import cellmlmanip
from weblab_cg._commaind_line_script import chaste_codegen
from weblab_cg.tests.chaste_test_utils import (
    load_chaste_models,
    compare_model_against_reference,
    compare_file_against_reference)


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def model_types():
    return ['Normal']


def chaste_models():
    """ Load all models"""
    return load_chaste_models(model_types=model_types())


class TestChasteCG(object):
    """ Tests weblab_cg against reference models generated with weblab_cg and tested in chaste.

    TODO: unit conversion vvia cellmlmanip once implemented"""
    _TIMESTAMP_REGEX = re.compile(r'(//! on .*\n)')

    @pytest.mark.chaste
    @pytest.mark.parametrize(('model'), chaste_models())
    def test_Normal(self, tmp_path, model):
        """ Check generation of Normal models against reference"""
        if 'Normal' in model['reference_models'].keys():
            LOGGER.info('Converting: Normal: ' + model['class_name'] + '\n')
            # Generate chaste code
            chaste_model = cg.NormalChasteModel(model['model'], model['class_name'], model['model_name_from_file'])
            chaste_model.generate_chaste_code()
            # Comprare against referene
            compare_model_against_reference('Normal', chaste_model, tmp_path)

    @pytest.mark.chaste
    def test_dymaic_model(self, tmp_path):
        tmp_path = str(tmp_path)
        LOGGER.info('Converting: Normal Dynamichodgkin_huxley_squid_axon_model_1952_modified\n')
        model_file = \
            os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
        chaste_model = cellmlmanip.load_model(model_file)
        chaste_model = cg.NormalChasteModel(chaste_model,
                                            'Dynamichodgkin_huxley_squid_axon_model_1952_modifiedFromCellML',
                                            'dynamic_hodgkin_huxley_squid_axon_model_1952_modified',
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
                                            'Cellmatsuoka_model_2003FromCellML',
                                            'expose_annotated_variables_cellmatsuoka_model_2003',
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
                                                'pandit_model_2001_epi_old_no_capacitance')
        assert str(error.value) == \
            'Membrane capacitance is required to be able to apply conversion to stimulus current!'

    @pytest.mark.chaste
    def test_script_help(self, capsys):
        testargs = ["chaste_codegen", "-h"]
        with mock.patch.object(sys, 'argv', testargs):
            try:
                chaste_codegen()
            except SystemExit:
                pass  # We expect this to print usage and exit
            captured = capsys.readouterr()
            # compare to expected
            output = str(captured.out)
            expected = open(os.path.join(cg.DATA_DIR, 'tests', 'console_sctipt_help.txt'), 'r').read()
            assert output == expected

    @pytest.mark.chaste
    def test_script_version(self, capsys):
        testargs = ["chaste_codegen", "--version"]
        with mock.patch.object(sys, 'argv', testargs):
            try:
                chaste_codegen()
            except SystemExit:
                pass  # We expect this to print usage and exit
            captured = capsys.readouterr()
            # compare to expected
            output = str(captured.out)
            assert output == 'chaste_codegen ' + cg.__version__ + '\n'

    @pytest.mark.chaste
    def test_script_convert(self, capsys, tmp_path):
        tmp_path = str(tmp_path)
        model_name = 'hodgkin_huxley_squid_axon_model_1952_modified'
        model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
        assert os.path.isfile(model_file)
        testargs = ["chaste_codegen", model_file]
        # Call commandline script
        savedPath = str(os.getcwd())
        os.chdir(tmp_path)
        with mock.patch.object(sys, 'argv', testargs):
            chaste_codegen()
        os.chdir(savedPath)
        # Check output
        reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Normal')
        compare_file_against_reference(os.path.join(reference, model_name + '.hpp'),
                                       os.path.join(tmp_path, model_name + '.hpp'))
        compare_file_against_reference(os.path.join(reference, model_name + '.cpp'),
                                       os.path.join(tmp_path, model_name + '.cpp'))

    @pytest.mark.chaste
    def test_script_class_convtype_output_dll_loadable(self, capsys, tmp_path):
        tmp_path = str(tmp_path)
        model_name = 'hodgkin_huxley_squid_axon_model_1952_modified'
        model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
        assert os.path.isfile(model_file)
        outfile = os.path.join(tmp_path, 'output_class.c')
        # Call commandline script
        testargs = ['translate', model_file, '-c', 'Chaste_CG', '-t', 'Chaste', '-o', outfile,
                    '--dynamically-loadable']
        with mock.patch.object(sys, 'argv', testargs):
            chaste_codegen()
        # Check output
        reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Normal')
        compare_file_against_reference(os.path.join(reference, 'output_class.h'),
                                       os.path.join(tmp_path, 'output_class.h'))
        compare_file_against_reference(os.path.join(reference, 'output_class.c'),
                                       os.path.join(tmp_path, 'output_class.c'))

    @pytest.mark.chaste
    def test_script_output_expose_annotated_variables(self, capsys, tmp_path):
        tmp_path = str(tmp_path)
        # Check options: -o --expose-annotated-variables
        model_name = 'matsuoka_model_2003'
        model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
        model_file = str(model_file)
        outfile = os.path.join(tmp_path, 'expose_annotated_variables_cellmatsuoka_model_2003.cpp')
        outfile = str(outfile)
        # Call commandline script
        testargs = ['translate', model_file, '-o', outfile, '--expose-annotated-variables']
        with mock.patch.object(sys, 'argv', testargs):
            chaste_codegen()
        # Check output
        model_name = 'expose_annotated_variables_cellmatsuoka_model_2003'
        reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Normal')
        compare_file_against_reference(os.path.join(reference, model_name + '.hpp'),
                                       os.path.join(tmp_path, model_name + '.hpp'))
        compare_file_against_reference(os.path.join(reference, model_name + '.cpp'),
                                       os.path.join(tmp_path, model_name + '.cpp'))
