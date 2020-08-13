from sympy import (exp, log, ln, sin, cos, tan, sec, csc, cot, sinh, cosh, tanh, sech, csch, coth, asin, acos, atan, asinh, acosh, atanh, asec, acsc, acot, asech, acsch, acoth)
# pow opt?


from chaste_codegen._rdf import OXMETA
from chaste_codegen._math_functions import (exp_, acos_, cos_, sin_)
from cellmlmanip.model import Variable



LOOKUP_VAR_METADATA_TAGS = ('membrane_voltage', 'cytosolic_calcium_concentration')

LUT_EXPENSIVE_FUNCTIONS = (exp, log, ln, sin, cos, tan, sec, csc, cot, sinh, cosh, tanh, sech, csch,
                           coth, asin, acos, atan, asinh, acosh, atanh, asec, acsc, acot, asech, acsch,
                           acoth, exp_, acos_, cos_, sin_)

_lookup_variables = set()
_lookup_table_expr = {}

def calc_lookup_tables(model, equations):
    for tag in LOOKUP_VAR_METADATA_TAGS:
        try:
            _lookup_variables.add(model.get_variable_by_ontology_term((OXMETA, tag)))
        except KeyError:
            pass  # variable not tagged in model

    for equation in equations:
        exp_func, vars_used = analyse_for_lut(equation.rhs)
        set_lookup_table_if_appropriate(exp_func, vars_used, equation.rhs)
    pass

def analyse_for_lut(expr):
    if isinstance(expr, Variable):
        return False, set([expr])
    elif len(expr.args) == 0:
        return False, set()  # other leaf
    else:
        expensive_func = isinstance(expr, LUT_EXPENSIVE_FUNCTIONS)
        vars_used_in_lut = set()
        args_func_vars = []
        for ex in expr.args:
            exp_func, vars_used = analyse_for_lut(ex)
            args_func_vars.append((exp_func, vars_used, ex))
            expensive_func = expensive_func or exp_func
            vars_used_in_lut.update(vars_used)
        
        if expensive_func and len(vars_used_in_lut) > 1:
            # there are arguments suitable for lookup table, but with different lookup table vars, so set each appropriate child aas lookup table var
            for exp_func, vars_used, ex in args_func_vars:
                set_lookup_table_if_appropriate(exp_func, vars_used, ex)
            return False, vars_used_in_lut
        return expensive_func, vars_used_in_lut

def set_lookup_table_if_appropriate(exp_func, vars_used, expr):
    if exp_func and len(vars_used) == 1 and list(vars_used)[0] in _lookup_variables:
        _lookup_table_expr[expr] = vars_used