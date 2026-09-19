---
name: software-design
description: Design or review software interfaces with simple neutral styling, clear hierarchy, and restrained use of color. Use for visual direction, app layouts, typography, spacing, themes, and interaction design. Use shadcn/ui and the ChatGPT desktop app as references; do not impose a framework or change backend architecture.
---

# Design

Create simple, usable software interfaces. Treat these preferences as defaults; an explicit
brief and an existing product's constraints take precedence. Design requests do not authorize
implementation, dependency installation, or publication.

## Visual direction

- Start with neutral backgrounds, readable text, subtle borders, and modest surface contrast.
  Color should communicate an action, selection, status, or data distinction. Do not assign
  a different bright color to every card, icon, section, or metric.
- Use **shadcn/ui** as a component and styling reference and **ChatGPT desktop** as an
  example of a quiet, compact workspace. Borrow their clarity without copying brand assets
  or assuming they share an implementation stack.
- Avoid generic AI-generated dashboard styling: decorative gradients, glowing backgrounds,
  glass panels without purpose, oversized rounded cards, excessive shadows, emoji icons,
  and animated decoration. Do not add dashboard metrics just to fill space.
- Build hierarchy through alignment, spacing, typography, and disclosure. Prefer a small
  type scale and a system sans-serif font. Make supporting text readable, not faint.
- Use consistent monochrome outline icons with accessible labels. Give primary actions
  clear emphasis; keep secondary actions visually quieter.
- Default theme to System, with persistent Light and Dark overrides. Evaluate contrast,
  focus, selected states, and actual content in both appearances.

## Structure and interaction

For workspace-style software, prefer one useful top header, a compact collapsible sidebar,
and a flexible main work area. Use a docked detail pane when users need to inspect a record
without losing their place. Do not force a three-pane shell onto a simple form or small tool.

Read [layout and visual choices](references/interface-patterns.md) for the header arrangement,
design options, responsive behavior, and what to check in a design review.

Keep long-running work visible without blocking navigation. Provide a compact progress
surface that can expand into details, with clear pending, success, partial failure, and
failure states. Preserve selection and context when opening and closing secondary views.

## Deliverable

For a design task, define the needed layout, token choices, component states, and responsive
behavior. When a preview is useful, show representative content and both themes. Do not
substitute an attractive empty shell for the requested workflow.

Keep visual decisions here. Use the available Frontend skill for implementation and Backend
skill for data/execution concerns only when those tasks are actually in scope.
