[![travis](https://travis-ci.com/ModellingWebLab/chaste-codegen.svg?branch=master)](https://travis-ci.com/ModellingWebLab/chaste-codegen)
[![codecov](https://codecov.io/gh/ModellingWebLab/chaste-codegen/branch/master/graph/badge.svg)](https://codecov.io/gh/ModellingWebLab/chaste-codegen)

# Code generation for cardiac Chaste

The `chaste_codegen` module takes [cellmlmanip](https://github.com/ModellingWebLab/cellmlmanip) models as input, and uses templating to generate code.

The [jinja2](http://jinja.pocoo.org/) templating engine is used.

## Installing 
We reccomend installing chaste_codegen in a vritual environment (using virtualenv or conda)

Users install `chaste_codegen` using pip.

```
pip install chaste_codegen
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

## Release notes
For release notes see [RELEASE.md](./RELEASE.md)


## Documentation
API documentation explaining how to use cellmlmanip can be found on [readthedocs](https://chaste_codegen.readthedocs.io/en/latest)


## Contributing
For guidelines on contributing to `chaste_codegen`, please see [CONTRIBUTING.md](CONTRIBUTING.md).
