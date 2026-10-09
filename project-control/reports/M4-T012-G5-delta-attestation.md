# G5 DELTA ATTESTATION — M4-T012 rework (dd7c8b74 -> 8538c272, attested at HEAD b3e66078)

> Orchestrator note: reviewer return saved VERBATIM from the agent-return channel
> (transport entity-decoding only). Reviewer: security-reviewer (same reviewer as the
> original G5 report, project-control/reports/M4-T012-G5-security-review.md).
> Recorded by the orchestrator per ADR-005.

Verified the actual delta at frozen head `b3e66078` (material `8538c272`). All five G5 concerns hold.

**Delta scope (M4-T012):** exactly 3 modified files — `test_r1_r2_height_setback.py`, `r1_r2_suffix_variants_pitched_height.rule.json`, `docs/ARCHITECT_REVIEW_QUESTIONS.md`. The 34-file M4-T015 connector material in the same push is disjoint and excluded from this attestation.

**§G zero-deps:** no `requirements*/pyproject/package.json/lockfile` anywhere in `dd7c8b74..8538c272`. PASS.

**Scope containment:** test file + ruleset are inside `allowed_paths`. `docs/ARCHITECT_REVIEW_QUESTIONS.md` is NOT in the listed allowed_paths but is NOT forbidden (the forbidden entry is the different `docs/MVP_ARCHITECT_REVIEW_QA.md`), is named in packet R005 as the home of the open professional ask, and per the ledger (progress-log 07:32) was edited by the **orchestrator as a Tier A rework correction**, not by the sandboxed producer — the same integration-correction pattern as the accepted pre-submit `allowed_paths += docs/research/zr-snapshots`. No forbidden path touched. ADVISORY (non-blocking): the write-scope list was not formally extended to that doc; the orchestrator may want to record it in the ledger as it did for the snapshots dir.

**No secrets / network / injection:** test-file delta (59 ins / 6 del) adds no imports, no network/subprocess/eval/exec. The ruleset and doc edits are text-only. The doc's `fc51ec09…`/`b5777618…` are sha256 digests (provenance), not secrets. Both reworked deliverable files are pure ASCII. PASS.

**Snapshot integrity:** 0 files changed under `_zr_snapshots` or `docs/research/zr-snapshots` (snapshots untouched, confirming the orchestrator's "sync OK 14"). The suffix-variants reword touched only the human-readable citation **quote gloss** (R2X FAR wording) — the hashed `verbatim_excerpt` and the cited `zr-23-21` digest `b52771e6…` are unchanged, and that snapshot file is untouched, so the hash guard remains intact. PASS.

**Draft posture unaffected:** ruleset still `status: needs_review`; values unchanged (25/35); applicability unchanged (R1-1, R1-2, R1-2A, R2A, R2X); the doc CORRECTION is a dated tooling-note reconciliation of the disclosed HTML-vs-PDF discrepancy — it does not close the professional ask, add a legal answer, or declare compliance. PASS.

G5 DELTA ATTESTATION: PASS stands — the M4-T012 delta is 3 files (2 in-scope; the ARCHITECT_REVIEW_QUESTIONS.md tooling-note correction is orchestrator Tier A rework on a non-forbidden, R005-named doc); zero dependency changes; no secrets/network/injection surface; snapshots and their hash-guarded digests untouched (reword hit only a citation gloss); every rule remains needs_review with unchanged values. One new non-blocking ADVISORY only (formalize the questions-doc in the write-scope ledger).
