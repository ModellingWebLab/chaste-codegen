"""
Main module for Web Lab code generation
"""
import logging
import sympy

from cellmlmanip import transpiler

# Configure logging
logging.basicConfig()
del(logging)

# Set cellmlmanip exp function
setattr(sympy, '_exp', sympy.Function('_exp'))
transpiler.SIMPLE_MATHML_TO_SYMPY_NAMES['exp'] = '_exp'

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
from ._load_template import load_template    # noqa
from ._chaste_printer import ChastePrinter  # noqa

from .chaste_model import ChasteModel  # noqa
from .normal_chaste_model import NormalChasteModel  # noqa
from .opt_chaste_model import OptChasteModel  # noqa

