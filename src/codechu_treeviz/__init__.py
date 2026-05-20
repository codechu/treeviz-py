"""Visualization subpackage.

- :class:`TreeNode` + :func:`build_tree` — disk map data structure
- :class:`SizeProvider` — dependency-injection protocol for cached directory sizes
- :class:`TreemapStrategy` — squarified treemap (Bruls, Huijsen, van Wijk 2000)
- :class:`SunburstStrategy` — radial treemap
- :class:`IcicleStrategy` — icicle plot (horizontal strips by depth)
- :class:`SliceDiceStrategy` — slice-and-dice treemap (order-preserving)
- :class:`FlameGraphStrategy` — flame graph (CPU-profiling style)
- :func:`node_color` — shared color palette (dark/light)
- :func:`is_hash_like` — label helper
"""
from __future__ import annotations

from .colors import node_color
from .strategies.flamegraph import (
    FlameGraphStrategy,
    flamegraph_hit_test,
    layout_flamegraph,
)
from .strategies.icicle import IcicleStrategy, icicle_hit_test, layout_icicle
from .strategies.slicedice import (
    SliceDiceStrategy,
    layout_slicedice,
    slicedice_hit_test,
)
from .strategies.sunburst import SunburstStrategy, layout_sunburst, sunburst_hit_test
from .strategies.treemap import (
    OTHER_MARKER,
    TreemapStrategy,
    hit_test,
    layout_treemap,
)
from .strategy import VizStrategy
from .text import is_hash_like
from .tree_node import SizeProvider, TreeNode, build_tree

__all__ = [
    "OTHER_MARKER",
    "FlameGraphStrategy",
    "IcicleStrategy",
    "SizeProvider",
    "SliceDiceStrategy",
    "SunburstStrategy",
    "TreeNode",
    "TreemapStrategy",
    "VizStrategy",
    "build_tree",
    "flamegraph_hit_test",
    "hit_test",
    "icicle_hit_test",
    "is_hash_like",
    "layout_flamegraph",
    "layout_icicle",
    "layout_slicedice",
    "layout_sunburst",
    "layout_treemap",
    "node_color",
    "slicedice_hit_test",
    "sunburst_hit_test",
]
