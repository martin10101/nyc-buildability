# M5-T076 — Directive-compliance verification (directive-compliance-verifier, read-only)

> Transmission history: returned across five transmissions — the opening span (truncated in
> the clause table at "| Worktree at/past the claim seam | `gi"), then four continuations
> each requested from the exact cut phrase ("**AS-4 engine bound — verified at blob level
> across the entire chain**, not", "The head is on `origin/candidate/D-024-mrl-option-b`
> only,", "**F3 (EVIDENCE LIMITATION, disclosed — not a"). Joined verbatim at each cut
> point (the resend anchor labels are transport artifacts). Saved verbatim by the
> orchestrator (transport entity-decoding only).

All verification is complete. Here is my report.

# M5-T076 — Directive-Compliance Verification (DCV)

**Repo** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` · **Verifier** directive-compliance-verifier (read-only; no writes, no `project_control.py` write verbs, no git/gh write verbs)

## Restamp pre-authorization (answered up front, and already exercised)

**Predicate — blob-level, with broad disjoint-peer tolerance.** This verdict holds at any head where all seven values below are unchanged. Other tasks' files, other material commits, new directive captures, and the addition of my own verification row to `D-084/verification.json` are all tolerated.

| Object | Value that must hold |
|---|---|
| Frozen content identity (`_task_git_identity`) | `1550af011b4fc71fcbfea91517107db14a6faa4fa6ce07d24b3b52b9492ee378` |
| `services/api/app/scenario/lot_geometry_derivation.py` | `9ffc95bfdf276dbc283075e20824381249397bf0` |
| `services/api/app/api/v1/max_envelope_api.py` | `781d8aa037d11b693b471c062c2268ca7e58cd87` |
| `services/api/tests/scenario/test_lot_geometry_derivation.py` | `9efeed36cd0ba09d130c3fba76e1c5ab69d8b2e0` |
| `services/api/tests/api/test_max_envelope_api.py` | `bc858b683440e4fa537a7005e1c4ff67c78f6772` |
| `project-control/reports/M5-T076-producer-report.md` | `fb835fd4723bc3cd69c1199994f652a05fbac050` |
| `services/api/app/scenario/max_envelope.py` (AS-4 engine bound) | `f0abf88479d078d8ec7e88d4c2b1942fd69c040d` |

**Head motion during review, already absorbed.** I began at the pinned head `fc6dc2af94a9288ea5fccb88f4d17c801013b397` (confirmed by `git rev-parse HEAD` at start). Mid-review a disjoint peer commit landed: `1cb14c4e405d16c472cedc3b40f6401af5d0b80c` (the D-086 UI-design-cleanup capture). I re-ran the predicate at `1cb14c4e`: the identity and all six blobs are byte-identical, the only path delta is `docs/UI_DEEP_DIVE_ASSESSMENT.md` + `project-control/directives/D-086-ui-design-cleanup/*` + `directives/index.json`, and `D-084/verification.json` is blob-identical (`7c3a2f00821bebfc5ba2b3db19b9badce420d2cc`) at both. **The verdict is valid at `fc6dc2af` and at `1cb14c4e`.**

## Applicability

`evaluate_task_refs(M5-T076)` returns `ok: true`, `applicable_ids: ["D-084-R001"]`, `cited_ids: ["D-084-R001"]`, `missing_ids: []`, `invalid_refs: []`. **Applicable == cited.** No other D-084 requirement reaches this task: R002 binds `M5-T073`, R003 binds `M5-T074`, neither lists `M5-T076` in `applicability.task_ids`.

**Registry digests reproduced by hand** (LF-normalized, as required on Windows): `source-001.md` → `f95ee41169ff90ae7b96a112448c580048a2ebb0bad247e40322d559ca5e8084`, equal to `manifest.sources[0].content_digest_sha256`. `requirements.json` → `d2baddf50bab601d750e8dc6cbdf9b6b4e91504e90199fb5a1e671b280e85752`, equal to `manifest.requirements_content_digest_sha256`. D-084 has **no amendments** (`manifest.amendments: []`), so the source set is the single original. The M5-T076 bind is logged in `manifest.audit_log` at `2026-09-23T06:05:00+00:00` with a same-commit digest resync. `D-084` is present in `index.json` with `status: active`.

## Per-requirement verdict

### D-084-R001 — **SATISFIED**

R001 is a lane-occupancy obligation with seven named sub-clauses. I verified each against primary evidence, not against the producer report or evidence map.

| Clause | Primary evidence I reproduced | Observed value |
|---|---|---|
| Contracted | `project-control/gates/M5-T076-G0.json` | `result: PASS`, reviewer `orchestrator`, `reviewed_sha 34e44cc5`; commit `34e44cc5` committed `2026-09-23T05:44:05Z` |
| Claimed | `tasks/M5-T076.json` `progress_log[0]`; commit `1dd7647a` | claimed by `backend-engineer` at `05:44:09.856Z`; commit `05:44:10Z` |
| Pushed | `git branch -r --contains 1dd7647a` | on `origin/candidate/D-024-mrl-option-b` |
| In-regime | `tasks/M5-T076.json` | `directive_regime_version: "1.0"`, `directive_regime_entered_at 2026-09-23T05:42:11Z`, `directive_refs` present |
| Worktree at/past the claim seam | `git -C wt-m5t076 rev-parse HEAD` = `815441f6`; `git merge-base --is-ancestor 1dd7647a 815441f6` | descendant confirmed; and the journal's `preflight_pass` is itself the ledger-corroboration proof (a pre-claim ledger copy refuses launch with `ledger_status_mismatch`) |
| Launcher pointed | `C:\SupervisorController\autostart-launch.ps1` lines 40/42/55–57 | `$Repo = C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t076` (full path, passed as both `--repo` and `--worktree`) |
| Fresh run-id | same file line 42; journal `transitions` | `persistent-local-71-m5t076`, distinct from run-70 |
| Stale asks denied in both stores first | journal `queued_asks`; `state_kv` non-approval keys | **zero** unanswered asks at any time; the prior lane-1 asks (run-68, run-69) were all answered `denied: denied by the owner at the CLI` by `05:08:03Z`, i.e. **before** the `05:44:57Z` launch. The only `pending_prompt/*` entries in the second store are from 2026-09-03 (canary/journey MRL one-shots), unrelated |

**Lane-1 run corroborated outside the repo, row by row.** Journal at `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\9aca7075…\supervisor_journal.sqlite3` (opened `mode=ro&immutable=1`), checkout key read from the launcher. Transitions 1738–1742 all carry `run_id persistent-local-71-m5t076`: `run_closed` → `start_command` (`05:44:57.096Z`, `operator_initiated: true`, `limited-auto`) → `preflight_pass` (`05:44:57.269Z`) → `claude_process_started` (`06:04:00.296Z`, containment `job_object`, session `3d0fc6e5…`) → `unsafe_condition` → `PAUSED_RECOVERY` (`06:04:00.358Z`, reason `invalid_checkpoint: checkpoint_field_mismatch: worker-supplied starting_sha='1dd7647a' does not match the controller-authoritative value '1dd7647ad3e40b29…'`).

The autostart log independently agrees: `autostart-20260923-014452.out.txt` (lane-1 prefix; 01:44:52 EDT = 05:44:52Z) records `DISPATCHED in limited-auto mode. cycles=1 final_state=PAUSED_RECOVERY stopped=no_valid_checkpoint`, `elapsed 1144.6s` — roughly 19 minutes of real lane-1 work on this packet.

**Audit-path discipline verified, not assumed.** `audit.jsonl` holds 2080 entries; I walked the whole chain and found **zero** `prev_digest` breaks; `audit.jsonl.head.json` `sequence 2080` and `digest f4d34220…` both match the last entry exactly; the last event is `approval_owner_denied` at `06:05:16.561Z`. Thirty entries carry this run's id (seq 2067–2080 inspected). The newest `*.forked-evidence-*` archive is dated `20260919`, so **no audit-appending CLI verb raced this run** — the chain was never forked during T076.

**Gated-process clause verified at the frozen identity.** Required gates `G0,G2,G3,G4`, all `PASS`:

- `G3` — reviewer `code-reviewer`, `role independent_review`, `content_manifest_sha256 1550af01…`, `reviewed_sha ccff99e9`, report `M5-T076-G3-delta.md`. Its `history[]` preserves the superseded `FAIL` at `03:02:34Z` (report `M5-T076-G3.md`), so the FAIL was superseded by a PASS at the corrected head rather than overwritten.
- `G4` — reviewer `qa-engineer`, `role independent_review`, `content_manifest_sha256 1550af01…`, `reviewed_sha 8ea1c8cc`.
- The live identity, `reports/M5-T076.json:content_manifest_sha256`, and both independent gate stamps are **the same value** `1550af011b4fc71fcbfea91517107db14a6faa4fa6ce07d24b3b52b9492ee378`. The submission record's `reviewed_sha` is `50bf4448`; all five allowed-path blobs are byte-identical from `50bf4448` through `fc6dc2af` and on to `1cb14c4e`, so **no material edit occurred after the re-freeze**.
- Lifecycle transitions are all present in `progress_log`: claimed (20) → claimed (95) → `rework` (70, `2026-09-24T03:02:45Z`) → `in_progress` (85, `03:23:30Z`) → submit (`03:23:42Z`, `awaiting_gate`). No illegal `rework→awaiting_gate` or `awaiting_gate→in_progress` hop.

**AS-4 engine bound — verified at blob level across the entire chain**, not by diff absence. `services/api/app/scenario/max_envelope.py` is `f0abf88479d078d8ec7e88d4c2b1942fd69c040d` at the contract seam `34e44cc5`, and at `b8dc1044`, `eed2350a`, `50bf4448`, `ccff99e9`, `8ea1c8cc`, `fc6dc2af`, and `1cb14c4e`. Byte-untouched throughout, including through the rework.

**Scope verified.** Both material commits touch exactly the five allowed paths (`b8dc1044`: 5 files, +909/−11; `eed2350a`: 5 files, +745/−61). `50bf4448` touches the producer report (inside allowed paths — and the re-freeze happened *after* it) plus the evidence map (outside allowed paths: the `[ORCH-CORRECTED]` fix, which moves no material identity). No dependency manifest is touched by the T076 material; every new import in the two production files is stdlib or first-party (`app.connectors.bbl`, `app.connectors.mappluto_geometry_arcgis`, `logging`, `enum`, `dataclasses`, `collections.abc`).

**Harness and behavior I re-ran myself**, never inherited from the producer or the gates:

- `python -m ruff check .` from `services/api` → `All checks passed!`, exit 0.
- `python -m pytest tests/scenario/test_lot_geometry_derivation.py tests/api/test_max_envelope_api.py -q` → **55 passed**.
- `python tools/modularity_check.py --check` → exit 0, failures 0.
- The eight load-bearing named tests exist and pass under `-k` selection (`recorded_single_lot_derives_but_is_honestly_unfittable`, `derived_path_yields_fitted_candidate`, `with_segments_is_byte_identical…`, `malformed_segments_refuse_identically…`, `…provider_raises_unexpectedly`): 8 passed, 29 deselected.
- **Display-connector isolation proven directly** by parsing the module with `ast`: imports are exactly `__future__`, `app.connectors.bbl`, `app.connectors.mappluto_geometry_arcgis`, `collections.abc`, `dataclasses`, `enum`, `logging`. `mappluto_lot_outline` is absent.
- **Route genuinely unmounted**: `from app.main import app` → no `max`/`envelope` path among the 19 real routes.
- **AS-3 fail-closed reproduced end to end in-process.** I mounted the router on a fresh `FastAPI()`, injected a provider raising `MapPlutoGeometryConnectorError("upstream down", correlation_id="probe-cid")`, and POSTed a geometry-free body with `lot.bbl = "1008350041"`. Result: `200`, `derived_lot_geometry.outcome == "connector_fault"`, `candidate == null`, `candidate_placement.status == "lot_geometry_unsupported"`, with `lot_rectangle`, `footprint`, `contained` all `null` and the detail carrying both halves: the engine's own "no lot-line geometry was supplied… never a fixed-anchor schematic" followed by "| server-side lot-geometry derivation (connector_fault): the official MapPLUTO geometry source could not be reached or returned an error (upstream_error); no server-side lot geometry was derived". No fabricated rectangle, no silent fallback. I also read `max_envelope_api.py:162-180` and `:350-384` directly and confirmed the F1 guard wraps both provider resolution and the threadpool hop, and that `_should_derive_lot_geometry` derives only on absent / `None` / empty-list.

**`validate_directive_compliance.py --check` → exit 0.** Run twice; the second run captured the **direct** exit code without a pipe (`VALIDATOR_DIRECT_EXIT=0`), per the known `| tail` exit-swallowing trap. The tool is quiet-on-success, so empty output plus exit 0 is the PASS.

## Prohibited-action sweep — clean

Task status `awaiting_gate`, progress 95, no `accepted_at` field, absent from `state.json:accepted_tasks`. `D-084/verification.json` holds exactly one row (M5-T072) and **no row for M5-T076** — the string does not occur in the file, and its blob `7c3a2f00821bebfc5ba2b3db19b9badce420d2cc` is identical at `fc6dc2af` and `1cb14c4e`. M5-T076 appears inside D-084 only in `manifest.json` (the applicability-bind audit entry) and `requirements.json` (`applicability.task_ids`) — the legitimate binds, not verification. The head is on `origin/candidate/D-024-mrl-option-b` only, **not on `main`**. PR #241 is `OPEN`, `mergedAt: null`, last updated `2026-08-20T06:49:35Z` — untouched. No PR exists for T076 (highest is #242). No file under `project-control/blockers/` contains `M5-T076`. Nothing deployed (route unmounted in the real app), nothing installed or purchased (no dependency manifest touched by the T076 material), nothing closed.

## Ruling 1 — rework provenance does not defeat R001

R001 obliges the orchestrator to *feed and launch* lane 1 on a contracted, claimed, in-regime packet under the normal gated process. It does not oblige every byte of the packet to be produced by the loop worker. The original unit **was** loop-produced: the journal and autostart log both show run `persistent-local-71-m5t076` fresh, launched on this packet, doing ~19 minutes of real work (`elapsed 1144.6s`) before closing on the `checkpoint_field_mismatch`. The rework followed a **G3 FAIL**, which is itself part of the normal gated process; the journal shows no lane-1 run after `06:04:00Z` on 09-23, so the 09-24 rework was demonstrably outside the loop. That deviation is disclosed in the producer report's Rework section (base `672c5743`, the G3-FAIL seam) and its `[ORCH-HARVEST] Rework harvest` section, and in the ledger progress log ("Producer rework dispatched"; "producer commit 93a2a667 cherry-picked to eed2350a"). **R001 SATISFIED.**

## Ruling 2 — reviewer independence holds

Packet `producer_agent` is `backend-engineer`. G3 was recorded by `code-reviewer`, G4 by `qa-engineer`; both are in `reviewer_agents: ["code-reviewer","qa-engineer","directive-compliance-verifier"]`, neither equals the producer, and both carry `role: independent_review` — what `accept()` enforces for `INDEPENDENT_GATES = {G1,G3,G4,G5,G6}`. G2 is a `self_check` recorded by `orchestrator`, correct by design. I produced none of the artifacts I judged.

## Ruling 3 — the accept-sweep rider list is complete

I checked every finding in all three reports against your list. Riders: G3-delta null-path asymmetry ("One new concern introduced by the rework"); G4 F1 (truthy-only malformed parametrize — half-net on the very defect class that caused the FAIL); G4 F2 (`BBL_UNRESOLVABLE` detail unasserted); G4 F3 (at-cap `>=` boundary untested); G4 F4 (non-scalar `lot.bbl` yields no `derived_lot_geometry` block); G3 F6 (web-client `lot.bbl` gap at `max-envelope-api.ts:50-53` / `:542`); G3 F8 (no request-scoped budget on the new upstream call, to be decided at the DB-045(b)/B-001 mount seam). Nothing is missing — G3 F1–F5 and F7 were all fixed and individually re-verified in the delta, and the G3 "log tag" item is explicitly recorded as a non-finding. One addition I recommend, at F5 below.

## Findings

**F1 (INFO, non-blocking, outside the packet).** Handoff commit `e8c921f2` calls the lane-1 run "closed COMPLETE-CLASS", but the journal records `PAUSED_RECOVERY` via `unsafe_condition` / `no_valid_checkpoint`. The packet's own record is honest — the evidence map says "closed PAUSED_RECOVERY unsafe_condition with the unit DELIVERED uncommitted" and commit `b8dc1044` says "unsafe_condition close harvested". Only the handoff prose is loose; "COMPLETE-CLASS" reads as a controller state that did not occur.

**F2 (PROCESS NOTE, non-blocking).** The G2 self-check sits at `reviewed_sha 490c3413`, `content_manifest_sha256 cdf2fa33f8ed…` — the **pre-rework** material (its body cites "40 passed"). No self-check record exists at the frozen identity `1550af01…`. CLI-legal: `accept()` compares only the submission report's manifest to the live identity and enforces role/independence for `{G1,G3,G4,G5,G6}`; it does not compare each gate record's manifest. Substance covered three ways — the `[ORCH-HARVEST]` rework verification at `50bf4448` (ruff clean, 55 passed, AS-4 held), both independent gates re-running the commands at the corrected head, and my own reruns. Recorded so the gap is visible rather than silent.

**F3 (EVIDENCE LIMITATION, disclosed — not a requirement gap).** `python tools/test_directive_compliance.py` **did not complete** in this environment and I do not claim it passed. I measured the cost: a 2-test subset took **909 seconds** (`Ran 2 tests in 909.192s ... OK`) — roughly 7.6 minutes per test against the grown registry, so 129 tests is on the order of 16 hours. The two that ran are `RequirementsBodyDigestTest` (including `test_missing_content_digest_flagged`), the digest-integrity class most relevant to my own digest verification, and both passed. A longer partial run reached `test_c14_s1_omitted_requirement` with every observed test `ok` and zero failures. The authoritative registry-integrity check, `validate_directive_compliance.py --check`, completed with a **direct exit code of 0**. The other two harness scripts are green: `test_project_control.py` → "OK: all 23 project-control test groups passed"; `test_directive_reminder.py` → "Ran 12 tests ... OK". R001 is verifiable on the evidence already cited; this is an environmental cost, not missing compliance evidence.

**F4 (INFO, wording).** The evidence map says "2 stale asks denied from piped JSON". Those asks (`ask_d8f97ef8…`, `ask_f3db341d…`) were created **during** the run at `05:59:30.685Z` / `05:59:32.858Z` and denied at `06:05:15.483Z` / `06:05:16.546Z` — post-run cleanup, not the pre-launch stale-ask sweep R001 names. The pre-launch state was independently clean (zero unanswered at `05:44:57Z`), so both facts are true; the word "stale" merges two different events. Cosmetic.

**F5 (RIDER CANDIDATE, producer-disclosed, not on your list).** The producer's "Limitations and honest residue" flags that `GEOMETRY_OVER_CAP` is a **new value in the `derived_lot_geometry.outcome` vocabulary** with no consumer today (route unmounted, web client sends no `lot.bbl`), and that a future consumer must treat it as distinct from `invalid_geometry`. I confirmed the value is emitted by the shipped module (`lot_geometry_derivation.py`, `_RING_OVER_CAP` branch). Since G3 F6 already routes the web-client `lot.bbl` gap to the sweep and the first consumer will be built at that same seam, carry the vocabulary duty alongside it so the two are not closed independently.

**F6 (RETURN ITEM from G4, needs an orchestrator action).** The G4 reviewer could not write its agent-memory entry (`Write` blocked for identity `t076-g4`, including under `.claude/agent-memory/qa-engineer/`, which its dispatch prompt had permitted) and asked that its lesson be persisted on its behalf: *when a guard fix is the headline correction, run two mutants — the literal pre-fix code from git AND the idiomatic simplification a future maintainer would plausibly write — because a truthy-only malformed-value parametrization cannot discriminate against `if container.get(key):`.* Transferable, and lost unless you record it. The same restriction applies to me; I have written nothing.

## Conclusion

One requirement is applicable to M5-T076 and it is satisfied on primary evidence I reproduced myself: the lane-1 packet was contracted, claimed, pushed, in-regime, and launched on a fresh run-id against a worktree at the claim seam with both ask stores clean; the run is corroborated by the supervisor journal, the autostart log, and an unbroken 2080-entry audit chain outside the repo; the frozen identity `1550af01…` is byte-stable across submit and both independent gates; the AS-4 engine bound `f0abf884…` held through the rework at blob level; and the fail-closed honesty property reproduces end to end. Six findings recorded, none blocking. The only item I could not complete is `test_directive_compliance.py`, reported as a measured environmental limitation rather than a pass.

**DCV VERDICT: PASS 1/1**

END-OF-REPORT
