# Recipes — `codechu_treeviz`

Working patterns. Each example is self-contained.

---

## 1. Build a treemap from disk usage data

`build_tree` walks a real directory; `layout_treemap` writes
rectangles onto each node.

```python
from codechu_treeviz import build_tree, layout_treemap

root = build_tree("~/Pictures")
if root is None:
    raise SystemExit("nothing to show")

layout_treemap(root, x=0.0, y=0.0, w=800.0, h=600.0, min_frac=0.005)

def walk(n, depth=0):
    if n.rect is None:
        return
    x, y, w, h = n.rect
    print(f"{'  ' * depth}{n.path}  {x:.0f},{y:.0f} {w:.0f}x{h:.0f}")
    for c in n.children:
        walk(c, depth + 1)

walk(root)
```

`layout_treemap` only lays out one level; recurse into a child and
call it again with that child's rect to drill in.

---

## 2. Build a sunburst from a directory tree

```python
import math
from codechu_treeviz import build_tree, layout_sunburst

root = build_tree("~/Projects")
W, H = 800.0, 800.0
cx, cy = W / 2, H / 2
max_depth = 3
r_step = min(W, H) / (2 * (max_depth + 1))

layout_sunburst(
    root,
    cx=cx, cy=cy,
    r_inner=r_step / 2,
    r_step=r_step,
    max_depth=max_depth,
)

# Render with whatever toolkit you have. Each node.rect is:
# (cx, cy, r_in, r_out, a0, a1, top_idx)
```

Or use the strategy wrapper:

```python
from codechu_treeviz import SunburstStrategy
SunburstStrategy(max_depth=3).layout(root, W, H)
```

---

## 3. Custom `SizeProvider` for non-filesystem data

A `SizeProvider` short-circuits the directory walk with a cached
size. Useful when:

- You already have an mtime-keyed cache from a previous run.
- You want to splice in synthetic sizes (quotas, billing, …).

```python
from pathlib import Path
from codechu_treeviz import build_tree

cache: dict[Path, tuple[float, int]] = load_cache()  # {path: (mtime, size)}

def provider(p: Path) -> int | None:
    entry = cache.get(p)
    if entry is None:
        return None
    cached_mtime, cached_size = entry
    try:
        live_mtime = p.stat().st_mtime
    except OSError:
        return None
    if live_mtime == cached_mtime:
        return cached_size   # trust the cache, skip recursion
    return None              # stale — walk it

root = build_tree("~/Pictures", size_provider=provider)
```

For non-filesystem hierarchies (a JSON tree, a database, an org
chart), skip `build_tree` entirely and construct `TreeNode` directly:

```python
from codechu_treeviz import TreeNode, layout_treemap

def from_json(d: dict) -> TreeNode:
    return TreeNode(
        path=d["name"],
        size=d.get("size", 0),
        is_dir=bool(d.get("children")),
        children=[from_json(c) for c in d.get("children", [])],
    )

root = from_json({
    "name": "company",
    "children": [
        {"name": "eng",   "size": 0, "children": [
            {"name": "backend",  "size": 12},
            {"name": "frontend", "size": 8},
        ]},
        {"name": "sales", "size": 5},
    ],
})
# Aggregate sizes bottom-up if your data doesn't already.
def fill(n):
    if n.children:
        for c in n.children:
            fill(c)
        n.size = sum(c.size for c in n.children) or n.size
fill(root)

layout_treemap(root, 0, 0, 800, 600)
```

---

## 4. Adding a new visualization (subclass `VizStrategy`)

The pattern: write a pure layout function, then wrap it as a strategy
so the UI can hot-swap visualizations.

```python
from typing import Optional
from codechu_treeviz import VizStrategy, TreeNode

def layout_icicle(node: TreeNode, x: float, y: float,
                  w: float, h: float, depth: int = 0,
                  row_h: float = 24.0) -> None:
    """Horizontal icicle: each level is a row of stacked rects."""
    node.rect = (x, y, w, row_h)
    if not node.children or node.size == 0 or h < row_h * 2:
        return
    total = sum(c.size for c in node.children) or 1
    cx = x
    for c in node.children:
        cw = w * c.size / total
        layout_icicle(c, cx, y + row_h, cw, h - row_h, depth + 1, row_h)
        cx += cw


def icicle_hit_test(node: TreeNode, mx: float, my: float) -> Optional[TreeNode]:
    if node.rect is None or len(node.rect) != 4:
        return None
    for c in node.children:
        hit = icicle_hit_test(c, mx, my)
        if hit:
            return hit
    x, y, w, h = node.rect
    if x <= mx <= x + w and y <= my <= y + h:
        return node
    return None


class IcicleStrategy(VizStrategy):
    name = "icicle"

    def __init__(self, row_h: float = 24.0) -> None:
        self.row_h = row_h

    def layout(self, node, w, h):
        layout_icicle(node, 0.0, 0.0, float(w), float(h), row_h=self.row_h)

    def hit_test(self, node, x, y):
        return icicle_hit_test(node, x, y)
```

Reuse `node_color(top_idx, depth, dark=...)` for consistent palettes
across strategies. Pick a `rect` shape and stick to it — defend
against the other shape in `hit_test` (as the bundled treemap /
sunburst do) so stale rects from a mode switch don't crash you.

---

## 5. Hit testing for click/hover interaction

The strategy methods are uniform — UI code doesn't branch on type.

```python
from codechu_treeviz import TreemapStrategy, SunburstStrategy

strategy = TreemapStrategy()      # or SunburstStrategy()
strategy.layout(root, w=800, h=600)

def on_motion(x: float, y: float) -> None:
    node = strategy.hit_test(root, x, y)
    if node is None:
        set_tooltip(None)
    elif node.is_other:
        set_tooltip(f"({node.small_count} small items, {node.size} bytes)")
    else:
        set_tooltip(f"{node.path} — {node.size} bytes")

def on_click(x: float, y: float) -> None:
    node = strategy.hit_test(root, x, y)
    if node is not None and node.is_dir and not node.is_other:
        drill_into(node)         # call strategy.layout(node, w, h) next
```

Calling `layout_*` again on a child redraws "from that child down" —
no need to rebuild the tree.

If you ever mix modes without re-laying out (e.g. tab switch
mid-animation), the bundled hit-tests defend against the wrong
`rect` shape and return `None` instead of crashing. Re-run `layout`
on the visible root after any mode change.
