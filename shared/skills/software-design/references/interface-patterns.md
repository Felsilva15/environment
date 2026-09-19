# Layout and visual choices

## Workspace header

```text
┌──────────────────────────┬──────────────────────────────────────────┐
│ window controls · toggle │ page or context            panel toggle  │
├──────────────────────────┼───────────────────────┬──────────────────┤
│ navigation               │                       │ selected item    │
│                          │ main work area        │ or inspector     │
│ scrollable items         │                       │                  │
│                          │                       │                  │
│ account / settings       │                       │                  │
└──────────────────────────┴───────────────────────┴──────────────────┘
```

Use one integrated top row rather than a wasted title strip above a separate toolbar.
In a desktop app, continue the sidebar surface behind the native controls and sidebar toggle.
Align its boundary with the sidebar below. Place the current page/context and relevant
actions in the same row; avoid repeating the page title in another oversized heading.

In a browser, the top row is an ordinary application toolbar. Leave OS window controls to
the browser: do not draw fake traffic lights or reserve a macOS-specific blank area.

Keep the header and account/settings footer stable. Let the middle navigation and each work
pane scroll independently. A right inspector should be resizable and nonmodal when the user
must continue interacting with the list. Hiding it should retain the selected record.

At narrow widths, collapse navigation and replace side-by-side inspection with a usable
detail view and return path. Favor legibility over retaining the desktop diagram at all sizes.

## Starting choices

These are adjustable starting points, not a pixel specification copied from another app.

| Dimension | Default direction | Change when |
| --- | --- | --- |
| Palette | Neutral/grayscale surfaces; high-contrast text | Meaningful status, categorical data, or requested branding needs color |
| Accent | No decorative accent required; one restrained accent if useful | Multiple data series must be distinguished accessibly |
| Density | Compact controls and rows, with clear grouping | Touch targets, accessibility, or content require more room |
| Typography | System sans-serif, small consistent hierarchy | The product brief establishes another type system |
| Corners | Consistent modest rounding | Existing components use a coherent alternative |
| Elevation | Borders and subtle surface changes | A floating layer needs separation |
| Motion | Short functional feedback; respect reduced motion | An interaction genuinely benefits from a transition |

For a new desktop shell, a header around 48–56px and sidebar around 240–280px are reasonable
prototype measurements. Verify against native controls, target screens, text scaling, and
actual content. They are not exact ChatGPT dimensions or permanent user requirements.

Use semantic tokens for surfaces, text, borders, emphasis, focus, and destructive actions.
Pair background/foreground tokens in both themes. Avoid scattered hard-coded colors.
shadcn's [theme controls](https://ui.shadcn.com/docs/theming) support CSS variables and
previewing palette, radius, typography, and icon choices through its builder.

## Review real states

Inspect loading, empty, populated, selected, disabled, validation, error, and long-content
states. Check keyboard focus, text zoom, narrow windows, and theme contrast. Use text/icon
cues in addition to color for status. A minimal UI still needs discoverable controls.

Formatted documents can carry their own colors. A light document canvas inside dark chrome
can be preferable to unreadable forced dark backgrounds. Preserve document readability
without recoloring the whole application or globally inverting embedded content.

OpenAI's [UI guidelines](https://developers.openai.com/plugins/concepts/ui-guidelines)
provide a public reference for restrained surfaces, typography, spacing, and iconography.
They address apps embedded in ChatGPT; their widget-specific layout restrictions are not
requirements for standalone desktop or web software.
