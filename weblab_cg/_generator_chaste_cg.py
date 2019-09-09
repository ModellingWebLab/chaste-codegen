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


def mkdir_p(path):
    """ Tries to create the path
    if teh path already exists it continuous without error"""
    try:
        os.makedirs(path)
    except FileExistsError:
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
        # name = parts[-1]
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


def format_equation_list(printer, equations, model,
                         units=None, secondary_units=None, secondary_unit_rhs_multiplier=""):
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
        if units is not None:
            try:
                current_units = model.units.summarise_units(eq.lhs)
                if current_units != units:
                    factor = model.units.get_conversion_factor(1 * current_units, units)
                    eq = sp.relational.Equality(eq.lhs, factor * eq.rhs)
            except errors.DimensionalityError:
                # var_chaste_interface__membrane__stim_amplitude might be in different units
                # and need multiplying with capacitance
                if secondary_units is not None and current_units != secondary_units:
                    factor = model.units.get_conversion_factor(1 * current_units, secondary_units)
                    eq = sp.relational.Equality(eq.lhs, factor * eq.rhs)
                rhs_multiplier = secondary_unit_rhs_multiplier
        equation_to_append = {
            'lhs': printer.doprint(eq.lhs),
            'rhs': printer.doprint(eq.rhs) + rhs_multiplier
        }
        if equation_to_append not in formatted_equations:
            formatted_equations.append(equation_to_append)
    return formatted_equations


def get_initial_value_comment(model, symbol):
    '''Create the comment for the cpp file that indicates the units and initial value for teh symbol'''
    initial_value = str(model.get_initial_value(symbol))
    unit_name = str(model.units.summarise_units(symbol))
    return "// Units: " + unit_name + "; Initial value: " + initial_value


def create_chaste_model(path, model_name_from_file, class_name, model, model_type=ChasteModelType.Normal):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.cpp`` and ``.cpp`` model
    for use with Chaste, and stores it at ``path``.

    Arguments

    ``path``
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
    path = os.path.join(path, model_type.name)

    # Make sure the folder exists for the type of model
    mkdir_p(path)

    # Add file name (based on model name)
    hhp_file_path = os.path.join(path, model_name_from_file + ".hpp")

    # Add file name (based on model name)
    cpp_file_path = os.path.join(path, model_name_from_file + ".cpp")

    # Add all neded units to the model (for conversion) if they don't yet exist
    model.units.add_preferred_custom_unit_name('uA_per_cm2', [{'prefix': 'micro', 'units': 'ampere'},
                                                              {'exponent': '-2', 'prefix': 'centi', 'units': 'metre'}])
    model.units.add_preferred_custom_unit_name('uA_per_uF', [{'prefix': 'micro', 'units': 'ampere'},
                                                             {'exponent': '-1', 'prefix': 'micro', 'units': 'farad'}])
    model.units.add_preferred_custom_unit_name('millisecond', [{'prefix': 'milli', 'units': 'second'}])
    model.units.add_preferred_custom_unit_name('millimolar', [{'units': 'mole', 'prefix': 'milli'},
                                                              {'units': 'litre', 'exponent': '-1'}])
    model.units.add_preferred_custom_unit_name('millivolt', [{'prefix': 'milli', 'units': 'volt'}])

    # Set up printer to be able to write equations
    # Get unique names for all symbols
    unames = get_unique_names(model)

    # get state variables
    state_vars = model.get_state_symbols()

    # Printer for printing chaste variable assignments
    printer = cg.ChastePrinter(lambda symbol, stae_vars = state_vars: ('var_chaste_interface__' if symbol in state_vars else 'var_') + unames[symbol],
                               lambda deriv: 'd_dt_' + (unames[deriv.expr]
                                                        if isinstance(deriv, sp.Derivative) else unames[deriv]))

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
                format_equation_list(printer, cellml_default_stimulus_equations['period'],
                                     model, model.units.ureg.millisecond)

            cellml_default_stimulus_equations['duration'] = \
                model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA,
                                        "membrane_stimulus_current_duration")], False)
            formatted_cellml_default_stimulus_equations['duration'] = \
                format_equation_list(printer, cellml_default_stimulus_equations['duration'],
                                     model, model.units.ureg.millisecond)

            cellml_default_stimulus_equations['amplitude'] = \
                model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA,
                                        "membrane_stimulus_current_amplitude")], False)
            formatted_cellml_default_stimulus_equations['amplitude'] = \
                format_equation_list(printer, cellml_default_stimulus_equations['amplitude'],
                                     model, model.units.ureg.uA_per_cm2, model.units.ureg.uA_per_uF,
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
                format_equation_list(printer, cellml_default_stimulus_equations['offset'],
                                     model, model.units.ureg.millisecond)
        except KeyError:
            pass  # offset is optional

        # optional default_stimulus_equation end
        try:
            cellml_default_stimulus_equations['end'] = \
                model.get_equations_for([model.get_symbol_by_ontology_term(OXMETA, "membrane_stimulus_current_end")], False)
            formatted_cellml_default_stimulus_equations['end'] = \
                format_equation_list(printer, cellml_default_stimulus_equations['end'], model,
                                     model.units.ureg.millisecond)
        except KeyError:
            pass  # end is optional

        # function used to order state variables in the same way as pycml does (for easy comparison)
        def state_var_key_order(membrane_voltage_var, cai_var, var):
            if var == membrane_voltage_var:
                return MEMBRANE_VOLTAGE_INDEX
            elif var == cai_var:
                return CYTOSOLIC_CALCIUM_CONCENTRATION
            else:
                return MEMBRANE_VOLTAGE_INDEX + CYTOSOLIC_CALCIUM_CONCENTRATION + 1

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

        # Get state variables
        state_vars = sorted(state_vars,
                            key=lambda state_var: state_var_key_order(membrane_voltage_var,
                                                                      cytosolic_calcium_concentration_var, state_var))

        # use the RHS of the ODE defining V
        ionic_derivatives = [x for x in model.get_derivative_symbols() if x.args[0] == membrane_voltage_var]
        # figure out the currents (by finding variables with the same units
        # as the stimulus iirc) (without lexicographical_sort)
        equations_for_ionic_vars = model.get_equations_for(ionic_derivatives, False)

        # model.get_equations_for gets them back ordered topographicly we want them in reverse topographical order
        equations_for_ionic_vars.reverse()

        # Only equations with teh same (lhs) units as the membrane_stimulus_current are needed.
        # Also exclude the membrane_stimulus_current variable itself,
        # and cellml_default_stimulus_equations (if he model has those)
        ionic_vars = [x
                      for x in equations_for_ionic_vars
                      if x.lhs != membrane_stimulus_current_var
                      and (cellml_default_stimulus_equations is None
                      or [x] not in cellml_default_stimulus_equations.values())
                      and model.units.summarise_units(x.lhs) == membrane_stimulus_current_units]

        used_symbols = []
        resulting_equations = []
        for ionic_var in ionic_vars:
            variable_eqs = model.get_equations_for([ionic_var.lhs], False)
            subs_dict = {}
            for var_eq in variable_eqs:
                # Skip the main equation (it will get added after substitutions)
                if var_eq != ionic_var:
                    # Keep variables with annotation
                    if var_eq.lhs not in used_symbols:
                        if model.get_ontology_term_by_symbol(OXMETA, var_eq.lhs) is not None:
                            resulting_equations.append(var_eq)
                        else:
                            subs_dict[var_eq.lhs] = var_eq.rhs
                    # Keep track of used equations as they might come up multiple ionic vars but shouldn't be redefined
                    used_symbols.append(var_eq.lhs)
            if subs_dict:
                ionic_var = sp.Eq(ionic_var.lhs, ionic_var.rhs.subs(subs_dict))
                
            resulting_equations.append(ionic_var)


        # Format the state ionic variables
        formatted_ionic_vars = format_equation_list(printer, resulting_equations, model)

        # Get conversion factor for vars need a conversion factor
        try:
            ionic_conversion_factor = \
                model.units.get_conversion_factor(1 * membrane_stimulus_current_units, model.units.ureg.uA_per_cm2)
            use_capacitance_i_ionic = False
        except errors.DimensionalityError:
            ionic_conversion_factor = \
                model.units.get_conversion_factor(1 * membrane_stimulus_current_units, model.units.ureg.uA_per_uF)
            use_capacitance_i_ionic = True

        # Get the initial values and units as a comment for the chanste output
        # Filter state vars that aren't used out for getIIonic
        state_vars_used_ionic = set()
        for ionic_var in ionic_vars:
            state_vars_used_ionic= state_vars_used_ionic.union(model.get_symbols(ionic_var))

        ionic_state_vars = [x for x in state_vars if x in state_vars_used_ionic]

        initial_value_comments_ionic_state_vars = [get_initial_value_comment(model, var) for var in ionic_state_vars]
        # Format the state variables
        ionic_state_vars = [printer.doprint(var) for var in ionic_state_vars]

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
                'ionic_state_vars': ionic_state_vars,
                'initial_value_comments_ionic_state_vars': initial_value_comments_ionic_state_vars,
                'ionic_vars': formatted_ionic_vars,
                'membrane_stimulus_current_units': membrane_stimulus_current_units,
                'ionic_conversion_factor': ionic_conversion_factor,
                'use_capacitance_i_ionic': use_capacitance_i_ionic,
            }))

    elif model_type == ChasteModelType.Opt:
        pass

    elif model_type == ChasteModelType.CvodeAnalyticJ:
        pass

    elif model_type == ChasteModelType.CvodeNumericalJ:
        pass

    elif model_type == ChasteModelType.BE:
        pass
