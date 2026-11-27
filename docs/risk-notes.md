# Risk and execution notes

This personal experiment has approval to use the pinned SDK dependencies with
known issues on disposable GitHub-hosted runners. It does not claim that the
tools are secure, fixed, or fully audited. No security patch is applied to Jazzy,
CocoaPods-Core, Doclava, embedded Guava, or Doxygen/GD.

## Installation scope

| Component | Public source and method | Hosted destination |
| --- | --- | --- |
| Ruby 3.3.8 / Bundler 4.0.10 | Pinned `ruby/setup-ruby`; Ruby builds and RubyGems | macOS runner tool cache |
| Swift gems | RubyGems, frozen SDK bundle | `$RUNNER_TEMP/sdk-reference/gems` |
| Xcode 16.4 | Select the preinstalled application | No installation |
| Temurin 11.0.33.1+1 | Adoptium archive with SHA-256 verification | `$RUNNER_TEMP/sdk-reference/jdk` |
| Android API 33 / Build Tools 30.0.3 | Preinstalled Google `sdkmanager` | Runner Android SDK directory |
| SDK Gradle and dependencies | Official wrapper, Google Maven and Maven Central | `$RUNNER_TEMP/sdk-reference/gradle` |
| Doxygen | Ubuntu official apt repositories | Disposable Ubuntu package directories |
| Checkout / artifact actions | GitHub, pinned commits | Runner action directory |

Generation jobs use public input and `contents: read`. The publication job alone
requests `contents: write` and `actions: read`, using only this repository's
`GITHUB_TOKEN` with preinstalled Git, gh, and jq. Checkout credentials are not
persisted, and no custom secrets or shared caches are used. The publication
script authenticates only to the fixed public GitHub repository and pushes only
the generated branch. The separate manual Pages workflow reads configuration
with `pages: read` and deploys with `pages: write` and `id-token: write` only in
its deployment job. Its official Actions are pinned to commits; automatic Pages
enablement is disabled. Adding this definition does not authorize running it or
changing Pages settings. Local installations, trust changes, actual deployment,
schedules, notifications, and upstream changes require separate authorization.

## Build adjustments and limits

Swift copies Gemfile, Gemfile.lock, and Pluginfile into a temporary directory.
`bundle lock --add-platform` adds the runner platform there. Before the frozen
install, `Bundler::LockfileParser` compares unique gem name/version pairs, so
platform-specific spec additions do not count as version changes. Jazzy runs
directly with the original configuration/theme/copyright, avoiding fastlane hooks.
Android's parent init script supplies the compiled release classpath and sets
`failOnError=true`. Unity uses its original Doxyfile; no Editor or Graphviz is used.
Tracked SDK files are checked for changes after generation.

Source SHAs and major tool versions go to CI logs. Before upload, each job checks
its index and representative API pages with `test -s`. The workflow does not
perform a full dependency audit or general link/asset/anchor validation.

After all three generation jobs succeed, publication downloads their artifacts
from the same run, validates representative pages/assets and actual SDK commits,
and commits the complete snapshot once. It preserves generated-branch history
with a normal push. Default-branch, concurrency, and stale-run checks protect
against unintended or out-of-order publication; see the README for the contract.

The Pages workflow checks out the supplied commit and copies `swift/`, `android/`,
`unity/`, and `build-info.json` into the Pages artifact. Only the Pages copy of
the known site-root `/en/` navigation links is adjusted to the public developer site;
upstream analytics tags and other output limitations remain. No SDK build,
dependency installation, Pages configuration change, or deployment has been
performed to validate this workflow definition. See the README for manual
prerequisites, browser checks, and rollback by snapshot SHA.

Known issues include the old Ruby/gem graph, Gradle 7.6, Guava r06 embedded in
Doclava ([GHSA-5mg8-w23w-74h3](https://github.com/advisories/GHSA-5mg8-w23w-74h3)),
and Doxygen's bundled GD issue ([CVE-2018-14553](https://www.cve.org/CVERecord?id=CVE-2018-14553)).
Fixed public inputs and disabled optional features do not prove these paths
unreachable. No independent security-fix verification is claimed.

The [earlier detailed run](results-2026-11-24.md) records existing Android header
background/favicon omissions, an unused CSS image reference, Swift fragment
link omissions, and site-root `/en/` links. These limitations are retained.
