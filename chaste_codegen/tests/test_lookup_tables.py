import os

import pytest

from chaste_codegen._chaste_printer import ChastePrinter
from chaste_codegen._lookup_tables import _EXPENSIVE_FUNCTIONS, DEFAULT_LOOKUP_PARAMETERS, LookupTables
from chaste_codegen.tests.conftest import TESTS_FOLDER


def test_defaults(s_model):
    """ Test to check defaults are not changed unintentionally"""
    assert str(_EXPENSIVE_FUNCTIONS) == ("(exp, log, log, sin, cos, tan, sec, csc, cot, sinh, cosh, tanh, sech, csch, "
                                         "coth, asin, acos, atan, asinh, acosh, atanh, asec, acsc, acot, asech, acsch,"
                                         " acoth, exp_, acos_, cos_, sin_)")
    assert DEFAULT_LOOKUP_PARAMETERS == (['membrane_voltage', -250.0, 550.0, 0.001], )


def test_no_method_printed_for(s_model):
    lut = LookupTables(s_model)
    lut.calc_lookup_tables(s_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)
    output = ""
    for eq in s_model.equations:
        output += printer.doprint(eq)
    assert '_lt_0_row[0]' not in output
    # We can't use an external text files here since the data contains sets
    # printing these would make the test dependant on their order
    params_for_printing = lut.print_lookup_parameters(printer)

    assert len(params_for_printing) == 1
    assert sorted(params_for_printing[0].keys()) == \
        ['lookup_epxrs', 'mTableMaxs', 'mTableMins', 'mTableSteps', 'metadata_tag', 'table_used_in_methods', 'var']
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['mTableMins'] == -250.0
    assert params_for_printing[0]['mTableMaxs'] == 550.0
    assert params_for_printing[0]['mTableSteps'] == 0.001
    assert params_for_printing[0]['table_used_in_methods'] == set()
    assert params_for_printing[0]['var'] == 'cell$V'

    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_no_method_printed_for.txt'), 'r').read()
    assert str(params_for_printing[0]['lookup_epxrs']) == expected, str(params_for_printing[0]['lookup_epxrs'])


def test_method_printed_for(s_model):
    lut = LookupTables(s_model)
    lut.calc_lookup_tables(s_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    output = ""
    for eq in s_model.equations:
        with lut.method_being_printed('template_method'):
            output += printer.doprint(eq.rhs)
    assert '_lt_0_row[0]' in output

    params_for_printing = lut.print_lookup_parameters(printer)

    assert len(params_for_printing) == 1
    assert sorted(params_for_printing[0].keys()) == \
        ['lookup_epxrs', 'mTableMaxs', 'mTableMins', 'mTableSteps', 'metadata_tag', 'table_used_in_methods', 'var']
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['mTableMins'] == -250.0
    assert params_for_printing[0]['mTableMaxs'] == 550.0
    assert params_for_printing[0]['mTableSteps'] == 0.001
    assert params_for_printing[0]['table_used_in_methods'] == set({'template_method'})
    assert params_for_printing[0]['var'] == 'cell$V'

    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_method_printed_for.txt'), 'r').read()
    assert str(params_for_printing[0]['lookup_epxrs']) == expected, str(params_for_printing[0]['lookup_epxrs'])


def test_nested_method_printed_for(s_model):
    lut = LookupTables(s_model)
    lut.calc_lookup_tables(s_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    output = ""
    for eq in s_model.equations:
        with lut.method_being_printed('outer_method'):
            with lut.method_being_printed('innter_method'):
                output += printer.doprint(eq.rhs)
    assert '_lt_0_row[0]' in output

    params_for_printing = lut.print_lookup_parameters(printer)

    assert len(params_for_printing) == 1
    assert sorted(params_for_printing[0].keys()) == \
        ['lookup_epxrs', 'mTableMaxs', 'mTableMins', 'mTableSteps', 'metadata_tag', 'table_used_in_methods', 'var']
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['mTableMins'] == -250.0
    assert params_for_printing[0]['mTableMaxs'] == 550.0
    assert params_for_printing[0]['mTableSteps'] == 0.001
    assert params_for_printing[0]['table_used_in_methods'] == set({'outer_method'})
    assert params_for_printing[0]['var'] == 'cell$V'

    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_nested_method_printed_for.txt'), 'r').read()
    assert str(params_for_printing[0]['lookup_epxrs']) == expected, str(params_for_printing[0]['lookup_epxrs'])


def test_multiple_methods_printed_for(s_model):
    lut = LookupTables(s_model)
    lut.calc_lookup_tables(s_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    for eq in s_model.equations:
        with lut.method_being_printed('method1'):
            printer.doprint(eq.rhs)

    for eq in s_model.equations:
        with lut.method_being_printed('method2'):
            printer.doprint(eq.rhs)

    params_for_printing = lut.print_lookup_parameters(printer)

    assert len(params_for_printing) == 1
    assert sorted(params_for_printing[0].keys()) == \
        ['lookup_epxrs', 'mTableMaxs', 'mTableMins', 'mTableSteps', 'metadata_tag', 'table_used_in_methods', 'var']
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['mTableMins'] == -250.0
    assert params_for_printing[0]['mTableMaxs'] == 550.0
    assert params_for_printing[0]['mTableSteps'] == 0.001
    assert params_for_printing[0]['table_used_in_methods'] == set({'method1', 'method2'})
    assert params_for_printing[0]['var'] == 'cell$V'

    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_multiple_methods_printed_for.txt'), 'r').read()
    assert str(params_for_printing[0]['lookup_epxrs']) == expected, str(params_for_printing[0]['lookup_epxrs'])


def test_change_lookup_table(be_model):
    lut = LookupTables(be_model, lookup_params=[['membrane_voltage', -25.0001, 54.9999, 0.01],
                                                ['cytosolic_calcium_concentration', 0.0, 50.0, 0.01],
                                                ['unknown_tag', 0.0, 50.0, 0.01]])
    lut.calc_lookup_tables(be_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    output = ""
    for eq in be_model.equations:
        with lut.method_being_printed('template_method'):
            output += printer.doprint(eq.rhs)
    assert '_lt_0_row[0]' in output
    assert '_lt_1_row[0]' in output
    assert '_lt_2_row[0]' not in output

    params_for_printing = lut.print_lookup_parameters(printer)

    assert len(params_for_printing) == 2
    assert all([sorted(p.keys()) ==
                ['lookup_epxrs', 'mTableMaxs', 'mTableMins', 'mTableSteps', 'metadata_tag',
                 'table_used_in_methods', 'var'] for p in params_for_printing])
    assert params_for_printing[0]['metadata_tag'] == 'membrane_voltage'
    assert params_for_printing[0]['mTableMins'] == -25.0001
    assert params_for_printing[0]['mTableMaxs'] == 54.9999
    assert params_for_printing[0]['mTableSteps'] == 0.01
    assert params_for_printing[0]['table_used_in_methods'] == set({'template_method'})
    assert params_for_printing[0]['var'] == 'membrane$V'

    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_change_lookup_table.txt'), 'r').read()
    assert str(params_for_printing[0]['lookup_epxrs']) == expected, str(params_for_printing[0]['lookup_epxrs'])

    assert params_for_printing[1]['metadata_tag'] == 'cytosolic_calcium_concentration'
    assert params_for_printing[1]['mTableMins'] == 0.0
    assert params_for_printing[1]['mTableMaxs'] == 50.0
    assert params_for_printing[1]['mTableSteps'] == 0.01
    assert params_for_printing[1]['table_used_in_methods'] == set({'template_method'})
    assert params_for_printing[1]['var'] == 'slow_inward_current$Cai'

    assert str(params_for_printing[1]['lookup_epxrs']) \
        == "[['-82.3 - 13.0287 * log(0.001 * slow_inward_current$Cai)', False]]"


def test_no_print_after_table(s_model):
    lut = LookupTables(s_model)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)
    assert lut.print_lookup_parameters(printer) == []

    with pytest.raises(ValueError, match="Cannot print lookup expression after main table has been printed"):
        for eq in s_model.equations:
            printer.doprint(eq)


def test_no_calc_after_print(s_model):
    lut = LookupTables(s_model)
    lut.calc_lookup_tables(s_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    for eq in s_model.equations:
        printer.doprint(eq)

    with pytest.raises(ValueError, match="Cannot calculate lookup tables after printing has started"):
        lut.calc_lookup_tables(s_model.equations)
