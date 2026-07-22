import glob
import os
import re

import pytest
import sympy

from chaste_codegen import DATA_DIR, load_model_with_conversions
from chaste_codegen._script_utils import write_file


CELLML_FOLDER = os.path.join(DATA_DIR, 'tests', 'cellml', 'cellml')
TESTS_FOLDER = os.path.join(DATA_DIR, 'tests')

TIMESTAMP_REGEX = re.compile(r'(//! on .*)')
COMMENTS_REGEX = re.compile(r'(//.*)')
VERSION_REGEX = re.compile(r'(//! This source file was generated from CellML by chaste_codegen version .*)')

cached_models = {}


def cache_model(model_name):
    """ Load a model, caching it so repeated requests return the same instance.

    :param model_name: path to the cellml model file
    :return: the loaded model
    """
    return cached_models.setdefault(model_name, load_model_with_conversions(model_name))


@pytest.fixture(scope='session')
def s_model():
    return cache_model(os.path.join(CELLML_FOLDER, 'shannon_wang_puglisi_weber_bers_2004.cellml'))


@pytest.fixture(scope='session')
def be_model():
    return cache_model(os.path.join(CELLML_FOLDER, 'beeler_reuter_model_1977.cellml'))


@pytest.fixture(scope='session')
def hh_model():
    model_name = os.path.join(CELLML_FOLDER, 'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
    return cache_model(model_name)


@pytest.fixture(scope='session')
def fr_model():
    model_name = os.path.join(CELLML_FOLDER, 'faber_rudy_2000.cellml')
    return cache_model(model_name)


@pytest.fixture(scope='session')
def n_model():
    model_name = os.path.join(CELLML_FOLDER, 'noble_model_1962.cellml')
    return cache_model(model_name)


def load_chaste_models(model_types=[], reference_folder='chaste_reference_models'):
    """ Load all models that have reference Chaste code for the given model types.

    :param model_types: the model types to load
    :param reference_folder: directory holding the reference Chaste code
    :return: a list of ``{'model_type', 'model', 'model_name_from_file'}`` dicts
    """
    # Walk through all cellml files in the folder
    model_files = []
    for root, dirs, files in os.walk(CELLML_FOLDER):
        for model_file in files:
            if model_file.endswith('.cellml'):  # make sure we only process .cellml files
                model_name_from_file = model_file.replace('.cellml', '')
                model_file = os.path.join(CELLML_FOLDER, model_file)
                for model_type in model_types:
                    expected_path = \
                        os.path.join(TESTS_FOLDER, reference_folder, model_type, model_name_from_file) + '.hpp'

                    # Skip cellml files without reference Chaste code
                    if os.path.isfile(expected_path):
                        model_files.append({'model_type': model_type,
                                            'model': model_file,
                                            'model_name_from_file': model_name_from_file})
    return model_files


def regenerate_reference(reference_file, content):
    """Regenerate ``reference_file`` from ``content`` if regeneration is enabled.

    When the ``CHASTE_CODEGEN_REGENERATE_REFERENCES`` environment variable is
    set, ``content`` is written to a sympy-version tagged reference file
    ``<reference>.regen.<major>.<minor>``.

    :param reference_file: path to the reference file to regenerate
    :param content: the generated content to write to the regen file
    :return: ``True`` if regeneration is enabled else ``False``
    """
    if not os.environ.get('CHASTE_CODEGEN_REGENERATE_REFERENCES'):
        return False
    version = '.'.join(sympy.__version__.split('.')[:2])
    with open(reference_file + '.regen.' + version, 'w') as out:
        out.write(content)
    return True


def get_reference_candidates(reference_file):
    """Return the base reference file plus any variant ``--<label>`` files.

    Different dependency versions can format the generated code differently
    (usually dependent on sympy version, sometimes Python version). Each alternative
    acceptable output is stored in a variant file with a ``--<label>`` suffix
    inserted before the extension, e.g. ``foo.cpp`` -> ``foo--sympy_1_11.cpp``.
    The generated output is accepted if it matches the base file or *any* variant.

    :param reference_file: path to the base reference file
    :return: a list of the base ``reference_file`` followed by sorted variants
    """
    root, ext = os.path.splitext(reference_file)
    return [reference_file] + sorted(glob.glob(glob.escape(root) + '--*' + glob.escape(ext)))


def get_file_string(file_path):
    """ Load a file into a single string, dropping a single trailing newline.

    :param file_path: path to the file
    :return: the file contents as a string
    """
    with open(file_path, 'r') as f:
        content = f.read()
    # Drop a trailing newline to avoid spurious diffs in string comparisons.
    return content[:-1] if content.endswith('\n') else content


def get_file_lines(file_path, remove_comments=False):
    """ Load a file into a normalised list of lines

    Strips surrounding whitespace, removes the timestamp/version header lines
    and (optionally) comments, and drops blank lines.

    :param file_path: path to the file
    :param remove_comments: whether to remove all comments  starting with //
    :return: the normalised, non-empty lines of the file
    """
    # Check file exists
    assert os.path.isfile(file_path)
    lines = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            line = line.rstrip().lstrip()  # Remove trailing and preceding whitespace
            line = TIMESTAMP_REGEX.sub("", line)  # Remove timestamp
            line = VERSION_REGEX.sub("", line)  # Remove Version
            if remove_comments:
                line = COMMENTS_REGEX.sub("", line)  # Remove comments
            if line != '':  # Skip empty lines
                lines.append(line)
    return lines


def compare_model_against_reference(chaste_model, tmp_path, model_type, reference_folder='chaste_reference_models'):
    """ Check a model's generated files against its reference files.

    Writes each generated file into ``tmp_path`` and compares it against the
    corresponding reference (see :func:`compare_file_against_reference`).

    :param chaste_model: the generated Chaste model to check
    :param tmp_path: temporary folder for generated files
    :param model_type: the model type
    :param reference_folder: directory holding the reference Chaste code
    """
    tmp_path = str(tmp_path)
    expected_path = os.path.join(TESTS_FOLDER, reference_folder, model_type, chaste_model.file_name)
    # Write generated files
    # Compare against reference
    assert len(chaste_model.generated_code) == len(chaste_model.generated_code) == len(chaste_model.DEFAULT_EXTENSIONS)
    assert len(chaste_model.generated_code) > 0
    for ext, code in zip(chaste_model.DEFAULT_EXTENSIONS, chaste_model.generated_code):
        gen_file_path = os.path.join(tmp_path, chaste_model.file_name + ext)
        write_file(gen_file_path, code)
        compare_file_against_reference(expected_path + ext, gen_file_path)


def compare_string_against_reference(reference_file, actual):
    """ Check an actual string against its reference(s).

    The generated string is accepted if it matches the base reference file or
    *any* variant (see :func:`get_reference_candidates`).

    :param reference_file: path to the base reference file
    :param actual: the generated string to check
    """
    # Write to file if regeneration is enabled
    if regenerate_reference(reference_file, actual):
        return

    # Compare against reference
    if any(actual == get_file_string(candidate) for candidate in get_reference_candidates(reference_file)):
        return
    assert actual == get_file_string(reference_file), reference_file


def compare_file_against_reference(reference_file, file):
    """ Check a generated file against its reference(s).

    The generated file is accepted if it matches the base reference file or
    *any* sibling variant (see :func:`get_reference_candidates`).

    :param reference_file: path to the base reference file
    :param file: path to the generated file to check
    """
    # Write to file if regeneration is enabled
    with open(file, 'r') as gen:
        if regenerate_reference(reference_file, gen.read()):
            return

    # Compare against reference
    actual = get_file_lines(file)
    if any(actual == get_file_lines(candidate) for candidate in get_reference_candidates(reference_file)):
        return
    assert actual == get_file_lines(reference_file), reference_file
