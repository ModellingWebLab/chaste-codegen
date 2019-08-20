#
# Functions related to generating model code for Chaste.
#
import os
import sympy as sp
import weblab_cg as cg

 
def create_chaste_model(path, class_name, model, parameters):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.cpp`` and ``.cpp`` model 
    for use with Chaste, and stores it at ``path``.

    Arguments

    ``path``
        The path to store the generated model code at. (Just the path, excluding the file name as file name will be determined by the class_name)
    ``class_name``
        A name for the generated class.
    ``model``
        A :class:`cellmlmanip.Model` object.
    ``parameters``
        An ordered list of annotations ``(namespace_uri, local_name)`` for the
        variables to use as model parameters. All variables used as parameters
        must be literal constants.

    """
    # First steps to generate files with the correct file name.
    path = os.path.join(path, class_name+".hpp")
    print(path)
    #outputs = []

    # Generate model
    
    #for beeler_reuter: use_cellml_default_stimulus = "boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();"
    #for beeler_reuter: get_intracellular_calcium_concentration = "double GetIntracellularCalciumConcentration();"
    template = cg.load_template('chaste', 'normal_model.hpp')
    with open(path, 'w') as f:
        f.write(template.render({
            'model_name': class_name,        
            'ucase_model_name': class_name.upper(),
            'use_cellml_default_stimulus':'',
            'get_intracellular_calcium_concentration':'',
        }))