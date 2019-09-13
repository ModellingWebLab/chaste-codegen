#
# Tests the basics of weblab_cg
#
import cellmlmanip
import logging
import os
import re
import weblab_cg as cg
import pytest


# Show more logging output
logging.getLogger().setLevel(logging.DEBUG)

#c++ -> simpy
#pow->Pow
#ceil -> ceiling

@pytest.fixture(scope="module")
def cellml_models():
    models = []
    # Get folder with test cellml files
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'cellml')

    # Walk through all cellml files in the folder
    for root, dirs, files in os.walk(model_folder):
        for model_file in files:
            if '.cellml' in model_file:  # make sure we only process .cellml files
                model_name_from_file = model_file.replace('.cellml', '')
                class_name = 'Dynamic' + model_name_from_file
                model_file = os.path.join(model_folder, model_file)
                # Load cellml model and add it to the list of models
                models.append({'model': cellmlmanip.load_model(model_file),
                              'model_name_from_file': model_name_from_file, 'class_name': class_name})
    return models


def test_generate_normal_models(tmp_path, cellml_models):
    run_test_models(tmp_path, cellml_models, cg.ChasteModelType.Normal, True)


@pytest.mark.skip(reason="Opt models not yet implemented")
def test_generate_opt_models(tmp_path, cellml_models):
    run_test_models(tmp_path, cellml_models, cg.ChasteModelType.Opt, skip_missing_ref_models=True)


@pytest.mark.skip(reason="Analytic_j models not yet implemented")
def test_generate_cvode_analytic_j_models(tmp_path, cellml_models):
    run_test_models(tmp_path, cellml_models, cg.ChasteModelType.CvodeAnalyticJ, skip_missing_ref_models=True)


@pytest.mark.skip(reason="Numerical_j models not yet implemented")
def test_generate_cvode_numerical_j_models(tmp_path, cellml_models):
    run_test_models(tmp_path, cellml_models, cg.ChasteModelType.CvodeNumericalJ, skip_missing_ref_models=True)


@pytest.mark.skip(reason="BE models not yet implemented")
def test_generate_be_models(tmp_path, cellml_models):
    run_test_models(tmp_path, cellml_models, cg.ChasteModelType.BE, skip_missing_ref_models=True)


def run_test_models(tmp_path, cellml_models, model_type, skip_missing_ref_models=False):
    # Walk through all cellml files in the folder
    for model in cellml_models:
        # Generate chaste cpp and hpp file for the normal model
        cg.create_chaste_model(tmp_path, model['model_name_from_file'], model['class_name'], model['model'], model_type)

        # Check the generated and reference hpp and cpp match
        check_match_gengerated_chaste_model(tmp_path, model['model_name_from_file'], model_type,
                                            skip_missing_ref_models)


def check_match_gengerated_chaste_model(gen_path, model_name_from_file, model_type, skip_missing_ref_models=False):
    """
    Returns whether the generated and reference models are the same

    Arguments

    ``gen_path``
        The path to store the generated model code at. (Just the path, excluding the file name as file name)
    ``class_name``
        Class name for the generated model.
    """
    header_tag_regex = re.compile("(//.*\n)")

    expected_hpp = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models',
                     model_type.name, model_name_from_file + '.hpp')
    expected_cpp = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models',
                     model_type.name, model_name_from_file + '.cpp')
    # Skip if reference model is missing and skip_missing_reference flasg is True
    if not os.path.isfile(expected_hpp) or not os.path.isfile(expected_cpp):
        assert skip_missing_ref_models
    else:
        # Read expected output hpp from file
        with open(expected_hpp, 'r') as f:
            expected_hpp = f.read()
            # Ignore comments
            expected_hpp = header_tag_regex.sub("", expected_hpp)
            f.close()

        # Read expected output cpp from file
        with open(expected_cpp, 'r') as f:
            expected_cpp = f.read()
            # Ignore comments
            expected_cpp = header_tag_regex.sub("", expected_cpp)
            f.close()

        # Read generated output hpp from file
        generated_hpp = os.path.join(gen_path, model_type.name, model_name_from_file + '.hpp')
        with open(generated_hpp, 'r') as f:
            generated_hpp = f.read()
            # Ignore comments
            generated_hpp = header_tag_regex.sub("", generated_hpp)
            f.close()

        # Read generated output cpp from file
        generated_cpp = os.path.join(gen_path, model_type.name, model_name_from_file + '.cpp')
        with open(generated_cpp, 'r') as f:
            generated_cpp = f.read()
            # Ignore comments
            generated_cpp = header_tag_regex.sub("", generated_cpp)
            f.close()

        # Now they should match
        assert generated_hpp == expected_hpp
#        assert generated_cpp == expected_cpp
