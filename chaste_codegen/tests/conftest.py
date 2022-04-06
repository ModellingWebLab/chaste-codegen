import os
import re

import pytest

from chaste_codegen import DATA_DIR, load_model_with_conversions
from chaste_codegen._script_utils import write_file


CELLML_FOLDER = os.path.join(DATA_DIR, 'tests', 'cellml', 'cellml')
TESTS_FOLDER = os.path.join(DATA_DIR, 'tests')

TIMESTAMP_REGEX = re.compile(r'(//! on .*)')
COMMENTS_REGEX = re.compile(r'(//.*)')
VERSION_REGEX = re.compile(r'(//! This source file was generated from CellML by chaste_codegen version .*)')

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


def get_file_lines(file_name, remove_comments=False):
    """ Load a file into a list of lines

    :param file_name: file name including path
    :param remove_comments: indicates whether to remove all comments  starting with //
    """
    # Check file exists
    assert os.path.isfile(file_name)
    lines = []
    with open(file_name, 'r') as f:
        for line in f.readlines():
            line = line.rstrip().lstrip()  # Remove trailing and preceding whitespace
            line = TIMESTAMP_REGEX.sub("", line)  # Remove timestamp
            line = VERSION_REGEX.sub("", line)  # Remove Version
            if remove_comments:
                line = COMMENTS_REGEX.sub("", line)  # Remove comments
            lines.append(line)
        f.close()

    # Remove empty lines
    i = 0
    while i < len(lines):
        if lines[i] == '':
            del lines[i]
        else:
            i += 1

    return lines


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
    """ Check a model's generated files against given reference files
    """
    # Load reference file
    file = get_file_lines(file)
    reference = get_file_lines(reference_file)
    alt_reference = reference_file + '_alt'
    if file != reference and os.path.exists(alt_reference):
        reference = get_file_lines(alt_reference)
    assert file == reference, str(alt_reference)
