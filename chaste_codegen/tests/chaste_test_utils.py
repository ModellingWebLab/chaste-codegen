import os
import re

import chaste_codegen as cg
from chaste_codegen._script_utils import write_file


TIMESTAMP_REGEX = re.compile(r'(//! on .*)')
COMMENTS_REGEX = re.compile(r'(//.*)')
VERSION_REGEX = re.compile(r'(//! This source file was generated from CellML by chaste_codegen version .*)')


def load_chaste_models(model_types=[], reference_folder='chaste_reference_models'):
    """ Load all models"""
    # Get folder with test cellml files
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'cellml')

    # Walk through all cellml files in the folder
    model_files = []
    for root, dirs, files in os.walk(model_folder):
        for model_file in files:
            if model_file.endswith('.cellml'):  # make sure we only process .cellml files
                model_name_from_file = model_file.replace('.cellml', '')
                model_file = os.path.join(model_folder, model_file)
                for model_type in model_types:
                    expected_hpp_path = os.path.join(cg.DATA_DIR, 'tests', reference_folder)
                    expected_cpp_path = os.path.join(cg.DATA_DIR, 'tests', reference_folder)

                    expected_hpp_path = os.path.join(expected_hpp_path, model_type, model_name_from_file + '.hpp')
                    expected_cpp_path = os.path.join(expected_cpp_path, model_type, model_name_from_file + '.cpp')

                    # Skip cellml files without reference chaste code
                    if os.path.isfile(expected_hpp_path) and os.path.isfile(expected_cpp_path):
                        model_files.append({'model_type': model_type,
                                            'expected_hpp_path': expected_hpp_path,
                                            'expected_cpp_path': expected_cpp_path,
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


def compare_model_against_reference(chaste_model, tmp_path, expected_hpp_path, expected_cpp_path):
    """ Check a model's generated files against given reference files
    """
    tmp_path = str(tmp_path)
    # Compare against reference
    # Write generated files
    hhp_gen_file_path = os.path.join(tmp_path, chaste_model.file_name + ".hpp")
    cpp_gen_file_path = os.path.join(tmp_path, chaste_model.file_name + ".cpp")
    write_file(hhp_gen_file_path, chaste_model.generated_hpp)
    write_file(cpp_gen_file_path, chaste_model.generated_cpp)

    # Compare converted files vs reference
    compare_file_against_reference(hhp_gen_file_path, expected_hpp_path)
    compare_file_against_reference(cpp_gen_file_path, expected_cpp_path)


def compare_file_against_reference(file, reference):
    """ Check a model's generated files against given reference files
    """
    # Load reference file
    file = get_file_lines(file)
    reference = get_file_lines(reference)
    assert file == reference
