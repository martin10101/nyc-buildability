---
name: m0-t018-g3-carryforward
description: M0-T018 dependency-parity G3+G4 PASS @7ffd542; uv-lock parity facts, DP-S4 negative-proof technique, requirements.in header-tool mislabel LOW to recheck at M0-T019 policy landing
metadata:
  type: project
---

M0-T018 (backend production dependency parity + Python supply-chain enforcement) PASSED G3+G4, merged main @7ffd542 (PR #55). Verified independently 2026-07-20, not from producer conclusions.

**Why:** P0 owner directive 2026-07-20 — Render prod install silently omitted runtime `jsonschema` (lazy import at app/profile/contract.py:231 inside `_validator()`), and starlette==0.46.2 carried 9 advisories. Must land before M0-T019 / M2-T013 / M2-T014.

**How to apply:**
- requirements.txt is now a GENERATED uv universal hash-pinned lock (851 lines, 27 pkgs, 774 hash lines) sourced from requirements.in. Do NOT hand-edit requirements.txt — the `api-lock-verify` CI job (`bash scripts/lock_requirements.sh --check`, pinned uv==0.11.29) fails on drift. Edit requirements.in, regenerate.
- Render buildCommand stays `pip install -r requirements.txt` (unchanged). CI `exact-production-install` uses `pip install --require-hashes -r requirements.txt` — the extra flag is a documented equivalence (pip auto-enters hash mode when any line is hashed), NOT a divergence.
- DP-S4 negative-proof technique (reusable): to prove a lazy-import smoke actually exercises the runtime dep, verify the negative script (a) exits 0 when the dep is absent AND validate fails as expected, and (b) exits 1 when the dep IS present (proves not a no-op). I validated both branches locally by blocking jsonschema via a sys.meta_path finder (no env mutation on thin client). CI does real `pip uninstall -y jsonschema` between positive and restore steps.
- 538 tests collected on this checkout (exactly meets >=538). pytest count is parametrize-expanded from 435 base `def test_` funcs.
- shapely stays 2.0.7 (GEOS 3.11.4 digest pin, M2-T009) — do not bump.

**LOW residual (recheck at M0-T019 DEPENDENCY_SECURITY_POLICY landing):** requirements.in header comment (lines 9, 11) still says the lock is produced by `pip-compile`/`pip-tools`, but the actual generator (lock_requirements.sh) and CI use `uv pip compile`. Producer report §6 admits uv was chosen over pip-tools; the requirements.in header just wasn't updated to match. Cosmetic/provenance-doc only — the real generator is correct and CI-enforced. Non-blocking.

**OBSERVATION residuals:** (1) `--require-hashes` in CI vs plain in render.yaml is intentional equivalence, documented in render.yaml:92-96. (2) producer flagged services/api/*.egg-info not gitignored (.gitignore outside this task scope) — follow-up recommended. (3) age pins websockets==16.1 / numpy==2.4.6 will need deliberate refresh once successors clear 7-day window.
