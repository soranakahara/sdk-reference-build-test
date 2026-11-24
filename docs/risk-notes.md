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

The jobs use public input, `contents: read`, no application secrets, no persistent
checkout credentials, and no shared cache. Local installations, trust changes,
deployment, schedules, notifications, and upstream changes are not authorized.

## Build adjustments and limits

Swift copies Gemfile, Gemfile.lock, and Pluginfile into a temporary directory.
Only the lock's PLATFORMS section is adjusted; installation is frozen. Jazzy runs
directly with the original configuration/theme/copyright, avoiding fastlane hooks.
Android's parent init script supplies the compiled release classpath and sets
`failOnError=true`. Unity uses its original Doxyfile; no Editor or Graphviz is used.
Tracked SDK files are checked for changes after generation.

Source SHAs and major tool versions go to CI logs. Before upload, each job checks
its index and representative API pages with `test -s`. The workflow does not
perform a full dependency audit or general link/asset/anchor validation.

Known issues include the old Ruby/gem graph, Gradle 7.6, Guava r06 embedded in
Doclava ([GHSA-5mg8-w23w-74h3](https://github.com/advisories/GHSA-5mg8-w23w-74h3)),
and Doxygen's bundled GD issue ([CVE-2018-14553](https://www.cve.org/CVERecord?id=CVE-2018-14553)).
Fixed public inputs and disabled optional features do not prove these paths
unreachable. No independent security-fix verification is claimed.

The [earlier detailed run](results-2026-11-24.md) records existing Android header
background/favicon omissions, an unused CSS image reference, Swift fragment
link omissions, and site-root `/en/` links. These limitations are retained.
