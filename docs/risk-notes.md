# Risk and execution notes

This personal experiment intentionally uses pinned SDK dependency versions with
known issues, with explicit approval for disposable hosted-runner execution. It
does not claim that the tools are secure, fixed, or fully audited. No security or
compatibility patch is applied to Jazzy, CocoaPods-Core, Doclava, Guava, or GD.

## Authorized installation scope

| Component | Public distributor and method | Destination |
| --- | --- | --- |
| Ruby 3.3.8 / Bundler 4.0.10 | Pinned `ruby/setup-ruby` action; Ruby builds and RubyGems | macOS hosted runner's tool cache |
| Swift gems | RubyGems, `bundle install` with the SDK's locked gem versions | `$RUNNER_TEMP/sdk-reference/gems`, without a shared cache |
| Xcode 16.4 | Select the preinstalled macOS runner application | No installation |
| Temurin JDK 11.0.33.1+1 | Exact Eclipse Adoptium archive, SHA-256 verified before extraction | `$RUNNER_TEMP/sdk-reference/jdk` on the Ubuntu runner |
| Android API 33 / Build Tools 30.0.3 | Preinstalled Google's `sdkmanager`; install missing packages from Google | Hosted runner's Android SDK directory |
| Gradle 7.6 and declared dependencies | SDK wrapper, official Gradle distribution, Google Maven and Maven Central | `$RUNNER_TEMP/sdk-reference/gradle` |
| Doxygen | Ubuntu official apt repositories, `apt-get install --no-install-recommends doxygen` | Disposable Ubuntu hosted runner's package directories |
| Checkout and artifact actions | GitHub, immutable action commits recorded in the workflow | Hosted runner's action directory |

No local tool installation is needed. No environment-variable dump or complete
Git configuration is recorded. Metadata records only selected runner/run
identifiers, versions, dependency reports, and public input hashes.

Swift's Gemfile, lock, and Pluginfile are copied into a temporary bundle
directory. The runner Ruby's platform can be added to that lock's PLATFORMS
section; the script verifies all other bytes remain unchanged. Installation is
then frozen. Both original and effective lock hashes and the adjustment are
recorded, and the tracked SDK files are unchanged.

## Known issues and relevance to this run

- **Ruby 3.3.8** predates the Ruby project's November 2026 security fixes. Source parsing, strings, and regular expressions remain attack surfaces. Pinned public inputs limit variability but do not repair the runtime.
- **ActiveSupport 7.2.3.1**, **Addressable 2.9.0**, **JSON 2.21.1**, **Mustache 1.1.2**, **Rubyzip 2.4.1**, and **SQLite3 gem 1.7.3** in the Swift lockfile match published advisories. Records include [GHSA-8474-xrp6-wh69](https://github.com/advisories/GHSA-8474-xrp6-wh69), [GHSA-5hrj-7fc3-cmx9](https://github.com/advisories/GHSA-5hrj-7fc3-cmx9), and [GHSA-28hh-pr2h-2w89](https://github.com/advisories/GHSA-28hh-pr2h-2w89). Jazzy uses the fixed SDK theme and a local docset index; this is not proof that every vulnerable path is unreachable. All locked gems are installed, although fastlane is not invoked.
- **Gradle 7.6** has known issues, and plugin/dependency downloads introduce supply-chain exposure. The workflow uses the original wrapper and public dependency definitions; it does not eliminate those risks.
- **Doclava 1.0.6** embeds **JSilver 1.0.0** and **Guava r06**. Guava matches [GHSA-5mg8-w23w-74h3](https://github.com/advisories/GHSA-5mg8-w23w-74h3), concerning permissions on temporary directories. Static inspection found no `createTempDir` reference in non-Guava classes in this JAR. The original JAR is used without repackaging; a no-match result for Doclava would not clear its embedded code.
- **Ubuntu Doxygen** includes a GD copy affected by [CVE-2018-14553](https://www.cve.org/CVERecord?id=CVE-2018-14553). C# input and `HAVE_DOT=NO` do not remove the bundled library or prove its affected functions unreachable. No GD backport is applied.

These observations are specific to this public-input documentation run. They are
not a complete reachability proof, full dependency audit, or guarantee against
unknown vulnerabilities. Dependency reports and package inventories accompany
the HTML for later assessment.

## Isolation and output checks

The independent jobs use GitHub-hosted runners with `contents: read`, no
persistent checkout credentials, no shared cache, no application secrets, and no
deployment or repository-write operation. Installing/running tools still
executes third-party code on those runners. This is the accepted boundary.

Swift invokes Jazzy directly, preserving `.jazzy.yaml`, the theme, and copyright
meaning while avoiding fastlane's `before_all` and release actions. Android
uses Doclava and the SDK templates, including `@hide`. Unity uses the original
Doxyfile with only an external output-directory override.

The validator checks a nonempty index, representative API pages and symbols,
local scripts/styles/images, and reports navigation-link and fragment failures
separately. A directory alone is never success. Existing templates can contain
external links and analytics; the offline validator reports these without
fetching them. Browser inspection uses local copies with external requests blocked.
