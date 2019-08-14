#
# Functions related to generating model code.
# TODO: Find a better name/description/layout
#
import jinja2
import logging
import os
import posixpath
import sympy as sp
import time
import weblab_cg as cg


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
    Loads a template from the local template directory.

    Templates can be specified as a single filename, e.g.
    ``load_template('temp.txt')``, or loaded from subdirectories using e.g.
    ``load_template('subdir_1', 'subdir_2', 'file.txt')``.

    """
    # Due to a Jinja2 convention, posixpaths must be used, regardless of the
    # user's operating system!
    path = posixpath.join(*name)
    if os.path.sep != '/' and os.path.sep in path:  # pragma: no linux cover
        log = logging.getLogger()
        log.warning('Paths to templates must be specified as posix paths.')

    env = _jinja_environment()
    return env.get_template(path)


def get_unique_names(model):
    """
    Creates unique names for all symbols in a CellML model.
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

    for v in model.get_equation_graph():
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
        An ordered list of annotations ``(namespace_uri, local_name)`` for the
        variables to use as model outputs.
    ``parameters``
        An ordered list of annotations ``(namespace_uri, local_name)`` for the
        variables to use as model parameters. All variables used as parameters
        must be literal constants.

    """
    # TODO: Jon's comment on the outputs/parameters being annotations:
    # IIRC the pycml code basically says you can use anything that's a valid
    # input to create_rdf_node. So we might eventually want to avoid all the
    # *parameter unpacking when passing around, but I don't think it's urgent.

    # TODO: About the outputs:
    # WL1 uses just the local names here, without the base URI part. What we
    # should do eventually is update the ModelWrapperEnvironment so we can use
    # a separate instance for each namespace defined by the protocol, and then
    # we can use longer names here and let each environment wrap its respective
    # subset. But until that happens, users just have to make sure not to use
    # the same local name in different namespaces.

    # Get unique names for all symbols
    unames = get_unique_names(model)

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
        state_info.append({
            'index': i,
            'var_name': symbol_name(state),
            'deriv_name': derivative_name(state),
            'initial_value': model.get_initial_value(state),
        })

    # Create parameter information dicts
    parameter_info = []
    for i, parameter in enumerate(parameters):
        symbol = model.get_symbol_by_ontology_term(*parameter)
        parameter_info.append({
            'index': i,
            'annotation': parameter,
            'var_name': symbol_name(symbol),
            'initial_value': model.get_value(symbol),
        })

    # Create map of parameter symbols to their indices
    parameter_symbols = {}
    for i, parameter in enumerate(parameters):
        symbol = model.get_symbol_by_ontology_term(*parameter)
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
            symbol = model.get_symbol_by_ontology_term(*output)
            var_name = symbol_name(symbol)
            parameter_index = parameter_symbols.get(symbol, None)
            length = None

        output_info.append({
            'index': i,
            'annotation': output,
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
    output_symbols = [model.get_symbol_by_ontology_term(*x) for x in outputs
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

