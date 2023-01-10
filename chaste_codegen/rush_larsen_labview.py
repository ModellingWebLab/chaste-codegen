from sympy.codegen.rewriting import log1p_opt

import chaste_codegen as cg
from chaste_codegen._labview_printer import LabviewPrinter
from chaste_codegen.rush_larsen_c import RushLarsenC, get_variable_name


class RushLarsenLabview(RushLarsenC):
    """ Holds template and information specific for the RushLarsen model type"""

    DEFAULT_EXTENSIONS = (None, '.txt')

    def __init__(self, model, file_name, **kwargs):
        # disable log1p optimisation as it's not supported by labview
        cg._optimize._LOG_OPTIMS = tuple(o for o in cg._optimize._LOG_OPTIMS if o != log1p_opt)

        super().__init__(model, file_name, **kwargs)
        self._templates = ['labview.txt']
        self._vars_for_template['model_type'] = 'RushLarsenLabview'

    def _add_printers(self, lookup_table_function=lambda e: None):
        """ Initialises Printers for outputting chaste code. """
        # Printer for printing chaste regular variable assignments (var_ prefix)
        # Print variables in interface as var_chaste_interface
        # (state variables, time, lhs of default_stimulus eqs, i_ionic and lhs of y_derivatives)
        # Print modifiable parameters as mParameters[index]
        self._printer = \
            LabviewPrinter(lambda variable:
                           get_variable_name(variable, variable in self._in_interface)
                           if variable not in self._model.modifiable_parameters
                           else self._print_modifiable_parameters(variable),
                           lambda deriv: get_variable_name(deriv),
                           lookup_table_function)

        # Printer for printing variable in comments e.g. for ode system information
        self._name_printer = LabviewPrinter(lambda variable: get_variable_name(variable))
