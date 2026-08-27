# M0-T106 G3 code review — round 1 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: code-reviewer (independent,
read-only, dispatched 2026-08-27). Verdict returned: **PASS — with 1 REQUIRED (blocking)
correction + 4 advisories**.

---

# GATE REPORT — M0-T106 (D-024 Amendment 3 unit E: bounded /goal integration) — G3 code review

**Reviewer:** code-reviewer (independent, read-only)
**Task:** M0-T106 — `/goal` bounded inner-continuation integration
**Frozen identity reviewed:** branch `control/D-024-fable-codex-loop`, HEAD `ff2e2a808ed04fa94e0fb58caae88e0a0c33d8a3`; deliverable commit `c3f376882690a0460222f26612e03fcbf02608bd`; content_manifest_sha256 `d2c25b7edd07054ce352d975a28dea36c9c49d2986cfbc68fa8bac1dc31bf225`.
**Applicable requirements (packet):** D-024-R152, D-024-R162, D-024-R174.
**Identity check:** production source is byte-identical between deliverable `c3f3768` and HEAD `ff2e2a8` (the three intervening commits touch only `project-control/` control-plane files: `git diff --stat c3f3768 ff2e2a8` = gates/reports/state/task JSON only). Reviewed from the working tree at HEAD, which equals the deliverable source.

## VERDICT: PASS — with 1 REQUIRED (blocking) correction + 4 advisories

Recorded as PASS; correction **C1 is BLOCKING for acceptance and the next gate** per `.claude/rules/project-control.md` gate-verdict semantics. The deterministic core (S1–S11) is correct, faithful to the official `/goal` contract, modular, lint-clean, and independently reproduced green. The one blocking item is a latent silent-data-loss flaw in the additive `event_bus.publish_typed` seam that the module's own docstring invites callers to use for status records.

---

## Evidence reproduced (independently, read-only)

| Check | Command | Result |
|---|---|---|
| Goal pack | `python -m pytest tools/test_agent_supervisor_goal_integration.py -q` | **31 passed** in 0.19s |
| Unit-D event-bus pack (regression) | `python -m pytest tools/test_agent_supervisor_event_bus.py -q` | **38 passed** in 1.61s |
| Full supervisor surface (freeze scope) | `python -m pytest tools/ -q -k agent_supervisor` | **2278 passed, 2 skipped** in 187s — re-establishes the ≥1165 freeze baseline, no regressions |
| `event_bus.py` diff | `git diff 8bc13fa..c3f3768 -- …/event_bus.py` | exactly **+19 lines, one additive method**; all pre-existing publish paths byte-unchanged |
| Modularity | `python tools/modularity_check.py --check` | 0 failures (largest new file 240 lines); the 5 warnings are pre-existing unrelated files |
| Lint | `python -m ruff check` (0.13.0) on all 5 changed files | All checks passed |
| Line counts | `wc -l` | goal_contract **153**, goal_outcomes **240**, goal_checkins **170**, test **346**, event_bus **311** — all match the report |
| R045 reuse | `subagent_contracts.py:140 def assert_worker_text_clean` | genuine reuse of the accepted fail-closed validator; not re-implemented |

The producer's disclosed full-suite gap (two local runs externally stopped) is **adequately compensated for THIS diff**: the blast radius is narrow — three brand-new modules that nothing existing imports (grep confirms only the new test + `record_checkin` reference them), plus one additive method whose own 38-test pack is green — and I independently ran the entire 2,278-test supervisor surface green. A full local run was not required to bound regression for this change.

---

## Dimension findings

### 1. Contract correctness vs official /goal semantics (R152/R174) — PASS
Cross-checked `goal_contract.py` against the M0-T102 snapshot (`project-control/reports/M0-T102-docs-snapshot/goal.md`):
- One-goal-per-task binding: `_TASK_ID_RE ^M\d+-T\d+$` + foreign-ledger-task detection (`_LEDGER_TASK_RE`) + campaign tripwire, all enforced in `__post_init__` so an invalid condition never becomes an object. Direct-construction test (`test_s1_direct_construction_cannot_drop_the_bound`) proves the turn-bound guard bites even on hand-built objects — good defensive design.
- 4,000-char ceiling matches docs; turn-bound clause (`stop after N turns/minutes/hours`) required and matches the documented `or stop after 20 turns` bound. Composed layout (end state / stated check / constraints / bound) mirrors the documented "effective condition" shape.
- R045: `assert_worker_text_clean` runs **last on the full composed text**, exactly as `/goal` would see it — correct placement; S2 proves fail-closed on quota/countdown/%/conserve phrasings.
- Campaign tripwire scope is honestly framed as a heuristic backstop on obvious shapes atop the structural guard — not claimed to be exhaustive. Acceptable (see advisory A4).

### 2. Outcome honesty (goal_outcomes.py) — PASS
- Four clearing classes matched from the **authoritative documented prefix**, with ordered cause markers (auth → credit → context → model). The generic `model` marker is checked **last**, so it cannot shadow the more specific causes — verified. Unmatched cause under a valid prefix → `unknown_unrecoverable` with `cleared=True` (honest: cleared per the authoritative prefix, class unknown). A prefixed message containing a transient word (e.g. "timeout") is still governed by the authoritative prefix — verified live (`prefixed+timeout -> True model_unavailable`); a bare transient stays active (`transient_error_active`). Direction of the host-managed-credentials nuance is correct (auth + host-managed → `cleared=False`, goal stays active) and matches docs line 127.
- STRUCTURAL no-progress classification (`classify_pause`) deliberately does **not** parse the undocumented stall warning text — it keys on `control_returned` + `goal_still_active`. This is the right call (docs do not specify the warning text; guessing it would be a fabricated schema). Goal-stays-set semantics preserved.
- Resume gate (`resume_restores_goal`) exactly encodes docs lines 99–101: achieved/cleared never restored; active restores on all routes ≥2.1.239, else all routes except `picker`; unparseable version → `None` (honest unknown). Verified by S6 tests.
- `is_turnover_seam_trigger` fires **only** on `context_overflow` (autocompact = emergency buffer, never a seam substitute) — verified `credit_exhausted`/transient return False.
- `ingest_goal_status`: absent numbers → `Measurement.unknown` (never zero); `bool`/negative/non-numeric coerced to unknown via `_count`; spend detail names the resume reset so it is never presented as whole-session. R042 labels applied.

### 3. Check-in math (goal_checkins.py) — PASS
- Default cadence gaps F,2F,4F,4F… → offsets (30,90,210,330,450) matches docs ("1h after the first, then every 2h", capped at 4×). Env scaling and `0`-disables verified. Version gates ≥2.1.234 / ≥2.1.236 / cap-3 ≥2.1.246 match docs.
- Malformed-env → `GoalCheckinError` (fail-visible). This is a defensible and repo-consistent trade (surface a broken deployment rather than silently invent a schedule); it is controller-side corroboration math, so raising does not affect worker behavior. Acceptable.

### 4. `publish_typed` seam — ONE BLOCKING DEFECT (C1)
The additive method is appropriately minimal (+19 lines, reuses `idempotency_key`/`_store`/`_seen`, existing paths byte-unchanged, unit-D pack green). **However**, the dedup key is built over `{record_type, session_id, task_id, attributes}` and **deliberately excludes `measurements`**. For `goal_status` records — whose entire informational payload (turns evaluated, token spend) lives in `measurements` — two distinct snapshots that advance the numbers but share attributes produce an **identical dedup key and the newer record is silently dropped**. Reproduced:

```
r1 meas: {'goal_turns_evaluated': 3, 'goal_token_spend': 1000}
r2 meas: {'goal_turns_evaluated': 9, 'goal_token_spend': 5000}
s1 stored: True
s2 stored: False   (None => FALSE DEDUP of a distinct record)
duplicates_ignored: 1 ; stored count: 1
```

This is **latent** (no delivered caller routes status through the bus: `publish_typed` is called only by `record_checkin`, and check-in records carry no measurements — grep-confirmed). But the `publish_typed` docstring itself advertises the path — *"goal check-in/**status** records produced by other modules persist through the SAME durable store"* — and `ingest_goal_status` is a delivered, tested public function whose sole purpose is to produce exactly these measurement-bearing records for persistence. The moment the seam is used as its own docstring describes (C1 canary / controller wiring), it silently loses distinct durable telemetry — violating permanent principle #2 (every material value retains provenance / uncertainty stays visible) in a just-accepted frozen-file seam that this review was told to scrutinize with extra care.

### 5. Test quality — PASS (with one coverage gap, see A5)
S1–S11 assertions bite on real behavior (raises, exact offset tuples, dedup counts + replayed store contents, measurement values/labels, structural pause outcomes). Each named mutant maps to a biting test (e.g. `publish-typed-dedup-removed`→S8 second==None; `seam-trigger-any-unrecoverable`→S10 credit==False; `backoff-cap-removed`→S7 offsets; `host-managed-nuance-removed`→S4) — the 9/9 claim is plausible. Fixture facts cross-checked against the M0-T102 snapshot (verdicts, warning prefix/suffix, four classes, host-managed nuance, transient, no-progress, resume counters, checkin versions/idle-cap/interval/env-var, 4000 ceiling) — no invented facts; leak-scan tooth present.

### 6. Report/evidence accuracy — PASS
Line counts, test counts (31/38), and the +19 additive-method claim all reproduce exactly. Directive mapping: R152/R174 satisfied by the reproduced deterministic core; R162 (owner-gated canary pattern) is correctly deferred — C1 is prepared and owner-gated (R192/R197), not executed, consistent with the unit-C/D handling. (The binding `verification.json` PASS is the separate directive-compliance-verifier's responsibility, not this G3 report.)

---

## Required correction (BLOCKING acceptance)

**C1 (MEDIUM, blocking).** `event_bus.publish_typed` false-dedups distinct measurement-bearing records because the dedup key omits `record.measurements`. Two `/goal` status snapshots that differ only in `turns_evaluated`/`token_spend` collapse to one; the newer is silently dropped. Fix, low-risk: include a canonical digest of `record.measurements` in the key payload dict (check-in records have empty measurements, so their dedup is unaffected — the fix is a no-op for the only current caller), **or** narrow the docstring and guard `publish_typed` to reject measurement-bearing records with a typed error until a status persistence path with a correct key is designed. Add a regression test that publishes two goal_status records differing only in measurements and asserts both persist (this is the untested path — see A5).

## Advisories (non-blocking; fold into C1's fix or track)

- **A5 (INFO, pairs with C1).** No test exercises `publish_typed` with a measurement-bearing record; the coverage gap coincides exactly with the C1 defect. The regression test above closes both.
- **A2 (LOW).** `idle_checkin_cap` returns `None` for BOTH "uncapped (≥2.1.236)" and "unparseable version" — a caller cannot distinguish "no cap" from "version unknown". Consider distinct sentinels so an unknown version is not mistaken for uncapped.
- **A3 (LOW).** `record_checkin` dedup collapses two distinct check-ins that share identical attributes when no `sequence` (or other discriminator) is present (reproduced). Content-identical delivery is plausibly a genuine duplicate, so this is acceptable, but note the runtime is not guaranteed to always supply a discriminator.
- **A4 (LOW).** `_CAMPAIGN_SCALE_RE` can false-positive on legitimately single-task phrasings containing "all units"/"all milestones" (e.g. "…until all units are under budget"). The bias is fail-closed/conservative and the structural one-task binding is the primary guard, so acceptable — noted only so a false refusal is understood as expected behavior.

## Relevant files (absolute)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_bus.py` (lines 287–304: `publish_typed` — C1)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\goal_outcomes.py` (`ingest_goal_status` lines 199–240 — the measurement-bearing producer)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\goal_checkins.py` (`record_checkin`/`ingest_checkin` — A2/A3)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\goal_contract.py` (A4)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_goal_integration.py` (A5)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\goal_semantics_2_1_247.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T102-docs-snapshot\goal.md` (source-of-truth cross-check)

**Bottom line:** PASS. The deterministic `/goal` core is faithful to the official contract, honest under uncertainty, modular, and independently green across the full supervisor surface. Acceptance is blocked only until C1 (the latent `publish_typed` measurement false-dedup) is corrected with a regression test; A2–A5 are non-blocking.
