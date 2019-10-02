from ._printer import WebLabPrinter, _math_functions
import sympy

from sympy.printing.precedence import precedence


class ChastePrinter(WebLabPrinter):
    """
    Converts Sympy expressions to strings for use in Chaste code generation, based on the WeblabPrinter.

    To use, create a :class:`ChastePrinter` instance, and call its method
    :meth:`doprint()` with a Sympy expression argument.

    Arguments:

    ``symbol_function``
        A function that converts symbols to strings (variable names).
    ``derivative_function``
        A function that converts derivatives to strings.

    """

    def __init__(self, symbol_function=None, derivative_function=None):
        super().__init__(symbol_function, derivative_function)

        # Do not use the math. prefix for functions, as chaste c++ files include an include for this
        self._prefix = ''

        # Make sure we can output a call to GetIntracellularAreaStimulus
        _math_functions.add('GetIntracellularAreaStimulus')

    def _print_And(self, expr):
        """ Handles logical And. """
        my_prec = precedence(expr)
        return ' && '.join([self._bracket(x, my_prec) for x in expr.args])

    def _print_BooleanFalse(self, expr):
        """ Handles False """
        return 'false'

    def _print_BooleanTrue(self, expr):
        """ Handles True """
        return 'true'

    def _print_Or(self, expr):
        """ Handles logical Or. """
        my_prec = precedence(expr)
        return ' || '.join([self._bracket(x, my_prec) for x in expr.args])

    def _print_Pow(self, expr):
        """ Handles Pow(), which includes all division
        only ordinary power is different, the rest is handed back up to the parent class (WebLabPrinter) """
        # Square root or ((only if communicative) 1/sqrt or ordinary devision )
        if expr.exp is sympy.S.Half or (expr.is_commutative and
                                        (-expr.exp is sympy.S.Half or -expr.exp is sympy.S.One)):
            return super()._print_Pow(expr)
        else:
            # Ordinary power
            p = precedence(expr)
            return 'pow(' + self._bracket(expr.base, p) + ', ' + self._bracket(expr.exp, p) + ')'

    def _print_Piecewise(self, expr):
        """
        Handles Piecewise functions.

        Sympy's piecewise is defined as a list of tuples ``(expr, cond)`` and
        evaluated by returning the first ``expr`` whose ``cond`` is true. If
        none of the conditions hold a value error is raised.
        """
        from sympy.logic.boolalg import BooleanTrue

        # Assign NaN if no conditions hold
        # If a condition `True` is found, use its expression instead
        other = 'float(\'nan\')'

        parts = ['(']
        brackets = 1
        for e, c in expr.args:
            # Check if boolean True (if found, stop evaluating further)
            if isinstance(c, BooleanTrue):
                other = self._print(e)
                break
            # Sympy filters these out:
            # elif isinstance(c, BooleanFalse):
            #    continue

            # Add e-if-c-else-? statement
            #parts.append('(')
            #parts.append(self._print(e))
            #parts.append(') if (')
            #parts.append(self._print(c))
            #parts.append(') else (')
            # add c ? e :
            parts.append('(')
            parts.append(self._print(c))
            parts.append(') ? (')
            parts.append(self._print(e))
            parts.append(') : (')            
            brackets += 1
        parts.append(other)
        parts.append(')' * brackets)
        return ''.join(parts)
