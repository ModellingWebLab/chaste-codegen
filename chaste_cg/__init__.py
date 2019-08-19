"""
Main module for Web Lab code generation
"""

# Configure logging
import logging
logging.basicConfig()
del(logging)


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

from ._printer import (     # noqa
    WebLabPrinter,
)

