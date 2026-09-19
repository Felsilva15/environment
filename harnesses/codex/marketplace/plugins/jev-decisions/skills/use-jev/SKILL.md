---
name: use-jev
description: Use TypeSafe Jev for fast probabilistic classification, scoring, or bounded decisions when the user asks for Jev or a compact decision model would materially help.
---

# Use Jev

Use the Jev MCP tools for narrow judgment tasks: binary probability (`jev_noul`), categorical selection (`jev_choice`), rubric scoring (`jev_score`), or several related questions in one request (`jev_decide`).

Before calling a Jev tool, select only the state needed for the decision. The state is sent to TypeSafe's API, so exclude passwords, API keys, authentication tokens, private credentials, and unrelated sensitive data. Tell the user when this external transfer would not already be obvious from their request.

Treat Jev output as advisory evidence. Preserve its probability, confidence, or distribution when reporting a result, and do not present a thresholded answer as certainty. Use deterministic code for arithmetic, exact validation, and rules that do not require judgment.

Prefer one batched `jev_decide` call when multiple questions share the same state. Give choices and rubric criteria concrete, mutually distinguishable descriptions. If `jev_status` reports that authentication is missing, explain how to run `node shared/tools/jev/scripts/configure-key.mjs from the environment repository`, then stop instead of inventing an answer from Jev.
