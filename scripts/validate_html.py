"""Validate generated local documentation without fetching external URLs."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


REQUIRED = {
    "swift": {
        "Classes/LoginManager.html": ["LoginManager", "login"],
        "Enums/API.html": ["API", "getProfile"],
        "Structs/AccessToken.html": ["AccessToken"],
        "Structs/UserProfile.html": ["UserProfile"],
    },
    "android": {
        "com/linecorp/linesdk/api/LineApiClient.html": ["LineApiClient", "getProfile", "verifyToken"],
        "com/linecorp/linesdk/auth/LineLoginApi.html": ["LineLoginApi", "getLoginIntent"],
        "com/linecorp/linesdk/auth/LineLoginResult.html": ["LineLoginResult"],
        "com/linecorp/linesdk/LineAccessToken.html": ["LineAccessToken"],
        "com/linecorp/linesdk/widget/LoginButton.html": ["LoginButton"],
    },
    "unity": {
        "class_line_1_1_line_s_d_k_1_1_line_s_d_k.html": ["LineSDK", "Login"],
        "class_line_1_1_line_s_d_k_1_1_access_token.html": ["AccessToken"],
        "class_line_1_1_line_s_d_k_1_1_login_result.html": ["LoginResult"],
        "class_line_1_1_line_s_d_k_1_1_user_profile.html": ["UserProfile"],
    },
}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.anchors = set()
        self.references = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("id", "name"):
            if attrs.get(key):
                self.anchors.add(attrs[key])
        for key in ("href", "src"):
            if attrs.get(key):
                asset = key == "src" or (tag == "link" and attrs.get("rel") in ("stylesheet", "icon"))
                self.references.append((attrs[key], asset))


def validate(sdk, directory):
    directory = directory.resolve()
    site = sorted(p for p in directory.rglob("*.html") if not any(part.endswith(".docset") for part in p.parts) and "metadata" not in p.relative_to(directory).parts)
    if not site or not (directory / "index.html").is_file() or not (directory / "index.html").stat().st_size:
        raise ValueError("Nonempty root index.html is required")
    pages = {p: Page(p.read_text(errors="replace")) for p in site}
    required = []
    for name, tokens in REQUIRED[sdk].items():
        matches = [p for p in site if p.as_posix().endswith("/" + name)]
        if len(matches) != 1:
            raise ValueError(f"Missing or ambiguous required API page: {name}")
        text = matches[0].read_text(errors="replace")
        if not all(token in text for token in tokens):
            raise ValueError(f"Required API content missing: {name}")
        required.append(str(matches[0].relative_to(directory)))
    if len(site) < {"swift": 20, "android": 15, "unity": 20}[sdk]:
        raise ValueError("Unexpectedly small API site")

    missing_files, missing_assets, missing_fragments, root_links, external = set(), set(), set(), set(), set()
    reference_count = 0

    def check(source, raw, asset):
        nonlocal reference_count
        url = urlsplit(raw)
        if url.scheme or url.netloc:
            if url.scheme in ("https", "http") or url.netloc:
                external.add(raw)
            return
        reference_count += 1
        if url.path.startswith("/"):
            root_links.add(raw)
            return
        target = (source.parent / unquote(url.path)).resolve() if url.path else source
        label = (str(source.relative_to(directory)), raw)
        if not target.is_relative_to(directory):
            root_links.add(raw)
            return
        if target.is_dir():
            target /= "index.html"
        if not target.is_file() or not target.stat().st_size:
            (missing_assets if asset else missing_files).add(label)
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].anchors:
            missing_fragments.add(label)

    for path, page in pages.items():
        for raw, asset in page.references:
            check(path, raw, asset)
    for path in directory.rglob("*.css"):
        if any(part.endswith(".docset") for part in path.parts):
            continue
        for raw in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", path.read_text(errors="replace")):
            check(path, raw, True)
    files = [p for p in directory.rglob("*") if p.is_file() and "metadata" not in p.relative_to(directory).parts]
    report = {
        "sdk": sdk, "site_html_count": len(site),
        "all_html_count": len(list(directory.rglob("*.html"))),
        "documentation_file_count": len(files), "documentation_bytes": sum(p.stat().st_size for p in files),
        "required_api_pages": required, "local_references_checked": reference_count,
        "missing_local_assets": sorted(missing_assets), "missing_local_files": sorted(missing_files),
        "missing_fragments": sorted(missing_fragments), "site_root_links": sorted(root_links),
        "external_urls_not_fetched": sorted(external),
        "passed": not missing_assets and not missing_files,
    }
    metadata = directory / "metadata"
    metadata.mkdir(exist_ok=True)
    (metadata / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("missing_fragments", "external_urls_not_fetched")}, indent=2))
    if not report["passed"]:
        raise ValueError("Local documentation links or assets are missing; see metadata/validation.json")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sdk", choices=REQUIRED)
    parser.add_argument("directory", type=Path)
    arguments = parser.parse_args()
    validate(arguments.sdk, arguments.directory)
