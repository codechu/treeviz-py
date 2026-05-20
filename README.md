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

[![PyPI](https://img.shields.io/pypi/v/codechu-treeviz.svg)](https://pypi.org/project/codechu-treeviz/)
[![Python](https://img.shields.io/pypi/pyversions/codechu-treeviz.svg)](https://pypi.org/project/codechu-treeviz/)
[![CI](https://github.com/codechu/treeviz-py/actions/workflows/ci.yml/badge.svg)](https://github.com/codechu/treeviz-py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> *Squarified treemap + sunburst layouts — rectangles and arcs, you render.*

# codechu-treeviz

Squarified treemap and sunburst layout algorithms for hierarchical
data. Pure Python, no GUI dependency — gives you rectangles and arcs
and lets you render them with whatever toolkit you prefer (Cairo,
SVG, Matplotlib, browser canvas, Pillow PNG).

```text
            input                            output
   ┌────────────────────┐         ┌────────────────────┐
   │ /                  │         │ ┌─────────┬──────┐ │
   │ ├── photos  (450)  │   →     │ │ photos  │ src  │ │
   │ ├── src     (200)  │ layout  │ ├─────────┴──────┤ │
   │ ├── cache   (180)  │         │ │  cache  │ logs │ │
   │ └── logs    (120)  │         │ ├─────────┴──────┤ │
   └────────────────────┘         │ └────────────────┘ │
                                   per-node (x, y, w, h)
```

## Install

```bash
pip install codechu-treeviz
```

Python 3.10+. Pure stdlib + `math`, zero third-party deps.

## Quick example

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

## What you get

- **Squarified treemap** — Bruls/Huijsen/van Wijk algorithm,
  aspect-ratio optimized rectangles.
- **Sunburst** — circular hierarchical chart with concentric rings.
- **`TreeNode` builder** — turn a `(path, size)` list into a
  hierarchical tree with cancel + progress callbacks.
- **Hit testing** — find the node at any (x, y) coordinate.
- **"Other" bundling** — collapse small slivers into one
  `"(N items)"` bucket.
- **Color palette** — perceptually balanced default fill colors.

No rendering, no GUI dependency, bounded depth
(`TREEMAP_MAX_DEPTH = 40`) so pathological nesting can't OOM you.

## Read more

- [API reference](docs/API.md) — TreeNode, SizeProvider,
  VizStrategy, layout functions, hit-test, color helpers.
- [Recipes](docs/RECIPES.md) — disk-usage treemap, sunburst from a
  directory tree, custom `SizeProvider`, subclassing `VizStrategy`,
  hit-test plumbing.
- [Migration guide](docs/MIGRATION.md)
- [Changelog](CHANGELOG.md)

## Family

| Library | Purpose |
|---------|---------|
| [codechu-treedata](https://pypi.org/project/codechu-treedata/) | N-ary tree data structures and algorithms |
| [codechu-spark](https://pypi.org/project/codechu-spark/) | Unicode sparklines, mini bar charts, heatmaps |
| [codechu-fmt](https://pypi.org/project/codechu-fmt/) | Human-readable sizes, durations, rates |
| [codechu-cli](https://pypi.org/project/codechu-cli/) | CLI primitives — colors, progress, prompts |
| [codechu-color](https://pypi.org/project/codechu-color/) | Color palettes, WCAG contrast, color-blind variants |

Full ecosystem: [github.com/codechu](https://github.com/codechu).

## Credits

- Squarified treemap algorithm by Bruls, Huijsen, van Wijk (2000).
- Sunburst layout following Stasko & Zhang radial visualizations.
- Inspiration from [squarify](https://github.com/laserson/squarify) —
  single-algorithm; codechu-treeviz extends to multiple strategies.

## License

MIT — see [LICENSE](LICENSE).

Part of [Codechu](https://github.com/codechu).
