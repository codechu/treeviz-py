"""Visualization Strategy ABC.

Treemap and Sunburst implement the same interface; when the UI switches
tabs it only swaps the :class:`VizStrategy` instance. A new visualization
(icicle, flame graph, ...) can be added as a :class:`VizStrategy`
subclass.

For now ``layout`` and ``hit_test`` are mandatory (pure logic, lives in
this subpackage). ``draw`` is optional — current implementations do the
cairo drawing in the UI panel (intertwined with animation + hover state).
In Phase G the panel will delegate to ``strategy.draw``.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import cairo

    from .tree_node import TreeNode


class VizStrategy(ABC):
    """Visualization strategy — layout + hit-test (mandatory), draw (optional)."""

    name: str = "unknown"

    @abstractmethod
    def layout(self, node: "TreeNode", w: float, h: float) -> None:
        """Compute recursive layout for the given canvas and write it onto the nodes."""

    @abstractmethod
    def hit_test(self, node: "TreeNode", x: float, y: float) -> Optional["TreeNode"]:
        """Find the node at ``(x, y)`` (None if there isn't one)."""

    def draw(
        self,
        cr: "cairo.Context",
        node: "TreeNode",
        *,
        hover: Optional["TreeNode"] = None,
        dark: bool = False,
    ) -> None:
        """Draw onto a cairo context.

        The default implementation raises ``NotImplementedError`` because
        the UI panel currently performs this work. Override in a subclass
        to use a strategy directly.
        """
        raise NotImplementedError(
            f"{type(self).__name__}.draw is not on the strategy yet — "
            "the UI panel (TreemapPanel/SunburstPanel) does the drawing."
        )


__all__ = ["VizStrategy"]
