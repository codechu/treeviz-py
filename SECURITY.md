# Security policy

`codechu-treeviz` is a pure-Python layout library. It does not touch
the network, the filesystem, or `subprocess`. The threat model is
therefore narrow — but malformed input (huge trees, pathological
recursion, NaN / inf sizes) can still create denial-of-service
issues, and we treat those as security-relevant.

## Supported versions

| Version | Supported |
|---|:---:|
| `main` branch | ✅ |
| Latest minor release (0.x) | ✅ |
| Older releases | ❌ |

Pre-1.0.0 period — only the latest minor receives security fixes.

## Reporting a vulnerability

### Preferred path — GitHub Security Advisory (private)

Open a **private** advisory at
[github.com/codechu/codechu-treeviz-py/security/advisories/new](https://github.com/codechu/codechu-treeviz-py/security/advisories/new).
The disclosure stays non-public until a fix lands, and a CVE can be
requested automatically.

### Alternative — Email

Write to `security@codechu.com`.

## Scope — what to report

**In scope:**

- **Unbounded recursion / stack overflow** on attacker-controlled
  tree depths (the `max_depth` parameter on `build_tree` is the
  intended defence — a bypass is a bug).
- **Quadratic-or-worse runtime** on inputs that look benign
  (algorithmic complexity attacks).
- **Memory blowup** from `(path, size)` lists that should be
  rejected.
- **Layout invariant breaks** — overlapping rectangles, children
  outside their parent, negative dimensions on valid input.

**Out of scope:**

- Numerical precision noise within `pytest.approx` tolerance.
- Rendering glitches in downstream renderers (not this library).
- Misuse of the API (passing negative sizes, etc. — those should
  raise; if they silently corrupt layout, that **is** in scope).

## Process

Reports are reviewed on a best-effort basis — no fixed SLA. We aim
for coordinated disclosure within **90 days** of the report,
extendable by mutual agreement if a fix is non-trivial.

Public disclosure is coordinated after the fix is released
(together with the reporter).

## Public disclosure

Once a confirmed fix is released:

- A summary is added to the CHANGELOG under the `### Security`
  category (with the reporter's name if they want credit).
- A GitHub Security Advisory is published.
- If a CVE was assigned, its number is referenced.
