import chaste_codegen as cg
import sympy as sp
import time
from chaste_codegen._partial_eval import partial_eval


class CvodeChasteModel(cg.ChasteModel):
    """ Holds template and information specific for the CVODE model type"""
    # TODO: jacobians sympy, followed by cse

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._use_analytic_jacobian = kwargs.get('use_analytic_jacobian', False)  # store if jacobians are needed
        self._jacobian_equations, self._jacobian_matrix = self._get_jacobian()

    def _get_jacobian(self):
        jacobian_equations, jacobian_matrix = [], []
        if self._use_analytic_jacobian:
            state_var_matrix = sp.Matrix(self._state_vars)
            derivative_eqs = partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
            derivative_eq_matrix = sp.Matrix([eq.rhs for eq in derivative_eqs])
            jacobian_matrix = derivative_eq_matrix.jacobian(state_var_matrix)
        return jacobian_equations, jacobian_matrix

    def generate_chaste_code(self):
        """ Generates and stores chaste code for the CVODE model"""

        # Generate hpp for model
        template = cg.load_template('cvode_model.hpp')
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
            'jacobian_equations': []})

        # Generate cpp for model
        template = cg.load_template('cvode_model.cpp')
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
            'jacobian_equations': []})
