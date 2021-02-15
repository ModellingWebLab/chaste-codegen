import collections

from cellmlmanip.model import Quantity, Variable
from sympy import (
    Piecewise,
    Pow,
    Symbol,
    acos,
    acosh,
    acot,
    acoth,
    acsc,
    acsch,
    asec,
    asech,
    asin,
    asinh,
    atan,
    atanh,
    cos,
    cosh,
    cot,
    coth,
    csc,
    csch,
    exp,
    ln,
    log,
    sec,
    sech,
    sin,
    sinh,
    tan,
    tanh,
)

from chaste_codegen import LOGGER
from chaste_codegen._math_functions import (
    acos_,
    cos_,
    exp_,
    sin_,
)
from chaste_codegen._rdf import OXMETA


# The expensive functions the lookup table analysis searches for
_EXPENSIVE_FUNCTIONS = (exp, log, ln, sin, cos, tan, sec, csc, cot, sinh, cosh, tanh, sech, csch, coth, asin, acos,
                        atan, asinh, acosh, atanh, asec, acsc, acot, asech, acsch, acoth, exp_, acos_, cos_, sin_)


# tuple of ([<metadata tag>, mTableMins, mTableMaxs, mTableSteps], )
DEFAULT_LOOKUP_PARAMETERS = (['membrane_voltage', -250.0, 550.0, 0.001], )


class LookupTables:
    """ Holds information about lookuptables and methods to analyse the model for lookup tables.
    """

    def __init__(self, model, lookup_params=DEFAULT_LOOKUP_PARAMETERS):
        """ Initialise a LookUpTables instance
        :param model: A :class:`cellmlmanip.Model` object.
        :param lookup_params: Optional collection of lists: [[<metadata tag>, mTableMins, mTableMaxs, mTableSteps]]
        """
        self._lookup_parameters = tuple({'metadata_tag': param[0],
                                         'mTableMins': param[1],
                                         'mTableMaxs': param[2],
                                         'mTableSteps': param[3],
                                         'table_used_in_methods': set(),
                                         'var': None,
                                         'lookup_epxrs': []} for param in lookup_params)
        self._model = model
        self._lookup_variables = set()
        self._lookup_table_expr = collections.OrderedDict()
        self._lookup_params_processed, self._lookup_params_printed = False, False

        self._method_printed = None

        for param in self._lookup_parameters:
            try:
                var = self._model.get_variable_by_ontology_term((OXMETA, param['metadata_tag']))
                self._lookup_variables.add(var)
                param['var'] = var
            except KeyError:
                LOGGER.warning('A lookup table was specified for ' + param['metadata_tag'] +
                               ' but it is not tagged in the model, skipping!')

    def calc_lookup_tables(self, equations):
        """ Calculates and stores the lookup table expressions for equations.
            *Please Note:* cannot been called after `_process_lookup_parameters` has been calledt
            to prepare table for printing. """
        if self._lookup_params_processed:
            raise ValueError('Cannot calculate lookup tables after printing has started')

        for equation in equations:
            exp_func, vars_used, in_pw = self._analyse_for_lut(equation.rhs, isinstance(equation.rhs, Piecewise))
            self._set_lookup_table_if_appropriate(exp_func, vars_used, equation.rhs, in_pw)

    def _analyse_for_lut(self, expr, in_piecewise):
        """ Analyse whether an expression contains lookup table suitable (sub-_ expressions. """
        in_piecewise = in_piecewise or isinstance(expr, Piecewise)
        # Used variables are either Variable or Symbol but not Quantity
        used_vars = set(filter(lambda v: not isinstance(v, Quantity), expr.atoms(Variable, Symbol)))
        if not expr.has(*_EXPENSIVE_FUNCTIONS) or len(used_vars) == 0:
            return False, used_vars, in_piecewise  # other leaf
        elif expr in self._lookup_table_expr:  # expr already set for lookup table, no need to analyse
            lut_expr, in_pw = self._lookup_table_expr[expr]
            return True, lut_expr, in_piecewise or in_pw
        else:
            expensive_func = isinstance(expr, _EXPENSIVE_FUNCTIONS)
            vars_used_in_lut = set()
            args_func_vars = []
            for ex in expr.args:
                exp_func, vars_used, in_pw = self._analyse_for_lut(ex, in_piecewise)
                in_pw = in_pw or in_piecewise
                args_func_vars.append((exp_func, vars_used, ex, in_pw))
                expensive_func = expensive_func or exp_func
                vars_used_in_lut.update(vars_used)

            if expensive_func and len(vars_used_in_lut) > 1:
                # there are arguments suitable for lookup table, but with different lookup table vars
                # so set each appropriate child as lookup table var if appropriate, but not this expr
                for exp_func, vars_used, ex, in_pw in args_func_vars:
                    self._set_lookup_table_if_appropriate(exp_func, vars_used, ex, in_pw)
                return False, vars_used_in_lut, in_piecewise
            return expensive_func, vars_used_in_lut, in_piecewise

    def _set_lookup_table_if_appropriate(self, exp_func, vars_used, expr, in_pw):
        """ Store an expression to the lookup table if it's suitable. """
        # Expressions are suitable for lut if:
        # - they have an expensive function
        # - they're not already set as suitable
        # - they only contain 1 variable and this variable is one of the lookup variables

        # Prevent putting expressions of the form 1 / A since the expressions might cause a singularity in the table
        # since expressions being analised might the bottom of a GHK equation os similar
        if isinstance(expr, Pow) and expr.args[1] == -1.0:
            expr = expr.args[0]

        if exp_func and expr not in self._lookup_table_expr and \
                len(vars_used) == 1 and next(iter(vars_used)) in self._lookup_variables:
            self._lookup_table_expr[expr] = [vars_used, in_pw]
        elif expr in self._lookup_table_expr:  # Store whether the experssion appears in a Piecewise
            self._lookup_table_expr[expr][1] = self._lookup_table_expr[expr][1] or in_pw

    def _process_lookup_parameters(self):
        """ Prepare the stored lookup table parameters for generating chaste code.
            *Please Note:* no more calls to `calc_lookup_tables` can be made after this. """
        if not self._lookup_params_processed:
            # Stick in a list of all expressions for the variable for easy access in the template
            for param in self._lookup_parameters:
                param['lookup_epxrs'] = [(k, v[1]) for k, v in self._lookup_table_expr.items() if param['var'] in v[0]]

            # Filter out the parameter set for which we didn't find any complicated expressions
            self._lookup_parameters = list(filter(lambda p: len(p['lookup_epxrs']) > 0, self._lookup_parameters))
            self._lookup_params_processed = True

    def print_lut_expr(self, expr):
        """ prints an individual lookup expression e.g. `lt_row_0[0].
            *Please Note:* cannot be called after `print_lookup_parameters` has been called.
            :param expr: the expression to print.
            :return: a string with the printed lookup table expression if expr is in the lookup table
                     and a method hass been associated, else None.

            *Please Note:* in order to print lookup table expressions
                           please associate a method_name via `method_being_printed`,
                           if no method name is associated, None is returned."""
        if self._lookup_params_printed:
            raise ValueError('Cannot print lookup expression after main table has been printed')

        self._process_lookup_parameters()
        if self._method_printed and expr in self._lookup_table_expr:
            variables = expr.free_symbols & self._lookup_variables
            assert len(variables) == 1, "Lookup table expressions should have exactly 1 (lookup) variable"
            var = tuple(variables)[0]

            for i, param in enumerate(self._lookup_parameters):
                if param['var'] is var:
                    param['table_used_in_methods'].add(self._method_printed)
                    return '_lt_{}_row[{}]'.\
                        format(i, param['lookup_epxrs'].index((expr, self._lookup_table_expr[expr][1])))
        return None

    def print_lookup_parameters(self, printer):
        """ Formats the expressions int he table for printing to chaste code.
            *Please Note:* no more individual lookup table expressions can be priinted after this.
            :param printer: A :class:`sympy.printing.printer.Printer` object to print the lookup table with.
            :return: a list with which the lookup table can be generated:
                    [<metadata tag>, printed_variable, [<printed lookup epxrs>], mTableMins, mTableSteps,
                     mTableStepInverses, mTableMaxs, <set_of_method_names_table_is_used_in>]."""
        # Don't use lookup tables to print these expressions
        if not self._lookup_params_printed:
            self._process_lookup_parameters()
            old_lookup_table_func = printer.lookup_table_function
            printer.lookup_table_function = lambda e: None

            for param in self._lookup_parameters:
                # For lookup table expressions we store a tuple of (expr, "is this licated in a Piecewise")
                param['lookup_epxrs'] = list(map(lambda e: [printer.doprint(e[0]), e[1]], param['lookup_epxrs']))
                param['var'] = printer.doprint(param['var'])

            # reinstate lookup tables
            printer.lookup_table_function = old_lookup_table_func
            self._lookup_params_printed = True
        return self._lookup_parameters

    def method_being_printed(self, method_name):
        """ Method to associate a string with a set of lookup table expressions are being used.
            This method is intended to facilitate the template correctly initialising the required lookup table.
            This can also be used with the with statement to auto-reset the associated printing method_name

            For example:
            ``with self._lookup_tables.method_being_printed('GetIIonic'):
                  return super()._format_ionic_vars()``

            *Please Note:* associating a method_name is required,
                           without it printing individual lookup table expressions is disabled.
            *Please Note: The method is only saved if not already set,
                          therfore only reccording the outer most method when using in a nested scenario."""
        if not self._method_printed:
            self._method_printed = method_name
        return self

    def __enter__(self):
        """ enter method, needed to allow using with statements"""
        return self

    def __exit__(self, type, value, traceback):
        """Resets self._method_printed when a with statement goes out of scope."""
        self._method_printed = None
