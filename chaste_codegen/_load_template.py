#
# Methods to configure jinja2 and load templates.
#
import logging
import os
import posixpath
import re

import jinja2

import chaste_codegen as cg


def regex_replace(s, find, replace):
    """Regex replace that skips // and /* */ comments."""
    if s is None:
        return s

    out = []
    in_block_comment = False

    lines = s.splitlines(keepends=True)
    for line in lines:
        i = 0
        result = ''

        while i < len(line):
            if in_block_comment:
                end = line.find('*/', i)
                if end == -1:
                    # whole line is inside block comment
                    result += line[i:]
                    i = len(line)
                else:
                    # exit block comment
                    result += line[i:end+2]
                    i = end + 2
                    in_block_comment = False
            else:
                # look for comment starts
                line_comment = line.find('//', i)
                block_comment = line.find('/*', i)

                # choose nearest comment start
                candidates = [p for p in [line_comment, block_comment] if p != -1]
                if not candidates:
                    # pure code
                    result += re.sub(find, replace, line[i:])
                    i = len(line)
                else:
                    next_comment = min(candidates)
                    # process code before comment
                    result += re.sub(find, replace, line[i:next_comment])
                    i = next_comment

                    if next_comment == line_comment:
                        # rest of line is // comment
                        result += line[i:]
                        i = len(line)
                    else:
                        # enter /* */ block
                        end = line.find('*/', i+2)
                        if end == -1:
                            result += line[i:]
                            i = len(line)
                            in_block_comment = True
                        else:
                            result += line[i:end+2]
                            i = end + 2

        out.append(result)

    return ''.join(out)


# Shared Jinja environment
_environment = None


def _jinja_environment():
    """
    Returns a shared Jinja environment to create templates from.
    """
    global _environment
    if _environment is None:
        _environment = jinja2.Environment(
            # Automatic loading of templates stored in the module
            # This also enables template inheritance
            loader=jinja2.PackageLoader('chaste_codegen', cg.TEMPLATE_SUBDIR),

            # Keep a single trailing newline, if present
            keep_trailing_newline=True,

            # Don't replace undefined template variables by an empty string
            # but raise a jinja2.UndefinedError instead.
            undefined=jinja2.StrictUndefined,
        )

        # register the filter
        _environment.filters['regex_replace'] = regex_replace
    return _environment


def load_template(*name):
    """
    Loads a template from the local template directory.

    Templates can be specified as a single filename, e.g.
    ``load_template('temp.txt')``, or loaded from subdirectories using e.g.
    ``load_template('subdir_1', 'subdir_2', 'file.txt')``.

    """
    # Due to a Jinja2 convention, posixpaths must be used, regardless of the
    # user's operating system!
    path = posixpath.join(*name)
    if os.path.sep != '/' and os.path.sep in path:  # pragma: no linux cover
        log = logging.getLogger()
        log.warning('Paths to templates must be specified as posix paths.')

    env = _jinja_environment()
    return env.get_template(path)
