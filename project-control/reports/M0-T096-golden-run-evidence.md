# M0-T096 — Unit I: two-unit golden run, fault-injected canaries, Amendment-7 watcher — D-024 Phase H

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R106** (Phase H; packet-named). Status: **STAGED** (sections 0–3; section 4 evidence is
filled by the implementation). Lane discipline (Amendment 7): every scenario below is **lane-1
INJECTED/deterministic** (R222/R223) — fake provider executables, scratch runtimes, disposable
git checkouts, accelerated counters. Nothing waits for or provokes a natural Fable 5 event
(R220/R221); natural-event evidence stays `pending_live_observation` (R224).

## 0. Reuse boundary (R018: prove existing architecture, extend — never duplicate)

Prove-first verdict over the existing packs (full executable register in the test file §1 P-1):

**Fully proven — CITE, do not rebuild:** 16.9 items (b) mixed Fable/4.8 (`model_chain`
RealProcessSwitch/Return + `turnover_integration` exactly-one-opus), (c) bounded subagents/no
parent flooding (`bounded_contracts` producer-cap/lease + `runtime_supervision` transcript-cap/
band tests + `subagent_telemetry`), (d) main/healthy-resume/fresh-spawn + startup overhead
(`bounded_contracts` spawn-decision + startup-observation clusters), (j) status clarity
(`operator_channel` S2StatusSection14 + succession S15TelemetryHonesty), (k) stop → coherent
resumable checkpoint (succession S4StopIntentPrecedence + `operator_channel` S3DurableControls);
R031/R032 host-restart/auto-resume (`scheduler` FixedAction/AutostartPlan/FakeSchtasks/
AutostartInstaller + succession S9HostRestartAutoResume incl. the truthful-activation-blocker
test + `native_adapter` activation-limitations); R186 steps 1,3,4,5,6,7,9,10,11,13,14,15
(campaign orientation, native backend selection, goal bounding, passive observation,
non-interrupting health bands, safe-seam validation, replay-corpus decision rules, exact-once
effects, successor reconstruction, operator controls, crash matrices, owner-gate invariants
7–9 + the 15-invariant register); R113 16.7 graph/context items except on-demand-after-compact
(`test_code_graph` determinism/staleness/tamper, `test_context_pack` AS2 eight default
exclusions + AS3 never-silently-truncated, `test_context_pack_index` tiers,
`test_repo_views`, `test_context_benchmark` frozen no-worse baseline = the R079 performance
envelope; `bounded_contracts` stale-graph-never-used = R080).

**Existing composition surfaces (REUSE):** `CliStartTests` + `make_live_checkout` + fake
provider scripts (`test_agent_supervisor_loop.py`) — the operator-shaped `cli.main(["start",…])`
end-to-end harness; `LoopTestBase`/`FakeRunner`/`FakeReviewer` (loop), `ChainTestBase` +
`fake_claude_chain.py` env-driven fake (model_chain), `FakeClock` (bounded_mode),
`CrashTestBase.crash()` journal-handle kill/reopen (crash), `JournalCase.reopen()` +
`epoch_lease` injected clock (controller_succession), `SeamRotationTests` threshold+READY
pattern, `reconcile_after_restart` (runtime_backend), `campaign_continuity.advance()` optimistic
sequence guard, register-test pattern (`invariants` InvariantRegisterTests / crash
BoundaryRegisterTests / bounded_mode BreakerWiringTests).

**Genuine gaps this unit builds (and nothing else):**

| Gap | Delivered as |
|---|---|
| 16.9 (m) golden run: two consecutive units from the exact owner command crossing ≥1 safe rotation + 1 injected controller restart (R115/R121/R186) | NEW `tools/agent_supervisor/golden_run.py` (deterministic campaign/fixture builders + fault-injection drivers) + NEW `tools/test_agent_supervisor_golden_run.py` |
| 16.9 (h) bounded soak via accelerated counters (R119/R182) | soak scenario in the golden-run pack driving accelerated cycles across health-band/breaker boundaries; bound documented from the breaker registry/config |
| 16.9 (a)(e)(f)(g)(i) composition gaps: multi-epoch×forced-rotation; extended pause via FakeClock; status/ask while `CLAUDE_RUNNING`; accelerated overnight + injected restart; behavioural double-`start` idempotency | thin composition tests in the golden-run pack (each composes the cited existing mechanisms; no new machinery) |
| R186 step 2 (autonomous bounded selection) + step 12 (correct-next advance) | thin tests: injected-Codex next-unit selection validated through the bounded-task rules; `advance()` to the dependency-correct next id with stale-sequence refusal |
| R113 on-demand retrieval after a compact handoff | thin test composing the compact-boundary fixture pattern with deep on-demand retrieval |
| R118 progression ladder register | executable register (invariants-file pattern): each rung → named proof; meta-test fails if a rung loses coverage |
| Amendment-7 watcher + `pending_live_observation` register (R224–R227) | NEW `tools/agent_supervisor/live_observation.py`: read-only observer over EXISTING durable records; CAS-idempotent `state_kv` register; `evidence_class` live/injected labeling fail-closed; no code path writes `verified_live=true` |
| **Discovered integration defect:** the accepted H1 refusal seam (`GuardrailBridgeIntegration`, loop.py:1603) is never constructed in the production `start` path — `cli.py` wires the quota seam and `WorkerTurnoverIntegration` but no guardrail bridge, so a real run records no `guardrail_refusal/*` entry and the watcher would have nothing to observe (R226 unobservable) | `cli.py::_run_loop` wiring: build `GuardrailBridgeIntegration(journal=…, authorized_task=AuthorizedTaskRecord(from the task packet))` and pass `guardrail_bridge=`; missing packet fields → `authorized_task` stays unproven and the classifier fails closed (CONDITION_AUTHORIZATION_UNPROVEN), exactly the H1 design; record-intent-only on this build (no actuation channel exists) |

**Explicitly NOT built (already satisfied or owner-gated):** no new epoch/lease/rotation/
crash/effect machinery; no new telemetry capture (R225 reuse); no schema/table change to the
journal (`state_kv` register only, no `JOURNAL_SCHEMA_VERSION` bump); no graduation automation
(R227 comparison produces a report; flipping any `verified_live` flag remains an owner-reviewed
capture step per the fixture's own `upgrade_procedure`); no live 4.8 actuation path
(`assert_actuation_permitted` double-gate untouched).

## 1. Acceptance-scenario pack (pre-implementation; R115/R186/R121/R118/R222–R227)

All scenarios deterministic/injected (R182); fake executables labeled INJECTED in every record
the harness produces (R223).

| ID | Scenario (Given / When / Then) | Key reqs |
|---|---|---|
| P-1 prove-first register | Given the citation register (16.9 a–m + R186 steps 1–15 → existing or new test names), when the meta-test runs, then every cited proof exists in its named file and every register row is covered — the executable form of the R018 prove-first duty. | R018/R115/R186 |
| GR-1 exact-command two-unit golden run | Given a disposable git checkout (task branch, real ledger packet), scratch runtime, fake Claude/Codex executables, and a two-unit campaign record, when `cli.main(["start", "--mode", "limited-auto", "--owner-enable-bounded-auto", "--max-cycles", "2", …])` runs ONCE with the exact operator verb/flag shape, then: unit 1 dispatches, checkpoints, is reviewed by injected Codex, forwards exactly once; unit 2 receives the reviewer's forwarded prompt (not the original); the run ends at a coherent seam; zero human messages moved the campaign between units (R121: the only operator input is the start command itself; the bounded-auto enable is part of the recorded exact command). | R115(m)/R121/R186/R222 |
| GR-2 real low-risk repository effect | Given the golden run's unit 1, when the fake producer performs a REAL `git commit` on the non-protected task branch of the disposable checkout and reports the real SHA in its checkpoint, then the checkpoint validates against live git state and no protected ref is touched (R118 "one low-risk real repository task" — in the injected harness; live-model canaries are NOT run, section 2). | R118/R186 |
| GR-3 safe-seam rotation inside the golden run | Given unit 1 crosses the context threshold (`usage_known=True`), when the seam is reached, then rotation happens BETWEEN units via the standard path (never mid-unit), the successor's first checkpoint is READY at the commanded identity, and unit 2 completes on the fresh session — one safe primary-session rotation crossed (R115(m)). | R115(a,m)/R186/R098 |
| GR-4 injected controller restart, exact-once | Given the golden run crashes (journal handle killed) at a chosen boundary between unit 1's acceptance and unit 2's dispatch, when the SAME start command runs again, then recovery reconciles (lease → same epoch; outbox → same message; no second forward, no duplicate producer, no lost pending action) and unit 2 proceeds — one injected controller restart crossed without duplicate work. | R115(g,m)/R030/R186/R222 |
| GR-5 injected refusal | Given the fake producer emits the recognized structured refusal shape (INJECTED fixture), when the unit ends without a checkpoint, then the quota delegate declines, the guardrail seam classifies recognized-refusal, records the R070 journal record (`shape_verified_live=false`), stops at PAUSED_RECOVERY — record-intent only, no bridge actuation (`assert_actuation_permitted` refuses both halves). | R110/R222/R223/R228 |
| GR-6 injected quota exhaustion | Given the fake producer emits the Fable-exhaustion signal, when the seam evaluates, then the quota policy owns the signal (disjoint from the refusal bridge), detect-and-hold behavior holds/turns over per the accepted worker-turnover seam, INJECTED-labeled. | R110/R222/R184 |
| GR-7 injected fallback sequence | Given an exhaustion with an authorized injected controller, when turnover actuates in the harness, then exactly one 4.8 worker redispatches and the next task returns to the pin at the seam (cited `model_chain`/`turnover_integration` proofs + golden-run composition). | R115(b)/R222 |
| GR-8 ambiguous-effect recovery | Given a crash between `record_before_effect` and `record_after_effect` during the golden run's push-equivalent effect, when restart reconciles, then the effect is proven from read-only evidence or the run stops asking — never retried on a guess, never duplicated. | R115(g)/R185/R222 |
| GR-9 status/ask while producer running | Given the machine is at `CLAUDE_RUNNING` with a live (fake) child, when `status`/ask read paths run, then they answer read-only from durable state without touching the producer (no cancel, no context injection, no worker message). | R115(f)/R089/R045 |
| GR-10 behavioural double-start idempotency | Given a start holds the single-instance lock, when a second `cli.main(["start",…])` runs against the same checkout/runtime, then it is a typed refusal/no-op naming the live lock — no second dispatch, no journal damage. | R115(i)/R027/R036 |
| GR-11 multi-epoch × forced rotation | Given three renewable epochs in one journal, when each epoch ends through a FORCED rotation (owner-request/threshold), then epochs advance strictly one-active-at-a-time with succession recorded and no revival. | R115(a) |
| GR-12 extended pause, clean resume | Given a durable pause and a FakeClock advanced far (days), when resume + revalidation run, then the campaign state is intact, elapsed time is honest (no reset), and work resumes exactly where it stopped. | R115(e) |
| GR-13 accelerated overnight + restart | Given an accelerated multi-cycle campaign crossing simulated UTC day rolls, when an injected restart lands mid-campaign, then per-day tallies restore correctly, no unit duplicates, and the campaign completes. | R115(g)/R119/R182 |
| GR-14 bounded soak via accelerated counters | Given the breaker/health-band registry driven across each boundary by accelerated counters (many cycles, zero real tokens), when the soak completes, then every band transition fires at its configured boundary, tallies persist across a mid-soak reopen, and no counter grows unbounded — the R118 "required bounded soak/reliability proof", bound stated from the registry. | R115(h)/R118/R119/R182 |
| GR-15 autonomous bounded selection + correct-next advance | Given the injected Codex decision selects the campaign's next unit, when selection is validated through the bounded-task rules and `advance()` moves the record, then a vague/oversized selection refuses; a stale sequence refuses; the record lands on the dependency-correct next task. | R186 steps 2,12 |
| GR-16 progression-ladder register | Given the R118 ladder (deterministic simulation → shadow telemetry → supervised local canary/fake effects → disposable real-session canary → crash/forced-fallback canary → low-risk real task → two-unit golden run → host-restart canary/limitation → soak → independent review → owner activation checkpoint), when the register test runs, then each rung maps to a named existing/new proof or an explicit owner-gated status — no silent rung. | R118 |
| GR-17 on-demand retrieval after compact handoff | Given a compact-boundary handoff (pre-token fixture pattern), when deep on-demand retrieval runs afterwards, then exact excerpts with provenance still resolve (no dependence on evicted transcript). | R113 |
| W-1 watcher is structurally passive | Given `live_observation.py`, when inspected/executed, then it opens durable state read-only-by-contract (getter calls only), spawns no subprocess, sends no prompt/message, injects no context (structural assertions on the module source + behavioral no-write checks against a journal fixture). | R225/R226/R045 |
| W-2 natural-event capture, idempotent | Given a journal carrying a (test-injected simulation of a) live classifier record (`guardrail_refusal/*`, exhaustion transition, `usage_limit_record`, provider abort, model-change audit), when the watcher scans, then exactly ONE sanitized register row per distinct event is CAS-written (`pending_live_observation/<digest>`) carrying the five R226 fields (observed event type, installed-version shape, classification decision, selected response, sanitized outcome); a re-scan writes nothing new. | R224/R226 |
| W-3 injected never masquerades as live | Given register rows, when any source record is injected/fixture-born (`shape_verified_live=false` corpus, harness markers), then `evidence_class="injected"` (the fail-closed default) and the row can NEVER satisfy the live precondition; `evidence_class="live"` requires the explicit live-session provenance the watcher can only take from a genuinely observed record. | R223/R224 |
| W-4 no premature verification | Given the whole module, when searched/executed, then NO code path writes `verified_live=true`, flips a corpus flag, or marks the live canary PASS; the register exposes only `pending_live_observation`/`observed` states; graduation (R227) is a comparison REPORT + the fixture's owner-reviewed `upgrade_procedure`, never an automatic act. | R224/R227 |
| W-5 pre-graduation natural event behaves fail-closed | Given a natural event arrives before its feature graduates, when classified, then the accepted H1/H2 machinery holds safely (quota → detect-and-hold; refusal → record-intent + PAUSED_RECOVERY), `assert_actuation_permitted` refuses (measured-live absent AND R595 absent), and the watcher's captured row is the only new durable artifact. | R227/R228 |
| W-6 sanitization at the register boundary | Given hostile/verbose source content (paths, secrets, terminal escapes, oversized text), when a register row is written, then `sanitize_structure` bounds/redacts it and the row records its redaction count. | R226 |
| W-7 refusal seam wired in production start | Given the cli wiring fix, when `_run_loop` builds the loop, then a `GuardrailBridgeIntegration` is constructed from the task packet (unprovable authorization → fails closed) and the loop's refusal seam is reachable in a real run — proven by driving the CLI-built loop against an injected refusal. | R106/R110/R226 |

## 2. Owner-gated / deliberately-not-run items (honest boundary)

- **No live-model canary and no natural-event waiting/provocation** (R220/R221/R119): every
  scenario uses injected runners. The live refusal-shape capture stays `pending-owner-C1`
  (H1 posture); the natural refusal/quota/model-turnover observation stays
  `pending_live_observation` (R224) with the watcher as the capture path.
- **Feature gated on live observation: exactly ONE** — automatic 4.8 bridge actuation
  (measured-live shape AND R595, both absent; fail-safe). Nothing else blocks (R228).
- **Continuous mode stays DISABLED after the golden run** (R187); limited-auto inside the
  harness is per-launch, explicit, disposable, and part of the recorded exact command — it
  activates nothing on the live host (R118 default-off; start refuses the mode by name
  without the explicit enable).
- **R595 activation path, anchor publication, PR #241, protected refs:** untouched.
- **Shadow-mode-against-real-sessions + the campaign's own primary-session turnover
  (16.9 l):** historical/campaign evidence, cited in section 4 from the ledger and campaign
  record (mechanism tests cited in P-1), not re-executed.

## 3. Implementation guidance

- Modules: `golden_run.py` (campaign fixture builders + fault-injection drivers + ladder
  register data), `live_observation.py` (watcher + register), thin `cli.py` wiring (bridge
  construction only; commit cites D-024-R106). Registry/fixture JSON written LF.
- Tests: ONE new file `tools/test_agent_supervisor_golden_run.py` (the §1 matrix; unittest
  style like the loop pack; fake executables materialized per test; scratch `--runtime-base`).
- Environment: foreground chunked suite runs; never mutate during a live suite;
  `modularity_check` only after `git add`; CI on the pushed SHA is the confirming
  whole-suite run.
- DCV scale: 83 applicable requirements; `M0-T095-evidence-map.json` + its verification entry
  are the worked templates.

## 4. Evidence (filled by the implementation session)

*Pending implementation.*
