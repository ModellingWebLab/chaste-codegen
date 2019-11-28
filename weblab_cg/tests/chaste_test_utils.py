import os
import re
import weblab_cg as cg
import cellmlmanip

TIMESTAMP_REGEX = re.compile(r'(//! on .*)')
COMMENTS_REGEX = re.compile(r'(//.*)')


def load_chaste_models(model_types=[], ref_path_prefix=['chaste_reference_models'], class_name_prefix='Cell'):
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
                reference_models = {}
                for model_type in model_types:
                    expected_hpp_path = os.path.join(cg.DATA_DIR, 'tests')
                    expected_cpp_path = os.path.join(cg.DATA_DIR, 'tests')
                    for pref in ref_path_prefix:
                        expected_hpp_path = os.path.join(expected_hpp_path, pref)
                        expected_cpp_path = os.path.join(expected_cpp_path, pref)
                    expected_hpp_path = os.path.join(expected_hpp_path, model_type, model_name_from_file + '.hpp')
                    expected_cpp_path = os.path.join(expected_cpp_path, model_type, model_name_from_file + '.cpp')

                    # Skip cellml files without reference chaste code
                    if os.path.isfile(expected_hpp_path) and os.path.isfile(expected_cpp_path):
                        reference_models.update({model_type: {'expected_hpp_path': expected_hpp_path,
                                                'expected_cpp_path': expected_cpp_path}})

                if len(reference_models) > 0:
                    class_name = class_name_prefix + model_name_from_file
                    model_files.append({'model': cellmlmanip.load_model(model_file),
                                        'model_name_from_file': model_name_from_file,
                                        'class_name': class_name + 'FromCellML',
                                        'reference_models': reference_models})
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


def write_file(file_name, file_contents):
    """ Write a file into the given file name

    :param file_name: file name including path
    :param file_contents: a str with the contents of the file to be written
    """
    # Make sure the folder we are writing in exists
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # Write the file
    file = open(file_name, 'w')
    file.write(file_contents)
    file.close()
