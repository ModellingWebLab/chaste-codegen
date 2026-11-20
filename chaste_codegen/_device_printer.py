from sympy.printing.precedence import precedence

from chaste_codegen._chaste_printer import ChastePrinter


# Calls in the CPU code that become arguments of the generated device functions
DEVICE_INPUTS = {
    'GetIntracellularAreaStimulus': 'stimulus',
    'HeartConfig::Instance()->GetCapacitance': 'capacitance',
}


def _is_int_literal(printed):
    """ Returns True if ``printed`` is the C++ text of an integer literal. """
    return printed.lstrip('-').isdigit()


class ChasteDevicePrinter(ChastePrinter):
    """
    Converts Sympy expressions to strings for use in code that can be compiled for both CPU and GPU.

    Expressions are printed for function templates on ``ValueType`` (``float`` or ``double``), taking care that
    float code never silently turns into double code. Chaste calls that are not available on a GPU are printed as
    arguments of the generated function instead, see ``DEVICE_INPUTS``.

    Arguments are the same as for :class:`ChastePrinter`.
    """
    # nvcc has device versions of the std:: maths functions (hipcc is documented to as well), so one call works on
    # both CPU and GPU and picks its float or double overload from ValueType.
    # Signum is replaced in _print_Function; factorial (not in C++) and the data clamp (host only) are unsupported.
    _function_names = {name: 'std::' + func for name, func in ChastePrinter._function_names.items()
                       if name not in DEVICE_INPUTS and name not in ('sign', 'factorial',
                                                                     'GetExperimentalVoltageAtTimeT')}

    _literal_names = {
        'e': 'ValueType(M_E)',
        'nan': 'NAN',
        'pi': 'ValueType(M_PI)',
    }

    def _print_float(self, expr):
        """ Handles ``float``s. Non-integer values are cast to ``ValueType``, as double literals promote float code. """
        printed = super()._print_float(expr)
        return printed if _is_int_literal(printed) else 'ValueType(' + printed + ')'

    def _print_Function(self, expr):
        """ Handles function calls, replacing Chaste calls by arguments of the device function. """
        name = expr.func.__name__
        if name in DEVICE_INPUTS:
            return DEVICE_INPUTS[name]
        if name == 'sign':
            # Chaste's Signum is host only
            arg = self._print(expr.args[0])
            return '((' + arg + ') > 0 ? ValueType(1) : ((' + arg + ') < 0 ? ValueType(-1) : ValueType(0)))'
        func = self._function_names.get(name, None)
        if func is None:
            raise ValueError('Unsupported function: ' + str(name))
        # Integer arguments select the double overload, which silently turns float code into double code
        args = [self._print(arg) for arg in expr.args]
        args = ['ValueType(' + arg + ')' if _is_int_literal(arg) else arg for arg in args]
        return func + '(' + ', '.join(args) + ')'

    def _print_ordinary_pow(self, expr):
        """ Handles ``Pow()`` without division. Integer bases and exponents are cast, as ``std::pow`` and
        ``std::sqrt`` return ``double`` if any argument is an integer. """
        p = precedence(expr)
        base = self._bracket(expr.base, p)
        if _is_int_literal(base):
            base = 'ValueType(' + base + ')'
        if expr.exp == 0.5:
            return 'std::sqrt(' + base + ')'
        exponent = self._bracket(expr.exp, p)
        if _is_int_literal(exponent):
            exponent = 'ValueType(' + exponent + ')'
        return 'std::pow(' + base + ', ' + exponent + ')'

    def _print_Rational(self, expr):
        """ Handles rationals, which would otherwise be printed as integer division. """
        return 'ValueType(' + str(expr.p) + ') / ValueType(' + str(expr.q) + ')'
