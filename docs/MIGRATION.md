# Migration — `codechu_treeviz`

## 0.1.x → 0.2.0

**No breaking changes.** Existing code keeps working as-is.

### What moved

The bundled strategies now live in a `strategies/` subpackage:

```
codechu_treeviz/
├── strategies/
│   ├── treemap.py       (was codechu_treeviz/treemap.py)
│   ├── sunburst.py      (was codechu_treeviz/sunburst.py)
│   ├── icicle.py        (new)
│   ├── slicedice.py     (new)
│   └── flamegraph.py    (new)
├── strategy.py          (VizStrategy ABC — unchanged location)
├── tree_node.py
├── colors.py
└── text.py
```

### Why it doesn't break

Three import paths all continue to work:

```python
# Recommended (unchanged from 0.1)
from codechu_treeviz import TreemapStrategy, SunburstStrategy, layout_treemap

# Explicit subpackage (new in 0.2)
from codechu_treeviz.strategies import TreemapStrategy
from codechu_treeviz.strategies.treemap import layout_treemap

# Legacy module path (re-export shim, kept for 0.1 compatibility)
from codechu_treeviz.treemap import TreemapStrategy, layout_treemap
from codechu_treeviz.sunburst import SunburstStrategy, layout_sunburst
```

`codechu_treeviz.treemap` and `codechu_treeviz.sunburst` are now thin
shims that re-export from `codechu_treeviz.strategies.*`. If you used
either path in 0.1.x you do not need to change anything.

### New API surface

Three new strategies, each a `VizStrategy` subclass:

| Class                 | Layout shape | Notes                                       |
|-----------------------|--------------|---------------------------------------------|
| `IcicleStrategy`      | 4-tuple      | Horizontal strips, one per depth level      |
| `SliceDiceStrategy`   | 4-tuple      | Alternating-axis treemap, preserves order   |
| `FlameGraphStrategy`  | 4-tuple      | Like icicle but rooted at the bottom        |

See [`API.md`](API.md) for full reference and [`RECIPES.md`](RECIPES.md)
for example usage.

### `node.rect` shape unchanged

All new strategies use the same 4-tuple `(x, y, w, h)` as `TreemapStrategy`.
Only `SunburstStrategy` continues to use a 7-tuple. Drawing code that
already handles treemap rects can render the three new strategies
without modification.

### Recommended action

Nothing required. To follow the new convention in fresh code, prefer:

```python
from codechu_treeviz import TreemapStrategy        # top-level
# instead of
from codechu_treeviz.treemap import TreemapStrategy  # legacy shim
```

The shim modules will stay through the 0.x line; we will not remove
them without a major-version bump.
