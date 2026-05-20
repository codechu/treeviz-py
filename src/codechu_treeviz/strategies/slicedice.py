"""Slice-and-dice treemap — alternating-axis treemap algorithm.

The slice-and-dice algorithm (Shneiderman, 1992) is the original
treemap layout: at each level, split the parent rectangle along one
axis, alternating horizontal/vertical at every level. Children are
sized proportionally to ``node.size``.

Compared to the squarified treemap (:mod:`.treemap`) it produces less
square aspect ratios but preserves sibling order, which is useful when
order encodes meaning (chronology, alphabetical, …).

``node.rect`` is a 4-tuple ``(x, y, w, h)``.
"""
from __future__ import annotations

from typing import Optional

from ..strategy import VizStrategy
from ..tree_node import TreeNode


def layout_slicedice(
    node: TreeNode,
    x: float,
    y: float,
    w: float,
    h: float,
    depth: int = 0,
    horizontal: Optional[bool] = None,
) -> None:
    """Slice-and-dice treemap — writes 4-tuple rects onto every node.

    ``horizontal`` controls the first split: if ``None`` (default) the
    longer axis is sliced first, then alternates. If ``True`` the first
    split is along x (vertical cuts); if ``False`` along y.

    Unlike squarified treemap, this lays out the *whole* subtree
    recursively (one call covers all descendants).
    """
    node.rect = (x, y, w, h)
    if not node.children or node.size == 0 or w < 1 or h < 1:
        return
    total = sum(c.size for c in node.children)
    if total <= 0:
        return
    if horizontal is None:
        horizontal = w >= h
    pos = 0.0
    for c in node.children:
        frac = c.size / total
        if horizontal:
            cw = w * frac
            layout_slicedice(c, x + pos, y, cw, h, depth + 1, not horizontal)
            pos += cw
        else:
            ch = h * frac
            layout_slicedice(c, x, y + pos, w, ch, depth + 1, not horizontal)
            pos += ch


def slicedice_hit_test(node: TreeNode, mx: float, my: float) -> Optional[TreeNode]:
    """Find the deepest node containing ``(mx, my)``.

    Children are tested first so descendants take precedence over the
    enclosing parent rectangle.
    """
    if node.rect is None or len(node.rect) != 4:
        return None
    for c in node.children:
        hit = slicedice_hit_test(c, mx, my)
        if hit is not None:
            return hit
    x, y, w, h = node.rect
    if x <= mx <= x + w and y <= my <= y + h:
        return node
    return None


class SliceDiceStrategy(VizStrategy):
    """:class:`VizStrategy` — slice-and-dice treemap (order-preserving).

    Use this when the order of sibling nodes matters (e.g. a timeline)
    and aspect ratios are less important than predictable placement.
    """

    name = "slicedice"

    def __init__(self, horizontal: Optional[bool] = None) -> None:
        self.horizontal = horizontal

    def layout(self, node: TreeNode, w: float, h: float) -> None:
        layout_slicedice(node, 0.0, 0.0, float(w), float(h), horizontal=self.horizontal)

    def hit_test(self, node: TreeNode, x: float, y: float) -> Optional[TreeNode]:
        return slicedice_hit_test(node, x, y)


__all__ = ["SliceDiceStrategy", "layout_slicedice", "slicedice_hit_test"]
