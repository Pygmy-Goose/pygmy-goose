#!/bin/sh

set -eu

SPLIT_DIR="split"

if ! git diff --quiet || ! git diff --cached --quiet; then
	echo "Refusing to split with uncommitted changes in the worktree."
	exit 1
fi

mkdir -p "${SPLIT_DIR}"

if [ -d extension/core_functions ]; then
	git mv extension/core_functions core_functions
	git commit -m "Move core_functions before split" -- core_functions extension/core_functions
fi

split_path_to_repo() {
	source_path="$1"
	repo_name="$2"
	shift 2

	git clone --bare . "${SPLIT_DIR}/${repo_name}.git"
	git -C "${SPLIT_DIR}/${repo_name}.git" filter-repo --force \
		--path "${source_path}/" \
		--path-rename "${source_path}/:" \
		"$@"
}

split_path_to_repo extension extensions "$@"
split_path_to_repo data data "$@"
split_path_to_repo third_party third_party "$@"

git clone --bare . "${SPLIT_DIR}/duckdb.git"
git -C "${SPLIT_DIR}/duckdb.git" filter-repo --force \
	--path third_party/ --invert-paths \
	--path data/ --invert-paths \
	--path extension/ --invert-paths \
	--path examples/ --invert-paths \
	--path tools/amalgamation/ --invert-paths \
	--path tools/juliapkg/ --invert-paths \
	--path tools/nodejs/ --invert-paths \
	--path tools/pythonpkg/ --invert-paths \
	--path tools/rpkg/ --invert-paths \
	--path tools/swift/ --invert-paths \
	--path tools/wasm/ --invert-paths \
	--path tools/utils/ --invert-paths \
	--path tools/utils/upload-s3.py --invert-paths \
	--path tools/utils/release-pip.py --invert-paths \
	"$@"
