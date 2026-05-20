"""Icicle plot layout — horizontal strips, one per depth level.

Like a treemap, but instead of nesting children inside their parent's
rectangle the children are laid out as a strip *below* the parent. The
strip's vertical position is determined by depth; its width is
proportional to the child's share of the parent.

The result reads top-to-bottom: the root is the top bar, level 1 is
the strip directly beneath, and so on. Sibling order is preserved, so
visually adjacent rectangles share a parent.

``node.rect`` is a 4-tuple ``(x, y, w, h)`` — same shape as treemap, so
the same drawing/hit-test helpers can share a code path.
"""
from __future__ import annotations

from typing import Optional

from ..strategy import VizStrategy
from ..tree_node import TreeNode

_DEFAULT_MAX_DEPTH = 8


def layout_icicle(
    node: TreeNode,
    x: float,
    y: float,
    w: float,
    h: float,
    depth: int = 0,
    max_depth: int = _DEFAULT_MAX_DEPTH,
) -> None:
    """Icicle plot — writes 4-tuple ``(x, y, w, h)`` rects onto every node.

    Each level is a horizontal strip of equal height ``row_h``; children
    of a node are packed left-to-right inside the parent's column span,
    each child's width proportional to its size.

    Recurses up to ``max_depth`` levels below the entry depth.
    """
    if max_depth <= 0 or h <= 0 or w <= 0:
        node.rect = (x, y, w, max(h, 0.0))
        return
    row_h = h / (max_depth + 1)
    node.rect = (x, y, w, row_h)
    if not node.children or node.size == 0 or depth >= max_depth:
        return
    total = sum(c.size for c in node.children)
    if total <= 0:
        return
    cx = x
    remaining_h = h - row_h
    for c in node.children:
        cw = w * c.size / total
        layout_icicle(c, cx, y + row_h, cw, remaining_h, depth + 1, max_depth - 1)
        cx += cw


def icicle_hit_test(node: TreeNode, mx: float, my: float) -> Optional[TreeNode]:
    """Find the deepest node containing ``(mx, my)``.

    Children are tested first so a click on a lower (deeper) strip hits
    the descendant rather than the ancestor whose column it falls in.
    Skips nodes with a non-4-tuple ``rect`` (e.g. stale sunburst data).
    """
    if node.rect is None or len(node.rect) != 4:
        return None
    for c in node.children:
        hit = icicle_hit_test(c, mx, my)
        if hit is not None:
            return hit
    x, y, w, h = node.rect
    if x <= mx <= x + w and y <= my <= y + h:
        return node
    return None


class IcicleStrategy(VizStrategy):
    """:class:`VizStrategy` — icicle plot (horizontal strips by depth).

    ``max_depth`` controls how many levels of strips are drawn; the
    canvas height is divided evenly across ``max_depth + 1`` rows so
    deeper trees compress automatically.
    """

    name = "icicle"

    def __init__(self, max_depth: int = _DEFAULT_MAX_DEPTH) -> None:
        self.max_depth = max_depth

    def layout(self, node: TreeNode, w: float, h: float) -> None:
        layout_icicle(node, 0.0, 0.0, float(w), float(h), max_depth=self.max_depth)

    def hit_test(self, node: TreeNode, x: float, y: float) -> Optional[TreeNode]:
        return icicle_hit_test(node, x, y)


__all__ = ["IcicleStrategy", "icicle_hit_test", "layout_icicle"]
