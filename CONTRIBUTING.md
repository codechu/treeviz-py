# Contributing to codechu-treeviz

Thanks for thinking about contributing. `codechu-treeviz` provides
layout primitives — squarified treemap, sunburst arcs, tree builders —
without any rendering code. Patches that respect the "layout in, no
rendering" boundary are warmly received.

This library was originally extracted from [Disk Cleaner](https://github.com/codechu/disk-cleaner),
but is maintained independently with its own release cadence.

## Development setup

```bash
git clone https://github.com/codechu/codechu-treeviz-py.git
cd codechu-treeviz-py
pip install -e ".[dev]"
pytest -q
ruff check src tests
```

## Workflow

- Branch names: `feature/<short>`, `fix/<short>`, `refactor/<short>`,
  `docs/<short>`, `test/<short>`.
- Commit messages: [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
- Open a PR using the template; describe the *why* in the body.
- One change per PR — keep diffs reviewable.

## Bug reports

A useful bug report includes:

- Python version + OS.
- A minimal reproducer with the input tree (`[(path, size), ...]`) and
  the bounding rectangle / radii used.
- Expected vs observed layout — a numeric diff or a tiny screenshot is
  fine. For aspect-ratio regressions, give a worst-case ratio.

## Tests

- `pytest -q` must pass; coverage stays at **≥85 %**.
- New layout feature → new test. Cover the boundary cases: empty
  children, one giant + many slivers, deeply nested trees, zero-size
  nodes.
- **Property-based tests are welcome** (`hypothesis`): area
  conservation, no-overlap, child-fits-in-parent are natural
  invariants to assert against random inputs.
- Layout output is geometry, not pixels — assert on coordinates with
  `pytest.approx`, not on rendered images.

## Public API discipline

The public surface is `build_tree`, `layout_treemap`,
`layout_sunburst`, and `TreeNode`. Renderers belong **downstream** —
no Cairo, SVG, matplotlib, or browser-canvas code in this package.
No translation calls (`_()`) — this is library code.

## Style

- `ruff check` + `ruff format` clean.
- Type hints on public APIs (`from __future__ import annotations`).
- Use `logging.getLogger(__name__)`; avoid `print`.

## Security

If you find a security issue, see [SECURITY.md](SECURITY.md) — do not
open a public issue for it.

## Developer Certificate of Origin (DCO)

Every commit must be signed off with the [DCO](https://developercertificate.org/).
The sign-off certifies that you wrote the patch, or otherwise have the
right to submit it under the project's license. Add a line to your
commit message:

```
Signed-off-by: Your Name <you@example.com>
```

`git commit -s` does this automatically. PRs without sign-off will
be asked to amend before merge.

Contributions are accepted under the project's license (see
[LICENSE](LICENSE)).
