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
    assert DEFAULT_LOOKUP_PARAMETERS == (['membrane_voltage', -250.0001, 549.9999, 0.001], )


def test_no_method_printed_for(s_model):
    lut = LookupTables(s_model)
    lut.calc_lookup_tables(s_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)
    output = ""
    for eq in s_model.equations:
        output += printer.doprint(eq)
    assert '_lt_0_row[0]' not in output
    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_1.txt'), 'r').read()
    assert str(lut.print_lookup_parameters(printer)) == expected, str(lut.print_lookup_parameters(printer))


def test_method_printed_for(s_model):
    lut = LookupTables(s_model)
    lut.calc_lookup_tables(s_model.equations)
    printer = ChastePrinter(lookup_table_function=lut.print_lut_expr)

    output = ""
    for eq in s_model.equations:
        with lut.method_being_printed('template_method'):
            output += printer.doprint(eq.rhs)
    assert '_lt_0_row[0]' in output
    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_2.txt'), 'r').read()
    assert str(lut.print_lookup_parameters(printer)) == expected, str(lut.print_lookup_parameters(printer))


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
    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_3.txt'), 'r').read()
    assert str(lut.print_lookup_parameters(printer)) == expected, str(lut.print_lookup_parameters(printer))


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
    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_4.txt'), 'r').read()
    params = lut.print_lookup_parameters(printer)
    # check table_used_in_methods entry and replace sorted list to aid comparisson
    # (as varying order  coud disrupt string comparisson)
    assert len(params) == 1
    assert params[0]['table_used_in_methods'] == set({'method1', 'method2'})
    params[0]['table_used_in_methods'] = sorted(params[0]['table_used_in_methods'])
    print(lut.print_lookup_parameters(printer))
    assert str(lut.print_lookup_parameters(printer)) == expected, str(lut.print_lookup_parameters(printer))


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
    expected = open(os.path.join(TESTS_FOLDER, 'test_lookup_tables_5.txt'), 'r').read()
    assert str(lut.print_lookup_parameters(printer)) == expected, str(lut.print_lookup_parameters(printer))


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

