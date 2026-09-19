# Provenance

| Item | Origin | Repository policy |
| --- | --- | --- |
| no-ai-slop | Felipe's existing authored/personal skill | Canonical source in shared/skills; initially imported unchanged |
| Jev integration | Existing local plugin naming Felipe Silva as author | Shared runtime plus Codex-owned packaging; third-party notice preserved |
| Google Drive | OpenAI curated integration, intentionally restored | Install by native plugin ID; authentication remains local |
| Codex system/runtime/default skills | Vendor-managed | Do not vendor, delete, or synchronize their caches |
| Former Cursor-derived skills and Claude Cowork imports | Previous cleanup | Not part of desired state; no automatic removal on other computers |

The previous cleanup incorrectly treated all curated skills as optional. Plugin Management and
default artifact templates are installed by default. Sites was re-provisioned by the environment
after its cache was removed. These observations are why this repository never prunes unknowns
or equates a skill's storage directory with authorship.

This public repository contains selected source only. It does not contain a dump of either
harness's home directory, account connections, transcripts, auth stores, or machine inventory.

Jev runtime attribution: see shared/tools/jev/THIRD_PARTY_NOTICES.md.
