# M0-T091 — G3 Independent Code Review

> Saved VERBATIM by the orchestrator from the code-reviewer agent-return channel (transport
> entity-decoding only). Verdict: PASS (no blocking defects; 2 NITs, non-blocking).

All report figures verified accurate (290 + 15 context-pack = 305). My independent review is complete. Here is the gate report.

---

# GATE REPORT — G3 Independent Code Review

| Field | Value |
|---|---|
| **Gate ID** | G3 (code review) |
| **Task ID** | M0-T091 — D-024 C2: invisible runtime supervision |
| **Reviewer** | code-reviewer (independent; not the producer) |
| **Producer** | orchestrator |
| **Frozen content commit** | `ee564dd` |
| **Live HEAD at dispatch** | `b4f7e40` |
| **Result** | **PASS** (no blocking defects; 2 NITs, non-blocking) |

## Clean-environment note
Review performed against the frozen content identity `ee564dd`. Verified the working tree is at HEAD `b4f7e40` and that the deliverable source is **byte-identical** between `ee564dd` and HEAD: `git diff --stat ee564dd b4f7e40` shows only control-plane files (`gates/M0-T091-G2.json`, `reports/M0-T091-G2-self-check.md`, `reports/M0-T091-evidence-map.json`, `state.json`, `tasks/M0-T091.json`) — no deliverable module or test file changed post-freeze. Sandbox Python is 3.11.9; the supervisor modules use `from __future__ import annotations` and no PEP 695 generics, so they collect and run cleanly. All commands below are read-only (pytest, ruff, python probes, git log/diff). No `project_control.py`, git-write, or `gh` was run.

## Acceptance criteria reviewed
Packet `acceptance_scenarios` is empty; the acceptance contract is the packet `objective` + `outputs` and the D-024 anchors (s5.4, s5.5, s6, s6.1–6.3, s13, s16.2). All three named `outputs` are present at `ee564dd`:
- health-band / no-progress / extension-gate / landing enforcement under `tools/agent_supervisor` (5 new modules) — present, accelerated-clock testable;
- `tools/test_agent_supervisor_runtime_supervision.py` (54 tests incl. forty-minute-equivalent landing, high-usage-near-seam, observe-produces-no-message) — present;
- `project-control/reports/M0-T091-runtime-supervision.md` — present.

## Directive-requirement verification (requirements the modules explicitly encode)
Each re-derived from `source-001.md` and confirmed in source + independently probed/tested:

- **s5.4 (token count is one signal; explicit rule set over multiple signals)** — `evaluate_band` selects on occupancy band + `ProgressAssessment` (verified_progress/coherent/near_complete/losing_thread/no_progress/scope_drift). Raw counters (cumulative_tokens, compactions, elapsed, turns, tool_batches) are carried by-value in `TelemetrySnapshot` with source/confidence; progress/retry/elapsed signals are aggregated by `runtime_detectors` into the assessment flags. PASS.
- **s5.5 (private bands; unknown-conservative; losing-thread immediate; near-complete reaches seam; emergency only under the closed set; no maxTurns/spend as routine sizing; catastrophic ceiling ≥5× outside normal; per-model calibration)** — all present and probed (see dimension table). PASS.
- **s6 (two linked records; producer cap ≤3; no overlapping leases; leak guard)** — `subagent_contracts` + `lease_runtime`. PASS.
- **s6.1 (extension return items incl. likely-evidence-sources; default defer-to-backlog; approval = one least-costly bounded experiment; decision is a record with no apply surface)** — `extension_gate`. PASS.
- **s6.2 (durable-evidence progress definition; only evidence resets; repeated commands/hypotheses/cycling tests/unbounded searches/successive summaries)** — `runtime_detectors`. PASS.
- **s6.3 (parent/child turnover draining; no new children once landing; one landing instruction per child; successor read-only anytime, write only after children + external effects reconciled + zero live writer grants)** — `child_handoff.TurnoverCoordinator`. PASS.
- **s13 (smallest-complete packet; non-omittable categories)** — `workload_sizing`. PASS.
- **s16.2 (the packet's supervision cases)** — every runtime case maps to code + a passing test (observe/prepare/land, high-usage-near-seam, low-usage-speculation, forty-minute-equivalent, TaskStop-reserved, catastrophic ceiling recovery, scope-drift→extension, backlog default, approve/deny-without-editing, nested children can't evade cap/leases, parent rotation no overlap, verbose transcript out of context, read-only agents don't consume cap, child API failure explicit). PASS.
- **Supervisor-freeze (D-024-R101 citation in packet + commit + every new module docstring + test-pack docstring)** — verified in all six docstrings and the `ee564dd` commit message. PASS.

## Steps independently executed (reproducible)
1. `git diff --stat ee564dd~1 ee564dd` — change set = 5 new modules + 3 edited (subagent_contracts/workload_classifier/workload_sizing) + 1 new test pack + report; **C1 pack `test_agent_supervisor_bounded_contracts.py` NOT in the change set** (confirmed untouched).
2. `git diff --stat ee564dd b4f7e40` — post-freeze diff control-plane only.
3. `pytest tools/test_agent_supervisor_runtime_supervision.py -q` → **54 passed**.
4. `pytest tools/test_agent_supervisor_bounded_contracts.py -q` → **53 passed** (C1 untouched, green under corrected guards).
5. Adjacent packs (statusline handler, telemetry core, subagent telemetry, rotation, scheduler) → **290 passed**; `test_context_pack.py` → **15 passed** (290+15 = **305**, matching the report).
6. `pytest tools/ -k agent_supervisor -q` → **2148 passed, 2 skipped, 0 failed** (supervisor-freeze baseline duty amply satisfied, ≥1165).
7. `ruff check` over all 9 new/edited files → **All checks passed**.
8. `python tools/modularity_check.py --check` → **exit 0**, 0 failures (the 5 warnings are all pre-existing files — `cli.py`, `policy.py`, `context_benchmark.py`, `surveyReview/types.ts`, `mappluto_geometry_arcgis.py`; none the new modules).
9. `wc -l` on the 5 new modules + test pack → 163 / 478 / 274 / 213 / 212 / 849 — **exact match to report §1**.
10. Independent `python -c` probes of the guards, lease normalizer, ledger, and band evaluation (outputs below).
11. `git diff ee564dd~1 ee564dd` on the 3 edited files — each change is scoped exactly to a correction-bundle item (no scope creep).

## Expected vs actual — by review dimension

| Dimension | Expected | Actual | Verdict |
|---|---|---|---|
| 1. Band precedence / landing / detectors / gate / lease / handoff fidelity | Per s5.4/5.5/6/6.1/6.2/6.3/16.2 | Probed: unknown-occupancy→observe (never normal); losing-thread→immediate LAND at occ 0.10; no-progress/scope-drift→forced PREPARE + requires_review; near-complete+coherent at LAND→ALLOW-SEAM (no message); emergency only under closed set (occ≥emergency auto-adds imminent-hard-limit; unknown condition rejected); one-message landing exactly once; durable-evidence-only reset | PASS |
| 2. Carried correction bundle (9 items) | Each genuinely applied + regression test + correct edge behavior | All 9 applied, each with a named regression test, all independently probed (below). Legit prose ("Fix the landing page", "Observe the failing test", "island England landing", "Save and test what is coherent", the landing text) passes BOTH guards; band vocabulary + spaced/spelled percent + conserve synonyms rejected | PASS |
| 3. R045/R050/R056 (no worker-visible counter/quota/band vocab) | DetectorFinding/BandEvaluation expose nothing worker-facing; single landing message passes both guards | `DetectorFinding` fields = {assignment_id, kind, detail, at_minutes, requires} (no worker_message); `BandEvaluation.reasons` are controller-private, only `worker_message` reaches worker and is re-proven through `assert_worker_text_clean`+`assert_no_envelope_leak` in `SupervisionState.apply` | PASS |
| 4. No regression | C1 pack unedited + green; adjacent packs green; ruff+modularity clean | C1 untouched + 53 green; 2148 agent_supervisor tests pass; ruff clean; modularity exit 0 | PASS |
| 5. Report accuracy | Line/test counts + §1–5 claims | Line counts exact; 54 new / 53 C1 / 107 combined / 305 adjacent all reproduced; freeze citation present | PASS |
| 6. Shadow-only / leaf discipline | No spawn/resume/stop/message; no new dep; no graph/index import | grep confirms no subprocess/os.system/network/spawn/message; "TaskStop" appears only in doc comments; imports are stdlib + sibling modules; no graph/index import in the 5 new files; no new dependency | PASS |

## Reproduced probe evidence (key correction-bundle items)
- **Guards (MAJOR-1 / MAJOR-2 / MINOR-3 / G5 M1/M2):** `assert_worker_text_clean` + `assert_no_envelope_leak` — legit prose (`Fix the landing page`, `Observe the failing test`, `island England landing`, `Save and test what is coherent`, `LANDING_DIRECTION_TEXT`, `Land the change on the branch`) all pass BOTH guards; pressure paraphrases (`70 %`, `70 percent of your budget`, `conserve tokens`, `save tokens`, `be frugal with tokens`, `economize on context`, `spare your window`, `5000 tokens left`, `budget of 200000`, `50% of your context window`) all `quota_language`-rejected; band vocabulary (`prepare to land band`, `prepare_to_land`, `emergency_stop`, `observe band`, `health band land`, `normal band`) all `envelope_leak`-rejected.
- **Lease normalizer (MINOR-4 / M3):** `/`, `.`, `''` → `bad_lease_path`; `c:/dir`, `c:dir` (absolute) → reject; `../up`, `pkg/../../x` (traversal) → reject; `./pkg`→`pkg`, `pkg/./sub`→`pkg/sub`, `PKG/Sub`→`pkg/sub`; dot-segment overlap `./pkg` vs `pkg/sub` detected.
- **Ledger serialization (M4):** first candidate granted+folded, second overlapping candidate `lease_overlap`-rejected against the live active set; producer cap enforced at 4th writer (`producer_cap`); nested child overlap rejected via same fold; parent release refused while child holds (`children_not_drained`); out-of-scope write `scope_violation`; unknown parent rejected. Test `test_grant_ledger_serializes_where_snapshot_validation_cannot` proves the snapshot hole first (`assert_grantable((), first)` and `assert_grantable((), second)` both pass) then closes it via the ledger — genuine teeth.

## Defects
- **NIT-1 (non-blocking) — mixed exception types from `LeaseLedger.grant()`.** `grant()` raises `subagent_contracts.ContractError` for overlap/cap/bad-lease (via `assert_grantable`/`validate_envelope`) but `lease_runtime.LeaseRuntimeError` for duplicate/unknown-parent/children-not-drained. Reproduced: the overlap refusal surfaces as `ContractError(code=lease_overlap)`, not `LeaseRuntimeError`. A future runtime caller that catches only `LeaseRuntimeError` to queue-and-retry would let an overlap/cap refusal propagate uncaught. The fail-closed invariant is fully intact (no grant occurs; no overlapping writers) and both are `ValueError` subclasses, so this is a robustness/consistency observation, not a correctness or security hole. Optional: catch `except ValueError` in callers, or re-wrap in `grant()`.
- **NIT-2 (non-blocking, by design) — `percent_numeric` quota pattern is broader than "context percentage".** It rejects any numeric percent in worker text (e.g. "80% test coverage"), not only context/budget percentages. This is a fail-closed, directionally-safe trade the producer documented (report §2, ADV-2 residual); the worker rephrases. Noted for completeness only.

No MAJOR or MINOR defects found.

## Required rework
None blocking. NIT-1 and NIT-2 are optional and may be deferred to a follow-up; neither weakens a directive requirement or a fail-closed invariant.

## Reviewer conclusion
The five new runtime modules faithfully encode D-024 s5.4/5.5/6/6.1/6.2/6.3/13/16.2: band precedence is correct (unknown-conservative, losing-thread escalation, no-progress/scope-drift forced review, near-complete reach-seam, emergency only under the closed condition set), the one-message landing discipline is sparse and guard-proven, detectors reset only on durable evidence, the extension gate defaults deny-to-backlog with no apply surface, the lease ledger serializes grants and folds each in (closing the documented G5 M4 snapshot hole), nested children cannot evade the cap or leases, and child handoff / turnover draining preserve exact-once ownership. All nine carried M0-T090 corrections are genuinely applied, each with a regression test, and each verified by independent probe. Supervision is invisible and shadow-only: no actuation surface, leaf-package discipline intact, no new dependency, R595/activation untouched, and no worker-visible counter/quota/band vocabulary anywhere (the sole worker-facing artifact is the guard-proven landing sentence). The C1 pack was not edited and stays green; ruff, modularity, and 2148 agent_supervisor tests pass; report figures reproduce exactly.

**Verdict: PASS.** (Blocking corrections for the next gate/acceptance: none. NIT-1/NIT-2 recorded as optional non-blocking follow-ups.)

Relevant absolute paths:
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\runtime_health.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\lease_runtime.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\runtime_detectors.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\extension_gate.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\child_handoff.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\subagent_contracts.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\workload_classifier.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\workload_sizing.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_runtime_supervision.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T091-runtime-supervision.md`
