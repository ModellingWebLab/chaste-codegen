import os

import pytest
from cellmlmanip import load_model

import chaste_codegen as cg
from chaste_codegen._chaste_printer import ChastePrinter
from chaste_codegen._lookup_tables import _DEFAULT_LOOKUP_PARAMETERS, _EXPENSIVE_FUNCTIONS, LookupTables


@pytest.fixture(scope='session')
def hn_model():
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'hilgemann_noble_model_1987.cellml')
    return load_model(model_folder)


def test_defaults(hn_model):
    """ Test to check defaults are not changed unintentionally"""
    assert str(_EXPENSIVE_FUNCTIONS) == ("(exp, log, log, sin, cos, tan, sec, csc, cot, sinh, cosh, tanh, sech, csch, "
                                         "coth, asin, acos, atan, asinh, acosh, atanh, asec, acsc, acot, asech, acsch,"
                                         " acoth, exp_, acos_, cos_, sin_)")
    assert _DEFAULT_LOOKUP_PARAMETERS == (['membrane_voltage', -250.0001, 549.9999, 0.001], )


def test_no_method_printed_for(hn_model):
    lut = LookupTables(hn_model)
    lut.calc_lookup_tables(hn_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)
    output = ""
    for eq in hn_model.equations:
        output += printer.doprint(eq)
    assert '_lt_0_row[0]' not in output
    assert lut.print_lookup_parameters(printer) == \
        [['membrane_voltage', -250.0001, 549.9999, 0.001, set(), 'membrane$V',
         ['8000.0 * exp(-(66.0 + membrane$V) * 0.056)', '20.0 * exp(-(75.0 + membrane$V) * 0.125)',
          '2000.0 / (320.0 * exp(-(75.0 + membrane$V) * 0.1) + 1.0)', 'exp((-40.0 + membrane$V) * 0.08)']]]


def test_method_printed_for(hn_model):
    lut = LookupTables(hn_model)
    lut.calc_lookup_tables(hn_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    output = ""
    for eq in hn_model.equations:
        with lut.method_being_printed('template_method'):
            output += printer.doprint(eq.rhs)
    assert '_lt_0_row[0]' in output

    assert lut.print_lookup_parameters(printer) == \
        [['membrane_voltage', -250.0001, 549.9999, 0.001, {'template_method'}, 'membrane$V',
         ['8000.0 * exp(-(66.0 + membrane$V) * 0.056)', '20.0 * exp(-(75.0 + membrane$V) * 0.125)',
          '2000.0 / (320.0 * exp(-(75.0 + membrane$V) * 0.1) + 1.0)', 'exp((-40.0 + membrane$V) * 0.08)']]]


def test_nested_method_printed_for(hn_model):
    lut = LookupTables(hn_model)
    lut.calc_lookup_tables(hn_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    output = ""
    for eq in hn_model.equations:
        with lut.method_being_printed('outer_method'):
            with lut.method_being_printed('innter_method'):
                output += printer.doprint(eq.rhs)
    assert '_lt_0_row[0]' in output

    assert lut.print_lookup_parameters(printer) == \
        [['membrane_voltage', -250.0001, 549.9999, 0.001, {'outer_method'}, 'membrane$V',
         ['8000.0 * exp(-(66.0 + membrane$V) * 0.056)', '20.0 * exp(-(75.0 + membrane$V) * 0.125)',
          '2000.0 / (320.0 * exp(-(75.0 + membrane$V) * 0.1) + 1.0)', 'exp((-40.0 + membrane$V) * 0.08)']]]


def test_multiple_methods_printed_for(hn_model):
    lut = LookupTables(hn_model)
    lut.calc_lookup_tables(hn_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    for eq in hn_model.equations:
        with lut.method_being_printed('method1'):
            printer.doprint(eq.rhs)

    for eq in hn_model.equations:
        with lut.method_being_printed('method2'):
            printer.doprint(eq.rhs)
    assert lut.print_lookup_parameters(printer) == \
        [['membrane_voltage', -250.0001, 549.9999, 0.001, {'method1', 'method2'}, 'membrane$V',
         ['8000.0 * exp(-(66.0 + membrane$V) * 0.056)', '20.0 * exp(-(75.0 + membrane$V) * 0.125)',
          '2000.0 / (320.0 * exp(-(75.0 + membrane$V) * 0.1) + 1.0)', 'exp((-40.0 + membrane$V) * 0.08)']]]


def test_change_lookup_table():
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'cellml', 'LuoRudy1991.cellml')
    model = load_model(model_folder)

    lut = LookupTables(model, lookup_params=[['membrane_voltage', -25.0001, 54.9999, 0.01],
                                             ['cytosolic_calcium_concentration', 0.0, 50.0, 0.01]])
    lut.calc_lookup_tables(model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    output = ""
    for eq in model.equations:
        with lut.method_being_printed('template_method'):
            output += printer.doprint(eq.rhs)
    assert '_lt_0_row[0]' in output
    assert '_lt_1_row[0]' in output

    assert lut.print_lookup_parameters(printer) == \
        [['membrane_voltage', -25.0001, 54.9999, 0.01, {'template_method'}, 'membrane$V',
          ['(47.13 + membrane$V) * 0.32 / (-exp(-(47.13 + membrane$V) * 0.1) + 1.0)',
           '0.08 * exp(-membrane$V / 11.0)',
           '((40.0 < -membrane$V) ? (0.135 * exp(-(80.0 + membrane$V) / 6.8)) : (0.0))',
           '((40.0 < -membrane$V) ? (3.56 * exp(0.079 * membrane$V) + 310000.0 * exp(0.35 * membrane$V)) : '
           '(1.0 / ((1.0 + exp(-(10.66 + membrane$V) / 11.1)) * 0.13)))',
           '((40.0 < -membrane$V) ? ((-127140.0 * exp(0.2444 * membrane$V) - 3.474e-05 * exp(-0.04391 * membrane$V)) *'
           ' (37.78 + membrane$V) / (1.0 + exp((79.23 + membrane$V) * 0.311))) : (0.0))',
           '((40.0 < -membrane$V) ? (0.1212 * exp(-0.01052 * membrane$V) / (1.0 + exp(-(40.14 + membrane$V) * 0.1378))'
           ') : (0.3 * exp(-2.535e-07 * membrane$V) / (1.0 + exp(-(32.0 + membrane$V) * 0.1))))',
           '0.095 * exp(-(-5.0 + membrane$V) * 0.01) / (1.0 + exp(-(-5.0 + membrane$V) * 0.072))',
           '0.07 * exp(-(44.0 + membrane$V) * 0.017) / (1.0 + exp((44.0 + membrane$V) * 0.05))',
           '0.012 * exp(-(28.0 + membrane$V) * 0.008) / (1.0 + exp((28.0 + membrane$V) * 0.15))',
           '0.0065 * exp(-(30.0 + membrane$V) * 0.02) / (1.0 + exp(-(30.0 + membrane$V) * 0.2))',
           '0.0005 * exp((50.0 + membrane$V) * 0.083) / (1.0 + exp((50.0 + membrane$V) * 0.057))',
           '0.0013 * exp(-(20.0 + membrane$V) * 0.06) / (1.0 + exp(-(20.0 + membrane$V) * 0.04))',
           '((100.0 > -membrane$V) ? ((-1.0 + exp((77.0 + membrane$V) * 0.04)) * 2.837 / ((77.0 + membrane$V) * '
           'exp((35.0 + membrane$V) * 0.04))) : (1.0))',
           '1.0 / (1.0 + exp((-membrane$V + 7.488) / 5.98))']],
         ['cytosolic_calcium_concentration', 0.0, 50.0, 0.01, {'template_method'},
          'intracellular_calcium_concentration$Cai',
          ['-13.0287 * log(intracellular_calcium_concentration$Cai / 1.0) + 7.7']]]


def test_no_print_after_table(hn_model):
    lut = LookupTables(hn_model)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)
    assert lut.print_lookup_parameters(printer) == []

    with pytest.raises(ValueError, match="Cannot print lookup expression after main table has been printed"):
        for eq in hn_model.equations:
            printer.doprint(eq)


def test_no_calc_after_print(hn_model):
    lut = LookupTables(hn_model)
    lut.calc_lookup_tables(hn_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    for eq in hn_model.equations:
        printer.doprint(eq)

    with pytest.raises(ValueError, match="Cannot calculate lookup tables after printing has started"):
        lut.calc_lookup_tables(hn_model.equations)

