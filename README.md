# SDK reference build experiment

A personal experiment that generates HTML API references from three pinned
public SDKs. It uses their existing documentation configurations and dependency
versions. The files are downloadable GitHub Actions artifacts, not a published
website or an official SDK release.

The three-job [verification run](https://github.com/soranakahara/sdk-reference-build-test/actions/runs/45308465230)
succeeded. See [results and retained limitations](docs/results-2026-11-24.md).

| SDK | Source | Pinned revision |
| --- | --- | --- |
| Swift | [line-sdk-ios-swift](https://github.com/line/line-sdk-ios-swift) | `230d05aab8ae48b6eeb893b9f257d7f5095d3352` |
| Android | [line-sdk-android](https://github.com/line/line-sdk-android) | `f18f8e27ff192d7a1a4ceaa379526b975f928838` |
| Unity | [line-sdk-unity](https://github.com/line/line-sdk-unity) | `b7925f2f5f4fab974422d5b6a5140f9b8e45c9a6` |

The SDKs are HTTPS Git submodules under `sdk/`. Their tracked source, dependency
versions, templates, and configuration files are unchanged. Input checksums are
recorded in [sources.lock.json](sources.lock.json).

Run **Build SDK references** manually from the Actions tab. Choose `all` (the
default) for all three independent jobs, or select one SDK for a focused rerun:

| Job | Hosted environment and generator | Artifact |
| --- | --- | --- |
| Swift | macOS 15 arm64, Xcode 16.4, Ruby 3.3.8, Bundler 4.0.10, locked SDK gems; invoke Jazzy directly | `swift-reference` |
| Android | Ubuntu 24.04, Temurin 11.0.33.1+1, Android API 33 / Build Tools 30.0.3, SDK Gradle 7.6 / AGP 7.3.1 / Doclava 1.0.6 | `android-reference` |
| Unity | Ubuntu 24.04, Ubuntu Doxygen, SDK Doxyfile; no Unity Editor or Graphviz | `unity-reference` |

Artifacts are retained for **7 days**. Each includes HTML, generation logs,
validation results, source revisions, and actual tool/dependency versions under
`metadata/`. Required API pages and local asset references are checked before
upload; an empty output is an error. The verifier also works offline:

```sh
python3 scripts/validate_html.py swift artifacts/swift
```

The workflow has only a manual trigger, `contents: read`, no persistent checkout
credentials, no shared dependency cache, and no publish/deploy/push step. It uses
public input only and no application secrets. Runner images and Ubuntu package
repositories change, so actual versions are captured for each run.

**Known dependency vulnerabilities are accepted for this bounded experiment.**
They have not been fixed here. See [risk and execution notes](docs/risk-notes.md)
for conditions, limits, bundled dependencies, and the temporary Swift platform
adjustment, which preserves every locked gem version. Installation authorization
covers the listed hosted-runner setup. It does not authorize local installations,
trust changes, deployment, schedules, upstream contributions, or notifications.
