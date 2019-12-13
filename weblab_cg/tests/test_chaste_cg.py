import logging
import os
import re
import weblab_cg as cg
import pytest
import cellmlmanip
from weblab_cg.tests.chaste_test_utils import load_chaste_models, get_file_lines, write_file


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
    def test_generate_chaste_model(self, tmp_path, model):
        """ Check generation of Normal models against reference"""
        tmp_path = str(tmp_path)

        for model_type in model['reference_models'].keys():
            LOGGER.info('Converting: ' + model_type + ' ' + model['class_name'] + '\n')
            # Generate chaste code
            chaste_model = cg.NormalChasteModel(model['model'], model['class_name'], model['model_name_from_file'])
            chaste_model.generate_chaste_code()

            # Write generated files
            hhp_gen_file_path = os.path.join(tmp_path, model_type, chaste_model.file_name + ".hpp")
            cpp_gen_file_path = os.path.join(tmp_path, model_type, chaste_model.file_name + ".cpp")
            write_file(hhp_gen_file_path, chaste_model.generated_hpp)
            write_file(cpp_gen_file_path, chaste_model.generated_cpp)

            # Load reference files
            expected_hpp = get_file_lines(model['reference_models'][model_type]['expected_hpp_path'])
            expected_cpp = get_file_lines(model['reference_models'][model_type]['expected_cpp_path'])

            # Load generated files
            generated_hpp = get_file_lines(hhp_gen_file_path)
            generated_cpp = get_file_lines(cpp_gen_file_path)

            assert expected_hpp == generated_hpp
            assert expected_cpp == generated_cpp

    @pytest.mark.chaste
    def test_generate_dymaic_chaste_model(self, tmp_path):
        tmp_path = str(tmp_path)
        LOGGER.info('Converting: Normal Dynamichodgkin_huxley_squid_axon_model_1952_modified\n')
        model_file = \
            os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
        chaste_model = cellmlmanip.load_model(model_file)
        chaste_model = cg.NormalChasteModel(chaste_model,
                                            'Dynamichodgkin_huxley_squid_axon_model_1952_modifiedFromCellML',
                                            'dynamic_hodgkin_huxley_squid_axon_model_1952_modified')
        chaste_model.dynamically_loadable = True
        chaste_model.generate_chaste_code()

        # Write generated file
        hhp_gen_file_path = os.path.join(tmp_path, 'Normal', chaste_model.file_name + ".hpp")
        cpp_gen_file_path = os.path.join(tmp_path, 'Normal', chaste_model.file_name + ".cpp")
        write_file(hhp_gen_file_path, chaste_model.generated_hpp)
        write_file(cpp_gen_file_path, chaste_model.generated_cpp)

        # Load reference files
        expected_hpp = \
            os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Normal', chaste_model.file_name + ".hpp")
        expected_cpp = \
            os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Normal', chaste_model.file_name + ".cpp")
        expected_hpp = get_file_lines(expected_hpp)
        expected_cpp = get_file_lines(expected_cpp)

        # Load generated files
        generated_hpp = get_file_lines(hhp_gen_file_path)
        generated_cpp = get_file_lines(cpp_gen_file_path)

        assert expected_hpp == generated_hpp
        assert expected_cpp == generated_cpp

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
    def test_expose_annotated_variables(self, tmp_path):
        tmp_path = str(tmp_path)
        LOGGER.info('Testing expose_annotated_variables option\n')
        model_file = \
            os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'matsuoka_model_2003.cellml')
        chaste_model = cellmlmanip.load_model(model_file)

        chaste_model = cg.NormalChasteModel(chaste_model,
                                            'cellmatsuoka_model_2003FromCellML',
                                            'expose_annotated_variables_cellmatsuoka_model_2003')
        chaste_model.expose_annotated_variables = True
        chaste_model.generate_chaste_code()
        # Write generated file
        hhp_gen_file_path = os.path.join(tmp_path, 'Normal', chaste_model.file_name + ".hpp")
        cpp_gen_file_path = os.path.join(tmp_path, 'Normal', chaste_model.file_name + ".cpp")
        write_file(hhp_gen_file_path, chaste_model.generated_hpp)
        write_file(cpp_gen_file_path, chaste_model.generated_cpp)

        # Load reference files
        expected_hpp = \
            os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Normal', chaste_model.file_name + ".hpp")
        expected_cpp = \
            os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'Normal', chaste_model.file_name + ".cpp")
        expected_hpp = get_file_lines(expected_hpp)
        expected_cpp = get_file_lines(expected_cpp)

        # Load generated files
        generated_hpp = get_file_lines(hhp_gen_file_path)
        generated_cpp = get_file_lines(cpp_gen_file_path)

        assert expected_hpp == generated_hpp
        assert expected_cpp == generated_cpp
