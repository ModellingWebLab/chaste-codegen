#
# Functions related to generating model code.
# TODO: Find a better name/description/layout
#
import fccodegen
import jinja2
import os


def load_template(*name):
    """
    Returns a path to the given template
    """
    path = os.path.join(fccodegen.DIR_TEMPLATE, *name)
    #TODO: Check absolute path is still in DIR_TEMPLATE
    #TODO: Check exists
    #TODO: Look at the jinja PackageLoader. What's the advantage?
    with open(path, 'r') as f:
        return jinja2.Template(f.read())


def load_model(path):
    """
    Loads a cellml model.
    """
    #TODO: This should become part of cellmlmanip

    import cellmlmanip
    import cellmlmanip.parser

    model = cellmlmanip.parser.Parser(path).parse()
    model.make_connections()
    for c in model.components.values():
        c.add_units_to_equations()
    for e in model.equations:
        model.check_left_right_units_equal(e)
    return model


def get_equations(model):
    """
    Gets the equations from a cellml model.
    """
    #TODO: This should become part of cellmlmanip

    graph = model.get_equation_graph()

    # Get sorted symbols
    import networkx as nx
    symbols = nx.lexicographical_topological_sort(graph, key=lambda x: str(x))

    # Create list of equations
    from sympy.physics.units import Quantity
    eqs = []
    for symbol in symbols:
        # Get equation
        eq = graph.nodes[symbol]['equation']

        # Skip symbols that are not set with an equation
        if eq is None:
            continue

        # Remove quantities (units)
        eq = eq.subs({q: 1 for q in eq.atoms(Quantity)}, simultaneous=True)

        eqs.append(eq)

    return eqs


def create_weblab_model(model, path):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.pyx`` model for use
    with the Web Lab, and stores it at ``path``.
    """
    template = load_template('wl', 'weblab_model.pyx')
    with open(path, 'w') as f:
        f.write(template.render())

