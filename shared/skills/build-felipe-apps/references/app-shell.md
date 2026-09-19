# App shell and UI

## One useful top row

The reference is a desktop work surface with this spatial arrangement:

```text
┌──────────────────────────┬──────────────────────────────────────────┐
│ native controls · toggle │ current page              panel toggle   │
├──────────────────────────┼───────────────────────┬──────────────────┤
│ search / navigation      │                       │ selected record  │
│                          │ main list or workspace│                  │
│ recent items (scroll)    │                       │ independent      │
│                          │                       │ scroll           │
│ account / settings       │                       │                  │
└──────────────────────────┴───────────────────────┴──────────────────┘
```

The header is a single row across the shell. Continue the sidebar surface behind the
native controls and its toggle; continue the workspace surface behind the page title.
Align the vertical boundary with the sidebar below. Give the page identity a clear place
without repeating a large page heading that consumes another row unnecessarily.

Jev Mail used a **52px header**, **264px sidebar**, **8px corner radius**, and mostly
**12–14px UI text**. These are reference measurements, not fixed requirements. Adapt to
content, display scaling, platform, and the existing design system. Use real shadcn/ui
components where applicable, with consistent semantic color tokens across custom pieces.

Use grid/flex containers with `min-width: 0` and `min-height: 0` so content can shrink and
scroll inside the intended panes. Keep header and sidebar footer stable; scroll the
navigation/history middle region and work panes independently. At narrow widths, collapse
navigation and change the detail arrangement before making either pane unreadably small.
On mobile web, a full-width detail view with a clear return path can replace side-by-side panes.

## Detail pane

The desktop reference is the ChatGPT **Toggle side panel** interaction: docked to the right,
resizable, and nonmodal. Opening a record leaves navigation and the list interactive.
Avoid a dimmed backdrop or focus trap for this persistent workspace pane.

Keep selection separate from visibility: hiding the pane should not forget the record.
Retain it across relevant page navigation and reopen it with the header toggle. Bound
the divider to usable widths and support keyboard resizing. Label icon buttons, show focus,
and return focus to the triggering control when closing. Reserve modal dialogs for actual
modal tasks; Escape should close the topmost dialog before the underlying pane.

## Progress, content, and theme

Background work continues while the user navigates or reads records. Minimize its detail
dialog into a compact progress surface, with a way to reopen details. Display completed,
pending, and failed counts, elapsed time during execution, and total duration afterward.
Use actual orchestration state rather than optimistic cosmetic completion.

Default appearance to System and react to system changes while that choice is selected.
Persist explicit Light/Dark overrides. Verify selected, muted, disabled, error, and focus
states in both themes, not just the empty shell.

Embedded HTML/documents can specify their own foreground colors. Preserve readable pairs
of foreground/background inside an isolated document surface; a light document canvas
inside dark app chrome is valid. Do not invert arbitrary content or force only its background
dark. Keep formatted reading content distinct from normalized text used for analysis.
Sanitize untrusted HTML and handle remote assets explicitly; image retrieval was still
being investigated in the source task, so its last implementation is not an approved default.

## Desktop versus web

| Concern | Electron desktop | Web app |
| --- | --- | --- |
| Header | Integrates actual OS controls and safe drag areas | Ordinary app toolbar beneath browser chrome |
| Window sizing | Use available work area; Jev Mail opens maximized | Fill available viewport; respond to browser resizing |
| Native controls | Preserve platform controls and their safe area | Do not draw fake traffic lights or reserve macOS control space |
| Detail/navigation | Docked panes with independent scroll | Same at suitable widths; adapt on narrow/mobile screens |
| Theme | Coordinate renderer and native window appearance | Use browser system preference plus saved override |
| Data access | Typed preload bridge to privileged main process | Existing server/API boundary; never introduce Electron IPC |

Use an established app logo consistently when one exists, including native app identity
when delivering desktop packaging. Creating a new logo requires task scope that includes it.
