import chaste_codegen as cg
import time


class BeModel(cg.CvodeChasteModel):
    """ Holds template and information specific for the CVODE model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, use_analytic_jacobian=True, **kwargs)
        self._formatted_nonlinear_state_vars = self._format_nonlinear_state_vars()

    def _get_non_linear_state_vars(self):
        # get non-linear state var. A var is linear if it's equation doesn't contain variables other than V and itself
        non_linear_state_vars = [eq.lhs.args[0] for eq in self._derivative_equations
                                 if not eq.lhs.args[0] == self._membrane_voltage_var and
                                 len(eq.rhs.free_symbols - set([eq.lhs.args[0], self._membrane_voltage_var])) != 0]
        return non_linear_state_vars

    def _format_nonlinear_state_vars(self):
        formatted_vars = [s for s in self._formatted_state_vars if s['sympy_var'] in self._get_non_linear_state_vars()]
        # order by dispay name
        formatted_vars = sorted(formatted_vars, key=lambda d: self._get_var_display_name(d['sympy_var']))
        return formatted_vars

    def generate_chaste_code(self):
        """ Generates and stores chaste code for the BE model"""
        # Generate hpp for model
        template = cg.load_template('be_model.hpp')
        self.generated_hpp = template.render({
            'converter_version': cg.__version__,
            'model_name': self._model.name,
            'class_name': self.class_name,
            'dynamically_loadable': self._dynamically_loadable,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'default_stimulus_equations': self._formatted_default_stimulus,
            'use_get_intracellular_calcium_concentration':
                self._cytosolic_calcium_concentration_var in self._state_vars,
            'free_variable': self._free_variable,
            'use_verify_state_variables': self._use_verify_state_variables,
            'derived_quantities': self._formatted_derived_quant,
            'nonlinear_state_vars': self._formatted_nonlinear_state_vars})

        # Generate cpp for model
        template = cg.load_template('be_model.cpp')
        self.generated_cpp = template.render({
            'converter_version': cg.__version__,
            'model_name': self._model.name,
            'file_name': self.file_name,
            'class_name': self.class_name,
            'header_ext': self._header_ext,
            'dynamically_loadable': self._dynamically_loadable,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'default_stimulus_equations': self._formatted_default_stimulus,
            'use_get_intracellular_calcium_concentration':
                self._cytosolic_calcium_concentration_var in self._state_vars,
            'membrane_voltage_index': self._MEMBRANE_VOLTAGE_INDEX,
            'cytosolic_calcium_concentration_index':
                self._state_vars.index(self._cytosolic_calcium_concentration_var)
                if self._cytosolic_calcium_concentration_var in self._state_vars
                else self._CYTOSOLIC_CALCIUM_CONCENTRATION_INDEX,
            'state_vars': self._formatted_state_vars,
            'ionic_vars': self._formatted_extended_equations_for_ionic_vars,
            'y_derivative_equations': self._formatted_derivative_eqs,
            'y_derivatives': self._formatted_y_derivatives,
            'use_capacitance_i_ionic': self._current_unit_and_capacitance['use_capacitance'],
            'free_variable': self._free_variable,
            'ode_system_information': self._ode_system_information,
            'modifiable_parameters': self._formatted_modifiable_parameters,
            'named_attributes': self._named_attributes,
            'use_verify_state_variables': self._use_verify_state_variables,
            'derived_quantities': self._formatted_derived_quant,
            'derived_quantity_equations': self._formatted_quant_eqs,
            'jacobian_equations': self._formatted_jacobian_equations,
            'jacobian_entries': self._formatted_jacobian_matrix_entries,
            'nonlinear_state_vars': self._formatted_nonlinear_state_vars})
