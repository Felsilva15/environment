# Environment

Felipe's personal agent environment, versioned across computers and harnesses.

The repository stores **desired capabilities and authored source**. Each harness owns the native
adapter that installs them. A Codex configuration is never converted into a Claude Code
configuration by changing product names.

## Current status

| Harness | Owner | Status |
| --- | --- | --- |
| Codex | Codex | Implemented; tested on this Mac plus isolated fixtures |
| Claude Code | Claude Code | Pending by design; see its onboarding brief |
| OpenClaw, Hermes, DeepSeek, others | Their respective harnesses | Add an adapter when requested |

Desired capabilities:

- `no-ai-slop`: Felipe's canonical response-style skill.
- `software-design`: simple neutral UI, layout, visual hierarchy, and interaction preferences.
- `software-frontend`: components, UI state, web/Electron boundaries, and runtime verification.
- `software-backend`: contracts, persistence, integrations, and reliable background work.
- `jev`: Felipe's Jev integration, with a shared MCP runtime and native harness packaging.
- `google-drive`: intentionally retained third-party integration, not a custom skill.

Vendor defaults remain vendor-managed. Unlisted integrations are reported, never deleted.

The three software skills use neutral names and reusable guidance without prior-project
examples. Load only the roles relevant to the task; a full-stack feature can use all three.
Codex replaces the earlier combined skill through an explicit migration: install its replacements,
verify them, and back up the known unchanged old skill outside discovery. Local edits block
that migration. Other harnesses own their corresponding migration if they installed the old skill.

## Another computer

Prerequisites: Git, Python 3.10+, the target harness installed and signed in; Node.js 20+ and npm for Jev.

```sh
git clone https://github.com/Felsilva15/environment.git
cd environment
python3 env.py validate
python3 env.py plan codex
python3 env.py apply codex
python3 env.py status codex
```

The adapter prefers the desktop app's CLI when present, then Codex on PATH. A standalone CLI
may not expose account-connected remote plugins. Use `--codex /path/to/codex` or set
`ENVIRONMENT_CODEX_BIN` to select a specific installation; status --json reports the chosen binary.
If an existing `jev-decisions@personal` is found, preview it and run:

```sh
python3 env.py apply codex --migrate-legacy-jev
```

This installs and verifies the repository plugin before removing only the known old Jev
registration. It does not delete the old source folder or its Keychain credential. Differing
local copies of managed skills require `--adopt-existing`; they are backed up first.

Authentication is local. Connect Google Drive when prompted. For Jev, set `TYPESAFE_API_KEY`
in the harness environment, or on macOS run:

```sh
node shared/tools/jev/scripts/configure-key.mjs
```

Never put keys into this repository. Installation success is not proof that an account is authorized.

## Keep machines current

Commit and push intentional source changes from the computer where you make them. On each other
computer, run:

```sh
python3 env.py sync codex
```

`sync` requires a clean working tree, pulls with `--ff-only`, then re-executes the updated adapter
to apply the desired state. It refuses automatic merges/stashes. `status` exits nonzero on drift
and supports `--json`, making it usable by a future OS scheduler. Nothing runs in the background
yet; a Git repository alone cannot make an offline computer update. Schedule sync separately on
each machine only after that machine's adapter and authentication have been verified.

## Layout

```text
environment.json          desired capabilities and provenance
shared/skills/            canonical portable skills
shared/tools/             reusable tool implementations, not credentials
harnesses/<id>/           native adapter, packaging, status, and documentation
docs/adapter-contract.md  contract for new harnesses
.local/                   ignored receipts, generated packages, backups, and locks
```

## Let Claude Code implement itself

Open this repository in Claude Code and say:

> Read CLAUDE.md and implement the Claude Code adapter under harnesses/claude-code. Discover
> your current native skill/plugin/MCP mechanisms, use the shared capabilities, and follow
> docs/adapter-contract.md. Do not modify the Codex adapter or overwrite unrelated user settings.
> Test in an isolated home, then preview and apply on this computer. Document authentication
> separately and mark unsupported integrations honestly.

Claude Code owns its native choices. Codex has created only the routing note and neutral contract.
Other harnesses follow the same entry point in `AGENTS.md`; no speculative adapters are shipped.

## Development

```sh
python3 env.py validate
python3 -m unittest discover -s tests -v
cd shared/tools/jev
npm ci --ignore-scripts
npm test
```

See [architecture](docs/architecture.md), [provenance](docs/provenance.md), and
[Codex adapter details](harnesses/codex/README.md). Shared intent is deliberate; local discoveries
must not silently expand the desired manifest.
