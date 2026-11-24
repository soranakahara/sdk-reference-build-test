"""Record selected public build provenance; never dump the environment."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def run(*args, cwd=ROOT):
    result = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return result.stdout.strip()


sdk = sys.argv[1]
source = ROOT / "sdk" / sdk
spec = next(s for s in json.loads((ROOT / "sources.lock.json").read_text())["sources"] if s["name"] == sdk)
revision = run("git", "rev-parse", "HEAD", cwd=source)
if revision != spec["commit"] or run("git", "diff", "--name-only", cwd=source):
    raise ValueError("SDK source differs from its pinned revision")
for name, expected in spec["configuration_sha256"].items():
    if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
        raise ValueError(f"SDK input changed: {name}")
commands = {
    "swift": {"ruby": ["ruby", "--version"], "bundler": ["bundle", "--version"], "jazzy": ["bundle", "exec", "jazzy", "--version"], "xcode": ["xcodebuild", "-version"], "swift": ["xcrun", "swift", "--version"]},
    "android": {"java": ["java", "-version"]},
    "unity": {"doxygen": ["doxygen", "--version"]},
}
if sdk == "swift":
    os.environ["BUNDLE_GEMFILE"] = str(Path(os.environ["RUNNER_TEMP"]) / "sdk-reference/swift/Gemfile")
metadata = ROOT / "artifacts" / sdk / "metadata"
record = {
    "source_url": spec["url"], "source_revision": revision,
    "input_configuration_sha256": spec["configuration_sha256"],
    "parent_revision": run("git", "rev-parse", "HEAD"),
    "run": {key: os.environ.get(key) for key in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_REF", "RUNNER_OS", "RUNNER_ARCH", "ImageOS", "ImageVersion")},
    "tool_versions": {name: run(*command, cwd=source) for name, command in commands[sdk].items()},
    "known_dependency_issues": "Accepted for this disposable public-input experiment; see docs/risk-notes.md. No security patches applied.",
}
if sdk == "android":
    record["android_sdk_packages"] = {
        name: (Path(os.environ["ANDROID_HOME"]) / name / "source.properties").read_text()
        for name in ("platforms/android-33", "build-tools/30.0.3", "cmdline-tools/latest")
    }
(metadata / "provenance.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
