# Claude Code: implementation pending

Owner: Claude Code. Felipe explicitly requested that Claude Code implement this itself.

Read the root README, environment.json, and docs/adapter-contract.md. Inspect the current Claude
Code documentation and local installation. Decide native locations, skill discovery, plugin or MCP
packaging, and configuration ownership yourself. No native Claude settings have been supplied.

Acceptance criteria:

- Consume the canonical no-ai-slop content without drifting its meaning.
- Reuse shared/tools/jev if your native tool interface supports it; supply your own wrapper and skill.
- Determine the supported Google Drive connection; document unsupported behavior or required login.
- Preserve vendor defaults and unrelated plugins, settings, rules, and credentials.
- Implement preview, apply, drift reporting, backup, idempotence, and isolated tests.
- Record current documentation sources and actual validation; then change adapter.json to implemented.
- Leave Codex's native adapter alone. Propose shared contract changes explicitly if necessary.

Until this work is done, `python3 env.py apply claude-code` exits with a clear pending message.
