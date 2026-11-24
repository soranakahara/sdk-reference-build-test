"""Copy the SDK bundle definition and adjust only its platform list."""

from pathlib import Path
import re
import shutil
import sys


source, destination, platform = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
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
if "  " + platform not in entries:
    entries.append("  " + platform)
effective = prefix + b"PLATFORMS\n" + "\n".join(sorted(entries)).encode() + b"\n\n" + suffix
(destination / "Gemfile.lock").write_bytes(effective)
print(f"Bundle platform: {platform}; locked gem versions unchanged")
