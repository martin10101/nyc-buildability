# G3 DELTA ATTESTATION — M4-T012 rework (dd7c8b74 -> 8538c272, attested at HEAD b3e66078)

> Orchestrator note: reviewer return saved VERBATIM from the agent-return channel
> (transport entity-decoding only). Reviewer: code-reviewer (same reviewer as the
> original G3 report, project-control/reports/M4-T012-G3-rule-content-review.md).
> Recorded by the orchestrator per ADR-005.

Delta verified. My independent reruns at the new head reproduce the orchestrator's evidence, and the scoped diff confirms the delta is exactly the three described changes with nothing else touched in M4-T012's material dirs.

What I checked:
- Anchor: primary-checkout HEAD is now `b3e66078` (material `8538c272`); I ran no state-changing git command.
- Scoped `git diff dd7c8b74..8538c272` over the three files matches the description; a `--stat` over all M4-T012 material dirs (`rulesets`, `_zr_snapshots`, `docs/research/zr-snapshots`, `tests/rules`) shows ONLY two files changed — the suffix-variants rule (1-line gloss) and the test file. No snapshot, no other ruleset, no engine/evaluator/schema.
- Suffix-variants rule: the `zr-23-21` citation gloss now reads exactly my A2 wording ("R2X occupies its own 23-21 row at standard FAR 1.00, distinct from the R2/R2A row at 0.75 and from the R4 row"), which is accurate against the cited `zr-23-21` snapshot. `content_digest_sha256` unchanged (`b52771…`); no value, applicability, computation, or output changed. The digest guard binds the snapshot's `verbatim_excerpt`, not the citation-quote string, so `test_as2` remains valid.
- Test file: the 6 lint wraps + removal of one unused `rule` local (no assertion/logic touched), plus ADVISORY-1 (the (g) rule added to both AS-3 effective-date parametrize lists, +2) and ADVISORY-2 (two new NC-1 foreign-district in_set pins for the QRS and (g) rules, +8). Every change is cosmetic or additive; no existing assertion weakened.
- Questions doc: the A1 TOOLING NOTE now carries a dated CORRECTION stating the raw HTML bytes DO contain (g) (sha `fc51ec09…`, pointer to the source-capture report; extraction-layer artifact) while explicitly affirming the print/PDF pipeline rule STANDS — exactly my A1 follow-up, honestly framed.
- Independent reruns at the new head: new pack `110 passed`; full rules suite `568 passed`; `modularity EXIT: 0`; `sync_zr_snapshots --check OK 14`.

My two content-bearing advisories from the original report (A2 citation gloss, A1 questions-doc correction) are now RESOLVED with my exact wording/intent. A3 (parameter-note "pending raw-HTML verification" language) and A4 (bare-R1 (g) G6-agenda note) remain non-blocking observations, unchanged. Nothing in the delta concerns me; the M4-T015 connector material is disjoint and did not touch any M4-T012 file.

G3 DELTA ATTESTATION: PASS stands — verified the actual `dd7c8b74..8538c272` diff (only the suffix-variants citation gloss + additive/lint test edits + the questions-doc A1 correction; digests, values, applicability, and all snapshots unchanged), reran independently (rules 110/568 passed, modularity EXIT 0, sync OK 14); my A1/A2 items were applied with my wording and are now resolved, the NC/effective-date additions only strengthen coverage, and no new content-bearing risk was introduced.
