import chaste_codegen as cg
from cellmlmanip.model import VariableDummy
import sympy as sp


class OptChasteModel(cg.NormalChasteModel):
    """ Holds information specific for the Optimised model type. Builds on Normal model type"""
    def _partial_eval(self, equations, required_lhs):
        evaluated_eqs = []
        # count usage of variables on rhs of equations
        usage_count = dict()
        for eq in equations:
            usage_count.setdefault(eq.lhs, 0)
            for var in eq.rhs.atoms(VariableDummy):
                usage_count.setdefault(var, 0)
                usage_count[var] += 1
        # subs in all constants and expressions only used once
        subs_dict = {}
        for eq in equations:
            new_eq = eq.xreplace(subs_dict)
            if new_eq.lhs not in required_lhs and \
                    (isinstance(new_eq.rhs, sp.numbers.Float) or usage_count[new_eq.lhs] <= 1):
                subs_dict[new_eq.lhs] = new_eq.rhs
            else:
                evaluated_eqs.append(new_eq)
        return evaluated_eqs

    def _get_stimulus(self):
        """ Get the partially evaluated stimulus currents in the model"""
        stim_param, return_stim_eqs = super()._get_stimulus()
        return stim_param, self._partial_eval(return_stim_eqs, stim_param)

    def _get_extended_equations_for_ionic_vars(self):
        """ Get the partially evaluated equations defining the ionic derivatives and all dependant equations"""
        return self._partial_eval(super()._get_extended_equations_for_ionic_vars(),
                                  [eq.lhs for eq in self._equations_for_ionic_vars])

    def _get_derivative_equations(self):
        """ Get partially evaluated equations defining the derivatives including V (self._membrane_voltage_var)"""
        return self._partial_eval(super()._get_derivative_equations(),
                                  self._y_derivatives)
