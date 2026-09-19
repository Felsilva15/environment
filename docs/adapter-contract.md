# Adapter contract v1

An adapter turns shared capabilities into one harness's native installation. Its owning harness
must research and implement it. A new harness starts by reading AGENTS.md and environment.json.

## Registration

Create `harnesses/<id>/adapter.json` with schema_version 1, id matching its folder, owner,
status (`pending` or `implemented`), and a capabilities array of IDs from environment.json.
An implemented adapter additionally provides entrypoint, a Python module relative to its own
directory. It exports `execute(args, root, manifest)` and returns:

```json
{
  "harness": "example",
  "converged": false,
  "items": [{"id": "no-ai-slop", "status": "install", "detail": "Native destination"}],
  "unmanaged_plugins": []
}
```

The entrypoint may call its own native shell/Node/other tooling with argument arrays. Python is
only the common dispatcher, not a required implementation language for the underlying adapter.
`args.command` is plan, status, or apply; sync pulls and then delegates to apply. Adapter-specific
extensions should use an ignored `.local/<id>/settings.json` or extend the common CLI deliberately.

## Required behavior

1. **plan/status** inspect without changing files, installing packages, authenticating, or sending
   external model requests. Represent unsupported capabilities explicitly. A missing CLI is an error.
2. **apply** checks conflicts before mutations, applies only declared resources, backs up overwritten
   files, and verifies outcomes. Keep state and generated artifacts in `.local/<id>/`.
3. Use native installation commands for plugins and MCP integrations. Never sync caches, whole user
   config files, sessions, OAuth tokens, or API keys. Merge only adapter-owned configuration fields
   if the native harness lacks a CLI; preserve unrelated fields and document that choice.
4. Unknown resources and vendor defaults remain untouched. Plugin removal disconnects integrations
   and requires an explicit removal/migration request. No general prune command in v1.
5. Local edits are conflicts, not garbage. Store content hashes/receipts and back up before replacing.
   A second apply must perform no installation when the desired source and installed state match.
6. Authenticate separately per machine. Never claim an installed plugin is fully functional without
   a separate read-only authentication check. Do not make paid API requests as a health check.
7. Maintain one canonical meaning for shared skills. Reuse a portable skill when supported; if
   native translation is required, keep it in your adapter, record its source and validation,
   and do not invent capabilities the harness cannot execute.
8. Test with temporary homes and mocked command runners. Include fresh install, idempotence,
   local edits, failures, and preservation of unrelated data. Native smoke tests supplement fixtures.
9. Add documentation for bootstrap, prerequisites, updates, rollback, credentials, and supported OSes.
   Mark an adapter implemented only after its own harness has run its native validation.

## Ownership

Shared content changes affect every harness and require tests/review across implemented adapters.
Native details belong to harnesses/<id>. Do not edit another harness to make its config resemble yours.
An adapter can mark a capability unsupported with a reason until the owner supplies a native solution.

## Exit codes

The dispatcher uses 0 for successful validation, plan, or converged status/apply; 1 for reported
drift; 2 for operational errors, conflicts, pending adapters, or unsupported registration.
The plan document can contain drift while the preview command still succeeds.
