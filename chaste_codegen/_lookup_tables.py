import collections

from cellmlmanip.model import Variable
from sympy import (
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

from chaste_codegen._math_functions import (
    acos_,
    cos_,
    exp_,
    sin_,
)
from chaste_codegen._rdf import OXMETA


_EXPENSIVE_FUNCTIONS = (exp, log, ln, sin, cos, tan, sec, csc, cot, sinh, cosh, tanh, sech, csch, coth, asin, acos,
                        atan, asinh, acosh, atanh, asec, acsc, acot, asech, acsch, acoth, exp_, acos_, cos_, sin_)


class LookupTables:
    """ Holds information about lookuptables and methods to analyse the model for lookup tables.
    """

    def __init__(self, model):
        """ Initialise a LookUpTables instance
        ``model``
            A :class:`cellmlmanip.Model` object.
        ``printer``
            A :class:`sympy.printing.printer.Printer` object.
        """
        # Lookup vars is a tuple of [<metadata tag>, variable, [<lookup epxrs>], mTableMins, mTableSteps, mTableStepInverses,
        #                            mTableMaxs, <set_of_method_names_table_is_used_in>]
        self._lookup_parameters = (['membrane_voltage', None, [], -150.0001, 0.001, 1000.0, 199.9999, set()],
                                   ['cytosolic_calcium_concentration', None, [], 0.00001, 0.001, 1000.0, 30.00001, set()])

        self._model = model
        self._lookup_variables = set()
        self._lookup_table_expr = collections.OrderedDict()
        self._lookup_params_processed, self._lookup_params_printed = False, False

        self._method_printed = None

        for tag in self._lookup_parameters:
            try:
                var = self._model.get_variable_by_ontology_term((OXMETA, tag[0]))
                self._lookup_variables.add(var)
                tag[1] = var
            except KeyError:
                pass  # variable not tagged in model

    def calc_lookup_tables(self, equations):

        if self._lookup_params_processed:
            raise ValueError('Cannot calculate lookup tables after printing has started')

        for equation in equations:
            exp_func, vars_used = self._analyse_for_lut(equation.rhs)
            self._set_lookup_table_if_appropriate(exp_func, vars_used, equation.rhs)

    def _analyse_for_lut(self, expr):
        if isinstance(expr, Variable):
            return False, set([expr])
        elif len(expr.args) == 0:
            return False, set()  # other leaf
        elif expr in self._lookup_table_expr:  # expr already set for lookup table, no need to analyse
            return True, self._lookup_table_expr[expr]
        else:
            expensive_func = isinstance(expr, _EXPENSIVE_FUNCTIONS)
            vars_used_in_lut = set()
            args_func_vars = []
            for ex in expr.args:
                exp_func, vars_used = self._analyse_for_lut(ex)
                args_func_vars.append((exp_func, vars_used, ex))
                expensive_func = expensive_func or exp_func
                vars_used_in_lut.update(vars_used)

            if expensive_func and len(vars_used_in_lut) > 1:
                # there are arguments suitable for lookup table, but with different lookup table vars
                # so set each appropriate child as lookup table var if appropriate, but not this expr
                for exp_func, vars_used, ex in args_func_vars:
                    self._set_lookup_table_if_appropriate(exp_func, vars_used, ex)
                return False, vars_used_in_lut
            return expensive_func, vars_used_in_lut

    def _set_lookup_table_if_appropriate(self, exp_func, vars_used, expr):
        # Expressions are suitable for lut if:
        # - they have an expensive function
        # - they're not already set as suitable
        # - they only contain 1 variable and this variable is one of the lookup variables
        if exp_func and expr not in self._lookup_table_expr and \
                len(vars_used) == 1 and list(vars_used)[0] in self._lookup_variables:
            self._lookup_table_expr[expr] = vars_used

    def _process_lookup_parameters(self):
        if not self._lookup_params_processed:
            # Stick in a list of all expressions for the variable for easy access in the template
            for param in self._lookup_parameters:
                param[2] = list(filter(lambda k: param[1] in self._lookup_table_expr[k], self._lookup_table_expr))

            # Filter out the parameter set for which we didn't find any complicated expressions
            self._lookup_parameters = list(filter(lambda p: len(p[2]) > 0, self._lookup_parameters))
            self._lookup_params_processed = True

    def print_lookup_parameters(self, printer):
        # Don't use lookup tables to print these expressions
        if not self._lookup_params_printed:
            self._process_lookup_parameters()
            old_lookup_tables = printer.lookup_tables
            printer.lookup_tables = None
            for param in self._lookup_parameters:
                param[2] = list(map(lambda e: printer.doprint(e), param[2]))
                param[1] = printer.doprint(param[1])

            # reinstate lookup tables
            printer.lookup_tables = old_lookup_tables
            self._lookup_params_printed = True
        return self._lookup_parameters

    def is_lut_expr(self, expr):
        if self._lookup_params_printed:
            raise ValueError('Cannot process lookup expression after main table has been printed')
        self._process_lookup_parameters()
        return self._lookup_table_expr

    def print_lut_expr(self, expr):
        if self._lookup_params_printed:
            raise ValueError('Cannot print lookup expression after main table has been printed')

        self._process_lookup_parameters()
        if self._method_printed and expr in self._lookup_table_expr:
            variables = expr.free_symbols
            assert len(variables) == 1, "Lookup table expressions should have exactly 1 (lookup) variable"
            var = tuple(variables)[0]
            for i, param in enumerate(self._lookup_parameters):
                if param[1] is var:
                    param[7].add(self._method_printed)
                    return '_lt_' + str(i) + '_row[' + str(param[2].index(expr)) + ']'
        return None

    def method_being_printed(self, method_name):
        self._method_printed = method_name
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):##
        self._method_printed = None
