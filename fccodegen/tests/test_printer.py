#
# Tests conversion of sympy expressions to weblab cython code.
#
import fccodegen as cg
import logging
import math
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

    # Powers and square roots
    assert p.doprint(sp.sqrt(2)) == 'math.sqrt(2)'
    assert p.doprint(1 / sp.sqrt(2)) == 'math.sqrt(2) / 2'
    assert p.doprint(
        sp.Mul(1, 1 / sp.sqrt(2), eval=False)) == 'math.sqrt(2) / 2'
    assert p.doprint(sp.sqrt(x)) == 'math.sqrt(x)'
    assert p.doprint(1 / sp.sqrt(x)) == '1 / math.sqrt(x)'
    assert p.doprint(x**(x / (2 * x))) == 'math.sqrt(x)'
    assert p.doprint(x**(x / (-2 * x))) == '1 / math.sqrt(x)'
    assert p.doprint(x**0.5) == 'x**0.5'
    assert p.doprint(x**-0.5) == 'x**(-0.5)'
    assert p.doprint(x**(1 + y)) == 'x**(1 + y)'
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

    # Boolean logic
    assert p.doprint(x == x) == 'True'
    assert p.doprint(x != x) == 'False'
    assert p.doprint(sp.And(sp.Eq(x, y), sp.Eq(x, z))) == 'x == y and x == z'
    assert (
        p.doprint(sp.And(sp.Eq(x, y), sp.Eq(x, z), sp.Eq(x, 2))) ==
        'x == y and x == z and x == 2')
    assert p.doprint(sp.Or(sp.Eq(x, y), sp.Eq(x, z))) == 'x == y or x == z'
    assert (
        p.doprint(sp.Or(sp.Eq(x, y), sp.Eq(x, z), sp.Eq(x, 2))) ==
        'x == y or x == z or x == 2')
    #assert p.doprint(x != x) == 'False'

    # Longer expressions
    assert (
        p.doprint((x + y) / (2 + z / sp.exp(x - y))) ==
        '(x + y) / (2 + z * math.exp(y - x))')

