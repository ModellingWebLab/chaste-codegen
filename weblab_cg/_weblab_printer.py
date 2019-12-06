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
        'sqrt': 'math.sqrt',
        'e': 'math.e',
        'exp': 'math.exp',
        'expm1': 'math.expm1',
        'factorial': 'math.factorial',
        'floor': 'math.floor',
        'log': 'math.log',
        'log10': 'math.log10',
        'log1p': 'math.log1p',
        'log2': 'math.log2',
        'nan': 'float(\'nan\')',
        'pi': 'math.pi',
        'sin': 'math.sin',
        'sinh': 'math.sinh',
        'sqrt': 'math.sqrt',
        'tan': 'math.tan',
        'tanh': 'math.tanh'
    }

    def __init__(self, symbol_function=None, derivative_function=None):
        super().__init__(symbol_function, derivative_function)

