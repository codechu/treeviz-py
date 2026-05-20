"""Backwards-compatible shim — see :mod:`codechu_treeviz.strategies.treemap`.

The implementation moved to the :mod:`codechu_treeviz.strategies` subpackage in
v0.2.0. This module re-exports the same names so existing imports keep working.
"""
from __future__ import annotations

from .strategies.treemap import (
    OTHER_MARKER,
    TreemapStrategy,
    hit_test,
    layout_treemap,
)

__all__ = [
    "OTHER_MARKER",
    "TreemapStrategy",
    "hit_test",
    "layout_treemap",
]
