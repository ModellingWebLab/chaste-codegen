"""
Main module for cardiac Chaste code generation
"""
import logging
from cellmlmanip.transpiler import Transpiler
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

# Set transpiler to prodcue our custom classes in order to avoid premature simplification/canonisation
Transpiler.set_mathml_handler('exp', _exp)
Transpiler.set_mathml_handler('abs', _abs)
Transpiler.set_mathml_handler('acos', _acos)
Transpiler.set_mathml_handler('cos', _cos)
Transpiler.set_mathml_handler('sqrt', _sqrt)
Transpiler.set_mathml_handler('sin', _sin)
