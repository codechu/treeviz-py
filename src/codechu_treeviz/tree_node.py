"""TreeNode + ``build_tree`` — Disk map data structure.

Recursive directory walk is guarded against symlink loops and excessive
depth. File size is taken from ``st_blocks * 512`` — accurate disk usage
for sparse files.
"""
from __future__ import annotations

import stat as statmod
from pathlib import Path
from threading import Event
from typing import Callable, Optional, Protocol

TREEMAP_MAX_DEPTH: int = 40  # protect against pathological depth


class SizeProvider(Protocol):
    """Optional override for directory size during build_tree.

    Called with the directory's Path. Return the cached size in bytes
    if available — build_tree will skip recursing into that directory
    and use the returned size. Return None to fall back to fresh
    walk + lstat aggregation.

    Typical use: a disk-usage cache that's valid as long as the
    directory's mtime hasn't changed since the cached value was
    written. The provider, not build_tree, owns the freshness policy.
    """
    def __call__(self, path: "Path") -> "int | None": ...


class TreeNode:
    """A single directory/file node used by treemap / sunburst layouts."""

    __slots__ = ("path", "size", "children", "rect", "is_dir", "is_other", "small_count")

    def __init__(
        self,
        path: str,
        size: int,
        children: list["TreeNode"] | None = None,
        is_dir: bool = False,
        *,
        is_other: bool = False,
        small_count: int = 0,
    ) -> None:
        self.path: str = path
        self.size: int = size
        self.children: list[TreeNode] = children or []
        # ``rect`` is set after layout; treemap → 4-tuple
        # ``(x, y, w, h)``, sunburst → 7-tuple
        # ``(cx, cy, r_in, r_out, a0, a1, top_idx)``.
        self.rect: tuple[float, ...] | None = None
        self.is_dir: bool = is_dir
        self.is_other: bool = is_other
        self.small_count: int = small_count


def build_tree(
    root: str | Path,
    cancel: Optional[Event] = None,
    progress: Optional[Callable[[str], None]] = None,
    *,
    max_depth: int = TREEMAP_MAX_DEPTH,
    size_provider: SizeProvider | None = None,
) -> TreeNode | None:
    """Walk ``root`` and return a :class:`TreeNode` (DFS).

    Args:
        root: directory to walk
        cancel: optional threading.Event — if set during walk, returns
            partial tree and stops descending
        progress: optional callback receiving short status strings; cheap
            to call (called once per directory entered)
        max_depth: depth ceiling to protect against pathological nesting
            (default: ``TREEMAP_MAX_DEPTH``, ie. 40)
        size_provider: optional :class:`SizeProvider` — if it returns a
            non-None size for a directory, recursion into that directory
            is skipped and the cached size is used.
    """
    root_p = Path(root).expanduser()
    counter = [0]  # mutable capture — file counter
    return _build(root_p, cancel, depth=0, seen=set(),
                  progress=progress, counter=counter, max_depth=max_depth,
                  size_provider=size_provider)


def _build(
    p: Path,
    cancel: Optional[Event],
    depth: int,
    seen: set[tuple[int, int]],
    progress: Optional[Callable[[str], None]],
    counter: list[int],
    max_depth: int,
    size_provider: SizeProvider | None = None,
) -> TreeNode | None:
    if cancel is not None and cancel.is_set():
        return None
    if depth > max_depth:
        return TreeNode(str(p), 0, is_dir=True)
    try:
        st = p.lstat()
    except OSError:
        return None
    if statmod.S_ISLNK(st.st_mode):
        return TreeNode(str(p), 0, is_dir=False)
    if not statmod.S_ISDIR(st.st_mode):
        counter[0] += 1
        # st_blocks * 512 = actual disk usage (correct for sparse files).
        return TreeNode(str(p), st.st_blocks * 512, is_dir=False)
    # Directory — consult the size provider before recursing.
    if size_provider is not None:
        cached = size_provider(p)
        if cached is not None:
            return TreeNode(str(p), int(cached), is_dir=True, children=[])
    key = (st.st_dev, st.st_ino)
    if key in seen:
        return TreeNode(str(p), 0, is_dir=True)
    seen.add(key)
    if progress is not None:
        progress("{n} files · {p}".format(n=counter[0], p=p))
    children: list[TreeNode] = []
    total = 0
    try:
        for c in p.iterdir():
            sub = _build(c, cancel, depth + 1, seen, progress, counter, max_depth,
                         size_provider=size_provider)
            if sub:
                children.append(sub)
                total += sub.size
    except (PermissionError, OSError):
        pass
    children.sort(key=lambda n: -n.size)
    return TreeNode(str(p), total, children=children, is_dir=True)


__all__ = ["TreeNode", "SizeProvider", "build_tree"]
