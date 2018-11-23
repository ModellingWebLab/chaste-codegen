#
# Tests conversion of sympy expressions to weblab cython code.
#
import fccodegen as cg
import logging
import math
import pytest
import sympy as sp


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


def test_simple():
    x, y, z = sp.symbols('x y z')

    p = cg.WebLabPrinter()

    # Number types
    assert p.doprint(1) == '1'                  # int
    assert p.doprint(1.2) == '1.2'              # float, short format
    assert p.doprint(math.pi) == '3.141592653589793'    # float, long format
    assert p.doprint(1.436432635636e-123) == '1.436432635636e-123'
    assert p.doprint(x - x) == '0'              # Zero
    assert p.doprint(x / x) == '1'              # One
    assert p.doprint(-x / x) == '-1'            # Negative one
    assert p.doprint(5 * (x / x)) == '5'        # Sympy integer
    assert p.doprint(5.5 * (x / x)) == '5.5'        # Sympy float
    assert p.doprint(5 * (x / x) / 7) == '5 / 7'    # Sympy rational

    # Special numbers
    assert p.doprint(sp.pi) == 'math.pi'
    assert p.doprint(sp.E) == 'math.e'

    # Symbols
    assert p.doprint(x) == 'x'

    # Symbol function
    def symbol_function(symbol):
        return symbol.name.upper()

    q = cg.WebLabPrinter(symbol_function)
    assert q.doprint(x) == 'X'

    # Derivatives
    assert p.doprint(sp.Derivative(x, y)) == 'Derivative(x, y)'

    # Derivative function
    def derivative_function(deriv):
        a, b = deriv.args
        return 'd' + symbol_function(a) + '/' + 'd' + symbol_function(b)

    q = cg.WebLabPrinter(derivative_function=derivative_function)
    assert q.doprint(sp.Derivative(x, y)) == 'dX/dY'

    # Addition and subtraction
    assert p.doprint(x + y) == 'x + y'
    assert p.doprint(x + y + z) == 'x + y + z'
    assert p.doprint(x - y) == 'x - y'
    assert p.doprint(2 + z) == '2 + z'
    assert p.doprint(z + 2) == '2 + z'
    assert p.doprint(z - 2) == '-2 + z'
    assert p.doprint(2 - z) == '2 - z'
    assert p.doprint(-x) == '-x'
    assert p.doprint(-x - 2) == '-2 - x'

    # Multiplication and division
    assert p.doprint(x * y) == 'x * y'
    assert p.doprint(x * y * z) == 'x * y * z'
    assert p.doprint(x / y) == 'x / y'
    assert p.doprint(2 * z) == '2 * z'
    assert p.doprint(z * 5) == '5 * z'
    assert p.doprint(4 / z) == '4 / z'
    assert p.doprint(z / 3) == 'z / 3'
    assert p.doprint(1 / x) == '1 / x'  # Uses pow
    assert p.doprint(1 / (x * y)) == '1 / (x * y)'
    assert p.doprint(1 / -(x * y)) == '-1 / (x * y)'
    assert p.doprint(x + (y + z)) == 'x + y + z'
    assert p.doprint(x * (y + z)) == 'x * (y + z)'
    assert p.doprint(x * y * z) == 'x * y * z'
    assert p.doprint(x + y > x * z), 'x + y > x * z'
    assert p.doprint(x**2 + y**2) == 'x**2 + y**2'
    assert p.doprint(x**2 + 3 * y**2) == 'x**2 + 3 * y**2'
    assert p.doprint(x**(2 + y**2)) == 'x**(2 + y**2)'
    assert p.doprint(x**(2 + 3 * y**2)) == 'x**(2 + 3 * y**2)'
    assert p.doprint(x**-1 * y**-1) == '1 / (x * y)'
    assert p.doprint(x / y / z) == 'x / (y * z)'
    assert p.doprint(x / y * z) == 'x * z / y'
    assert p.doprint(x / (y * z)) == 'x / (y * z)'
    assert p.doprint(x * y**(-2 / (3 * x / x))) == 'x / y**(2 / 3)'

    # Sympy issue #14160
    d = sp.Mul(
        -2,
        x,
        sp.Pow(sp.Mul(y, y, evaluate=False), -1, evaluate=False),
        evaluate=False
    )
    assert p.doprint(d) == '-2 * x / (y * y)'

    # Powers and square roots
    assert p.doprint(sp.sqrt(2)) == 'math.sqrt(2)'
    assert p.doprint(1 / sp.sqrt(2)) == 'math.sqrt(2) / 2'
    assert p.doprint(
        sp.Mul(1, 1 / sp.sqrt(2), eval=False)) == 'math.sqrt(2) / 2'
    assert p.doprint(sp.sqrt(x)) == 'math.sqrt(x)'
    assert p.doprint(1 / sp.sqrt(x)) == '1 / math.sqrt(x)'
    assert p.doprint(x**(x / (2 * x))) == 'math.sqrt(x)'
    assert p.doprint(x**(x / (-2 * x))) == '1 / math.sqrt(x)'
    assert p.doprint(x**-1) == '1 / x'
    assert p.doprint(x**0.5) == 'x**0.5'
    assert p.doprint(x**-0.5) == 'x**(-0.5)'
    assert p.doprint(x**(1 + y)) == 'x**(1 + y)'
    assert p.doprint(x**-(1 + y)) == 'x**(-1 - y)'
    assert p.doprint((x + z)**-(1 + y)) == '(x + z)**(-1 - y)'
    assert p.doprint(x**-2) == 'x**(-2)'
    assert p.doprint(x**3.2) == 'x**3.2'

    # Trig functions
    assert p.doprint(sp.acos(x)) == 'math.acos(x)'
    assert p.doprint(sp.acosh(x)) == 'math.acosh(x)'
    assert p.doprint(sp.asin(x)) == 'math.asin(x)'
    assert p.doprint(sp.asinh(x)) == 'math.asinh(x)'
    assert p.doprint(sp.atan(x)) == 'math.atan(x)'
    assert p.doprint(sp.atanh(x)) == 'math.atanh(x)'
    assert p.doprint(sp.ceiling(x)) == 'math.ceil(x)'
    assert p.doprint(sp.cos(x)) == 'math.cos(x)'
    assert p.doprint(sp.cosh(x)) == 'math.cosh(x)'
    assert p.doprint(sp.exp(x)) == 'math.exp(x)'
    assert p.doprint(sp.factorial(x)) == 'math.factorial(x)'
    assert p.doprint(sp.floor(x)) == 'math.floor(x)'
    assert p.doprint(sp.log(x)) == 'math.log(x)'
    assert p.doprint(sp.sin(x)) == 'math.sin(x)'
    assert p.doprint(sp.sinh(x)) == 'math.sinh(x)'
    assert p.doprint(sp.tan(x)) == 'math.tan(x)'
    assert p.doprint(sp.tanh(x)) == 'math.tanh(x)'

    # Conditions
    assert p.doprint(sp.Eq(x, y)) == 'x == y'
    assert p.doprint(sp.Eq(x, sp.Eq(y, z))) == 'x == (y == z)'
    assert p.doprint(sp.Eq(sp.Eq(x, y), z)) == '(x == y) == z'
    assert p.doprint(sp.Ne(x, y)) == 'x != y'
    assert p.doprint(sp.Gt(x, y)) == 'x > y'
    assert p.doprint(sp.Lt(x, y)) == 'x < y'
    assert p.doprint(sp.Ge(x, y)) == 'x >= y'
    assert p.doprint(sp.Le(x, y)) == 'x <= y'
    assert p.doprint(sp.Eq(sp.Eq(x, 3), 12)) == '(x == 3) == 12'

    # Boolean logic
    assert p.doprint(True) == 'True'
    assert p.doprint(False) == 'False'
    assert p.doprint(sp.Eq(x, x)) == 'True'
    assert p.doprint(sp.Ne(x, x)) == 'False'
    assert p.doprint(sp.And(sp.Eq(x, y), sp.Eq(x, z))) == 'x == y and x == z'
    assert (
        p.doprint(sp.And(sp.Eq(x, y), sp.Eq(x, z), sp.Eq(x, 2))) ==
        'x == 2 and x == y and x == z')
    assert p.doprint(sp.Or(sp.Eq(x, y), sp.Eq(x, z))) == 'x == y or x == z'
    assert (
        p.doprint(sp.Or(sp.Eq(x, y), sp.Eq(x, z), sp.Eq(x, 2))) ==
        'x == 2 or x == y or x == z')
    a, b, c = x > 2, x > y, x > z
    assert p.doprint(a & b) == 'x > 2 and x > y'
    # 1 or (0 and 0) = 1 = 1 or 0 and 0 -- and binds stronger
    # (1 or 0) and 0 = 0
    assert p.doprint(a | (b & c)) == 'x > 2 or x > y and x > z'
    assert p.doprint((a | b) & c) == 'x > z and (x > 2 or x > y)'

    # Piecewise expressions
    e = sp.Piecewise((0, x > 0), (1, True))
    assert p.doprint(e) == '((0) if (x > 0) else (1))'
    e = sp.Piecewise((0, x > 0), (1, x > 1), (2, True))
    assert p.doprint(e) == '((0) if (x > 0) else ((1) if (x > 1) else (2)))'
    e = sp.Piecewise((0, x > 0), (1, x > 1), (2, True), (3, x > 3))
    assert p.doprint(e) == '((0) if (x > 0) else ((1) if (x > 1) else (2)))'
    # Sympy filters out False statements
    e = sp.Piecewise(
        (0, x > 0), (1, x != x), (2, True), (3, x > 3),
        evaluate=False)
    assert p.doprint(e) == '((0) if (x > 0) else (2))'

    # Longer expressions
    assert (
        p.doprint((x + y) / (2 + z / sp.exp(x - y))) ==
        '(x + y) / (2 + z * math.exp(y - x))')
    assert p.doprint((y + sp.sin(x))**-1) == '1 / (y + math.sin(x))'

    # Unsupported sympy item
    e = sp.Matrix()
    with pytest.raises(RuntimeError):
        p.doprint(e)

    # Unsupported sympy function
    e = sp.gamma(x)
    with pytest.raises(RuntimeError):
        p.doprint(e)
