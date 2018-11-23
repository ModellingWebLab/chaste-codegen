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


def test_create_weblab_model(tmp_path):
    # Tests the create_weblab_model() method

    # Load cellml model
    model = os.path.join(
        cg.DIR_DATA, 'tests',
        'hodgkin_huxley_squid_axon_model_1952_modified.cellml')
    model = cg.load_model(model)
    #eqs = cg.get_equations(model)

    # Create expression printer
    #p = cg.WebLabPrinter()

    #TODO
    #for eq in eqs:
    #    lhs, rhs = eq.lhs, eq.rhs
    #    print('LHS: ' + p.doprint(lhs))
    #    print('  = ' + p.doprint(rhs))

    # Select output path (in temporary dir)
    path = tmp_path / 'model.pyx'

    # Create weblab model at path
    cg.create_weblab_model(model, path)

    # To see the result, use pytest -s
    # print(path.read_text())
