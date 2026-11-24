#!/usr/bin/env bash
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true ]] || { echo 'Run on a hosted Actions runner.' >&2; exit 2; }

output="$GITHUB_WORKSPACE/artifacts/android"
export GRADLE_USER_HOME="$RUNNER_TEMP/sdk-reference/gradle"
mkdir -p "$output/metadata"
cd "$GITHUB_WORKSPACE/sdk/android"
./gradlew --no-daemon --console=plain --version > "$output/metadata/gradle.txt"
./gradlew --no-daemon --console=plain --init-script "$GITHUB_WORKSPACE/scripts/android-javadoc.init.gradle" :line-sdk:javadoc_public 2>&1 | tee "$output/metadata/generation.log"
if grep -Eq '(^|:[[:space:]])error:' "$output/metadata/generation.log"; then
  echo 'Javadoc reported an error; refusing incomplete output.' >&2
  exit 1
fi
cp -R line-sdk/build/docs/javadoc_public/. "$output/"
./gradlew --no-daemon --console=plain :line-sdk:dependencies --configuration doclava > "$output/metadata/doclava-dependencies.txt"
./gradlew --no-daemon --console=plain :line-sdk:dependencies --configuration javadocs > "$output/metadata/javadoc-dependencies.txt"
./gradlew --no-daemon --console=plain :line-sdk:dependencies --configuration releaseCompileClasspath > "$output/metadata/compile-dependencies.txt"
git diff --exit-code
