"""Color palette for treemap/sunburst.

Hue is consistent per top-level child index (the same branch always
gets the same tone), with a slight shift per depth to separate layers.
Dark mode is calmer (lower saturation ~0.40); light mode is more vivid.

``dark`` is passed in as a parameter — calling ``theme.is_dark_theme()``
is the caller's responsibility (we keep the Gtk dependency out of here).
"""
from __future__ import annotations

import colorsys


def node_color(top_idx: int, depth: int, *, dark: bool, is_other: bool = False) -> tuple[float, float, float]:
    """Return RGB ``(r, g, b)`` with each component in 0..1.

    ``is_other`` selects a neutral gray palette for the bundle node that
    aggregates small items (avoids a salad of colors).
    """
    if is_other:
        v = (0.40 + min(depth, 4) * 0.03) if dark else (0.85 - min(depth, 4) * 0.05)
        return (v, v, v)
    base_hue = (top_idx * 0.618 + 0.08) % 1.0
    hue = (base_hue + depth * 0.015) % 1.0
    if dark:
        lightness = max(0.30, 0.42 + min(depth, 5) * 0.04)
        sat = max(0.28, 0.45 - min(depth, 5) * 0.04)
    else:
        lightness = min(0.82, 0.50 + min(depth, 5) * 0.05)
        sat = max(0.40, 0.72 - min(depth, 5) * 0.06)
    return colorsys.hls_to_rgb(hue, lightness, sat)


__all__ = ["node_color"]
