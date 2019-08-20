#
# Tests the basics of weblab_cg
#
#import pytest
import cellmlmanip
import logging
import os
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
                convert_model(tmp_path, model_folder, model_file)
    #assert 1 == 2
    
def convert_model(tmp_path, model_folder, model_file):
    class_name=model_file.replace(".cellml", "")

    parameters=[]
    
    # Load cellml model
    model = os.path.join(model_folder , model_file)
    model = cellmlmanip.load_model(model)            

    #generate chaste cpp and hpp file
    cg.create_chaste_model(tmp_path, class_name, model, parameters)