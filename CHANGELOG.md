# Changelog

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) + [SemVer](https://semver.org/).

## [Unreleased]

## [0.2.0] — 2026-05-20

### Added
- `IcicleStrategy` — icicle plot (horizontal strips, one per depth level)
- `SliceDiceStrategy` — slice-and-dice treemap (order-preserving, alternating-axis)
- `FlameGraphStrategy` — flame graph (inverted icicle, CPU-profiling-style)
- `strategies/` subpackage hosting every bundled `VizStrategy`
- `docs/MIGRATION.md` — v0.1 → v0.2 notes

### Changed
- `TreemapStrategy` and `SunburstStrategy` moved into `codechu_treeviz.strategies/`.
  Top-level imports (`from codechu_treeviz import ...`) and the legacy
  `codechu_treeviz.treemap` / `codechu_treeviz.sunburst` module paths
  continue to work via re-export shims — no breaking change.

## [0.1.0] — 2026-05-19

### Added
- Initial extraction from [codechu/disk-cleaner](https://github.com/codechu/disk-cleaner)
- Squarified treemap (Bruls/Huijsen/van Wijk algorithm)
- Concentric-ring sunburst layout
- `TreeNode` builder from flat `(path, size)` records
- Hit testing for treemap rects + sunburst arcs
- "Other" bundling for small slivers
- Stable color palette per node identity
- Hash-like name detection (cache key vs human label)
- Pure stdlib — no rendering / GUI dependency
