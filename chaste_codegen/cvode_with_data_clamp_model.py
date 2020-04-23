import sympy as sp

from chaste_codegen.cvode_chaste_model import CvodeChasteModel


class CvodeWithDataClampeModel(CvodeChasteModel):
    """ Holds template and information specific for the CVODE with data clamp model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'cvode_with_data_clamp_model.hpp'
        self._cpp_template = 'cvode_with_data_clamp_model.cpp'

    def _get_modifiable_parameters(self):
        """ Get all modifiable parameters and adds membrane_data_clamp_current_conductance"""
        modifiable_parameters = super()._get_modifiable_parameters()

        # add membrane_data_clamp_current_conductance
        self._membrane_data_clamp_current_conductance = \
            self._model.add_variable(name='membrane_data_clamp_current_conductance',
                                     units=self._units.get_unit('dimensionless'))
        self._model.add_equation(sp.Eq(self._membrane_data_clamp_current_conductance, 0.0))

        # add membrane_data_clamp_current
        self._membrane_data_clamp_current = self._model.add_variable(name='membrane_data_clamp_current',
                                                                     units=self._units.get_unit('uA_per_cm2'))
        # add clamp current equation
        self._in_interface.append(self._membrane_data_clamp_current)
        clamp_current = self._membrane_data_clamp_current_conductance * \
            (self._membrane_voltage_var - sp.Function('GetExperimentalVoltageAtTimeT')(self._time_variable))
        self._membrane_data_clamp_current_eq = sp.Eq(self._membrane_data_clamp_current, clamp_current)
        self._model.add_equation(self._membrane_data_clamp_current_eq)

        modifiable_parameters.append(self._membrane_data_clamp_current_conductance)
        return modifiable_parameters

    def _get_derived_quant(self):
        """ Get all derived quantities, adds membrane_data_clamp_current and its defining equation"""
        derived_quant = super()._get_derived_quant()

        derived_quant.append(self._membrane_data_clamp_current)
        return derived_quant

    def _get_derivative_equations(self):
        """ Get equations defining the derivatives including V and add in membrane_data_clamp_current"""
        derivative_equations = super()._get_derivative_equations()
        # piggy-backs on the analysis that finds ionic currents, in order to add in data_claamp currents
        # Find dv/dt
        voltage_index = None
        if len(self._equations_for_ionic_vars) > 0:
            for i, eq in enumerate(derivative_equations):
                if isinstance(eq.lhs, sp.Derivative) and eq.lhs.args[0] == self._membrane_voltage_var:
                    # We need to add data_clamp to the equation with the correct sign
                    # This is achieved by substitution the first of the ionic currents
                    # by (ionic_current + data_clamp_current)
                    voltage_index = i
                    rhs = eq.rhs.xreplace({self._equations_for_ionic_vars[0].lhs:
                                           self._equations_for_ionic_vars[0].lhs + self._membrane_data_clamp_current})
                    derivative_equations[voltage_index] = sp.Eq(eq.lhs, rhs)
            # add the equation for data_clamp_current to derivative_equations just before dv/dt
            if voltage_index is not None:
                derivative_equations.insert(voltage_index, self._membrane_data_clamp_current_eq)

        return derivative_equations

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
