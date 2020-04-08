import sympy as sp


def get_jacobian(state_vars, derivative_equations):
    """Calculate the analytic jacobian
    
    :param state_vars: set of state variables
    :param derivative_equations: set of equations defining derivatives
    :return: Common expressions, jacobian matrix.
             The list of common expressions is of the form [('var_x1', <expression>), ..]
             The jacobian Matrix is an sympy.Matrix
    """
    if len(state_vars) == 0:
        return [], sp.Matrix([])
    jacobian_equations, jacobian_matrix = [], []
    state_var_matrix = sp.Matrix(state_vars)
    # sort by state var
    derivative_eqs = sorted(derivative_equations, key=lambda d: state_vars.index(d.lhs.args[0]))
    # we're only interested in the rhs
    derivative_eqs = [eq.rhs for eq in derivative_eqs]
    derivative_eq_matrix = sp.Matrix(derivative_eqs)
    jacobian_matrix = derivative_eq_matrix.jacobian(state_var_matrix)
    jacobian_equations, jacobian_matrix = sp.cse(jacobian_matrix, order='none')
    return jacobian_equations, sp.Matrix(jacobian_matrix)


def format_jacobian(jacobian_equations, jacobian_matrix, printer, swap_inner_outer_index=True, skip_0_entries=True):
    """Format the jacobian for outputting
    
    :param jacobian_equations: list of common term equations (expects a list as per get_jacobian)
    :param jacobian_matrix: a jacobian matrix (expects a sympy.Matrix as per get_jacobian)
    :param printer: printer object to retreive outputtable version of variables and equations
    :param swap_inner_outer_index: swap inner and outer index so [j, i] instead of [i, j]  by swapping swap loops.
                                   This swpas whether the 1st index is row or column.
    :param skip_0_entries: should entries in the jacobian matrixt that are 0 be skipped in the output?
    :return: Formatted common expressions, formattex jacobian matrix.
             The formatted list of common expressions is of the form 
             [{'lhs': 'var_x1', 'rhs': <printed_expr>, 'sympy_lhs': x1}]
             The jacobian Matrix is a list of the form: 
             [{'i': i, 'j': 'entry': <printted jacobian matrix entry for index [i, j])}
    """
    assert isinstance(jacobian_matrix, sp.Matrix), 'Expecting a jacobian as a matrix'
    equations = [{'lhs': printer.doprint(eq[0]), 'rhs': printer.doprint(eq[1]), 'sympy_lhs': eq[0]}
                 for eq in jacobian_equations]
    rows, cols = jacobian_matrix.shape
    jacobian = []
    for i in range(cols if swap_inner_outer_index else rows):
        for j in range(rows if swap_inner_outer_index else cols):
            matrix_entry = jacobian_matrix[j, i] if swap_inner_outer_index else jacobian_matrix[i, j]
            if not skip_0_entries or matrix_entry != 0:
                jacobian.append({'i': j if swap_inner_outer_index else i, 'j': i if swap_inner_outer_index else j,
                                 'entry': printer.doprint(matrix_entry)})
    return equations, jacobian
