# Repository instructions

This public repository experiments with HTML API reference generation from public SDK sources.

- Keep repository files and commit metadata suitable for public disclosure. Use only public source URLs and public SDK information.
- Do not add credentials, local configuration, private service URLs, internal reports, or personal filesystem paths.
- Obtain explicit user permission before installing or updating external tools and packages, including on hosted runners. State the package, source, method, and destination.
- Publish complete HTML snapshots to the generated Git branch; use Actions artifacts for CI handoff. A manual Pages deployment workflow is defined; running it or changing Pages settings requires separate user authorization, as do scheduled execution, notifications, and upstream contributions.
- This personal experiment has approval to use the SDK dependencies with known issues on disposable hosted runners. Do not describe them as fixed or free of vulnerabilities; see docs/risk-notes.md.
- Keep source pins in the submodule gitlinks, log source SHAs and major tool versions, and check a nonempty index and representative API pages before upload.
- Keep required build adjustments outside the SDK submodules. Prefer standard commands and keep the workflow and Android init script simple; retain historical results as records of their original runs.
- For this public experiment, use the author and committer identity `soranakahara <40860127+soranakahara@users.noreply.github.com>`. Do not use corporate signatures or corporate email trailers; the user explicitly approved their omission for this experiment.
