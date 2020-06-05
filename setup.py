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

# Load license
with open('LICENSE') as f:
    license_ = f.read()

# Go!
setup(
    # Module name (lowercase)
    name='chaste_codegen',

    version=version,
    description='Code generation for cardiac Chaste',
    long_description=readme,
    long_description_content_type="text/markdown",
    license=license_,
    author='Maurice Hendrix',
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
    python_requires='>=3.5',

    # List of dependencies
    install_requires=[
        # cellmlmanip                # Add this in when cellmlmanip is ready
        'Jinja2>=2.11',
    ],
    extras_require={
        'test': [
            'pytest>=3.9',          # For unit tests
            'pytest-cov>=2.5',      # For coverage checking
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
