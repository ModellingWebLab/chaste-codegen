import fccodegen
import jinja2
import os


def load_template(*name):
    """
    Returns a path to the given template
    """
    path = os.path.join(fccodegen.DIR_TEMPLATE, *name)
    #TODO: Check absolute path is still in DIR_TEMPLATE
    #TODO: Check exists
    #TODO: Look at the jinja PackageLoader. What's the advantage?
    with open(path, 'r') as f:
        return jinja2.Template(f.read())


def create_weblab_model(model, path):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.pyx`` model for use
    with the Web Lab, and stores it at ``path``.
    """
    from cellmlmanip import parser    
    
    template = load_template('wl', 'weblab_model.pyx')
    with open(path, 'w') as f:
        f.write(template.render())

