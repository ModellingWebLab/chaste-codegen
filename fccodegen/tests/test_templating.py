#
# Tests templating functionality
#
import fccodegen as cg
import jinja2
import logging
import os
import pytest


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


def test_load_template():
    # Tests the load_template() method

    template = cg.load_template('tests', 'hello.txt')
    assert template.render(name='Michael') == 'Hello Michael!\n'


def test_missing_variable_raises_exception():
    # An error should be raised if the template uses variables that are not
    # given as input. We want errors to be noticed!

    template = cg.load_template('tests', 'hello.txt')
    with pytest.raises(jinja2.UndefinedError):
        template.render()


def test_unique_name_generation():
    # Tests if unique variable names are generated correctly

    # Load cellml model, get unique names
    model = cg.load_model(
        os.path.join(cg.DATA_DIR, 'tests', 'conflicting_names.cellml'))
    graph = model.get_equation_graph()

    # Test unique names
    from fccodegen._generator import get_unique_names
    unames = get_unique_names(graph)
    assert len(unames) == 9
    symbols = [v for v in graph]
    symbols.sort(key=str)

    assert unames[symbols[0]] == 'time'         # env.time
    assert unames[symbols[1]] == 'x__a'         # x.a
    assert unames[symbols[2]] == 'b'            # x.b
    assert unames[symbols[3]] == 'x__y__z_1'    # x.y__z
    assert unames[symbols[4]] == 'x__y__a'      # x__y.a
    assert unames[symbols[5]] == 'x__y__z'      # x__y.x__y__z
    assert unames[symbols[6]] == 'z'            # x__y.z
    assert unames[symbols[7]] == 'z__a'         # z.a
    assert unames[symbols[8]] == 'z__y__z'      # z.y__z

