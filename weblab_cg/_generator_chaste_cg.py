#
# Functions related to generating model code for Chaste.
#

# TODO: apply unit conversions
# y derivatives msthematics
# Unit conversion for state variables voltage, time, cytosolic_calcium_concentration state vars
# capacitance in UseCellMLDefaultStimulus, using oxmeta see aslanidi_model_2009
# GetIntracellularAreaStimulus with conversion & different time unit see jafri_rice_winslow_1998 (-), or aslanidi_model_2009
# * period     // millisecond done, to check
# * duration   // millisecond, to check
# * amplitude  // uA_per_cm2, to check
# * offset     // millisecond, to check
# * end     // millisecond, to check

import logging
import os
import time
import sympy as sp
import enum
import weblab_cg as cg
from pint import errors

logging.getLogger().setLevel(logging.INFO)
MEMBRANE_VOLTAGE_INDEX = 0
CYTOSOLIC_CALCIUM_CONCENTRATION = 1
OXMETA = "https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#"

UNIT_DEFINITIONS = {'uA_per_cm2': [{'prefix': 'micro', 'units': 'ampere'}, {'exponent': '-2', 'prefix': 'centi', 'units': 'metre'}],
         'uA_per_uF': [{'prefix': 'micro', 'units': 'ampere'}, {'exponent': '-1', 'prefix': 'micro', 'units': 'farad'}],
         'millisecond': [{'prefix': 'milli', 'units': 'second'}],
         'millimolar': [{'units': 'mole', 'prefix': 'milli'}, {'units': 'litre', 'exponent': '-1'}],
         'millivolt': [{'prefix': 'milli', 'units': 'volt'}]}

STIMULUS_CURRENT = "membrane_stimulus_current"
STIMULUS_UNITS = {'membrane_stimulus_current_period': 'millisecond', 'membrane_stimulus_current_duration': 'millisecond', 
                  'membrane_stimulus_current_amplitude': 'uA_per_cm2', 'membrane_stimulus_current_offset': 'millisecond',
                  'membrane_stimulus_current_end': 'millisecond'}
STIMULUS_SECONDARY_UNITS = {'membrane_stimulus_current_amplitude': 'uA_per_uF'}
STIMULUS_RHS_MULTIPLIER = {'membrane_stimulus_current_amplitude': ' * HeartConfig::Instance()->GetCapacitance()'}


class ChasteModelType(enum.Enum):
    """ Enum used to indicate what type of model we have """
    Normal = 1
    Opt = 2
    CvodeAnalyticJ = 3
    CvodeNumericalJ = 4
    BE = 5

def create_chaste_model(output_path, model_name_from_file, class_name, model, model_type=ChasteModelType.Normal):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.cpp`` and ``.cpp`` model
    for use with Chaste, and stores it at ``path``.

    Arguments

    ``output_path``
        The path to store the generated model code at.
        (Just the path, excluding the file name as file name will be determined by the model_name)
    ``model_name``
        A name for the generated model.
    ``model``
        A :class:`cellmlmanip.Model` object.
    """
    # First steps to generate files with the correct file name.
    output_path = os.path.join(output_path, model_type.name)

    # Make sure the folder exists for the type of model
    try:
        os.makedirs(output_path)
    except FileExistsError:
        pass

    # Add file name (based on model name)
    hhp_file_path = os.path.join(output_path, model_name_from_file + ".hpp")

    # Add file name (based on model name)
    cpp_file_path = os.path.join(output_path, model_name_from_file + ".cpp")

    # Add all neded units to the model (for conversion) if they don't yet exist
    for unit_name in UNIT_DEFINITIONS:
        model.units.add_preferred_custom_unit_name(unit_name, UNIT_DEFINITIONS[unit_name])

    # Get state variables
    state_vars = model.get_state_symbols()
   
    # Printer for printing chaste state variable assignments
    var_chaste_interface_printer = cg.ChastePrinter(lambda symbol: 'var_chaste_interface_' + str(symbol).replace('$','__'),
                               lambda deriv: 'd_dt_chaste_interface_' + (str(deriv.expr).replace('$','__')
                                                        if isinstance(deriv, sp.Derivative) else str(deriv).replace('$','__')))

    # Printer for printing chaste regular variable assignments
    var_printer = cg.ChastePrinter(lambda symbol: 'var' + str(symbol).replace('$','__'),
                               lambda deriv: 'd_dt' + (str(deriv.expr).replace('$','__')
                                                        if isinstance(deriv, sp.Derivative) else str(deriv).replace('$','__')))

    # Printer for printing chaste regular variable assignments
    name_printer = cg.ChastePrinter(lambda symbol: str(symbol)[1:].replace('$','__'))

    def format_equation_list(equations, units=None, secondary_units=None, secondary_unit_rhs_multiplier="",
                            model=model, var_chaste_interface_printer=var_chaste_interface_printer, var_printer=var_printer):
        """ Formats list of equations for printing to the chaset cpp.
        Arguments

        ``printer``
            The printer to can transform sympy equations
        ``euations``
            The list of equations to format
        ``model``
            A :class:`cellmlmanip.Model` object.
        ``units``
            Optional units to convert rhs to
        ``secondary_units``
            Optional secondary units to convert rhs to if conversion to units fails
        ``secondary_unit_rhs_multiplier``
            A string to add as multiplier to the rhs in case secondary_units conversion is applied
        """
        formatted_equations = []
        rhs_multiplier = ""
        for eq in equations:
            factor = None
            current_units = model.units.summarise_units(eq.lhs)
            if units is not None:
                try:
                    # Try unit conversion -- ultimately this should be sorted in cellmlmanip?
                    if current_units != units:
                        factor = model.units.get_conversion_factor(1 * current_units, units)
                except errors.DimensionalityError:
                    # var_chaste_interface__membrane__stim_amplitude might be in different units
                    # and need multiplying with capacitance
                    if secondary_units is not None and current_units != secondary_units:
                        factor = model.units.get_conversion_factor(1 * current_units, secondary_units)
                        # Just so we can gie the correct comment
                        units = secondary_units
                    rhs_multiplier = secondary_unit_rhs_multiplier
            # Add intermediate conversion equation
            if factor is not None:
                converter_var = sp.Dummy(eq.lhs.name + '_converter')
                formatted_equations.append({'lhs': var_printer.doprint(eq.lhs),
                                            'rhs': var_printer.doprint(eq.rhs),
                                            'units': str(current_units)
                                            })                
                formatted_equations.append({'lhs': var_chaste_interface_printer.doprint(converter_var),
                                            'rhs': var_printer.doprint(eq.lhs),
                                            'units': str(current_units)
                                            })
            if factor is not None:
                rhs = var_chaste_interface_printer.doprint(factor) + ' * ' + var_chaste_interface_printer.doprint(converter_var)
            else:
                rhs = var_chaste_interface_printer.doprint(eq.rhs)
            formatted_equations.append({'lhs': var_chaste_interface_printer.doprint(eq.lhs),
                                        'rhs': rhs + rhs_multiplier,
                                        'units': str(units if not units is None else current_units)
                                        })
        return formatted_equations

    if model_type == ChasteModelType.Normal:
        # Check if the model has cytosolic_calcium_concentration,
        # if so we need to add GetIntracellularCalciumConcentration, otherwise leave blank
        try:
            model.get_symbol_by_ontology_term(OXMETA, "cytosolic_calcium_concentration")
            use_get_intracellular_calcium_concentration = True
        except KeyError:
            use_get_intracellular_calcium_concentration = False

        # Use an annotation on voltage to find V
        membrane_voltage_var = model.get_symbol_by_ontology_term(OXMETA, "membrane_voltage")

        # Get stimulus current
        cellml_default_stimulus = dict()        
        cellml_default_stimulus['membrane_stimulus_current'] = model.get_symbol_by_ontology_term(OXMETA, STIMULUS_CURRENT)
        # Get stimulus current units
        membrane_stimulus_current_units = model.units.summarise_units(cellml_default_stimulus['membrane_stimulus_current'])


        # Output a default cell stimulus from the metadata specification as long as the metadata exists:
        # Note the metadata and expected units are defined as constants above
        # STIMULUS_CURRENT, STIMULUS_UNITS, STIMULUS_SECONDARY_UNITS, STIMULUS_RHS_MULTIPLIER = {'membrane_stimulus_current_amplitude': ' * HeartConfig::Instance()->GetCapacitance()'}
        formatted_cellml_default_stimulus = dict()
        for eq in model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA, STIMULUS_CURRENT)]):
            ontology_terms = model.get_ontology_terms_by_symbol(eq.lhs, OXMETA)
            key = ontology_terms[0] if len(ontology_terms) > 0 else eq.lhs
            cellml_default_stimulus[key] = eq
            formatted_cellml_default_stimulus[key] = format_equation_list([eq], units=getattr(model.units.ureg, STIMULUS_UNITS[key]) if key in STIMULUS_UNITS else None,
            secondary_units=getattr(model.units.ureg, STIMULUS_SECONDARY_UNITS[key])  if key in STIMULUS_SECONDARY_UNITS else None,
            secondary_unit_rhs_multiplier=STIMULUS_RHS_MULTIPLIER[key] if key in STIMULUS_RHS_MULTIPLIER else None)

        try:
            cytosolic_calcium_concentration_var = \
                model.get_symbol_by_ontology_term(OXMETA, "cytosolic_calcium_concentration")
        except KeyError:
            cytosolic_calcium_concentration_var = None
            print("MODEL HAS NO cytosolic_calcium_concentration VARIABLE")

        # function used to order state variables in the same way as pycml does (for easy comparison)
        def state_var_key_order(membrane_voltage_var, cai_var, var):
            if var == membrane_voltage_var:
                return MEMBRANE_VOLTAGE_INDEX
            elif var == cai_var:
                return CYTOSOLIC_CALCIUM_CONCENTRATION
            else:
                return MEMBRANE_VOLTAGE_INDEX + CYTOSOLIC_CALCIUM_CONCENTRATION + 1

        # Sort the state variables, to make sure they have similar order to pycml
        state_vars = sorted(model.get_state_symbols(),
                            key=lambda state_var: state_var_key_order(membrane_voltage_var,
                                                                      cytosolic_calcium_concentration_var, state_var))

        # Getting the equations for const definitions for GetIIonic
        # use the RHS of the ODE defining V
        ionic_derivatives = [x for x in model.get_derivative_symbols() if x.args[0] == membrane_voltage_var]
        # figure out the currents (by finding variables with the same units
        # as the stimulus iirc) (without lexicographical_sort
        # Only equations with the same (lhs) units as the STIMULUS_CURRENTt are keps.
        # Also exclude the membrane_stimulus_current variable itself, and cellml_default_stimulus equations (if he model has those)
        equations_for_ionic_vars = [eq for eq in model.get_equations_for(ionic_derivatives, sort_by_input_symbols=True)
                                    if ((not 'membrane_stimulus_current' in cellml_default_stimulus)
                                    or (eq != cellml_default_stimulus['membrane_stimulus_current'] and eq not in cellml_default_stimulus.values()))
                                    and model.units.summarise_units(eq.lhs) == membrane_stimulus_current_units]

        # reverse toplological order is more similar (though not necessarily identical) to pycml
        equations_for_ionic_vars.reverse()
        # Once we have the ionic variables and their equations, we also need to add helper equtions that link symbols used in those to state variables
        # TODO: would not be needed if model.get_equations_for could preserve input order?
        used_symbols = []

        extended_equations_for_ionic_vars = model.get_equations_for([ionic_var_eq.lhs for ionic_var_eq in equations_for_ionic_vars], sort_by_input_symbols=True)
        # Format the state ionic variables
        formatted_ionic_vars = []
        # Only write equations once
        used_symbols = []
        # Some symbold will need substituting while printing ionic variables
        ionic_subs_dict = {}        
        for eq_ionic in extended_equations_for_ionic_vars:
            # Check if interface link vars are needed
            for v in model.get_symbols(eq_ionic.rhs):
                if v in state_vars:
                    #used_symbols.append(v)
                    # Link variable names start with the first bit of the equation they relate to (the component) followed by the variable name they are linking
                    link_var_name = eq_ionic.lhs.name.split('$')[0] + '$' + v.name.split('$')[1]
                    link_var = sp.Dummy(link_var_name)
                    ionic_subs_dict[v] = link_var
                    if link_var not in used_symbols:
                        used_symbols.append(link_var)
                        formatted_ionic_vars.append({
                                             'lhs': var_printer.doprint(link_var),
                                             'rhs': var_chaste_interface_printer.doprint(v),
                                             'units': 'dimensionless'
                                            })
            formatted_ionic_vars.append({
                                         'lhs': var_printer.doprint(eq_ionic.lhs),
                                         'rhs': var_printer.doprint(eq_ionic.rhs.subs(ionic_subs_dict)),
                                         'units': str(model.units.summarise_units(eq_ionic.lhs))
                                        })

        # Check whether to use capacitance in the ionic current and check what units to convert to
        try:
            model.units.get_conversion_factor(1 * membrane_stimulus_current_units, model.units.ureg.uA_per_cm2)
            ionic_current_units =  model.units.ureg.uA_per_cm2
            use_capacitance_i_ionic = False
        except errors.DimensionalityError:
            model.units.get_conversion_factor(1 * membrane_stimulus_current_units, model.units.ureg.uA_per_uF)
            ionic_current_units =  model.units.ureg.uA_per_uF
            use_capacitance_i_ionic = True

        formatted_ionic_interface_vars = [{'lhs': var_chaste_interface_printer.doprint(eq.lhs),
                                           'rhs': var_printer.doprint(eq.lhs),
                                           'units': str(model.units.summarise_units(eq.lhs)),
                                           'conversion_factor': model.units.get_conversion_factor(1 * model.units.summarise_units(eq.lhs), ionic_current_units)} 
                                           for eq in equations_for_ionic_vars]

        # Get the free variable for the model
        free_var = model.get_free_variable_symbol()
        free_variable = {'name': name_printer.doprint(free_var),
                         'units': model.units.summarise_units(free_var),
                         'system_name': model.name}

        ode_system_information = [{'name': model.get_ontology_terms_by_symbol(var, OXMETA)[0] if model.has_ontology_annotation(var, OXMETA) else name_printer.doprint(var),
                                   'initial_value': str(model.get_initial_value(var)),
                                    'units': str(model.units.summarise_units(var))}
                                    for var in state_vars]

        # EvaluateYDerivatives
        # Get derivatives for state variables in the same order as the state variables. Exclude membrane_voltage variable as it's treated seperately
        y_derivatives = [deriv for state_var in state_vars for deriv in model.get_derivative_symbols() if deriv.args[0] == state_var and deriv.args[0] != membrane_voltage_var]
        # Get the equations for the derivatives, excluding cellml_default_stimulus equations
        derivative_equations = model.get_equations_for(y_derivatives, sort_by_input_symbols=True, excluded_symbols=[x.lhs for x in cellml_default_stimulus.values()])

        # Format y_derivatives for writing to chaste output
        format_y_derivatives = [var_chaste_interface_printer.doprint(deriv) for deriv in y_derivatives]

        # TODO: special treatment membrane_v
        # TODO: linker variables??
        formatted_derivative_equations = format_equation_list(derivative_equations)


        # Filter unused state vars for ionic variables
        used_vars_ionic = set()
        for ionic_var in extended_equations_for_ionic_vars:
            used_vars_ionic = used_vars_ionic.union(model.get_symbols(ionic_var.rhs))

        # Filter unused state vars for EvaluateYDerivatives
        used_y_deriv = set()
        for derivative_eq in derivative_equations:
            used_y_deriv = used_vars_ionic.union(model.get_symbols(derivative_eq.rhs))

        # Format the state variables Keep order, add ones used in getIonic first
        formatted_state_vars=[]
        for var in state_vars:
            if var in used_vars_ionic:
                formatted_state_vars.append({'var': var_chaste_interface_printer.doprint(var),
                                             'initial_value': str(model.get_initial_value(var)),
                                            'units': str(model.units.summarise_units(var)),
                                            'in_ionic': True})

        # Now add the ones used in y derivatives only
        for var in state_vars:
            if var not in used_vars_ionic and var in used_y_deriv:
                formatted_state_vars.append({'var': var_chaste_interface_printer.doprint(var),
                                             'initial_value': str(model.get_initial_value(var)),
                                            'units': str(model.units.summarise_units(var)),
                                            'in_ionic': False})
        # Generate hpp for model
        template = cg.load_template('chaste', 'normal_model.hpp')
        with open(hhp_file_path, 'w') as f:
            f.write(template.render({
                'model_name_from_file': model_name_from_file,
                'class_name': class_name,
                'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'cellml_default_stimulus_equations': cellml_default_stimulus,
                'use_get_intracellular_calcium_concentration': use_get_intracellular_calcium_concentration,
            }))

        # Generate cpp for model
        template = cg.load_template('chaste', 'normal_model.cpp')
        with open(cpp_file_path, 'w') as f:
            f.write(template.render({
                'model_name_from_file': model_name_from_file,
                'class_name': class_name,
                'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'cellml_default_stimulus_equations': formatted_cellml_default_stimulus,
                'use_get_intracellular_calcium_concentration': use_get_intracellular_calcium_concentration,
                'membrane_voltage_index': MEMBRANE_VOLTAGE_INDEX,
                'cytosolic_calcium_concentration_index': CYTOSOLIC_CALCIUM_CONCENTRATION,
                'state_vars': formatted_state_vars,
                'ionic_vars': formatted_ionic_vars,
                'ionic_interface_vars': formatted_ionic_interface_vars,
                'y_derivative_equations': formatted_derivative_equations,
                'y_derivatives': format_y_derivatives,
                'use_capacitance_i_ionic': use_capacitance_i_ionic,
                'free_variable': free_variable,
                'ode_system_information': ode_system_information
            }))

    elif model_type == ChasteModelType.Opt:
        pass

    elif model_type == ChasteModelType.CvodeAnalyticJ:
        pass

    elif model_type == ChasteModelType.CvodeNumericalJ:
        pass

    elif model_type == ChasteModelType.BE:
        pass
