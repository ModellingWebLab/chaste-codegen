#
# Tests templating functionality
#
import logging

import jinja2
import pytest

import chaste_codegen as cg


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


def test_load_template():
    # Tests the load_template() method

    template = cg.load_template('hello.txt')
    assert template.render(name='Michael') == 'Hello Michael!\n'


def test_missing_variable_raises_exception():
    # An error should be raised if the template uses variables that are not
    # given as input. We want errors to be noticed!

    template = cg.load_template('hello.txt')
    with pytest.raises(jinja2.UndefinedError):
        template.render()
