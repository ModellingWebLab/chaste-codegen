[![travis](https://travis-ci.com/ModellingWebLab/chaste-codegen.svg?branch=master)](https://travis-ci.com/ModellingWebLab/chaste-codegen)
[![codecov](https://codecov.io/gh/ModellingWebLab/chaste-codegen/branch/master/graph/badge.svg)](https://codecov.io/gh/ModellingWebLab/chaste-codegen)

# Code generation for cardiac Chaste

The `chaste_codegen` module takes [cellmlmanip](https://github.com/ModellingWebLab/cellmlmanip) models as input, and uses templating to generate code.

The [jinja2](http://jinja.pocoo.org/) templating engine is used.

## Installing 
We reccomend installing chaste_codegen in a vritualenvironment (or using conda)

Users install `chaste_codegen` using pip.

`pip install chaste_codegen`

To install chaste_codegen from GitHub source, first clone SymPy using git:

`$ git clone https://github.com/sympy/sympy.git`
Then, in the sympy repository that you cloned, simply run:

`$ python setup.py install`

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

### Git setup
The tests contain a large amount of reference files. When reference files are updated it's a common practice to regenerate them all and (after testing with chaste). Often only a few will have changes.
In order to hide reference files for which only the timestamps have changed, please set up your git environment as follows.
```
git config --global filter.strip_gen_time.clean "sed 's;^//! on .*;//! on (date omitted as unimportant);'"
git config --global filter.strip_gen_time.smudge cat
```
See https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes#_keyword_expansion for full details.
If you are on windows you may need to install sed for windows and add it to your path: http://gnuwin32.sourceforge.net/packages/sed.htm
