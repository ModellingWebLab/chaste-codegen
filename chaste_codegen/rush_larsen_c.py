from cellmlmanip.model import Variable
from cellmlmanip.units import UnitStore
from sympy import (
    Derivative,
    Eq,
    Float,
    Piecewise,
)

import chaste_codegen as cg
from chaste_codegen._math_functions import exp_
from chaste_codegen.model_with_conversions import (
    _get_membrane_stimulus_current,
    _get_membrane_voltage_var,
    add_conversions,
)
from chaste_codegen.rush_larsen_model import RushLarsenModel


def component_name(var):
    """Get the name of the component variable var is in"""
    name = str(var)
    return name[:name.find('$')]


def get_variable_name(s, interface=False):
    """Get the correct variable name based on the variable and whether it should be in the chaste_interface."""
    s_name = s.expr if isinstance(s, Derivative) else s
    s_name = str(s_name)
    s_name = s_name[s_name.find('$') + 1:]

    if isinstance(s, Derivative):
        return 'd_dt_' + s_name
    else:
        return s_name


class RushLarsenC(RushLarsenModel):
    """ Holds template and information specific for the RushLarsen model type"""

    DEFAULT_EXTENSIONS = ('.h', '.c')

    def __init__(self, model, file_name, **kwargs):
        self._i_inj_params = set()
        # add i_inj
        V = _get_membrane_voltage_var(model, convert=False)
        i_stim = _get_membrane_stimulus_current(model)
        if i_stim:
            # add units
            units = UnitStore(model.units)
            picoF = units.add_unit('picoF', 'farad / 1e12')
            one_over_mv = units.add_unit('one_over_millivolt', '1 / (volt * 1e-3)')
            one_over_ohm = units.add_unit('one_over_ohm', '1 / ohm')
            millivolt = units.add_unit('millivolt', 'volt / 1e3')

            # add variables
            Scaling = model.add_variable('Scaling', units='dimensionless')
            Cext = model.add_variable('Cext', units=picoF)
            Ampl_gain = model.add_variable('Ampl_gain', units='dimensionless')
            R_seal = model.add_variable('R_seal', units='ohm')
            g_leak = model.add_variable('g_leak', units=one_over_ohm)
            leak_comp_perc = model.add_variable('leak_comp_perc', units='dimensionless')
            E_l = model.add_variable('E_l', units=millivolt)
            A0_bck = model.add_variable('A0_bck', units='dimensionless')
            k_bck = model.add_variable('k_bck', units=one_over_mv)
            Scale_bck = model.add_variable('Scale_bck', units='dimensionless')
            i_leak_comp = model.add_variable('i_leak_comp', units='dimensionless')
            i_bck = model.add_variable('i_bck', units='dimensionless')
            I_ext = model.add_variable('I_ext', units='dimensionless')
            I_curr = model.add_variable('I', units='dimensionless')
            i_inj = model.add_variable('i_inj', units='dimensionless')

            self._i_inj_params = {A0_bck, Ampl_gain, Cext, E_l, I_curr, R_seal, Scale_bck, Scaling, k_bck,
                                  leak_comp_perc}
            # add defining numbers
            model.add_equation(Eq(Scaling, Float(1.0)))
            model.add_equation(Eq(A0_bck, Float(1.0278)))
            model.add_equation(Eq(k_bck, Float(0.0986)))
            model.add_equation(Eq(R_seal, Float(1.0)))
            model.add_equation(Eq(Cext, Float(1.0)))
            model.add_equation(Eq(leak_comp_perc, Float(1.0)))
            model.add_equation(Eq(E_l, Float(1.0)))
            model.add_equation(Eq(I_curr, Float(1.0)))
            model.add_equation(Eq(Ampl_gain, Float(1.0)))
            model.add_equation(Eq(Scale_bck, Float(1.0)))

            # add eqs
            model.add_equation(Eq(g_leak, 1 / R_seal))
            model.add_equation(Eq(i_leak_comp, (g_leak / Cext) * (V - E_l) * (leak_comp_perc / 100)))
            model.add_equation(Eq(i_bck, (Scale_bck / Cext) * A0_bck / (1 + exp_(-k_bck * V))))
            model.add_equation(Eq(I_ext, I_curr / (Cext * Ampl_gain)))
            model.add_equation(Eq(i_inj, Scaling * (I_ext - i_leak_comp - i_bck)))

            dvdt = next((eq for eq in model.equations if eq.lhs == Derivative(V, model.get_free_variable())), None)
            assert dvdt is not None, "Expecting exatctly 1 dvdt equation"
            model.remove_equation(dvdt)
            model.add_equation(Eq(dvdt.lhs, dvdt.rhs.replace(i_stim, i_stim + i_inj)))
            # find dv/dt

        # add conversions
        add_conversions(model, use_modifiers=False, skip_chaste_stimulus_conversion=True)
        model.modifiable_parameters |= set(self._i_inj_params)

        # For equations containing a piecewise not at the top level, pull it out into it's own equation
        for eq in tuple(model.equations):
            # Piecewises cannot be inline, so attach each to a new variable
            if eq.has(Piecewise):
                if eq.rhs.has(Piecewise) and (not isinstance(eq.rhs, Piecewise) or len(eq.rhs.atoms(Piecewise)) > 1):
                    new_rhs = eq.rhs
                    # sort the piecewsies to guarantee consistent output across re-runs
                    for i, pw in enumerate(sorted(eq.rhs.atoms(Piecewise), key=str)):
                        new_pw_lhs = model.add_variable(eq.lhs.name + '_PW_' + str(i), eq.lhs.units)
                        model.add_equation(Eq(new_pw_lhs, pw))
                        new_rhs = new_rhs.replace(pw, new_pw_lhs)
                    model.remove_equation(eq)
                    model.add_equation(Eq(eq.lhs, new_rhs))

        super().__init__(model, file_name, **kwargs)
        self._templates = ['labview.h', 'labview.c']
        self._vars_for_template['model_type'] = 'RushLarsenC'

        # store info for .c/.h
        self._vars_for_template['stat_var_name_max_length'] = \
            max([len(sv['var']) for sv in self._formatted_state_vars])
        self._vars_for_template['unit_name_max_length'] = \
            max([len(sv['units']) for sv in self._formatted_state_vars])
        self._vars_for_template['components'] = \
            tuple([component_name(sv['sympy_var']) for sv in self._formatted_state_vars])
        self._vars_for_template['component_name_max_length'] = \
            max([len(sv) for sv in self._vars_for_template['components']])

    def _add_printers(self, lookup_table_function=lambda e: None):
        """ Initialises Printers for outputting chaste code. """
        # Printer for printing chaste regular variable assignments (var_ prefix)
        # Print variables in interface as var_chaste_interface
        # (state variables, time, lhs of default_stimulus eqs, i_ionic and lhs of y_derivatives)
        # Print modifiable parameters as mParameters[index]
        self._printer = \
            cg.ChastePrinter(lambda variable:
                             get_variable_name(variable, variable in self._in_interface)
                             if variable not in self._model.modifiable_parameters
                             else self._print_modifiable_parameters(variable),
                             lambda deriv: get_variable_name(deriv),
                             lookup_table_function)

        # Printer for printing variable in comments e.g. for ode system information
        self._name_printer = cg.ChastePrinter(lambda variable: get_variable_name(variable))

    def _print_sv_ind(self, v):
        var_name = "Y[%s]" % self._state_vars.index(list(v.free_symbols)[0])
        if isinstance(v, Derivative):
            var_name = "d" + var_name
        return Variable(var_name, units='dimensionless')

    def _format_derivative_alpha_beta(self, deriv):
        return {'type': 'non_linear', 'deriv': self._print_sv_ind(deriv)}

    def _print_rhs_with_modifiers(self, modifier, eq, modifiers_with_defining_eqs=set()):
        """ Print modifiable parameters in the correct format for the model type"""
        # replace state vars by Y vector derived by dY vector, tome by last Y
        subs_dict = {v: self._print_sv_ind(v)
                     for v in self._model.find_variables_and_derivatives([eq])
                     if list(v.free_symbols)[0] in self._state_vars}
        subs_dict |= {self._model.get_free_variable(): Variable("Y[%s]" % len(self._state_vars), units='dimensionless')}
        return self._printer.doprint(eq.xreplace(subs_dict))

    def _print_modifiable_parameters(self, variable):
        """ Print modifiable parameters in the correct format for the model type"""
        # labview export does not use modifiable parameters, instead these are sorted on top of the ocntstants block
        return get_variable_name(variable)

    def _format_modifiable_parameters(self):
        """ Format the modifiable parameter for printing to chaste code"""
        # sort i_inj consts on top of the parameters so they end up on top of the consts block
        self._modifiable_parameters = sorted(self._modifiable_parameters, key=lambda p: p not in self._i_inj_params)

        # Add component information
        formatted_params = super()._format_modifiable_parameters()
        for fp, p in zip(formatted_params, self._modifiable_parameters):
            fp['component'] = component_name(p)
        return formatted_params

    def format_derivative_equation(self, eq, modifiers_with_defining_eqs):
        """ Format an individual derivative equation
            specified so that other model types can specify more detailed printing """
        # Add component name, whether this is a constant, a state var or a piecewise
        formatted_eq = super().format_derivative_equation(eq, modifiers_with_defining_eqs)
        formatted_eq['is_constant'] = isinstance(eq.rhs, Float)
        formatted_eq['component'] = component_name(eq.lhs)
        formatted_eq['lhs_is_sv'] = \
            isinstance(formatted_eq['sympy_lhs'], Derivative) or formatted_eq['sympy_lhs'] in self._model.state_vars
        if formatted_eq['lhs_is_sv']:
            formatted_eq['lhs'] = self._print_sv_ind(formatted_eq['sympy_lhs'])

        formatted_eq['is_piecewise'] = isinstance(eq.rhs, Piecewise)
        if formatted_eq['is_piecewise']:
            formatted_eq['pw_expr_conds'] = [(self._print_rhs_with_modifiers(eq.lhs, a[0]),
                                              self._print_rhs_with_modifiers(eq.lhs, a[1])) for a in eq.rhs.args]
        return formatted_eq
