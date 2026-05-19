# Tests — codechu-treeviz

Run the suite from the repo root:

```bash
pytest -q
```

With coverage:

```bash
pytest --cov=codechu_treeviz --cov-report=term-missing
```

## Coverage gate

The coverage floor is **85 %**. PRs that drop below it are rejected;
add tests with your change.

## Conventions

- Layout output is geometry — assert on coordinates with
  `pytest.approx`, not on rendered pixels.
- Property-based tests (via `hypothesis`) are welcome for invariants
  like area conservation, no-overlap, and child-fits-in-parent.
- Cover boundary cases: empty children, one giant + many slivers,
  deeply nested trees, zero-size nodes.
