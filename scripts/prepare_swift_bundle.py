"""Copy the SDK bundle definition and adjust only its platform list."""

import hashlib
import json
from pathlib import Path
import re
import shutil
import sys


source, destination, platform, metadata = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
if not re.fullmatch(r"arm64-darwin-\d+", platform):
    raise ValueError(f"Unexpected Ruby platform: {platform}")
destination.mkdir(parents=True, exist_ok=True)
(destination / "fastlane").mkdir(exist_ok=True)
shutil.copyfile(source / "Gemfile", destination / "Gemfile")
shutil.copyfile(source / "fastlane/Pluginfile", destination / "fastlane/Pluginfile")
original = (source / "Gemfile.lock").read_bytes()
prefix, rest = original.split(b"PLATFORMS\n", 1)
platforms, suffix = rest.split(b"\n\n", 1)
entries = platforms.decode().splitlines()
added = "  " + platform not in entries
if added:
    entries.append("  " + platform)
effective = prefix + b"PLATFORMS\n" + "\n".join(sorted(entries)).encode() + b"\n\n" + suffix
effective_prefix, effective_rest = effective.split(b"PLATFORMS\n", 1)
_, effective_suffix = effective_rest.split(b"\n\n", 1)
if effective_prefix != prefix or effective_suffix != suffix:
    raise ValueError("Gem versions or non-platform lock data changed")
(destination / "Gemfile.lock").write_bytes(effective)
metadata.mkdir(parents=True, exist_ok=True)
(metadata / "Gemfile.lock.original").write_bytes(original)
(metadata / "Gemfile.lock.effective").write_bytes(effective)
(metadata / "bundle-platform.json").write_text(json.dumps({
    "ruby_platform": platform,
    "platform_added_to_temporary_lock": added,
    "non_platform_bytes_unchanged": True,
    "original_sha256": hashlib.sha256(original).hexdigest(),
    "effective_sha256": hashlib.sha256(effective).hexdigest(),
}, indent=2) + "\n")
