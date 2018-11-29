"""
Main module for Web Lab code generation
"""


#
# Load constants and version information
#
from ._config import (   # noqa
    DIR_DATA,
    DIR_ROOT,
    DIR_TEMPLATE,
    VERSION,
    VERSION_INT,
    version,
)


#
# Load main classes and functions
#
from ._generator import (   # noqa
    create_weblab_model,
    get_equations,
    load_model,
    load_template,
)

from ._printer import (     # noqa
    WebLabPrinter,
)

