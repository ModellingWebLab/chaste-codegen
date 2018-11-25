#
# Tests templating functionality
#
import fccodegen as cg
import logging
import os


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


def test_load_template():
    # Tests the load_template() method

    template = cg.load_template('tests', 'hello.txt')
    assert template.render(name='Michael') == 'Hello Michael!'


def test_unique_name_generation():
    # Tests if unique variable names are generated correctly

    # Load cellml model, get unique names
    model = os.path.join(
        cg.DIR_DATA, 'tests',
        #'hodgkin_huxley_squid_axon_model_1952_modified.cellml'
        'conflicting_names.cellml',
    )
    model = cg.load_model(model)
    graph = model.get_equation_graph()

    # Test unique names
    from fccodegen._generator import get_unique_names
    unames = get_unique_names(graph)
    assert len(unames) == 9
    symbols = [v for v in graph]
    symbols.sort(key=lambda x: str(x))

    assert unames[symbols[0]] == 'time'         # env$time
    assert unames[symbols[1]] == 'x_a'          # x$a
    assert unames[symbols[2]] == 'b'            # x$b
    assert unames[symbols[3]] == 'x_y_z_1'      # x$y_z
    assert unames[symbols[4]] == 'x_y_a'        # x_y$a
    assert unames[symbols[5]] == 'x_y_z'        # x_y$x_y_z
    assert unames[symbols[6]] == 'z'            # x_y$z
    assert unames[symbols[7]] == 'z_a'          # z$a
    assert unames[symbols[8]] == 'z_y_z'        # z$y_z

