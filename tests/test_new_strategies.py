"""Tests for v0.2 strategies: Icicle, SliceDice, FlameGraph."""
from __future__ import annotations

import pytest

from codechu_treeviz import (
    FlameGraphStrategy,
    IcicleStrategy,
    SliceDiceStrategy,
    TreeNode,
    VizStrategy,
    flamegraph_hit_test,
    icicle_hit_test,
    layout_flamegraph,
    layout_icicle,
    layout_slicedice,
    slicedice_hit_test,
)


def _mk_tree() -> TreeNode:
    root = TreeNode("root", 1000, is_dir=True)
    root.children = [
        TreeNode("a", 600, is_dir=False),
        TreeNode("b", 300, is_dir=False),
        TreeNode("c", 100, is_dir=False),
    ]
    return root


def _mk_nested() -> TreeNode:
    root = TreeNode("root", 1000, is_dir=True)
    a = TreeNode("a", 700, is_dir=True)
    a.children = [
        TreeNode("a/1", 400, is_dir=False),
        TreeNode("a/2", 300, is_dir=False),
    ]
    b = TreeNode("b", 300, is_dir=False)
    root.children = [a, b]
    return root


# ── strategy contract ────────────────────────────────────────────────


@pytest.mark.parametrize("strat", [
    IcicleStrategy(),
    SliceDiceStrategy(),
    FlameGraphStrategy(),
])
def test_strategy_is_vizstrategy(strat):
    assert isinstance(strat, VizStrategy)
    assert isinstance(strat.name, str) and strat.name


@pytest.mark.parametrize("strat", [
    IcicleStrategy(),
    SliceDiceStrategy(),
    FlameGraphStrategy(),
])
def test_strategy_layout_sets_rects(strat):
    root = _mk_tree()
    strat.layout(root, 200.0, 100.0)
    assert root.rect is not None
    assert len(root.rect) == 4
    for c in root.children:
        assert c.rect is not None
        assert len(c.rect) == 4


@pytest.mark.parametrize("strat", [
    IcicleStrategy(),
    SliceDiceStrategy(),
    FlameGraphStrategy(),
])
def test_strategy_draw_default_raises(strat):
    root = _mk_tree()
    strat.layout(root, 100.0, 100.0)
    with pytest.raises(NotImplementedError):
        strat.draw(None, root)


# ── icicle ───────────────────────────────────────────────────────────


def test_layout_icicle_root_is_top_strip():
    root = _mk_tree()
    layout_icicle(root, 0, 0, 200, 100, max_depth=4)
    rx, ry, rw, rh = root.rect
    assert (rx, ry) == (0, 0)
    assert rw == 200
    # row height = h / (max_depth + 1) = 100 / 5 = 20
    assert rh == pytest.approx(20.0)
    # Children should sit below the root strip
    for c in root.children:
        cx, cy, cw, ch = c.rect
        assert cy >= rh - 1e-6


def test_layout_icicle_children_widths_proportional():
    root = _mk_tree()
    layout_icicle(root, 0, 0, 1000, 100, max_depth=4)
    a, b, c = root.children
    assert a.rect[2] == pytest.approx(600.0)
    assert b.rect[2] == pytest.approx(300.0)
    assert c.rect[2] == pytest.approx(100.0)


def test_icicle_hit_test_finds_child():
    root = _mk_nested()
    layout_icicle(root, 0, 0, 200, 200, max_depth=4)
    a = root.children[0]
    ax, ay, aw, ah = a.rect
    hit = icicle_hit_test(root, ax + aw / 2, ay + ah / 2)
    # Inside 'a' but a has its own children stacked below; we should hit
    # either a or one of its descendants. Both are acceptable — test
    # that hit landed within the 'a' branch.
    assert hit is not None
    assert hit is a or hit in a.children


def test_icicle_hit_test_miss_returns_none():
    root = _mk_tree()
    layout_icicle(root, 0, 0, 100, 100, max_depth=4)
    assert icicle_hit_test(root, -50, -50) is None


def test_icicle_draw_smoke():
    """Smoke test: layout + hit_test runs without exceptions on a real-ish tree."""
    root = _mk_nested()
    strat = IcicleStrategy(max_depth=3)
    strat.layout(root, 400.0, 200.0)
    # Hit-test a grid of points; nothing should explode.
    for gx in range(0, 400, 50):
        for gy in range(0, 200, 50):
            strat.hit_test(root, float(gx), float(gy))


# ── slice & dice ─────────────────────────────────────────────────────


def test_layout_slicedice_root_covers_canvas():
    root = _mk_tree()
    layout_slicedice(root, 0, 0, 300, 200)
    assert root.rect == (0, 0, 300, 200)


def test_layout_slicedice_children_tile_parent():
    """Children should exactly tile the parent — sum of widths = parent w."""
    root = _mk_tree()
    layout_slicedice(root, 0, 0, 300, 200, horizontal=True)
    total_w = sum(c.rect[2] for c in root.children)
    assert total_w == pytest.approx(300.0)
    for c in root.children:
        assert c.rect[1] == 0
        assert c.rect[3] == pytest.approx(200.0)


def test_layout_slicedice_alternates_axis():
    """First split horizontal, second split vertical."""
    root = _mk_nested()
    layout_slicedice(root, 0, 0, 300, 200, horizontal=True)
    a = root.children[0]  # 'a' has children — second level should be vertical
    # 'a' rect width covers a fraction of the canvas; its children stack vertically
    a_w = a.rect[2]
    for c in a.children:
        assert c.rect[2] == pytest.approx(a_w)


def test_slicedice_hit_test_finds_leaf():
    root = _mk_nested()
    layout_slicedice(root, 0, 0, 300, 200)
    leaf = root.children[0].children[0]
    lx, ly, lw, lh = leaf.rect
    hit = slicedice_hit_test(root, lx + lw / 2, ly + lh / 2)
    assert hit is leaf


def test_slicedice_hit_test_miss_returns_none():
    root = _mk_tree()
    layout_slicedice(root, 0, 0, 100, 100)
    assert slicedice_hit_test(root, -10, -10) is None


def test_slicedice_draw_smoke():
    root = _mk_nested()
    strat = SliceDiceStrategy()
    strat.layout(root, 400.0, 300.0)
    for gx in (10.0, 100.0, 200.0, 350.0):
        strat.hit_test(root, gx, 150.0)


# ── flame graph ──────────────────────────────────────────────────────


def test_layout_flamegraph_root_anchored_at_bottom():
    root = _mk_tree()
    layout_flamegraph(root, 0, 0, 200, 100, max_depth=4)
    rx, ry, rw, rh = root.rect
    # row_h = 20; root y = 100 - 20 = 80
    assert ry == pytest.approx(80.0)
    assert rh == pytest.approx(20.0)
    # Children should be above the root
    for c in root.children:
        cy = c.rect[1]
        assert cy < ry + 1e-6


def test_layout_flamegraph_children_widths_proportional():
    root = _mk_tree()
    layout_flamegraph(root, 0, 0, 1000, 100, max_depth=4)
    a, b, c = root.children
    assert a.rect[2] == pytest.approx(600.0)
    assert b.rect[2] == pytest.approx(300.0)
    assert c.rect[2] == pytest.approx(100.0)


def test_flamegraph_hit_test_finds_root():
    root = _mk_tree()
    layout_flamegraph(root, 0, 0, 200, 100, max_depth=4)
    rx, ry, rw, rh = root.rect
    hit = flamegraph_hit_test(root, rx + rw / 2, ry + rh / 2)
    assert hit is root


def test_flamegraph_hit_test_miss_returns_none():
    root = _mk_tree()
    layout_flamegraph(root, 0, 0, 100, 100, max_depth=4)
    assert flamegraph_hit_test(root, -10, -10) is None


def test_flamegraph_draw_smoke():
    root = _mk_nested()
    strat = FlameGraphStrategy(max_depth=3)
    strat.layout(root, 400.0, 200.0)
    for gx in range(0, 400, 50):
        for gy in range(0, 200, 50):
            strat.hit_test(root, float(gx), float(gy))


# ── package layout / re-exports ──────────────────────────────────────


def test_strategies_subpackage_re_exports():
    from codechu_treeviz import strategies
    assert strategies.IcicleStrategy is IcicleStrategy
    assert strategies.SliceDiceStrategy is SliceDiceStrategy
    assert strategies.FlameGraphStrategy is FlameGraphStrategy
    # Existing strategies are also hosted there
    from codechu_treeviz import SunburstStrategy, TreemapStrategy
    assert strategies.TreemapStrategy is TreemapStrategy
    assert strategies.SunburstStrategy is SunburstStrategy


def test_legacy_module_imports_still_work():
    """Old import paths must keep working after the strategies/ move."""
    from codechu_treeviz.treemap import TreemapStrategy as T, layout_treemap, hit_test  # noqa: F401
    from codechu_treeviz.sunburst import SunburstStrategy as S, layout_sunburst  # noqa: F401
    assert T is not None
    assert S is not None
