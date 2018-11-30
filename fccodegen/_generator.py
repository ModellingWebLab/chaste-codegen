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
    #TODO: This should become part of cellmlmanip, with a syntax like
    # get_equations_for(variables), and then called with the derivatives to
    # generate the RHS, or with the outputs to generate the output code.

    # Get sorted symbols
    #TODO: networkx is not a dependency of fccodegen - only of cellmlmanip. If
    #      this does _not_ get moved to cellmlmanip, it should become a dep.
    #      here too.
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
    # Component variable separator
    # Note that variables are free to use __ in their names too, it makes the
    # produced code less readable but doesn't break anything.
    sep = '__'

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
                oname = uname(oparts[0] + sep + oparts[1])
                symbols[other] = oname
                reverse[oname] = other

            # Get new name for v
            name = uname(parts[0] + sep + parts[1])

        # Store symbol name
        symbols[v] = name
        reverse[name] = v

    return symbols


def get_derivative_symbols(graph):
    """
    Returns a list of derivative symbols found in the given model graph.
    """
    #TODO: This should become part of cellmlmanip

    return [v for v in graph if isinstance(v, sp.Derivative)]


def get_state_symbols(graph):
    """
    Returns a list of state variables found in the given model graph.
    """
    #TODO: This should become part of cellmlmanip

    return [v.args[0] for v in get_derivative_symbols(graph)]


def get_free_variable_symbol(graph):
    """
    Returns the free variable of the given model graph.
    """
    #TODO: This should become part of cellmlmanip

    for v in graph:
        if graph.nodes[v].get('variable_type', '') == 'free':
            return v

    # pragma: no cover
    # This should be unreachable
    raise ValueError('No free variable set in model.')


def get_symbol_by_cmeta_id(graph, cmeta_id):
    """
    Searches the given graph and returns the symbol for the variable with the
    given cmeta_id.
    """
    #TODO: This should become part of cellmlmanip
    #TODO: Either add an argument to allow derivative symbols to be fetched, or
    #      create a separate method for them.

    for v in graph:
        if graph.nodes[v].get('cmeta:id', '') == cmeta_id:
            return v
    raise KeyError('No variable with cmeta id "' + str(cmeta_id) + '" found.')


def get_value(graph, symbol):
    """
    Returns the evaluated value of the given symbol's RHS.
    """
    # TODO This should become part of cellmlmanip

    # Find RHS
    rhs = graph.nodes[symbol]['equation'].rhs

    # Remove units
    from sympy.physics.units import Quantity
    rhs = rhs.subs({q: 1 for q in rhs.atoms(Quantity)}, simultaneous=True)

    # Evaluate and return
    return float(rhs.evalf())


def create_weblab_model(path, class_name, model, outputs, parameters):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.pyx`` model for use with
    the Web Lab, and stores it at ``path``.

    Arguments

    ``path``
        The path to store the generated model code at.
    ``class_name``
        A name for the generated class.
    ``model``
        A :class:`cellmlmanip.Model` object.
    ``outputs``
        An ordered list of cmeta ids for the variables to use as model outputs.
    ``parameters``
        An ordered list of cmeta ids for the variables to use as model
        parameters. All variables used as parameters must be literal constants.

    """
    # Get equation graph
    graph = model.get_equation_graph()

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
    printer = cg.WebLabPrinter(symbol_name, derivative_name)

    #TODO: Update cellmlmanip to make this code look more like:
    #
    # free_var = model.get_free_variable()
    # state_vars = model.get_state_variables()
    # derivatives = [sp.Derivative(state, free_var) for state in state_vars]
    # eqs = model.get_equations_for(derivatives)
    #

    # Create free variable name
    free_name = symbol_name(get_free_variable_symbol(graph))

    # Create state information dicts
    state_info = []
    for i, state in enumerate(get_state_symbols(graph)):
        initial_value = float(graph.nodes[state]['initial_value'])
        state_info.append({
            'index': i,
            'var_name': symbol_name(state),
            'deriv_name': derivative_name(state),
            'initial_value': initial_value,
        })

    # Create output information dicts
    # Each output is associated either with a symbol or a parameter.
    output_info = []
    for i, output in enumerate(outputs):
        # For outputs that are parameters, obtain the parameter index
        pid = None
        try:
            pid = parameters.index(output)
        except ValueError:
            pass

        output_info.append({
            'index': i,
            'cmeta_id': output,
            'var_name': symbol_name(get_symbol_by_cmeta_id(graph, output)),
            'parameter_index': pid,
        })

    # Create parameter information dicts
    parameter_info = []
    for i, parameter in enumerate(parameters):
        symbol = get_symbol_by_cmeta_id(graph, parameter)
        parameter_info.append({
            'index': i,
            'cmeta_id': parameter,
            'var_name': symbol_name(symbol),
            'initial_value': get_value(graph, symbol),
        })

    # Create the RHS equations
    #deriv_syms = get_derivative_symbols(graph)
    rhs_equations = []
    for eq in get_equations(graph):
        lhs, rhs = eq.lhs, eq.rhs
        rhs_equations.append(
            printer.doprint(lhs) + ' = ' + printer.doprint(rhs))

    # Generate model
    template = load_template('wl', 'weblab_model.pyx')
    with open(path, 'w') as f:
        f.write(template.render({
            'class_name': class_name,
            'free_variable': free_name,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'generator_name': cg.version(formatted=True),
            'model_name': model.name,
            'n_parameters': len(parameter_info),
            'n_states': len(state_info),
            'outputs': output_info,
            'parameters': parameter_info,
            'rhs_equations': rhs_equations,
            'states': state_info,
        }))

