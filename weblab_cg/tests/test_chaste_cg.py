#
# Tests the basics of weblab_cg
#
import cellmlmanip
import logging
import os
import re
import weblab_cg as cg
import pytest
import sympy

#TODO: 
# deal with stimulus current in wrong name
# model -
# model conversion vars
# see generator

# Show more logging output
logging.getLogger().setLevel(logging.DEBUG)

COMMENTS_REGEX = re.compile(r'(//.*\n)')
NUM_REGEX = re.compile(r'[-+]?[\d]+\.?[\d]*[Ee](?:[-+]?[\d]+)?|\d+\.\d+')
DIGITS_REGEX = re.compile(r'\d+\.\d+')
FLOAT_PRECISION = 15


@pytest.fixture(scope="module")
def chaste_models():
    models = []
    # Get folder with test cellml files
    model_folder = os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'cellml')

    # Walk through all cellml files in the folder
    for root, dirs, files in os.walk(model_folder):
        for model_file in files:
            if '.cellml' in model_file:  # make sure we only process .cellml files
                model_name_from_file = model_file.replace('.cellml', '')
                class_name = 'Dynamic' + model_name_from_file
                model_file = os.path.join(model_folder, model_file)
                # Load cellml model and add it to the list of models
                models.append({'model': cellmlmanip.load_model(model_file),
                               'model_name_from_file': model_name_from_file,
                               'class_name': class_name})
    return models

def test_generate_normal_models(tmp_path, chaste_models):
    for model in chaste_models:
        chaste_model = cg.NormalChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
        chaste_model.write_chaste_code(tmp_path)

        _check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'Normal')
        _check_match_gengerated_chaste_cpp(tmp_path, model['model_name_from_file'], 'Normal')


@pytest.mark.skip(reason="Opt models not yet implemented")
def test_generate_opt_models(tmp_path, chaste_generators):
    for model in chaste_models:
        chaste_model = cg.OptChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
        chaste_model.write_chaste_code(tmp_path)

        _check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'Opt')
       
        #_check_match_gengerated_chaste_cpp()

@pytest.mark.skip(reason="Analytic_j models not yet implemented")
def test_generate_cvode_analytic_j_models(temp_folder, chaste_generators):
    for model in chaste_models:
        chaste_model = cg.Analytic_jChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
        chaste_model.write_chaste_code(tmp_path)

        _check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'Analytic_j')
       
        #_check_match_gengerated_chaste_cpp()

@pytest.mark.skip(reason="Numerical_j models not yet implemented")
def test_generate_cvode_numerical_j_models(temp_folder, chaste_generators):
    for model in chaste_models:
        chaste_model = cg.Numerical_jChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
        chaste_model.write_chaste_code(tmp_path)

        _check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'Numerical_j')
       
        #_check_match_gengerated_chaste_cpp()

@pytest.mark.skip(reason="BE models not yet implemented")
def test_generate_be_models(temp_folder, chaste_generators):
    for model in chaste_models:
        chaste_model = cg.BEChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
        chaste_model.write_chaste_code(tmp_path)

        _check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'BE')
       
        #_check_match_gengerated_chaste_cpp()

def _check_match_gengerated_chaste_hpp(gen_path, model_name_from_file, model_type):
    """
    Returns whether the generated and reference models are the same

    Arguments

    ``gen_path``
        The path to store the generated model code at. (Just the path, excluding the file name as file name)
    ``class_name``
        Class name for the generated model.
    """
    expected_hpp = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models',
                     model_type, model_name_from_file + '.hpp')

    # Check reference model exists
    assert os.path.isfile(expected_hpp)
    # Read expected output hpp from file
    with open(expected_hpp, 'r') as f:
        expected_hpp = f.read()
        # Ignore comments
        expected_hpp = COMMENTS_REGEX.sub("", expected_hpp)
        f.close()

    # Read generated output hpp from file
    generated_hpp = os.path.join(gen_path, model_name_from_file + '.hpp')
    with open(generated_hpp, 'r') as f:
        generated_hpp = f.read()
        # Ignore comments
        generated_hpp = COMMENTS_REGEX.sub("", generated_hpp)
        f.close()

    # Now they should match
    assert generated_hpp == expected_hpp

def _get_file_lines(file_path):
    # Check file exists
    assert os.path.isfile(file_path)
    lines = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            line = COMMENTS_REGEX.sub("", line)  # Ignore comments
            line = line.rstrip()  # Remove traling whitespace
            lines.append(line)
        f.close() 
    return lines       

def _numbers_with_float_precision(line):
    def format_numbers(m):
        pattern = "{0:." + str(FLOAT_PRECISION) + "f}"
        return str(float(pattern.format(float(m.group(0)))))

    #pow->Pow ceil -> ceiling
    line = line.replace("Pow(", 'Pow(').replace("ceil(", 'ceiling(')
    line = DIGITS_REGEX.sub(format_numbers, line)
    return line

def _same_with_number(line1, line2):
    if line1 == line2:
        return True

    line1 = _numbers_with_float_precision(line1)
    line1 = _numbers_with_float_precision(line1)

    # Get numbers out (both digits and scientific notation)
    num1 = NUM_REGEX.findall(line1)
    num2 = NUM_REGEX.findall(line2)

    # Remove numbers from lines to check if th text is the same
    # The escape ascii character is inserted to check placing of number is the same
    line1 = NUM_REGEX.sub(chr(27), line1)
    line2 = NUM_REGEX.sub(chr(27), line2)
    # Check lines are teh same without the numbers
    if line1 == line2:
        #check numbers are the same using sympy
        if len(num1) == len(num2):
            for i in range(len(num1)):
                num1 = _numbers_with_float_precision(num1)
                num2 = _numbers_with_float_precision(num1)
                if sympy.sympify(num1[i]) == sympy.sympify(num2[i]):
                    return False
            return True
    return False

def _get_equation_list(model_lines, index):
    equations = []
    eq = model_lines[index].replace(';','').strip().split("=", 1)
    while len(eq) ==2:
        eq[0] = eq[0].strip()
        eq[1] = sympy.simplify(eq[1])
        eq[1] = _numbers_with_float_precision(str(eq[1]))
        eq[1] = sympy.sympify(eq[1])
        equations.append(eq)
        index += 1
        eq = model_lines[index].replace(';','').strip().split("=", 1)
    assert len(equations) > 0
    return index, equations

def _get_var_name(c_dec):
    return c_dec.replace('const', '').replace('double','').strip()

def _is_deriv_decl(c_dec):
    return _get_var_name(c_dec).startswith('d_dt_chaste_interface__')

def _is_converter(c_dec):
    return _get_var_name(c_dec).endswith('_converter')    

def _perform_eq_subs(eq, subs_dict):
    # keep var_chaste_interface__i_ionic as it's hardcoded in
    if eq[0] == 'const double var_chaste_interface__i_ionic':
        return eq[1]
    else:
        return eq[1].subs(subs_dict)

def _check_equation_list(expected, generated):
    link_subs = dict()

    # Resolve derivatives
    remove = []
    for i in reversed(range(len(expected))):
        if _is_deriv_decl(expected[i][0]):
            if isinstance(expected[i][1], sympy.symbol.Symbol):
                # See if there is any linkers
                for j in reversed(range(len(expected))):
                    if _get_var_name(expected[j][0]) == str(expected[i][1]):
                        expected[i][1] = expected[j][1]
                        remove.append(expected[j])


    # Resolve converter variables first
    converter_vars =  [eq for eq in expected if (_is_converter(eq[0]) or isinstance(eq[1], sympy.symbol.Symbol)) and not _is_deriv_decl(eq[0])]
    exclude = []
    for converter in reversed(converter_vars):
        # If rhs is symobol, see if there is an equation we can subs in
        if isinstance(converter[1], sympy.symbol.Symbol):
            for i in reversed(range(len(expected))):
                if str(converter[1]) == _get_var_name(expected[i][0]):
                    converter[1] = expected[i][1]
                    if _is_converter(converter[0]):
                        exclude.append(expected[i])
                    break
        var_name = _get_var_name(converter[0])
        link_subs[var_name] = converter[1]

    # Perform substitutions
    expected = [[eq[0], _perform_eq_subs(eq, link_subs)] for eq in expected if not eq in converter_vars+exclude]

    # Remove linkiners for derivatives
    expected = [x for x in expected if x[0] not in [y[0] for y in remove]]
  
    # The 2 sets of equations have the same left hand sides
    assert len(expected) == len(generated)
    assert set([eq[0] for eq in expected]) == set([eq[0] for eq in generated])

    # for all eq in eqs1 find in eq2 and check they are equal
    for eq_comp in [(x[1],y[1]) for x in generated for y in expected if x[0]==y[0]]:
        exp =  _numbers_with_float_precision(str(eq_comp[1]))
        gen = _numbers_with_float_precision(str(eq_comp[1]))
        assert exp == gen
    
    # Check the order for generated: lhs doesn't apear in earlier rhs (could give c++ compile error)
    for i in range (len(generated)-1,-1,-1):
        #check the equation doesn't appear on rhs beforehand
        var = _get_var_name(generated[i][0])
        for j in range (i-1,-1,-1):
            assert isinstance(generated[j][1], sympy.numbers.Float) or not var in [str(x) for x in generated[j][1].free_symbols]

def _check_match_gengerated_chaste_cpp(gen_path, model_name_from_file, model_type):
    expected_cpp_file = \
        os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models',
                     model_type, model_name_from_file + '.cpp')
    generated_cpp_file = os.path.join(gen_path, model_name_from_file + '.cpp')

    expected_cpp = _get_file_lines(expected_cpp_file)
    generated_cpp = _get_file_lines(generated_cpp_file)

    expected_i = generated_i = 0
    while expected_i < len(expected_cpp) and generated_i < len(generated_cpp):
        #If lines are the same (ignore indtation)
        expected_line = expected_cpp[expected_i].strip()
        generated_line = generated_cpp[generated_i].strip()
        if _same_with_number(expected_line, generated_line):
            expected_i += 1
            generated_i += 1
        else:
            # We must be in an equation block (or the model is wrong)
            expected_i, expected_eq = _get_equation_list(expected_cpp, expected_i)
            generated_i, generated_eq = _get_equation_list(generated_cpp, generated_i)

            # Check the equations are the same
            _check_equation_list(expected_eq, generated_eq)
    # Must have reached end of both files
    assert expected_i == len(expected_cpp) and generated_i == len(generated_cpp)
