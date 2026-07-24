#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/../../.." && pwd)"

# Chaste checkout to build/test against - defaults to a sibling checkout, matching the
# convention Chaste's own local-dev/common.sh uses in the other direction
# (CHASTE_CODEGEN_SOURCE_DIR defaulting to ../chaste-codegen).
CHASTE_SOURCE_DIR="${CHASTE_SOURCE_DIR:-${repo_root}/../Chaste}"
if [[ ! -f "${CHASTE_SOURCE_DIR}/CMakeLists.txt" ]]; then
	echo "Error: CHASTE_SOURCE_DIR ('${CHASTE_SOURCE_DIR}') doesn't look like a Chaste checkout." >&2
	echo "Set CHASTE_SOURCE_DIR to one." >&2
	exit 1
fi
CHASTE_BUILD_DIR="${CHASTE_BUILD_DIR:-${CHASTE_SOURCE_DIR}/build}"
CHASTE_TEST_OUTPUT="${CHASTE_TEST_OUTPUT:-${CHASTE_SOURCE_DIR}/output}"

if ! [[ "${NCORES:-}" =~ ^[1-9][0-9]*$ ]]; then
	NCORES=4
fi

export CHASTE_SOURCE_DIR
python3 "${script_dir}/generate_refcheck_harness.py"

if [[ ! -f "${CHASTE_BUILD_DIR}/CMakeCache.txt" ]]; then
	echo "Error: Chaste build not configured at '${CHASTE_BUILD_DIR}'." >&2
	echo "Configure it first (e.g. Chaste's local-dev/configure.sh, or plain cmake)." >&2
	exit 1
fi

cmake "${CHASTE_SOURCE_DIR}" -B "${CHASTE_BUILD_DIR}" >/dev/null # pick up newly-generated projects
cmake --build "${CHASTE_BUILD_DIR}" --target Codegen --parallel "${NCORES}"

mkdir -p "${CHASTE_TEST_OUTPUT}"
CHASTE_TEST_OUTPUT="${CHASTE_TEST_OUTPUT}" ctest --test-dir "${CHASTE_BUILD_DIR}" -j"${NCORES}" -V -L Codegen -R '^Test_RefCheck|^TestRefCheckCompareAll' --output-on-failure
