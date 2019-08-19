"""
Constants and version information.
"""

#
# Get package location, find template directory
#
import os, inspect  # noqa
try:
    frame = inspect.currentframe()
    MODULE_DIR = os.path.dirname(inspect.getfile(frame))
finally:
    # Always manually delete frame
    # https://docs.python.org/2/library/inspect.html#the-interpreter-stack
    del(frame)

# Template sub-directory
TEMPLATE_SUBDIR = os.path.join('templates')

# Directory for any other data
DATA_DIR = os.path.join(MODULE_DIR, 'data')


#
# Version info
#
with open(os.path.join(MODULE_DIR, 'version.txt'), 'r') as f:
    __version_int__ = tuple([int(x) for x in f.read().split('.', 3)])
__version__ = '.'.join([str(x) for x in __version_int__])


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
        return 'weblab_cg ' + __version__
    else:
        return __version_int__