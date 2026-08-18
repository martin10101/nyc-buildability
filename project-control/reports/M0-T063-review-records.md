# M0-T063 Unit A1 — round-1 independent review records

Condensed verdict records by the orchestrator (report-preservation rule): each
captures the reviewer's verdict and every blocking/major finding; the full
verbatim returns are in the session task-notification records. NOT labeled
verbatim. All three reviewers were independent read-only subagents at frozen
HEAD `41f84a4`; producer ≠ verifier. The findings were closed in the rework at
`c45c39e` (see M0-T063-rework-evidence.md) and delta-re-verified.

## G3 code + security review — PASS with required corrections (1 MAJOR blocking)

Scope/forbidden-path gate PASS (13 A1 files; supervisor + code_graph byte-unchanged; imported read-only). Tests 32 passed/1 skipped; modularity 0 failures.

- **MAJOR-1 (BLOCKING) — tracked-only fingerprint vs generator all-eligible.** `compute_fingerprint` classified an untracked eligible file as excluded and never hashed its content, but `code_graph.build_graph` (which the baseline calls) indexes ALL filesystem-eligible files. Reproduced: two different untracked contents → SAME snapshot_fingerprint but DIFFERENT code-graph export → a stale index would be served when A2 keys on the fingerprint. Required fix: hash all eligible files so the fingerprint uniquely determines the generator output. **CLOSED at c45c39e.**
- MINOR-2 (non-blocking) — recover() quarantines a live writer's in-progress temp dir (fails closed, but spurious write-abort under read/write concurrency). Fix: skip live-pid temp dirs. **CLOSED.**
- MINOR-3 (non-blocking) — lock-reclaim TOCTOU + _set_current outside lock (single-writer intent; low risk). Noted for hardening.
- MINOR-4 — FAILED_SYMLINK_LOOP/FAILED_UNREADABLE only covered by the symlink test (skips on Windows; runs on CI ubuntu); reviewer forced both branches manually — classify + reconcile correctly.
- MINOR-5 — evidence-map producer field / reviewed_sha placeholder (orchestrator to reconcile).

Confirmations PASS: determinism (no wall-clock in any digest; domain_hash length-framed collision-safe); mtime-never-proof real; census reconciles in every adversarial case; cache crash-safety core contract holds (load_current runs recover then validates; never serves half/corrupt/nonexistent; validate-before-os.replace; retry idempotent; stale dead-pid lock reclaimed, live refused); outside-repo guarantee; evidence redacted (only sha256 digests, no secrets/paths/emails); subprocess argv-list, no shell=True.

## G4 QA review — FAIL (1 blocking; all functional contracts pass)

Documented commands all green (32/1). AS-1..AS-5 independently reproduced in own fixtures (all contracts hold). Boundary QA (empty/only-excluded/CRLF-vs-LF) PASS. Modularity + <600 SLOC PASS. Forbidden-path/unmodified-generator PASS.

- **F1 (BLOCKING) — committed baseline evidence does not reproduce at HEAD.** Committed export_digest `0f93…4282` / nodes 8324 / edges 3382 / files 422, but a clean rebuild at HEAD yields `1879…f705` / 8414 / 3419 / 426. Root cause (not a harness bug): the evidence was committed at `d9881e4` (422-file corpus); the subsequent merge `a54dc34` from origin/main added 4 code-graph-eligible tools/*.py files (M0-T073/T074), growing the corpus 422→426, so every content-derived value shifted. The baseline is the frozen byte-level REFERENCE AS-4 / the A2 parity invariant compare against — stale on day one. Remedy: regenerate + recommit at the final identity. **CLOSED at c45c39e** (regenerated: `3d64d3b…` / 8418 / 3420 / 426; reproduces at HEAD).
- Minor — reviewed_sha placeholder; source_fingerprint naming clarification (input-corpus fingerprint, not generator-code identity). **CLOSED** (doc note added).

## DCV directive-compliance verification — PASS (46/46)

Every applicable D-013 row (R001..R082 subset, 46 rows) re-derived PASS at 41f84a4. The R037/R079 judgment call independently confirmed CORRECT against source-002-amendment.md: decisions 2/4/6 place the incremental build + the byte-identical parity TEST in A2; A1 delivers the deterministic REFERENCE + determinism (no false completion claim; evidence map explicitly defers the test to A2). **Outstanding A2 obligation:** the enforced byte-identical incremental-vs-full test is a hard deliverable of M0-T064 (built and passing in the A2 worktree). Findings: reviewed_sha placeholder must be stamped at submit (CLOSED at acceptance); D-001 process otherwise clean (regime stamp + refs; no directives/** changes; validator exit 0; forbidden paths untouched).
