# Electron implementation

## Native shell

Integrate the toolbar with the operating system's window controls. For macOS, the following
options illustrate retaining traffic lights while removing the extra native title strip:

```ts
const macHeader = process.platform === 'darwin'
  ? { titleBarStyle: 'hidden' as const, trafficLightPosition: { x: 16, y: 18 } }
  : {};
// Merge macHeader into the app's BrowserWindow options.
```

The offsets are an example, not a required measurement. Reserve safe space for native controls
in both expanded and collapsed sidebar states. Mark blank header regions draggable and every
interactive control non-draggable using Electron's app-region CSS. Check dragging, double-click
behavior, and button hit targets in the actual desktop window.

Use available work area without forcing a full-screen Space. Respect saved window geometry
when present; maximizing on first launch can suit a workspace app. Implement platform-specific
native controls on Windows/Linux if hiding their title bar; do not copy macOS offsets there.

Verify APIs against the installed Electron version using the official
[custom title bar](https://www.electronjs.org/docs/latest/tutorial/custom-title-bar) and
[window interactions](https://www.electronjs.org/docs/latest/tutorial/custom-window-interactions)
documentation. Browser screenshots cannot establish that native controls work.

## Process boundary

Keep `contextIsolation: true`, `nodeIntegration: false`, and renderer sandboxing enabled.
Use a sandbox-compatible preload build. Expose narrow typed operations via `contextBridge`,
validate inputs and caller context at privileged boundaries, and keep provider SDKs, database
connections, and credentials in privileged code. Do not expose arbitrary IPC or disable
isolation to work around an import/build error.

Coordinate native window and renderer appearance. Keep background job state outside the
mounted renderer page. Use platform lifecycle conventions and the existing single-instance
behavior where appropriate.

References: [context isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation)
and [sandboxing](https://www.electronjs.org/docs/latest/tutorial/sandbox).

## Runtime checks

After changing native window options, fully restart Electron; renderer hot reload is insufficient.
For structural/runtime changes, run the development entrypoint and the built application using
the repository's actual scripts. Check preload loading, asset paths, navigation, and native
header behavior. Test packaged installation only when packaging/distribution is in scope.
Do not claim cross-platform verification from a single-platform launch.
