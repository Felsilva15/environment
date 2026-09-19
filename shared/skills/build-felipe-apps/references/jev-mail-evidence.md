# Evidence and scope

Derived from Felipe's **Build Jev Mail desktop app** task on 2026-09-19, including its original
brief, subsequent corrections, header/sidebar reference images, and the implemented app.
This is a sanitized preference record, not a transcript or an assertion that every implementation
choice was explicitly approved. Times below are UTC, matching the task record.

| User instruction | Resulting reusable preference |
| --- | --- |
| Initial brief: local app that actually runs; dense, auditable interface | Operational UI and working delivery; visible evidence behind decisions |
| 17:31: needs a README explaining startup | Handoff must be runnable without reading implementation code |
| 17:39: use pnpm | Default package manager for new apps in this workflow |
| 20:23: minimize task dialog to progress; browse records; use shadcn/ui | Nonblocking jobs, usable detail views, restrained component-based UI |
| 20:45: test the actual app; stop task processes afterward | Runtime verification and clean handoff |
| 20:59: use the MacBook screen; second pane like ChatGPT Toggle side panel | Available-space layout with persistent docked detail pane |
| 21:22: use the top area like ChatGPT; header image supplied | Unified native header rather than unused top chrome |
| 21:27: sidebar like ChatGPT desktop; image supplied | Compact continuous sidebar, scrollable navigation, stable footer |
| 21:43: editable private criteria; keep author name; formatted reading | Separate personal configuration from public source; preserve readable content |
| 22:00: rerun from stored data | Avoid unnecessary provider fetching when local data is sufficient |
| 22:12: elapsed/final duration; dark mode defaulting to system | Honest task timing and System/Light/Dark appearance |
| 22:28–22:31: create and apply a logo for this app | Consistent identity when assets are part of the request |
| 22:53: unreadable content and duplication | Check embedded-content contrast; current records appear once, with history separately accessible |

Implementation corroboration came from `src/main/index.ts`, `src/main/appearance.ts`,
`src/renderer/src/App.tsx`, `styles.css`, sidebar/reader/progress/appearance components,
the README, UI tests, and rendered app images in the Jev Mail project. The native header
options, 52px height, 264px sidebar, traffic-light offsets, and divider bounds were implementation
choices supporting the requested experience; preserve the behavior, not exact measurements.

The request about duplicate content led to deduplicated message rows with separate audit
history. It is not evidence that all repeated brand marks or titles were rejected.

The original desktop stack was Electron/React/TypeScript/Vite/Tailwind with typed preload.
PostgreSQL, Drizzle, Gmail, provider authentication, classification criteria, and Jev belonged
to this product's requirements. Do not turn them into dependencies for unrelated apps.

Remote-image fetching was still being questioned at the review cutoff. Treat it as unresolved,
not as a settled preference to always block or always load remote assets. The later question
about Jev computer use also did not authorize automatic computer-control integrations.

No real email content, personal classification rules, account identifiers, credentials,
raw conversation dumps, or screenshots are included in this portable skill.
