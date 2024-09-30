#
# Chaste codegen setuptools script
#
import os

from setuptools import find_packages, setup


# Load text for description
with open('README.md') as f:
    readme = f.read()

# Load version number
with open(os.path.join('chaste_codegen', 'version.txt'), 'r') as f:
    version = f.read()

# Go!
setup(
    # Module name (lowercase)
    name='chaste_codegen',

    version=version,
    description='Code generation for cardiac Chaste',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Maurice Hendrix, Michael Clerx, Jonathan Cooper',
    author_email='Maurice.Hendrix@nottingham.ac.uk',
    maintainer='Maurice Hendrix',
    maintainer_email='Maurice.Hendrix@nottingham.ac.uk',
    url='https://github.com/ModellingWebLab/chaste-codegen',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],

    # Packages to include
    packages=find_packages(
        include=('chaste_codegen', 'chaste_codegen.*')),

    # Include non-python files (via MANIFEST.in)
    include_package_data=True,

    # Required Python version
    python_requires='>=3.6',

    # List of dependencies
    install_requires=[
        'py>=1.10.0',
        'decorator>=4.4.2, <6',
        'importlib-metadata>=1.7, <8',
        'isodate>=0.6.0, <1',
        'lxml>=4.6.5, <6',
        'MarkupSafe>=1.1.1, <3',
        'mpmath>=1.1.0, <2',
        'networkx>=2.4, <4',
        'packaging>=20.4, <24',
        'Pint>=0.9, <0.30',
        'pyparsing>=2.4.7, <4',
        'rdflib>=5.0.0, <8',
        'six>=1.15.0, <2',
        'sympy>=1.9, <1.11',
        'zipp>=1.2.0, <4',
        'Jinja2>=3.0.0, <4',
        'cellmlmanip>=0.3.6, <0.4',
    ],
    extras_require={
        'docs': [
            'sphinx>=3.0',
            'sphinx-automodapi>=0.12',
        ],
        'test': [
            'pytest-cov>=2.10',     # For coverage checking
            'pytest>=4.6',          # For unit tests
            'flake8>=3',            # For code style checking
            'isort',
            'mock>=3.0.5',         # For mocking command line args etc.
        ],
    },
    entry_points={
        'console_scripts': [
            'chaste_codegen='
            'chaste_codegen._command_line_script:chaste_codegen',
        ],
    },
)
