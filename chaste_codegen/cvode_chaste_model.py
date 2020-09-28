from functools import partial

from sympy import (
    Derivative,
    Eq,
    Function,
    Matrix,
)

from chaste_codegen._jacobian import format_jacobian, get_jacobian
from chaste_codegen._partial_eval import partial_eval
from chaste_codegen._rdf import OXMETA
from chaste_codegen.chaste_model import ChasteModel


class CvodeChasteModel(ChasteModel):
    """ Holds template and information specific for the CVODE model type"""
    def __init__(self, model, file_name, **kwargs):
        self._use_data_clamp = kwargs.get('cvode_data_clamp', False)  # store if data clamp is needed
        self._use_analytic_jacobian = kwargs.get('use_analytic_jacobian', False)  # store if jacobians are needed

        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'cvode_model.hpp'
        self._cpp_template = 'cvode_model.cpp'

        if self._use_data_clamp:
            self._vars_for_template['base_class'] = 'AbstractCvodeCellWithDataClamp'
        else:
            self._vars_for_template['base_class'] = 'AbstractCvodeCell'

        if self._use_data_clamp:
            self._vars_for_template['model_type'] = 'CvodeCellWithDataClamp'
        elif self._use_analytic_jacobian:
            self._vars_for_template['model_type'] = 'AnalyticCvode'
        else:
            self._vars_for_template['model_type'] = 'NumericCvode'

        self._vars_for_template['vector_decl'] = "N_Vector"  # indicate how to declare state vars and values

        if self._use_analytic_jacobian:
            # get deriv eqs and substitute in all variables other than state vars
            self._derivative_equations = \
                partial_eval(self._derivative_equations, self._model.y_derivatives, keep_multiple_usages=False)
            self._jacobian_equations, self._jacobian_matrix = get_jacobian(self._state_vars, self._derivative_equations)
            self._formatted_state_vars = self._update_state_vars()

            self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
                self._print_jacobian()
        else:
            self._vars_for_template['jacobian_equations'], self._vars_for_template['jacobian_entries'] = \
                [], Matrix()

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
        derivative_equations = super()._get_derivative_equations()
        if self._use_data_clamp:
            def find_ionic_var(eq, ionic_var, deqs):
                """Finds ionic_var on the rhs of eq, recursing through defining equations if necessary"""
                if ionic_var in eq.rhs.free_symbols:
                    return deqs.index(eq)
                else:
                    found_eq = None
                    for var in eq.rhs.free_symbols:
                        def_eqs = filter(lambda e: e.lhs == var, deqs)
                        def_eq = next(def_eqs, None)
                        if def_eq is not None and next(def_eqs, None) is None:  # exactly 1
                            found_eq = find_ionic_var(def_eq, ionic_var, deqs)
                            if found_eq is not None:
                                break
                    return found_eq

            # make a copy of the list of derivative eq, so that the underlying model can be reused
            derivative_equations = list([eq for eq in derivative_equations])

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
            ionic_var = self._model.ionic_vars[0]
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
        if self._use_data_clamp:
            # Add membrane_data_clamp_current to modifiable parameters
            # (this was set in _get_modifiable_parameters as it's also needed in _get_derivative_equations)
            derived_quant.append(self._membrane_data_clamp_current)
            derived_quant.sort(key=lambda q: self._model.get_display_name(q, OXMETA))
        return derived_quant

    def _format_derivative_equations(self, derivative_equations):
        """Format derivative equations for chaste output and add is_data_clamp_current flag"""
        formatted_eqs = super()._format_derivative_equations(derivative_equations)
        if self._use_data_clamp:
            for eq in formatted_eqs:
                eq['is_data_clamp_current'] = eq['sympy_lhs'] == self._membrane_data_clamp_current
        return formatted_eqs

    def _format_derived_quant_eqs(self):
        """ Format equations for derived quantities and add is_data_clamp_current flag"""
        formatted_eqs = super()._format_derived_quant_eqs()
        if self._use_data_clamp:
            for eq in formatted_eqs:
                eq['is_data_clamp_current'] = eq['sympy_lhs'] == self._membrane_data_clamp_current
        return formatted_eqs

    def _print_jacobian(self):
        modifiers_with_defining_eqs = set((eq[0] for eq in self._jacobian_equations)) | self._model.state_vars
        return format_jacobian(self._jacobian_equations, self._jacobian_matrix, self._printer,
                               partial(self._print_rhs_with_modifiers,
                                       modifiers_with_defining_eqs=modifiers_with_defining_eqs))

    def _print_modifiable_parameters(self, variable):
        return 'NV_Ith_S(mParameters, ' + self._modifiable_parameter_lookup[variable] + ')'

    def _format_rY_entry(self, index):
        return 'NV_Ith_S(rY, ' + str(index) + ')'

    def _update_state_vars(self):
        jacobian_symbols = set()
        for eq in self._jacobian_equations:
            jacobian_symbols.update(eq[1].free_symbols)
        for en in self._jacobian_matrix:
            jacobian_symbols.update(en.free_symbols)
        formatted_state_vars = self._formatted_state_vars
        for sv in formatted_state_vars:
            sv['in_jacobian'] = sv['sympy_var'] in jacobian_symbols
        return formatted_state_vars

    def __exit__(self, type, value, traceback):
        """ Clean-up, removed the data clamp if used, so that the model object can be re-used"""
        if self._use_data_clamp:
            # Remove modifiable parameter
            self._model.modifiable_parameters.remove(self._membrane_data_clamp_current_conductance)

            # Remove equation from model
            self._model.remove_equation(self.dataclamp_eq)
            self._model.remove_equation(self._membrane_data_clamp_current_eq)

            # Remove variable from model
            self._model.remove_variable(self._membrane_data_clamp_current_conductance)
            self._model.remove_variable(self._membrane_data_clamp_current)
