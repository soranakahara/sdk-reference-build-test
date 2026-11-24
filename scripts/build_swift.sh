#!/usr/bin/env bash
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true ]] || { echo 'Run on a hosted Actions runner.' >&2; exit 2; }

output="$GITHUB_WORKSPACE/artifacts/swift"
export BUNDLE_PATH="$RUNNER_TEMP/sdk-reference/gems"
echo "BUNDLE_PATH=$BUNDLE_PATH" >> "$GITHUB_ENV"
metadata="$RUNNER_TEMP/sdk-reference/swift-metadata"
mkdir -p "$metadata"
cd "$GITHUB_WORKSPACE/sdk/swift"
[[ "$(uname -m)" == arm64 ]]
xcodebuild -version | tee "$metadata/xcode.txt"
bundle_copy="$RUNNER_TEMP/sdk-reference/swift"
python3 "$GITHUB_WORKSPACE/scripts/prepare_swift_bundle.py" "$PWD" "$bundle_copy" "$(ruby -e 'print Gem::Platform.local')" "$metadata"
export BUNDLE_GEMFILE="$bundle_copy/Gemfile"
bundle install --jobs 4 --retry 3
bundle list > "$metadata/gems.txt"
cmp "$bundle_copy/Gemfile.lock" "$metadata/Gemfile.lock.effective"
git diff --exit-code
# Jazzy's clean:true removes its output directory, so retain logs outside it.
bundle exec jazzy --copyright "© $(date +%Y) [LY Corporation.](https://line.me) All rights reserved." --output "$output" 2>&1 | tee "$metadata/generation.log"
mkdir -p "$output/metadata"
cp -R "$metadata/." "$output/metadata/"
git diff --exit-code
