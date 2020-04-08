import sympy as sp


def get_jacobian(state_vars, derivative_equations):
    """Calculate the analytic jacobian"""
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


def format_jacobian(jacobian_equations, jacobian_matrix, printer, swap_inner_outer_loop=True, skip_0_entries=True):
    """Format the jacobian for outputting"""
    assert isinstance(jacobian_matrix, sp.Matrix), 'Expecting a jacobian as a matrix'
    equations = [{'lhs': printer.doprint(eq[0]), 'rhs': printer.doprint(eq[1]), 'sympy_lhs': eq[0]}
                 for eq in jacobian_equations]
    rows, cols = jacobian_matrix.shape
    jacobian = []
    for i in range(cols if swap_inner_outer_loop else rows):
        for j in range(rows if swap_inner_outer_loop else cols):
            matrix_entry = jacobian_matrix[j, i] if swap_inner_outer_loop else jacobian_matrix[i, j]
            if not skip_0_entries or matrix_entry != 0:
                jacobian.append({'i': j if swap_inner_outer_loop else i, 'j': i if swap_inner_outer_loop else j,
                                 'entry': printer.doprint(matrix_entry)})
    return equations, jacobian
