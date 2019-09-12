#
# Functions related to generating model code for Chaste.
#
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
    # todo: apply unit conversions
    # * period     // millisecond
    # * duration   // millisecond
    # * amplitude  // uA_per_cm2
    # * offset     // millisecond
    # * end     // millisecond
    # Also: voltage, time

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
    model.units.add_preferred_custom_unit_name('uA_per_cm2', [{'prefix': 'micro', 'units': 'ampere'},
                                                              {'exponent': '-2', 'prefix': 'centi', 'units': 'metre'}])
    model.units.add_preferred_custom_unit_name('uA_per_uF', [{'prefix': 'micro', 'units': 'ampere'},
                                                             {'exponent': '-1', 'prefix': 'micro', 'units': 'farad'}])
    model.units.add_preferred_custom_unit_name('millisecond', [{'prefix': 'milli', 'units': 'second'}])
    model.units.add_preferred_custom_unit_name('millimolar', [{'units': 'mole', 'prefix': 'milli'},
                                                              {'units': 'litre', 'exponent': '-1'}])
    model.units.add_preferred_custom_unit_name('millivolt', [{'prefix': 'milli', 'units': 'volt'}])

    # Get state variables
    state_vars = model.get_state_symbols()
   
    # Printer for printing chaste state variable assignments
    var_chaste_interface_printer = cg.ChastePrinter(lambda symbol: 'var_chaste_interface_' + str(symbol).replace('$','__'),
                               lambda deriv: 'd_dt_' + (str(deriv.expr)
                                                        if isinstance(deriv, sp.Derivative) else str(deriv)))

    # Printer for printing chaste regular variable assignments
    var_printer = cg.ChastePrinter(lambda symbol: 'var' + str(symbol).replace('$','__'),
                               lambda deriv: 'd_dt_' + (str(deriv.expr)
                                                        if isinstance(deriv, sp.Derivative) else str(deriv)))

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
        for equation in equations:
            eq = equation
            factor = None
            if units is not None:
                try:
                    # Try unit conversion -- ultimately this should be sorted in cellmlmanip?
                    current_units = model.units.summarise_units(eq.lhs)
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
                                            'units': str(model.units.summarise_units(eq.lhs))
                                            })                
                formatted_equations.append({'lhs': var_chaste_interface_printer.doprint(converter_var),
                                            'rhs': var_printer.doprint(eq.lhs),
                                            'units': str(model.units.summarise_units(eq.lhs))
                                            })
            if factor is not None:
                rhs = var_chaste_interface_printer.doprint(factor) + ' * ' + var_chaste_interface_printer.doprint(converter_var)
            else:
                rhs = var_chaste_interface_printer.doprint(eq.rhs)
            formatted_equations.append({'lhs': var_chaste_interface_printer.doprint(eq.lhs),
                                        'rhs': rhs + rhs_multiplier,
                                        'units': str(units)
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

        # Output a default cell stimulus from the metadata specification as long as the following metadata exists:
        # * membrane_stimulus_current_amplitude
        # * membrane_stimulus_current_period
        # * membrane_stimulus_current_duration
        # * optionally: offset and end
        # Ensures that the amplitude of the generated RegularStimulus is negative.
        cellml_default_stimulus_equations = None
        formatted_cellml_default_stimulus_equations = None
        try:
            cellml_default_stimulus_equations = dict()
            formatted_cellml_default_stimulus_equations = dict()

            # start, period, duration, amplitude
            cellml_default_stimulus_equations['period'] = \
                model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA, "membrane_stimulus_current_period")], False)
            formatted_cellml_default_stimulus_equations['period'] = \
                format_equation_list(cellml_default_stimulus_equations['period'], model.units.ureg.millisecond)

            cellml_default_stimulus_equations['duration'] = \
                model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA,
                                        "membrane_stimulus_current_duration")], False)
            formatted_cellml_default_stimulus_equations['duration'] = \
                format_equation_list(cellml_default_stimulus_equations['duration'], model.units.ureg.millisecond)

            cellml_default_stimulus_equations['amplitude'] = \
                model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA,
                                        "membrane_stimulus_current_amplitude")], False)
            formatted_cellml_default_stimulus_equations['amplitude'] = \
                format_equation_list(cellml_default_stimulus_equations['amplitude'],
                                     model.units.ureg.uA_per_cm2, model.units.ureg.uA_per_uF,
                                     " * HeartConfig::Instance()->GetCapacitance()")
        except KeyError:
            cellml_default_stimulus_equations = None
            formatted_cellml_default_stimulus_equations = None
            cellml_default_stimulus_equations = None
            print("No default_stimulus_equations\n")

        # optional default_stimulus_equation offset
        try:
            cellml_default_stimulus_equations['offset'] = \
                model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA, "membrane_stimulus_current_offset")], False)
            formatted_cellml_default_stimulus_equations['offset'] = \
                format_equation_list(cellml_default_stimulus_equations['offset'], model.units.ureg.millisecond)
        except KeyError:
            pass  # offset is optional

        # optional default_stimulus_equation end
        try:
            cellml_default_stimulus_equations['end'] = \
                model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA, "membrane_stimulus_current_end")], False)
            formatted_cellml_default_stimulus_equations['end'] = \
                format_equation_list(cellml_default_stimulus_equations['end'], model.units.ureg.millisecond)
        except KeyError:
            pass  # end is optional

        try:
            cytosolic_calcium_concentration_var = \
                model.get_symbol_by_ontology_term(OXMETA, "cytosolic_calcium_concentration")
        except KeyError:
            cytosolic_calcium_concentration_var = None
            print("MODEL HAS NO cytosolic_calcium_concentration VARIABLE")

        # Getting the equations for const definitions for GetIIonic
        # Use an annotation on voltage to find V
        membrane_voltage_var = model.get_symbol_by_ontology_term(OXMETA, "membrane_voltage")

        # Get stimulus current
        membrane_stimulus_current_var = model.get_symbol_by_ontology_term(OXMETA, "membrane_stimulus_current")
        # Get stimulus current units
        membrane_stimulus_current_units = model.units.summarise_units(membrane_stimulus_current_var)

        # function used to order state variables in the same way as pycml does (for easy comparison)
        def state_var_key_order(membrane_voltage_var, cai_var, var):
            if var == membrane_voltage_var:
                return MEMBRANE_VOLTAGE_INDEX
            elif var == cai_var:
                return CYTOSOLIC_CALCIUM_CONCENTRATION
            else:
                return MEMBRANE_VOLTAGE_INDEX + CYTOSOLIC_CALCIUM_CONCENTRATION + 1

        # Sort the state variables
        state_vars = sorted(model.get_state_symbols(),
                            key=lambda state_var: state_var_key_order(membrane_voltage_var,
                                                                      cytosolic_calcium_concentration_var, state_var))
        # use the RHS of the ODE defining V
        ionic_derivatives = [x for x in model.get_derivative_symbols() if x.args[0] == membrane_voltage_var]
        # figure out the currents (by finding variables with the same units
        # as the stimulus iirc) (without lexicographical_sort)
        equations_for_ionic_vars = model.get_equations_for(ionic_derivatives, False)

#        # model.get_equations_for gets them back ordered topographicly we want them in reverse topographical order
        equations_for_ionic_vars.reverse()

        # Only equations with the same (lhs) units as the membrane_stimulus_current are needed.
        # Also exclude the membrane_stimulus_current variable itself,
        # and cellml_default_stimulus_equations (if he model has those)
        equations_for_ionic_vars = [x
                      for x in equations_for_ionic_vars
                      if x.lhs != membrane_stimulus_current_var
                      and (cellml_default_stimulus_equations is None
                      or [x] not in cellml_default_stimulus_equations.values())
                      and model.units.summarise_units(x.lhs) == membrane_stimulus_current_units]

        # Once we have the ionic variables and their equations, we also need to add equtions that define symbols used in those
        used_symbols = []
        extended_equations_for_ionic_vars = []
        for ionic_var_eq in equations_for_ionic_vars:
            variable_eqs = model.get_equations_for([ionic_var_eq.lhs], False)
            for eq in variable_eqs:
                if eq.lhs not in used_symbols:
                    extended_equations_for_ionic_vars.append(eq)
                    used_symbols.append(eq.lhs)

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

        ionic_interface_vars = [v.lhs for v in equations_for_ionic_vars]
        formatted_ionic_interface_vars = []
        for ionic_interface_var in equations_for_ionic_vars:
            formatted_ionic_interface_vars.append({
                                         'lhs': var_chaste_interface_printer.doprint(ionic_interface_var.lhs),
                                         'rhs': var_printer.doprint(ionic_interface_var.lhs),
                                         'units': str(model.units.summarise_units(ionic_interface_var.lhs)),
                                         'conversion_factor': model.units.get_conversion_factor(1 * model.units.summarise_units(ionic_interface_var.lhs), ionic_current_units)
                                        })
       
        # Format the state variables with the initial values and units
        formatted_state_vars = [{'var': var_chaste_interface_printer.doprint(var),
                                 'initial_value': str(model.get_initial_value(var)),
                                 'units': str(model.units.summarise_units(var))} 
                                 for var in state_vars]

        # Get the free variable for the model
        free_var = model.get_free_variable_symbol()
        free_variable = {'name': name_printer.doprint(free_var),
                         'units': model.units.summarise_units(free_var),
                         'system_name': model.name}

        ode_system_information = [{'name': model.get_ontology_terms_by_symbol(var, OXMETA)[0] if model.has_ontology_annotation(var, OXMETA) else name_printer.doprint(var),
                                   'initial_value': str(model.get_initial_value(var)),
                                    'units': str(model.units.summarise_units(var))}
                                    for var in state_vars]

        # Generate hpp for model
        template = cg.load_template('chaste', 'normal_model.hpp')
        with open(hhp_file_path, 'w') as f:
            f.write(template.render({
                'model_name_from_file': model_name_from_file,
                'class_name': class_name,
                'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'cellml_default_stimulus_equations': cellml_default_stimulus_equations,
                'use_get_intracellular_calcium_concentration': use_get_intracellular_calcium_concentration,
            }))

        # Generate cpp for model
        template = cg.load_template('chaste', 'normal_model.cpp')
        with open(cpp_file_path, 'w') as f:
            f.write(template.render({
                'model_name_from_file': model_name_from_file,
                'class_name': class_name,
                'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'cellml_default_stimulus_equations': formatted_cellml_default_stimulus_equations,
                'use_get_intracellular_calcium_concentration': use_get_intracellular_calcium_concentration,
                'membrane_voltage_index': MEMBRANE_VOLTAGE_INDEX,
                'cytosolic_calcium_concentration_index': CYTOSOLIC_CALCIUM_CONCENTRATION,
                'state_vars': formatted_state_vars,
                'ionic_vars': formatted_ionic_vars,
                'ionic_interface_vars': formatted_ionic_interface_vars,
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
