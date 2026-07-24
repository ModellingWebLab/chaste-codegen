#!/usr/bin/env python3
"""Snapshots this repo's `master`-branch reference-model corpus into a permanent local
directory (baseline/), once.

This is the one and only place `master` is ever read from `git`. generate_refcheck_harness.py
never touches git at all - it only reads from this frozen snapshot. That's deliberate: the
whole point of this harness is to compare current-branch renderings against a *fixed* basis
that does not silently drift if this repo's master branch gets new commits later. Re-run this
script explicitly (with --force) only when you actually want to move the baseline forward to a
newer master - never as a side effect of the normal generate-and-test loop.

Only each model's default (unsuffixed) rendering is frozen (see is_default_reference()) -
sibling variant files (a legacy `.cpp_python36` rendering, or a `--sympy_X_Y`/`--python_X_Y`
suffixed file on branches that have them) are skipped, since generate_refcheck_harness.py never
reads them as a baseline either.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REFS_REL_PATH = "chaste_codegen/data/tests/chaste_reference_models"
BASELINE_DIR = Path(__file__).resolve().parent / "baseline"

# Only each model's default (unsuffixed) rendering belongs in the baseline - the fixed basis
# generate_refcheck_harness.py diffs every current-branch variant against. Sibling variant
# files - a legacy `.cpp_python36` rendering, a `--sympy_X_Y`/`--python_X_Y`-suffixed file on
# branches that have them, or any other alternate rendering of the same model - are excluded up
# front rather than freezing dead weight into baseline/.
DEFAULT_REFERENCE_EXTENSIONS = {".c", ".cpp", ".h", ".hpp", ".txt"}


def is_default_reference(path):
    name = Path(path)
    return name.suffix in DEFAULT_REFERENCE_EXTENSIONS and "--" not in name.stem


def run_git(args):
    result = subprocess.run(["git", "-C", str(REPO_ROOT)] + args,
                             capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: git {' '.join(args)} failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                         help="Overwrite an existing frozen baseline (moves it to a newer master).")
    args = parser.parse_args()

    if BASELINE_DIR.exists() and not args.force:
        print(f"Error: a frozen baseline already exists at {BASELINE_DIR}.", file=sys.stderr)
        print("This baseline is meant to stay fixed - it is not refreshed automatically.",
              file=sys.stderr)
        print("Pass --force if you really want to move it forward to master's current state.",
              file=sys.stderr)
        sys.exit(1)

    commit = run_git(["rev-parse", "master"]).strip()
    print(f"Freezing chaste_codegen baseline from master commit {commit} ...")

    file_list = run_git(["ls-tree", "-r", "--name-only", "master", "--", REFS_REL_PATH])
    all_paths = [line for line in file_list.splitlines() if line]
    if not all_paths:
        print(f"Error: no files found under {REFS_REL_PATH} on master.", file=sys.stderr)
        sys.exit(1)

    paths = [path for path in all_paths if is_default_reference(path)]
    skipped = len(all_paths) - len(paths)

    if BASELINE_DIR.exists():
        shutil.rmtree(BASELINE_DIR)

    count = 0
    for path in paths:
        rel = Path(path).relative_to(REFS_REL_PATH)
        content = run_git(["show", f"master:{path}"])
        dest = BASELINE_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
        count += 1

    (BASELINE_DIR / "FROZEN_AT_COMMIT.txt").write_text(
        f"{commit}\n\nThis directory is a permanent, fixed snapshot of\n"
        f"{REFS_REL_PATH}\nfrom this repo's master branch at the commit above.\n"
        f"generate_refcheck_harness.py reads baseline content only from here, never from git,\n"
        f"so this basis will not change unless freeze_baseline.py --force is run again.\n"
        f"Only default (unsuffixed) reference renderings are included - sibling variants "
        f"(e.g. `.cpp_python36`, `--sympy_X_Y`/`--python_X_Y`) are skipped; see "
        f"is_default_reference() in freeze_baseline.py.\n"
    )

    print(f"Froze {count} files into {BASELINE_DIR} ({skipped} sibling variant file(s) skipped)")


if __name__ == "__main__":
    main()
