"""
Constants and version information.
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

# Directory for any other data
DIR_DATA = os.path.join(DIR_ROOT, 'data')


#
# Version info
#
with open(os.path.join(DIR_ROOT, 'version.txt'), 'r') as f:
    VERSION_INT = tuple([int(x) for x in f.read().split('.', 3)])
VERSION = '.'.join([str(x) for x in VERSION_INT])


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
