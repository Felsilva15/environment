# Electron and delivery

## Native header example

Jev Mail combined a React header with native macOS traffic lights. This is a layout fragment,
not a complete app bootstrap; adapt build paths and lifecycle to the repository.

```ts
const win = new BrowserWindow({
  show: false,
  ...(process.platform === 'darwin' ? {
    titleBarStyle: 'hidden',
    trafficLightPosition: { x: 16, y: 18 },
  } : {}),
  webPreferences: {
    preload: absoluteBuiltPreloadPath,
    contextIsolation: true,
    nodeIntegration: false,
    sandbox: true,
  },
});
win.once('ready-to-show', () => {
  win.maximize();
  win.show();
});
```

Use maximization to occupy the available work area; the request to use the screen did
not require entering a separate macOS full-screen Space. Respect existing saved window
bounds if the app already provides them.

```css
/* Apply only in the Electron renderer's native title-bar mode. */
[data-native-titlebar="true"] .window-titlebar {
  -webkit-app-region: drag;
  user-select: none;
}
[data-native-titlebar="true"] .titlebar-control {
  -webkit-app-region: no-drag;
}
[data-platform="darwin"] .titlebar-leading {
  padding-left: 96px; /* reference clearance; verify against actual native controls */
}
```

Apply the interactive control class to every button, input, link, or menu trigger in the
drag region. Retain safe clearance when the sidebar collapses. Check native controls,
dragging, double-click behavior, and hit targets in the real desktop app. A browser screenshot
cannot validate them. Changes to `BrowserWindow` options require a full Electron restart.

The example retains the normal frame on other platforms. If the task targets Windows/Linux
with a custom header, implement and verify native window controls and overlay safe areas
there instead of copying macOS offsets. Verify against the installed Electron version.
Sources: [Electron custom title bar](https://www.electronjs.org/docs/latest/tutorial/custom-title-bar)
and [window interactions](https://www.electronjs.org/docs/latest/tutorial/custom-window-interactions).

## Runtime boundaries

Keep renderer, preload, and main responsibilities distinct. Expose narrow typed operations
through `contextBridge`, validate input at IPC boundaries, and keep credentials, database
connections, and provider SDKs out of renderer code. Avoid exposing generic IPC send/invoke
primitives to page content. Use a sandbox-compatible preload build rather than disabling
isolation to fix a bundling problem. See [context isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation)
and [sandboxed preload limitations](https://www.electronjs.org/docs/latest/tutorial/sandbox).

For job-oriented apps, keep orchestration state outside the mounted page so navigation does
not cancel processing or lose status. Bound configurable concurrency, isolate per-record
errors, and preserve enough state to retry safely. Keep decision generation, deterministic
action policy, provider calls, and persistence separable when the workflow has those layers.
Do not add Jev, PostgreSQL, Docker, or an email provider merely because Jev Mail used them.

## Verification and handoff

Use the repository's actual scripts. For Jev Mail these included `pnpm dev`, `pnpm build`,
and `pnpm start`; do not assume another app defines identical scripts.

- After structural/runtime changes, launch the development app and the built application.
  Jev Mail once built successfully while its running development renderer failed to resolve
  an import. Build output alone did not establish usability.
- For header/sidebar/pane changes, inspect the real window at the target screen size and a
  smaller size. Exercise collapse, record selection, pane close/reopen, divider, and navigation.
- For background work, use synthetic data or mocked providers to exercise success and failure
  while browsing. For theme changes, inspect both themes and representative formatted content.
- Document prerequisites, configuration names, dependency installation, database setup only
  if needed, and exact startup commands. State any external configuration still missing.
- Stop only app/dev-server processes started for this task when checks finish, leaving Felipe
  able to launch the app himself. Do not terminate unrelated terminals or another active task.

Match validation to the change. Do not run paid API calls, mutate live inboxes, or publish a
repository solely because this skill describes delivery. Report what was actually exercised
and any unverified native/platform behavior.
