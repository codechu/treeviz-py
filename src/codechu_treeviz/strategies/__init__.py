"""Strategy implementations for :class:`VizStrategy`.

Each module in this subpackage hosts one visualization layout.
The bundled strategies are also re-exported from the top-level
``codechu_treeviz`` package for backwards compatibility.
"""
from __future__ import annotations

from .flamegraph import FlameGraphStrategy, flamegraph_hit_test, layout_flamegraph
from .icicle import IcicleStrategy, icicle_hit_test, layout_icicle
from .slicedice import SliceDiceStrategy, layout_slicedice, slicedice_hit_test
from .sunburst import SunburstStrategy, layout_sunburst, sunburst_hit_test
from .treemap import OTHER_MARKER, TreemapStrategy, hit_test, layout_treemap

__all__ = [
    "OTHER_MARKER",
    "FlameGraphStrategy",
    "IcicleStrategy",
    "SliceDiceStrategy",
    "SunburstStrategy",
    "TreemapStrategy",
    "flamegraph_hit_test",
    "hit_test",
    "icicle_hit_test",
    "layout_flamegraph",
    "layout_icicle",
    "layout_slicedice",
    "layout_sunburst",
    "layout_treemap",
    "slicedice_hit_test",
    "sunburst_hit_test",
]
