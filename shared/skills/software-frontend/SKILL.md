---
name: software-frontend
description: Implement and validate software frontends with reusable components, accessible interactions, responsive layouts, persistent UI state, and clear runtime boundaries. Use for web interfaces and Electron renderers or desktop shells. Apply simple neutral styling; use the Design skill for visual direction and Backend for server or job logic.
---

# Frontend

Implement the requested interface using the project's existing conventions. Keep current
scope intact: a review or explanation does not authorize a rewrite. These are implementation
preferences, not a requirement to reproduce another product's architecture.

## Framework and component choices

- For a new React interface with no chosen stack, prefer TypeScript, Tailwind, and shadcn/ui,
  using pnpm. Preserve an established framework and package manager unless migration is
  part of the request. Choose web routing/rendering based on the app's needs.
- Use shadcn as the reference for consistent, accessible components; customize shared tokens
  rather than styling each instance independently. Keep the interface simple and neutral.
- Inspect the existing shadcn configuration before adding components. Use its chosen primitive
  base consistently; do not mix Radix and Base UI APIs or replace it merely because another
  preset exists. Add libraries only for actual requirements.
- For an Electron target, a React/TypeScript/Vite renderer is a suitable starting point.
  A request for a web app does not imply Electron, and matching ChatGPT's appearance does
  not require duplicating its entire dependency tree.
- Read [reference technology evidence](references/reference-technology.md) when asked about
  ChatGPT's libraries or design tooling. It separates observed packages from recommendations.

## Components and state

Keep a reusable shell, UI primitives, feature components, and data-access boundary distinct.
Follow existing feature organization; do not mandate a large folder hierarchy for a small app.
Separate server data, local presentation state, and persisted user preferences.

For a workspace layout, implement a single header, collapsible sidebar, and optional docked
detail pane. Keep selection separate from pane visibility. Preserve relevant scroll/selection
state while navigating. Bound splitter sizes and provide keyboard control. On narrow screens,
adapt navigation and detail presentation before reducing either pane to an unusable width.

Use grid/flex with `min-width: 0` and `min-height: 0` so each scroll region behaves correctly.
Keep persistent inspectors nonmodal; reserve focus trapping and dimmed backdrops for real
dialogs. Label icon buttons, show focus, and restore focus when a temporary surface closes.

Jobs must survive page changes. Render progress from authoritative task state, including
elapsed time, final duration, and failures. Do not put job execution in a component's mount
lifecycle or show false success when an API request fails.

Default appearance to System and follow live system changes until an explicit override is
selected. Persist overrides. Sanitize untrusted rich content and preserve readable foreground/
background pairs. Make remote-content behavior explicit for the product's privacy needs.

For native windows, preload/IPC, and desktop launch validation, read
[Electron implementation](references/electron.md). Keep secrets and privileged operations
behind the appropriate server or main-process boundary.

## Verification and handoff

Exercise the actual changed workflow with representative or synthetic data. Build success
does not establish runtime usability. Check relevant interactions, error states, both themes,
and resizing; avoid testing unrelated features by default.

Document prerequisites, configuration names, and exact startup/build commands. Stop only
development processes started for the current task when checks finish. Report what ran and
what remains unverified. Publishing, paid API calls, and live data changes require their own
task authorization.
