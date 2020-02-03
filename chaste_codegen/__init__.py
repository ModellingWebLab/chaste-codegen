"""
Main module for Web Lab code generation
"""
import logging
from cellmlmanip import transpiler
import sympy

# Configure logging
logging.basicConfig()
del(logging)

# set cellmlmanip exp function
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
# Load public classes and functions
#
from ._generator import (   # noqa
    create_weblab_model,
    load_template,
)

from .chaste_model import ChasteModel  # noqa
from .normal_chaste_model import NormalChasteModel  # noqa
from .opt_chaste_model import OptChasteModel  # noqa

from ._weblab_printer import (     # noqa
    WebLabPrinter,
)


from ._chaste_printer import (     # noqa
    ChastePrinter,
)

