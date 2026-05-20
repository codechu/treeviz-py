```text
   ┌──────────────────────┬───────────────┬─────────┐
   │  codechu-treeviz     │  ┌─────────┐  │  ┌───┐  │
   │  ┌────────┬───────┐  │  │ photos  │  │  │ . │  │
   │  │ videos │ music │  │  ├────┬────┤  │  └───┘  │
   │  ├────────┴───────┤  │  │ .. │ .. │  │ cache   │
   │  │   documents    │  │  └────┴────┘  │         │
   │  └────────────────┘  │   pictures    │  logs   │
   └──────────────────────┴───────────────┴─────────┘
```

> *Squarified treemap + sunburst layouts — rectangles and arcs, you render.*

# codechu-treeviz

Squarified treemap + sunburst layout algorithms for hierarchical data.
Pure Python, no GUI dependency — gives you rectangles and arcs; you
render them with whatever toolkit (Cairo, SVG, Matplotlib, browser canvas).

```bash
pip install codechu-treeviz
```

## What it gives you

- **Squarified treemap** layout — Bruls/Huijsen/van Wijk algorithm, aspect-ratio optimized
- **Sunburst** layout — circular hierarchical chart with concentric rings
- **TreeNode** builder — turn a `(path, size)` list into a hierarchical tree
- **Hit testing** — given (x, y), find the node at that position
- **"Other" bundling** — small slivers grouped into a single "(N items)" bucket
- **Color palette** — perceptually balanced fill colors
- Pure stdlib + Python `math`, zero deps

## Example

```python
from codechu_treeviz import build_tree, TreemapStrategy

# 1. Walk a directory into a TreeNode
root = build_tree("~/Pictures")

# 2. Lay it out — writes (x, y, w, h) onto every node.rect
strategy = TreemapStrategy(min_frac=0.005)
strategy.layout(root, w=800, h=600)

# 3. Render however you like (Cairo, SVG, browser canvas, …)
for child in root.children:
    if child.rect is not None:
        x, y, w, h = child.rect
        print(child.path, (x, y, w, h))

# 4. Hit test for hover/click
node = strategy.hit_test(root, x=120, y=80)
```

Swap `TreemapStrategy()` for `SunburstStrategy()` and the same code
renders a radial chart (rects become 7-tuples — see the API docs).

## Documentation

- **[docs/API.md](docs/API.md)** — full API reference (TreeNode,
  SizeProvider, VizStrategy, layout functions, hit-test, colors)
- **[docs/RECIPES.md](docs/RECIPES.md)** — patterns: disk-usage
  treemap, sunburst from a directory tree, custom `SizeProvider`,
  subclassing `VizStrategy`, hit-test plumbing

## Design

- **No rendering** — algorithms produce geometry; rendering is your job
  (Cairo, SVG, PNG via Pillow, browser canvas via JSON over HTTP, etc.)
- **No GUI dependency** — `import codechu_treeviz` works without GTK/Qt/Tk
- **Cancel + progress** support in `build_tree` for long inputs
- **Bounded depth** (`TREEMAP_MAX_DEPTH = 40`) protects against pathological nesting

## Use cases

- Disk usage visualizer (the original)
- Source-code size / dependency tree explorer
- Package size analyzer (npm, PyPI, Cargo)
- Time-tracking dashboard (project / task / subtask hierarchy)
- Any "where did the bytes / hours / records go?" question

## License

MIT — see [LICENSE](LICENSE).

Part of [Codechu](https://github.com/codechu).
