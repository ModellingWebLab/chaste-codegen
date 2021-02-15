[![travis](https://travis-ci.com/ModellingWebLab/chaste-codegen.svg?branch=master)](https://travis-ci.com/ModellingWebLab/chaste-codegen) [![Documentation Status](https://readthedocs.org/projects/chaste-codegen/badge/?version=latest)](https://chaste-codegen.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/ModellingWebLab/chaste-codegen/branch/master/graph/badge.svg)](https://codecov.io/gh/ModellingWebLab/chaste-codegen)

# Code generation for cardiac Chaste

The `chaste_codegen` module takes [CellML](https://www.cellml.org/) models as input, via [cellmlmanip](https://github.com/ModellingWebLab/cellmlmanip) to read and manipulate them, then uses templating to generate C++ code.

The [jinja2](http://jinja.pocoo.org/) templating engine is used.

## Installing 
We recommend installing chaste_codegen in a virtual environment (using virtualenv or conda)

Users install `chaste_codegen` using pip.

```
pip install chaste_codegen
```

## Using `chaste_codegen`
After installation, chaste_codegen can be called using the `chaste_codegen` command:
```
usage: chaste_codegen [-h] [--version] [--normal] [--cvode] [--cvode-data-clamp] [--backward-euler] [--rush-larsen]
                      [--grl1] [--grl2] [-j] [-o OUTFILE] [--output-dir OUTPUT_DIR] [--show-outputs] [-c CLS_NAME]
                      [-q] [--skip-ingularity-fixes] [-y] [--opt] [-m] [--lookup-table <metadata tag> min max step]
                      cellml_file
chaste_codegen: error: the following arguments are required: cellml_file
```

For more information about the available options call
`chaste_codegen -h` or see the [CodeGenerationFromCellML guide](https://chaste.cs.ox.ac.uk/trac/wiki/ChasteGuides/CodeGenerationFromCellML) 


## Release notes
For release notes see [RELEASE.md](./RELEASE.md)


## Documentation
API documentation explaining how to use cellmlmanip can be found on [readthedocs](https://chaste-codegen.readthedocs.io/en/latest/)


## Contributing
For guidelines on contributing to `chaste_codegen`, please see [CONTRIBUTING.md](CONTRIBUTING.md).
