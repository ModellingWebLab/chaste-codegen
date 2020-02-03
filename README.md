[![travis](https://travis-ci.com/ModellingWebLab/chaste-codegen.svg?branch=master)](https://travis-ci.com/ModellingWebLab/chaste-codegen)
[![codecov](https://codecov.io/gh/ModellingWebLab/chaste-codegen/branch/master/graph/badge.svg)](https://codecov.io/gh/ModellingWebLab/chaste-codegen)

# Code generation for cardiac Chaste

The `chaste_codegen` module takes [cellmlmanip](https://github.com/ModellingWebLab/cellmlmanip) models as input, and uses templates and `printers` to generate code.

A [printer](https://docs.sympy.org/latest/tutorial/printing.html) is an object that can convert Sympy equations (as used in `cellmlmanip`) to string equations.
The [jinja2](http://jinja.pocoo.org/) templating engine is used.


## Installing 

Currently, there is no 'user' way of installing.
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for the developer installation instructions.

## Using `chaste_codegen`

To generate code for the Web Lab:

```
# Select a path to write the output to
path = 'model.pyx'

# Select a name for the generated model class
class_name = 'TestModel'

# Load a CellML model using cellmlmanip
model = cellmlmanip.load_model(
    'hodgkin_huxley_squid_axon_model_1952_modified.cellml')

# Select the variables to track as model outputs
oxmeta = 'https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#'
outputs = [
    (oxmeta, 'membrane_fast_sodium_current'),
    (oxmeta, 'membrane_voltage'),
    (oxmeta, 'time'),
    'state_variable',
]
# Here, `state_variable` is a special name that returns an array of all states

# Select the variables to use as model parameters
parameters = [
    (oxmeta, 'membrane_fast_sodium_current_conductance'),
    (oxmeta, 'membrane_potassium_current_conductance'),
]

# Run!
cg.create_weblab_model(path, class_name, model, outputs, parameters)
```

## Extending `chaste_codegen`

To generate models in your own syntax, you'll need the following ingredients:

1. A suitable printer class
2. One or more jinja templates
3. A method to generate unique names for model variables
4. Some code to bring it all together

**Printers**: Start by checking if a suitable printer already exists (see `_printer.py`).
If not, you'll need to create a printer for the language you wish to export to, probably by subclassing or copy-pasting an existing class in `_printer.py`.

**Templates**: These will contain all the static bits of your generated code (e.g. function names, headers), along with some [jinja syntax](http://jinja.pocoo.org/docs/2.10/templates/) specifying where the dynamical bits come in.

**Unique variable names**: See `get_unique_names()` in `_generator.py` for an example of how to generate unique variable names.
It may be possible to use this method directly, or you may need to create your own method.

**Bringing it all together**: See `create_weblab_model()` in `_generator.py` for an example.

**Adding your stuff to `chaste_codegen`**: If you want to include your generator/templates/printers in `chaste_codegen`, please create one or more PRs.
(We'll probably need to update the code layout for this too, at some point!)


## Contributing

For guidelines on contributing to `chaste_codegen`, please see [CONTRIBUTING.md](CONTRIBUTING.md).
