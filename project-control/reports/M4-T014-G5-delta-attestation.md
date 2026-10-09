# G5 DELTA ATTESTATION — M4-T014 @ 346f8535

> Preservation note: saved VERBATIM by the orchestrator from the same G5 reviewer's agent-return
> channel (transport entity-decoding only). Companion to M4-T014-G5-security-review.md.

## G5 PASS STANDS at 346f8535. No new residuals. (Prior low advisory A1 unchanged, non-blocking.)

The G3-mandated provenance correction is a **notes-only** change to `zr-23-421-r3-r4.snapshot.json` (canonical + bundle) plus report edits. It does not touch any hashed content, ruleset, schema, engine, test, or dependency. It **strengthens** integrity/honesty (areas 2 and 4) and weakens none of the six PASS areas.

### Delta scope (c8d94f38..346f8535), security-relevant material
- `docs/research/zr-snapshots/v1/zr-23-421-r3-r4.snapshot.json` — `notes[1]` and `notes[2]` only (4 lines)
- `services/api/app/_zr_snapshots/v1/zr-23-421-r3-r4.snapshot.json` — identical notes change (same blob)
- `project-control/reports/M4-T014-source-capture.md` — report honesty edit (drops pseudo-verbatim quote marks)
- Remainder: `docs/ARCHITECT_REVIEW_QUESTIONS.md` (owner/peer research, owner-verified 2026-09-13; not this task's material) + control-plane (directives/gates/reports/state/tasks). **No** rulesets, schemas, engine, tests, deps, lockfiles, tools, or CI workflows changed.

### (a) Hashed content + digest UNCHANGED — VERIFIED
- Recomputed at 346f8535: `sha256(verbatim_excerpt)` = `68e4d147a351188ce0df06d8609b1c3766c76776e0a87482e04ac2cc9459e046` = stored `content_digest_sha256`. `verbatim_excerpt` still opens `R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A R5A`.
- Rulesets/schemas/tests untouched in the delta (`git diff --stat` empty for those paths), so every ruleset citation digest still matches: pitched cites `68e4d147…` (unchanged verbatim) + `3fea…` (zr-23-42, untouched); flat cites `0268…` + `3fea…`; R4B cites `0268…` (both untouched). All still MATCH.

### (b) Canonical/bundle byte-identity HOLDS — VERIFIED
Both files resolve to the identical git blob `4edbea4cb4c619bcc59b7a81bd1de6337580f7ee` at 346f8535. (The `test_zr_snapshot_bundle` guard / `sync --check` invariant is preserved.)

### (c) No executable/HTML hazard, no secret/PII in the new note text — VERIFIED
Scan of the changed `notes` field at 346f8535: HTML tags `<..>` = NONE (the `<=80-degree` fragment has no closing `>` and is not a tag); URLs = NONE; secret patterns = NONE; control chars = NONE. The added text (HTML-channel (g) blind-spot disclosure; source attributions to agent memory + `docs/ARCHITECT_REVIEW_QUESTIONS.md`; the owner-verified (g) trigger figures 9,500 sq ft / 100 ft width / 5% slope / 5 ft) is inert JSON metadata in a field the engine never hashes and never parses as HTML. The referenced repo paths are internal, not secrets. Zoning figures are public-law provisions, not PII.

### (d) Six PASS areas — none weakened; two strengthened — VERIFIED
1. Supply chain: no dependency/tool/CI change in delta — UNCHANGED PASS.
2. Snapshot provenance integrity: **STRENGTHENED** — hashed content/digest and byte-identity preserved, and the notes now honestly bound what THIS capture did vs did not read.
3. Injection/eval: no ruleset/schema/engine change; notes are non-executable data — UNCHANGED PASS.
4. Honesty/legal-safety: **STRENGTHENED** — removes the prior implicit over-claim that the apex-point/`<=80°`/(a)–(g) detail was read from this HTML capture; now explicitly "NOT read by THIS capture … owner-verified-elsewhere … full-text (print/PDF) proof still owed before G6." Still needs_review DRAFT; sloping-plane setback still an A2 `documented_limitation`, never numeric.
5. Secrets/PII: scan clean — UNCHANGED PASS.
6. Scope: the material notes change is within allowed_paths (`services/api/app/_zr_snapshots`, `docs/research/zr-snapshots`) + the source-capture report (allowed). `docs/ARCHITECT_REVIEW_QUESTIONS.md` is owner-owned research outside this task's material scope, not a producer scope violation — UNCHANGED PASS.

### CI/behavior note
The changed `notes` field is non-executable, non-hashed metadata; no test in `test_r3_r4_height.py` asserts on notes, and the digest guard is over `verbatim_excerpt` (unchanged). The 18/18-green executable behavior (rules suite outcome) is invariant to this change; the CI evidence re-stamp in the delta is consistent with that.

### Residuals
None new. The only carried item is the pre-existing **low advisory A1** (the honesty-guard test bans the space-form `"buildable envelope"` while rulesets use the negated hyphenated `"buildable-envelope"`) — test-robustness only, content safe, routed to qa/code reviewers; unchanged by this delta and non-blocking for G5.

**G5 PASS STANDS at 346f8535.** Orchestrator records the gate.
