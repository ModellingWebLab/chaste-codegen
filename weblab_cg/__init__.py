"""
Main module for Web Lab code generation
"""

# Configure logging
import logging
logging.basicConfig()
del(logging)
from cellmlmanip import transpiler
import sympy

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

from ._generator_chaste_cg import (   # noqa
    NormalChasteModel,
    OptChasteModel,
    Analytic_jChasteModel,
    Numerical_jChasteModel,
    BEOptChasteModel,
)

from ._weblab_printer import (     # noqa
    WebLabPrinter,
)


from ._chaste_printer import (     # noqa
    ChastePrinter,
)

