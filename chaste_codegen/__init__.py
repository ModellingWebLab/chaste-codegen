"""
Main module for cardiac Chaste code generation
"""
import logging
import sympy

from cellmlmanip import transpiler
from ._math_functions import _exp, _abs, _acos, _cos, _sqrt, _sin

#
# Load constants and version information
#
from ._config import (   # noqa
    DATA_DIR,
    MODULE_DIR,
    TEMPLATE_SUBDIR,
    __version__,
    __version_int__,
    version,
)


#
# Load and expose public classes and functions
#
from ._load_template import load_template  # noqa
from ._chaste_printer import ChastePrinter  # noqa

from .chaste_model import ChasteModel  # noqa
from .normal_chaste_model import NormalChasteModel  # noqa
from .opt_chaste_model import OptChasteModel  # noqa
from .cvode_chaste_model import CvodeChasteModel  # noqa

# Configure logging
logging.basicConfig()
del(logging)

# Set cellmlmanip exp function
setattr(sympy, '_exp', _exp)
transpiler.SIMPLE_MATHML_TO_SYMPY_NAMES['exp'] = '_exp'

setattr(sympy, '_abs', _abs)
transpiler.SIMPLE_MATHML_TO_SYMPY_NAMES['abs'] = '_abs'

setattr(sympy, '_acos', _acos)
transpiler.SIMPLE_MATHML_TO_SYMPY_NAMES['acos'] = '_acos'

setattr(sympy, '_cos', _cos)
transpiler.SIMPLE_MATHML_TO_SYMPY_NAMES['cos'] = '_cos'

setattr(sympy, '_sqrt', _sqrt)
transpiler.SIMPLE_MATHML_TO_SYMPY_NAMES['sqrt'] = '_sqrt'

setattr(sympy, '_sin', _sin)
transpiler.SIMPLE_MATHML_TO_SYMPY_NAMES['sin'] = '_sin'
