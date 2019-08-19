#
# Tests the basics of weblab_cg
#
#import pytest
import logging
import os
import weblab_cg as cg


# Show more logging output
logging.getLogger().setLevel(logging.INFO)

def test_generate_cpp_hpp(tmp_path):
    class_name=""
    parameters=[]
    print(tmp_path)
    # Get folder with test cellml files
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'chaste_cg', 'cellml')

    #Walk through all cellml files in the folder
    for root, dirs, files in os.walk(model_folder):
        for file in files:
            if '.cellml' in file: #make sure we only process .cellml files
                # Load cellml model
                model = os.path.join(file)
                model = cellmlmanip.load_model(model)            
                
                #generate chaste cpp and hpp file
                cg.create_chaste_model(tmp_path, class_name, model, parameters)
    assert 1 == 2