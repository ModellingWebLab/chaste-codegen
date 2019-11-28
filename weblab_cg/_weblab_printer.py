from ._printer import Printer


class WebLabPrinter(Printer):

    # Dictionary of functions we can handle and their corresponding names to be generated
    _function_names = {
        'Abs': 'abs',
        'acos': 'math.acos',
        'acosh': 'math.acosh',
        'asin': 'math.asin',
        'asinh': 'math.asinh',
        'atan': 'math.atan',
        'atan2': 'math.atan2',
        'atanh': 'math.atanh',
        'ceiling': 'math.ceil',
        'cos': 'math.cos',
        'cosh': 'math.cosh',
        'exp': 'math.exp',
        'expm1': 'math.expm1',
        'factorial': 'math.factorial',
        'floor': 'math.floor',
        'log': 'math.log',
        'log10': 'math.log10',
        'log1p': 'math.log1p',
        'log2': 'math.log2',
        'sin': 'math.sin',
        'sinh': 'math.sinh',
        'tan': 'math.tan',
        'tanh': 'math.tanh',
    }

    def __init__(self, symbol_function=None, derivative_function=None):
        super().__init__(symbol_function, derivative_function)

        # Prefix for functions
        self._prefix = 'math.'

