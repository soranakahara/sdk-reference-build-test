# SDK reference build experiment

A personal experiment that generates HTML API references from three public SDKs.
Sources are pinned by HTTPS Git submodule gitlinks. Their tracked source,
dependency versions, templates, and documentation configurations are unchanged.

Run **Build SDK references** manually from the Actions tab. It always runs three
independent generation jobs and retains these CI artifacts for **7 days**:

| SDK source | Hosted toolchain | Artifact |
| --- | --- | --- |
| [Swift](https://github.com/line/line-sdk-ios-swift) | macOS 15 arm64, Xcode 16.4, Ruby 3.3.8, Bundler 4.0.10, SDK-locked Jazzy | `swift-reference` |
| [Android](https://github.com/line/line-sdk-android) | Ubuntu 24.04, Temurin 11.0.33.1+1, Android API 33 / Build Tools 30.0.3, SDK Gradle and Doclava | `android-reference` |
| [Unity](https://github.com/line/line-sdk-unity) | Ubuntu 24.04, Ubuntu Doxygen | `unity-reference` |

The implementation is one [workflow](.github/workflows/references.yml) plus
[android-javadoc.init.gradle](scripts/android-javadoc.init.gradle), which supplies
the compiled SDK/dependency classpath and enables failure on Javadoc errors.

Swift uses `bundle lock --add-platform` on a temporary bundle copy. Before the
frozen install, Bundler's lockfile parser checks that gem names and versions are
unchanged, allowing duplicate specs for different platforms.

Each job logs the source SHA and major tool versions, checks a nonempty index and
representative API pages, and uploads the generator's default output directory.
There are no package inventories or general link/CSS scanners. A fourth job
publishes a complete Git snapshot after all three generation jobs succeed.

Generation was previously verified in [run 45339524894](https://github.com/soranakahara/sdk-reference-build-test/actions/runs/45339524894):
all three generation jobs and artifacts succeeded, with all 137 locked gem name/version
pairs unchanged. All 145 site HTML files were byte-identical to the previous
verified run, and the search data was equivalent.

## Generated branch contract

The public `generated` branch is the downstream delivery interface. Its root is:

```text
swift/             # index.html, API pages, and assets
android/           # index.html, API pages, and assets
unity/             # index.html, API pages, and assets
build-info.json
```

`build-info.json` contains these provenance fields:

| Field | Value |
| --- | --- |
| `source_repository` | `https://github.com/soranakahara/sdk-reference-build-test` |
| `source_commit` | The generating workflow's `GITHUB_SHA`, not the generated-branch commit |
| `workflow_run` | The public GitHub Actions run URL for that build |
| `workflow_run_number` | Numeric `GITHUB_RUN_NUMBER`, retained in Git to reject older runs without querying past Actions runs |
| `sdks` | `swift`, `android`, and `unity`: the actual 40-character SDK checkout commits, verified against the source commit's gitlinks |

Artifacts are the internal handoff between jobs and remain available for seven
days for inspection. Downstream consumers fetch a public Git snapshot instead
of calling the Actions artifact API. Workflow/configuration remain on `main`;
only the three SDK directories and provenance are committed to `generated`.

## Run and inspect

After the workflow change is merged, dispatch it from `main`:

```sh
gh workflow run references.yml --repo soranakahara/sdk-reference-build-test --ref main
```

Check all four jobs, including the publication log. Then clone the output into
a new directory and check that provenance names the expected source commit/run:

```sh
git clone --single-branch --branch generated https://github.com/soranakahara/sdk-reference-build-test.git sdk-reference-snapshot
cat sdk-reference-snapshot/build-info.json
```

Each Git commit is one complete snapshot: all three SDKs plus provenance. A
failed generation, artifact download, or validation leaves the previous output
untouched. Publication rejects unexpected root entries rather than deleting
unrelated files. Concurrent push conflicts fail without force-pushing or
rewriting history.

Only manual runs from this repository's `main` branch can publish. Generation
jobs retain `contents: read`; only publication gets `contents: write` and
`actions: read`, using the repository's `GITHUB_TOKEN` and preinstalled tools.
The workflow uses pinned action commits, no persistent checkout credentials,
no shared cache, no custom secrets, and no deployments, notifications, or cron.

Runs on the same source ref are serialized without canceling the active run.
GitHub can replace pending runs; the queue is not FIFO. Publication skips if
`main` has advanced or if a higher workflow run number is already published.
Missing or invalid stored run numbers stop publication. Inspect the log
when a successful build does not advance `generated`, and dispatch a fresh run
from current `main` when needed.

A new dispatch may create a provenance-only commit even when the HTML is
identical, because its run URL changes. Retrying publication for the same run
is a no-op when both output and provenance are identical. Downstream change
detection should compare HTML under the SDK directories, not `build-info.json`.
Expired artifacts require a fresh dispatch rather than a publication-only retry.

The linked successful run above validates generation only. The publication
change has been tested locally with fixtures and bare Git repositories; hosted
publication has not yet been exercised.

Known dependency issues are accepted for this bounded hosted-runner experiment;
they are not fixed here. See [risk notes](docs/risk-notes.md) and the
[earlier detailed verification](docs/results-2026-11-24.md) for retained limitations.
Local tool installation, trust changes, deployment, upstream contributions, and
notifications are outside the authorized scope.
