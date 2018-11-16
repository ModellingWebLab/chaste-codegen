#
# fccodegen setuptools script
#
import os
from setuptools import setup, find_packages

# Load text for description
with open('README.md') as f:
    readme = f.read()

# Load version number
with open(os.path.join('fccodegen', 'version.txt'), 'r') as f:
    version = f.read()

# Go!
setup(
    # Module name (lowercase)
    name='fccodegen',

    # Remember to keep this in sync with fccodegen/__init__.py
    version='0.0.1',

    description='Code generation for the Web Lab',
    long_description=readme,
    license='BSD 3-clause license',
    # author='',
    # author_email='',
    maintainer='Web Lab team',
    maintainer_email='michael.clerx@cs.ox.ac.uk',
    url='https://github.com/ModellingWebLab/fccodegen',

    # Packages to include
    packages=find_packages(include=('fccodegen', 'fccodegen.*')),

    # Include non-python files (via MANIFEST.in)
    include_package_data=True,

    # List of dependencies
    install_requires=[
        'Jinja2>=2.10',
    ],
    extras_require={
        'test': [
            'pytest>=3',            # For unit tests
            'pytest-cov>=2.5',      # For coverage checking
            'flake8>=3',            # For code style checking
        ],
    },
)

