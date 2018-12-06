#
# Tests the basics of fccodegen
#
#import pytest
import logging


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


def test_module_import():
    import fccodegen    # noqa


def test_version():
    # Test the version() method
    import fccodegen

    version = fccodegen.version()
    assert isinstance(version, tuple)
    assert len(version) == 3
    assert isinstance(version[0], int)
    assert isinstance(version[1], int)
    assert isinstance(version[2], int)
    assert version[0] >= 0
    assert version[1] >= 0
    assert version[2] >= 0

    version = fccodegen.version(formatted=True)
    assert isinstance(version, str)
    assert len(version) >= 1


def test_cellmlmanip_import():
    # cellmlmanip should be available, via the setup scripts
    import cellmlmanip  # noqa
