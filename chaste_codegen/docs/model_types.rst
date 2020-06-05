************************************************
Creating different types of chaste code export
************************************************

.. currentmodule:: chaste_codegen

To create a type of chaste model, provide appropriate Jinja2 templates in /templates, extend :class:`chaste_codegen.ChasteModel` and set the following in :func:`chaste_codegen.ChasteModel`

`self._hpp_template = '<template_name>'`

`self._cpp_template = '<template_name>'`


