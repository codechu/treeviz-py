"""TreeNode + ``build_tree`` — Disk haritası veri yapısı.

Recursive dizin walk'u, sembolik link döngülerine ve aşırı derinliğe
karşı korunuyor. Dosya boyutu ``st_blocks * 512`` ile alınır — sparse
dosyalar için gerçek disk kullanımı.
"""
from __future__ import annotations

import stat as statmod
from pathlib import Path
from threading import Event
from typing import Callable, Optional

TREEMAP_MAX_DEPTH: int = 40  # protect against pathological depth


class TreeNode:
    """Treemap / sunburst için tek bir dizin/dosya düğümü."""

    __slots__ = ("path", "size", "children", "rect", "is_dir")

    def __init__(
        self,
        path: str,
        size: int,
        children: list["TreeNode"] | None = None,
        is_dir: bool = False,
    ) -> None:
        self.path: str = path
        self.size: int = size
        self.children: list[TreeNode] = children or []
        # ``rect`` layout sonrası set edilir; treemap → 4-tuple
        # ``(x, y, w, h)``, sunburst → 7-tuple
        # ``(cx, cy, r_in, r_out, a0, a1, top_idx)``.
        self.rect: tuple[float, ...] | None = None
        self.is_dir: bool = is_dir


def build_tree(
    root: str | Path,
    cancel: Optional[Event] = None,
    progress: Optional[Callable[[str], None]] = None,
    *,
    max_depth: int = TREEMAP_MAX_DEPTH,
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
    """
    root_p = Path(root).expanduser()
    counter = [0]  # mutable capture — file counter
    return _build(root_p, cancel, depth=0, seen=set(),
                  progress=progress, counter=counter, max_depth=max_depth)


def _build(
    p: Path,
    cancel: Optional[Event],
    depth: int,
    seen: set[tuple[int, int]],
    progress: Optional[Callable[[str], None]],
    counter: list[int],
    max_depth: int,
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
        # st_blocks * 512 = gerçek disk kullanımı (sparse için doğru).
        return TreeNode(str(p), st.st_blocks * 512, is_dir=False)
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
            sub = _build(c, cancel, depth + 1, seen, progress, counter, max_depth)
            if sub:
                children.append(sub)
                total += sub.size
    except (PermissionError, OSError):
        pass
    children.sort(key=lambda n: -n.size)
    return TreeNode(str(p), total, children=children, is_dir=True)


__all__ = ["TreeNode", "build_tree"]
