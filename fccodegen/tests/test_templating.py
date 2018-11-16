import fccodegen as cg
import logging
#import pytest

from .shared import TemporaryDirectory


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


class TestBasics(object):
    """
    Tests the templating methods.
    """
    def test_load_template(self):

        template = cg.load_template('tests', 'hello.txt')
        assert template.render(name='Michael') == 'Hello Michael!'

    def test_weblab_model(self):

        with TemporaryDirectory() as d:
            path = d.path('model.pyx')
            cg.create_weblab_model(None, path)
