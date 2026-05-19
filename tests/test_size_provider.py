"""Tests for the SizeProvider DI hook on build_tree."""
from __future__ import annotations

from pathlib import Path

from codechu_treeviz import SizeProvider, build_tree


def test_size_provider_not_called_when_none(tmp_path: Path) -> None:
    """Default behavior (size_provider=None) must not invoke any provider."""
    (tmp_path / "a.bin").write_bytes(b"x" * 1024)
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.bin").write_bytes(b"y" * 2048)

    tree = build_tree(tmp_path)  # no size_provider
    assert tree is not None
    assert tree.is_dir
    # Children were walked normally.
    assert len(tree.children) >= 1


def test_size_provider_called_for_each_directory_once(tmp_path: Path) -> None:
    """Provider is consulted once per directory encountered."""
    (tmp_path / "a.bin").write_bytes(b"x" * 1024)
    (tmp_path / "d1").mkdir()
    (tmp_path / "d1" / "n.bin").write_bytes(b"y" * 1024)
    (tmp_path / "d2").mkdir()
    (tmp_path / "d2" / "m.bin").write_bytes(b"z" * 1024)

    calls: list[Path] = []

    def provider(path: Path) -> int | None:
        calls.append(path)
        return None  # always fall through

    tree = build_tree(tmp_path, size_provider=provider)
    assert tree is not None

    # Root + both subdirs = 3 directories visited.
    assert len(calls) == 3
    # Each path exactly once.
    assert len(set(calls)) == 3
    assert tmp_path in calls
    assert tmp_path / "d1" in calls
    assert tmp_path / "d2" in calls


def test_size_provider_hit_skips_recursion(tmp_path: Path) -> None:
    """Returning an int short-circuits: empty children, cached size used."""
    (tmp_path / "cached").mkdir()
    (tmp_path / "cached" / "huge.bin").write_bytes(b"x" * 4096)
    (tmp_path / "cached" / "nested").mkdir()
    (tmp_path / "cached" / "nested" / "more.bin").write_bytes(b"y" * 2048)
    (tmp_path / "fresh.bin").write_bytes(b"z" * 512)

    CACHED_SIZE = 999_999

    def provider(path: Path) -> int | None:
        if path.name == "cached":
            return CACHED_SIZE
        return None

    tree = build_tree(tmp_path, size_provider=provider)
    assert tree is not None
    cached_node = next(c for c in tree.children if c.path.endswith("cached"))
    assert cached_node.is_dir
    assert cached_node.size == CACHED_SIZE
    # No recursion happened — children list is empty even though the
    # directory has real contents on disk.
    assert cached_node.children == []


def test_size_provider_none_falls_back_to_walk(tmp_path: Path) -> None:
    """Provider returning None must reproduce default behavior exactly."""
    (tmp_path / "a.bin").write_bytes(b"x" * 4096)
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.bin").write_bytes(b"y" * 8192)

    baseline = build_tree(tmp_path)
    via_provider = build_tree(tmp_path, size_provider=lambda _p: None)

    assert baseline is not None and via_provider is not None
    assert baseline.size == via_provider.size
    assert len(baseline.children) == len(via_provider.children)


def test_size_provider_protocol_is_exported() -> None:
    """SizeProvider Protocol is part of the public API."""
    assert SizeProvider is not None
