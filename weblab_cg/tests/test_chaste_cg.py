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
from sympy import SympifyError, Eq
import pyparsing

# Show more logging output
logging.getLogger().setLevel(logging.DEBUG)

class TestChasteCG(object):
    _COMMENTS_REGEX = re.compile(r'(//.*\n)')
    _NUM_REGEX = re.compile(r'[-+]?[\d]+\.?[\d]*[Ee](?:[-+]?[\d]+)?|\d+\.\d+')
    _DIGITS_REGEX = re.compile(r'\d+\.\d+')
    _FLOAT_PRECISION = 14


    @pytest.fixture(scope="class")
    def chaste_models(self):
        # Get folder with test cellml files
        model_folder = os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models', 'cellml')

        # Walk through all cellml files in the folder
        model_files = []
        for root, dirs, files in os.walk(model_folder):
            for model_file in files:
                if model_file.endswith('.cellml'):  # make sure we only process .cellml files
                    model_name_from_file = model_file.replace('.cellml', '')
                    model_file = os.path.join(model_folder, model_file)
                    class_name = 'Dynamic' + model_name_from_file
                    model_files.append({'model': cellmlmanip.load_model(model_file),
                                        'model_name_from_file': model_name_from_file,
                                        'class_name': class_name})
        return model_files

    def test_generate_normal_models(self, tmp_path, chaste_models):
        for model in chaste_models:
            chaste_model = cg.NormalChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
            chaste_model.write_chaste_code(tmp_path)

            self._check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'Normal')
            self._check_match_gengerated_chaste_cpp(tmp_path, model['model_name_from_file'], 'Normal')

    @pytest.mark.skip(reason="Opt models not yet implemented")
    def test_generate_opt_models(self, tmp_path, chaste_models):
        for model in chaste_models:
            chaste_model = cg.OptChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
            chaste_model.write_chaste_code(tmp_path)

            self._check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'Opt')
            self._check_match_gengerated_chaste_cpp(tmp_path, model['model_name_from_file'], 'Opt')

    @pytest.mark.skip(reason="Analytic_j models not yet implemented")
    def test_generate_cvode_analytic_j_models(self, tmp_path, chaste_models):
        for model in chaste_models:
            chaste_model = cg.Analytic_jChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
            chaste_model.write_chaste_code(tmp_path)

            self._check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'Analytic_j')
            self._check_match_gengerated_chaste_cpp(tmp_path, model['model_name_from_file'], 'Analytic_j')

    @pytest.mark.skip(reason="Numerical_j models not yet implemented")
    def test_generate_cvode_numerical_j_models(self, tmp_path, chaste_models):
        for model in chaste_models:
            chaste_model = cg.Numerical_jChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
            chaste_model.write_chaste_code(tmp_path)

            self._check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'Numerical_j')
            self._check_match_gengerated_chaste_cpp(tmp_path, model['model_name_from_file'], 'Numerical_j')

    @pytest.mark.skip(reason="BE models not yet implemented")
    def test_generate_be_models(self, tmp_path, chaste_models):
        for model in chaste_models:
            chaste_model = cg.BEChasteModel(model['model'], model['model_name_from_file'], model['class_name'])
            chaste_model.write_chaste_code(tmp_path)

            self._check_match_gengerated_chaste_hpp(tmp_path, model['model_name_from_file'], 'BE')
            self._check_match_gengerated_chaste_cpp(tmp_path, model['model_name_from_file'], 'BE')

    def _check_match_gengerated_chaste_hpp(self, gen_path, model_name_from_file, model_type):
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
        # Read expected output hpp from file
        with open(expected_hpp, 'r') as f:
            expected_hpp = f.read()
            # Ignore comments
            expected_hpp = self._COMMENTS_REGEX.sub("", expected_hpp)
            f.close()

        # Read generated output hpp from file
        generated_hpp = os.path.join(gen_path, model_name_from_file + '.hpp')
        with open(generated_hpp, 'r') as f:
            generated_hpp = f.read()
            # Ignore comments
            generated_hpp = self._COMMENTS_REGEX.sub("", generated_hpp)
            f.close()

        # Now they should match
        assert generated_hpp == expected_hpp

    def _get_file_lines(self, file_path):
        # Check file exists
        assert os.path.isfile(file_path)
        lines = []
        with open(file_path, 'r') as f:
            for line in f.readlines():
                line = self._COMMENTS_REGEX.sub("", line)  # Ignore comments
                line = line.rstrip().lstrip()  # Remove trailing and preceding whitespace
                lines.append(line)
            f.close()
        return lines

    def _numbers_with_float_precision(self, line):
        def format_numbers(m):
            pattern = "{0:." + str(self._FLOAT_PRECISION - 1) + "f}"
            return str(float(pattern.format(float(m.group(0)))))

        # pow->Pow ceil -> ceiling
        line = line.replace("Pow(", 'Pow(').replace("ceil(", 'ceiling(')
        line = self._DIGITS_REGEX.sub(format_numbers, line)
        return line

    def _same_with_number(self, line1, line2):
        # If they are the same, no need for elaborate check
        if line1 == line2:
            return True

        line1 = self._numbers_with_float_precision(line1)
        line2 = self._numbers_with_float_precision(line2)

        # Get numbers out (both digits and scientific notation)
        num1 = self._NUM_REGEX.findall(line1)
        num2 = self._NUM_REGEX.findall(line2)

        # Remove numbers from lines to check if th text is the same
        # The escape ascii character is inserted to check placing of number is the same
        line1 = self._NUM_REGEX.sub(chr(27), line1)
        line2 = self._NUM_REGEX.sub(chr(27), line2)
        # Check lines are teh same without the numbers
        if line1 == line2:
            # check numbers are the same using sympy
            if len(num1) == len(num2):
                for i in range(len(num1)):
                    if sympy.sympify(num1[i]) != sympy.sympify(num2[i]):
                        return False
                return True
        return False

    def _get_expression(self, expr_parts):
        # TODO:
        # process list
        # if element is list, recursively process list
        # if len(element> >= 5 : proess recursively
        # else if ? -> condition, ;-> expr, end -> expr
        # else (not ? :)-> add expr
        # if not conditional return expr
        # else: repeat: find last expr and resolve
        expression = ''
        conditional_parts = []
        if not isinstance(expr_parts, list) and not len(expr_parts) >=5:
            return expr_parts
        else:
            for part in expr_parts:
                if part == '==':
                    conditional_parts.append(('expression',expression))
                    conditional_parts.append(('==','=='))
                    expression = ''                
                elif part == '?':
                    conditional_parts.append(('expression',expression))
                    conditional_parts.append(('?','?'))
                    expression = ''
                elif part == ':':
                    conditional_parts.append(('expression',expression))
                    conditional_parts.append((':',':'))
                    expression = ''
                else:
                    expression+=self._get_expression(part)
            conditional_parts.append(('expression', expression))  # ends with expression

            # translate equals
            has_equals = True
            while has_equals:
                has_equals = False
                for i in range(len(conditional_parts)):
                    if conditional_parts[i][0] == '==':
                        has_equals = True
                        exp1 = conditional_parts[i-1][1]
                        exp2 = conditional_parts[i+1][1]
                        conditional_parts[i-1] = 'Eq('+exp1+', '+exp2+')'
                        del conditional_parts[i:i+2] 
                        break

            # translate conditionals
            while len(conditional_parts) > 1:
                #find last condition
               for i in range(len(conditional_parts)-1, -1, -1):
                    if conditional_parts[i][0] == '?' and conditional_parts[i+2][0] == ':':
                        #resolve nex 2 must be expressions as this was the last condition
                        cond = conditional_parts[i-1][1]
                        exp1 = conditional_parts[i+1][1]
                        exp2 = conditional_parts[i+3][1]
                        conditional_parts[i-1] = ('expression', exp1 + ' if ' + cond + ' else ' + exp2)
                        del conditional_parts[i:]
                        break
            expression_str = conditional_parts[0][1]
            if isinstance(expr_parts, list):
                expression_str = '(' + expression_str + ')'
        return expression_str

    def _to_equation(self, equation_str):
        # pow->Pow ceil -> ceiling in sympy
        equation_str = equation_str.replace("Pow(", 'Pow(').replace("ceil(", 'ceiling(')
        # This might be a C++ call with class members/pointer accessors?
        equation_str = equation_str.replace('()->', '_').replace('::', '_')
        equation_str = equation_str.replace('&&', '&').replace('||', '|')
        try:
            return sympy.simplify(equation_str)
        except SympifyError:
            expression = pyparsing.Word(pyparsing.printables, excludeChars="()")
            parens     = pyparsing.nestedExpr( '(', ')', content=expression)
            parenthesis_expr = parens.parseString('('+equation_str+')').asList()
            expr_str = self._get_expression(parenthesis_expr)
            return sympy.simplify(expr_str)

    def _get_equation_list(self, model_lines, index):          
        equations = []
        eq = model_lines[index].replace(';', '').split("=", 1)
        while len(eq) == 2:
            eq[0] = eq[0].rstrip().lstrip()  # Remove trailing and preceding whitespace
            eq[1] = eq[1].rstrip().lstrip()  # Remove trailing and preceding whitespace
            eq[1] = self._to_equation(eq[1])

            equations.append(eq)
            index += 1
            eq = model_lines[index].replace(';', '').split("=", 1)
        assert len(equations) > 0
        return index, equations

    def _get_var_name(self, c_dec):
        return c_dec.replace('const', '').replace('double', '').strip()

    def _is_deriv_decl(self, c_dec):
        return self._get_var_name(c_dec).startswith('d_dt_chaste_interface__') or  self._get_var_name(c_dec).endswith('dt')

    def _is_converter(self, c_dec):
        return self._get_var_name(c_dec).endswith('_converter')

    def _perform_eq_subs(self, eq, subs_dict):
        substituted_term = eq[1].subs(subs_dict)
        while substituted_term != eq[1]:
            eq[1] = substituted_term
            substituted_term = eq[1].subs(subs_dict)
        return [eq[0], eq[1]]

    def _is_same_equation(self, eq1, eq2):
        # If they are the same, no need for elaborate check
        if eq1 == eq2:
            return True

        eq1 = self._numbers_with_float_precision(str(eq1))
        eq1 = sympy.simplify(eq1)

        eq2 = self._numbers_with_float_precision(str(eq2))
        eq2 = sympy.simplify(eq2)

        if eq1 == eq2:
            return True

        if eq2 != 0.0:
            return sympy.simplify(eq1 / eq2) == 1.0
        else:
            return eq1-eq2 == 0.0

    def _resolve_linkers(self, equation_list, subs_dict):
        # Resolve derivatives
        remove = []
        for i in reversed(range(len(equation_list))):
            if self._is_deriv_decl(equation_list[i][0]):
                if isinstance(equation_list[i][1], sympy.symbol.Symbol):
                    # See if there are any linkers
                    for j in reversed(range(len(equation_list))):
                        if self._get_var_name(equation_list[j][0]) == str(equation_list[i][1]):
                            equation_list[i][1] = equation_list[j][1]
                            remove.append(equation_list[j])

        # Remove linkiners for derivatives
        equation_list = [x for x in equation_list if x[0] not in [y[0] for y in remove]]

        # Resolve converter / linker variables in remaining equations
        converter_vars = [eq for eq in equation_list
                          if (self._is_converter(eq[0]) or isinstance(eq[1], sympy.symbol.Symbol))
                          and not self._is_deriv_decl(eq[0])]

        exclude = []
        for converter in reversed(converter_vars):
            # If rhs is symobol, see if there is an equation we can subs in
            if isinstance(converter[1], sympy.symbol.Symbol):
                if self._is_converter(converter[0]):
                    for i in reversed(range(len(equation_list))):
                        if str(converter[1]) == self._get_var_name(equation_list[i][0]):
                            converter[1] = equation_list[i][1]
                            exclude.append(equation_list[i])
            var_name = self._get_var_name(converter[0])
            subs_dict[var_name] = converter[1]

        # Perform substitutions
        equation_list = [self._perform_eq_subs(eq, subs_dict)
                    for eq in equation_list if eq not in converter_vars + exclude]

        return equation_list, subs_dict

    def _check_equation_list(self, expected, generated):
        if not self._keep_subs:
            self.link_subs_expected = dict()
            self.link_subs_generated = dict()
        self._keep_subs = False

        # Resolve linkers and converter variables        
        expected, self.link_subs_expected = self._resolve_linkers(expected, self.link_subs_expected)
        generated, self.link_subs_generated = self._resolve_linkers(generated, self.link_subs_generated)

        # The 2 sets of equations have the same left hand sides
        assert len(expected) == len(generated)

        # only exception could be name of stimulus current
        if set([eq[0] for eq in expected]) != set([eq[0] for eq in generated]):
            # The last one in the list should be dV/dt
            # Check if it is a derivative
            assert self._is_deriv_decl(expected[-1][0])
            assert self._is_deriv_decl(generated[-1][0])

            # Find the 2 differing lhs. There should be 1 and they should have the same rhs:
            differing_expected = [eq for eq in expected if eq[0] not in [e[0] for e in generated]]
            differing_generated = [eq for eq in generated if eq[0] not in [e[0] for e in expected]]
            assert len(differing_expected) == len(differing_generated) == 1
            assert self._is_same_equation(differing_expected[0][1], differing_generated[0][1])

            # update the expected dV/dt  with the differeing variable name
            # so that the check for the set of equations succeeds
            expected[-1][1] = expected[-1][1].subs({self._get_var_name(differing_expected[0][0]):
                                                    self._get_var_name(differing_generated[0][0])})

            # update the expected name for this variable, so that the check for the set of equations succeeds
            expected_index = expected.index(differing_expected[0])
            expected[expected_index][0] = differing_generated[0][0]

            # now the lhs of equations should be the same

        # Equations are equal
        sorted_generated = sorted(generated, key=lambda eq: eq[0])
        sorted_expected = sorted(expected, key=lambda eq: eq[0])
        for i in range(len(sorted_generated)):
            assert sorted_generated[i][0] == sorted_expected[i][0]
            assert self._is_same_equation(sorted_generated[i][1], sorted_expected[i][1])

        # Check the order for generated: lhs doesn't appear in earlier rhs (could give c++ compile error)
        rhs_symbols = set()
        for i in range(len(generated)):
            # Update symbold we have seen on the rhs so far
            rhs_symbols.update([str(x) for x in generated[i][1].free_symbols])
            # The lhs should not appear as otherwise it is being used before being defined
            assert self._get_var_name(generated[i][0]) not in rhs_symbols

    def _check_match_gengerated_chaste_cpp(self, gen_path, model_name_from_file, model_type):
        expected_cpp_file = \
            os.path.join(cg.DATA_DIR, 'tests', 'chaste_reference_models',
                         model_type, model_name_from_file + '.cpp')
        generated_cpp_file = os.path.join(gen_path, model_name_from_file + '.cpp')

        expected_cpp = self._get_file_lines(expected_cpp_file)
        generated_cpp = self._get_file_lines(generated_cpp_file)

        self._keep_subs = False

        # Remove empty lines
        expected_i = generated_i = 0
        while expected_i < len(expected_cpp) or generated_i < len(generated_cpp):
            if expected_i < len(expected_cpp) and expected_cpp[expected_i] == '':
                del expected_cpp[expected_i]
            else:
                expected_i += 1
            if generated_i < len(generated_cpp) and generated_cpp[generated_i] == '':
                del generated_cpp[generated_i]
            else:
                generated_i += 1

        expected_i = generated_i = 0
        while expected_i < len(expected_cpp) and generated_i < len(generated_cpp):
            # If lines are the same (ignore indtation)
            expected_line = expected_cpp[expected_i]
            generated_line = generated_cpp[generated_i]
            self._keep_subs = self._keep_subs or expected_line.strip() == 'if (mSetVoltageDerivativeToZero)'
            if self._same_with_number(expected_line, generated_line):
                expected_i += 1
                generated_i += 1
            else:
                # We must be in an equation block (or the model is wrong)
                expected_i, expected_eq = self._get_equation_list(expected_cpp, expected_i)
                generated_i, generated_eq = self._get_equation_list(generated_cpp, generated_i)

                # Check the equations are the same
                self._check_equation_list(expected_eq, generated_eq)
        # Must have reached end of both files
        assert expected_i == len(expected_cpp) and generated_i == len(generated_cpp)
