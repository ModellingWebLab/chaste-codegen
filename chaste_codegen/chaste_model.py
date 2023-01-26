import time

from sympy import Derivative, Float

import chaste_codegen as cg
from chaste_codegen._rdf import OXMETA, PYCMLMETA, get_variables_transitively
from chaste_codegen.model_with_conversions import (
    CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX,
    MEMBRANE_VOLTAGE_INDEX,
    get_equations_for,
    state_var_key_order,
)


TIME_STAMP = time.strftime('%Y-%m-%d %H:%M:%S')


def get_variable_name(s, interface=False):
    """Get the correct variable name based on the variable and whether it should be in the chaste_interface."""
    s_name = s.expr if isinstance(s, Derivative) else s
    s_name = str(s_name).replace('$', '__')
    if not s_name.startswith('_'):
        s_name = '_' + s_name

    if isinstance(s, Derivative):
        return 'd_dt_chaste_interface_var' + s_name
    elif interface:
        return 'var_chaste_interface_' + s_name
    else:
        return 'var' + s_name


class ChasteModel(object):
    """ Holds information about a cellml model for which chaste code is to be generated.

    It also holds relevant formatted equations and derivatives.
    Please Note: this calass cannot generate chaste code directly, instead use a subclass of the model type
    """

    DEFAULT_EXTENSIONS = ('.hpp', '.cpp')

    def __enter__(self):
        """ Pre analysis preparation. Required to be able to use model in context (with).
        Defined for overwriting in sub-classes if pre-processing is needed to use the model for code generation. """
        return self

    def __init__(self, model, file_name, **kwargs):
        """ Initialise a ChasteModel instance
        Arguments

        ``model``
            A :class:`cellmlmanip.Model` object.
        ``file_name``
            The name you want to give your generated files WITHOUT the .hpp and .cpp extension
            (e.g. aslanidi_model_2009 leads to aslanidi_model_2009.cpp and aslanidi_model_2009.hpp)
        """

        # Store default options
        self.file_name = file_name
        self._templates = []
        self.generated_code = []

        # Items to print as chaste_interface_...
        self._in_interface = set()

        self._model = model

        self._stimulus_equations = self._get_stimulus()
        self.use_modifiers = kwargs.get('use_modifiers', False)
        self._modifiers = self._model.modifiers if self.use_modifiers else ()

        self._extended_ionic_vars = self._get_extended_ionic_vars()
        self._derivative_equations = self._get_derivative_equations()

        self._derivative_eqs_excl_voltage = self._get_derivative_eqs_excl_voltage()
        self._derivative_eqs_voltage = self._get_derivative_eqs_voltage()

        self._derived_quant = self._get_derived_quant()
        self._derived_quant_eqs = self._get_derived_quant_eqs()

        # Update items to print as chaste_interface_...
        self._in_interface.update(self._model.state_vars)
        self._in_interface.add(self._model.time_variable)
        self._in_interface.add(self._model.i_ionic_lhs)
        self._in_interface.update(self._model.stimulus_params)
        # Sort before printing
        # Sort the state variables, in similar order to pycml to prevent breaking existing code.
        # V and cytosolic_calcium_concentration need to be set for the sorting
        # the state variables, in similar order to pycml to prevent breaking existing code.
        self._state_vars = sorted(self._model.state_vars,
                                  key=lambda state_var: state_var_key_order(model, state_var))
        self._modifiable_parameters = sorted(self._model.modifiable_parameters,
                                             key=lambda v: self._model.get_display_name(v, OXMETA))
        self._modifiable_parameter_lookup = {p: str(i) for i, p in enumerate(self._modifiable_parameters)}

        # retrieve probabilities that don't stay in 0 ... 1 range and shouldn't be checked
        not_quite_probabilities = \
            set(get_variables_transitively(self._model, (OXMETA, 'not_a_probability_even_though_it_should_be')))

        # store indices of concentrations & probabilities
        self.concentrations = set(get_variables_transitively(self._model, (OXMETA, 'Concentration')))
        self.probabilities = set(get_variables_transitively(self._model,
                                                            (OXMETA, 'Probability'))) - not_quite_probabilities

        # Printing
        self._pre_print_hook()
        self._add_printers()
        self._formatted_state_vars, self._use_verify_state_variables = self._format_state_variables()

        # dict of variables to pass to the jinja2 templates
        self._vars_for_template = \
            {'base_class': '',
             'model_type': '',
             # indicate how to declare state vars and values
             'vector_decl': 'std::vector<double>&',
             'converter_version': cg.__version__,
             'model_name': self._model.name,
             'file_name': self.file_name,
             'class_name': kwargs.get('class_name', 'ModelFromCellMl'),
             'header_ext': kwargs.get('header_ext', '.hpp'),
             'dynamically_loadable': kwargs.get('dynamically_loadable', False),
             'use_model_factory': kwargs.get('use_model_factory', False),
             'cellml_base': kwargs.get('cellml_base', ''),
             'modifiers': self._format_modifiers(),
             'generation_date': TIME_STAMP,
             'use_get_intracellular_calcium_concentration':
                 self._model.cytosolic_calcium_concentration_var in self._model.state_vars,
             'membrane_voltage_index': MEMBRANE_VOLTAGE_INDEX,
             'cytosolic_calcium_concentration_index':
                 self._state_vars.index(self._model.cytosolic_calcium_concentration_var)
                 if self._model.cytosolic_calcium_concentration_var in self._model.state_vars
                 else CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX,

             'modifiable_parameters': self._format_modifiable_parameters(),
             'state_vars': self._formatted_state_vars,
             'use_verify_state_variables': self._use_verify_state_variables,
             'default_stimulus_equations': self._format_default_stimulus(),
             'ionic_vars': self._format_ionic_vars(),
             'y_derivatives': self._format_y_derivatives(),
             'y_derivative_equations': self._format_derivative_equations(self._derivative_equations),
             'free_variable': self._format_free_variable(),
             'ode_system_information': self._format_system_info(),
             'named_attributes': self._format_named_attributes(),
             'derived_quantities': self._format_derived_quant(),
             'derived_quantity_equations': self._format_derived_quant_eqs()}

    def _get_initial_value(self, var):
        """Returns the initial value of a variable if it has one, 0 otherwise"""
        # state vars have an initial value parameter defined
        initial_value = 0
        if var in self._model.state_vars:
            initial_value = getattr(var, 'initial_value', 0)
        else:
            eqs = get_equations_for(self._model, (var,), filter_modifiable_parameters_lhs=False, optimise=False)
            # If there is a defining equation, there should be just 1 equation and it should be of the form var = value
            if len(eqs) == 1 and isinstance(eqs[0].rhs, Float):
                initial_value = eqs[0].rhs
        return initial_value

    def _get_stimulus(self):
        return self._model.stimulus_equations

    def _get_extended_ionic_vars(self):
        """ Get the equations defining the ionic derivatives and all dependant equations"""
        return self._model.extended_ionic_vars

    def _get_derivative_equations(self):
        """ Get equations defining the derivatives including V (self._model.membrane_voltage_var)"""
        return self._model.derivative_equations

    def _get_derivative_eqs_excl_voltage(self):
        """ Get equations defining the derivatives excluding V (self._model.membrane_voltage_var)"""
        # stat with derivatives without voltage and add all equations used
        eqs = set()
        deriv_and_eqs = set(filter(lambda deriv: deriv.args[0] != self._model.membrane_voltage_var,
                            self._model.y_derivatives))
        num_derivatives = -1
        while num_derivatives < len(deriv_and_eqs):
            num_derivatives = len(deriv_and_eqs)
            eqs = set(filter(lambda eq: eq.lhs in deriv_and_eqs, self._derivative_equations))
            deriv_and_eqs.update(self._model.find_variables_and_derivatives([eq.rhs for eq in eqs]))
        return eqs

    def _get_derivative_eqs_voltage(self):
        """ Get equations defining the derivatives for V only (self._model.membrane_voltage_var)"""
        # start with derivatives for V only and add all equations used
        eqs = set()
        derivatives = set(filter(lambda deriv: deriv.args[0] == self._model.membrane_voltage_var,
                          self._model.y_derivatives))
        num_derivatives = -1
        while num_derivatives < len(derivatives):
            num_derivatives = len(derivatives)
            eqs = set(filter(lambda eq: eq.lhs in derivatives, self._derivative_equations))
            for eq in eqs:
                derivatives.update(self._model.find_variables_and_derivatives((eq.rhs, )))
        return eqs

    def _get_derived_quant(self):
        """ Get all derived quantities

        Stimulus currents are ignored and the result is sorted by display name"""
        tagged = set(self._model.get_variables_by_rdf((PYCMLMETA, 'derived-quantity'), 'yes', sort=False))
        # Get annotated derived quantities excluding stimulus current params
        annotated = set(filter(lambda q: q not in self._model.stimulus_params
                               and self._model.has_ontology_annotation(q, OXMETA),
                               self._model.get_derived_quantities(sort=False)))

        return sorted(tagged | annotated, key=lambda v: self._model.get_display_name(v, OXMETA))

    def _get_derived_quant_eqs(self):
        """ Get the defining equations for derived quantities"""
        return get_equations_for(self._model, self._derived_quant)

    def _pre_print_hook(self):
        """ The method provides a hook for subclasses to be able to add additional computation
            before printing of the output starts"""
        pass

    def _add_printers(self, lookup_table_function=lambda e: None):
        """ Initialises Printers for outputting chaste code. """
        # Printer for printing chaste regular variable assignments (var_ prefix)
        # Print variables in interface as var_chaste_interface
        # (state variables, time, lhs of default_stimulus eqs, i_ionic and lhs of y_derivatives)
        # Print modifiable parameters as mParameters[index]
        self._printer = \
            cg.ChastePrinter(lambda variable:
                             get_variable_name(variable, variable in self._in_interface)
                             if variable not in self._model.modifiable_parameters
                             else self._print_modifiable_parameters(variable),
                             lambda deriv: get_variable_name(deriv),
                             lookup_table_function)

        # Printer for printing variable in comments e.g. for ode system information
        self._name_printer = cg.ChastePrinter(lambda variable: get_variable_name(variable))

    def _print_rhs_with_modifiers(self, modifier, eq, modifiers_with_defining_eqs=set()):
        """ Print modifiable parameters in the correct format for the model type"""
        # Make sure printer doesn't print variables as modifiers if they are state vars or eq lhs
        # as those are handled by _print_rhs_with_modifiers
        modifier_printer = \
            cg.ChastePrinter(lambda variable:
                             self._format_modifier(variable) + '->Calc(' +
                             self._printer.doprint(variable) + ', ' +
                             self._printer.doprint(self._model.time_variable) + ')'
                             if variable in self._modifiers and variable not in modifiers_with_defining_eqs
                             else self._printer.doprint(variable),
                             lambda deriv: self._printer.doprint(deriv),
                             self._printer.lookup_table_function)
        if modifier in self._modifiers:
            return self._format_modifier(modifier) + '->Calc(' + modifier_printer.doprint(eq) + ', ' + \
                self._printer.doprint(self._model.time_variable) + ')'
        return modifier_printer.doprint(eq)

    def _format_modifier(self, var):
        """ Formatting of modifier for printing"""
        return 'mp_' + self._model.get_display_name(var) + '_modifier'

    def _format_modifiers(self):
        """ Format the modifiers for printing to chaste code"""
        return [{'name': self._model.modifier_names[param],
                 'modifier': self._format_modifier(param)}
                for param in self._modifiers]

    def _print_modifiable_parameters(self, variable):
        """ Print modifiable parameters in the correct format for the model type"""
        return 'mParameters[' + self._modifiable_parameter_lookup[variable] + ']'

    def _format_modifiable_parameters(self):
        """ Format the modifiable parameter for printing to chaste code"""
        return [{'units': self._model.units.format(self._model.units.evaluate_units(param)),
                 'comment_name': self._name_printer.doprint(param),
                 'name': self._model.get_display_name(param, OXMETA),
                 'initial_value': self._printer.doprint(self._get_initial_value(param))}
                for param in self._modifiable_parameters]

    def _format_rY_entry(self, index):
        """ Formatting of rY entry for printing"""
        return 'rY[' + str(index) + ']'

    def _format_rY_lookup(self, index, var, use_modifier=True):
        """ Formatting of rY lookup for printing"""
        entry = self._format_rY_entry(index)
        if use_modifier and var in self._modifiers:
            entry = self._format_modifier(var) +\
                '->Calc(' + entry + ', ' + self._printer.doprint(self._model.time_variable) + ')'
        if var == self._model.membrane_voltage_var:
            entry = '(mSetVoltageDerivativeToZero ? this->mFixedVoltage : ' + entry + ')'
        return entry

    def _format_state_variables(self):
        """ Get equations defining the derivatives including  V (self._model.membrane_voltage_var)"""
        def get_range_annotation(subject, annotation_tag):
            """ Get range-low and range-high annotation for to verify state variables. """
            if subject.cmeta_id is not None:
                range_annotation = self._model.get_rdf_annotations(subject='#' + subject.cmeta_id,
                                                                   predicate=(PYCMLMETA, annotation_tag))
                annotation = next(range_annotation, None)
                assert next(range_annotation, None) is None, 'Expecting 0 or 1 range annotation'
                if annotation is not None:
                    return float(annotation[2])
            return ''

        # Get all used variables for eqs for ionic variables to be able to indicate if a state var is used
        ionic_var_variables = set()
        for eq in self._extended_ionic_vars:
            ionic_var_variables.update(eq.rhs.free_symbols)

        # Get all used variables for y derivs to be able to indicate if a state var is used
        y_deriv_variables = set()
        for eq in self._derivative_equations:
            y_deriv_variables.update(eq.rhs.free_symbols)

        # Get all used variables for y derivs to be able to indicate if a state var is used
        voltage_deriv_variables = set()
        for eq in self._derivative_eqs_voltage:
            voltage_deriv_variables.update(eq.rhs.free_symbols)

        # Get all used variables for derivatives_excl_voltage to be able to indicate if a state var is used
        deriv_excl_voltage_variables = set()
        for eq in self._derivative_eqs_excl_voltage:
            deriv_excl_voltage_variables.update(eq.rhs.free_symbols)

        # Get all used variables for eqs for derived quantities variables to be able to indicate if a state var is used
        derived_quant_variables = set(filter(lambda q: q in self._model.state_vars, self._derived_quant))
        for eq in self._derived_quant_eqs:
            derived_quant_variables.update(eq.rhs.free_symbols)

        formatted_state_vars = \
            [{'var': self._printer.doprint(var[1]),
              'annotated_var_name': self._model.get_display_name(var[1], OXMETA),
              'rY_lookup': self._format_rY_lookup(var[0], var[1]),
              'rY_lookup_no_modifier': self._format_rY_lookup(var[0], var[1], use_modifier=False),
              'initial_value': str(self._get_initial_value(var[1])),
              'modifier': self._format_modifier(var[1]) if var[1] in self._modifiers else None,
              'units': self._model.units.format(self._model.units.evaluate_units(var[1])),
              'in_ionic': var[1] in ionic_var_variables,
              'in_y_deriv': var[1] in y_deriv_variables,
              'in_deriv_excl_voltage': var[1] in deriv_excl_voltage_variables,
              'in_voltage_deriv': var[1] in voltage_deriv_variables,
              'in_derived_quant': var[1] in derived_quant_variables,
              'range_low': get_range_annotation(var[1], 'range-low'),
              'range_high': get_range_annotation(var[1], 'range-high'),
              'sympy_var': var[1],
              'state_var_index': self._state_vars.index(var[1]),
              'is_concentration': var[1] in self.concentrations,
              'is_probability': var[1] in self.probabilities}
             for var in enumerate(self._state_vars)]

        use_verify_state_variables = next(filter(lambda eq: eq['range_low'] != '' or eq['range_high'] != '',
                                                 formatted_state_vars), None) is not None
        return (formatted_state_vars, use_verify_state_variables)

    def _format_default_stimulus(self):
        """ Format eqs for stimulus_current for outputting to chaste code"""
        default_stim = {'equations':
                        [{'lhs': self._printer.doprint(eq.lhs),
                          'rhs': self._printer.doprint(eq.rhs),
                          'units': self._model.units.format(self._model.units.evaluate_units(eq.lhs)),
                          'lhs_modifiable': eq.lhs in self._model.modifiable_parameters}
                         for eq in self._stimulus_equations]}
        for param in self._model.stimulus_params:
            default_stim[self._model.get_display_name(param, OXMETA)] = self._printer.doprint(param)

        return default_stim

    def _format_ionic_vars(self):
        """ Format equations and dependant equations ionic derivatives"""
        # Format the state ionic variables
        return [{'lhs': self._printer.doprint(eq.lhs), 'rhs': self._printer.doprint(eq.rhs),
                 'units': self._model.units.format(self._model.units.evaluate_units(eq.lhs))}
                for eq in self._extended_ionic_vars]

    def _format_y_derivatives(self):
        """ Format y_derivatives for writing to chaste output"""
        self._in_interface.update(self._model.y_derivatives)
        return [self._printer.doprint(deriv) for deriv in self._model.y_derivatives]

    def _format_derivative_equations(self, derivative_equations):
        """ Format derivative equations for chaste output"""
        # Make sure printer doesn't print variables as modifiers if they are state vars or eq lhs
        # as those are handled by _print_rhs_with_modifiers
        modifiers_with_defining_eqs = set((eq.lhs for eq in derivative_equations)) | self._model.state_vars
        # exclude ionic currents
        formatted_deriv_eqs = [self.format_derivative_equation(eq, modifiers_with_defining_eqs)
                               for eq in derivative_equations]
        return formatted_deriv_eqs

    def format_derivative_equation(self, eq, modifiers_with_defining_eqs):
        """ Format an individual derivative equation
            specified so that other model types can specify more detailed printing """
        return {'lhs': self._printer.doprint(eq.lhs),
                'rhs': self._print_rhs_with_modifiers(eq.lhs, eq.rhs, modifiers_with_defining_eqs),
                'sympy_lhs': eq.lhs,
                'sympy_rhs': eq.rhs,
                'units': self._model.units.format(self._model.units.evaluate_units(eq.lhs)),
                'in_eqs_excl_voltage': eq in self._derivative_eqs_excl_voltage,
                'in_membrane_voltage': eq in self._derivative_eqs_voltage,
                'is_voltage': isinstance(eq.lhs, Derivative) and
                eq.lhs.args[0] == self._model.membrane_voltage_var}

    def _format_free_variable(self):
        """ Format free variable for chaste output"""
        return {'name': self._model.get_display_name(self._model.time_variable, OXMETA),
                'units': self._model.units.format(self._model.units.evaluate_units(self._model.time_variable)),
                'system_name': self._model.name,
                'var_name': self._printer.doprint(self._model.time_variable)}

    def _format_system_info(self):
        """ Format general ode system info for chaste output"""
        return [{'name': self._model.get_display_name(var[1], OXMETA),
                 'initial_value': str(self._get_initial_value(var[1])),
                 'units': self._model.units.format(self._model.units.evaluate_units(var[1])),
                 'rY_lookup': self._format_rY_entry(var[0])}
                for var in enumerate(self._state_vars)]

    def _format_named_attributes(self):
        """ Format named attributes for chaste output"""
        named_attributes = []
        named_attrs = self._model.get_rdf_annotations(subject=self._model.rdf_identity,
                                                      predicate=(PYCMLMETA, 'named-attribute'))
        for s, p, attr in named_attrs:
            name = self._model.get_rdf_value(subject=attr, predicate=(PYCMLMETA, 'name'))
            value = self._model.get_rdf_value(subject=attr, predicate=(PYCMLMETA, 'value'))
            named_attributes.append({'name': name, 'value': value})

        named_attributes.sort(key=lambda a: a['name'])
        return named_attributes

    def _format_derived_quant(self):
        return [{'units': self._model.units.format(self._model.units.evaluate_units(quant)),
                 'var': self._printer.doprint(quant),
                 'name': self._model.get_display_name(quant, OXMETA)}
                for quant in self._derived_quant]

    def _format_derived_quant_eqs(self):
        """ Format equations for derived quantities based on current settings"""
        modifiers_with_defining_eqs = set((eq.lhs for eq in self._derived_quant_eqs)) | self._model.state_vars
        formatted_eq = [{'lhs': self._printer.doprint(eq.lhs),
                         'rhs': self._print_rhs_with_modifiers(eq.lhs, eq.rhs, modifiers_with_defining_eqs),
                         'sympy_lhs': eq.lhs,
                         'units': self._model.units.format(str(self._model.units.evaluate_units(eq.lhs)))}
                        for eq in self._derived_quant_eqs]
        return formatted_eq

    def generate_chaste_code(self):
        """ Generates and stores chaste code"""
        for templ in self._templates:
            template = cg.load_template(templ)
            self.generated_code.append(template.render(self._vars_for_template))

    def __exit__(self, type, value, traceback):
        """ Clean-up. Required to be able to use model in context (with).
        Defined for overwriting in sub-classes if state needs to be reset for subsequent code generation. """
        pass
