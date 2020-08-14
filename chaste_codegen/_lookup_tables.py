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


class LookupTables:
    """ Holds information about lookuptables and methods to analyse the model for lookup tables.
    """

    def __init__(self, model, lookup_metadata_tags=('membrane_voltage', 'cytosolic_calcium_concentration'),
                 expensive_functions=(exp, log, ln, sin, cos, tan, sec, csc, cot, sinh, cosh, tanh, sech, csch, coth,
                                      asin, acos, atan, asinh, acosh, atanh, asec, acsc, acot, asech, acsch, acoth,
                                      exp_, acos_, cos_, sin_)):
        """ Initialise a LookUpTables instance
        Arguments

        ``model``
            A :class:`cellmlmanip.Model` object.
        ``lookup_metadata_tags``
            The metadata tags of the variables for which lookup tables are generated.
            (By default V and cytosolic_calcium_concentration).
        ``expensive_functions``
            The expensive functions for which lookup tables are generated.
        """
        self._model = model
        self._lut_expensive_functions = expensive_functions
        self._lookup_variables = set()
        self._lookup_table_expr = {}

        for tag in lookup_metadata_tags:
            try:
                self._lookup_variables.add(self._model.get_variable_by_ontology_term((OXMETA, tag)))
            except KeyError:
                pass  # variable not tagged in model

    def calc_lookup_tables(self, equations):

        for equation in equations:
            exp_func, vars_used = self._analyse_for_lut(equation.rhs)
            self._set_lookup_table_if_appropriate(exp_func, vars_used, equation.rhs)

    def _analyse_for_lut(self, expr):
        if isinstance(expr, Variable):
            return False, set([expr])
        elif len(expr.args) == 0:
            return False, set()  # other leaf
        elif expr in self._lookup_table_expr:  # expr already set for lookup table, no need to analyse
            return True, expr.free_symbols
        else:
            expensive_func = isinstance(expr, self._lut_expensive_functions)
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
