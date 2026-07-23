# M4-T006 — G2 self-check (orchestrator-recorded)

**Gate:** G2 (self_check — never satisfies an independent gate; G3/G4/G5 remain required).
**Task:** M4-T006 — R5 height & setback draft rule family. **Frozen SHA:** `6509db3`.
**Result:** PASS (self-check + orchestrator independent re-validation).

## Producer self-check (from M4-T006-producer-report.md) + orchestrator re-run on the task branch @ 6509db3
- `python -m ruff check .` (services/api) → **All checks passed!**
- `python -m pytest tests/rules/test_r5_height_setback.py -q` → **45 passed** (AS-1..AS-6 + NC-1..NC-7)
- `python -m pytest tests/rules/test_zr_snapshot_bundle.py tests/rules/test_installed_deployability.py -q` → **8 passed**
- `python scripts/sync_zr_snapshots.py --check` → **byte-identical (6 files)**
- `python -m pytest -q` (full API) → **926 passed** (881 baseline + 45 new; no regression)

## Scope / integrity (orchestrator-verified)
- Content integrated onto the task branch is exactly the allowed paths: 6 rulesets (`residential_height_setback`), 5 ZR snapshots (canonical `docs/research/zr-snapshots/v1/` + byte-identical synced bundle), `test_r5_height_setback.py`, and the M4-T006 reports. **No `.claude/agent-memory` rode the product branch.**
- Forbidden paths byte-unchanged vs `c5e8cd0`: `r5_residential_far.rule.json`, `evaluator.py`, `integration.py`, `app/scenario/**`, `app/api/**`, `apps/web/**`, and canonical contracts (`property_profile`/`rule_evaluation`/`coverage_status`) — empty diff.
- Every rule `status: needs_review`, verified-ineligible, `effective_from 2024-12-05`; per-district separate files; fail-closed on unavailable inputs; §23-424 vs base → `rule_conflict`.

## Disclosed (needs_review / G6 items — not blockers, forwarded to reviewers)
1. Snapshots carry honest `raw_html_verified:false`; some values `extraction_status: extracted_draft` pending byte-level raw-HTML verbatim confirmation (a G6/verification item).
2. §23-42/426/44/425 override contexts implemented as PRR exceptions with `citation_ref:null` (verbatim capture is a follow-up).
3. Local `pip install --no-deps .` blocked by local Python 3.11 (< requires-python 3.12); wheel resolution proven by package-data guard tests; the literal install runs in the PR #88 CI `exact-production-install` (3.12) job.

Self-check PASS. G3 (code), G4 (integration/regression + CI deployability), G5 (security) dispatched independently at `6509db3`. **G6 qualified-human legal approval remains required before any publication/verification/acceptance — not weakened; independent of B-010.**
