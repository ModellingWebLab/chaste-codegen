"""
Main module for Web Lab code generation
"""


#
# Get package location, find template directory
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
del(inspect)    # Don't expose as part of codegen


#
# Version info
#
with open(os.path.join(DIR_ROOT, 'version.txt'), 'r') as f:
    VERSION_INT = tuple([int(x) for x in f.read().split('.', 3)])
VERSION = '.'.join([str(x) for x in VERSION_INT])
del(os)


#
# Expose version number
#
def version(formatted=False):
    """
    Returns the version number, as a 3-part integer (major, minor, revision).
    If ``formatted=True``, it returns a string formatted version (e.g.
    "codegen 1.0.0").
    """
    if formatted:
        return 'fccodegen ' + VERSION
    else:
        return VERSION_INT


#
# Load main classes and functions
#
from ._generator import (   # noqa
    create_weblab_model,
    load_template,
)

