# M0-T106 G2 self-check (producer = fable-orchestrator-session)

Recorded 2026-08-27 UTC at the deliverable identity (the commit citing D-024-R152/R174 this
report lands beside). Machine: installed claude 2.1.247 (measured at use), local Python 3.11.9
(CI 3.12 — no 3.12-only syntax; no PEP 695). Session runs under D-031 (owner extension to ~750k
context then handoff).

## 1. Test evidence at the frozen identity

| Pack | Result |
|---|---|
| Goal pack `tools/test_agent_supervisor_goal_integration.py` | **31 passed** (S1–S11 all mapped; every row deterministic — the S11 docs fetch ran at build time and is frozen in the fixture) |
| Unit-D event-bus pack (re-run: `publish_typed` is additive to it) | **38 passed** (no regression; 69 combined) |
| Targeted regression slice (goal + event-bus + telemetry core + subagent telemetry + native adapter + bounded contracts) | **278 passed, 0 failed** (8.4s) |
| Whole-tree collection (`--collect-only`, minus `test_directive_compliance.py`) | **2,720 tests collected, zero import/collection errors** |
| Full freeze suite locally | **NOT COMPLETED LOCALLY — disclosed:** two background full-suite runs were externally stopped mid-run (~40% with zero failures at the stop; not stopped by the producer); rather than relaunch a third time against an operator stop signal, the evidence rests on (a) the targeted slice covering every touched/neighboring module, (b) clean whole-tree collection, (c) the deliverable being new-files-plus-one-additive-method (the modified file's own 38-test pack green), and (d) the full suite running on CI at the pushed head — the same structurally-sound reasoning G4 accepted at M0-T105. Reviewers may run the full suite themselves. |
| `validate_directive_compliance.py --check` standalone | ran EXIT=0 earlier this session at the D-031 capture; re-run recorded at submit if the registry changed since (it did not — no registry file in this deliverable) |
| Readonly-guard self-runner packs | **ALL CHECKS PASSED** ×2; `.claude/hooks/` diff empty (forbidden path respected) |
| Mutation self-check (9 hand-applied mutants across all three new modules + the bus addition) | **9/9 killed**; packs GREEN after restoration; `__pycache__` cleared post-mutation (the M0-T105 stale-bytecode lesson applied) |

## 2. Static checks

- `ruff check` (0.13.0, the CI version) on all five changed Python files: **clean**; whole-tree
  findings unchanged (pre-existing files only, untouched here).
- `python tools/modularity_check.py --check`: **0 failures**; largest new file 240 lines.
- No-leak scan (username, user paths, key shapes, email, full UUIDs) over every new path:
  **CLEAN** except the precedented benign class — the leak-needle assertion string inside the
  test pack itself (M0-T104/T105 precedent).

## 3. Packet-obligation walk (self-audit)

One cohesive task at a time ✓ (S1: structural one-task binding + foreign-ledger-task refusal +
campaign-scale tripwires, all mutation-proven); measurable completion condition generated from
packet fields with the documented shape (end state / stated check / constraints) ✓ (S1); safe
completion condition = EXPLICIT turn bound required, enforced even on hand-built objects ✓ (S1
direct-construction test); condition ceiling 4,000 chars ✓; no worker-visible token pressure —
R045 via the REUSED `assert_worker_text_clean` on the full composed text, fail closed ✓ (S2,
mutation-proven); condition-met / impossible / not-yet-met verdicts normalized with honest
unknown ✓ (S3); the FOUR unrecoverable clearing classes classified from the documented warning
frame, incl. the host-managed-credentials stays-active nuance; transient failures stay active ✓
(S4, mutation-proven both ways); no-progress = STRUCTURAL classification with the goal still set
(undocumented warning text is never parsed) ✓ (S5); resume = counters reset, achieved/cleared
never restored, all-routes gate ≥2.1.239 with honest pre-2.1.239 picker exclusion and unknown on
unparseable versions ✓ (S6); background check-ins: documented cadence math (doubling capped 4×),
env scaling, 0-disables, malformed-env fails visible, version gates ≥2.1.234/≥2.1.236/cap-3
≥2.1.246 ✓ (S7); check-ins ingested into the DURABLE journal via the reused unit-D bus,
dedup-keyed, duplicate = counted no-op, outside Fable context ✓ (S8 — the one additive bus
method `publish_typed`, dedup mutation-proven); `/goal` status numbers R042-labelled, absent →
unknown never zero, spend detail names the resume-reset so it is never presented as
whole-session ✓ (S9); `/autocompact` = emergency buffer only — context-overflow clearing is the
turnover seam trigger and ONLY that class ✓ (S10, mutation-proven); docs reviewed at execution
time (R147) — live re-fetch reconciled against the accepted M0-T102 snapshot, drift NONE,
fixture↔code pinned on every constant ✓ (S11); health bands remain private controller evidence ✓
(nothing here surfaces them to a worker); no transcript polling added ✓ (passive
classification/ingestion only).

## 3a. Correction-round delta (round-1 G3-C1 + G4-M1 blocking; re-frozen identity)

Applied F1–F7 (main report §3a): F1 measurements digested into the `publish_typed` dedup key
(G3-C1) + both-persist regression; F2 check-in discriminator caller contract, fail-visible on a
missing `sequence` (G4-M1) + persist/replay/refusal tests; F3 `goal_spend_tokens` rename
(G5-ADV-1) + durable READABLE read-back test; F4 `IdleCapVerdict(cap, known)` (G3-A2/G4-A1);
F5 campaign-tripwire widening with the four proven-slip phrasings (G4-L1); F6 constraint-poison +
excerpt-bound coverage (G4-L2); F7 `MAX_SCHEDULE_COUNT=64` cap (G5-ADV-2); fixture pre-2.1.239
completeness note (G4-A3). Delta evidence at the re-frozen identity: **38/38** goal pack +
**38/38** unit-D pack (76 combined); mutation total **12/12 KILLED** (adds
measurements-dropped-from-key, sequence-guard-removed, tripwire-widening-reverted); ruff clean;
line counts now 158 / 245 / 206 / 317 (+25 vs accepted unit D) / 432. Independent full-suite
evidence from round 1 stands: G3 ran the 2,278-test supervisor surface green; G4 ran the full
`tools/` suite (2,830 passed; 5 failures = their export's git-absence artifacts, none in scope).

## 4. Known limitations (disclosed for review)

1. The goal-semantics fixture is documentation-confidence (official-docs). The C1 live goal
   canary (owner-gated, R192/R197) upgrades verdict/check-in shapes to measured-live; the
   deterministic core does not depend on it (unit-C/D precedent).
2. `classify_goal_message` cause-matching uses keyword markers inside the DOCUMENTED warning
   frame; a cause worded entirely outside those markers classifies honestly as
   `unknown_unrecoverable` (cleared=True from the authoritative prefix — never a wrong class).
3. `ingest_goal_status` consumes an observation payload (structured fields); the live mapping
   from the `/goal` status view to that payload shape is C1 territory and recorded as such.
4. `publish_typed` grows the accepted unit-D `event_bus.py` by one additive method (+19 lines);
   existing publish paths are byte-unchanged and the unit-D pack re-ran green (38/38) —
   flagged for the G3 delta eye on the just-accepted file.
