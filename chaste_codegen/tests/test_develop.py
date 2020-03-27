import logging
import math
import os
import random
import re
import time

import cellmlmanip
import pyparsing
import pytest
import sympy
from sympy import SympifyError

import chaste_codegen as cg
import chaste_codegen.tests.chaste_test_utils as test_utils


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def get_models():
    """ Load all models if they haven't been loaded yet"""
    return test_utils.load_chaste_models(model_types=['Normal', 'Opt', 'Cvode'], reference_folder='develop')


class TestChasteCG(object):
    """ Tests to help development of chaste_codegen. This test compares symbolically against pycml reference output"""
    _NUM_REGEX = re.compile(r'(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?')
    _FLOAT_PRECISION = 11

    @pytest.mark.parametrize(('model'), get_models())
    def test_generate_chaste_models_develop(self, tmp_path, model):
        """ Check generation of Normal models against reference"""
        tmp_path = str(tmp_path)
        class_name = 'Cell' + model['model_name_from_file'] + 'FromCellML'
        LOGGER.info('Converting: ' + model['model_type'] + ' ' + class_name + '\n')
        # Generate chaste code
        chaste_model = cg.NormalChasteModel(cellmlmanip.load_model(model['model']), model['model_name_from_file'],
                                            class_name=class_name)
        chaste_model.dynamically_loadable = True
        chaste_model.generate_chaste_code()

        # Write generated files
        hhp_gen_file_path = os.path.join(tmp_path, model['model_type'], chaste_model.file_name + ".hpp")
        cpp_gen_file_path = os.path.join(tmp_path, model['model_type'], chaste_model.file_name + ".cpp")
        test_utils.write_file(hhp_gen_file_path, chaste_model.generated_hpp)
        test_utils.write_file(cpp_gen_file_path, chaste_model.generated_cpp)

        # Load reference files
        expected_hpp = \
            test_utils.get_file_lines(model['expected_hpp_path'], remove_comments=True)
        expected_cpp = \
            test_utils.get_file_lines(model['expected_cpp_path'], remove_comments=True)

        # Load generated files
        generated_hpp = test_utils.get_file_lines(hhp_gen_file_path, remove_comments=True)
        generated_cpp = test_utils.get_file_lines(cpp_gen_file_path, remove_comments=True)

        assert expected_hpp == generated_hpp
        self._check_match_gengerated_chaste_cpp(generated_cpp, expected_cpp)

    def _check_match_gengerated_chaste_cpp(self, generated_cpp, expected_cpp):
        """ Check the generated cpp symbolicly"""
        self._keep_subs = False

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

    def _numbers_with_float_precision(self, line):
        """ Get numbers reduced to set float precision"""
        def format_numbers(m):
            number = m.group(0)
            count = 0
            num_str = ""
            i = 0
            exponent = 0
            before_dot = 0
            existingexp_ = ""
            seen_dot = False
            # get the digits until float precision
            while i < len(number) and count <= self._FLOAT_PRECISION and not number[i].lower() == 'e':
                count += 1  # count the dot as for fractional numbers later we add an extra digit for rounding
                if number[i] != '.':
                    if not seen_dot:
                        before_dot += 1
                else:
                    seen_dot = True
                num_str += number[i]
                i += 1

            if seen_dot and i < len(number) and number[i].isnumeric():
                num_str += number[i]
                num_str = str(round(float(num_str), self._FLOAT_PRECISION - before_dot))

            # Count exponent factor to add
            while i < len(number) and not number[i].lower() == 'e':
                seen_dot = seen_dot or number[i] == '.'
                if not seen_dot:
                    exponent += 1
                i += 1

            # See if there was an exponent already
            if i < len(number) and number[i].lower() == 'e':
                i += 1
                while i < len(number):
                    existingexp_ += number[i]
                    i += 1

            # Add exponent to what w got from cut off
            if existingexp_ != "":
                exponent += int(existingexp_)

            if exponent != 0:
                num_str += "e" + str(exponent)

            return num_str

        line = self._NUM_REGEX.sub(format_numbers, line)
        return line

    def _is_same_equation(self, eq1, eq2, try_numeric=False):
        """ Check if 2 sympy equations are the same"""
        def is_float(s):
            try:
                float(str(s))
                return True
            except ValueError:
                return False

        def is_same(eq1, eq2):
            return (eq1 == eq2) or (sympy.simplify(eq1 - eq2) == 0.0) \
                or (eq2 != 0.0 and (sympy.simplify(eq1 / eq2)) == 1.0)

        # If they are the same, no need for elaborate check
        if eq1 == eq2:
            return True
        eq1 = sympy.sympify(eq1)
        eq2 = sympy.sympify(eq2)

        e1 = sympy.sympify(self._numbers_with_float_precision(str(eq1)))
        e2 = sympy.sympify(self._numbers_with_float_precision(str(eq2)))
        if is_same(e1, e2):
            return True
        if not try_numeric:
            return False

        random.seed(time.time())
        subs_dict = {}
        for i in range(1000):
            free_symbols = eq1.free_symbols
            free_symbols.update(eq2.free_symbols)
            for symbol in free_symbols:
                random_val = random.uniform(-1000, 1000)
                subs_dict.update({symbol: random_val})
            a = sympy.simplify(eq1.subs(subs_dict))
            b = sympy.simplify(eq2.subs(subs_dict))
            if not math.isclose(float(a), float(b)):
                return False
        return True

    def _same_with_number(self, line1, line2):
        """ Compare strings comparing numbers pairwise with sympy"""
        # If they are the same, no need for elaborate check
        if line1 == line2:
            return True

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
                    if not self._is_same_equation(num1[i], num2[i]):
                        return False
                return True
        return False

    def _getexp_ression(self, expr_parts):
        """ Return the expression, handling conditionals (cond?exp:exp). Given a list of nested expression parts"""
        # process list
        # if element is list, recursively process list
        # if len(element> >= 5 : proess recursively
        # else if ? -> condition, ;-> expr, end -> expr
        # else (not ? :)-> add expr
        # if not conditional return expr
        # else: repeat: find last expr and resolve
        expression = ''
        conditional_parts = []
        if not isinstance(expr_parts, list) and not len(expr_parts) >= 5:
            return expr_parts
        else:
            for part in expr_parts:
                if part == '==':
                    conditional_parts.append(('expression', expression))
                    conditional_parts.append(('==', '=='))
                    expression = ''
                elif part == '?':
                    conditional_parts.append(('expression', expression))
                    conditional_parts.append(('?', '?'))
                    expression = ''
                elif part == ':':
                    conditional_parts.append(('expression', expression))
                    conditional_parts.append((':', ':'))
                    expression = ''
                else:
                    expression += self._getexp_ression(part)
            conditional_parts.append(('expression', expression))  # ends with expression

            # translate equals
            has_equals = True
            while has_equals:
                has_equals = False
                for i in range(len(conditional_parts)):
                    if conditional_parts[i][0] == '==':
                        has_equals = True
                        exp1 = conditional_parts[i - 1][1]
                        exp2 = conditional_parts[i + 1][1]
                        conditional_parts[i - 1] = 'Eq(' + exp1 + ', ' + exp2 + ')'
                        del conditional_parts[i:i + 2]
                        break

            # translate conditionals
            while len(conditional_parts) > 1:
                # find last condition
                for i in range(len(conditional_parts) - 1, - 1, - 1):
                    if conditional_parts[i][0] == '?' and conditional_parts[i + 2][0] == ':':
                        # resolve nex 2 must be expressions as this was the last condition
                        cond = conditional_parts[i - 1][1]
                        exp1 = conditional_parts[i + 1][1]
                        exp2 = conditional_parts[i + 3][1]
                        conditional_parts[i - 1] = \
                            ('expression', 'Piecewise(((' + exp1 + '), (' + cond + ')), ((' + exp2 + '), True))')
                        del conditional_parts[i:]
                        break
            expression_str = conditional_parts[0][1]
            if isinstance(expr_parts, list):
                expression_str = '(' + expression_str + ')'
        return expression_str

    def _to_equation(self, equation_str):
        """ Do needed substitutions and parse brackets to handle conditionals (cond?exp:exp) """
        # pow->Pow ceil -> ceiling in sympy
        equation_str = equation_str.replace("pow(", 'Pow(').replace("ceil(", 'ceiling(').replace('fabs(', 'Abs(')
        equation_str = equation_str.replace('M_PI', 'pi')
        # This might be a C++ call with class members/pointer accessors?
        equation_str = \
            equation_str.replace('HeartConfig::Instance()->GetCapacitance()', 'HeartConfig_Instance_GetCapacitance')
        equation_str = equation_str.replace('()->', '_').replace('::', '_')
        equation_str = equation_str.replace('&&', '&').replace('||', '|')
        equation_str = equation_str.replace('[', '____').replace(']', '____')
        try:
            return sympy.simplify(equation_str)
        except SympifyError:
            expression = pyparsing.Word(pyparsing.printables, excludeChars="()")
            parens = pyparsing.nestedExpr('(', ')', content=expression)
            parenthesisexp_r = parens.parseString('(' + equation_str + ')').asList()
            expr_str = self._getexp_ression(parenthesisexp_r)
            return sympy.simplify(expr_str)

    def _get_equation_list(self, model_lines, index):
        """ Given a string list and starting index get list of equations (untill non-equation found)"""
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
        """ Get the name of a variable, stripping off declaration"""
        return c_dec.replace('const', '').replace('double', '').strip()

    def _is_deriv_decl(self, c_dec):
        """ Is the given variable name a derivative"""
        return self._get_var_name(c_dec).startswith('d_dt_chaste_interface__') \
            or self._get_var_name(c_dec).endswith('dt')

    def _is_converter(self, c_dec):
        """ Is the given variable name a converter (ending in _converter)"""
        return self._get_var_name(c_dec).endswith('_converter')

    def _perform_eq_subs(self, eq, subs_dict):
        """ Perform substitutions multiple times, untill nothing changes"""
        substituted_term = eq[1].subs(subs_dict)
        while substituted_term != eq[1]:
            eq[1] = substituted_term
            substituted_term = eq[1].subs(subs_dict)
        return [eq[0], eq[1]]

    def _resolve_linkers(self, equation_list, subs_dict):
        """ Process linking variables, remove from the list and update all relevant equations"""
        # Resolve derivatives
        remove = []
        for eq in reversed(equation_list):
            if self._is_deriv_decl(eq[0]):
                if isinstance(eq[1], sympy.symbol.Symbol):
                    # See if there are any linkers
                    for linked_eq in reversed(equation_list):
                        if self._get_var_name(linked_eq[0]) == str(eq[1]):
                            eq[1] = linked_eq[1]
                            remove.append(linked_eq[0])

        # Remove linkiners for derivatives
        equation_list = [x for x in equation_list if x[0] not in remove]

        # Resolve converter / linker variables in remaining equations
        converter_vars = [eq for eq in equation_list
                          if (self._is_converter(eq[0]) or isinstance(eq[1], sympy.symbol.Symbol) or
                              isinstance(eq[1] * -1, sympy.symbol.Symbol)) and not self._is_deriv_decl(eq[0])]

        exclude = []
        for converter in reversed(converter_vars):
            # If rhs is symobol, see if there is an equation we can subs in
            if isinstance(converter[1], sympy.symbol.Symbol) or isinstance(converter[1] * -1, sympy.symbol.Symbol):
                if self._is_converter(converter[0]):
                    for eq in reversed(equation_list):
                        if str(converter[1]) == self._get_var_name(eq[0]):
                            # remove if it's not used in anything else
                            converter[1] = eq[1]
                            exclude.append(eq)
                            subs_dict[self._get_var_name(eq[0])] = eq[1]
                        elif str(converter[1] * -1) == self._get_var_name(eq[0]):
                            converter[1] = -eq[1]
                            exclude.append(eq)
                            subs_dict[self._get_var_name(eq[0])] = -eq[1]
            var_name = self._get_var_name(converter[0])
            subs_dict[var_name] = converter[1]

        # Perform substitutions
        equation_list = [self._perform_eq_subs(eq, subs_dict)
                         for eq in equation_list if eq not in converter_vars + exclude]

        return equation_list, subs_dict

    def _resolve_remaining_linkers(self, expected, generated):
        differingexp_ected = self._different_eqs(expected, generated)
        for difexp_ in differingexp_ected:
            delete = False
            for j in range(len(expected)):
                if difexp_ != expected[j]:
                    old = expected[j][1]
                    expected[j][1] = expected[j][1].subs({self._get_var_name(difexp_[0]):
                                                          difexp_[1]})
                    delete = delete or old != expected[j][1]
                    for k in range(len(generated)):
                        if expected[j][0] == generated[k][0]:
                            generated[k][1] = generated[k][1].subs({self._get_var_name(difexp_[0]):
                                                                    difexp_[1]})
            if delete:
                expected_element_index = expected.index(difexp_)
                del expected[expected_element_index]
        return expected, generated

    def _different_eqs(self, main_eqs, filter_eqs):
        filter_lhss = [eq[0] for eq in filter_eqs]
        return [eq for eq in main_eqs if eq[0] not in filter_lhss]

    def _check_equation_list(self, expected, generated):
        """ Check expected and generated represent the same equation"""
        if not self._keep_subs:
            self.link_subsexp_ected = dict()
            self.link_subs_generated = dict()
            self.generated_subs = dict()
            self.expected_subs = dict()
        self._keep_subs = False

        # Resolve linkers and converter variables
        expected, self.link_subsexp_ected = self._resolve_linkers(expected, self.link_subsexp_ected)
        generated, self.link_subs_generated = self._resolve_linkers(generated, self.link_subs_generated)

        # if they aren't the same length it could be state_var conversions try and subs
        # The 2 sets of equations should now have the same amount of equations
        # If not we may have a state var conversion still
        if len(expected) != len(generated):
            differingexp_ected = self._different_eqs(expected, generated)
            for i in range(len(differingexp_ected)):
                if len(differingexp_ected[i][1].args) == 2 and \
                        isinstance(differingexp_ected[i][1].args[0], sympy.numbers.Float) and \
                        isinstance(differingexp_ected[i][1].args[1], sympy.symbol.Symbol):
                    conversion_subs = {self._get_var_name(differingexp_ected[i][0]): differingexp_ected[i][1]}
                    expected_element_index = expected.index(differingexp_ected[i])
                    newexp_ected = [[exp[0], exp[1].subs(conversion_subs)] for exp in expected]
                    if expected != newexp_ected:
                        expected = newexp_ected
                        del expected[expected_element_index]

        # Maybe converters not recognized as converters in the expected?
        if len(expected) != len(generated):
            (expected, generated) = self._resolve_remaining_linkers(expected, generated)
        if len(expected) != len(generated):
            (generated, expected) = self._resolve_remaining_linkers(generated, expected)

        assert len(expected) == len(generated)

        # Variable names assigned to should match;
        # only exception could be name of stimulus current
        if set([eq[0] for eq in expected]) != set([eq[0] for eq in generated]):

            # Find the 2 differing lhs. There should be 1 and they should have the same rhs:
            differingexp_ected = self._different_eqs(expected, generated)
            differing_generated = self._different_eqs(generated, expected)
            assert len(differingexp_ected) == len(differing_generated)

            update_subs = dict()
            # For each equation find one that has the same rhs
            for i in range(len(differingexp_ected)):
                found = False
                for j in range(len(differing_generated)):
                    found = self._is_same_equation(differingexp_ected[i][1], differing_generated[j][1])
                    if found:
                        break
                assert found
                # update the expected name for this variable, so that the check for the set of equations succeeds
                update_subs[self._get_var_name(differingexp_ected[i][0])] = \
                    self._get_var_name(differing_generated[j][0])
                expected_index = expected.index(differingexp_ected[i])
                expected[expected_index][0] = differing_generated[j][0]

            # update the expected equations
            expected = [self._perform_eq_subs(eq, update_subs) for eq in expected]

            # Add to substitution dictionary for future use (if needed)
            self.link_subsexp_ected.update(update_subs)

        # Equations are equal
        self.generated_subs.update({self._get_var_name(x[0]): x[1] for x in generated})
        self.expected_subs.update({self._get_var_name(x[0]): x[1] for x in expected})
        sorted_generated = sorted(generated, key=lambda eq: eq[0])
        sortedexp_ected = sorted(expected, key=lambda eq: eq[0])
        for i in range(len(sorted_generated)):
            assert sorted_generated[i][0] == sortedexp_ected[i][0]
            if not self._is_same_equation(sorted_generated[i][1], sortedexp_ected[i][1]):
                eq_gen = self._perform_eq_subs(sorted_generated[i], self.generated_subs)
                eqexp_ = self._perform_eq_subs(sortedexp_ected[i], self.expected_subs)
                same = self._is_same_equation(eq_gen[1], eqexp_[1], try_numeric=True)
                assert same

        # Check the order for generated: lhs doesn't appear in earlier rhs (could give c++ compile error)
        rhs_symbols = set()
        for i in range(len(generated)):
            # Update symbold we have seen on the rhs so far
            rhs_symbols.update([str(x) for x in generated[i][1].free_symbols])
            # The lhs should not appear as otherwise it is being used before being defined
            assert self._get_var_name(generated[i][0]) not in rhs_symbols
