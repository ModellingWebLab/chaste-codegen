# Contributing to Chaste codegen

## Installation

Users install `chaste_codegen` using pip.
For instructions on installing as a user, see [README.md](README.md)

Developers should:

1. Clone the repository
2. Create a virtual environment, using e.g. virtualenv or conda. Make sure to use Python3 (e.g. `$ virtualenv venv -p python3`). (If you are on windows you might need to install virtual env first with `pip install virtualenv`. Make sure your python3 installation is in your path.)
3. Activate the environment (e.g. `$ source venv/bin/activate`). (On Windows, virtualenv creates a batch file to activate the virtualenv: `\path\to\env\Scripts\activate`)
4. Install the developer requirements into the virtual environment: `pip install -r dev-requirements/dev.txt`
5. Run the tests: `$ python -m pytest`.

### Requirements

There are two lists of requirements.

1. User requirements, specified in `setup.py`.
2. Developer requirements, specified in the `dev-requirements` directory.

User requirements specify minimum versions of each dependency, and can be used in an existing Python ecosystem.
Developer requirements specify "pinned" versions of each dependency, and should be installed inside a virtual environment.
Having pinned versions ensures different developers get consistent results.
Continuous integration testing happens with user requirements.

Using a virtualenv for development also helps you notice when requirements are missing from the developer requirements.
Similarly, on CI testing anything not listed in the user requirements will cause the tests to fail.

**User requirements** are listed in `setup.py`.
They are divided into base dependencies (listed in `install_requires`) and `test` dependencies (listed in `extras_require[test]`).
Users install these requirements automatically when they `pip install chaste_codegen`.

**Developer requirements** are listed in `base.in`, `test.in`, and `dev.in` (where `test` requires `base`, while `dev` requires `base` and `test`).
These `.in` files are compiled into `.txt` files for `pip` using [pip-tools](https://pypi.org/project/pip-tools/).
To compile them, use the Makefile in the `dev-requirements` folder, by simply typing `make`.

To install the developer requirements into your virtualenv, make sure you've activated the virtual environment, and then:

```sh
$ pip install -r dev-requirements/dev.txt
```


## Coding style guidelines

We follow the [PEP8 recommendations](https://www.python.org/dev/peps/pep-0008/) for coding style, and use [flake8](http://flake8.pycqa.org/en/latest/) to check our PEP8 adherence. To run, type

```sh
$ flake8
```

## Python version
Python 3.5+

## Documentation

Every method and every class should have a [docstring](https://www.python.org/dev/peps/pep-0257/) that describes in plain terms what it does, and what the expected input and output is.

These docstrings can be fairly simple, but can also make use of [reStructuredText](http://docutils.sourceforge.net/docs/user/rst/quickref.html), a markup language designed specifically for writing [technical documentation](https://en.wikipedia.org/wiki/ReStructuredText). For example, you can link to other classes and methods by writing ```:class:`myokit.Model` ``` and  ```:meth:`run()` ```.

## Testing
Testing happens in 2 different ways: there are python-based tests to test `chaste_codegen` as a stand-alone utility and there is a test pack within the chaste project, which tests that the generated modules produce the numerical results expected (within tolerances)

### python-based tests
We're using [pytest](https://docs.pytest.org/en/latest/). To run, type

```sh
$ python -m pytest
```
### chaste C++ based tests
The Codegen tastpack within chaste will download & install the latest release of chaste_codegen, compile a number of models and check their numericla outcomes. See [chatse wiki](https://chaste.cs.ox.ac.uk/trac/wiki/ChasteGuides/CmakeFirstRun). You can run this test with any changes that have been made as follows:
- You'll need environment in which you can compile chaste (e.g. with the dependancies installed or in a docker).
- Make sure the changes are committed to a new branch e.g. `changed_xyy_to_do_pqr`.
- Check-out chaste. ``git clone --recursive --branch develop https://github.com/Chaste/Chaste.git`
- from the source folder checkout the ApPreict project `git clone --recursive https://github.com/Chaste/ApPredict projects/ApPredict`
- create a build folder and cd in to it. e.g. `mkdir build; cd build`
- Type: `cmake <path to chaste source>`. This sets-up the build folder for compiling chaste.
- There isshould now be a python virtual environment in the build folder called `codegen_python3_venv`
- Uninstall the release of chatse codegen: `./codegen_python3_venv/bin/python -m pip uninstall chaste_codegen`
- Clone the source of chatse_codegen with the changes in your branch follows `git clone --recursive --branch changed_xyy_to_do_pqr https://github.com/ModellingWebLab/chaste-codegen.git`
- Install this version into the virtual environment `./codegen_python3_venv/bin/python -m pip install -e chaste-codegen/`
- You can check it has worked by typing ./codegen_python3_venv/bin/python -m pip freeze` you should see something like `-e git+https://github.com/ModellingWebLab/chaste-codegen.git@e401d52fc584d4cba7330bd1aee3b741269d7084#egg=chaste_codegen` (where e401d52fc584d4cba7330bd1aee3b741269d7084 is a specific git commit id)
- no make your project as normal `make -jN` where N is the number of processes you want to use (depending on the machine you're using)
- Iow test the codegen output. **this will take quite a while** Ctest -JN -L `Codegen ----output-on-failure`
- If this passes, test the ApPreidct project as well: `Ctest -jN -L project_ApPredict  ----output-on-failure`


## Workflow for proposing changes
In order to propose changes to `chaste_codegen` the steps are as follows:
- Make a new branch with your changes
- Make sure it passes all tests locally (run them with pytest, see above) using a virtual environment. Make sure to install the dev requirements as well.
- Make sure you're code formatting is up to scratch using `flake8`
- Make sure you're import odering is up to scratch using 'isort'
- You may need to regenerate quite a few reference models.
- Commit & push your new brach.
- Make a pull request on github, explain what and you have changed using the pull request template that comes up.
- Github will run the python tests with different python versions, check code formatting (flake8) and sorting (isort).
- It will also check code coverage.
- Run chaste tests and ApPredict test with this version as per above and check these tests still pass as expected. If they do, mak a comment in the pull request.
- If all is well and all tests above pass, ask for a code review.

## Release workflow
Once changes are ready to be release the following steps need to be taken, Note this needs publishing rights to the chaste_codgen project on PyPi:
- update `chaste_codegen/version.txt` to the next minor/major version number as appropriate
- add a git tag, with the version number `git tag -a <version number> -m "release <version_number>"`
- Follow the [PyPi guide for generating distribution archives](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives)
