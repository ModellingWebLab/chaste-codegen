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

### Python version

Python 3.5+


## Testing

We're using [pytest](https://docs.pytest.org/en/latest/). To run, type

```sh
$ python -m pytest
```


## Documentation

Every method and every class should have a [docstring](https://www.python.org/dev/peps/pep-0257/) that describes in plain terms what it does, and what the expected input and output is.

These docstrings can be fairly simple, but can also make use of [reStructuredText](http://docutils.sourceforge.net/docs/user/rst/quickref.html), a markup language designed specifically for writing [technical documentation](https://en.wikipedia.org/wiki/ReStructuredText). For example, you can link to other classes and methods by writing ```:class:`myokit.Model` ``` and  ```:meth:`run()` ```.


## Infrastructure & configuration files

### Visual Studio Code Development Environment
Visual Studio Code (not to be confused with Visual Studio) is a cross-platform free lightweight IDE from Microsoft.
To use it for ``chaste_codegen`` development you will need to install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python).
To be able to run and debug tests you will also need to install the [pytest extension](https://code.visualstudio.com/docs/python/testing).
In your settings you should also make it use the correct vritual environment. This can be done via the UI but it is a bit hit and miss. 
However there is a settings file in the `.vscode` folder in the ``chaste_codegen`` folder called `settings.json`. Note that `.vscode` is included in our `.gitignore` so any changes will not be tracked or committed.
Below is an example `settings.json`; replace `<python_path>` with the folder that contains `python.exe` for your virtual environment (in Windows it is in `\Scripts` and on linux in `/bin `).
`<project_path>` is just the root folder of the ``chaste_codegen`` code.
```
{
    "python.pythonPath" : "<python_path>",
    "python.venvPath": "${workspaceFolder}",
    "python.venvFolders": [
        "<project_path>"
    ],

    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["--rootdir=.", "--verbose"]
}
```
