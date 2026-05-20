"""Flame graph layout — CPU-profiling-style stack visualization.

A flame graph is an icicle plot rotated 180 degrees: the root sits at
the *bottom* of the canvas and deeper levels stack *upward*. The visual
metaphor is a flame — wide hot frames at the base, narrower call sites
toward the tip.

Although flame graphs originated for CPU profiling, the layout is
exactly the same shape as an icicle plot and works for any
hierarchical size data.

``node.rect`` is a 4-tuple ``(x, y, w, h)``.
"""
from __future__ import annotations

from typing import Optional

from ..strategy import VizStrategy
from ..tree_node import TreeNode

_DEFAULT_MAX_DEPTH = 8


def layout_flamegraph(
    node: TreeNode,
    x: float,
    y: float,
    w: float,
    h: float,
    depth: int = 0,
    max_depth: int = _DEFAULT_MAX_DEPTH,
) -> None:
    """Flame graph layout — writes 4-tuple ``(x, y, w, h)`` rects.

    The entry ``(x, y, w, h)`` describes the *entire* canvas; the root
    is placed at the bottom row inside that rect, children stack upward
    above their parent. Each row is ``h / (max_depth + 1)`` tall.
    """
    if max_depth <= 0 or h <= 0 or w <= 0:
        node.rect = (x, y, w, max(h, 0.0))
        return
    row_h = h / (max_depth + 1)
    # Root anchored at the bottom of the canvas
    node.rect = (x, y + h - row_h, w, row_h)
    if not node.children or node.size == 0 or depth >= max_depth:
        return
    total = sum(c.size for c in node.children)
    if total <= 0:
        return
    cx = x
    # Children occupy the canvas above the current row
    child_canvas_h = h - row_h
    for c in node.children:
        cw = w * c.size / total
        layout_flamegraph(c, cx, y, cw, child_canvas_h, depth + 1, max_depth - 1)
        cx += cw


def flamegraph_hit_test(node: TreeNode, mx: float, my: float) -> Optional[TreeNode]:
    """Find the deepest node containing ``(mx, my)``.

    Children are tested first so a click on a higher stack frame hits
    the deeper call rather than the root at the base.
    """
    if node.rect is None or len(node.rect) != 4:
        return None
    for c in node.children:
        hit = flamegraph_hit_test(c, mx, my)
        if hit is not None:
            return hit
    x, y, w, h = node.rect
    if x <= mx <= x + w and y <= my <= y + h:
        return node
    return None


class FlameGraphStrategy(VizStrategy):
    """:class:`VizStrategy` — flame graph (inverted icicle).

    ``max_depth`` controls how many call levels are drawn; the canvas
    is sliced into ``max_depth + 1`` rows.
    """

    name = "flamegraph"

    def __init__(self, max_depth: int = _DEFAULT_MAX_DEPTH) -> None:
        self.max_depth = max_depth

    def layout(self, node: TreeNode, w: float, h: float) -> None:
        layout_flamegraph(node, 0.0, 0.0, float(w), float(h), max_depth=self.max_depth)

    def hit_test(self, node: TreeNode, x: float, y: float) -> Optional[TreeNode]:
        return flamegraph_hit_test(node, x, y)


__all__ = ["FlameGraphStrategy", "flamegraph_hit_test", "layout_flamegraph"]
