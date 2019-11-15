import cellmlmanip
import logging
import os
import re
import weblab_cg as cg
import pytest
import sympy
from sympy import SympifyError
import pyparsing

# Show more logging output
logging.getLogger().setLevel(logging.DEBUG)

class TestChasteCG(object):
    """ Tests weblab_cg against reference models generated with weblab_cg and tested in chaste.
    
    TODO: at some point we might be able to create a set of smaller test models to cover all options"""
    _TIMESTAMP_REGEX =  re.compile(r'(//! on .*\n)')

    def model_types(self):
        return ['Normal']

    @pytest.fixture(scope="class")
    def chaste_models(self):
        """ Load all models"""
        # Get folder with test cellml files
        model_folder = os.path.join(cg.DATA_DIR, 'tests', 'cellml')

        # Walk through all cellml files in the folder
        model_files = []
        for root, dirs, files in os.walk(model_folder):
            for model_file in files:
                if model_file.endswith('.cellml'):  # make sure we only process .cellml files
                    model_name_from_file = model_file.replace('.cellml', '')
                    model_file = os.path.join(model_folder, model_file)
                    reference_models = {}
                    for model_type in self.model_types():
                        expected_hpp_path = \
                                os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models',
                                             model_type, model_name_from_file + '.hpp')
                        expected_cpp_path = \
                                os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models',
                                             model_type, model_name_from_file + '.cpp')
                        # Skip cellml files without reference chaste code
                        if os.path.isfile(expected_hpp_path) and os.path.isfile(expected_cpp_path):
                            reference_models.update({model_type:{'expected_hpp_path': expected_hpp_path, 'expected_cpp_path':expected_cpp_path}})

                    if len(reference_models) > 0:
                        class_name = 'Dynamic' + model_name_from_file
                        model_files.append({'model': cellmlmanip.load_model(model_file),
                                            'model_name_from_file': model_name_from_file,
                                            'class_name': class_name,
                                            'reference_models': reference_models})
        return model_files

    def test_generate_models(self, tmp_path, chaste_models):
        """ Check generation of Normal models against reference"""
        tmp_path = str(tmp_path)
        for model in chaste_models:
            for model_type in model['reference_models'].keys():
                # Generate chaste code                
                chaste_model = cg.NormalChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
                chaste_model.generate_chaste_code()

                # Load reference files
                expected_hpp = self._get_file_contents(model['reference_models'][model_type]['expected_hpp_path'])
                expected_cpp = self._get_file_contents(model['reference_models'][model_type]['expected_cpp_path'])

                # Ignore the timestamp
                expected_hpp = self._TIMESTAMP_REGEX.sub("", expected_hpp)
                expected_cpp = self._TIMESTAMP_REGEX.sub("", expected_cpp)
                generated_hpp = self._TIMESTAMP_REGEX.sub("", chaste_model.generated_hpp)
                generated_cpp = self._TIMESTAMP_REGEX.sub("", chaste_model.generated_cpp)

                assert expected_hpp == generated_hpp
                assert expected_cpp == generated_cpp

    def _get_file_contents(self, file_path):
        """ Returns the content of file at the location file_path"""
        # Check reference model exists
        assert os.path.isfile(file_path)
        # Read expected output hpp from file
        with open(file_path, 'r') as f:
            expected_hpp = f.read()
            f.close()
        return expected_hpp