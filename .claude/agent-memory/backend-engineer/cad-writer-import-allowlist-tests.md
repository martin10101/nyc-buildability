---
name: cad-writer-import-allowlist-tests
description: app/cad writer modules have AST import-allowlist/stdlib-only tests that fail closed when you add ANY intra-repo import; how to keep compatibility aliases past ruff F401
metadata:
  type: feedback
---

Adding an intra-repo import to an `app/cad` writer trips its own AST guard tests
unless you also update the test. These tests fail closed by design.

**Why:** the CAD writers were built "zero new dependency / stdlib only" and each
pins its import surface with an AST scan.

**How to apply (verified M5-T102, seq 129):**
- `tests/cad/test_dxf_writer.py::test_as4_module_import_allowlist` reads
  `dxf_writer.py` and asserts imports == `IMPORT_ALLOWLIST` in BOTH directions
  (non-vacuity), so a new import must be ADDED to `IMPORT_ALLOWLIST`
  (e.g. `app.cad.claim_words`). It also now flags `__import__(...)`/`importlib`
  (M5-T096 G4 A1 / DB-067 a).
- `tests/cad/test_glb_writer.py` stdlib test collects top-level roots; an
  `app.*` import adds root `"app"` — add it to the expected set.
- A compatibility RE-EXPORT (e.g. keep `dxf_writer.CLAIM_CLASS_WORDS` importable
  after moving the literal) is unused-in-module, so ruff F401 flags it. Use the
  explicit `from x import Y as Y` idiom OR add `Y` to `__all__` — both mark it a
  deliberate re-export. `python -m ruff check .` from `services/api` is the api CI
  job's first step; catch this locally.
- Refactoring only the claim/refusal SCREEN of a writer does NOT move its golden
  bytes or the `docs/samples/cad/` owner samples (valid output is unaffected;
  only refusal behaviour changes). `test_cad_owner_samples.py` +
  `tests/drawings/test_dxf_roundtrip.py` are READ-ONLY consumers that must stay
  green unchanged. Related: [[socrata-pluto-gotchas]].
