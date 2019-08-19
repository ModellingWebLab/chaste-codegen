#
# Functions related to generating model code.
# TODO: Find a better name/description/layout
#
import jinja2
import logging
import os
import posixpath
import sympy as sp
import time
import weblab_cg as cg

 
def create_chaste_model(path, class_name, model, parameters):
    """
    Takes a :class:`cellmlmanip.Model`, generates a ``.cpp`` and ``.cpp`` model 
    for use with Chaste, and stores it at ``path``.

    Arguments

    ``path``
        The path to store the generated model code at. (Just the path, excluding the file name as file name will be determined by the class_name)
    ``class_name``
        A name for the generated class.
    ``model``
        A :class:`cellmlmanip.Model` object.
    ``parameters``
        An ordered list of annotations ``(namespace_uri, local_name)`` for the
        variables to use as model parameters. All variables used as parameters
        must be literal constants.

    """
    # First steps to generate files with the correct file name.
    path = os.path.join(path, class_name+".cpp")
    print(path)
    outputs = []
