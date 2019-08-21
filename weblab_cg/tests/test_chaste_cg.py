#
# Tests the basics of weblab_cg
#
import cellmlmanip
import logging
import os
import re
import weblab_cg as cg


# Show more logging output
logging.getLogger().setLevel(logging.DEBUG)

def test_generate_normal_models(tmp_path):
    run_test_models(tmp_path, cg.ChasteModelType.Normal)

#def test_generate_opt_models(tmp_path):
#    run_test_models(tmp_path, cg.ChasteModelType.Opt, skip_missing_ref_models=True)
#
#def test_generate_cvode_analytic_j_models(tmp_path):
#    run_test_models(tmp_path, cg.ChasteModelType.CvodeAnalyticJ, skip_missing_ref_models=True)
#
#def test_generate_cvode_numerical_j_models(tmp_path):
#    run_test_models(tmp_path, cg.ChasteModelType.CvodeNumericalJ, skip_missing_ref_models=True)
#
#def test_generate_be_models(tmp_path):
#    run_test_models(tmp_path, cg.ChasteModelType.BE, skip_missing_ref_models=True)


def run_test_models(tmp_path, model_type, skip_missing_ref_models=False):
    # Get folder with test cellml files
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'chaste_cg', 'cellml')

    #Walk through all cellml files in the folder
    for root, dirs, files in os.walk(model_folder):
        for model_file in files:
            if '.cellml' in model_file: #make sure we only process .cellml files
                class_name=model_file.replace(".cellml", "")
                model_file = os.path.join(model_folder , model_file)

                # Load cellml model
                model = cellmlmanip.load_model(model_file)

                #generate chaste cpp and hpp file for the normal model
                cg.create_chaste_model(tmp_path, class_name , model, model_type)

                # Check the generated and reference hpp and cpp match
                check_match_gengerated_chaste_model(tmp_path, class_name, model_type, skip_missing_ref_models)
 
 
def check_match_gengerated_chaste_model(gen_path, class_name, model_type, skip_missing_ref_models=False):
    """
    Returns whether the generated and reference models are the same

    Arguments

    ``gen_path``
        The path to store the generated model code at. (Just the path, excluding the file name as file name)
    ``class_name``
        Class name for the generated model.
    """
    #todo: other types of model, check cpp file

    expected_hpp = os.path.join(cg.DATA_DIR, 'tests', 'chaste_cg', 'reference_models', model_type.name, class_name+'.hpp')
    expected_cpp = os.path.join(cg.DATA_DIR, 'tests', 'chaste_cg', 'reference_models', model_type.name, class_name+'.cpp')
    #skip if reference model is missing and skip_missing_reference flasg is True
    if not os.path.isfile(expected_hpp) or not os.path.isfile(expected_cpp):
        assert skip_missing_ref_models
    else:
        # Read expected output hpp from file
        with open(expected_hpp, 'r') as f:
            expected_hpp = f.read()
            #ignore date stamp
            expected_hpp = re.sub("//! on .*\n", "", expected_hpp)
            f.close()

        # Read expected output cpp from file    
        with open(expected_cpp, 'r') as f:
            expected_cpp = f.read()
            #ignore date stamp
            expected_cpp = re.sub("//! on .*\n", "", expected_cpp)
            f.close()            
       
        # Read generated output hpp from file
        generated_hpp = os.path.join(gen_path, model_type.name, class_name + '.hpp')
        with open(generated_hpp, 'r') as f:
            generated_hpp = f.read()
            #ignore date stamp
            generated_hpp = re.sub("//! on .*\n", "", generated_hpp)
            f.close()

        # Read generated output cpp from file
        generated_cpp = os.path.join(gen_path, model_type.name, class_name + '.cpp')
        with open(generated_cpp, 'r') as f:
            generated_cpp = f.read()
            #ignore date stamp
            generated_cpp = re.sub("//! on .*\n", "", generated_cpp)
            f.close()

        # Now they should match
        assert generated_hpp == expected_hpp
#        assert generated_cpp == expected_cpp