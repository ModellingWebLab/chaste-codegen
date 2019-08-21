#
# Functions related to generating model code for Chaste.
#
import logging
import os
import sympy as sp
import enum
import time
import weblab_cg as cg

logging.getLogger().setLevel(logging.INFO)

class ChasteModelType(enum.Enum):
    Normal = 1
    Opt = 2
    CvodeAnalyticJ = 3
    CvodeNumericalJ = 4
    BE=5
  
def mkdir_p(path):
    """ Tries to create the path """
    try:
        os.makedirs(path)
    except:
        pass
        
def create_chaste_model(path, model_name, model, model_type=ChasteModelType.Normal):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.cpp`` and ``.cpp`` model 
    for use with Chaste, and stores it at ``path``.

    Arguments

    ``path``
        The path to store the generated model code at. (Just the path, excluding the file name as file name will be determined by the model_name)
    ``model_name``
        A name for the generated model.
    ``model``
        A :class:`cellmlmanip.Model` object.
    """
    # First steps to generate files with the correct file name.
    path = os.path.join(path, model_type.name)
    
    #Make sure the folder exists for the type of model
    mkdir_p(path)
    
    #Add file name (based on model name)
    hhp_file_path = os.path.join(path, model_name+".hpp")

    #Add file name (based on model name)
    cpp_file_path = os.path.join(path, model_name+".cpp")

    
    # Check if the model has cytosolic_calcium_concentration, if so we need to add GetIntracellularCalciumConcentration, otherwise leave blank
    try:
        model.get_symbol_by_cmeta_id("cytosolic_calcium_concentration")
        get_intracellular_calcium_concentration = True
    except:
        get_intracellular_calcium_concentration = False
  
    #Output a default cell stimulus from the metadata specification as long as the following metadata exists:
    # * membrane_stimulus_current_amplitude
    # * membrane_stimulus_current_period         
    # * membrane_stimulus_current_duration 
    # * optionally: offset and end
    # Ensures that the amplitude of the generated RegularStimulus is negative.
    vars_membrane_stimulus_current = dict()
    use_cellml_default_stimulus = False
    print(vars_membrane_stimulus_current)
    try:
        vars_membrane_stimulus_current['period'] = model.get_symbol_by_cmeta_id("membrane_stimulus_current_period")
        vars_membrane_stimulus_current['duration'] = model.get_symbol_by_cmeta_id("membrane_stimulus_current_duration")
        vars_membrane_stimulus_current['amplitude'] = model.get_symbol_by_cmeta_id("membrane_stimulus_current_amplitude")
        
        use_cellml_default_stimulus = True
        vars_membrane_stimulus_current['offset'] = model.get_symbol_by_cmeta_id("membrane_stimulus_current_offset")
        vars_membrane_stimulus_current['end'] = model.get_symbol_by_cmeta_id("membrane_stimulus_current_end")        
    except:
        pass

    extended_dependencies_vars_membrane_stimulus = model.get_equations_for(vars_membrane_stimulus_current.values())
    #todo: apply unit conversions
    # * period     // millisecond
    # * duration   // millisecond
    # * amplitude  // uA_per_cm2
    # * offset     // millisecond
    # * end     // millisecond

    
    # Generate hpp for model
    template = cg.load_template('chaste', 'normal_model.hpp')
    with open(hhp_file_path, 'w') as f:
        f.write(template.render({
            'ucase_model_name': model_name.upper(),
            'model_name': model_name,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'use_cellml_default_stimulus':use_cellml_default_stimulus,
            'get_intracellular_calcium_concentration':get_intracellular_calcium_concentration,
        }))
    # Generate cpp for model
    template = cg.load_template('chaste', 'normal_model.cpp')
    with open(cpp_file_path, 'w') as f:
        f.write(template.render({
            'model_name': model_name,        
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'use_cellml_default_stimulus':use_cellml_default_stimulus,
            'get_intracellular_calcium_concentration':get_intracellular_calcium_concentration,            
        }))        