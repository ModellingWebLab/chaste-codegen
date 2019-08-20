#
# Tests the basics of weblab_cg
#
#import pytest
import cellmlmanip
import logging
import warnings
import os
import re
import weblab_cg as cg


# Show more logging output
logging.getLogger().setLevel(logging.INFO)

def test_generate_cpp_hpp(tmp_path):
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
                cg.create_chaste_model(tmp_path, class_name , model, cg.ChasteModelType.Normal)

                # Check the generated and reference hpp and cpp match
                check_match_gengerated(tmp_path, class_name, cg.ChasteModelType.Normal)


def check_match_gengerated(gen_path, class_name, model_type):
    """
    Returns whether the generated and reference models are the same

    Arguments

    ``gen_path``
        The path to store the generated model code at. (Just the path, excluding the file name as file name)
    ``class_name``
        Class name for the generated model.
    """
    #todo: other types of model, check cpp file
    
    # Read expected output hpp from file
    expected_hpp = os.path.join(cg.DATA_DIR, 'tests', 'chaste_cg', 'reference_models', model_type.name, class_name+'.hpp')
    print (expected_hpp)
    with open(expected_hpp, 'r') as f:
        expected_hpp = f.read()
        #ignore date stamp
        expected_hpp = re.sub("//! on .*\n", "", expected_hpp)
        f.close()
   
    # Read generated output hpp from file
    generated_hpp = os.path.join(gen_path, model_type.name, class_name + '.hpp')
    print (generated_hpp)
    with open(generated_hpp, 'r') as f:
        generated_hpp = f.read()
        #ignore date stamp
        generated_hpp = re.sub("//! on .*\n", "", generated_hpp)
        f.close()       

    # Now they should match
    assert generated_hpp == expected_hpp