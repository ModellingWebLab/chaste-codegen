# CodegenRefCheck

The rest of chaste_codegen's test suite checks generated model code textually
against the frozen reference files under `chaste_codegen/data/tests/chaste_reference_models/`.
When a sympy/Python version renders a model differently, a version-suffixed variant file
(e.g. `--sympy_1_14.cpp`) is added alongside the default file, on the assumption that the new
rendering is mathematically equivalent to before. This needs to be verified numerically.

This suite compiles every reference model variant as a real Chaste `heart`
class, simulates it, and numerically compares the result to the corresponding
baseline model (a **fixed snapshot**) which is a stable basis to compare against.
A fixed snapshot is used as the baseline so that it does not silently drift when
new commits are merged in. If the baseline ever needs to be shifted forward,
`freeze_baseline.py --force` can be used to make a new snapshot into `baseline/`.

This is a quick numerical check that supplements the `TestCodegenLong` Chaste
tests that perform more rigorous end-to-end testing.

## Building and running the tests
`CodegenRefCheck` is a small Chaste user project. It contains `TestRefCheckCompareAll.hpp`
which reads the manifest the harness generator creates on the fly (`test/RefCheckManifest.hpp`)
and numerically diffs each variant's `.dat` against its baseline via Chaste's existing
`CompareCellModelResults` helper (`heart/src/fortests/RunAndCheckIonicModels.hpp`).

`generate_refcheck_harness.py` is the test harness generator. For every
(scheme, model, variant) tuple, it creates **one standalone Chaste project** in
`<CHASTE_SOURCE_DIR>/projects/RefCheck_<scheme>_<model>_<variant>/`
(`variant` is `Baseline`, `Default`, `Sympy111`, `Python311`, etc.), each holding
one variant consisting of a generated `src/<header>.hpp/.cpp` pair and a
generated CxxTest runner that constructs a cell, runs it, and writes a `.dat` file.
Every tuple gets its *own* project to avoid name collisions. If you want to inspect
what was generated, review the resulting content under `<CHASTE_SOURCE_DIR>/projects/RefCheck_*`.
Check `<CHASTE_SOURCE_DIR>/projects/CodegenRefCheck/generated_manifest.md` for
what was generated or skipped.

To build and run this suite, checkout Chaste, point `CHASTE_SOURCE_DIR` at it,
build the `heart` module, and run `run_all.sh` to regenerate → configure → build → test,
end to end.

```sh
CHASTE_SOURCE_DIR=/path/to/Chaste ./run_all.sh
```

`TestRefCheckCompareAll`'s output prints one PASS/FAIL/NO-BASELINE/ERROR
line per (scheme, model, variant) tuple plus a totals line. ERROR means a `.dat`
file was missing (e.g. a CVODE-only model on a build without `CHASTE_CVODE`,
or a reference `.cpp` failed to compile) rather than a genuine numerical mismatch.
