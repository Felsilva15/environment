# Reference technology and design tooling

Checked 2026-09-19. Use this evidence to understand the reference, not as a lockfile or a
dependency checklist for new projects. ChatGPT implementations can differ by platform and release.

## Locally observed desktop build

Read-only inspection of the installed macOS ChatGPT application, version **26.915.31945**, found:

| Evidence | Observation | Limit |
| --- | --- | --- |
| Bundled package manifest | Electron 42.3.0; Vite 8.2.0; TypeScript ^7.0.2; Electron Forge ^7.11.2 tooling | Declared build dependencies, not proof of every runtime code path |
| Bundled package manifest | TanStack Query core, Zod, better-sqlite3, node-pty | Present for this desktop product's needs; not mandatory frontend dependencies |
| UI JavaScript | React element/runtime markers and react-dom references | React evidence; no complete renderer dependency/version manifest established |
| UI CSS and assets | Tailwind version banners, Radix-named CSS variables, Lucide icon modules | Bundled technology indicators; some assets can belong to embedded tools |

The manifest identifies the desktop package as an Electron application. These observations
apply to the inspected build; they do not establish the stack of older macOS releases, the
Windows app, or the entire ChatGPT website. Presence of Radix/Tailwind does **not** prove
shadcn/ui is used internally. The complete proprietary design system and all dependencies
were not established. No application code or extracted bundles are distributed with this skill.

## Public design resources

OpenAI's [UI guidelines](https://developers.openai.com/plugins/concepts/ui-guidelines) point to
the optional `@openai/apps-sdk-ui` library, which provides components, Tailwind foundations,
and CSS-variable tokens intended to match ChatGPT. The same page links its Figma component
library. These are public resources for apps embedded in ChatGPT, not a statement that the
whole desktop client is implemented with that package.

[shadcn/ui](https://ui.shadcn.com/docs) is the preferred independent implementation reference
for React software. Its [theming documentation](https://ui.shadcn.com/docs/theming) describes
semantic color pairs and configurable palette, radius, typography, and icon options. Start
with a neutral palette and tune those choices deliberately. Inspect the selected component
base and existing configuration before generating additions.

For standalone applications, prefer one coherent component system. Use shadcn/ui by default
for a new suitable React project; consider OpenAI's public kit when matching an embedded
ChatGPT experience is the actual requirement. Do not install both just because both are references.
