#!/usr/bin/env python3
"""Materialises a Chaste-side numerical cross-check harness from this repo's own
reference-model corpus (chaste_codegen/data/tests/chaste_reference_models/).

For every (scheme, model) pair found in the currently checked-out branch, and for every "variant"
rendering of it (the unsuffixed "default" file, plus any --sympy_X_Y / --python_X_Y variant
present, plus the fixed baseline/ snapshot of chaste-codegen's master branch - see below), this
generates one standalone Chaste project under <CHASTE_SOURCE_DIR>/projects/RefCheck_<scheme>_<model>_<variant>/,
containing:
  - the reference .hpp/.cpp for that one (scheme, model, variant) tuple, copied verbatim;
  - one CxxTest runner that constructs the generated cell, runs it, and writes a .dat file into
    a shared per-(scheme,model) output folder.

Each tuple gets its own project (rather than grouping several into one shared library) because
chaste_codegen reuses global names across unrelated files in ways that collide if linked
together: every dynamically-loadable ("dynamic_"-prefixed) model defines an identical global
`MakeCardiacCell` factory function regardless of which model/scheme it is, and some scheme
pairs (e.g. Cvode vs. Cvode_with_jacobian) reuse the exact same generated class name for the
same model. One project per tuple sidesteps every such collision by construction, at the cost
of many small projects rather than few large ones.

This script does not build/run anything itself - it materialises a Chaste project tree into
CHASTE_SOURCE_DIR (env var, defaulting to a sibling ../Chaste checkout). See run_all.sh for the
full generate -> configure -> build -> test sequence, or README.md for the manual steps.

CodegenRefCheck/ (staged verbatim into <CHASTE_SOURCE_DIR>/projects/CodegenRefCheck/
on every run - see stage_compare_project_template()) has no generated cell code of its own; its
hand-written test/TestRefCheckCompareAll.hpp reads the manifest this script also generates
(test/RefCheckManifest.hpp) and numerically diffs every variant's .dat against its model's baseline via
Chaste's existing CompareCellModelResults helper.

The baseline itself is deliberately NOT read live from git here. It comes from a one-time,
explicit snapshot (see freeze_baseline.py) checked into baseline/, so that the comparison basis
stays fixed even if this repo's master branch gets new commits later. Run freeze_baseline.py
once before the first use of this script; this script will refuse to run if that snapshot
doesn't exist yet.
"""

import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

NUMERICAL_CHECK_DIR = Path(__file__).resolve().parent
REPO_ROOT = NUMERICAL_CHECK_DIR.parent.parent.parent
REFS_DIR = REPO_ROOT / "chaste_codegen" / "data" / "tests" / "chaste_reference_models"
# Fixed, frozen snapshot of the baseline reference-model corpus (this repo's master branch) -
# see freeze_baseline.py. Never read live from git; that script is the only place baseline
# content is ever fetched.
BASELINE_DIR = NUMERICAL_CHECK_DIR / "baseline"
COMPARE_PROJECT_TEMPLATE_DIR = NUMERICAL_CHECK_DIR / "CodegenRefCheck"

CHASTE_SOURCE_DIR = Path(
    os.environ.get("CHASTE_SOURCE_DIR", str(REPO_ROOT.parent / "Chaste"))
).resolve()
PROJECTS_DIR = CHASTE_SOURCE_DIR / "projects"
COMPARE_PROJECT = "CodegenRefCheck"
PROJECT_PREFIX = "RefCheck_"  # every generated per-tuple project directory starts with this

# Explicit allow-list: RL_C (plain C) and RL_labview (LabVIEW text) are not Chaste-compatible
# C++ and are excluded by construction, not by accident of globbing.
SCHEMES = [
    "Normal", "Opt", "BE", "BEopt",
    "Cvode", "Cvode_opt", "Cvode_with_jacobian", "Cvode_opt_with_jacobian",
    "CVODE_DATA_CLAMP", "CVODE_DATA_CLAMP_OPT",
    "GRL1", "GRL1Opt", "GRL2", "GRL2Opt",
    "RL", "RLopt",
]

# A "variant" identifies *which rendering* of a given (scheme, model) is being tested - the
# unsuffixed "default" file, the frozen "baseline" snapshot, or one of the version-suffixed
# variants below. Its raw string form (the dict keys here) is what's threaded through as the
# generated .dat file's basename and the manifest's `variant` field (see manifest_entries and
# RefCheckEntry below) - it reaches the compare test unchanged. VARIANT_TO_SHORT only maps it to a
# CamelCase display form for use inside identifiers (project/directory names), since raw forms
# like "sympy_1_14" don't read well embedded in a name; nothing downstream of project naming
# ever sees this short form.
VARIANT_TO_SHORT = {
    "default": "Default",
    "sympy_1_11": "Sympy111",
    "sympy_1_13": "Sympy113",
    "sympy_1_14": "Sympy114",
    "python_3_11": "Python311",
    "baseline": "Baseline",
}

# Synthetic fixtures chaste_codegen uses to test one specific codegen feature (piecewise
# handling, non-state-variable voltage, etc.) rather than real cardiac models. Not meaningful to
# numerically cross-check, and some trip Chaste's -Werror warnings that chaste_codegen's own
# (compile-free) test suite never exercises - out of scope for this harness.
MODEL_NAME_PREFIXES_TO_SKIP = ("test_",)

# (scheme, model) groups whose reference .cpp/.hpp were written against a Chaste heart API
# shape that has since changed, and so fail to compile against current headers regardless of
# which variant is used (verified individually before adding here - see the comment on
# each). Excluded up front rather than discovering it as an opaque compile failure at build time.
COMPILE_INCOMPATIBLE_GROUPS = {
    # error: "AbstractGeneralizedRushLarsenCardiacCell is not a direct base" of the generated
    # class - AbstractCardiacCellWithModifiers/AbstractGeneralizedRushLarsenCardiacCell's
    # inheritance relationship has changed since this fixture was generated.
    ("GRL1", "dynamic_matsuoka_model_2003"),
}

CLASS_RE = re.compile(r"^class\s+(\w+)", re.MULTILINE)
SELF_INCLUDE_RE = re.compile(r'^#include "([^"]+)\.hpp"', re.MULTILINE)


def read_frozen_baseline(scheme, filename):
    """Read a file from the frozen baseline/ snapshot, or None if it's not there.
    Never touches git - see freeze_baseline.py and BASELINE_DIR's docstring."""
    path = BASELINE_DIR / scheme / filename
    return path.read_text() if path.is_file() else None


def extract_self_include(cpp_text, exists_fn, label):
    """Find a generated .cpp's own paired header. Its *filename* does not always match the
    .cpp's own filename (a handful of chaste_codegen's checked-in reference fixtures have a
    self-include that doesn't match their own on-disk name, invisible to chaste_codegen's own
    text-only tests) - and the self-include is not always the *first* local #include either
    (BackwardEuler-scheme files '#include "CardiacNewtonSolver.hpp"', a real Chaste heart
    header, before their own paired header). Resolve by checking, in order, which local
    #include actually resolves to a file present alongside this .cpp in the reference-model
    corpus - genuine Chaste framework headers (CardiacNewtonSolver.hpp, Exception.hpp, ...)
    never live there, so the first match is reliably the model's own header. `exists_fn(stem)`
    abstracts over checking the current-branch filesystem vs. the frozen baseline/ snapshot."""
    stems = SELF_INCLUDE_RE.findall(cpp_text)
    if not stems:
        print(f"  WARNING: {label}: no local #include found in .cpp", file=sys.stderr)
        return None
    for stem in stems:
        if exists_fn(stem):
            return stem
    return None


def parse_class_info(hpp_text, label):
    """Extract (class_name, needs_empty_solver, needs_cvode_guard) from a reference .hpp."""
    match = CLASS_RE.search(hpp_text)
    if match is None:
        return None
    class_name = match.group(1)
    ctor_match = re.search(re.escape(class_name) + r"\s*\(([^;]*)\)\s*;", hpp_text)
    ctor_args = ctor_match.group(1) if ctor_match else ""
    if ctor_match is None:
        print(f"  WARNING: could not find constructor declaration for {label} "
              f"(class {class_name}); assuming a real solver is wanted.", file=sys.stderr)
    needs_empty_solver = "unused" in ctor_args
    needs_cvode_guard = hpp_text.lstrip().startswith("#ifdef CHASTE_CVODE")
    return class_name, needs_empty_solver, needs_cvode_guard


def render_test_file(project_name, class_name, header_stem,
                      needs_empty_solver, needs_cvode_guard, output_folder, variant_basename):
    """variant_basename is the tuple's raw variant ("default", "baseline", "sympy_1_14", ...) - written
    here as the literal basename WriteToFile() gives the generated .dat file, so
    TestRefCheckCompareAll can later find it again by that same variant value via RefCheckEntry.variant."""
    ident = f"Test_{project_name}"
    guard = re.sub(r"[^A-Za-z0-9_]", "_", ident).upper()

    solver_line = (
        "        boost::shared_ptr<AbstractIvpOdeSolver> p_solver; // unused by this scheme; must stay empty"
        if needs_empty_solver else
        "        boost::shared_ptr<AbstractIvpOdeSolver> p_solver(new EulerIvpOdeSolver);"
    )

    body = f"""{solver_line}
        boost::shared_ptr<AbstractStimulusFunction> p_stimulus(new SimpleStimulus(-25.5, 2.0, 50.0));
        boost::shared_ptr<AbstractCardiacCellInterface> p_cell(new {class_name}(p_solver, p_stimulus));

        double end_time = 700.0; // ms, fallback if the model has no SuggestedCycleLength attribute
        AbstractUntemplatedParameterisedSystem* p_system =
            dynamic_cast<AbstractUntemplatedParameterisedSystem*>(p_cell.get());
        if (p_system != NULL)
        {{
            if (p_system->HasAttribute("SuggestedCycleLength"))
            {{
                end_time = p_system->GetAttribute("SuggestedCycleLength");
            }}
            if (p_system->HasAttribute("SuggestedForwardEulerTimestep"))
            {{
                double dt = p_system->GetAttribute("SuggestedForwardEulerTimestep");
                if (dt > 0.0)
                {{
                    p_cell->SetTimestep(dt);
                }}
            }}
        }}
#ifdef CHASTE_CVODE
        AbstractCvodeSystem* p_cvode_system = dynamic_cast<AbstractCvodeSystem*>(p_cell.get());
        if (p_cvode_system != NULL)
        {{
            p_cvode_system->SetMaxSteps(1000);
        }}
#endif

        OdeSolution solution = p_cell->Compute(0.0, end_time, 1.0);
        solution.WriteToFile("{output_folder}", "{variant_basename}", "ms", 10, false);"""

    if needs_cvode_guard:
        run_method = f"""    void TestRunAndWrite()
    {{
#ifdef CHASTE_CVODE
{body}
#else
        TS_TRACE("Skipped: this model requires CHASTE_CVODE, which is not enabled in this build.");
#endif
    }}"""
    else:
        run_method = f"""    void TestRunAndWrite()
    {{
{body}
    }}"""

    return f"""// AUTOGENERATED by chaste_codegen/tests/numerical/generate_refcheck_harness.py
// Do not hand-edit; rerun the generator instead.
#ifndef {guard}_HPP_
#define {guard}_HPP_

#include <cxxtest/TestSuite.h>
#include <boost/shared_ptr.hpp>

#include "AbstractCardiacCellInterface.hpp"
#include "AbstractStimulusFunction.hpp"
#include "AbstractUntemplatedParameterisedSystem.hpp"
#include "EulerIvpOdeSolver.hpp"
#include "OdeSolution.hpp"
#include "SimpleStimulus.hpp"
#include "{header_stem}.hpp"
#ifdef CHASTE_CVODE
#include "AbstractCvodeSystem.hpp"
#endif

// This test must run sequentially (never in parallel), like other codegen tests.
#include "FakePetscSetup.hpp"

class {ident} : public CxxTest::TestSuite
{{
public:
{run_method}
}};

#endif // {guard}_HPP_
"""


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def ensure_model_factory(project_name, cpp_text, ensured):
    """Copy the generic ModelFactory.hpp/.cpp (from Chaste's own ApPredict example project)
    into a project the first time it turns out to need it (detected by the generated .cpp
    itself #include-ing it)."""
    if project_name in ensured:
        return
    if '#include "ModelFactory.hpp"' not in cpp_text:
        return
    model_factory_hpp = PROJECTS_DIR / "ApPredict" / "src" / "fortests" / "ModelFactory.hpp"
    model_factory_cpp = PROJECTS_DIR / "ApPredict" / "src" / "fortests" / "ModelFactory.cpp"
    dest_dir = PROJECTS_DIR / project_name / "src" / "fortests"
    write_file(dest_dir / "ModelFactory.hpp", model_factory_hpp.read_text())
    write_file(dest_dir / "ModelFactory.cpp", model_factory_cpp.read_text())
    ensured.add(project_name)


def write_tuple_project(project_name, header_stem, hpp_text, cpp_text, class_name,
                         needs_empty_solver, needs_cvode_guard, output_folder, variant_basename,
                         model_factory_ensured):
    """Create a complete, standalone Chaste project for exactly one (scheme, model, variant)
    tuple: its own CMakeLists.txt, one src .hpp/.cpp pair, one test runner. Isolating each
    tuple in its own project/library sidesteps every cross-tuple symbol collision (see module
    docstring) without needing any custom (non-macro) CMake linking logic."""
    proj_dir = PROJECTS_DIR / project_name
    write_file(proj_dir / "CMakeLists.txt", f"""# AUTOGENERATED by chaste_codegen/tests/numerical/generate_refcheck_harness.py (chaste-codegen repo)
# Do not hand-edit; rerun the generator instead.
find_package(Chaste COMPONENTS heart)
chaste_do_project({project_name})
""")
    write_file(proj_dir / "test" / "CMakeLists.txt", f"""# AUTOGENERATED by chaste_codegen/tests/numerical/generate_refcheck_harness.py (chaste-codegen repo)
# Do not hand-edit; rerun the generator instead.
chaste_do_test_project({project_name})
""")
    write_file(proj_dir / "src" / f"{header_stem}.hpp", hpp_text)
    write_file(proj_dir / "src" / f"{header_stem}.cpp", cpp_text)
    ensure_model_factory(project_name, cpp_text, model_factory_ensured)

    test_content = render_test_file(project_name, class_name, header_stem,
                                     needs_empty_solver, needs_cvode_guard, output_folder, variant_basename)
    test_filename = f"Test_{project_name}.hpp"
    write_file(proj_dir / "test" / test_filename, test_content)
    write_file(proj_dir / "test" / "CodegenTestPack.txt", test_filename + "\n")
    return f"Test_{project_name}"


def clean_previous_projects():
    if not PROJECTS_DIR.is_dir():
        return
    for child in PROJECTS_DIR.iterdir():
        if child.is_dir() and child.name.startswith(PROJECT_PREFIX):
            shutil.rmtree(child)


def stage_compare_project_template():
    """Copy CodegenRefCheck/ (the hand-written CMakeLists.txt + TestRefCheckCompareAll.hpp
    template that lives in this repo) wholesale into <CHASTE_SOURCE_DIR>/projects/, fresh each
    run. Everything else under that project directory (test/CMakeLists.txt, RefCheckManifest.hpp,
    CodegenTestPack.txt, generated_manifest.md) is generated by this script below."""
    dest = PROJECTS_DIR / COMPARE_PROJECT
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(COMPARE_PROJECT_TEMPLATE_DIR, dest)
    (dest / "src").mkdir(exist_ok=True)
    (dest / "src" / ".gitkeep").touch()


def main():
    clean_previous_projects()
    stage_compare_project_template()

    # (scheme, model_name) -> {variant_tag: cpp_path}   (variant_tag "default" == the unsuffixed
    # rendering)
    groups = defaultdict(dict)
    skipped = []

    for scheme in SCHEMES:
        scheme_dir = REFS_DIR / scheme
        if not scheme_dir.is_dir():
            print(f"WARNING: scheme directory not found, skipping: {scheme_dir}", file=sys.stderr)
            continue
        for cpp_path in sorted(scheme_dir.glob("*.cpp")):
            name = cpp_path.stem
            if "--" in name:
                model_name, variant = name.split("--", 1)
            else:
                model_name, variant = name, "default"
            if model_name.startswith(MODEL_NAME_PREFIXES_TO_SKIP):
                skipped.append(f"{scheme}/{cpp_path.name}: synthetic codegen-feature fixture, not a cardiac model")
                continue
            groups[(scheme, model_name)][variant] = cpp_path

    manifest_entries = []  # (scheme, model, variant, has_baseline)
    no_baseline = []
    unknown_variants = []
    all_test_names = []
    model_factory_ensured = set()  # project names that already got ModelFactory.hpp/.cpp this run

    for (scheme, model_name), variants in sorted(groups.items()):
        if (scheme, model_name) in COMPILE_INCOMPATIBLE_GROUPS:
            skipped.append(f"{scheme}/{model_name}: excluded, known incompatible with current "
                            f"Chaste heart API (see COMPILE_INCOMPATIBLE_GROUPS)")
            continue

        output_folder = f"CodegenRefCheck/{scheme}/{model_name}"

        # baseline - resolved via the baseline's own .cpp's self-include, not model_name.hpp.
        # Read from the fixed baseline/ snapshot only - never live from git.
        baseline_cpp = read_frozen_baseline(scheme, f"{model_name}.cpp")
        has_baseline = baseline_cpp is not None

        if has_baseline:
            baseline_hpp_cache = {}

            def baseline_hpp_exists(stem, _scheme=scheme, _cache=baseline_hpp_cache):
                if stem not in _cache:
                    _cache[stem] = read_frozen_baseline(_scheme, f"{stem}.hpp")
                return _cache[stem] is not None

            b_header_stem = extract_self_include(baseline_cpp, baseline_hpp_exists, f"{scheme}/{model_name} (baseline)")
            baseline_hpp = baseline_hpp_cache.get(b_header_stem) if b_header_stem is not None else None
            if b_header_stem is None or baseline_hpp is None:
                has_baseline = False
                no_baseline.append(f"{scheme}/{model_name}: baseline .cpp self-include unresolved "
                                    f"(expects {b_header_stem}.hpp)" if b_header_stem else
                                    f"{scheme}/{model_name}: baseline .cpp has no local #include")
            else:
                baseline_info = parse_class_info(baseline_hpp, f"{scheme}/{model_name} (baseline)")
                if baseline_info is None:
                    has_baseline = False
                    no_baseline.append(f"{scheme}/{model_name}: baseline file found but has no parseable class")
                else:
                    b_class_name, b_needs_empty_solver, b_needs_cvode_guard = baseline_info
                    project_name = f"{PROJECT_PREFIX}{scheme}_{model_name}_{VARIANT_TO_SHORT['baseline']}"
                    test_name = write_tuple_project(
                        project_name, b_header_stem, baseline_hpp, baseline_cpp, b_class_name,
                        b_needs_empty_solver, b_needs_cvode_guard, output_folder,
                        "baseline",  # this tuple's variant - written verbatim as the .dat basename
                        model_factory_ensured)
                    all_test_names.append(test_name)
        if not has_baseline:
            no_baseline.append(f"{scheme}/{model_name}: no baseline (not in the frozen "
                                f"baseline snapshot - new on this branch?)")

        for variant_tag, cpp_path in sorted(variants.items()):
            # variant: "default" (the unsuffixed rendering) or a version-suffix tag. Kept in this raw
            # form all the way to write_tuple_project()'s variant_basename arg (-> the .dat filename)
            # and manifest_entries (-> RefCheckEntry.variant, read back by TestRefCheckCompareAll).
            # short_variant below is a display-only derivative, used just for project_name.
            variant = variant_tag
            short_variant = VARIANT_TO_SHORT.get(variant)
            if short_variant is None:
                unknown_variants.append(f"{scheme}/{model_name}--{variant_tag}: unrecognised variant tag, skipped")
                continue

            variant_cpp_text = cpp_path.read_text()
            label = f"{scheme}/{cpp_path.name}"
            scheme_dir = REFS_DIR / scheme
            header_stem = extract_self_include(
                variant_cpp_text, lambda stem, _d=scheme_dir: (_d / f"{stem}.hpp").is_file(), label)
            if header_stem is None:
                skipped.append(f"{label}: self-include unresolved - no local #include target exists "
                                f"in {scheme}/ (broken fixture)")
                continue
            hpp_path = scheme_dir / f"{header_stem}.hpp"
            hpp_text = hpp_path.read_text()
            info = parse_class_info(hpp_text, label)
            if info is None:
                skipped.append(f"{label}: could not find a class declaration in {header_stem}.hpp")
                continue
            class_name, needs_empty_solver, needs_cvode_guard = info

            project_name = f"{PROJECT_PREFIX}{scheme}_{model_name}_{short_variant}"
            test_name = write_tuple_project(
                project_name, header_stem, hpp_text, variant_cpp_text, class_name,
                needs_empty_solver, needs_cvode_guard, output_folder, variant, model_factory_ensured)
            all_test_names.append(test_name)

            manifest_entries.append((scheme, model_name, variant, has_baseline))

    # Compare project: manifest header + CMakeLists.txt (with DEPENDS on every generated test)
    manifest_lines = ["// AUTOGENERATED by chaste_codegen/tests/numerical/generate_refcheck_harness.py (chaste-codegen repo)",
                       "// Do not hand-edit; rerun the generator instead.",
                       "#ifndef REFCHECKMANIFEST_HPP_",
                       "#define REFCHECKMANIFEST_HPP_",
                       "",
                       "#include <string>",
                       "#include <vector>",
                       "",
                       "struct RefCheckEntry",
                       "{",
                       "    std::string scheme;",
                       "    std::string model;",
                       "    // Which rendering of (scheme, model) this is: \"default\", \"baseline\",",
                       "    // or a version-suffix tag (e.g. \"sympy_1_14\"). Doubles as the .dat",
                       "    // file's basename this tuple's runner wrote - see TestRefCheckCompareAll.",
                       "    std::string variant;",
                       "    bool hasBaseline;",
                       "};",
                       "",
                       "inline std::vector<RefCheckEntry> GetRefCheckManifest()",
                       "{",
                       "    std::vector<RefCheckEntry> entries;"]
    for scheme, model_name, variant, has_baseline in manifest_entries:
        cpp_bool = "true" if has_baseline else "false"
        manifest_lines.append(
            f'    entries.push_back(RefCheckEntry{{"{scheme}", "{model_name}", "{variant}", {cpp_bool}}});')
    manifest_lines += ["    return entries;", "}", "", "#endif // REFCHECKMANIFEST_HPP_", ""]
    write_file(PROJECTS_DIR / COMPARE_PROJECT / "test" / "RefCheckManifest.hpp", "\n".join(manifest_lines))

    write_file(PROJECTS_DIR / COMPARE_PROJECT / "test" / "CodegenTestPack.txt", "TestRefCheckCompareAll.hpp\n")

    depends_list = ";".join(sorted(all_test_names))
    compare_cmake = f"""# AUTOGENERATED by chaste_codegen/tests/numerical/generate_refcheck_harness.py (chaste-codegen repo)
# Do not hand-edit; rerun the generator instead.

chaste_do_test_project({COMPARE_PROJECT})

# TestRefCheckCompareAll only makes sense after every RefCheck* tuple-runner test (each in its
# own sibling RefCheck_<scheme>_<model>_<variant> project) has written its .dat output; ctest does
# not order tests by default, so this dependency must be explicit.
set_tests_properties(TestRefCheckCompareAll PROPERTIES DEPENDS "{depends_list}")
"""
    write_file(PROJECTS_DIR / COMPARE_PROJECT / "test" / "CMakeLists.txt", compare_cmake)

    # Human-readable report
    report_lines = [
        "# CodegenRefCheck generated manifest",
        "",
        f"Source repo (this checkout): `{REPO_ROOT}`",
        f"Target Chaste checkout: `{CHASTE_SOURCE_DIR}`",
        "",
        f"- Groups (scheme, model) found: {len(groups)}",
        f"- Tuples generated (variant runners, excluding baseline): {len(manifest_entries)}",
        f"- Groups with a baseline: {len(set((s, m) for s, m, _, hb in manifest_entries if hb))}",
        f"- Groups with NO baseline: {len(no_baseline)}",
        f"- Skipped non-model files: {len(skipped)}",
        f"- Unknown variant tags skipped: {len(unknown_variants)}",
        f"- Generated projects: {len(all_test_names)}",
        "",
    ]
    if no_baseline:
        report_lines += ["## No baseline", ""] + [f"- {x}" for x in no_baseline] + [""]
    if skipped:
        report_lines += ["## Skipped (non-model files)", ""] + [f"- {x}" for x in skipped] + [""]
    if unknown_variants:
        report_lines += ["## Unknown variant tags", ""] + [f"- {x}" for x in unknown_variants] + [""]
    write_file(PROJECTS_DIR / COMPARE_PROJECT / "generated_manifest.md", "\n".join(report_lines))

    print(f"Generated {len(all_test_names)} projects ({len(manifest_entries)} variant-runner tuples "
          f"+ baselines) across {len(set((s, m) for s, m, _, _ in manifest_entries))} "
          f"(scheme, model) groups; {len(no_baseline)} without a baseline, "
          f"{len(skipped)} non-model files skipped, {len(unknown_variants)} unknown variant tags skipped.")
    print(f"Materialised into {PROJECTS_DIR}")
    print(f"See {PROJECTS_DIR / COMPARE_PROJECT / 'generated_manifest.md'} for details.")


if __name__ == "__main__":
    if not REFS_DIR.is_dir():
        print(f"Error: reference model directory not found: {REFS_DIR}", file=sys.stderr)
        sys.exit(1)
    if not BASELINE_DIR.is_dir():
        print(f"Error: no frozen baseline found at {BASELINE_DIR}.\n"
              f"Run freeze_baseline.py once first (this is deliberate - the baseline "
              f"is meant to stay fixed, not be created implicitly).", file=sys.stderr)
        sys.exit(1)
    if not (CHASTE_SOURCE_DIR / "CMakeLists.txt").is_file():
        print(f"Error: CHASTE_SOURCE_DIR ({CHASTE_SOURCE_DIR}) doesn't look like a Chaste checkout "
              f"(no CMakeLists.txt found there). Set CHASTE_SOURCE_DIR to one.", file=sys.stderr)
        sys.exit(1)
    main()
