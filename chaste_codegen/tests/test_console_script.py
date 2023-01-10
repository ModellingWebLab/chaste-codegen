import logging
import os
import shutil
import sys
from unittest import mock

import chaste_codegen as cg
from chaste_codegen import LOGGER
from chaste_codegen._command_line_script import (
    TRANSLATORS,
    TRANSLATORS_OPT,
    TRANSLATORS_WITH_MODIFIERS,
    chaste_codegen,
)
from chaste_codegen.tests.conftest import CELLML_FOLDER, TESTS_FOLDER, compare_file_against_reference


cg.__version__ = "(version omitted as unimportant)"
cg.chaste_model.TIME_STAMP = "(date omitted as unimportant)"


def test_script_TRANSLATORS(capsys):
    """Test TRANSLATORS are still consistent"""
    LOGGER.info('Testing help for command line script\n')
    assert all((k[2:] in TRANSLATORS.keys() for k in TRANSLATORS_WITH_MODIFIERS))
    assert all((k in TRANSLATORS for k in TRANSLATORS_OPT))


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
        expected = open(os.path.join(TESTS_FOLDER, 'test_console_script_help.txt'), 'r').read()
        expected_python_3_10 = expected.replace('optional arguments', 'options')
        assert str(captured.out) in (expected, expected_python_3_10), str(captured.out)


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
        assert str(captured.out) == 'chaste_codegen ' + cg.__version__ + '\n', str(captured.out)


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
        expected = open(os.path.join(TESTS_FOLDER, 'test_console_script_usage.txt'), 'r').read()
        assert str(captured.err) == expected, str(captured.err)


def test_script_o_output_dif(caplog):
    """Convert a normal model via command line script"""
    LOGGER.info('Testing --show-output\n')
    model_name = 'grandi_pasqualini_bers_2010_ss'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)

    testargs = ["chaste_codegen", '--cvode-data-clamp', '--backward-euler', model_file, '--show-output',
                '-o', '/bla.cppp', '--output-dir', '/']
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "-o and --output-dir cannot be used together!" in caplog.text


def test_script_double_show_output(capsys):
    """Convert a normal model via command line script"""
    LOGGER.info('Testing --show-output\n')
    model_name = 'grandi_pasqualini_bers_2010_ss'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')

    testargs = ["chaste_codegen", '--cvode-data-clamp', '--backward-euler', model_file, '--show-output']
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
        captured = capsys.readouterr()
        output = str(captured.out)
        assert "grandi_pasqualini_bers_2010_ssCvodeDataClamp.cpp" in output
        assert "grandi_pasqualini_bers_2010_ssCvodeDataClamp.hpp" in output
        assert "grandi_pasqualini_bers_2010_ssBackwardEuler.hpp" in output


def test_script_double_show_output2(capsys):
    """Convert a normal model via command line script"""
    LOGGER.info('Testing --show-output\n')
    model_name = 'grandi_pasqualini_bers_2010_ss'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)

    testargs = ["chaste_codegen", '--cvode-data-clamp', '--backward-euler', model_file, '--show-output',
                '--output-dir', '/cellml', '-q']
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
        captured = capsys.readouterr()
        output = str(captured.out).replace("\\", "/")
        assert "/cellml/grandi_pasqualini_bers_2010_ssCvodeDataClamp.cpp" in output
        assert "/cellml/grandi_pasqualini_bers_2010_ssCvodeDataClamp.hpp" in output
        assert "/cellml/grandi_pasqualini_bers_2010_ssBackwardEuler.hpp" in output


def test_non_existing_cellml(caplog):
    """Test converting non-existing cellml file"""
    LOGGER.info('Testing non-existing cellml\n')

    testargs = ["chaste_codegen", "bla.cellml"]
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "Could not find cellml file bla.cellml" in caplog.text


def test_script_convert(caplog, tmp_path):
    """Convert a normal model via command line script"""
    caplog.set_level(logging.INFO, logger='chaste_codegen')
    LOGGER.info('Testing regular model conversion for command line script\n')

    tmp_path = str(tmp_path)
    model_name = 'fox_mcharg_gilmour_2002'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    target = os.path.join(tmp_path, model_name + '.cellml')
    shutil.copyfile(model_file, target)

    testargs = ['chaste_codegen', '--skip-singularity-fixes', target]
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
        assert "The model has no capacitance tagged." in caplog.text

    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Normal')
    compare_file_against_reference(os.path.join(reference, model_name + '_console_script.hpp'),
                                   os.path.join(tmp_path, model_name + '.hpp'))
    compare_file_against_reference(os.path.join(reference, model_name + '_console_script.cpp'),
                                   os.path.join(tmp_path, model_name + '.cpp'))


def test_script_convert_quiet(caplog, tmp_path):
    """Convert a normal model via command line script in quiet mode"""
    caplog.set_level(logging.INFO, logger='chaste_codegen')
    LOGGER.info('Testing regular model conversion for command line script in quiet mode\n')
    tmp_path = str(tmp_path)
    model_name = 'fox_mcharg_gilmour_2002'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    target = os.path.join(tmp_path, model_name + '.cellml')
    shutil.copyfile(model_file, target)

    testargs = ['chaste_codegen', '--skip-singularity-fixes', target, '--quiet']
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
        assert "The model has no capacitance tagged." not in caplog.text

    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Normal')
    compare_file_against_reference(os.path.join(reference, model_name + '_console_script.hpp'),
                                   os.path.join(tmp_path, model_name + '.hpp'))
    compare_file_against_reference(os.path.join(reference, model_name + '_console_script.cpp'),
                                   os.path.join(tmp_path, model_name + '.cpp'))


def test_script_double_type_output(caplog):
    """Convert multiple model types"""
    LOGGER.info('Testing multiple models\n')
    model_name = 'grandi_pasqualini_bers_2010_ss'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)

    testargs = ['chaste_codegen', '--cvode-data-clamp', '--backward-euler', model_file, '-o', 'bla.cpp']
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "-o cannot be used when multiple model types have been selected!" in caplog.text


def test_script_double_type_output2(caplog):
    """Convert multiple model types"""
    LOGGER.info('Testing multiple models\n')
    model_name = 'grandi_pasqualini_bers_2010_ss'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)

    testargs = ['chaste_codegen', '--cvode-data-clamp', '--backward-euler', model_file, '--dynamically-loadable']
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "Only one model type may be specified if creating a dynamic library!" in caplog.text


def test_script_double_type(tmp_path):
    """Convert multiple model types"""
    LOGGER.info('Testing multiple models\n')
    tmp_path = str(tmp_path)
    model_name = 'grandi_pasqualini_bers_2010_ss'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    target = os.path.join(tmp_path, model_name + '.cellml')
    shutil.copyfile(model_file, target)

    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', '--cvode-data-clamp',
                '--backward-euler', target]
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models')

    compare_file_against_reference(os.path.join(reference, 'CVODE_DATA_CLAMP', model_name + 'CvodeDataClamp.hpp'),
                                   os.path.join(tmp_path, model_name + 'CvodeDataClamp.hpp'))
    compare_file_against_reference(os.path.join(reference, 'CVODE_DATA_CLAMP', model_name + 'CvodeDataClamp.cpp'),
                                   os.path.join(tmp_path, model_name + 'CvodeDataClamp.cpp'))

    compare_file_against_reference(os.path.join(reference, 'BE', model_name + 'BackwardEuler.hpp'),
                                   os.path.join(tmp_path, model_name + 'BackwardEuler.hpp'))
    compare_file_against_reference(os.path.join(reference, 'BE', model_name + 'BackwardEuler.cpp'),
                                   os.path.join(tmp_path, model_name + 'BackwardEuler.cpp'))


def test_script_data_clamp_opt(tmp_path):
    """Convert code with data clamp opt"""
    LOGGER.info('Testing multiple models\n')
    tmp_path = str(tmp_path)
    model_name = 'grandi_pasqualini_bers_2010_ss'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    target = os.path.join(tmp_path, model_name + '.cellml')
    shutil.copyfile(model_file, target)

    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', '--cvode-data-clamp', '--opt',
                target]
    # Call commandline script
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models')
    reference_opt = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models')

    compare_file_against_reference(os.path.join(reference, 'CVODE_DATA_CLAMP',
                                                model_name + 'CvodeDataClamp.hpp'),
                                   os.path.join(tmp_path, model_name + 'CvodeDataClamp.hpp'))
    compare_file_against_reference(os.path.join(reference, 'CVODE_DATA_CLAMP',
                                                model_name + 'CvodeDataClamp.cpp'),
                                   os.path.join(tmp_path, model_name + 'CvodeDataClamp.cpp'))

    compare_file_against_reference(os.path.join(reference_opt, 'CVODE_DATA_CLAMP_OPT',
                                                model_name + 'CvodeDataClampOpt.hpp'),
                                   os.path.join(tmp_path, model_name + 'CvodeDataClampOpt.hpp'))
    compare_file_against_reference(os.path.join(reference_opt, 'CVODE_DATA_CLAMP_OPT',
                                                model_name + 'CvodeDataClampOpt.cpp'),
                                   os.path.join(tmp_path, model_name + 'CvodeDataClampOpt.cpp'))


def test_script_class_convtype_output_dll_loadable(tmp_path):
    """Convert a normal model with a given class name and dynamicly loadable via command line script"""
    LOGGER.info('Testing model with options --normal -c --dynamically-loadable and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'noble_model_1998'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'output_class.c')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '-c', 'Chaste_CG',
                '--normal', '-o', outfile, '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Normal')
    compare_file_against_reference(os.path.join(reference, 'output_class.h'),
                                   os.path.join(tmp_path, 'output_class.h'))
    compare_file_against_reference(os.path.join(reference, 'output_class.c'),
                                   os.path.join(tmp_path, 'output_class.c'))


def test_script_opt_dynamic(tmp_path):
    """Convert an optimised normal model type"""
    # If using --opt with output file and/or dynamicly loadable it will generate only opt models
    LOGGER.info('Testing model with options --normal --opt and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'aslanidi_Purkinje_model_2009'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    target = os.path.join(tmp_path, model_name + '.cellml')
    shutil.copyfile(model_file, target)

    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', target, '--normal', '--opt',
                '--dynamically-loadable', '--use-modifiers']

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models')
    compare_file_against_reference(os.path.join(reference, 'Opt', 'dynamic_aslanidi_Purkinje_model_2009.hpp'),
                                   os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009Opt.hpp'))
    compare_file_against_reference(os.path.join(reference, 'Opt', 'dynamic_aslanidi_Purkinje_model_2009.cpp'),
                                   os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009Opt.cpp'))


def test_script_opt(tmp_path):
    """Convert an optimised normal model type"""
    # If using --opt with no output file and not dynamic it will generate both non-opt and opt models
    # this version does not have the ModelFactory stuff
    LOGGER.info('Testing model with options --normal --opt and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'aslanidi_Purkinje_model_2009'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    target = os.path.join(tmp_path, model_name + '.cellml')
    shutil.copyfile(model_file, target)

    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', target, '--normal', '--opt', '--use-modifiers']

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models')
    compare_file_against_reference(os.path.join(reference, 'Opt', 'non_dynamic_aslanidi_Purkinje_model_2009.hpp'),
                                   os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009Opt.hpp'))
    compare_file_against_reference(os.path.join(reference, 'Opt', 'non_dynamic_aslanidi_Purkinje_model_2009.cpp'),
                                   os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009Opt.cpp'))
    compare_file_against_reference(os.path.join(reference, 'Normal', 'non_dynamic_aslanidi_Purkinje_model_2009.hpp'),
                                   os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009.hpp'))
    compare_file_against_reference(os.path.join(reference, 'Normal', 'non_dynamic_aslanidi_Purkinje_model_2009.cpp'),
                                   os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009.cpp'))


def test_script_cvode_opt(tmp_path):
    """Convert an optimised cvode model type"""
    # If using --opt with an output and/or dynamicly loadable file it will generate only the opt model
    LOGGER.info('Testing model with options --normal --opt and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'aslanidi_Purkinje_model_2009'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_aslanidi_Purkinje_model_2009.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '--cvode', '--opt',
                '-o', outfile, '--dynamically-loadable', '--use-modifiers']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Cvode_opt')
    compare_file_against_reference(os.path.join(reference, 'dynamic_aslanidi_Purkinje_model_2009.hpp'),
                                   os.path.join(tmp_path, 'dynamic_aslanidi_Purkinje_model_2009.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_aslanidi_Purkinje_model_2009.cpp'),
                                   os.path.join(tmp_path, 'dynamic_aslanidi_Purkinje_model_2009.cpp'))


def test_script_cvode(tmp_path):
    """Convert a CVODE model type"""
    LOGGER.info('Testing model with options -t CVODE and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'mahajan_shiferaw_2008'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_mahajan_shiferaw_2008.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', model_file, '--cvode', '-o', outfile,
                '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Cvode')
    compare_file_against_reference(os.path.join(reference, 'dynamic_mahajan_shiferaw_2008.hpp'),
                                   os.path.join(tmp_path, 'dynamic_mahajan_shiferaw_2008.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_mahajan_shiferaw_2008.cpp'),
                                   os.path.join(tmp_path, 'dynamic_mahajan_shiferaw_2008.cpp'))


def test_script_cvode_jacobian(tmp_path):
    """Convert a CVODE model type with jacobian"""
    LOGGER.info('Testing model with options --cvode and -o for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'shannon_wang_puglisi_weber_bers_2004'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_Shannon2004.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '--cvode',
                '-o', outfile, '--use-analytic-jacobian', '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Cvode_with_jacobian')
    compare_file_against_reference(os.path.join(reference, 'dynamic_Shannon2004.hpp'),
                                   os.path.join(tmp_path, 'dynamic_Shannon2004.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_Shannon2004.cpp'),
                                   os.path.join(tmp_path, 'dynamic_Shannon2004.cpp'))


def test_script_dynamic_BE(tmp_path):
    """Convert a BackwardsEuler model type"""
    LOGGER.info('Testing model with options --backward-euler, and --dynamically-loadable for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'courtemanche_ramirez_nattel_1998'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_courtemanche_ramirez_nattel_1998.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '--backward-euler',
                '-o', outfile, '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'BE')
    compare_file_against_reference(os.path.join(reference, 'dynamic_courtemanche_ramirez_nattel_1998.hpp'),
                                   os.path.join(tmp_path, 'dynamic_courtemanche_ramirez_nattel_1998.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_courtemanche_ramirez_nattel_1998.cpp'),
                                   os.path.join(tmp_path, 'dynamic_courtemanche_ramirez_nattel_1998.cpp'))


def test_script_dynamic_BEopt(tmp_path):
    """Convert a BackwardsEuler model type"""
    LOGGER.info('Testing model with options --backward-euler, --dynamically-loadable, --opt for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'courtemanche_ramirez_nattel_1998'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_courtemanche_ramirez_nattel_1998.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '--backward-euler',
                '--opt', '-o', outfile, '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'BEopt')
    compare_file_against_reference(os.path.join(reference, 'dynamic_courtemanche_ramirez_nattel_1998.hpp'),
                                   os.path.join(tmp_path, 'dynamic_courtemanche_ramirez_nattel_1998.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_courtemanche_ramirez_nattel_1998.cpp'),
                                   os.path.join(tmp_path, 'dynamic_courtemanche_ramirez_nattel_1998.cpp'))


def test_script_dynamic_RL(tmp_path):
    """Convert a RushLarsen model type"""
    LOGGER.info('Testing model with options --rush-larsen, and --dynamically-loadable for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'livshitz_rudy_2007'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_livshitz_rudy_2007.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', model_file, '--rush-larsen', '-o', outfile,
                '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'RL')
    compare_file_against_reference(os.path.join(reference, 'dynamic_livshitz_rudy_2007.hpp'),
                                   os.path.join(tmp_path, 'dynamic_livshitz_rudy_2007.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_livshitz_rudy_2007.cpp'),
                                   os.path.join(tmp_path, 'dynamic_livshitz_rudy_2007.cpp'))


def test_script_RLopt(tmp_path):
    """Convert a RushLarsen model type"""
    LOGGER.info('Testing model with options --rush-larsen --opt,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'bondarenko_szigeti_bett_kim_rasmusson_2004_apical'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_bondarenko_szigeti_bett_kim_rasmusson_2004_apical.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '--rush-larsen',
                '--opt', '-o', outfile, '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'RLopt')
    compare_file_against_reference(os.path.join(reference,
                                                'dynamic_bondarenko_szigeti_bett_kim_rasmusson_2004_apical.hpp'),
                                   os.path.join(tmp_path,
                                                'dynamic_bondarenko_szigeti_bett_kim_rasmusson_2004_apical.hpp'))
    compare_file_against_reference(os.path.join(reference,
                                                'dynamic_bondarenko_szigeti_bett_kim_rasmusson_2004_apical.cpp'),
                                   os.path.join(tmp_path,
                                                'dynamic_bondarenko_szigeti_bett_kim_rasmusson_2004_apical.cpp'))


def test_script_GRL1(tmp_path):
    """Convert a Generalised RushLarsen First Order model type"""
    LOGGER.info('Testing model Generalised RushLarsen First Order,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'demir_model_1994'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_demir_model_1994.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', model_file, '--grl1', '-o', outfile,
                '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'GRL1')
    compare_file_against_reference(os.path.join(reference, 'dynamic_demir_model_1994.hpp'),
                                   os.path.join(tmp_path, 'dynamic_demir_model_1994.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_demir_model_1994.cpp'),
                                   os.path.join(tmp_path, 'dynamic_demir_model_1994.cpp'))


def test_script_GRL1Opt(tmp_path):
    """Convert a Generalised RushLarsen First Order Opt model type"""
    LOGGER.info('Testing model Generalised RushLarsen First Order Opt ,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'matsuoka_model_2003'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_matsuoka_model_2003.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '--grl1',
                '--opt', '-o', outfile, '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'GRL1Opt')
    compare_file_against_reference(os.path.join(reference, 'dynamic_matsuoka_model_2003.hpp'),
                                   os.path.join(tmp_path, 'dynamic_matsuoka_model_2003.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_matsuoka_model_2003.cpp'),
                                   os.path.join(tmp_path, 'dynamic_matsuoka_model_2003.cpp'))


def test_script_GRL2(tmp_path):
    """Convert a Generalised RushLarsen First Order model type"""
    LOGGER.info('Testing model Generalised RushLarsen First Order,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'winslow_model_1999'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_winslow_model_1999.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', model_file, '--grl2', '-o', outfile,
                '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'GRL2')
    compare_file_against_reference(os.path.join(reference, 'dynamic_winslow_model_1999.hpp'),
                                   os.path.join(tmp_path, 'dynamic_winslow_model_1999.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_winslow_model_1999.cpp'),
                                   os.path.join(tmp_path, 'dynamic_winslow_model_1999.cpp'))


def test_script_GRL2Opt(tmp_path):
    """Convert a Generalised RushLarsen First Order Opt model type"""
    LOGGER.info('Testing model Generalised RushLarsen First Order Opt ,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'viswanathan_model_1999_epi'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_viswanathan_model_1999_epi.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '--grl2',
                '--opt', '-o', outfile, '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'GRL2Opt')
    compare_file_against_reference(os.path.join(reference, 'dynamic_viswanathan_model_1999_epi.hpp'),
                                   os.path.join(tmp_path, 'dynamic_viswanathan_model_1999_epi.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_viswanathan_model_1999_epi.cpp'),
                                   os.path.join(tmp_path, 'dynamic_viswanathan_model_1999_epi.cpp'))


def test_script_CVODE_DATA_CLAMP(tmp_path):
    """Convert a CVODE with Data Clamp model type"""
    LOGGER.info('Testing model CVODE with data clamp ,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'shannon_wang_puglisi_weber_bers_2004'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'dynamic_Shannon2004.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', model_file, '--cvode-data-clamp', '-o', outfile,
                '--dynamically-loadable']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'CVODE_DATA_CLAMP')
    compare_file_against_reference(os.path.join(reference, 'dynamic_Shannon2004.hpp'),
                                   os.path.join(tmp_path, 'dynamic_Shannon2004.hpp'))
    compare_file_against_reference(os.path.join(reference, 'dynamic_Shannon2004.cpp'),
                                   os.path.join(tmp_path, 'dynamic_Shannon2004.cpp'))


def test_script_CVODE_DATA_CLAMP_modifiers(tmp_path):
    """Convert a CVODE with data clamp and modifiers model type with modifiers"""
    LOGGER.info('Testing model CVODE with data clamp ,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'shannon_wang_puglisi_weber_bers_2004'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'Shannon2004_with_modifiers.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--use-model-factory', '--skip-singularity-fixes', model_file, '--cvode-data-clamp',
                '-o', outfile, '--use-modifiers']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'CVODE_DATA_CLAMP')
    compare_file_against_reference(os.path.join(reference, 'Shannon2004_with_modifiers.hpp'),
                                   os.path.join(tmp_path, 'Shannon2004_with_modifiers.hpp'))
    compare_file_against_reference(os.path.join(reference, 'Shannon2004_with_modifiers.cpp'),
                                   os.path.join(tmp_path, 'Shannon2004_with_modifiers.cpp'))


def test_script_lookup_table(tmp_path):
    """Convert a model with custom lookup table"""
    LOGGER.info('Testing custom lookup tables,  for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'beeler_reuter_model_1977'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'beeler_reuter_model_1977_lookup_tables.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', model_file, '--opt', '-o', outfile,
                '--lookup-table', 'membrane_voltage', '-150.0001', '199.9999', '0.01',
                '--lookup-table', 'cytosolic_calcium_concentration', '0.00001', '30.00001', '0.0001']

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Opt')
    compare_file_against_reference(os.path.join(reference, 'beeler_reuter_model_1977_lookup_tables.hpp'),
                                   os.path.join(tmp_path, 'beeler_reuter_model_1977_lookup_tables.hpp'))
    compare_file_against_reference(os.path.join(reference, 'beeler_reuter_model_1977_lookup_tables.cpp'),
                                   os.path.join(tmp_path, 'beeler_reuter_model_1977_lookup_tables.cpp'))


def test_script_lookup_table_no_opt(caplog):
    """Convert a model with custom lookup table"""
    LOGGER.info('Testing custom lookup tables,  for command line script\n')
    model_name = 'beeler_reuter_model_1977'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = 'beeler_reuter_model_1977_lookup_tables.cpp'
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-o', outfile,
                '--lookup-table', 'membrane_voltage', '-150.0001', '199.9999', '0.01',
                '--lookup-table', 'cytosolic_calcium_concentration', '0.00001', '30.00001', '0.0001']

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "Can only use lookup tables in combination with --opt" in caplog.text


def test_script_lookup_table_wrong_args(caplog):
    """Convert a model with custom lookup table"""
    LOGGER.info('Testing custom lookup tables,  for command line script\n')
    model_name = 'beeler_reuter_model_1977'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = 'beeler_reuter_model_1977_lookup_tables.cpp'
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '--opt', '-o', outfile,
                '--lookup-table', '-150.0001', '-150.0001', '199.9999', '0.01']

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "Lookup tables are expecting the following 4 values: <metadata tag> min max step" in caplog.text


def test_script_lookup_table_wrong_args2(caplog):
    """Convert a model with custom lookup table"""
    LOGGER.info('Testing custom lookup tables,  for command line script\n')
    model_name = 'beeler_reuter_model_1977'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = 'beeler_reuter_model_1977_lookup_tables.cpp'
    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', model_file, '--opt', '-o', outfile,
                '--lookup-table', 'membrane_voltage', 'membrane_voltage', '199.9999', '0.01']

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "Lookup tables are expecting the following 4 values: <metadata tag> min max step" in caplog.text


def test_script_lookup_table_check_non_existing_tag_ignored(caplog, tmp_path):
    """Check non-existing metadata tags are ignored"""
    LOGGER.info('Testing custom lookup tables, for command line script\n')
    tmp_path = str(tmp_path)
    model_name = 'beeler_reuter_model_1977'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'beeler_reuter_model_1977_lookup_tables.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', '--skip-singularity-fixes', model_file, '--opt', '-o', outfile,
                '--lookup-table', 'membrane_voltage', '-150.0001', '199.9999', '0.01',
                '--lookup-table', 'cytosolic_calcium_concentration', '0.00001', '30.00001', '0.0001',
                '--lookup-table', 'non_existing_tag', '-150.0001', '199.9999', '0.01']

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()

    assert 'WARNING' in caplog.text
    assert "A lookup table was specified for non_existing_tag but it is not tagged in the model, skipping!" \
        in caplog.text

    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Opt')
    compare_file_against_reference(os.path.join(reference, 'beeler_reuter_model_1977_lookup_tables.hpp'),
                                   os.path.join(tmp_path, 'beeler_reuter_model_1977_lookup_tables.hpp'))
    compare_file_against_reference(os.path.join(reference, 'beeler_reuter_model_1977_lookup_tables.cpp'),
                                   os.path.join(tmp_path, 'beeler_reuter_model_1977_lookup_tables.cpp'))


def test_script_load_non_cellml_file(caplog):
    """Check non-existing metadata tags are ignored"""
    LOGGER.info('Testing loading a file that is not a cellml file\n')
    model_file = os.path.join(TESTS_FOLDER, 'test_console_script_usage.txt')
    # Call commandline script
    testargs = ['chaste_codegen', model_file]

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()

    assert 'ERROR' in caplog.text
    assert "Could not load cellml model:" in caplog.text


def test_script_load_non_existing_file(caplog):
    """Check non-existing metadata tags are ignored"""
    LOGGER.info('Testing loading a file that does not exist\n')
    model_file = "bla.txt"
    # Call commandline script
    testargs = ['chaste_codegen', model_file]

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    print(caplog.text)
    assert 'ERROR' in caplog.text
    assert "Could not find cellml file bla.txt" in caplog.text


def test_range_and_capacitance_units(caplog, tmp_path):
    """Test range"""
    LOGGER.info('Testing range specs and capacitance incompatible units warning\n')
    tmp_path = str(tmp_path)
    model_name = 'test_luo_rudy_1991_with_range_cap_dimensionless'
    model_file = os.path.join(CELLML_FOLDER, '..', '..', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'test_luo_rudy_1991_with_range_cap_dimensionless.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '--opt', '-o', outfile]

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()

    # check capacitance units warning
    assert 'WARNING' in caplog.text
    assert "luo_rudy_1991 The model has capacitance in incompatible units." in caplog.text

    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Opt')
    compare_file_against_reference(os.path.join(reference, 'test_luo_rudy_1991_with_range_cap_dimensionless.hpp'),
                                   os.path.join(tmp_path, 'test_luo_rudy_1991_with_range_cap_dimensionless.hpp'))
    compare_file_against_reference(os.path.join(reference, 'test_luo_rudy_1991_with_range_cap_dimensionless.cpp'),
                                   os.path.join(tmp_path, 'test_luo_rudy_1991_with_range_cap_dimensionless.cpp'))


def test_piecewise_handling(caplog, tmp_path):
    """Test piecewise handling"""
    LOGGER.info('Testing piecewise handling\n')
    tmp_path = str(tmp_path)
    model_name = 'test_piecewises_be'
    model_file = os.path.join(CELLML_FOLDER, '..', '..', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'test_piecewises_be.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '--backward-euler', '-o', outfile]

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()

    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'BE')
    compare_file_against_reference(os.path.join(reference, 'test_piecewises_be.hpp'),
                                   os.path.join(tmp_path, 'test_piecewises_be.hpp'))
    compare_file_against_reference(os.path.join(reference, 'test_piecewises_be.cpp'),
                                   os.path.join(tmp_path, 'test_piecewises_be.cpp'))


def test_V_not_state_derived_quant(caplog, tmp_path):
    """Test V derived quant"""
    LOGGER.info('Testing V as derived quantity\n')
    tmp_path = str(tmp_path)
    model_name = 'test_V_not_state_derived_quant'
    model_file = os.path.join(CELLML_FOLDER, '..', '..', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'test_V_not_state_derived_quant.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-o', outfile]

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()

    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Normal')
    compare_file_against_reference(os.path.join(reference, 'test_V_not_state_derived_quant.hpp'),
                                   os.path.join(tmp_path, 'test_V_not_state_derived_quant.hpp'))
    compare_file_against_reference(os.path.join(reference, 'test_V_not_state_derived_quant.cpp'),
                                   os.path.join(tmp_path, 'test_V_not_state_derived_quant.cpp'))


def test_V_not_state_mparam(caplog, tmp_path):
    """Test V parameter"""
    LOGGER.info('Testing V as parameter\n')
    tmp_path = str(tmp_path)
    model_name = 'test_V_not_state_mparam'
    model_file = os.path.join(CELLML_FOLDER, '..', '..', model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'test_V_not_state_mparam.cpp')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '-o', outfile]

    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()

    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'Normal')
    compare_file_against_reference(os.path.join(reference, 'test_V_not_state_mparam.hpp'),
                                   os.path.join(tmp_path, 'test_V_not_state_mparam.hpp'))
    compare_file_against_reference(os.path.join(reference, 'test_V_not_state_mparam.cpp'),
                                   os.path.join(tmp_path, 'test_V_not_state_mparam.cpp'))


def test_script_RL_labview(tmp_path):
    """Convert a RushLarsen model type in labview output"""
    LOGGER.info('Testing model with options --rush-larsen-labview\n')
    tmp_path = str(tmp_path)
    model_name = 'aslanidi_Purkinje_model_2009'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'aslanidi_atrial_model_2009.txt')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '--rush-larsen-labview', '-o', outfile]
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'RL_labview')
    compare_file_against_reference(os.path.join(reference, 'aslanidi_atrial_model_2009.txt'),
                                   os.path.join(tmp_path, 'aslanidi_atrial_model_2009.txt'))


def test_script_RL_C(tmp_path):
    """Convert a RushLarsen model type in labview output"""
    LOGGER.info('Testing model with options --rush-larsen-C\n')
    tmp_path = str(tmp_path)
    model_name = 'aslanidi_Purkinje_model_2009'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    outfile = os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009.c')
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '--rush-larsen-c', '-o', outfile]
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    # Check output
    reference = os.path.join(os.path.join(TESTS_FOLDER), 'chaste_reference_models', 'RL_C')
    compare_file_against_reference(os.path.join(reference, 'aslanidi_Purkinje_model_2009.h'),
                                   os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009.h'))
    compare_file_against_reference(os.path.join(reference, 'aslanidi_Purkinje_model_2009.c'),
                                   os.path.join(tmp_path, 'aslanidi_Purkinje_model_2009.c'))


def test_script_RL_labview_double_type(caplog):
    """Check error message"""
    LOGGER.info('Testing model with options --rush-larsen-labview and --opt\n')
    model_name = 'aslanidi_Purkinje_model_2009'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '--rush-larsen-labview', '--cvode']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "--rush-larsen-labview and --rush-larsen-c cannot be used in combination with other model convertion types" \
        in caplog.text


def test_script_RL_C_double_type(caplog):
    """Check error message"""
    LOGGER.info('Testing model with options --rush-larsen-C and --opt\n')
    model_name = 'aslanidi_Purkinje_model_2009'
    model_file = os.path.join(CELLML_FOLDER, model_name + '.cellml')
    assert os.path.isfile(model_file)
    # Call commandline script
    testargs = ['chaste_codegen', model_file, '--rush-larsen-c', '--cvode']
    with mock.patch.object(sys, 'argv', testargs):
        chaste_codegen()
    assert 'ERROR' in caplog.text
    assert "--rush-larsen-labview and --rush-larsen-c cannot be used in combination with other model convertion types" \
        in caplog.text
