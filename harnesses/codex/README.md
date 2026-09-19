# Codex adapter

Owner: Codex. Requires Python 3.10+, a Codex CLI with `plugin` commands, and Node.js 20+/npm for Jev.
Verified on macOS. Linux/Windows paths use Python's home resolution; native platform smoke tests
are still required before claiming those platforms verified. Windows users may need `python` rather
than `python3` and must provide a working native Codex executable.

CLI selection: explicit --codex, then ENVIRONMENT_CODEX_BIN, then the desktop app's
~/.codex/plugins/.plugin-appserver/codex when present, then codex on PATH. A standalone CLI
can omit the account-connected remote catalog; do not interpret that as proof an integration
was disconnected. Use the same desktop-backed CLI for installation and verification.

Bindings:

| Capability | Native resource |
| --- | --- |
| no-ai-slop | ~/.agents/skills/no-ai-slop, backed by shared/skills/no-ai-slop |
| software-design | ~/.agents/skills/software-design, backed by shared/skills/software-design |
| software-frontend | ~/.agents/skills/software-frontend, backed by shared/skills/software-frontend |
| software-backend | ~/.agents/skills/software-backend, backed by shared/skills/software-backend |
| typesafe-ai | ~/.agents/skills/typesafe-ai, backed by shared/integrations/typesafe-ai; pinned vendor reference and scoped entrypoint |
| jev | jev-decisions@felipe-environment, rendered under .local/codex/marketplace |
| google-drive | google-drive@openai-curated-remote |

The committed marketplace directory is a template, not a directly installable plugin: the builder
adds shared/tools/jev and runs npm ci before registering the generated marketplace. Do not register
harnesses/codex/marketplace directly. Use env.py apply codex.

The builder uses the official scaffold's marketplace shape. A content digest supplies the Codex
cachebuster because this reproducible sync workflow must produce the same version on every machine.
The app installs a native cache copy; editing a cached copy is never the source of truth.

Skills with kind `skill` and a source directory are installed when explicitly listed in this
adapter's capabilities. Add each new skill to environment.json and adapter.json; no per-skill
Python binding is needed. Each source must contain SKILL.md. Receipts track digests per skill
and recognize the original single-skill receipt when upgrading.

`retired_skills` declares specific authorized replacements, not a general prune policy.
The original combined skill is backed up outside discovery only when its content matches
the recorded digest and all replacements have been verified. A differing local copy blocks
apply before mutations, even with --adopt-existing; reconcile it explicitly first. Unknown
skills and plugins remain untouched. The migration is safe on machines that never had it.

Existing skills are adopted without replacement if identical. Updates replace only the managed
skill after checking its last receipt. All skill conflicts are checked before any installation.
Differing unmanaged copies require --adopt-existing and are
backed up under .local/codex/backups. The known legacy Jev registration requires the explicit
--migrate-legacy-jev flag and is removed only after the new version is installed and verified.

Rollback: select the previous repository commit and run apply; versions are content-derived.
For a locally edited skill, restore the relevant backup only after reviewing the conflict. Plugin
and remote authentication side effects are not transactional; a failed apply reports failure and
may have completed earlier steps. Run plan and retry after resolving the reported cause.

Plan/status inspect plugin registration, not OAuth/API usability. Test Drive access in a fresh Codex
task and call Jev's status tool to check credential presence without a paid decision request.
