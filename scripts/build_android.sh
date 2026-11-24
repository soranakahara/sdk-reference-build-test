#!/usr/bin/env bash
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true ]] || { echo 'Run on a hosted Actions runner.' >&2; exit 2; }

output="$GITHUB_WORKSPACE/artifacts/android"
mkdir -p "$output/metadata"
cd "$GITHUB_WORKSPACE/sdk/android"
./gradlew --no-daemon --console=plain --version > "$output/metadata/gradle.txt"
./gradlew --no-daemon --console=plain :line-sdk:javadoc_public 2>&1 | tee "$output/metadata/generation.log"
cp -R line-sdk/build/docs/javadoc_public/. "$output/"
./gradlew --no-daemon --console=plain :line-sdk:dependencies --configuration doclava > "$output/metadata/doclava-dependencies.txt"
./gradlew --no-daemon --console=plain :line-sdk:dependencies --configuration javadocs > "$output/metadata/javadoc-dependencies.txt"
git diff --exit-code
