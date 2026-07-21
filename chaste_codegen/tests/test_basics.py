#
# Tests the basics of chaste_codegen
#


def test_module_import():
    import chaste_codegen  # noqa


def test_version():
    # Test the version() method
    import chaste_codegen as cg

    version = cg.version()
    assert isinstance(version, tuple)
    assert len(version) == 3
    assert isinstance(version[0], int)
    assert isinstance(version[1], int)
    assert isinstance(version[2], int)
    assert version[0] >= 0
    assert version[1] >= 0
    assert version[2] >= 0

    version = cg.version(formatted=True)
    assert isinstance(version, str)
    assert len(version) >= 1
    assert version.startswith('chaste_codegen ')


def test_cellmlmanip_import():
    # cellmlmanip should be available, via the setup scripts
    import cellmlmanip  # noqa


def test_reference_candidates(tmp_path):
    # reference_candidates lists the base reference plus any sibling --<label> variant files.
    from chaste_codegen.tests.conftest import reference_candidates

    base = str(tmp_path / 'foo.txt')
    variant_1 = str(tmp_path / 'foo--python_3_11.txt')
    variant_2 = str(tmp_path / 'foo--sympy_1_14.txt')
    for path in (base, variant_1, variant_2):
        open(path, 'w').close()
    open(str(tmp_path / 'foobar.txt'), 'w').close()  # unrelated sibling, must be ignored

    assert reference_candidates(base) == [base, variant_1, variant_2]


def test_compare_string_matches_any_variant(tmp_path):
    # A generated string is accepted if it matches the base reference or any variant, else it fails.
    from chaste_codegen.tests.conftest import compare_string_against_reference

    base = str(tmp_path / 'foo.txt')
    variant = str(tmp_path / 'foo--python_3_11.txt')
    with open(base, 'w') as f:
        f.write('base output')
    with open(variant, 'w') as f:
        f.write('variant output')

    compare_string_against_reference('base output', base)     # matches the base
    compare_string_against_reference('variant output', base)  # matches a variant

    import pytest
    with pytest.raises(AssertionError):
        compare_string_against_reference('something else', base)  # matches neither
