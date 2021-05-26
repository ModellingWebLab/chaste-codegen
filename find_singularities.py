# script to generate singularities images.
# requires chaste_codegen, it's cellml files (in cellml\cellml\), matplotlib

import multiprocessing as mp
import os

import matplotlib.pyplot as plt
from sympy import And, Float, Ge, Le, Piecewise, Wild

from chaste_codegen import DATA_DIR, ChastePrinter, load_model_with_conversions
from chaste_codegen._math_functions import exp_, subs_math_func_placeholders
from chaste_codegen.model_with_conversions import (_get_modifiable_parameters,
                                                   get_equations_for)

printer = ChastePrinter(lambda var: str(var).lstrip('_').replace('$', '__'),
                        lambda deriv: str(deriv).lstrip('_').replace('$', '__'))

exp_function = exp_


def get_initial_value(var, model):
    """Returns the initial value of a variable if it has one, 0 otherwise"""
    # state vars have an initial value parameter defined
    initial_value = 0
    if var in model.state_vars:
        initial_value = getattr(var, 'initial_value', 0)
    else:
        eqs = get_equations_for(model, (var,), filter_modifiable_parameters_lhs=False, optimise=False)
        # If there is a defining equation, there should be just 1 equation and it should be of the form var = value
        if len(eqs) == 1 and isinstance(eqs[0].rhs, Float):
            initial_value = eqs[0].rhs
    return initial_value


def draw_graphs(eq_no, file_name, new_ex, original_eq, new_V, original_V, vardefs, vardefs_offset, vardefs_fixed,
                vardefs_offset_fixed):
    graph_text = ''
    draw_points = 2000
    Vmin_wildcard, Vmax_wildcard = Wild('Vmin_wildcard', real=True), Wild('Vmax_wildcard', real=True)
    file_name = file_name.replace('.cellml', '')

    # subsitute in parameters in both euqations so we can draw them
    prev_ex = None
    while prev_ex != new_ex:
        prev_ex = new_ex
        newrex = new_ex.xreplace(vardefs_fixed)
        if newrex == 0:
            newrex = new_ex.xreplace(vardefs_offset_fixed)
        new_ex = newrex

    prev_ex = None
    while prev_ex != original_eq:
        prev_ex = original_eq
        newrex = original_eq.xreplace(vardefs)
        if newrex == 0:
            newrex = original_eq.xreplace(vardefs_offset)
        original_eq = newrex

    # subsitute in math functions (exp etc) for drawing
    new_ex = subs_math_func_placeholders(new_ex)
    original_eq = subs_math_func_placeholders(original_eq)

    Piecewises = new_ex.atoms(Piecewise)
    for pw_index, pw in enumerate(Piecewises):
        match = pw.args[0][1].match(And(Ge(new_V, Vmin_wildcard), Le(new_V, Vmax_wildcard)))
        if match and Vmin_wildcard in match and Vmax_wildcard in match:
            Vmin = min(match[Vmin_wildcard], match[Vmax_wildcard])
            Vmax = max(match[Vmin_wildcard], match[Vmax_wildcard])

            min_val, max_val = new_ex.subs({new_V: Vmin}), new_ex.subs({new_V: Vmax})

            min_val, max_val = min(min_val, max_val), max(min_val, max_val)

            fig = plt.figure()
            fig.add_subplot(111)
            x, y, x2, y2 = [], [], [], []

            plt.xlim(float(Vmin - (0.25 * (Vmax - Vmin))), float(Vmax + (0.25 * (Vmax - Vmin))))
            plt.ylim(float(min_val - (0.25 * (max_val - min_val))), float(max_val + (0.25 * (max_val - min_val))))
            plt.axvspan(Vmin, Vmax, color='gold', alpha=0.125)

            current_point = Vmin - (0.25 * (Vmax - Vmin))

            for _ in range(draw_points):
                try:
                    val = original_eq.subs({original_V: current_point})
                    if val.is_real:
                        x.append(current_point)
                        y.append(val)
                        if Vmin <= current_point <= Vmax:
                            x2.append(current_point)
                            y2.append(new_ex.subs({new_V: current_point}))
                except TypeError:
                    pass
                current_point += (1.5 * (Vmax - Vmin)) / draw_points
            plt.plot(x, y, color="silver")
            plt.plot(x2, y2, color="red")

            image_dir = 'diagrams/' + '/' + file_name
            os.makedirs(image_dir, exist_ok=True)
            image_name = image_dir + '/' + str(eq_no) + '_' + str(pw_index) + '.png'
            graph_text += "![Singularity](" + image_name + ")\n"

            plt.savefig(image_name)
            plt.close('all')
    return graph_text


def process_model(file_name):
    model_result_text = ""
    model = load_model_with_conversions(os.path.join(DATA_DIR, '..', '..', '..', 'cellml', 'cellml', file_name),
                                        quiet=True, skip_singularity_fixes=True)
    fixes_model = load_model_with_conversions(os.path.join(DATA_DIR, '..', '..', '..', 'cellml', 'cellml', file_name),
                                              quiet=True, skip_singularity_fixes=False)

    model_result_text += "# Model: " + model.name + '(' + file_name + ')'
    model_result_text += "Number of piecewises: " + str(sum([len(eq.rhs.atoms(Piecewise)) for eq in model.equations]))

    vardefs = {e: get_initial_value(e, model) for e in _get_modifiable_parameters(model) |
               (model.state_vars - set([model.membrane_voltage_var]))}
    vardefs_offset = {e: val + 1e-7 for e, val in vardefs.items()}

    vardefs_fixed = {e: get_initial_value(e, fixes_model)
                     for e in _get_modifiable_parameters(fixes_model) |
                     (fixes_model.state_vars - set([fixes_model.membrane_voltage_var]))}
    vardefs_offset_fixed = {e: val + 1e-7 for e, val in vardefs_fixed.items()}

    eq_no = 0
    num_sing = 0

    fixed_equations = fixes_model.derivative_equations
    for i, eq in enumerate(model.derivative_equations):
        vardefs[eq.lhs] = eq.rhs
        vardefs_offset[eq.lhs] = eq.rhs

        fixed_eq = [e for e in fixed_equations if printer.doprint(eq.lhs) == printer.doprint(e.lhs)]
        if len(fixed_eq) > 0:
            vardefs_fixed[fixed_eq[0].lhs] = fixed_eq[0].rhs
            vardefs_offset_fixed[fixed_eq[0].lhs] = fixed_eq[0].rhs

        if not isinstance(eq.rhs, Piecewise):
            if (len(fixed_eq) > 0 and printer.doprint(fixed_eq[0].rhs) != printer.doprint(eq.rhs)):
                eq_no += 1
                model_result_text += "## Equation " + str(eq_no) + ":\n"
                model_result_text += "```\n"
                model_result_text += printer.doprint(eq.lhs) + " = " + printer.doprint(eq.rhs) + "\n"
                model_result_text += "```\n"
                num_sing += len(fixed_eq[0].rhs.atoms(Piecewise))
                model_result_text += "## New Eq:\n"
                model_result_text += "```\n"
                model_result_text += printer.doprint(eq.lhs) + " = " + printer.doprint(fixed_eq[0].rhs) + "\n"
                model_result_text += "```\n"
                model_result_text += draw_graphs(eq_no, file_name, fixed_eq[0].rhs, eq.rhs,
                                                 fixes_model.membrane_voltage_var, model.membrane_voltage_var, vardefs,
                                                 vardefs_offset, vardefs_fixed, vardefs_offset_fixed)
                model_result_text += "\n\n"
    model_result_text += "Number of singularities: " + str(num_sing)
    model_result_text += "\n\n"
    return {file_name: model_result_text}


file_names = ['aslanidi_atrial_model_2009.cellml',
              'aslanidi_Purkinje_model_2009.cellml',
              'beeler_reuter_model_1977.cellml',
              'benson_epicardial_2008.cellml',
              'bernus_wilders_zemlin_verschelde_panfilov_2002.cellml',
              'bondarenko_szigeti_bett_kim_rasmusson_2004_apical.cellml',
              'bondarenko_szigeti_bett_kim_rasmusson_2004_septal.cellml',
              'bueno_2007_endo.cellml',
              'bueno_2007_epi.cellml',
              'carro_2011_endo.cellml',
              'carro_2011_epi.cellml',
              'clancy_rudy_2002.cellml',
              'corrias_purkinje_2011.cellml',
              'courtemanche_ramirez_nattel_1998.cellml',
              'davies_isap_2012.cellml',
              'decker_2009.cellml',
              'demir_model_1994.cellml',
              'difrancesco_noble_model_1985.cellml',
              'dokos_model_1996.cellml',
              'earm_noble_model_1990.cellml',
              'espinosa_model_1998_normal.cellml',
              'faber_rudy_2000.cellml',
              'fink_noble_giles_model_2008.cellml',
              'fox_mcharg_gilmour_2002.cellml',
              'grandi_pasqualini_bers_2010_ss.cellml',
              'grandi_pasqualini_bers_2010_ss_endo.cellml',
              'hilgemann_noble_model_1987.cellml',
              'hodgkin_huxley_squid_axon_model_1952_modified.cellml',
              'hund_rudy_2004.cellml',
              'iribe_model_2006.cellml',
              'iyer_2004.cellml',
              'iyer_model_2007.cellml',
              'jafri_rice_winslow_model_1998.cellml',
              'kurata_model_2002.cellml',
              'lindblad_model_1996.cellml',
              'livshitz_rudy_2007.cellml',
              'li_mouse_2010.cellml',
              'luo_rudy_1991.cellml',
              'luo_rudy_1994.cellml',
              'mahajan_shiferaw_2008.cellml',
              'maleckar_model_2009.cellml',
              'maltsev_2009.cellml',
              'matsuoka_model_2003.cellml',
              'mcallister_noble_tsien_1975_b.cellml',
              'noble_model_1962.cellml',
              'noble_model_1991.cellml',
              'noble_model_1998.cellml',
              'noble_model_2001.cellml',
              'noble_noble_SAN_model_1984.cellml',
              'noble_SAN_model_1989.cellml',
              'nygren_atrial_model_1998.cellml',
              'ohara_rudy_2011_endo.cellml',
              'ohara_rudy_2011_epi.cellml',
              'ohara_rudy_cipa_v1_2017.cellml',
              'paci_hyttinen_aaltosetala_severi_atrialVersion.cellml',
              'paci_hyttinen_aaltosetala_severi_ventricularVersion.cellml',
              'pandit_clark_giles_demir_2001_endocardial_cell.cellml',
              'pandit_clark_giles_demir_2001_epicardial_cell.cellml',
              'pasek_simurda_christe_2006.cellml',
              'pasek_simurda_orchard_christe_2008.cellml',
              'priebe_beuckelmann_1998.cellml',
              'ramirez_nattel_courtemanche_2000.cellml',
              'sachse_moreno_abildskov_2008_b.cellml',
              'sakmann_model_2000_epi.cellml',
              'shannon_wang_puglisi_weber_bers_2004.cellml',
              'stewart_zhang_model_2008_ss.cellml',
              'ten_tusscher_model_2004_endo.cellml',
              'ten_tusscher_model_2004_epi.cellml',
              'ten_tusscher_model_2004_M.cellml',
              'ten_tusscher_model_2006_endo.cellml',
              'ten_tusscher_model_2006_epi.cellml',
              'ten_tusscher_model_2006_M.cellml',
              'ToRORd_fkatp_endo.cellml',
              'ToRORd_fkatp_epi.cellml',
              'Trovato2020.cellml',
              'viswanathan_model_1999_epi.cellml',
              'wang_sobie_2008.cellml',
              'winslow_model_1999.cellml',
              'zhang_SAN_model_2000_0D_capable.cellml'
              ]

if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())
    results = pool.map(process_model, file_names)
    results.sort(key=lambda m: file_names.index(list(m.keys())[0]))
    for res in results:
        print(list(res.values())[0])
