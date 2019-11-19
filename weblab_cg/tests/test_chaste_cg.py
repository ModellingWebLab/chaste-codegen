import logging
import os
import re
import weblab_cg as cg
import pytest
from weblab_cg.tests.chaste_test_utils import load_chaste_models, get_file_lines, write_file


# Show more logging output
logging.getLogger().setLevel(logging.DEBUG)


class TestChasteCG(object):
    """ Tests weblab_cg against reference models generated with weblab_cg and tested in chaste.

    TODO: at some point we might be able to create a set of smaller test models to cover all options"""
    _TIMESTAMP_REGEX = re.compile(r'(//! on .*\n)')

    def model_types(self):
        return ['Normal']

    @pytest.fixture(scope="class")
    def chaste_models(self):
        """ Load all models"""
        return load_chaste_models(model_types=self.model_types())

    def test_generate_chate_models(self, tmp_path, chaste_models):
        """ Check generation of Normal models against reference"""
        tmp_path = str(tmp_path)
        for model in chaste_models:
            for model_type in model['reference_models'].keys():
                # Generate chaste code
                chaste_model = cg.NormalChasteModel(model['model'], model['class_name'], model['model_name_from_file'])
                chaste_model.dynamically_loadable = True
                chaste_model.generate_chaste_code()
                #TestManualaslanidi_model_2009FromCellML

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

                chaste_model.dynamically_loadable = False
                chaste_model.class_name = chaste_model.class_name.replace('Dynamic', 'TestManual')
                chaste_model.file_name = chaste_model.class_name
                chaste_model.generate_chaste_code()
                hhp_gen_file_path = os.path.join(tmp_path, model_type, chaste_model.file_name + ".hpp")
                cpp_gen_file_path = os.path.join(tmp_path, model_type, chaste_model.file_name + ".cpp")
                write_file(hhp_gen_file_path, chaste_model.generated_hpp)
                write_file(cpp_gen_file_path, chaste_model.generated_cpp)