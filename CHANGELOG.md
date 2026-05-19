# Changelog

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) + [SemVer](https://semver.org/).

## [Unreleased]

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
