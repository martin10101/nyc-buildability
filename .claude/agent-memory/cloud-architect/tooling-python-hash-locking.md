---
name: tooling-python-hash-locking
description: Reusable pip/uv facts for hash-pinned Python locks in services/api — the --require-hashes single-package gotcha, uv universal-lock determinism, PyPI Date-header UTC clock, and the local-3.11-vs-app-3.12 test workaround
metadata:
  type: feedback
---

Stable pip/uv techniques for the repo's Python supply-chain locks (services/api). Held across M0-T018 and M0-T020. (CRLF byte-identity is covered separately in [[tooling-lock-byte-identity-crlf]]; live age+advisory verification in [[reference-dependency-policy-verification]].)

**pip `--require-hashes` rejects `-r <lock> <bare-package>`.** `pip install --require-hashes -r requirements-tools.lock uv` fails — pip treats the bare `uv` as an *unpinned* requirement ("all requirements must have their versions pinned with =="). A `-c <lock>` constraints file does NOT supply hashes for named requirements either. To install just ONE tool from a hash-pinned lock, install the WHOLE lock (`pip install --require-hashes -r <lock>`); it is hash-verified and puts the console script (`uv`, `pytest`, `pip-audit`) on PATH. Do NOT create a separate hash-pinned subset just to install one tool — that duplicates an authoritative pin list (packets forbid it).
- **Why:** M0-T020 needed uv-from-lock (api-lock-verify), pyyaml-from-lock (contracts), pytest-from-lock (contracts-typegen); every single-package form failed require-hashes, so each installs the full tooling lock.
- **How to apply:** any CI step needing one locked tool → install the full `requirements-tools.lock`; extra packages are inert for stdlib-only/py-only steps.

**uv universal lock is byte-deterministic → a lock has a fixed sha256.** `uv pip compile --universal --python-version 3.12 --generate-hashes --no-header <in> -o <lock>` yields identical bytes across OS/interpreter and repeated runs (production lock `a75dc743…`/67325B; tooling lock `803e90f9…`/35229B). The `--check` scripts depend on this. Pin the uv version (0.11.28) — resolver output drifts across uv releases, and a too-new uv itself fails the 7-day age gate (0.11.29 was 5d old).

**Authoritative "now" for the age gate = PyPI `Date` response header**, not the local clock. `dependency_age_gate.py` HEADs a stable PyPI JSON URL and parses `Date` (RFC 2822)→UTC; age uses the newest upload among the lock-admitted sha256 artifacts (blocks an old version number with a freshly re-uploaded artifact). Exactly 604800s PASSES, 604799 FAILS.

**Local PC is Python 3.11; services/api declares `requires-python>=3.12`.** `pip install ./services/api` fails locally. To do pytest/collection work: install the runtime deps (fastapi/uvicorn/jsonschema/shapely have 3.11 wheels) + pytest, then run `PYTHONPATH=services/api pytest` (the app package need not be installed to collect/run `tests/`). Note `[tool.pytest.ini_options] testpaths=["tests"]` means bare `pytest` skips `scripts/tests` — run those explicitly. Full-suite proof on 3.12 is CI-authoritative; always say so in the report.
