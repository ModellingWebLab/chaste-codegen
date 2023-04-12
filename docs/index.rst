.. Root of all chaste_codegen docs

.. _GitHub: https://github.com/ModellingWebLab/chaste-codegen


Welcome to the chaste_codegen documentation
===========================================

chaste_codegen is hosted on GitHub_, where you can find the code and installation instructions.

This page provides the *API*, or *developer documentation* for ``chaste_codegen``.

Updating Sympy or other python packages
=================
Sympy or any other python package may need to be updated, especially as python versions evolve. To update the version:
- change the version listed in setup.py, e.g. for sympy it currently lists 'sympy>=1.9, <1.11', which means that the version is at least 1.9 and is less than 1.11.
- update dev-requirements/dev.txt if you want to also update your development pinned (fixed) versions
- create a new branch `git checkout -b <name_of_new_branc>`
- `git add`, `git commit` and `git push` the changes
- make a pull request. The tests may throw up some errors that may need fixing. The tests are in the tests folder and the reference data in data/tests. In data/tests/chaste_reference_models you'll see a few reference files ending in .cpp_python36, This is as due to sympy versions supported python 3.6 leads to an equivalent but subtly different generated model.
- Mention the changes made in the release notes `release.txt`
- To use the changes with chaste, do a new release of chaste_codegen.


Updating the ontology and including it in chaste_codegen
=================
- update the ontology according to the instructions in https://github.com/ModellingWebLab/ontologies
- the ontology is included in chaste_codegen via a submodule, update this with `git submodule update chaste_codegen/ontologies --remote`. 
- *Please note* this same way can be used to update the `cellml` in `chaste_codegen/data/tests/cellml` submodule if required.
- create a new branch `git checkout -b <name_of_new_branc>`
- `git add`, `git commit` and `git push` the changes
- make a pull run the tests and fix any issues that arise
- update the release notes `release.txt` with information about the updated ontology.
- To use the changes with chaste, do a new release of chaste_codegen.


Doing a new chaste_codegen release
=================
- Update the release version number in `chaste_codegen/version.txt`.
- Update the release notes `release.txt` with the latest release number.
- For this version number: minor numbers will e picked up by chaste automatically, for major version numbers, `chaste_codegene.txt` will need updating in the chaste repository.
- Follow the following tutorial to publish the package: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- You will need a login to pypi.org and the account you are using will need access to chaste_codegen.

API documentation
=================
.. automodapi:: chaste_codegen
   :no-inheritance-diagram:
 