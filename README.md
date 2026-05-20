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
from codechu_treeviz import build_tree, layout_treemap, layout_sunburst, hit_test

# 1. Build a tree from flat (path, size) records
items = [
    ("/home/user/Documents", 5_000_000_000),
    ("/home/user/Pictures",  2_000_000_000),
    ("/home/user/.cache",    1_200_000_000),
    ("/var/log",               300_000_000),
]
root = build_tree(items)

# 2. Treemap layout — produces rectangles for each node
rects = layout_treemap(root, width=800, height=600, min_frac=0.005)
for r in rects:
    # r.x, r.y, r.w, r.h, r.node
    print(r.node.label, (r.x, r.y, r.w, r.h))

# 3. Sunburst layout — produces arc segments
arcs = layout_sunburst(root, cx=400, cy=300, max_radius=250)
for a in arcs:
    # a.cx, a.cy, a.r1, a.r2, a.a1, a.a2, a.node
    print(a.node.label, "ring", a.a1, "→", a.a2)

# 4. Hit test
from codechu_treeviz import hit_test
node = hit_test(rects, x=120, y=80)  # which rect at (120,80)?
```

## API surface

| Function / class | Purpose |
|---|---|
| `build_tree(items, progress=None, cancel=None)` | Build TreeNode from flat (path, size) list |
| `layout_treemap(node, width, height, min_frac=0.005)` | Squarified rect layout |
| `layout_sunburst(node, cx, cy, max_radius, ...)` | Concentric-ring arc layout |
| `hit_test(rects, x, y)` | Find treemap rect at coords |
| `sunburst_hit_test(arcs, x, y, cx, cy)` | Find sunburst arc at coords |
| `TreeNode` | Hierarchical node (children, total_size, label) |
| `TreemapStrategy` / `SunburstStrategy` | OOP wrapper (optional, for plugin pattern) |
| `node_color(node)` | Stable color from node identity |
| `is_hash_like(s)` | Heuristic: is this a hash-like name (cache key vs human label) |

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
