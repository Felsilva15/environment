---
name: build-felipe-apps
description: Build or refine Electron desktop apps and operational web app interfaces using Felipe's UI and delivery preferences learned from Jev Mail. Use for app shells, top headers, sidebars, detail panes, themes, background work, and Electron delivery. Not a marketing-site style guide; preserve an existing project's framework and explicit task scope.
---

# Build Felipe Apps

Apply Felipe's preferences from **Build Jev Mail desktop app**. Treat these as defaults;
current instructions and the product's actual needs take precedence. A request to inspect,
explain, or plan remains that request; this skill does not authorize implementation or publishing.

## The app should feel like a desktop workspace

- Use the available window, with a compact navigation sidebar, one integrated top header,
  and a flexible work area. The references were the ChatGPT/Codex desktop layouts.
- Put navigation controls and the current page title in that top row. On macOS, integrate
  it with the native traffic lights; avoid a wasted title strip above another toolbar.
- Open selected records in a docked, resizable right pane. Keep the list usable, preserve
  selection across navigation, and let the user hide/reopen the pane with a header toggle.
- Keep long-running work out of the way: a dialog can minimize to visible progress while
  browsing continues. Show elapsed time, final duration, and distinct failures.
- Prefer shadcn/ui for new React UI: restrained neutral surfaces, thin borders, compact
  spacing, legible typography, and purposeful color. Avoid decorative gradients, oversized
  cards, excessive animation, and a generic AI-generated dashboard appearance.
- Offer System, Light, and Dark themes; default to System. Check actual content readability
  in both themes, including embedded documents with their own styles.

For layout work, read [the app-shell reference](references/app-shell.md). It defines the
top-header example, pane behavior, and which parts transfer to web apps.

## Build and deliver

For a new Electron app, the established starting point is Electron + React + TypeScript +
Vite/electron-vite + Tailwind + shadcn/ui, using **pnpm**. Preserve a working existing stack
unless the requested change calls for migration. Jev Mail's exclusion of Next.js applied
to that desktop app; it is not a ban on Next.js for web projects.

Read [Electron and delivery](references/electron-and-delivery.md) when setting up the
desktop runtime, native header, IPC, packaging, or validating an Electron release.

For both desktop and web apps:

- A finished app must run. Launch and exercise the changed workflow; a successful build
  alone is insufficient. Include startup instructions Felipe can follow without reading code.
- Keep task success, failure, pending state, and user-visible counts consistent. Do not
  report failed records as processed successfully or duplicate records to show audit history.
- Preserve useful local data and history. When a rerun only needs stored data, reuse it;
  fetching fresh provider data or executing external actions should be an explicit mode.
- For AI workflows, separate model decisions from deterministic execution policy. Surface
  the criteria and reasoning users need, with raw diagnostics available on demand. Show
  measured usage/cost where available and identify estimates; do not invent prices or totals.
- Put personal criteria and account-specific behavior in editable local settings. Public
  source, fixtures, and screenshots must not embed real inbox data or credentials. Preserve
  Felipe Silva's author attribution where applicable.

Use [the evidence notes](references/jev-mail-evidence.md) when deciding whether a detail was
an explicit preference or merely a Jev Mail implementation choice. Database, email provider,
Jev integration, and logo generation are not requirements for every app.
