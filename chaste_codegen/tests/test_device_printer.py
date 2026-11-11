#
# Tests conversion of sympy expressions to C++ code that can be compiled for both CPU and GPU.
#
import logging

import pytest
import sympy as sp

import chaste_codegen as cg


# Show more logging output
logging.getLogger().setLevel(logging.INFO)


class TestChasteDevicePrinter(object):

    @pytest.fixture(scope="class")
    def printer(self):
        return cg.ChasteDevicePrinter()

    @pytest.fixture(scope="class")
    def x(self):
        return sp.symbols('x')

    @pytest.fixture(scope="class")
    def y(self):
        return sp.symbols('y')

    @pytest.fixture(scope="class")
    def t(self):
        return sp.symbols('t')

    def test_numbers(self, printer, x):
        assert printer.doprint(sp.Float(0.25) * x) == 'ValueType(0.25) * x'
        assert printer.doprint(sp.Float(-1.5) + x) == 'ValueType(-1.5) + x'
        assert printer.doprint(sp.Float(3.0) * x) == '3 * x'
        assert printer.doprint(sp.Float(1e20) * x) == 'ValueType(1.0e+20) * x'
        assert printer.doprint(sp.Rational(1, 3)) == 'ValueType(1) / ValueType(3)'
        assert printer.doprint(sp.pi * x) == 'ValueType(M_PI) * x'
        assert printer.doprint(sp.E * x) == 'ValueType(M_E) * x'

    def test_pow(self, printer, x, y):
        assert printer.doprint(x ** y) == 'std::pow(x, y)'
        assert printer.doprint(x ** 3) == 'std::pow(x, ValueType(3))'
        assert printer.doprint(x ** sp.Float(3.0)) == 'std::pow(x, ValueType(3))'
        assert printer.doprint(x ** sp.Float(2.5)) == 'std::pow(x, ValueType(2.5))'
        assert printer.doprint(sp.Pow(x, 0.5)) == 'std::sqrt(x)'
        assert printer.doprint(sp.sympify('x ** (-1/2)')) == '1 / std::sqrt(x)'
        assert printer.doprint(1 / x) == '1 / x'

    def test_functions(self, printer, x, y):
        assert printer.doprint(sp.exp(x) + sp.log(y)) == 'std::exp(x) + std::log(y)'
        assert printer.doprint(sp.Abs(x)) == 'std::fabs(x)'
        assert printer.doprint(sp.floor(x)) == 'std::floor(x)'
        assert printer.doprint(sp.atan2(x, y)) == 'std::atan2(x, y)'

    def test_integer_function_arguments(self, printer, x):
        assert printer.doprint(sp.exp(2, evaluate=False)) == 'std::exp(ValueType(2))'
        assert printer.doprint(sp.Abs(-3, evaluate=False)) == 'std::fabs(ValueType(-3))'
        assert printer.doprint(sp.atan2(x, sp.Float(1.0))) == 'std::atan2(x, ValueType(1))'

    def test_sign(self, printer, x):
        assert printer.doprint(sp.sign(x)) == \
            '((x) > 0 ? ValueType(1) : ((x) < 0 ? ValueType(-1) : ValueType(0)))'

    def test_piecewise(self, printer, x):
        expr = sp.Piecewise((x, x > sp.Float(-40.5)), (sp.Float(0.5), True))
        assert printer.doprint(expr) == '((x > ValueType(-40.5)) ? (x) : (ValueType(0.5)))'

    def test_device_inputs(self, printer, x, t):
        stimulus = sp.Function('GetIntracellularAreaStimulus')(t)
        capacitance = sp.Function('HeartConfig::Instance()->GetCapacitance')()
        assert printer.doprint(-stimulus * x) == '-x * stimulus'
        assert printer.doprint(x / capacitance) == 'x / capacitance'

    def test_unsupported_functions(self, printer, x, t):
        with pytest.raises(ValueError, match='Unsupported function: factorial'):
            printer.doprint(sp.factorial(x))
        with pytest.raises(ValueError, match='Unsupported function: GetExperimentalVoltageAtTimeT'):
            printer.doprint(sp.Function('GetExperimentalVoltageAtTimeT')(t))
