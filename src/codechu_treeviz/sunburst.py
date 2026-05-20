"""Backwards-compatible shim — see :mod:`codechu_treeviz.strategies.sunburst`.

The implementation moved to the :mod:`codechu_treeviz.strategies` subpackage in
v0.2.0. This module re-exports the same names so existing imports keep working.
"""
from __future__ import annotations

from .strategies.sunburst import (
    SunburstStrategy,
    layout_sunburst,
    sunburst_hit_test,
)

__all__ = [
    "SunburstStrategy",
    "layout_sunburst",
    "sunburst_hit_test",
]
