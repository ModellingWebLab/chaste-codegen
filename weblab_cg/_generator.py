#
# Functions related to generating model code.
# TODO: Find a better name/description/layout
#
import weblab_cg as cg
import jinja2
import os
import sympy as sp
import time


# Shared Jinja environment
_environment = None


def _jinja_environment():
    """
    Returns a shared Jinja environment to create templates from.
    """
    global _environment
    if _environment is None:
        _environment = jinja2.Environment(
            # Automatic loading of templates stored in the module
            # This also enables template inheritance
            loader=jinja2.PackageLoader('weblab_cg', cg.TEMPLATE_SUBDIR),

            # Keep a single trailing newline, if present
            keep_trailing_newline=True,

            # Don't replace undefined template variables by an empty string
            # but raise a jinja2.UndefinedError instead.
            undefined=jinja2.StrictUndefined,
        )
    return _environment


def load_template(*name):
    """
    Returns a path to the given template
    """
    path = os.path.join(*name)
    #TODO: Check absolute path is still in cg.TEMPLATE_SUBDIR

    env = _jinja_environment()
    return env.get_template(path)


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

    # Create free variable name
    free_name = symbol_name(model.get_free_variable_symbol())

    # Create state information dicts
    state_info = []
    for i, state in enumerate(model.get_state_symbols()):
        initial_value = float(graph.nodes[state]['initial_value'])
        #TODO: Update cellmlmanip so this graph.nodes goes away
        state_info.append({
            'index': i,
            'var_name': symbol_name(state),
            'deriv_name': derivative_name(state),
            'initial_value': initial_value,
        })

    # Create parameter information dicts
    #TODO: Cmeta_id should be replaced by oxmeta annotation via RDF lookup
    parameter_info = []
    for i, parameter in enumerate(parameters):
        symbol = model.get_symbol_by_cmeta_id(parameter)
        parameter_info.append({
            'index': i,
            'cmeta_id': parameter,
            'var_name': symbol_name(symbol),
            'initial_value': model.get_value(symbol),
        })

    # Create map of parameter symbols to their indices
    parameter_symbols = {}
    for i, parameter in enumerate(parameters):
        symbol = model.get_symbol_by_cmeta_id(parameter)
        parameter_symbols[symbol] = i

    # Create output information dicts
    # Each output is associated either with a symbol or a parameter.
    output_info = []
    for i, output in enumerate(outputs):

        # Allow special output value 'state_variable'
        #TODO Replace this with a more generic implementation
        if output == 'state_variable':
            var_name = [{'index': x['index'], 'var_name': x['var_name']}
                        for x in state_info]
            parameter_index = None
            length = len(state_info)
        else:
            symbol = model.get_symbol_by_cmeta_id(output)
            var_name = symbol_name(symbol)
            parameter_index = parameter_symbols.get(symbol, None)
            length = None

        output_info.append({
            'index': i,
            'cmeta_id': output,
            'var_name': var_name,
            'parameter_index': parameter_index,
            'length': length,
        })

    # Create RHS equation information dicts
    rhs_equations = []
    for eq in model.get_equations_for(model.get_derivative_symbols()):
        #TODO: Parameters should never appear as the left-hand side of an
        # equation (cellmlmanip should already have filtered these out).
        rhs_equations.append({
            'lhs': printer.doprint(eq.lhs),
            'rhs': printer.doprint(eq.rhs),
            'parameter_index': parameter_symbols.get(eq.lhs, None),
        })

    # Create output equation information dicts
    output_equations = []
    output_symbols = [model.get_symbol_by_cmeta_id(x) for x in outputs
                      if x != 'state_variable']
    for eq in model.get_equations_for(output_symbols):
        output_equations.append({
            'lhs': printer.doprint(eq.lhs),
            'rhs': printer.doprint(eq.rhs),
            'parameter_index': parameter_symbols.get(eq.lhs, None),
        })

    # Generate model
    template = load_template('wl', 'weblab_model.pyx')
    with open(path, 'w') as f:
        f.write(template.render({
            'class_name': class_name,
            'free_variable': free_name,
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'generator_name': cg.version(formatted=True),
            'model_name': model.name,
            'outputs': output_info,
            'output_equations': output_equations,
            'parameters': parameter_info,
            'rhs_equations': rhs_equations,
            'states': state_info,
        }))

