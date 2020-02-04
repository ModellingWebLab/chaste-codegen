"""
Main module for cardiac Chaste code generation
"""
import logging
import sympy

from cellmlmanip import transpiler

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
from ._load_template import load_templates  # noqa
from ._chaste_printer import ChastePrinters  # noqa

from .chaste_model import ChasteModels  # noqa
from .normal_chaste_model import NormalChasteModels  # noqa
from .opt_chaste_model import OptChasteModels  # noqa
from .cvode_chaste_model import CvodeChasteModels  # noqa

# Configure logging
logging.basicConfig()
del(logging)

# Set cellmlmanip exp function
setattr(sympy, '_exp', sympy.Function('_exp'))
transpiler.SIMPLE_MATHML_TO_SYMPY_NAMES['exp'] = '_exp'
