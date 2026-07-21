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


def reference_candidates(reference_file):
    """Return the base reference file plus any sibling ``--<label>`` variant files.

    Different dependency versions can format the generated code differently (e.g. the ordering of
    summed terms on Python 3.10 vs 3.11+, or sympy 1.14's float handling). Each alternative
    acceptable output is stored in a sibling file with a ``--<label>`` suffix inserted before the
    extension, e.g. ``foo.cpp`` -> ``foo--python_3_11.cpp``. The generated output is accepted if it
    matches the base file or *any* variant, so the tests need not know which version produced which
    file. The ``<label>`` is purely descriptive and is not parsed.
    """
    root, ext = os.path.splitext(reference_file)
    return [reference_file] + sorted(glob.glob(glob.escape(root) + '--*' + glob.escape(ext)))


def _read_reference(reference_file):
    """Read a reference file, dropping a single trailing newline."""
    with open(reference_file, 'r') as f:
        content = f.read()
    return content[:-1] if content.endswith('\n') else content


def compare_string_against_reference(actual, reference_file):
    """ Check an actual string against its reference(s).

    The generated string is accepted if it matches the base reference file or *any* sibling
    ``--<label>`` variant (see :func:`reference_candidates`). Setting the
    ``CHASTE_CODEGEN_REGENERATE_REFERENCES`` environment variable writes the actual string to a
    ``<reference>.regen.<major>.<minor>`` file instead of asserting, for later use.
    """
    if os.environ.get('CHASTE_CODEGEN_REGENERATE_REFERENCES'):
        version = '.'.join(sympy.__version__.split('.')[:2])
        with open(reference_file + '.regen.' + version, 'w') as out:
            out.write(actual)
        return
    if any(actual == _read_reference(candidate) for candidate in reference_candidates(reference_file)):
        return
    assert actual == _read_reference(reference_file), reference_file


cached_models = {}


def cache_model(model_name):
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
    """ Load all models"""

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

                    # Skip cellml files without reference chaste code
                    if os.path.isfile(expected_path):
                        model_files.append({'model_type': model_type,
                                            'model': model_file,
                                            'model_name_from_file': model_name_from_file})
    return model_files


def normalise_lines(raw_lines, remove_comments=False):
    """ Normalise raw text lines for comparison

    Strips surrounding whitespace, removes the timestamp/version header lines
    and (optionally) comments, and drops blank lines.

    :param raw_lines: an iterable of raw lines (e.g. from ``file.readlines()``)
    :param remove_comments: indicates whether to remove all comments starting with //
    """
    lines = []
    for line in raw_lines:
        line = line.rstrip().lstrip()  # Remove trailing and preceding whitespace
        line = TIMESTAMP_REGEX.sub("", line)  # Remove timestamp
        line = VERSION_REGEX.sub("", line)  # Remove Version
        if remove_comments:
            line = COMMENTS_REGEX.sub("", line)  # Remove comments
        if line != '':  # Skip empty lines
            lines.append(line)
    return lines


def get_file_lines(file_name, remove_comments=False):
    """ Load a file into a normalised list of lines

    :param file_name: file name including path
    :param remove_comments: indicates whether to remove all comments  starting with //
    """
    # Check file exists
    assert os.path.isfile(file_name)
    with open(file_name, 'r') as f:
        return normalise_lines(f.readlines(), remove_comments)


def compare_model_against_reference(chaste_model, tmp_path, model_type, reference_folder='chaste_reference_models'):
    """ Check a model's generated files against given reference files
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


def compare_file_against_reference(reference_file, file):
    """ Check a generated file against its reference(s).

    The generated file is accepted if it matches the base reference file or *any* sibling
    ``--<label>`` variant (see :func:`reference_candidates`). Setting the
    ``CHASTE_CODEGEN_REGENERATE_REFERENCES`` environment variable dumps the generated output to a
    ``<reference>.regen.<major>.<minor>`` file instead of asserting, for later use.
    """
    if os.environ.get('CHASTE_CODEGEN_REGENERATE_REFERENCES'):
        version = '.'.join(sympy.__version__.split('.')[:2])
        with open(file, 'r') as gen, open(reference_file + '.regen.' + version, 'w') as out:
            out.write(gen.read())
        return
    actual = get_file_lines(file)
    if any(actual == get_file_lines(candidate) for candidate in reference_candidates(reference_file)):
        return
    assert actual == get_file_lines(reference_file), reference_file
