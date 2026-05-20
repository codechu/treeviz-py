# API Reference — `codechu_treeviz`

All public names re-exported from the package root:

```python
from codechu_treeviz import (
    TreeNode, SizeProvider, build_tree,
    VizStrategy,
    TreemapStrategy, SunburstStrategy,
    IcicleStrategy, SliceDiceStrategy, FlameGraphStrategy,
    layout_treemap, layout_sunburst,
    layout_icicle, layout_slicedice, layout_flamegraph,
    hit_test, sunburst_hit_test,
    icicle_hit_test, slicedice_hit_test, flamegraph_hit_test,
    node_color, is_hash_like,
    OTHER_MARKER,
)
```

> Strategy implementations live in `codechu_treeviz.strategies` since
> v0.2.0. The top-level re-exports above are the recommended import
> path; see [`MIGRATION.md`](MIGRATION.md) for the legacy module-path
> shims that remain supported.

The library is pure logic — layouts mutate `node.rect` on the input
tree; rendering is the caller's responsibility (Cairo, SVG, browser
canvas, …).

---

## `TreeNode`

```python
class TreeNode:
    path: str
    size: int
    children: list[TreeNode]
    is_dir: bool
    is_other: bool
    small_count: int
    rect: tuple[float, ...] | None
```

A single node in the hierarchy. `__slots__`-based; not a dataclass
(intentional, to keep memory low for million-node trees).

Construct directly when you have non-filesystem data:

```python
root = TreeNode("project", size=0, is_dir=True, children=[
    TreeNode("src",   size=12_000, is_dir=True),
    TreeNode("tests", size=4_000,  is_dir=True),
])
```

### `rect` polymorphism

`rect` is `None` until a layout function writes to it. The shape
depends on which layout was last run:

| Layout                | `rect`                                              |
|-----------------------|-----------------------------------------------------|
| `layout_treemap`      | `(x, y, w, h)` — 4-tuple, pixel rectangle           |
| `layout_sunburst`     | `(cx, cy, r_in, r_out, a0, a1, top_idx)` — 7-tuple  |

Hit-test functions defend against the mismatch: `hit_test` silently
ignores 7-tuples; `sunburst_hit_test` requires `len(rect) >= 6`.
When you switch modes, re-run the layout before drawing/hit-testing.

### `is_other` / `small_count`

Synthetic "Other" bundle nodes inserted by the layout when many tiny
siblings would clutter the view. Their `path` is `OTHER_MARKER`
(`"__OTHER__"`). Render them with a neutral color (see
`node_color(..., is_other=True)`) and a label like
`f"({n.small_count} items)"`.

---

## `SizeProvider`

```python
class SizeProvider(Protocol):
    def __call__(self, path: pathlib.Path) -> int | None: ...
```

Dependency-injection hook for `build_tree`. When walking a directory,
`build_tree` calls the provider; if it returns a non-`None` size, the
directory is **not** recursed into and the cached size is used.
Return `None` to fall back to a fresh `lstat` walk.

Freshness is the provider's responsibility (mtime check, TTL, etc.).
Typical use: a persistent disk-usage cache indexed by mtime.

---

## `build_tree(...)`

```python
build_tree(
    root: str | pathlib.Path,
    cancel: threading.Event | None = None,
    progress: Callable[[str], None] | None = None,
    *,
    max_depth: int = 40,        # TREEMAP_MAX_DEPTH
    size_provider: SizeProvider | None = None,
) -> TreeNode | None
```

Walk `root` (DFS) and return a `TreeNode`. Properties:

- **Sparse-file accurate** — leaf size is `st_blocks * 512`, not
  `st_size`.
- **Symlink-safe** — `st_dev/st_ino` cycle guard; symlinks become
  zero-size leaves.
- **Depth-bounded** — past `max_depth`, returns an empty directory
  stub rather than recursing.
- **Cancellable** — if `cancel.is_set()` becomes true mid-walk,
  returns the partial tree built so far.
- **Progress** — called once per directory entered with a short
  status string (e.g. `"1234 files · /home/u/Pictures"`).

Children are sorted by descending size at every level.

---

## `VizStrategy`

```python
class VizStrategy(ABC):
    name: str = "unknown"
    @abstractmethod
    def layout(self, node: TreeNode, w: float, h: float) -> None: ...
    @abstractmethod
    def hit_test(self, node: TreeNode, x: float, y: float) -> TreeNode | None: ...
    def draw(self, cr, node, *, hover=None, dark=False) -> None: ...
```

Abstract strategy interface. `layout` writes `rect` onto every node;
`hit_test` returns the deepest node at `(x, y)` or `None`. `draw`
takes a cairo context; the default raises `NotImplementedError` —
override it if you want a self-contained strategy. (The reference UI
in `disk-cleaner` still draws from its panel, so the bundled
strategies do not implement `draw`.)

Add a new visualization by subclassing `VizStrategy` — see
[`RECIPES.md`](RECIPES.md).

### `TreemapStrategy`

```python
TreemapStrategy(min_frac: float = 0.005)
```

Wraps `layout_treemap` + `hit_test`. `min_frac` is the threshold
(fraction of parent total) below which siblings collapse into an
"Other" bundle. `name = "treemap"`.

### `SunburstStrategy`

```python
SunburstStrategy(max_depth: int = 3, min_arc: float = 0.06)
```

Wraps `layout_sunburst` + `sunburst_hit_test`. `max_depth` is the
number of concentric rings rendered (root is the inner disk);
`min_arc` is the minimum arc length in radians (slivers below it are
bundled). `name = "sunburst"`.

The ring step is computed from canvas size:
`r_step = min(w, h) / (2 * (max_depth + 1))`.

### `IcicleStrategy`

```python
IcicleStrategy(max_depth: int = 8)
```

Icicle plot — horizontal strips, one per depth level. The root is the
top strip; each level below is a strip divided proportionally among
its children's sizes. `name = "icicle"`.

`rect` is a 4-tuple `(x, y, w, h)`. Row height is
`h / (max_depth + 1)`, so deeper trees compress automatically.

Useful when:

- The depth of a node should be obvious at a glance (vs. treemap where
  it's inferred from nesting).
- Sibling order must be preserved (no axis swap, no squarify shuffle).

### `SliceDiceStrategy`

```python
SliceDiceStrategy(horizontal: bool | None = None)
```

The original treemap algorithm (Shneiderman 1992): split the parent
along one axis, alternate horizontal/vertical at each level. Children
are sized proportionally and **drawn in their original order**.

`horizontal=None` (default) picks the longer initial axis and
alternates. `True` forces a horizontal first split; `False` a
vertical one.

`name = "slicedice"`. `rect` is a 4-tuple.

Aspect ratios are worse than squarified treemap, but the layout is
predictable — useful when ordering encodes meaning (chronology,
alphabetical, etc.).

Unlike `layout_treemap`, `layout_slicedice` lays out the **entire
subtree** in one call.

### `FlameGraphStrategy`

```python
FlameGraphStrategy(max_depth: int = 8)
```

A flame graph — icicle plot rotated 180°. The root sits at the
**bottom** of the canvas; children stack **upward**. `name =
"flamegraph"`. `rect` is a 4-tuple.

Originally a CPU-profiling visualization, but the layout works for
any size-weighted hierarchy.

---

## `layout_treemap(...)`

```python
layout_treemap(
    node: TreeNode,
    x: float, y: float, w: float, h: float,
    depth: int = 0,
    min_frac: float = 0.005,
) -> None
```

Squarified treemap (Bruls, Huijsen, van Wijk 2000). Lays out **one
level** — `node` plus its direct children — and writes 4-tuple rects.
Re-invoke on drill-in to lay out a child's subtree.

Side effect: any leftover synthetic "Other" children from a prior
layout pass are stripped before re-bundling.

---

## `layout_sunburst(...)`

```python
layout_sunburst(
    node: TreeNode,
    cx: float, cy: float,
    r_inner: float, r_step: float,
    max_depth: int = 3,
    start_angle: float = -math.pi / 2,
    end_angle: float = 3 * math.pi / 2,
    depth: int = 0,
    top_idx: int = 0,
    min_arc: float = 0.06,
) -> None
```

Recursive sunburst layout. Writes 7-tuples
`(cx, cy, r_in, r_out, a0, a1, top_idx)` onto every node down to
`max_depth`. Default angle range is a full circle starting at 12
o'clock.

`top_idx` tracks which top-level branch a descendant belongs to —
used by `node_color` to keep a branch visually coherent across rings.

The "Other" bundle is shown only if it accounts for `>=15%` of the
parent's total; below that the space is left blank rather than
adding a confusing gray sliver.

---

## `layout_icicle(...)`

```python
layout_icicle(
    node: TreeNode,
    x: float, y: float, w: float, h: float,
    depth: int = 0,
    max_depth: int = 8,
) -> None
```

Icicle plot layout. Writes 4-tuple `(x, y, w, h)` rects recursively
down to `max_depth` levels. The root occupies the top row of the
canvas; each subsequent level is a strip directly below the previous
one. Children's widths are proportional to their `size`.

## `layout_slicedice(...)`

```python
layout_slicedice(
    node: TreeNode,
    x: float, y: float, w: float, h: float,
    depth: int = 0,
    horizontal: bool | None = None,
) -> None
```

Slice-and-dice treemap. Writes 4-tuple rects across the entire
subtree in a single call. Alternates between horizontal and vertical
splits at each level. `horizontal=None` picks the longer initial axis
automatically.

## `layout_flamegraph(...)`

```python
layout_flamegraph(
    node: TreeNode,
    x: float, y: float, w: float, h: float,
    depth: int = 0,
    max_depth: int = 8,
) -> None
```

Flame graph layout. Same shape as `layout_icicle` but the root is
anchored at the **bottom** of the canvas (`y + h - row_h`) and
children stack upward. Row height is `h / (max_depth + 1)`.

---

## `hit_test(node, mx, my, depth=0)`

Treemap hit-test. Single level: scans `node.children` first, falls
back to `node` itself. Skips children whose `rect` is not a 4-tuple
(stale sunburst leftovers). Returns the hit `TreeNode` or `None`.

## `sunburst_hit_test(node, mx, my, depth=0, max_depth=3)`

Sunburst hit-test in polar coordinates. Recursive — drills into
children first, returns the deepest match. Honors `max_depth` to
avoid hitting stale inner rects from drill-in/out animations.

Both functions are also exposed as `strategy.hit_test(node, x, y)`
methods so callers can swap strategies without branching.

## `icicle_hit_test(node, mx, my)`

Recursive depth-first hit-test over icicle rects. Children are tested
before the parent, so clicks on deeper strips return the descendant.
Skips nodes with non-4-tuple `rect`s.

## `slicedice_hit_test(node, mx, my)`

Recursive hit-test for slice-and-dice rects. Children tested first;
returns the deepest match.

## `flamegraph_hit_test(node, mx, my)`

Recursive hit-test for flame graph rects. Children tested first, so
clicks on higher stack frames return the descendant call rather than
the root at the base.

---

## `colors.node_color(top_idx, depth, *, dark, is_other=False)`

```python
def node_color(
    top_idx: int, depth: int, *, dark: bool, is_other: bool = False
) -> tuple[float, float, float]
```

Returns RGB `(r, g, b)`, each in `0..1`. Algorithm:

- **Hue**: golden-ratio rotation of `top_idx` (`0.618`), shifted
  slightly per `depth` so rings/levels separate visually.
- **Light mode**: vivid (saturation 0.40–0.72, lightness 0.50–0.82).
- **Dark mode**: calmer (saturation 0.28–0.45, lightness 0.30–0.62).
- **`is_other=True`**: neutral gray, shaded by depth.

`dark` is a parameter — the library never imports a theme module.

## `text.is_hash_like(name) -> bool`

Heuristic: `True` for names ≥20 chars where >85% of characters are
hex/dash (UUIDs, SHA hashes, cache keys). The UI uses this to
shorten or hide unreadable labels.

---

## `OTHER_MARKER`

```python
OTHER_MARKER = "__OTHER__"
```

The synthetic `path` value used for bundle nodes. Treat it as opaque
— use `node.is_other` / `node.small_count` to render the label.

---

## See also

- [`RECIPES.md`](RECIPES.md) — common usage patterns
- [`../README.md`](../README.md) — quickstart
