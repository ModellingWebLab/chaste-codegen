import os
import re
import weblab_cg as cg
import cellmlmanip

TIMESTAMP_REGEX = re.compile(r'(//! on .*)')
COMMENTS_REGEX = re.compile(r'(//.*)')


def load_chaste_models(model_types=[], reference_path_prefix=['chaste_reference_models']):
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
                    for pref in reference_path_prefix:
                        expected_hpp_path = os.path.join(expected_hpp_path, pref)
                        expected_cpp_path = os.path.join(expected_cpp_path, pref)
                    expected_hpp_path = os.path.join(expected_hpp_path, model_type, model_name_from_file + '.hpp')
                    expected_cpp_path = os.path.join(expected_cpp_path, model_type, model_name_from_file + '.cpp')

                    # Skip cellml files without reference chaste code
                    if os.path.isfile(expected_hpp_path) and os.path.isfile(expected_cpp_path):
                        reference_models.update({model_type: {'expected_hpp_path': expected_hpp_path,
                                                'expected_cpp_path': expected_cpp_path}})

                if len(reference_models) > 0:
                    class_name = 'Dynamic' + model_name_from_file
                    model_files.append({'model': cellmlmanip.load_model(model_file),
                                        'model_name_from_file': model_name_from_file,
                                        'class_name': class_name,
                                        'reference_models': reference_models})
    return model_files

def get_file_lines(file_path, ignore_comments=False):
    # Check file exists
    assert os.path.isfile(file_path)
    lines = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            line = line.rstrip().lstrip()  # Remove trailing and preceding whitespace
            line = TIMESTAMP_REGEX.sub("", line)  # Ignore timestamp
            if ignore_comments:
                line = COMMENTS_REGEX.sub("", line)  # Ignore comments
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

def write_file(file_path, file_contents):
    make_dir( os.path.dirname(file_path))
    with open(file_path, 'w') as f:
        f.write(file_contents)
        f.close()

def make_dir(output_path):
    # Get full OS path to output models to and create it if it doesn't exist
    output_path = os.path.join(str(output_path))
    try:
        os.makedirs(output_path)
    except FileExistsError:
        pass
