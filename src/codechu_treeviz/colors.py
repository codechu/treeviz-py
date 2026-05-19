"""Treemap/sunburst için renk paleti.

Top-level çocuk indeksine göre tutarlı (aynı dal her seferinde aynı ton),
derinlikte hafif kayma ile katman ayrımı. Dark mode'da daha sakin
(düşük sat ~0.40), light mode'da daha canlı.

``dark`` parametre olarak alınır — ``theme.is_dark_theme()`` çağrısı
çağıran kodun sorumluluğunda (Gtk bağımlılığını burada tutmuyoruz).
"""
from __future__ import annotations

import colorsys


def node_color(top_idx: int, depth: int, *, dark: bool, is_other: bool = False) -> tuple[float, float, float]:
    """RGB ``(r, g, b)`` döner (her bileşen 0..1).

    ``is_other`` küçük öğeleri toplayan 'Diğer' yumakları için: nötr gri
    palet (renkli salata önlenir).
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
