 
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
    # TODO: Jon's comment on the outputs/parameters being annotations:
    # IIRC the pycml code basically says you can use anything that's a valid
    # input to create_rdf_node. So we might eventually want to avoid all the
    # *parameter unpacking when passing around, but I don't think it's urgent.

    # TODO: About the outputs:
    # WL1 uses just the local names here, without the base URI part. What we
    # should do eventually is update the ModelWrapperEnvironment so we can use
    # a separate instance for each namespace defined by the protocol, and then
    # we can use longer names here and let each environment wrap its respective
    # subset. But until that happens, users just have to make sure not to use
    # the same local name in different namespaces.
    print ("bla")