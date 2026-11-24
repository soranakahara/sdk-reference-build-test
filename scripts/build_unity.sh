#!/usr/bin/env bash
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true ]] || { echo 'Run on a hosted Actions runner.' >&2; exit 2; }

output="$GITHUB_WORKSPACE/artifacts/unity"
mkdir -p "$output/metadata"
config="$RUNNER_TEMP/sdk-reference-unity.doxyfile"
cp "$GITHUB_WORKSPACE/sdk/unity/Doxyfile" "$config"
printf '\nOUTPUT_DIRECTORY = "%s"\nHTML_OUTPUT = .\n' "$output" >> "$config"
cd "$GITHUB_WORKSPACE/sdk/unity"
doxygen "$config" 2>&1 | tee "$output/metadata/generation.log"
dpkg-query -W -f='${Package} ${Version}\n' > "$output/metadata/ubuntu-packages.txt"
git diff --exit-code
