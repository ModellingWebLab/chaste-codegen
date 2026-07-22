#
# Tests the reference-comparison helpers in conftest.py
#
import pytest

from chaste_codegen.tests.conftest import compare_string_against_reference, get_reference_candidates


def test_get_reference_candidates(tmp_path):
    # get_reference_candidates lists the base reference plus any sibling --<label> variant files.
    base = str(tmp_path / 'foo.txt')
    variant_1 = str(tmp_path / 'foo--python_3_11.txt')
    variant_2 = str(tmp_path / 'foo--sympy_1_14.txt')
    for path in (base, variant_1, variant_2):
        open(path, 'w').close()
    open(str(tmp_path / 'foobar.txt'), 'w').close()  # unrelated sibling, must be ignored

    assert get_reference_candidates(base) == [base, variant_1, variant_2]


def test_compare_string_matches_any_variant(tmp_path):
    # A generated string is accepted if it matches the base reference or any variant, else it fails.
    base = str(tmp_path / 'foo.txt')
    variant = str(tmp_path / 'foo--python_3_11.txt')
    with open(base, 'w') as f:
        f.write('base output')
    with open(variant, 'w') as f:
        f.write('variant output')

    compare_string_against_reference(base, 'base output')     # matches the base
    compare_string_against_reference(base, 'variant output')  # matches a variant

    with pytest.raises(AssertionError):
        compare_string_against_reference(base, 'something else')  # matches neither
