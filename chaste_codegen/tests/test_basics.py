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


def test_versioned_reference_path(tmp_path):
    # versioned_reference_path should pick the highest --sympy_X_Y threshold <= running version,
    # and must tolerate pre-release/dev version strings (e.g. '1.14rc1', '1.15.dev0').
    from chaste_codegen.tests.conftest import versioned_reference_path

    base = str(tmp_path / 'foo.txt')
    variant = str(tmp_path / 'foo--sympy_1_13.txt')
    open(base, 'w').close()
    open(variant, 'w').close()

    for below in ['1.10', '1.12', '1.12rc1']:
        assert versioned_reference_path(base, below) == base, below
    for at_or_above in ['1.13', '1.13.3', '1.14', '1.14rc1', '1.15.dev0', '2.0.0b1']:
        assert versioned_reference_path(base, at_or_above) == variant, at_or_above

    import pytest
    with pytest.raises(ValueError):
        versioned_reference_path(base, 'not-a-version')
