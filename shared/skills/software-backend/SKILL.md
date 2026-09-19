---
name: software-backend
description: Build or review backend services, persistence, integrations, and background jobs with clear contracts, dependable state, and controlled side effects. Use for server logic or privileged desktop services. Keep database, provider, framework, and hosting choices driven by requirements; visual styling belongs to Design and UI implementation to Frontend.
---

# Backend

Build the smallest backend structure that supports the requested software reliably. Preserve
the current stack and task scope. No database, cloud, provider, ORM, or backend framework is
a universal preference; do not inherit one from an unrelated project.

## Boundaries

Keep transport/API handlers, application rules, external integrations, and persistence
separable where those concerns exist. Use feature-level modules or the repository's established
organization. A small application can keep these boundaries in a few files; do not introduce
microservices, queues, or layers solely to match a template.

Validate inputs at trust boundaries and give clients predictable typed results and errors.
Keep credentials and privileged operations server-side or in a desktop app's main/service
process. Put personal criteria and account-specific behavior in editable configuration rather
than public source or fixtures. Make the configured decision criteria inspectable when users
need to understand automated behavior.

## State and jobs

- Keep durable records distinct from run history. Present a current record once while
  preserving the history needed for audit and diagnosis.
- Reuse stored data when a rerun only needs existing inputs. Distinguish recomputation,
  provider refresh, and external mutation so repeating an analysis does not unexpectedly
  repeat a real-world action.
- Keep long-running execution independent of the client's current page. Expose an observable
  state with completed, pending, and failed counts, timestamps, and useful error details.
- Bound concurrency and isolate item failures for batch jobs. A failed item must not appear
  successful or erase completed work. Decide retryability explicitly; retries must not
  duplicate side effects. Preserve enough state to resume when the workflow requires it.
- Apply schema migrations and transactional boundaries appropriate to the persistence needs.
  Do not reset existing user data to make a new implementation easier.

## Integrations and model-assisted decisions

Keep provider adapters separate from product rules. Use current documented APIs and honor
timeouts/rate limits; communicate disconnected or partially failed states accurately.

When models propose decisions, use validated outputs and deterministic policy to govern
external actions. Keep proposed decisions and actual execution results distinguishable.
Expose useful explanations and diagnostics without putting secrets in logs. Record actual
usage when available; label estimates and configure pricing instead of inventing costs.

This does not require every application to use a model, an agent framework, or an external
provider. Select those only when the requested behavior needs them.

## Verification and delivery

Use isolated data and mocked providers for failure, retry, duplicate-action, and partial-success
tests relevant to the change. Verify migrations against a disposable database when changed.
Do not send paid model requests or mutate live third-party data as an implicit health check.

Document configuration names, startup commands, persistence setup when needed, and recovery
steps for material failure modes. Report measured outcomes and missing external configuration.
Use the available Frontend skill when client integration is also requested; do not expand a
backend-only task into an interface redesign.
