# Release 0.9.10
- Added support for Sundials 6.0.0 which requires a newly introduced SUNContext object. This version of chaste_codegen now generates code that will work with Sundails 6.0, but is backwards compatible with previous sundails version and the 2021 release of chaste.

# Release 0.9.9
- Fixed an issue with unused variables appearing in common terms in jacobians.
- Fixes a bug printing large integers, in some environments: Large numbers such as 8.034023767017109e+27 which were actually ints would be printed as an the int 8034023767017108950029959168 and then the C++ compiler would complain as that's more than the maximum int value. This has been fixed by only printing ints as ints if they are `MIN_INT < number < MAX_INT` else we print them as a float (and we get the sceintific notation).
- Fixed tests to pass with sympy 1.10 and required latest cellmlmanip, which also works with sympy1.10. Updated sympy requirement to be >=1.9, < 1.11

# Release 0.9.5
- Corrected a type in the generated output for `--rush-larsen-c`
- Updated the help text to no longer imply that CellML files can be converted from remote URIs (a local file is required)
- Fixed required sympy version to be < 1.9 since the jacobean generation has in sympy1.10 changed and makes chaste_codegen tests fail
 
# Release 0.9.4
- This version drops python 3.5 support. The reason for this is python 3.5 is end of life and the chase project will soon be dropping support.
- Corrected Rush-Larsen output for `--rush-larsen-c`

# Release 0.9.3
- Performance upgrade for `--rush-larsen` using caching on linearity checking.

# Release 0.9.2
- Corrected a typo in command line argument `--skip-ingularity-fixes` renaming it to `--skip-singularity-fixes`

# Release 0.9.1
- Added RushLarsen translators for allowing output as c code (`--rush-larsen-c`) and labview (`--rush-larsen-labview`), These are for people wanting to generate generic c or labview code when using chaste_codegen as a stand-alone utility and are not used by chaste

# Release 0.9.0
- Updated to the latest version of the Web Lab Ontology.
- Better error messages when working with transitively finding terms, and encountering subjects that don't point to an existing node in the model.

# Release 0.8.0
- Added `--use-model-factory` flag to allow code to be added for models to self-register to the model factory of the ApPredict peoject.
- Renamed backward euler cells to be in line with others using `BackwardEulerOpt` / `BackwardEuler` instead of `BackwardEuler` and `BackwardEulerNoLot`.

# Release 0.7.0
- The singularities fixing code from release 0.6.3 has moved to the latest cellmlmanip release (0.3.0). You may see small differences in generated code, due to singularities now being fixed prior to any unit conversion taking place. These should not cause any differences in results when run with chaste.
- Improved capacitance unit checking.

# Release 0.6.3
- Fixed issue with backward euler opt models where unused state variables appeard in ComputeResidual
- Fixed memory leek on generated models within lookup table interpolation on nan/inf values in singularities.
- Removed chaste warnings from backward euler template for cases where inf/nan would end up in the table. Intead an error is thrown when multiple (more than 2) such warnings happen.

- Added an automatic fix for removable singularities in GHK equations (which can be switched off with --skip-ingularity-fixes).
  The process looks for equations of any of the following forms, where U is a function of V:
  - `U / (exp(U) - 1.0)`
  - `U / (1.0 - exp(U))`
  - `(exp(U) - 1.0) / U`
  - `(1.0 - exp(U)) / U`  
  It replaces these with a piecewise 1e-7 either side of U==0 drawing a stright line in the region.
  For example `(V + 5)/(exp(V + 5) - 1)` becomes `((fabs(-V - 5.0000000000000000) < fabs(-4.9999999000000000 / 2 - -5.0000001000000000 / 2)) ? ((-5.0000001000000000 + 5.0) / (-1.0 + exp(-5.0000001000000000 + 5.0)) + (--5.0000001000000000 + V) * ((-4.9999999000000000 + 5.0) / (-1.0 + exp(-4.9999999000000000 + 5.0)) - (-5.0000001000000000 + 5.0) / (-1.0 + exp(-5.0000001000000000 + 5.0))) / (--5.0000001000000000 - 4.9999999000000000)) : ((5.0 + V) / (-1.0 + exp(5.0 + V))))`

  See for more details appendix B in: Johnstone, R. H. (2018). Uncertainty characterisation in action potential modelling for cardiac drug safety [PhD thesis]. University of Oxford. https://ora.ox.ac.uk/objects/uuid:0a28829c-828d-4641-bfb0-11193ef47195
- For lookup tables prevented expressions of the form 1 / A from being added, instead adding A. 1 / A type expressions were causing issues, when A is 0. While many cases have a piecewise to prevent hissing this case, lookup table interpolation might cause issues.
- Updated the way BackwardEuler models are calculated, to allow the jacobian to be taken into consideration for lookup tables.
- Fixed a bug with BackwardEuler models where jacobian common term equations (e.g. var_x0) ended up in lookup tables.

# Release 0.5.4
- Fixed sympy deprecation warning when using sympy 1.7 and bumped cellmlmanip recuirement up to ensure sympy 1.7 compatibility
- Improved support for secondary trigonometric functions such as sec and acoth.
- When used with Cellmlmanip version 0.2.2+ an improved printing of devisions is used. For example `1 / (1/cos(x))` now gets rendered as `cos(x)` whereas previously it would be `1 / 1 / cos(x)` giving the incorrect result. An side effcet of the change is that powers of formulas get extra brackets e.g. `pow((1 / x), 2)`.
- chaste_codegen uses placeholder functions for some common maths functions like exp, in order to delay evaluation till the point where the code is written. For programmers using chaste_codegen as a library, there now is a function called `subs_math_func_placeholders` which can be used on any sympy expression to substitute these placeholders.
  E.g.
  ```
  >> expr
  2.0 * exp_(V)
  >> subs_math_func_placeholders(expr)
  2.0 * exp(V)```

# Release 0.5.3
- Added an additional error messages if cellml files can't be loaded and a warning if a lookup table is specified for a tag not present in the model.

# Release 0.5.2
- Error messages have been improved, especially for errors caused by invalid or missing metadata.

# Release 0.5.1
- Corrected usage mentioned in the readme

# Release 0.5.0
- Now implements lookup tables.
- Multiplication equations x * y * y now have 1.0 terms removed in a way that works more generically.

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
