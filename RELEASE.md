# (unreleased)
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
