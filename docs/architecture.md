# Architecture decisions

## Shared intent; native adapters

The desired state describes response style, Jev, and Google Drive. Those are capabilities, not
universal plugin identifiers. Each harness resolves its own native representation. This prevents
the earlier failure mode where Cursor instructions were relabeled Codex but retained Cursor paths.

Use the Agent Skills format for portable content when appropriate, but do not assume all harnesses
support the same discovery directories, frontmatter, hooks, MCP schema, or plugin lifecycle.

## Additive reconciliation

Unlisted does not mean unwanted. Vendor-managed skills can appear after runtime updates, and
removing a skill-bearing integration can disconnect useful tools. We therefore install/update
declared resources and report unknowns. Removal is a separate deliberate operation. The explicit
legacy Jev migration is narrow, verified, and does not become a general cleanup policy.

## Content and package versions

Git pins authored source. Jev's npm lockfile pins runtime dependencies. Generated Codex plugin
versions include a digest of the native templates and shared runtime, so changed code gets a new
cache identity while unchanged code is idempotent. Remote Google Drive resolves the version the
marketplace currently supplies; it is not falsely presented as reproducibly pinned. Vendor defaults
remain on the harness vendor's update channel.

## Local state and credentials

Receipts and backups live under ignored .local/. Each clone is per machine; do not cloud-sync that
directory. Authentication stays in the harness's secure store, environment, or macOS Keychain.
The existing codex-jev-typesafe Keychain service name is retained for compatibility; other harnesses
may reuse the shared runtime without copying keys. There is no secret discovery/export mechanism.

## Update orchestration

Start with an explicit fast-forward sync command. No always-running daemon, remote shell fleet
controller, or platform-specific scheduled jobs are required to bootstrap. Add per-machine scheduled
checks later; only verified adapters should automatically apply updates. Pin a Git release/tag if
machines need a slower update channel. Offline machines reconcile when they next run sync.

## Evidence and documentation

Verified 2026-09-19 against the local Codex CLI's plugin add/list/remove and marketplace commands,
and the Plugin Creator scaffold/validator. Native commands take precedence over guessing schemas.

- [Agent Skills specification](https://agentskills.io/specification)
- [OpenAI plugin packaging and local marketplaces](https://developers.openai.com/plugins/build/plugins)

Claude Code and future harness internals are intentionally unimplemented, not presumed compatible.
