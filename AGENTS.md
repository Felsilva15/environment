# Environment repository

Read README.md, environment.json, and docs/adapter-contract.md before changing this repository.

This repository is Felipe's source of truth for personal agent capabilities across computers.
Shared intent/content lives under shared/. Each harness owns harnesses/<id>/ and must use its
current native installation mechanisms. Do not translate another harness's configuration by
renaming product names. Codex may implement Codex; Claude Code must implement Claude Code.
Future harnesses should add their own adapter using the same contract.

Preserve vendor-managed defaults and unrelated plugins. Absence from the desired manifest is
never an uninstall instruction. Keep credentials, complete home-directory configs, machine
inventories, generated plugins, and authentication state out of Git. Use .local/ for local state.

Every adapter must preview changes, detect drift, back up replaced files, refuse conflicting
local edits, and converge on a second run. Changes to shared intent affect all adapters and
must be deliberate. Report unsupported capabilities instead of pretending they are installed.

Validation: python3 env.py validate; python3 -m unittest discover -s tests -v.
For the Jev runtime: npm ci --ignore-scripts and npm test in shared/tools/jev.
Tests must not use real credentials, send paid Jev requests, or modify the real home directory.

Do not implement another harness on its behalf. A routing note is acceptable; native settings,
skills, plugin wrappers, and installation commands belong to that harness's implementation.
