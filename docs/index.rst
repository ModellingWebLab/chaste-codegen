.. Root of all chaste_codegen docs

.. _GitHub: https://github.com/ModellingWebLab/chaste-codegen


Welcome to the chaste_codegen documentation
===========================================

chaste_codegen is hosted on GitHub_, where you can find the code and installation instructions.

Updating Sympy or other python packages
=================
Sympy or any other python package may need to be updated, especially as python versions evolve. To update the version:

- Change the version listed in setup.py, e.g. for sympy it may list 'sympy>=1.10, <1.15', which means that the version is at least 1.10 and is less than 1.15.
- Update dev-requirements/dev.txt if you want to also update your development pinned (fixed) versions
- Create a new branch ``git checkout -b <name_of_new_branch>``
- ``git add``, ``git commit`` and ``git push`` the changes
- Make a pull request. The tests may throw up some errors that may need fixing. The tests are in the tests folder and the reference data in data/tests.
- Sympy occasionally changes the exact (but mathematically equivalent) form of the generated code between versions.
   To cope with this, a reference file may have per-sympy-version variants named ``<name>--sympy_X_Y.<ext>`` (e.g. ``<model>--sympy_1_13.cpp``) alongside the base file.
   To regenerate the reference data for a new sympy version, run the tests with the ``CHASTE_CODEGEN_REGENERATE_REFERENCES`` environment variable set (this writes the generated output to ``<reference>.regen.<X>.<Y>`` files).
- Mention the changes made in the release notes ``RELEASE.md``
- To use the changes with chaste, do a new release of chaste_codegen.


Updating the ontology and including it in chaste_codegen
=================
- Update the ontology according to the instructions in https://github.com/ModellingWebLab/ontologies
- The ontology is included in chaste_codegen via a submodule, update this with ``git submodule update --remote chaste_codegen/ontologies``. 
- *Please note* this same way can be used to update the ``cellml`` in ``chaste_codegen/data/tests/cellml`` submodule if required.
- Create a new branch ``git checkout -b <name_of_new_branch>``
- ``git add``, ``git commit`` and ``git push`` the changes
- Make a pull request, run the tests and fix any issues that arise
- Update the release notes ``RELEASE.md`` with information about the updated ontology.
- To use the changes with chaste, do a new release of chaste_codegen.


Doing a new chaste_codegen release
=================
- Update the release version number in ``chaste_codegen/version.txt``.
- Update the release notes ``RELEASE.md`` with the latest release number.
- For this version number: minor numbers will be picked up by chaste automatically, for major version numbers, ``chaste_codegen.txt`` will need updating in the chaste repository.
- Follow the following tutorial to publish the package: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- You will need a login to pypi.org and the account you are using will need access to chaste_codegen.

API documentation
=================
.. automodapi:: chaste_codegen
   :no-inheritance-diagram:
 
