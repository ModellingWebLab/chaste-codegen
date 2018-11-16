"""
Main module for Web Lab code generation
"""
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals


#
# Version info: Remember to keep this in sync with setup.py!
#
import sys
VERSION_INT = 0, 0, 1
VERSION = '.'.join([str(x) for x in VERSION_INT])
if sys.version_info[0] < 3:     # pragma: no python 3 cover
    del(x)  # Before Python3, list comprehension iterators leaked
del(sys)


#
# Expose version number
#
def version(formatted=False):
    """
    Returns the version number, as a 3-part integer (major, minor, revision).
    If ``formatedd=True``, it returns a string formatted version (e.g.
    "codegen 1.0.0").
    """
    if formatted:
        return 'fccodegen ' + VERSION
    else:
        return VERSION_INT


#
# Data directory
#
import os, inspect  # noqa
try:
    frame = inspect.currentframe()
    DIR_ROOT = os.path.dirname(inspect.getfile(frame))
finally:
    # Always manually delete frame
    # https://docs.python.org/2/library/inspect.html#the-interpreter-stack
    del(frame)

# Template directory
DIR_TEMPLATE = os.path.join(DIR_ROOT, 'templates')
del(os, inspect)    # Don't expose as part of codegen


#
# Load main classes and functions
#
from ._generator import (   # noqa
    create_weblab_model,
    load_template,
)

