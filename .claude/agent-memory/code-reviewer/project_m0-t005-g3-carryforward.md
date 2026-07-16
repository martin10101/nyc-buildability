---
name: m0-t005-g3-carryforward
description: M0-T005 G3 PASS (2026-07-15) with 7 scanner-hardening defects; what to re-verify at the follow-up fix task and G5
metadata:
  type: project
---

M0-T005 G3 (2026-07-15, branch head a687b21) returned **PASS**. Full report: `project-control/reports/M0-T005-G3-review.md`.

Key facts worth carrying forward:

1. `secret_scan.py` generic regex `\b(?:...|token)\b` cannot match after `_` → `AUTH_TOKEN=/MY_SECRET=/allowed_token=` bypass the catch-all (Defect 1, medium). This is also why the G2 "invisible pragma notice" deviation happened: the `ALLOWLISTED LINE` code path exists and works (lines 147-164) — the fixture line just never produced a hit. The pragma suppression path has never been executed against the real script; the follow-up task must fix the regex AND re-fixture with `token = "<fake>" # secretscan:allow ...` and show the visible notice.
2. Inventory secrets that evade all classes in NAME=value form: GEOCLIENT_SUBSCRIPTION_KEY (hex), VERCEL_TOKEN, SUPABASE_DB_PASSWORD, SUPABASE_DB_URL (postgres URI — `:`/`@` outside generic value charset), RENDER_DEPLOY_HOOK_URL_* (Defect 2, medium; handed to G5).
3. Lesser gaps: basename allowlist matches `.env.example`/`package-lock.json` anywhere (D3); pragma with no justification still exits 0 (D4); `git ls-files` failure exits 1 not 2 (D5); UTF-16 files skipped as binary — PS 5.1 `>` default (D6); >2MB/binary skips silent (D7).
4. actions/checkout tag→SHA verified: v4.2.2 = `11bd71901bbe5b1630ceea73d27597364c9af683`; `08c6903...` = **v5.0.0** — the M0-T004 G5 report example mislabels it; never copy that pin.
5. Full-history secret sweep (all branches) was clean at a687b21.

**Why:** PASS because all six contracted scenarios pass on reproduced evidence; the defects are catch-all hardening gaps, not contract failures.
**How to apply:** when reviewing the scanner follow-up task, the G5 M0-T005 gate, or any future task touching `.github/scripts/secret_scan.py`/`docs/SECRETS_POLICY.md`, verify items 1-3 first and reuse item 4 for any workflow pin review. See [[m0-t006-g3-carryforward]] and [[m0-t004-g3-carryforward]].
