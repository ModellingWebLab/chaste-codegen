import chaste_codegen as cg
import sympy as sp
import time
from chaste_codegen._partial_eval import partial_eval


class CvodeChasteModel(cg.ChasteModel):
    """ Holds template and information specific for the CVODE model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._use_analytic_jacobian = kwargs.get('use_analytic_jacobian', False)  # store if jacobians are needed
        self._jacobian_equations, self._jacobian_matrix = self._get_jacobian()
        self._formatted_state_vars = self._update_state_vars()
        self._formatted_jacobian_equations, self._formatted_jacobian_matrix_entries = self._format_jacobian()

    def _print_modifiable_parameters(self, symbol):
        return 'NV_Ith_S(mParameters, ' + str(self._modifiable_parameters.index(symbol)) + ')'

    def _get_jacobian(self):
        jacobian_equations, jacobian_matrix = [], []
        if self._use_analytic_jacobian:
            state_var_matrix = sp.Matrix(self._state_vars)
            # get deriv eqs and substitute in all variables other than state vars
            derivative_eqs = partial_eval(self._derivative_equations, self._y_derivatives, keep_multiple_usages=False)
            # sort by state var so both are in the same order
            derivative_eqs = sorted(derivative_eqs, key=lambda d: self._state_vars.index(d.lhs.args[0]))
            # we're only interested in the rhs
            derivative_eqs = [eq.rhs for eq in derivative_eqs]
            derivative_eq_matrix = sp.Matrix(derivative_eqs)
            jacobian_matrix = derivative_eq_matrix.jacobian(state_var_matrix)
            jacobian_equations, jacobian_matrix = sp.cse(jacobian_matrix, order='none')
        return jacobian_equations, sp.Matrix(jacobian_matrix)

    def _update_state_vars(self):
        jacobian_symbols = set()
        for eq in self._jacobian_equations:
            jacobian_symbols.update(eq[1].free_symbols)
        for en in self._jacobian_matrix:
            jacobian_symbols.update(en.free_symbols)
        formatted_state_vars = self._formatted_state_vars
        for i in range(len(formatted_state_vars)):
            formatted_state_vars[i]['in_jacobian'] = formatted_state_vars[i]['sympy_var'] in jacobian_symbols
        return formatted_state_vars

    def _format_jacobian(self):
        assert isinstance(self._jacobian_matrix, sp.Matrix), 'Expecting a jacobian as a matrix'
        equations = [{'lhs': self._printer.doprint(eq[0]), 'rhs': self._printer.doprint(eq[1])}
                     for eq in self._jacobian_equations]
        rows, cols = self._jacobian_matrix.shape
        jacobian = []
        for j in range(cols):
            for i in range(rows):
                matrix_entry = self._jacobian_matrix[i, j]
                if matrix_entry != 0:
                    jacobian.append({'i': i, 'j': j, 'entry': self._printer.doprint(matrix_entry)})
        return equations, jacobian

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
            'jacobian_equations': self._formatted_jacobian_equations})

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
            'jacobian_equations': self._formatted_jacobian_equations,
            'jacobian_entries': self._formatted_jacobian_matrix_entries})
