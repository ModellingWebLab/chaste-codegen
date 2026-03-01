from cellmlmanip.printer import Printer
from sympy import (
    Mul,
    Not,
    Piecewise,
    Pow,
    Rational,
    S,
)
from sympy.core.mul import _keep_coeff
from sympy.printing import cxxcode
from sympy.printing.precedence import precedence

from chaste_codegen._chaste_printer_common import ChastePrinterCommon


C_MAX_INT = 2147483647
C_MIN_INT = -2147483647


class ChastePrinter(ChastePrinterCommon):
    """
    Converts Sympy expressions to strings for use in Chaste code generation.


    Expressions are generated in terms of the CHASTE_MATH name space, it is then the job
    of the Jinja template to ensure CHASTE_MATH points to the correct C++ namespace
    using the appropriate #include. E.g., #include "ChasteCpuMacros.hpp" converts these
    namespaced calls to std library calls


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
        'abs_': 'CHASTE_MATH::Abs',
        'acos_': 'CHASTE_MATH::Acos',
        'cos_': 'CHASTE_MATH::Cos',
        'exp_': 'CHASTE_MATH::Exp',
        'sqrt_': 'CHASTE_MATH::Sqrt',
        'sin_': 'CHASTE_MATH::Sin',

        'Abs': 'CHASTE_MATH::Abs',
        'acos': 'CHASTE_MATH::Acos',
        'acosh': 'CHASTE_MATH::Acosh',
        'asin': 'CHASTE_MATH::Asin',
        'asinh': 'CHASTE_MATH::Asinh',
        'atan': 'CHASTE_MATH::Atan',
        'atan2': 'CHASTE_MATH::Atan2',
        'atanh': 'CHASTE_MATH::Atanh',
        'ceiling': 'CHASTE_MATH::Ceil',
        'cos': 'CHASTE_MATH::Cos',
        'cosh': 'CHASTE_MATH::Cosh',
        'exp': 'CHASTE_MATH::Exp',
        'expm1': 'CHASTE_MATH::Expm1',
        'factorial': 'CHASTE_MATH::Factorial',
        'floor': 'CHASTE_MATH::Floor',
        'log': 'CHASTE_MATH::Log',
        'log10': 'CHASTE_MATH::Log10',
        'log1p': 'CHASTE_MATH::Log1p',
        'log2': 'CHASTE_MATH::Log2',
        'sin': 'CHASTE_MATH::Sin',
        'sinh': 'CHASTE_MATH::Sinh',
        'sqrt': 'CHASTE_MATH::Sqrt',
        'tan': 'CHASTE_MATH::Tan',
        'tanh': 'CHASTE_MATH::Tanh',

        'sign': 'CHASTE_MATH::Sign',
        
        'GetIntracellularAreaStimulus': 'CHASTE_STIM',
        'HeartConfig::Instance()->GetCapacitance': 'CHASTE_CAP',
        'GetExperimentalVoltageAtTimeT': 'CHASTE_EXP_VOLT'
    }

    _extra_trig_names = {
        'sec': 'CHASTE_MATH::Cos',
        'csc': 'CHASTE_MATH::Sin',
        'cot': 'CHASTE_MATH::Tan',
        'sech': 'CHASTE_MATH::Cosh',
        'csch': 'CHASTE_MATH::Sinh',
        'coth': 'CHASTE_MATH::Tanh',
    }

    _extra_inverse_trig_names = {
        'asec': 'CHASTE_MATH::Acos',
        'acsc': 'CHASTE_MATH::Asin',
        'acot': 'CHASTE_MATH::Atan',
        'asech': 'CHASTE_MATH::Acosh',
        'acsch': 'CHASTE_MATH::Asinh',
        'acoth': 'CHASTE_MATH::Atanh',
    }

    _literal_names = {
        'e': 'CHASTE_CONST(CHASTE_MATH::E)',
        'nan': 'CHASTE_CONST(CHASTE_MATH::NaN)',
        'pi': 'CHASTE_CONST(CHASTE_MATH::Pi)',
    }

    def _print_ordinary_pow(self, expr):
        """ Handles Pow(), handles just ordinary powers without division."""
        p = precedence(expr)
        if expr.exp == 0.5:
            return 'CHASTE_MATH::Sqrt(' + self._bracket(expr.base, p) + ')'
        return 'CHASTE_MATH::Pow(' + self._bracket(expr.base, p) + ', ' + self._bracket(expr.exp, p) + ')'

    def _print_float(self, expr):
        """
        Handles ``float``s. All constants must be wrapped with a macro so that
        generated code that ends up in a device kernel can easily be cast between 
        float and double as this has huge performance implications on device

        ChastePrinterCommon._print_Mul strips away - signs in the expression and then
        passes along the absolute value to print. When the multiplication is a number,
        this means we get output of the form -CHASTE_CONST(...), hence for consistency,
        we factor any negatives outside of CHASTE_CONST in the below.
        """
        # print integers as int if they are between min & max int in c++
        if expr.is_integer() and C_MIN_INT < expr < C_MAX_INT:
            return cxxcode(int(expr), standard='C++11')
        
        num_str = cxxcode(float(expr), standard='C++11')
        if num_str.startswith('-'):
            return f'-CHASTE_CONST({num_str[1:]})'
        return f'CHASTE_CONST({num_str})'
