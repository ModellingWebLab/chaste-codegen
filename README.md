[![travis](https://travis-ci.com/ModellingWebLab/chaste-codegen.svg?branch=master)](https://travis-ci.com/ModellingWebLab/chaste-codegen)
[![codecov](https://codecov.io/gh/ModellingWebLab/chaste-codegen/branch/master/graph/badge.svg)](https://codecov.io/gh/ModellingWebLab/chaste-codegen)

# Code generation for cardiac Chaste

The `chaste_codegen` module takes [cellmlmanip](https://github.com/ModellingWebLab/cellmlmanip) models as input, and uses templating to generate code.

The [jinja2](http://jinja.pocoo.org/) templating engine is used.

## Installing 
We reccomend installing chaste_codegen in a vritualenvironment (or using conda)

Users install `chaste_codegen` using pip.

```
pip install chaste_codegen
```

To install chaste_codegen from GitHub source, first clone SymPy using git:

```
$ git clone https://github.com/sympy/sympy.git
```
Then, in the sympy repository that you cloned, simply run:

```
$ python setup.py install
```

## Using `chaste_codegen`
After installation, chaste_codegen can be called using the `chaste_codegen` command:
```
usage: chaste_codegen [-h] [--version] [-t TYPE] [-o OUTFILE]
                      [--use-analytic-jacobian] [-c CLASS_NAME] [-y]
                      [--use-modifiers]
                      cellml_file
```

For more information about the available options call
`chaste_codegen -h`

## Contributing

For guidelines on contributing to `chaste_codegen`, please see [CONTRIBUTING.md](CONTRIBUTING.md).
