from sympy import Derivative, Eq, Function

from chaste_codegen._rdf import OXMETA
from chaste_codegen.cvode_chaste_model import CvodeChasteModel


class CvodeWithDataClampModel(CvodeChasteModel):
    """ Holds template and information specific for the CVODE with data clamp model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._vars_for_template['base_class'] = 'AbstractCvodeCellWithDataClamp'

    def _add_data_clamp_to_model(self):
        """ Add add membrane_data_clamp_current_conductance and membrane_data_clamp_current to the model"""
        self._membrane_data_clamp_current_conductance = \
            self._model.add_variable(name='membrane_data_clamp_current_conductance',
                                     units=self._model.conversion_units.get_unit('dimensionless'))
        self.dataclamp_eq = Eq(self._membrane_data_clamp_current_conductance, 0.0)
        self._model.add_equation(self.dataclamp_eq)

        # add membrane_data_clamp_current
        self._membrane_data_clamp_current = \
            self._model.add_variable(name='membrane_data_clamp_current',
                                     units=self._model.conversion_units.get_unit('uA_per_cm2'))
        # add clamp current equation
        self._in_interface.add(self._membrane_data_clamp_current)
        clamp_current = self._membrane_data_clamp_current_conductance * \
            (self._model.membrane_voltage_var - Function('GetExperimentalVoltageAtTimeT')(self._model.time_variable))
        self._membrane_data_clamp_current_eq = Eq(self._membrane_data_clamp_current, clamp_current)
        self._model.add_equation(self._membrane_data_clamp_current_eq)

        # Add data clamp current as modifiable parameter and re-sort
        self._model.modifiable_parameters.add(self._membrane_data_clamp_current_conductance)

    def _get_derivative_equations(self):
        """ Get equations defining the derivatives including V and add in membrane_data_clamp_current"""
        def find_ionic_var(eq, ionic_var, derivative_equations):
            """Finds ionic_var on the rhs of eq, recursing through defining equations if necessary"""
            if ionic_var in eq.rhs.free_symbols:
                return derivative_equations.index(eq)
            else:
                found_eq = None
                for var in eq.rhs.free_symbols:
                    def_eqs = filter(lambda e: e.lhs == var, derivative_equations)
                    def_eq = next(def_eqs, None)
                    if def_eq is not None and next(def_eqs, None) is None:  # exactly 1
                        found_eq = find_ionic_var(def_eq, ionic_var, derivative_equations)
                        if found_eq is not None:
                            break
                return found_eq

        # make a ciopy of the list of derivative eq, so that the underlying model can be reused
        derivative_equations = list([eq for eq in self._model.derivative_equations])

        self._add_data_clamp_to_model()

        # piggy-backs on the analysis that finds ionic currents, in order to add in data clamp currents
        # Find dv/dt

        deriv_eq_only = filter(lambda eq: isinstance(eq.lhs, Derivative) and
                               eq.lhs.args[0] == self._model.membrane_voltage_var, derivative_equations)
        dvdt = next(deriv_eq_only, None)
        assert dvdt is not None and next(deriv_eq_only, None) is None, 'Expecting exactly 1 dv/dt equation'

        current_index = None
        # We need to add data_clamp to the equation with the correct sign
        # This is achieved by substitution the first of the ionic currents
        # by (ionic_current + data_clamp_current)
        ionic_var = self._model.equations_for_ionic_vars[0].lhs
        current_index = find_ionic_var(dvdt, ionic_var, derivative_equations)
        if current_index is not None:
            eq = derivative_equations[current_index]
            rhs = eq.rhs.xreplace({ionic_var: (ionic_var + self._membrane_data_clamp_current)})
            derivative_equations[current_index] = Eq(eq.lhs, rhs)
            derivative_equations.insert(current_index, self._membrane_data_clamp_current_eq)

        return derivative_equations

    def _get_derived_quant(self):
        """ Get all derived quantities, adds membrane_data_clamp_current and its defining equation"""
        derived_quant = super()._get_derived_quant()

        # Add membrane_data_clamp_current to modifiable parameters
        # (this was set in _get_modifiable_parameters as it's also needed in _get_derivative_equations)
        derived_quant.append(self._membrane_data_clamp_current)
        derived_quant.sort(key=lambda q: self._model.get_display_name(q, OXMETA))
        return derived_quant

    def _format_derivative_equations(self, derivative_equations):
        """Format derivative equations for chaste output and add is_data_clamp_current flag"""
        formatted_eqs = super()._format_derivative_equations(derivative_equations)
        for eq in formatted_eqs:
            eq['is_data_clamp_current'] = eq['sympy_lhs'] == self._membrane_data_clamp_current
        return formatted_eqs

    def _format_derived_quant_eqs(self):
        """ Format equations for derived quantities and add is_data_clamp_current flag"""
        formatted_eqs = super()._format_derived_quant_eqs()
        for eq in formatted_eqs:
            eq['is_data_clamp_current'] = eq['sympy_lhs'] == self._membrane_data_clamp_current
        return formatted_eqs

    def __exit__(self, type, value, traceback):
        """ Clean-up, removed the data clamp we added to the model,so that the model object can be re-used"""
        # Remove modifiable parameter
        self._model.modifiable_parameters.remove(self._membrane_data_clamp_current_conductance)

        # Remove equation from model
        self._model.remove_equation(self.dataclamp_eq)
        self._model.remove_equation(self._membrane_data_clamp_current_eq)

        # Remove variable from model
        self._model.remove_variable(self._membrane_data_clamp_current_conductance)
