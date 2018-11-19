#
# Tests templating functionality
#
import fccodegen as cg
import logging
#import pytest


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


def test_load_template():

    template = cg.load_template('tests', 'hello.txt')
    assert template.render(name='Michael') == 'Hello Michael!'


def test_weblab_model(tmp_path):

    path = tmp_path / 'model.pyx'
    cg.create_weblab_model(None, path)

    # To see the result, use pytest -s
    # print(path.read_text())
