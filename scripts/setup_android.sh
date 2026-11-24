#!/usr/bin/env bash
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true ]] || { echo 'Run on a hosted Actions runner.' >&2; exit 2; }

tools="$RUNNER_TEMP/sdk-reference"
mkdir -p "$tools/jdk"
python3 -c 'print("y\n" * 100)' > "$tools/android-license-answers"
manager="${ANDROID_HOME:?}/cmdline-tools/latest/bin/sdkmanager"
[[ -x "$manager" ]]
"$manager" --licenses < "$tools/android-license-answers" > "$tools/android-licenses.log"
"$manager" 'platforms;android-33' 'build-tools;30.0.3'

archive="$tools/temurin.tar.gz"
curl --fail --location --retry 3 --proto '=https' 'https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.33.1%2B1/OpenJDK11U-jdk_x64_linux_hotspot_11.0.33.1_1.tar.gz' --output "$archive"
echo "3119b6dd17543e8e61fd0186f9325414bf2601270bf1edf8a314b9a51c5fb89d  $archive" | sha256sum --check
tar -xzf "$archive" -C "$tools/jdk" --strip-components=1
echo "JAVA_HOME=$tools/jdk" >> "$GITHUB_ENV"
echo "$tools/jdk/bin" >> "$GITHUB_PATH"
