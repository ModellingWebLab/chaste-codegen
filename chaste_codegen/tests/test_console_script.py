import logging
import os
import sys
from unittest import mock

import chaste_codegen as cg
from chaste_codegen._command_line_script import chaste_codegen
from chaste_codegen.tests.chaste_test_utils import compare_file_against_reference


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_script_help(capsys):
    """Test help message"""
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
    """Test version number message"""
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
    """Test script usage message"""
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
    """Test what happens when supplying wrong cvode options"""
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
    """Convert a normal model via command line script"""
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
    """Convert a normal model with a given class name and dynamicly loadable via command line script"""
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
    """Convert a normal model with expose annotated variables on"""
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
    """Convert an optimised model type"""
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
    """Convert a CVODE model type"""
    LOGGER.info('Testing model with options -t ChasteOpt and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'mahajan_2008'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'mahajan_2008.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'CVODE', '-o', outfile, '-c', 'Cellmahajan_2008FromCellMLCvode']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'Cvode')
    compare_file_against_reference(os.path.join(reference, 'mahajan_2008.hpp'),
                                   os.path.join(tmp_path, 'mahajan_2008.hpp'))
    compare_file_against_reference(os.path.join(reference, 'mahajan_2008.cpp'),
                                   os.path.join(tmp_path, 'mahajan_2008.cpp'))


def test_script_cvode_jacobian(capsys, tmp_path):
    """Convert a CVODE model type with jacobian"""
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


def test_script_dynamic_BE(capsys, tmp_path):
    """Convert a BackwardsEuler model type"""
    LOGGER.info('Testing model with options -t BackwardsEuler, and --dynamically-loadable for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'luo_rudy_1994'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_luo_rudy_1994.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'BackwardsEuler', '-o', outfile,
                '-c', 'Dynamicluo_rudy_1994FromCellMLBackwardEuler', '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'BE')
    compare_file_against_reference(os.path.join(reference, 'dynamic_luo_rudy_1994.hpp'),
                                   os.path.join(tmp_path, 'dynamic_luo_rudy_1994.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_luo_rudy_1994.cpp'),
                                   os.path.join(tmp_path, 'dynamic_luo_rudy_1994.cpp'))


def test_script_dynamic_RL(capsys, tmp_path):
    """Convert a RushLarsen model type"""
    LOGGER.info('Testing model with options -t RushLarsen, and --dynamically-loadable for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'luo_rudy_1994'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_luo_rudy_1994.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'RushLarsen', '-o', outfile,
                '-c', 'Dynamicluo_rudy_1994FromCellMLRushLarsen', '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'RL')
    compare_file_against_reference(os.path.join(reference, 'dynamic_luo_rudy_1994.hpp'),
                                   os.path.join(tmp_path, 'dynamic_luo_rudy_1994.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_luo_rudy_1994.cpp'),
                                   os.path.join(tmp_path, 'dynamic_luo_rudy_1994.cpp'))


def test_script_RLopt(capsys, tmp_path):
    """Convert a RushLarsen model type"""
    LOGGER.info('Testing model with options -t RushLarsenOpt,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'matsuoka_model_2003'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'matsuoka_model_2003.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'RushLarsenOpt', '-o', outfile,
                '-c', 'Cellmatsuoka_model_2003FromCellMLRushLarsen']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'RLopt')
    compare_file_against_reference(os.path.join(reference, 'matsuoka_model_2003.hpp'),
                                   os.path.join(tmp_path, 'matsuoka_model_2003.hpp'))
    compare_file_against_reference(os.path.join(reference, 'matsuoka_model_2003.cpp'),
                                   os.path.join(tmp_path, 'matsuoka_model_2003.cpp'))


def test_script_GRL1(capsys, tmp_path):
    """Convert a Generalised RushLarsen First Order model type"""
    LOGGER.info('Testing model Generalised RushLarsen First Order,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'luo_rudy_1994'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_luo_rudy_1994.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'GeneralisedRushLarsen1', '-o', outfile,
                '-c', 'Dynamicluo_rudy_1994FromCellMLGRL1', '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'GRL1')
    compare_file_against_reference(os.path.join(reference, 'dynamic_luo_rudy_1994.hpp'),
                                   os.path.join(tmp_path, 'dynamic_luo_rudy_1994.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_luo_rudy_1994.cpp'),
                                   os.path.join(tmp_path, 'dynamic_luo_rudy_1994.cpp'))


def test_script_GRL1Opt(capsys, tmp_path):
    """Convert a Generalised RushLarsen First Order Opt model type"""
    LOGGER.info('Testing model Generalised RushLarsen First Order Opt ,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'matsuoka_model_2003'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'matsuoka_model_2003.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'GeneralisedRushLarsen1Opt', '-o', outfile,
                '-c', 'Cellmatsuoka_model_2003FromCellMLGRL1']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'GRL1Opt')
    compare_file_against_reference(os.path.join(reference, 'matsuoka_model_2003.hpp'),
                                   os.path.join(tmp_path, 'matsuoka_model_2003.hpp'))
    compare_file_against_reference(os.path.join(reference, 'matsuoka_model_2003.cpp'),
                                   os.path.join(tmp_path, 'matsuoka_model_2003.cpp'))


def test_script_GRL2(capsys, tmp_path):
    """Convert a Generalised RushLarsen First Order model type"""
    LOGGER.info('Testing model Generalised RushLarsen First Order,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'luo_rudy_1994'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_luo_rudy_1994.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'GeneralisedRushLarsen2', '-o', outfile,
                '-c', 'Dynamicluo_rudy_1994FromCellMLGRL2', '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'GRL2')
    compare_file_against_reference(os.path.join(reference, 'dynamic_luo_rudy_1994.hpp'),
                                   os.path.join(tmp_path, 'dynamic_luo_rudy_1994.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_luo_rudy_1994.cpp'),
                                   os.path.join(tmp_path, 'dynamic_luo_rudy_1994.cpp'))


def test_script_GRL2Opt(capsys, tmp_path):
    """Convert a Generalised RushLarsen First Order Opt model type"""
    LOGGER.info('Testing model Generalised RushLarsen First Order Opt ,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'viswanathan_model_1999_epi'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'viswanathan_model_1999_epi.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'GeneralisedRushLarsen2Opt', '-o', outfile,
                '-c', 'Cellviswanathan_model_1999_epiFromCellMLGRL2']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'GRL2Opt')
    compare_file_against_reference(os.path.join(reference, 'viswanathan_model_1999_epi.hpp'),
                                   os.path.join(tmp_path, 'viswanathan_model_1999_epi.hpp'))
    compare_file_against_reference(os.path.join(reference, 'viswanathan_model_1999_epi.cpp'),
                                   os.path.join(tmp_path, 'viswanathan_model_1999_epi.cpp'))


def test_script_CVODE_DATA_CLAMP(capsys, tmp_path):
    """Convert a CVODE with Data Clamp model type"""
    LOGGER.info('Testing model CVODE with data clamp ,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'Shannon2004'
    model_file = os.path.join(cg.DATA_DIR, 'tests', 'cellml', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_Shannon2004.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-t', 'CVODE', '-o', outfile, '--dynamically-loadable',
                '-c', 'DynamicShannon2004FromCellMLCvodeDataClamp']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(cg.DATA_DIR, 'tests'), 'chaste_reference_models', 'CVODE_DATA_CLAMP')
    compare_file_against_reference(os.path.join(reference, 'dynamic_Shannon2004.hpp'),
                                   os.path.join(tmp_path, 'dynamic_Shannon2004.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_Shannon2004.cpp'),
                                   os.path.join(tmp_path, 'dynamic_Shannon2004.cpp'))
