---
name: typesafe-ai
description: Design, implement, or evaluate TypeSafe System One and Jev integrations when TypeSafe/Jev is explicitly selected, named in the request, or already used by the feature being changed. Use for its typed decisions, question design, uncertainty, batching, API/SDK integration, and workflow composition. Do not activate for generic AI brainstorming or provider-neutral backend work.
license: MIT
---

# TypeSafe integration

This entrypoint scopes a vendor-maintained integration skill to tasks involving TypeSafe/Jev.
It does not make TypeSafe a default backend dependency or alter general software preferences.

Read [the pinned upstream skill](references/upstream.md) for the task's integration guidance.
The upstream instructions are preserved unchanged; its broader discovery description does
not expand this entrypoint's activation scope. Follow its targeted live-documentation workflow
for current SDK/API details; the pinned skill is not a frozen API specification.

Distinguish building software that calls TypeSafe from calling the existing Jev MCP tools.
Use the available Jev tool guidance when the task is to obtain a decision through those tools;
use this skill for integration design and implementation. Do not install duplicate plugins or
introduce a provider solely because its skill is present.

Preserve the user's selected stack and task scope. Keep credentials out of source and renderer
code. Installation or documentation review does not authorize paid requests, external data
transfers, or production mutations; validate integrations with fixtures unless those actions
are part of the authorized task.

Upstream origin, exact revision, original paths, and file hashes are tracked in the environment
manifest. The accompanying LICENSE preserves TypeSafe AI's attribution. This scoped entrypoint
and its UI metadata are local adaptations; the referenced upstream content is third-party.
