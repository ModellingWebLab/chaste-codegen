#
# Functions related to generating model code.
# TODO: Find a better name/description/layout
#
import fccodegen as cg
import jinja2
import os
import sympy as sp
import time


def load_template(*name):
    """
    Returns a path to the given template
    """
    path = os.path.join(cg.DIR_TEMPLATE, *name)
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
    model.add_units_to_equations()
    for e in model.equations:
        model.check_left_right_units_equal(e)
    return model


def get_equations(graph):
    """
    Gets the equations from a cellml model graph.
    """
    #TODO: This should become part of cellmlmanip

    # Get sorted symbols
    #TODO: networkx is not a dependency
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


def get_unique_names(graph):
    """
    Creates unique names for all symbols in a cellml model graph.
    """

    # Create a symbol => name mapping, and a reverse name => symbol mapping
    symbols = {}
    reverse = {}

    def uname(name):
        """ Add an increasing number to a name until it's unique """
        root = name + '_'
        i = 0
        while name in reverse:
            i += 1
            name = root + str(i)
        return name

    for v in graph:
        if isinstance(v, sp.Derivative):
            continue

        # Try simple name
        parts = v.name.split('$')
        assert len(parts) == 2
        name = parts[-1]

        # If already taken, rename _both_ variables using component name
        if name in reverse:

            # Get existing variable
            other = reverse[name]

            # Check it hasn't been renamed already
            if symbols[other] == name:
                oparts = other.name.split('$')
                assert len(oparts) == 2
                oname = uname(oparts[0] + '_' + oparts[1])
                symbols[other] = oname
                reverse[oname] = other

            # Get new name for v
            name = uname(parts[0] + '_' + parts[1])

        # Store symbol name
        symbols[v] = name
        reverse[name] = v

    return symbols


def get_state_list(graph):
    """
    Returns a list of state variables found in the given model graph.
    """
    states = []
    for v in graph:
        if isinstance(v, sp.Derivative):
            states.append(v.args[0])
    return states


def create_weblab_model(model, path):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.pyx`` model for use
    with the Web Lab, and stores it at ``path``.
    """
    # Get equation graph
    graph = model.get_equation_graph()

    # Get ordered equations
    eqs = get_equations(graph)

    # Get unique names for all symbols
    unames = get_unique_names(graph)

    # Symbol naming function
    def symbol_name(symbol):
        return 'var_' + unames[symbol]

    # Derivative naming function
    def derivative_name(deriv):
        var = deriv.args[0] if isinstance(deriv, sp.Derivative) else deriv
        return 'd_dt_' + unames[var]

    # Create expression printer
    p = cg.WebLabPrinter(symbol_name, derivative_name)

    # Create a list of state variable indices, variables, and derivative vars
    states = []
    for i, state in enumerate(get_state_list(graph)):
        states.append((i, symbol_name(state), derivative_name(state)))

    # Create the RHS equations
    rhs_equations = []
    for eq in eqs:
        lhs, rhs = eq.lhs, eq.rhs
        rhs_equations.append(p.doprint(lhs) + ' = ' + p.doprint(rhs))

    # Generate model
    template = load_template('wl', 'weblab_model.pyx')
    with open(path, 'w') as f:
        f.write(template.render({
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'generator': cg.version(formatted=True),
            'name': model.name,
            'rhs_equations': rhs_equations,
            'states': states,
        }))

