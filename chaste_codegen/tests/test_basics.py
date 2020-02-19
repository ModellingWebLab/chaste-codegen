#
# Tests the basics of chaste_codegen
#
# import pytest
import logging
from chaste_codegen import _exp
from sympy import Symbol


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


def test_module_import():
    import chaste_codegen    # noqa


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


def test_cellmlmanip_import():
    # cellmlmanip should be available, via the setup scripts
    import cellmlmanip  # noqa


def test__exp():
    # cellmlmanip should be available, via the setup scripts
    x = Symbol('x', real=True)
    assert _exp(x).is_real
    assert _exp(x).diff() == _exp(x)
    expr = 5 * x + 6 + 25 * x ** 2
    assert _exp(expr).diff() == expr.diff() * _exp(expr)
