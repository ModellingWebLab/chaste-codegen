"""
Main module for cardiac Chaste code generation
"""
import logging
from cellmlmanip.transpiler import Transpiler
from ._math_functions import RealFunction, exp_, abs_, acos_, cos_, sqrt_, sin_

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
from .be_model import BeModel  # noqa

# Configure logging
logging.basicConfig()
del(logging)

# Set transpiler to prodcue our custom classes in order to avoid premature simplification/canonisation
Transpiler.set_mathml_handler('exp', exp_)
Transpiler.set_mathml_handler('abs', abs_)
Transpiler.set_mathml_handler('acos', acos_)
Transpiler.set_mathml_handler('cos', cos_)
Transpiler.set_mathml_handler('sqrt', sqrt_)
Transpiler.set_mathml_handler('sin', sin_)
