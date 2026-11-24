# SDK reference build experiment

A personal experiment that generates HTML API references from three public SDKs.
Sources are pinned by HTTPS Git submodule gitlinks. Their tracked source,
dependency versions, templates, and documentation configurations are unchanged.

Run **Build SDK references** manually from the Actions tab. It always runs three
independent jobs and retains these artifacts for **7 days**:

| SDK source | Hosted toolchain | Artifact |
| --- | --- | --- |
| [Swift](https://github.com/line/line-sdk-ios-swift) | macOS 15 arm64, Xcode 16.4, Ruby 3.3.8, Bundler 4.0.10, SDK-locked Jazzy | `swift-reference` |
| [Android](https://github.com/line/line-sdk-android) | Ubuntu 24.04, Temurin 11.0.33.1+1, Android API 33 / Build Tools 30.0.3, SDK Gradle and Doclava | `android-reference` |
| [Unity](https://github.com/line/line-sdk-unity) | Ubuntu 24.04, Ubuntu Doxygen | `unity-reference` |

The implementation is one [workflow](.github/workflows/references.yml) and two helpers:

- [prepare_swift_bundle.py](scripts/prepare_swift_bundle.py) copies the bundle definition and adds only the runner's Ruby platform. Locked gem versions stay unchanged.
- [android-javadoc.init.gradle](scripts/android-javadoc.init.gradle) supplies the compiled SDK/dependency classpath and enables failure on Javadoc errors.

Each job logs the source SHA and major tool versions, checks a nonempty index and
representative API pages, and uploads the generator's default output directory.
There are no metadata bundles, package inventories, or general link/CSS scanners.

The simplified workflow passed [run 45311731707](https://github.com/soranakahara/sdk-reference-build-test/actions/runs/45311731707):
all three jobs and artifacts succeeded. All 145 site HTML files were byte-identical
to the earlier verified run, and the search data was equivalent.

The workflow uses `workflow_dispatch`, `contents: read`, immutable action SHAs,
no persistent checkout credentials, and no shared cache. It does not deploy,
push, schedule jobs, or use application secrets.

Known dependency issues are accepted for this bounded hosted-runner experiment;
they are not fixed here. See [risk notes](docs/risk-notes.md) and the
[earlier detailed verification](docs/results-2026-11-24.md) for retained limitations.
Local tool installation, trust changes, deployment, upstream contributions, and
notifications are outside the authorized scope.
