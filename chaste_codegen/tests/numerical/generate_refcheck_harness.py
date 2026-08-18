#!/usr/bin/env python3
"""Creates a Chaste numerical cross-check harness from the reference model
corpus in this repository.

This generates one standalone Chaste project under
<CHASTE_SOURCE_DIR>/projects/RefCheck_<scheme>_<model>_<variant>/
for every "case" (scheme, model) found in the reference model corpus, and for
every "variant" rendering of it (e.g. sympy_X_Y variants).
Each project contains:
  - the reference .hpp/.cpp for that one case variant (scheme, model, variant).
  - one CxxTest runner that constructs the generated cell, runs it, and writes a
  .dat file into a shared case (scheme, model) output folder.

Each case variant (scheme, model, variant) gets its own project rather than
grouping several into one shared library to sidestep name collisions during
linking. For example, some scheme pairs (e.g. Cvode vs. Cvode_with_jacobian)
reuse the same class name for the same model. Also, every dynamically-loadable
model defines an identical global `MakeCardiacCell` factory function regardless
of which scheme/model it is.

The central CodegenRefCheck/ project has no generated cell code of its own. It
numerically diffs every variant's .dat output against its model's baseline via
Chaste's existing CompareCellModelResults helper.

See run_all.sh for the full generate -> configure -> build -> test sequence, or
README.md for the manual steps.
"""

import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

import jinja2

# Name of the hand-written compare project.
REFCHECK_PROJECT = "CodegenRefCheck"

# Every generated case project directory starts with this prefix.
PROJECT_PREFIX = "RefCheck_"

# Path to this numerical test harness.
NUMERICAL_TESTS_DIR = Path(__file__).resolve().parent

# Path to chaste-codegen repo root.
REPO_ROOT = NUMERICAL_TESTS_DIR.parents[2]

# Path to the reference-model corpus on the current branch.
REFS_DIR = REPO_ROOT / "chaste_codegen" / "data" / "tests" / "chaste_reference_models"

# Current frozen snapshot of the baseline reference-model corpus
BASELINE_DIR = NUMERICAL_TESTS_DIR / "baseline"

# The CodegenRefCheck/ project template
REFCHECK_PROJECT_TEMPLATE_DIR = NUMERICAL_TESTS_DIR / REFCHECK_PROJECT

# Path to Chaste source.
CHASTE_SOURCE_DIR = Path(
    os.environ.get("CHASTE_SOURCE_DIR", str(REPO_ROOT.parent / "Chaste"))
).resolve()
PROJECTS_DIR = CHASTE_SOURCE_DIR / "projects"

# Explicit allow-list: RL_C (plain C) and RL_labview (LabVIEW text) are excluded.
SCHEMES = [
    "Normal", "Opt", "BE", "BEopt",
    "Cvode", "Cvode_opt", "Cvode_with_jacobian", "Cvode_opt_with_jacobian",
    "CVODE_DATA_CLAMP", "CVODE_DATA_CLAMP_OPT",
    "GRL1", "GRL1Opt", "GRL2", "GRL2Opt",
    "RL", "RLopt",
]

# A "variant" identifies which rendering of a given "case" (scheme, model) is being tested:
# - baseline: the frozen snapshot.
# - default: the unsuffixed reference files.
# - sympy_X_Y: the sympy-version suffixed renderings.
# - python_X_Y: the python-version suffixed renderings.
# The dict keys below are used in filenames and the CamelCase forms in identifiers.
VARIANT_VARNAME = {
    "default": "Default",
    "sympy_1_11": "Sympy111",
    "sympy_1_13": "Sympy113",
    "sympy_1_14": "Sympy114",
    "python_3_11": "Python311",
    "baseline": "Baseline",
}

# Skip synthetic fixtures in reference model corpus that chaste_codegen uses to
# test one specific feature (piecewise handling, non-state-variable voltage, etc.)
# rather than real cardiac models.
MODEL_NAME_PREFIXES_TO_SKIP = ("test_",)

# Cases(scheme, model) written against an old Chaste heart API that no longer
# compiles against modern Chaste.
# TODO: fix or remove these from the reference-model corpus.
COMPILE_INCOMPATIBLE_CASES = {
    # error: "AbstractGeneralizedRushLarsenCardiacCell is not a direct base" of the generated
    # class - AbstractCardiacCellWithModifiers/AbstractGeneralizedRushLarsenCardiacCell's
    # inheritance relationship has changed since this fixture was generated.
    ("GRL1", "dynamic_matsuoka_model_2003"),
}

# Matches a class declaration, to parse the generated cell's class name.
CLASS_RE = re.compile(r"^class\s+(\w+)", re.MULTILINE)

# Matches every local #include in order.
SELF_INCLUDE_RE = re.compile(r'^#include "([^"]+)\.hpp"', re.MULTILINE)

# Create a Jinja env wired to the templates in this numerical test harness.
_JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(NUMERICAL_TESTS_DIR / "templates")),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=jinja2.StrictUndefined,
)

# Renders one CxxTest runner for each case variant (see render_test_file()).
VARIANT_RUNNER_TEMPLATE = _JINJA_ENV.get_template("variant_runner.hpp")

# Renders the central compare project's RefCheckManifest.hpp, a
# (scheme, model, variant, hasBaseline) table that TestRefCheckCompareAll uses.
REFCHECK_MANIFEST_TEMPLATE = _JINJA_ENV.get_template("refcheck_manifest.hpp")


def read_frozen_baseline(scheme: str, filename: str) -> Optional[str]:
    """Read a file from the frozen baseline, or None if it's not there."""
    path = BASELINE_DIR / scheme / filename
    return path.read_text() if path.is_file() else None


def extract_self_include(cpp_text: str, hpp_for_stem: Callable[[str], Optional[str]],
                          label: str) -> Optional[str]:
    """Find a generated .cpp's own paired .hpp header."""
    stems = SELF_INCLUDE_RE.findall(cpp_text)
    if not stems:
        print(f"  WARNING: {label}: no local #include found in .cpp", file=sys.stderr)
        return None
    # Check local includes in order.
    for stem in stems:
        hpp_text = hpp_for_stem(stem)
        if hpp_text is None:
            continue
        # Check that the class declared in the .hpp is actually defined in the .cpp.
        match = CLASS_RE.search(hpp_text)
        if match is None:
            continue
        class_name = match.group(1)
        if re.search(re.escape(class_name) + r"::", cpp_text):
            return stem
    return None


def parse_class_info(hpp_text: str, label: str) -> Optional[Tuple[str, bool, bool]]:
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


def render_test_file(project_name: str, class_name: str, header_stem: str,
                     needs_empty_solver: bool, needs_cvode_guard: bool, output_folder: str,
                     variant_basename: str) -> str:
    """variant_basename is the tuple's raw variant ("default", "baseline", "sympy_1_14", ...) - written
    here as the literal basename WriteToFile() gives the generated .dat file, so
    TestRefCheckCompareAll can later find it again by that same variant value via RefCheckEntry.variant."""
    ident = f"Test_{project_name}"
    guard = re.sub(r"[^A-Za-z0-9_]", "_", ident).upper()
    return VARIANT_RUNNER_TEMPLATE.render(
        guard=guard,
        ident=ident,
        class_name=class_name,
        header_stem=header_stem,
        needs_empty_solver=needs_empty_solver,
        needs_cvode_guard=needs_cvode_guard,
        output_folder=output_folder,
        variant_basename=variant_basename,
    )


def write_file(path: Path, content: str) -> None:
    """Write content to path, creating any missing parent directories first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def ensure_model_factory(project_name: str, cpp_text: str, ensured: Set[str]) -> None:
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


def write_tuple_project(project_name: str, header_stem: str, hpp_text: str, cpp_text: str,
                        class_name: str, needs_empty_solver: bool, needs_cvode_guard: bool,
                        output_folder: str, variant_basename: str,
                        model_factory_ensured: Set[str]) -> str:
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


def clean_projects_dir() -> None:
    """Remove all generated projects from previous runs (any PROJECTS_DIR
    subdirectory whose name starts with PROJECT_PREFIX) so each run starts from
    a clean slate. Does not touch CodegenRefCheck/ itself, which is staged fresh
    by stage_codegen_ref_check_project() instead."""
    if not PROJECTS_DIR.is_dir():
        return
    for child in PROJECTS_DIR.iterdir():
        if child.is_dir() and child.name.startswith(PROJECT_PREFIX):
            shutil.rmtree(child)


def stage_codegen_ref_check_project() -> None:
    """Copy the CodegenRefCheck/  project template (TestRefCheckCompareAll.hpp + CMakeLists.txt)
    wholesale into <CHASTE_SOURCE_DIR>/projects/, fresh each run. The rest of the
    CodegenRefCheck/ project is auto-generated by the rest of this script."""
    dest = PROJECTS_DIR / REFCHECK_PROJECT
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(REFCHECK_PROJECT_TEMPLATE_DIR, dest)
    (dest / "src").mkdir(exist_ok=True)
    (dest / "src" / ".gitkeep").touch()


def main() -> None:
    """Regenerate the whole harness from scratch: wipe previously generated per-tuple projects,
    stage a fresh CodegenRefCheck/ compare project, discover every (scheme, model, variant)
    tuple in the current checkout's reference-model corpus plus the frozen baseline/ snapshot,
    write one standalone Chaste project per tuple (see write_tuple_project()), then write the
    manifest, compare-project CMakeLists.txt, and a human-readable generated_manifest.md
    summarising what was generated, skipped, or found to have no baseline."""
    clean_projects_dir()
    stage_codegen_ref_check_project()

    # (scheme, model_name) -> {variant_tag: cpp_path}   (variant_tag "default" == the unsuffixed
    # rendering)
    cases: Dict[Tuple[str, str], Dict[str, Path]] = defaultdict(dict)
    skipped: List[str] = []

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
            cases[(scheme, model_name)][variant] = cpp_path

    manifest_entries: List[Tuple[str, str, str, bool]] = []  # (scheme, model, variant, has_baseline)
    no_baseline: List[str] = []
    unknown_variants: List[str] = []
    all_test_names: List[str] = []
    model_factory_ensured: Set[str] = set()  # project names that already got ModelFactory.hpp/.cpp this run

    for (scheme, model_name), variants in sorted(cases.items()):
        if (scheme, model_name) in COMPILE_INCOMPATIBLE_CASES:
            skipped.append(f"{scheme}/{model_name}: excluded, known incompatible with current "
                           f"Chaste heart API (see COMPILE_INCOMPATIBLE_CASES)")
            continue

        output_folder = f"CodegenRefCheck/{scheme}/{model_name}"

        # baseline - resolved via the baseline's own .cpp's self-include, not model_name.hpp.
        # Read from the fixed baseline/ snapshot only - never live from git.
        baseline_cpp = read_frozen_baseline(scheme, f"{model_name}.cpp")
        has_baseline = baseline_cpp is not None

        if baseline_cpp is not None:
            baseline_hpp_cache: Dict[str, Optional[str]] = {}

            def baseline_hpp_for_stem(stem: str, _scheme: str = scheme,
                                       _cache: Dict[str, Optional[str]] = baseline_hpp_cache) -> Optional[str]:
                """hpp_for_stem for extract_self_include() below: stem.hpp's content if it exists
                in this scheme's frozen baseline/ snapshot, else None. Memoised in _cache since
                the same stem can be probed more than once per (scheme, model)."""
                if stem not in _cache:
                    _cache[stem] = read_frozen_baseline(_scheme, f"{stem}.hpp")
                return _cache[stem]

            b_header_stem = extract_self_include(baseline_cpp, baseline_hpp_for_stem, f"{scheme}/{model_name} (baseline)")
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
                    project_name = f"{PROJECT_PREFIX}{scheme}_{model_name}_{VARIANT_VARNAME['baseline']}"
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
            short_variant = VARIANT_VARNAME.get(variant)
            if short_variant is None:
                unknown_variants.append(f"{scheme}/{model_name}--{variant_tag}: unrecognised variant tag, skipped")
                continue

            variant_cpp_text = cpp_path.read_text()
            label = f"{scheme}/{cpp_path.name}"
            scheme_dir = REFS_DIR / scheme

            def live_hpp_for_stem(stem: str, _d: Path = scheme_dir) -> Optional[str]:
                """hpp_for_stem for extract_self_include() below: stem.hpp's content if it
                exists alongside this .cpp in the live reference-model corpus, else None."""
                path = _d / f"{stem}.hpp"
                return path.read_text() if path.is_file() else None

            header_stem = extract_self_include(variant_cpp_text, live_hpp_for_stem, label)
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
    write_file(PROJECTS_DIR / REFCHECK_PROJECT / "test" / "RefCheckManifest.hpp",
               REFCHECK_MANIFEST_TEMPLATE.render(manifest_entries=manifest_entries))

    write_file(PROJECTS_DIR / REFCHECK_PROJECT / "test" / "CodegenTestPack.txt", "TestRefCheckCompareAll.hpp\n")

    depends_list = ";".join(sorted(all_test_names))
    compare_cmake = f"""# AUTOGENERATED by chaste_codegen/tests/numerical/generate_refcheck_harness.py (chaste-codegen repo)
# Do not hand-edit; rerun the generator instead.

chaste_do_test_project({REFCHECK_PROJECT})

# TestRefCheckCompareAll only makes sense after every RefCheck* tuple-runner test (each in its
# own sibling RefCheck_<scheme>_<model>_<variant> project) has written its .dat output; ctest does
# not order tests by default, so this dependency must be explicit.
set_tests_properties(TestRefCheckCompareAll PROPERTIES DEPENDS "{depends_list}")
"""
    write_file(PROJECTS_DIR / REFCHECK_PROJECT / "test" / "CMakeLists.txt", compare_cmake)

    # Human-readable report
    report_lines = [
        "# CodegenRefCheck generated manifest",
        "",
        f"Source repo (this checkout): `{REPO_ROOT}`",
        f"Target Chaste checkout: `{CHASTE_SOURCE_DIR}`",
        "",
        f"- Cases (scheme, model) found: {len(cases)}",
        f"- Tuples generated (variant runners, excluding baseline): {len(manifest_entries)}",
        f"- Cases with a baseline: {len(set((s, m) for s, m, _, hb in manifest_entries if hb))}",
        f"- Cases with NO baseline: {len(no_baseline)}",
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
    write_file(PROJECTS_DIR / REFCHECK_PROJECT / "generated_manifest.md", "\n".join(report_lines))

    print(f"Generated {len(all_test_names)} projects ({len(manifest_entries)} variant-runner tuples "
          f"+ baselines) across {len(set((s, m) for s, m, _, _ in manifest_entries))} "
          f"(scheme, model) cases; {len(no_baseline)} without a baseline, "
          f"{len(skipped)} non-model files skipped, {len(unknown_variants)} unknown variant tags skipped.")
    print(f"Materialised into {PROJECTS_DIR}")
    print(f"See {PROJECTS_DIR / REFCHECK_PROJECT / 'generated_manifest.md'} for details.")


if __name__ == "__main__":
    if not REFS_DIR.is_dir():
        print(f"Error: reference model directory not found: {REFS_DIR}", file=sys.stderr)
        sys.exit(1)
    if not BASELINE_DIR.is_dir():
        print(f"Error: no frozen baseline found at {BASELINE_DIR}.\n"
              f"Run freeze_baseline.py once first.", file=sys.stderr)
        sys.exit(1)
    if not (CHASTE_SOURCE_DIR / "CMakeLists.txt").is_file():
        print(f"Error: CHASTE_SOURCE_DIR ({CHASTE_SOURCE_DIR}) doesn't look like Chaste. "
              f"Set CHASTE_SOURCE_DIR to a Chaste checkout.", file=sys.stderr)
        sys.exit(1)
    main()
