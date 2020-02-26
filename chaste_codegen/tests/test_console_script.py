import sys
import logging
import os
import chaste_codegen as cg
from unittest import mock
from chaste_codegen._command_line_script import chaste_codegen
from chaste_codegen.tests.chaste_test_utils import compare_file_against_reference


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_script_help(capsys):
    LOGGER.info('Testing help for command line script\n')
    testargs = ["chaste_codegen", "-h"]
    with mock.patch.object(sys, 'argv', testargs):
        try:
            chaste_codegen()
        except SystemExit:
            pass  # We expect this to print usage and exit
        captured = capsys.readouterr()
        # compare to expected
        output = str(captured.out)
        expected = open(os.path.join(cg.DATA_DIR, 'tests', 'console_script_help.txt'), 'r').read()
        assert output == expected


def test_script_version(capsys):
    LOGGER.info('Testing version for command line script\n')
    testargs = ["chaste_codegen", "--version"]
    with mock.patch.object(sys, 'argv', testargs):
        try:
            chaste_codegen()
        except SystemExit:
            pass  # We expect this to print usage and exit
        captured = capsys.readouterr()
        # compare to expected
        output = str(captured.out)
        assert output == 'chaste_codegen ' + cg.__version__ + '\n'


def test_usage(capsys):
    LOGGER.info('Testing illegal combination of options for jacobians on command line\n')
    testargs = ["chaste_codegen"]
    with mock.patch.object(sys, 'argv', testargs):
        try:
            chaste_codegen()
        except SystemExit:
            pass  # We expect this to print usage and exit
        captured = capsys.readouterr()
        # compare to expected
        error = str(captured.err)
        expected = open(os.path.join(cg.DATA_DIR, 'tests', 'usage.txt'), 'r').read()
        print(error)
        assert error == expected


def test_wrong_cvode_options(capsys):
    LOGGER.info('Testing illegal combination of options for jacobians on command line\n')
    testargs = ["chaste_codegen", "-j", 'somefile.cellml']
    with mock.patch.object(sys, 'argv', testargs):
        try:
            chaste_codegen()
        except SystemExit:
            pass  # We expect this to print usage and exit
        captured = capsys.readouterr()
        # compare to expected
        error = str(captured.err)
        expected = open(os.path.join(cg.DATA_DIR, 'tests', 'wrong_cvode_options.txt'), 'r').read()
        assert error == expected


def test_script_convert(capsys, tmp_path):
    LOGGER.info('Testing regular model conversion for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'aslanidi_model_2009'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    testargs = ["chaste_codegen", model_file]
    # Call commandline script
    savedPath = str(os.getcwd())
    os.chdir(tmp_path)
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    os.chdir(savedPath)
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Normal')
    compare_file_against_reference(os.path.join(reference, model_name + '.hpp'),
                                   os.path.join(tmp_path, model_name + '.hpp'))
    compare_file_against_reference(os.path.join(reference, model_name + '.cpp'),
                                   os.path.join(tmp_path, model_name + '.cpp'))


def test_script_class_convtype_output_dll_loadable(capsys, tmp_path):
    LOGGER.info('Testing model with options -t Chaste -c --dynamically-loadable and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'aslanidi_model_2009'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'output_class.c')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-c', 'Chaste_CG', '-t', 'Chaste', '-o', outfile,
                '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Normal')
    compare_file_against_reference(os.path.join(reference, 'output_class.h'),
                                   os.path.join(tmp_path, 'output_class.h'))
    compare_file_against_reference(os.path.join(reference, 'output_class.c'),
                                   os.path.join(tmp_path, 'output_class.c'))


def test_script_output_expose_annotated_variables(capsys, tmp_path):
    LOGGER.info('Testing model with options --expose-annotated-variables and -o for command line script\n')
    tmp_path = str(tmp_path)
    # Check options: -o --expose-annotated-variables
    model_name = 'aslanidi_model_2009'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    model_file = str(model_file)
    outfile = os.path.join(tmp_path, 'expose_annotated_variables_cellaslanidi_model_2009.cpp')
    outfile = str(outfile)
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-o', outfile, '--expose-annotated-variables']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    model_name = 'expose_annotated_variables_cellaslanidi_model_2009'
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Normal')
    compare_file_against_reference(os.path.join(reference, model_name + '.hpp'),
                                   os.path.join(tmp_path, model_name + '.hpp'))
    compare_file_against_reference(os.path.join(reference, model_name + '.cpp'),
                                   os.path.join(tmp_path, model_name + '.cpp'))


def test_script_opt(capsys, tmp_path):
    LOGGER.info('Testing model with options -t ChasteOpt and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'livshitz_rudy_2007'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'livshitz_rudy_2007.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'ChasteOpt', '-o', outfile]
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Opt')
    compare_file_against_reference(os.path.join(reference, 'livshitz_rudy_2007.hpp'),
                                   os.path.join(tmp_path, 'livshitz_rudy_2007.hpp'))
    compare_file_against_reference(os.path.join(reference, 'livshitz_rudy_2007.cpp'),
                                   os.path.join(tmp_path, 'livshitz_rudy_2007.cpp'))


def test_script_cvode(capsys, tmp_path):
    LOGGER.info('Testing model with options -t ChasteOpt and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'luo_rudy_1994'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'luo_rudy_1994.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'CVODE', '-o', outfile, '-c', 'Cellluo_rudy_1994FromCellMLCvode']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Cvode')
    compare_file_against_reference(os.path.join(reference, 'luo_rudy_1994.hpp'),
                                   os.path.join(tmp_path, 'luo_rudy_1994.hpp'))
    compare_file_against_reference(os.path.join(reference, 'luo_rudy_1994.cpp'),
                                   os.path.join(tmp_path, 'luo_rudy_1994.cpp'))


def test_script_cvode_jacobian(capsys, tmp_path):
    LOGGER.info('Testing model with options -t ChasteOpt and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'luo_rudy_1994'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'luo_rudy_1994.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'CVODE', '-o', outfile, '-j',
                '-c', 'Cellluo_rudy_1994FromCellMLCvode']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Cvode_with_jacobian')
    compare_file_against_reference(os.path.join(reference, 'luo_rudy_1994.hpp'),
                                   os.path.join(tmp_path, 'luo_rudy_1994.hpp'))
    compare_file_against_reference(os.path.join(reference, 'luo_rudy_1994.cpp'),
                                   os.path.join(tmp_path, 'luo_rudy_1994.cpp'))