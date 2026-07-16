---
name: m0-t005-g3-carryforward
description: M0-T005 G3 PASS + M0-T005-R1 G3 PASS (2026-07-16); D1-D7/F1 all closed; residual R1-D1..D5 (placeholder-hint charset interaction) to recheck at G5/next hardening
metadata:
  type: project
---

M0-T005 G3 (2026-07-15) PASS with defects D1-D7; **M0-T005-R1 G3 (2026-07-16, commit 1caa972) PASS — all 11 rework items verified fixed by live re-execution.** Full report: `project-control/reports/M0-T005-R1-G3-review.md`.

Still-relevant carry-forward:

1. **Closed at R1 (do not re-flag):** compound-name regex, inventory-name class, postgres-URI class, exact-path allowlist + template content scan, empty-pragma exit 1, UTF-16 BOM decode, emit()/sanitize_for_log in BOTH .github/scripts, exit-2 for git failures, SKIPPED notices, RefResolver fail-closed guard (verified under real jsonschema 4.10.3 — CI-live version).
2. **Open residuals (recheck at G5 M0-T005-R1 and any scanner touch):** R1-D1 placeholder hints `$`/`<`/`{` suppress real secrets in inventory/postgres classes (charsets allow them, unlike generic — `SUPABASE_DB_PASSWORD=Xk9q$...` → no finding); R1-D2 `NAME = value` with spaces evades inventory (Python-config style); R1-D3 `user:pass` hint suppresses `produser:passXXX@` URIs; R1-D5 policy §5 first bullet still says "basename path allowlist" — orchestrator doc touch-up owed.
3. **Review technique that worked:** for exact-path-keyed checks, test end-to-end in a throwaway local clone (`git clone file://<worktree>` ≈ 2.2 MB) instead of transiently editing forbidden paths (producer's S4b shortcut — adjudicated acceptable-once, not to repeat). For forcing the jsonschema legacy path, a temp venv with `jsonschema==4.10.3` (~15 MB) is the honest test; poisoning `sys.modules['referencing']` under 4.26 kills jsonschema entirely (tests degraded mode instead). Windows note: `shutil.rmtree` on a clone needs an onerror chmod for read-only .git objects.
4. actions/checkout tag→SHA: v4.2.2 = `11bd71901bbe5b1630ceea73d27597364c9af683`; `08c6903...` = **v5.0.0** (M0-T004 G5 report example mislabels it; never copy that pin).

**Why:** R1 PASS because every packet item reproduced fixed with reviewer-owned fixtures; residuals are strictly narrower than the closed defects and share the accepted compensating-control rationale (push protection, no real credentials yet).
**How to apply:** at the M0-T005-R1 G5 gate or any future edit to `.github/scripts/secret_scan.py`/`validate_contracts.py`/`docs/SECRETS_POLICY.md`, check item 2 residuals first; reuse item 3 techniques; item 4 for workflow pins. See [[m0-t009-g3-carryforward]].
