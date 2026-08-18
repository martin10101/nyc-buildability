# M0-T072 directive-compliance verification — condensed verdict record (round 1)

CONDENSED transcription by the orchestrator (report-preservation rule): captures
the verifier's per-requirement verdicts; the full verbatim return is in the
session task-notification record. NOT labeled verbatim. Verifier: independent
directive-compliance-verifier subagent, read-only, at frozen `ec8bc58`.
Producer ≠ verifier. The one FAIL (R052) is closed at `be3a599`; a final DCV pass
re-verifies every row at the accepted head before acceptance.

## Applicable rows: D-017-R037..R053 (17). Overall round-1 verdict: FAIL (on R052 only)

16 of 17 rows PASS at `ec8bc58`, each re-derived from primary evidence (not the
producer's map): R037 (7 source facts confirmed at base), R038 (next unused ID
M0-T072; AD-093 evidence in packet + commit), R039-R041 (config.toml logical
binding, no path leak, record-manifest), R042-R044 (doctor/verify-controller/start
bind the external config; provider-contact gated before verification), R045 (four
fail-closed classes), R046 (model_selection excluded), R047 (test-only flows
retained), R048 (in-package duplicate refused), R049 (no symlink/hardlink), R050
(protected config byte-identical `6aef12a9…`, no write path), R051 (nine proofs
each have a passing test), R053 (runbook validated against argparse, no carets).

**R052 — FAIL at ec8bc58, CLOSED at be3a599.** The full battery showed
`14 failed, 1826 passed, 2 skipped`; the claimed "1813 passed, 0 failures" was a
run of a checkout WITHOUT the new test module (the ctl17 tree). The 14 failures
were the four fixture modules asserting the pre-repair contract. At `be3a599`
those fixtures are updated to the new fail-closed contract and the battery is
**1845 passed, 2 skipped, 0 failures** — freeze baseline re-established.

**D-001 process:** regime stamp + refs present; producer report/evidence-map/
reviewed-sha present; G0/G2 recorded; no `project-control/directives/` changes;
registry validator OK (17 active, producer≠verifier); forbidden paths untouched.
Round-1 process finding (gate records uncommitted at the frozen head) is closed —
the orchestrator committed the CLI-written gate records (`98267d3`).
