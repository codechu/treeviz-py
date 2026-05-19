# CLAUDE.md — codechu-treeviz

Bootstrap per `codechu-org/ai/AGENTS.md` §0 before any work. Prefer
the local clone at `$org_home/codechu-org/ai/AGENTS.md` (if
`~/.config/codechu/config.toml` has `org_home` set); otherwise
WebFetch the public raw URL
<https://raw.githubusercontent.com/codechu/codechu-org/main/ai/AGENTS.md>.
This file lists only product-local overrides.

## Product-local notes

- Pure-Python layout primitives — **no rendering** code lives here.
  Renderers (Cairo / SVG / matplotlib) are downstream concerns and
  must not creep into this package.
- Public API: `build_tree`, `layout_treemap`, `layout_sunburst`,
  `TreeNode`. The `max_depth` parameter on `build_tree` is the
  controlled extension point — prefer adding params over leaking
  internal state.
- No translation calls (`_()`) — this is library code, not a UI.
- Coverage target: ≥85 %.

## Discipline reminders (org rules apply)

- Conventional Commits, no AI signature.
- No `--no-verify`, no force push, no unapproved publish.
- See `codechu-org/ai/AGENTS.md` for the full list.
