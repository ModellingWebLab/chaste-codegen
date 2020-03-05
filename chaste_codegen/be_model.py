import chaste_codegen as cg
import time
import sympy as sp


class BeModel(cg.CvodeChasteModel):
    """ Holds template and information specific for the Backwards Euler model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, use_analytic_jacobian=True, **kwargs)

    def _get_non_linear_state_vars(self):
        # get non-linear state var. A var is linear if it's equation doesn't contain variables other than V and itself
        non_linear_state_vars = [eq.lhs.args[0] for eq in self._derivative_equations
                                 if isinstance(eq.lhs, sp.Derivative) and
                                 eq.lhs.args[0] != self._membrane_voltage_var and
                                 len(eq.rhs.free_symbols - set([eq.lhs.args[0], self._membrane_voltage_var])) != 0]
        return non_linear_state_vars

    def _format_nonlinear_state_vars(self):
        formatted_non_linear = \
            [s for s in self._formatted_state_vars if s['sympy_var'] in self._get_non_linear_state_vars()]
        # order by dispay name
        formatted_non_linear = sorted(formatted_non_linear, key=lambda d: self._get_var_display_name(d['sympy_var']))

        formatted_state_vars = self._formatted_state_vars
        residual_equations = []
        for i in range(len(formatted_state_vars)):
            formatted_state_vars[i]['linear'] = formatted_state_vars[i] not in formatted_non_linear
            if not formatted_state_vars[i]['linear']:
                residual_equations.append({'residual_index': formatted_non_linear.index(formatted_state_vars[i]),
                                           'state_var_index': i, 'var': self._formatted_y_derivatives[i]})

        return formatted_state_vars, formatted_non_linear, residual_equations

    def _get_jacobian(self):
        self.__formatted_state_vars, self._formatted_nonlinear_state_vars, self._residual_equations = \
            self._format_nonlinear_state_vars()
        non_linear_state_vars = [v['sympy_var'] for v in self._formatted_nonlinear_state_vars]
        state_var_matrix = sp.Matrix(non_linear_state_vars)
        # get derivatives for non-linear state vars
        derivative_eqs = [d for d in self._derivative_equations if d.lhs.args[0] in non_linear_state_vars]
        # sort by state var
        derivative_eqs = sorted(derivative_eqs, key=lambda d: non_linear_state_vars.index(d.lhs.args[0]))
        # we're only interested in the rhs
        derivative_eqs = [eq.rhs for eq in derivative_eqs]
        derivative_eq_matrix = sp.Matrix(derivative_eqs)
        jacobian_matrix = derivative_eq_matrix.jacobian(state_var_matrix)
        jacobian_equations, jacobian_matrix = sp.cse(jacobian_matrix, order='none')
        return jacobian_equations, sp.Matrix(jacobian_matrix)

    def _format_jacobian(self):
        assert isinstance(self._jacobian_matrix, sp.Matrix), 'Expecting a jacobian as a matrix'
        equations = [{'lhs': self._printer.doprint(eq[0]), 'rhs': self._printer.doprint(eq[1])}
                     for eq in self._jacobian_equations]
        rows, cols = self._jacobian_matrix.shape
        jacobian = []
        for i in range(rows):
            for j in range(cols):
                matrix_entry = self._jacobian_matrix[i, j]
                jacobian.append({'i': i, 'j': j, 'entry': self._printer.doprint(matrix_entry)})
        return equations, jacobian

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
            'nonlinear_state_vars': self._formatted_nonlinear_state_vars,
            'residual_equations': self._residual_equations})
