# Release 0.5.0
- Now implements lookup tables.

# Release 0.4.1
- Now outputs sqrt(x) instead of pow(x, 0.5).

# Release 0.4.0
- This release explicitly adds versions for dependencies, rather than leaving it up to the cellmlmanip and Jinja2 packages. Versions are semi-strict allowing for minor updates (which should not break compatibility).
- This release contains a bug fix with regards to the stimulus sign, which was calculated incorrectly when the stimulus equation had been changed due to unit conversions.
- The model type displayed in the header of generated files has been fixed and now displays correctly (instead of always displaying 'normal')

# Release 0.3.0
- This release includes the required ontology ttl files in the release itself.
- Removed test data from release package to save space.

# Release 0.2.0
- The command line interface now allows generating multiple model types in one go.
- The command line interface now has a --show-outputs option
- Some command line argument names have changed to more closely match what pycml used to use, command line arguments are not backwards compatible with release 0.1.0
- An issue with generating modifiers that are also parameters has been fixed, by generating the modifier in situ if it doesn't have a defining equation.
- An issue with GetIIonic where the sign of the equations was incorrect has been fixed by analysing the equation before any unit conversion has taken place.

# Release 0.1.0
Initial release of chaste_codegen
