# Integration skills

Vendor integration guidance is separate from personal Design, Frontend, and Backend preferences.
An integration skill has `kind: skill`, `category: integration`, `provenance: third-party`, and
an `upstream` record in environment.json. Its source lives under shared/integrations/<id>.

## TypeSafe

Source: [typesafe-ai/skills](https://github.com/typesafe-ai/skills), MIT license.
Revision: `65a39f393687675ce170e6094757de20370365b9`.

- `references/upstream.md` is the exact upstream `skills/typesafe-ai/SKILL.md`.
- `LICENSE` is the exact upstream license, including attribution.
- `SKILL.md` is a local entrypoint that limits activation to TypeSafe/Jev work.
- `agents/openai.yaml` supplies local Codex UI metadata.

This skill helps build integrations. The existing Jev plugin provides callable MCP tools;
neither replaces the other. The import does not install a second MCP server, run an API request,
or establish authentication. Provider-neutral software skills remain independent.

Codex installs the complete source directory through its existing skill adapter. Other harnesses
should preserve the scoped entrypoint and vendor attribution through their own native adapters.
Claude Code remains responsible for its implementation; its upstream marketplace commands are
not automatically run by Codex.

## Reviewed updates

1. Select an explicit upstream commit. Inspect its diff, skill resources, and license before importing.
2. Fetch the skill and license at that exact commit into an ignored temporary directory. For
   TypeSafe, the Codex skill-installer helper supports `--repo typesafe-ai/skills --ref <commit>
   --path skills/typesafe-ai --dest <temporary-directory>`; fetch LICENSE at the same revision.
3. Replace the unchanged vendor files, retaining all necessary references/assets if upstream
   adds them. Keep local scope changes in the entrypoint, not inside the vendor reference.
4. Update the manifest's revision, file mappings, and SHA-256 hashes together. Review activation
   and behavior changes; pinning the skill does not pin the live vendor documentation it consults.
5. Run `python3 env.py validate`, the environment tests, and the harness skill validator. Preview
   and apply the owning harness adapter. Commit and push; other machines use normal sync.

Validation checks vendored file hashes offline. It detects accidental edits but does not prove
upstream authenticity by itself; the import review establishes the repository/revision link.
Do not add automatic upstream pulls or turn vendor recommendations into global preferences.
