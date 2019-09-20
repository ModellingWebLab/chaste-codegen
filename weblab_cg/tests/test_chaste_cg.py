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

@pytest.fixture(scope='module')
def temp_folder(tmpdir_factory):
    temp_folder = tmpdir_factory.mktemp('generated_chaste_models')
    return temp_folder

@pytest.fixture(scope="module")
def chaste_generators(temp_folder, tmpdir_factory):
    generators = []
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
                generators.append(cg.ChasteCodeGenerator(cellmlmanip.load_model(model_file), os.path.join(temp_folder, 'Normal'), model_name_from_file, class_name))
    return generators

def test_generate_normal_models(temp_folder, chaste_generators):
    output_path = os.path.join(temp_folder, 'Normal')
    for generator in chaste_generators:
        generator.create_normal_model()
        check_match_gengerated_chaste_hpp(output_path, generator.model_name_for_filename, 'Normal', skip_missing_ref_models=False)
       
        #check_match_gengerated_chaste_cpp()

@pytest.mark.skip(reason="Opt models not yet implemented")
def test_generate_opt_models(temp_folder, chaste_generators):
    output_path = os.path.join(temp_folder, 'Opt')
    for generator in chaste_generators:
        generator.output_path = output_path
        generator.create_opt_model()
        check_match_gengerated_chaste_hpp(output_path, generator.model_name_for_filename, 'Opt', skip_missing_ref_models=False)
       
        #check_match_gengerated_chaste_cpp()

@pytest.mark.skip(reason="Analytic_j models not yet implemented")
def test_generate_cvode_analytic_j_models(temp_folder, chaste_generators):
    output_path = os.path.join(temp_folder, 'Analytic_j')
    for generator in chaste_generators:
        generator.output_path = output_path
        generator.create_analytic_jmodel()
        check_match_gengerated_chaste_hpp(output_path, generator.model_name_for_filename, 'Analytic_j', skip_missing_ref_models=False)
       
        #check_match_gengerated_chaste_cpp()

@pytest.mark.skip(reason="Numerical_j models not yet implemented")
def test_generate_cvode_numerical_j_models(temp_folder, chaste_generators):
    output_path = os.path.join(temp_folder, 'Numerical_j')
    for generator in chaste_generators:
        generator.output_path = output_path
        generator.create_numerical_j_model()
        check_match_gengerated_chaste_hpp(output_path, generator.model_name_for_filename, 'Numerical_j', skip_missing_ref_models=False)
       
        #check_match_gengerated_chaste_cpp()

@pytest.mark.skip(reason="BE models not yet implemented")
def test_generate_be_models(temp_folder, chaste_generators):
    output_path = os.path.join(temp_folder, 'BE')
    for generator in chaste_generators:
        generator.output_path = output_path
        generator.create_be_model()
        check_match_gengerated_chaste_hpp(output_path, generator.model_name_for_filename, 'BE', skip_missing_ref_models=False)
       
        #check_match_gengerated_chaste_cpp()

def check_match_gengerated_chaste_hpp(gen_path, model_name_from_file, model_type, skip_missing_ref_models=False):
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
                     model_type, model_name_from_file + '.hpp')

    # Skip if reference model is missing and skip_missing_reference flasg is True
    if not os.path.isfile(expected_hpp):
        assert skip_missing_ref_models
    else:
        # Read expected output hpp from file
        with open(expected_hpp, 'r') as f:
            expected_hpp = f.read()
            # Ignore comments
            expected_hpp = header_tag_regex.sub("", expected_hpp)
            f.close()

        # Read generated output hpp from file
        generated_hpp = os.path.join(gen_path, model_name_from_file + '.hpp')
        with open(generated_hpp, 'r') as f:
            generated_hpp = f.read()
            # Ignore comments
            generated_hpp = header_tag_regex.sub("", generated_hpp)
            f.close()

        # Now they should match
        assert generated_hpp == expected_hpp

#def check_match_gengerated_chaste_cpp(gen_path, model_name_from_file, model_type, skip_missing_ref_models=False):
