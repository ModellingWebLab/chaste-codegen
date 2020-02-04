"""
Main module for cardiac Chaste code generation
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
from ._load_template import load_template
from ._chaste_printer import ChastePrinter

from .chaste_model import ChasteModel
from .normal_chaste_model import NormalChasteModel
from .opt_chaste_model import OptChasteModel
from .cvode_chaste_model import CvodeChasteModel

