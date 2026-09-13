# G4 DELTA ATTESTATION — M4-T014 at 346f8535

> Preservation note: saved VERBATIM by the orchestrator from the same G4 reviewer's agent-return
> channel (transport entity-decoding only). Companion to M4-T014-G4-integration-review.md.

## VERDICT: G4 PASS STANDS at 346f8535

The G3-mandated (g)-provenance correction (rework round 1, commit `346f8535`) does not disturb any basis of my prior G4 PASS at `c8d94f38`. All four attestation points verified independently, read-only.

**(a) Canonical/bundle byte-identity holds at the new bytes — CONFIRMED.**
Both copies of `zr-23-421-r3-r4.snapshot.json` carry blob `4edbea4cb4c619bcc59b7a81bd1de6337580f7ee` at `346f8535` (`git ls-tree`): `services/api/app/_zr_snapshots/v1/` == `docs/research/zr-snapshots/v1/`. Identical blob = byte-identical.

**(b) `verbatim_excerpt` and `content_digest_sha256` unchanged; all citation digests still bind — CONFIRMED.**
Loading old (`c8d94f38`) vs new (`346f8535`) JSON:
- `verbatim_excerpt` byte-identical old==new: **True**
- `content_digest_sha256` field unchanged: **`68e4d147a351188ce0df06d8609b1c3766c76776e0a87482e04ac2cc9459e046`** (old == new)
- recomputed `sha256(new.verbatim_excerpt)` == stored == `68e4d147…`: **True** — the digest still genuinely binds the excerpt, so the three rulesets' `citations[].content_digest_sha256` references and the DSL fail-closed load check (`records … but the snapshot on disk stores …`) all still hold.
- Only differing top-level key: **`notes`**. `source` and `district_enumeration` blocks unchanged.

**(c) Rules suite still passes at the new tree — CONFIRMED (independently reproduced).**
Patched my isolated scratch tree with the `346f8535` snapshot bytes in both locations, then:
- `PYTHONPATH=. python -m pytest tests/rules -q` → **458 passed**
- `python scripts/sync_zr_snapshots.py --check` → **EXIT 0**, "byte-identical to the canonical source (10 file(s))"
Matches the orchestrator's post-edit reproduction exactly.

**(d) Nothing in the delta touches the other five PASS items — CONFIRMED.**
`git diff --stat c8d94f38..346f8535 -- services/api docs/research/zr-snapshots` = only the two `zr-23-421-r3-r4.snapshot.json` copies (4 ins / 4 del = the two rewritten `notes` entries per copy). No rule file, no `test_r3_r4_height.py` change, no engine/evaluator, no schema, no other snapshot. Mapping to my items:
- **Item 1 (regression / engine untouched):** only a data `notes` edit; engine/evaluator/tests still untouched. STANDS.
- **Item 2 (suite integrity, 90 cases):** test file unchanged; 458 reproduced. STANDS.
- **Item 3 (S1–S6):** rule values, coverage logic, and `test_as2` provenance checks (quote/section/last_amended/digest — none in `notes`) unchanged; 458 pass. STANDS.
- **Item 4 (snapshot integrity):** the item most implicated — and it is strengthened: canonical==bundle byte-identity holds, digest binds, sync = 10 files. The corrected notes now accurately attribute the 23-421(g) / 5-ft / 9,500-sqft content to owner-verified external sources rather than asserting it as HTML-capture content. STANDS.
- **Item 5 (determinism/flake):** a notes edit adds no network/time/randomness. STANDS.
- **Item 6 (CI evidence):** source rules-behavior proven identical; a fresh CI run at the delta head is the orchestrator's to capture. Source-level regression basis unchanged.

The remaining delta files (`producer-report.md`, `source-capture.md`, `docs/ARCHITECT_REVIEW_QUESTIONS.md`, and the control-plane gates/reports/directives/tasks/state) are documentation and control-plane records aligned with the G3 correction — outside my regression/integration scope and non-load-bearing for this attestation.

## Requested action
Record that G4 = PASS for M4-T014 continues to hold at material identity `346f8535`. No residuals; no rework owed on the integration/regression gate.
