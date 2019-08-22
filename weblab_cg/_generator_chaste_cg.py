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
        
def get_unique_names(model):
    """
    Creates unique names for all symbols in a CellML model.
    """
    # Component variable separator
    # Note that variables are free to use __ in their names too, it makes the
    # produced code less readable but doesn't break anything.
    sep = '__'

    # Create a symbol => name mapping, and a reverse name => symbol mapping
    symbols = {}
    reverse = {}

    def uname(name):
        """ Add an increasing number to a name until it's unique """
        root = name + '_'
        i = 0
        while name in reverse:
            i += 1
            name = root + str(i)
        return name

    for v in model.get_equation_graph():
        if isinstance(v, sp.Derivative):
            continue

        # Try simple name
        parts = v.name.split('$')
        assert len(parts) == 2
        #name = parts[-1]
        name = parts[0] + sep + parts[1]

        # If already taken, rename _both_ variables using component name
        if name in reverse:

            # Get existing variable
            other = reverse[name]

            # Check it hasn't been renamed already
            if symbols[other] == name:
                oparts = other.name.split('$')
                assert len(oparts) == 2
                oname = uname(oparts[0] + sep + oparts[1])
                symbols[other] = oname
                reverse[oname] = other

            # Get new name for v
            name = uname(parts[0] + sep + parts[1])

        # Store symbol name
        symbols[v] = name
        reverse[name] = v

    return symbols

def format_equation_list(printer, equations):
    formatted_equations=[]
    for eq in equations:
        formatted_equations.append({
            'lhs': printer.doprint(eq.lhs),
            'rhs': printer.doprint(eq.rhs)
        })
    return formatted_equations
    

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

    if model_type == ChasteModelType.Normal :
        # Check if the model has cytosolic_calcium_concentration, if so we need to add GetIntracellularCalciumConcentration, otherwise leave blank
        try:
            model.get_symbol_by_cmeta_id("cytosolic_calcium_concentration")
            get_intracellular_calcium_concentration = True
        except:
            get_intracellular_calcium_concentration = False
      
        #set up printer to be able to write equations
        # Get unique names for all symbols
        unames = get_unique_names(model)

        # Symbol naming function
        def symbol_name(symbol, prefix = "chaste_interface__"):
            return 'var_' + prefix + unames[symbol]

        # Derivative naming function
        def derivative_name(deriv):
            var = deriv.expr if isinstance(deriv, sp.Derivative) else deriv
            return 'd_dt_' + unames[var]

        printer = cg.WebLabPrinter(symbol_name, derivative_name)

        #Output a default cell stimulus from the metadata specification as long as the following metadata exists:
        # * membrane_stimulus_current_amplitude
        # * membrane_stimulus_current_period         
        # * membrane_stimulus_current_duration 
        # * optionally: offset and end
        # Ensures that the amplitude of the generated RegularStimulus is negative.
        cellml_default_stimulus_equations = None
        try:
            cellml_default_stimulus_equations = dict()
            #todo: apply unit conversions
            # * period     // millisecond
            # * duration   // millisecond
            # * amplitude  // uA_per_cm2
            # * offset     // millisecond
            # * end     // millisecond

            #start, period, duration, amplitude
            cellml_default_stimulus_equations['period'] = format_equation_list(printer, model.get_equations_for([model.get_symbol_by_cmeta_id("membrane_stimulus_current_period")]) )
            cellml_default_stimulus_equations['duration'] =  format_equation_list(printer, model.get_equations_for([model.get_symbol_by_cmeta_id("membrane_stimulus_current_duration")]) )

            model.units.add_custom_unit('uA_per_cm2', [{'prefix': 'micro', 'units': 'ampere'}, {'exponent': '-2', 'prefix': 'centi', 'units': 'metre'}])
            equations =  model.get_equations_for([model.get_symbol_by_cmeta_id("membrane_stimulus_current_amplitude")])
            units = model.units.summarise_units(equations[0].lhs)
            source_unit_quantity = equations[0].lhs * units
            factor = model.units.get_conversion_factor(source_unit_quantity, model.units.ureg.uA_per_cm2)
            
            cellml_default_stimulus_equations['amplitude'] =  format_equation_list(printer, equations )
           
        except:
            cellml_default_stimulus_equations = None
            print("No default_stimulus_equations\n")
        #optional default_stimulus_equation
        try:
            cellml_default_stimulus_equations['offset'] =  format_equation_list(printer, model.get_equations_for([model.get_symbol_by_cmeta_id("membrane_stimulus_current_offset")]) )
        except:
            pass

        #optional default_stimulus_equation            
        try:
            cellml_default_stimulus_equations['end'] =  format_equation_list(printer, model.get_equations_for([model.get_symbol_by_cmeta_id("membrane_stimulus_current_end")]) )              
        except:
            pass
        # Generate hpp for model
        template = cg.load_template('chaste', 'normal_model.hpp')
        with open(hhp_file_path, 'w') as f:
            f.write(template.render({
                'ucase_model_name': model_name.upper(),
                'model_name': model_name,
                'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'cellml_default_stimulus_equations':cellml_default_stimulus_equations,
                'get_intracellular_calcium_concentration':get_intracellular_calcium_concentration,
            }))
        # Generate cpp for model

        template = cg.load_template('chaste', 'normal_model.cpp')
        with open(cpp_file_path, 'w') as f:
            f.write(template.render({
                'model_name': model_name,        
                'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'cellml_default_stimulus_equations':cellml_default_stimulus_equations,
                'get_intracellular_calcium_concentration':get_intracellular_calcium_concentration,
            }))

    elif model_type == ChasteModelType.Opt:
        pass

    elif model_type == ChasteModelType.CvodeAnalyticJ:
        pass

    elif model_type == ChasteModelType.CvodeNumericalJ:
        pass

    elif model_type == ChasteModelType.BE:
        pass