# M0-T106 G3 code review — DELTA round 2 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: code-reviewer (same agent
resumed with round-1 context, 2026-08-27). Verdict returned: **PASS (clean — no blocking
corrections remaining)**.

---

# GATE REPORT (DELTA re-review) — M0-T106 (D-024 Amendment 3 unit E: bounded /goal integration) — G3

**Reviewer:** code-reviewer (independent, read-only)
**Round:** 2 (delta) — round-1 verdict was PASS with C1 (MEDIUM) blocking + advisories A2/A3/A4/A5
**Re-frozen identity:** deliverable commit `5e60a0d39dfe4c6eaa479924e4291285f9e15f00`; content_manifest_sha256 `4d31dba2e03f0644c72725010235f95d68fb034cb82c78c8f3b560d6aa123293`; live HEAD `6cc9cf258fec4390c09478d99611281bac9a9581`.
**Identity check:** production source byte-identical between deliverable `5e60a0d` and HEAD `6cc9cf2` (tail diff = `project-control/` gates/reports/state/task JSON only). Correction round `c3f3768..5e60a0d` touches exactly the four production modules + test pack + fixture named in the request (plus control-plane reports/gates).

## VERDICT: PASS (clean — no blocking corrections remaining)

Round-1 C1 and advisories A2/A3/A5 are genuinely closed with reproduced evidence; A4 is correctly residual (non-blocking, by design). The three cross-reviewer corrections folded into this round (F3 G5-ADV-1, F6/F7 G4/G5 coverage) are also verified correct. No new defects introduced.

---

## Delta evidence reproduced (read-only)

| Check | Command | Result |
|---|---|---|
| Goal pack | `pytest tools/test_agent_supervisor_goal_integration.py -q` | **38 passed** (was 31; +7 correction tests) |
| Event-bus pack (regression) | `pytest tools/test_agent_supervisor_event_bus.py -q` | **38 passed** — unchanged, no regression from the `publish_typed` key change |
| Combined | both together | **76 passed** — matches the claimed 76 |
| Line counts | `wc -l` | goal_contract **158**, goal_outcomes **245**, goal_checkins **206**, event_bus **317**, test **432** — all exactly match the claimed 158/245/206/317/432 |
| Lint | `ruff check` (0.13.0) on all 5 changed files | All checks passed |
| Modularity | `python tools/modularity_check.py --check` | 0 failures (warnings pre-existing/unrelated) |
| Signature-change blast radius | grep of the 4 changed public APIs repo-wide | `idle_checkin_cap`/`record_checkin`/`checkin_schedule`/`IdleCapVerdict` referenced only in `goal_checkins.py` + the test pack — no external consumer breaks |

---

## Correction-by-correction verification

**F1 (closes round-1 C1 MEDIUM + A5) — VERIFIED CLOSED.**
`event_bus.publish_typed` now digests `record.measurements` alongside attributes: `"measurements": {name: m.to_dict() for name, m in record.measurements.items()}`. Two `/goal` status snapshots advancing only their numbers are now distinct records; identical snapshots still collapse. Independently reproduced:
- Distinct measurements → both persist (my exact round-1 reproduction is now the committed test `test_s8_status_snapshots_differing_only_in_measurements_both_persist`).
- **True-replay idempotency preserved** (the correctness concern the coordinator flagged): I verified that the same observation with *differing ingestion timestamps* still collapses (`r2` returns None, `duplicates_ignored=1`) — timestamps are correctly excluded from the key. Check-in records carry empty measurements, so their dedup is unchanged.

**F2 (closes round-1 A3 + G4-M1) — VERIFIED CLOSED; fail-visible boundary is correct.**
`record_checkin` now enforces a caller contract: `payload` must be a Mapping carrying a `sequence` discriminator, else typed `GoalCheckinError`. This is the right boundary — the guard sits at the *bus-persistence* seam (`record_checkin`), where a silent collapse would undercount check-ins and defeat the idle-cap-of-3 corroboration; `ingest_checkin` (pure record construction, no persistence) still tolerates malformed input for honest inspection. Tests confirm: distinct sequences both persist, byte-identical re-delivery dedups (counted no-op), missing discriminator raises and stores nothing. Preferring fail-visible over silent data loss is consistent with the repo's honesty ethos.

**F4 (closes round-1 A2) — VERIFIED CLOSED.**
`idle_checkin_cap` now returns `IdleCapVerdict(cap, known)`. Reproduced: `2.1.247 → (cap=3, known=True)`, `2.1.240 → (cap=None, known=True)` [documented-uncapped], `garbled → (cap=None, known=False)` [unknown]. Ignorance is now distinguishable from "no cap" — the exact conflation I flagged is gone.

**F3 (G5-ADV-1; not my finding, reviewed for correctness) — VERIFIED CORRECT and material.**
`goal_token_spend → goal_spend_tokens`. I independently confirmed the journal's `SENSITIVE_KEY_PATTERN` (`(^|_)(…|token|…)($|_)`): `goal_token_spend` matches on the delimited `_token_` segment and would be over-redacted to `[REDACTED:sensitive_key]` on the durable store (blinding the R042 read-back); `goal_spend_tokens` is safe (the `tokens` suffix is not a delimited `token`). The rename is a genuine fix, and `test_s9_spend_survives_durable_store_readable` proves the value survives readable. No stale `goal_token_spend` key remains in live code (the only occurrence is the explanatory comment).

**F5 (G4-L1; widens the A4 heuristic) — VERIFIED; A4 correctly RESIDUAL.**
The campaign tripwire now also catches `finish/complete/wrap up/deliver … (milestone|backlog|project|campaign|remaining work)` and `the rest of the …` forms; the four proven-slip phrasings are covered by `test_s1_campaign_scale_refused`. This is a deliberately fail-closed-biased heuristic layered on the structural one-task binding; it does not (and does not claim to) be exhaustive, so my round-1 A4 remains a correct non-blocking residual advisory — the widening reduces, without eliminating, the heuristic gap, which is the honest and appropriate posture.

**F6/F7 (G4/G5 coverage) — VERIFIED PRESENT.**
`test_s2_token_pressure_via_constraint_fails_closed` (R045 poison via the constraint path bites, since the validator sees the full composed text), `test_s3_reason_excerpt_bounded_160` (160-char excerpt cap bites), and `MAX_SCHEDULE_COUNT=64` with `test_s7_schedule_count_bounded` (fail-visible over-count refusal) are all present and pass.

**Mutation (12/12 claim) — PLAUSIBLE.** The three new named mutants each have a biting test: `measurements-dropped-from-key` → `test_s8_status_snapshots_differing_only_in_measurements_both_persist` (snap2 would false-dedup); `sequence-guard-removed` → `test_s8_missing_discriminator_fails_visible` (no raise); `widening-reverted` → `test_s1_campaign_scale_refused` (new phrasings). Combined with the original 9, 12/12 is credible.

---

## Residual (non-blocking)

- **A4 (LOW, residual advisory).** The campaign-scale tripwire remains a heuristic (now widened) and is not exhaustive; the structural one-task binding is the primary guard. Fail-closed-biased, so a rare false refusal of a legitimately single-task phrasing containing widened verbs/nouns is the acceptable, expected behavior. No action required.

## Report/evidence accuracy at the new identity
Line counts (158/245/206/317/432), combined test count (76), and the additive nature of the `event_bus.py` change all reproduce exactly. Directive posture unchanged: R152/R174 satisfied by the reproduced deterministic core; R162 remains correctly owner-gated (C1 canary not executed). The binding `verification.json` PASS is the separate directive-compliance-verifier's responsibility.

## Relevant files (absolute)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_bus.py` (publish_typed, lines ~287–308 — F1)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\goal_checkins.py` (record_checkin contract F2; IdleCapVerdict F4; MAX_SCHEDULE_COUNT F7)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\goal_outcomes.py` (goal_spend_tokens F3)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\goal_contract.py` (campaign widening F5)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_goal_integration.py` (regression tests F1/F2/F4/F6/F7)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\redaction.py` (SENSITIVE_KEY_PATTERN — F3 cross-check)

**Bottom line:** PASS. The consolidated correction round closes round-1 C1 and advisories A2/A3/A5 with reproduced evidence and biting regression tests; A4 is a correct non-blocking residual; F3/F6/F7 are verified correct; no external API consumers break and no regression appears in either pack. This delta clears the round-1 blocking correction.
