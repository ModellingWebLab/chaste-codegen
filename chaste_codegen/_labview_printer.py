from sympy import Not

from chaste_codegen._chaste_printer import ChastePrinter


class LabviewPrinter(ChastePrinter):
    """
    Converts Sympy expressions to strings for use in Chaste code generation.

    To use, create a :class:`ChastePrinter` instance, and call its method
    :meth:`doprint()` with a Sympy expression argument.

    Arguments:

    ``symbol_function``
        A function that converts symbols to strings (variable names).
    ``derivative_function``
        A function that converts derivatives to strings.
    ``lookup_table_function``
        A function that prints lookup table expressions or returns None if the expression is not in the lookup table.

    """
    _function_names = {
        'abs_': 'abs',
        'acos_': 'acos',
        'cos_': 'cos',
        'exp_': 'exp',
        'sqrt_': 'sqrt',
        'sin_': 'sin',

        'Abs': 'abs',
        'acos': 'acos',
        'acosh': 'acosh',
        'asin': 'asin',
        'asinh': 'asinh',
        'atan': 'atan',
        'atan2': 'atan2',
        'atanh': 'atanh',
        'ceiling': 'ceil',
        'cos': 'cos',
        'cosh': 'cosh',
        'exp': 'exp',
        'expm1': 'expm1',
        'factorial': 'factorial',
        'floor': 'floor',
        'log': 'log',
        'log10': 'log10',
        # 'log1p': 'log1p', # does not exist
        'log2': 'log2',
        'sin': 'sin',
        'sinh': 'sinh',
        'sqrt': 'sqrt',
        'tan': 'tan',
        'tanh': 'tanh',

        'sign': 'sign',
    }
    _extra_trig_names = {
        'sec': 'cos',
        'csc': 'sin',
        'cot': 'tan',
        'sech': 'cosh',
        'csch': 'sinh',
        'coth': 'tanh',
    }
    _extra_inverse_trig_names = {
        'asec': 'acos',
        'acsc': 'asin',
        'acot': 'atan',
        'asech': 'acosh',
        'acsch': 'asinh',
        'acoth': 'atanh',
    }

    _literal_names = {
        'e': 'exp(1)',
        'nan': 'nan',
        'pi': 'pi',
    }

    def _print_Not(self, expr):
        """ handles Not(e) """
        return '~(' + self._print(Not(expr)) + ')'

    def _print_Relational(self, expr):
        """ Handles equality and inequalities. """
        return super()._print_Relational(expr).replace('!=', '~=')
