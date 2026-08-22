# M0-T080 producer report — real session continuity, the full turnover seam, owner-approved model routing

**Task:** M0-T080 (D-023 item 2; owner directive D-023-R013)
**Branch / worktree:** `task/M0-T080-session-model-turnover` in `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t080`
**Base:** `73f5b85` (includes the merged M0-T079 bounded-mode work)
**Producer:** M0-T080 producer agent. Gates G0/G2/G3/G5 are the reviewers' to run; this report is evidence, not a verdict.
**Platform of record:** Windows 11, Python 3.11.9.

---

## 1. AD-093 qualifying evidence (supervisor-freeze rule §2/§3)

Four qualifying items. The first three are **reproduced defects**; the fourth is a requirement stated verbatim in an owner directive. Each was verified against the pre-change tree before anything was written.

### 1.1 A reproduced defect — the invented "new session id"

`rotation.py:833-838` (pre-change) minted a supervisor-internal UUID and the loop stored it where a PROVIDER session identity belongs:

```python
def new_session_id(previous: str = "") -> str:
    """A brand-new session id (S11.3). Never reuses or derives from the old one."""
    candidate = f"sup-{uuid.uuid4().hex}"
```

Three consequences, each confirmed by a repository-wide search of the pre-change tree:

1. **`--resume` was never used in production.** `RunnerConfig.resume_session_id` exists (`claude_runner.py:319`) and `build_argv` knows how to emit `--resume <session-id>` (`claude_runner.py:358-365`). A search for writers found exactly one, and it is not production:

   ```
   $ grep -rn "resume_session_id" tools/agent_supervisor/
   claude_runner.py:319:    resume_session_id: str = ""
   claude_runner.py:358:    if config.resume_session_id:
   claude_runner.py:365:        argv += ["--resume", config.resume_session_id]
   cli.py:702:  build_claude_argv(RunnerConfig(executable="claude", resume_session_id="s-1"))
   ```

   `cli.py:702` is the `doctor` capability probe. So a completed rotation launched a **fresh, UNRESUMED** session while recording rotation success.

2. **The READY gate could never match.** `RotationLedger.assert_ready_checkpoint` compares `checkpoint.claude_session_id` — a PROVIDER id the worker reports — against the invented `sup-...` id.

3. **Nothing durable carried the real id.** `loop.py:1717-1719` read the real provider session id off the stream into `self._current_session_id`, and the three rotation seams then OVERWROTE that same attribute with the invented id (`loop.py:1307-1313`, `:1421-1427`, `:1559-1566`). No later act could name, resume, or archive the session that did the work.

### 1.2 A reproduced defect — the loop bypassed its own S11.3 protocol

`rotation.py` already provided the complete safe-rotation protocol. The live loop used almost none of it. All three seams wrote the smaller, explicitly non-S11.3 snapshot from `_refresh_session_handoff` — whose own docstring said so, verbatim:

> "It is NOT the full S11.3 Codex-verified handoff (that needs a live worker + reviewer and is out of fake-harness scope); it is the refresh step named by D-004"

— and then called `RotationLedger.complete_rotation` DIRECTLY. A production-caller search of the pre-change tree confirms the gap:

| `rotation.py` surface | Production callers before M0-T080 |
|---|---|
| `assert_safe_to_rotate` | **none** |
| `Handoff` / `validate_handoff` | **none** (only `cli export-handoff`, read-only) |
| `verify_handoff` | **none** |
| `RotationLedger.store_verified_handoff` | **none** |
| `assert_ready_checkpoint` | **none** |
| `RotationLedger.complete_rotation` | 3 (the three seams, called directly) |

So a production rotation never checked whether the moment was safe, never built nine of the fourteen required handoff fields, never verified a handoff, never stored a verified one, never gated on READY, and never checked afterwards that the successor was on the expected task, branch, HEAD, or model.

**One correction to this table (review U4).** Five of these six surfaces were given a production caller. `assert_ready_checkpoint` was **not**, and the first submission's claim that it was "fixed" was wrong. The live READY gate is a NEW implementation (`turnover_seam.SeamTurnover.require_ready`) with different — and correct — semantics: `assert_ready_checkpoint` demanded `claude_session_id == expected_session_id`, which is unsatisfiable on a reorientation because the successor's provider session id does not exist until the successor reports it. It stayed dead, disagreed with the live gate, and its new docstring falsely named `SeamTurnover` as its caller. It has been **REMOVED** (`rotation.py:723-741`, replaced by a comment recording why), along with the three tests that only exercised it; a guard test now asserts the duplicate cannot return.

### 1.3 A reproduced defect — model ids decided in SOURCE, not in owner config

Three sites chose models from literals rather than from owner-approved protected configuration:

- `config.py:82-84` — `DEFAULT_ORCHESTRATOR_MODEL_CHAIN = ("claude-fable-5", "claude-opus-4-8", "claude-opus-4-7")`, used whenever `[model_chain]` was absent. A controller config that approved nothing still selected three ids the owner had never written down. `ModelChain.__post_init__` additionally *refused* an empty chain, which forced a non-empty default to exist somewhere.
- `turnover_controller.py:54-55` — `ALLOWED_SUCCESSOR_MODEL_ID = "claude-opus-4-8"`, the successor of every turnover. (The task packet cites `turnover_adapters.py:32-33`; that is the module docstring restating the pin. The constant is **defined** at `turnover_controller.py:54` and imported by the adapters — corrected here for the reviewer's file map.)
- `cli.py:2547` and `cli.py:2665` — `current_model` defaulted to the literal `"claude-fable-5"` at both watchdog call sites.

### 1.4 A requirement stated verbatim in an owner directive

**D-023-R013:** only owner-approved, live-probed model IDs from protected config; NO silent or unlisted substitution of any kind (code default, settings fallback, Remote Control switch, provider convenience); exhaustion stops safely.

---

## 2. What changed — file:line map

### 2.1 New modules

| File | SLOC | Responsibility |
|---|---:|---|
| `tools/agent_supervisor/session_continuity.py` | 266 | The provider session identity, and the resume-vs-reorientation decision. |
| `tools/agent_supervisor/turnover_seam.py` | 452 | The full S11.3 turnover: safe seam, handoff, verify, persist, READY gate, post-launch check. |
| `tools/agent_supervisor/approved_models.py` | 332 | The owner-approved list, the live launch probe seam, the durable probe ledger, the router. |
| `tools/agent_supervisor/loop_turnover.py` | 275 | How the loop drives that seam (extracted from `loop.py`; modularity). |
| `tools/agent_supervisor/turnover_wiring.py` | 272 | How the CLI assembles the R595 actuation channels (extracted from `cli.py`; modularity). |
| `tools/agent_supervisor/handoff.py` | 216 | The S11.3 handoff schema + verification (split from `rotation.py`; modularity). |

New test module: `tools/test_agent_supervisor_turnover_live_seam.py` (67 tests).

### 2.2 Deliverable 1 — real session continuity

| Location | What |
|---|---|
| `claude_runner.py:1199-1207` | The provider session id is captured from **every** stream event, FIRST-WINS. It was previously read only from `system`/`init`, so a stream that opened without one — notably a RESUMED session — yielded an empty id. |
| `claude_runner.py:1204` | Two different ids on one stream set `session_id_conflict`; an ambiguous identity never authorizes a resume. |
| `claude_runner.py:915` | `RunResult.session_id_conflict`, the new honest field. |
| `claude_runner.py:1038` | **`ClaudeRunner.with_resume`** — the missing actuation, shaped exactly like `with_model`. Refuses an id carrying the `sup-` internal prefix outright. |
| `session_continuity.py:51` | `PROVIDER_SESSION_KEY` — the durable record of the last provider session and the model it ran on. |
| `session_continuity.py:147/166` | `record_provider_session` / `recorded_provider_session`. An EMPTY id is never recorded and never overwrites a good one. |
| `session_continuity.py:60-72` | The CLOSED list of impossibility reasons: `no_provider_session_recorded`, `cross_model`, `resume_capability_unverified`, `provider_session_expired`, `context_shedding_rotation`. |
| `session_continuity.py:236` | `decide_continuity` — collects **every** applicable reason, not just the first. |
| `session_continuity.py:180-234` | `ContinuityDecision` makes the dishonest states UNCONSTRUCTIBLE: a resume with no id, and a reorientation with no reason, both raise. |
| `session_continuity.py:303` | `reorientation_prompt` — the FULL exported handoff as the successor's first prompt, not a digest or a pointer. |
| `rotation.py:651` | `new_session_id` → **`new_rotation_record_key`**, prefix `sup-rot-`, documented as supervisor-internal bookkeeping. The old name is REMOVED, not aliased. |
| `rotation.py:750` | `complete_rotation` now carries BOTH identities plus `continuity_mode`, refuses `identity_conflated`, refuses a resume with no id, refuses an unexplained reorientation, and archives the outgoing session **only** on a reorientation. |
| `loop.py:945` | The loop keeps `_provider_session_id` and `_rotation_record_key` as SEPARATE attributes, the provider one restored from durable state on resume. |
| `loop.py:1771-1786` | The provider id is captured and persisted at unit completion; a conflict DROPS it and audits `provider_session_ambiguous`. |
| `loop_turnover.py:127` | `actuate_resume` — a runner that cannot be rebound is a REFUSAL (`resume_actuation_unavailable`), never a recorded resume. |

### 2.3 Deliverable 2 — the full turnover at the three loop seams

| Location | What |
|---|---|
| `turnover_seam.py:75/106` | `safety_state_from_run` / `assert_safe_seam` — pending effects, open asks, and an unknown SHA / worktree / stage are all unsafe moments. The judgement is delegated to `rotation.assert_safe_to_rotate`. |
| `turnover_seam.py:127/168` | `SeamFacts` + `build_handoff` — the full fourteen-field S11.3 handoff, built from the task authority, the recorded HEAD, and the last VALID checkpoint. |
| `turnover_seam.py:160` | `STRUCTURAL_FORBIDDEN_SCOPE` — the prohibitions true of every unit, so `forbidden_scope` is never empty just because a packet listed no paths. |
| `turnover_seam.py:216/305` | `deterministic_verdict` / `verify` — a live review-model verifier when one is wired; otherwise a **completeness + authority-consistency** gate (see §3.3 — corrected per review U3; it is NOT 14-field independent re-derivation). `model_used` distinguishes the two deterministic arms: `deterministic:supervisor-consistency` and, when a `FactSource` is wired, `deterministic:supervisor-independent-rederivation`. |
| `turnover_seam.py:66-72/313-341` | `FactSource` — the injected independent re-derivation seam (U3 arm (a)). When wired its values are authoritative and a divergence REFUSES the rotation; a source that raises refuses rather than silently downgrading to the weaker check. |
| `turnover_seam.py:338-...` | `SeamTurnover.execute` — safe seam → handoff → verify → **persist** → rotate → arm READY, in that order, so a refusal leaves the run exactly where it was. |
| `turnover_seam.py:...` | `require_ready` — status must be READY; a READY from the ARCHIVED session, or from a session other than the one a resume commanded, is refused. |
| `turnover_seam.py:...` | `verify_post_launch` — compares the successor's reported task, branch, worktree, starting SHA, and **model** to a `SuccessorExpectation` written down BEFORE it ran. |
| `loop_turnover.py:153-160`, `:176-188` | The expectation is read from the DURABLE armed gate before `require_ready` clears it, so a crash between the rotation and the successor's first checkpoint cannot skip the identity check (`_successor_expectation` is in-memory; the gate record is not). |
| `loop.py:1297-1319` | Thin delegating methods; the mechanics live in `loop_turnover.py`. |
| `loop.py:1321`, `:1474`, `:1583` | The three seams (`_rotate_at_seam`, `_switch_at_seam`, `_return_to_pinned`) now call `_full_turnover`; the three direct `complete_rotation` calls are gone. |
| `loop_turnover.py:195` | `turnover_refused` — an unsafe seam, an unbuildable handoff, or an unverified handoff PAUSES and queues an owner ask; the rotation stays pending, never half-applied. |
| `loop.py:2010` | The post-rotation gates run after a valid checkpoint and **before** evidence collection, review, or any forward. |
| `loop.py:2786`, `:2866` | The reorientation prompt is prepended to the next unit's prompt at both seam sites, so the handoff actually reaches the successor. |

### 2.4 Deliverable 3 — owner-approved, live-probed model routing

| Location | What |
|---|---|
| `config.py:99` | `[approved_models] models` is the canonical section; `[model_chain] orchestrator_preference` remains the accepted legacy spelling of the same list. |
| `config.py:264` | `ModelChain.entries` defaults to `()` and an empty chain is now LEGAL to construct. The refusal MOVED to the point of selection, where it can be typed and actionable. |
| `config.py:308` | `ControllerConfig.approved_models` — one object every selection act asks, carrying the config path so a refusal names the file to populate. |
| `config.py:394/428` | Both spellings read; both present with DIFFERENT contents is `approved_models_conflict`, refused rather than resolved by a precedence rule. |
| `config.py:63-70` | `approved_models` and `model_chain` added to `_CONTROLLER_ONLY_KEYS`: a runtime file can never name them. |
| `approved_models.py:102-181` | `ApprovedModels` — exact-string membership, `assert_populated`, `assert_listed`. |
| `approved_models.py:184-201` | `ProbeOutcome` + `LiveLaunchProbe`, the injected exact-id live launch probe seam. |
| `approved_models.py:205-306` | `ProbeRecord` / `ProbeLedger` — durable, bound to config identity AND CLI version; a probe from another config or CLI reads as NO probe. |
| `approved_models.py:327-431` | `ModelRouter.select` / `next_after` — LISTED, then PROBED, in that order. No probe seam ⇒ `model_probe_seam_missing`. Chain spent ⇒ `approved_chain_exhausted`. |
| `approved_models.py:64-72` | Reason code → refusal outcome: empty list and spent chain ⇒ `halted`; unlisted / unprobed / failed probe ⇒ `unsafe`. The 10 and 11 those outcomes carry are `Refusal.exit_code` PROPERTIES (`refusals.EXIT_CODES`); no CLI surface returns them for these refusals today - `orchestrator-watchdog` reports the safe stop in its payload and returns 0, and the `start` path maps its own outcome. Corrected per M0-T080 review U15. |
| `turnover_controller.py:68-110` | `ALLOWED_SUCCESSOR_MODEL_ID` **removed**. `ApprovedSuccessor` + the injected, REQUIRED `SuccessorResolver` replace it. `ALLOWED_SUCCESSOR_EFFORT` is kept and documented (see §3.4). |
| `turnover_controller.py` | New `TurnoverStatus.NO_APPROVED_SUCCESSOR` — a safe stop that launches nothing and does NOT consume the dedup key. |
| `turnover_adapters.py` | The launcher builds from `LaunchRequest.model_id`; a request naming no model is refused, since there is nothing to default to. |
| `turnover_wiring.py:98/124` | `approved_model_router` / `approved_successor_resolver` — the production wiring, bound to this config's digest and this CLI's identity. |
| `cli.py` (watchdog) | `current_model` is now REQUIRED with no default; when omitted it is read from the run's recorded provider session, and when that is unknown the watchdog REFUSES. |
| `cli.py` `--config` on `orchestrator-watchdog` | Names the config whose approved list the successor is chosen from. |
| `model_change_ipc.py:502-528` | The IPC's Gate 3 gains an independent approved-list check for the `claude` provider. Gate 1 (process ancestry) is untouched and still runs FIRST. |
| `cli.py` doctor | `approved_models` and `model_launch_probes` checks report the list and the probe evidence as data. |

**What the approved list does NOT govern (G5 I4 / G4 §3 — documented per the review's owner-decision item).** Two paths reach a model without consulting the probe ledger, and neither is misrepresented as covered:

1. **The run's INITIAL model pin.** It is admitted by `[claude] allowed_models` via `model_selection.toml`, with **no launch-probe requirement**. G4 ruled this is *not* an R013 violation — the initial pin is neither a turnover, a fallback, nor a substitution; it is the model the owner launched the run on, from an owner-authored list. Every LATER selection is held to `[approved_models]` + a recorded probe.
2. **The orchestrator quota-chain switch** (`loop._switch_at_seam`) probes each candidate by an ACTUAL LAUNCH at the seam, but neither reads nor writes `ProbeLedger`, so those probes leave no record in what `doctor` reports.

Both are confined to owner-authored lists; only the ledger is bypassed. This is now stated in three places a reader will actually hit: the `approved_models` and `model_launch_probes` doctor checks (`approved_models.py:484-538`) and `config.example.toml`'s `[approved_models]` comment. **The open question — should the initial pin ALSO require the approved list plus a probe? — is an OWNER DECISION and is deliberately left open here**; it is bundled into the single final owner checkpoint (D-023-R034), and the directive verifier rules on whether R013 reaches the pin. **No pin admission logic was changed by this correction round.**

### 2.5 Deliverable 4 — the stale note

`remote_approvals.py:307-309` — the wording that said limited-auto "is not implemented in this build" now says it is implemented (M0-T079) and OFF by default. One record's `note` string; nothing else in that file changed.

---

## 3. Design decisions

### 3.1 Two identities, and why the old name had to go

The directive permits the invented UUID to survive "ONLY as a supervisor-internal rotation-record key, clearly renamed/documented so it can never be mistaken for a provider session id". A lingering `new_session_id` alias would defeat exactly that, so the old name is **removed**, the prefix changed to `sup-rot-`, and three independent guards added: `complete_rotation` refuses `identity_conflated` when the two values are equal, `ClaudeRunner.with_resume` refuses any `sup-`-prefixed id outright, and a test asserts `rotation.new_session_id` no longer exists.

### 3.2 When a resume is possible — and the honest consequence on this build

`decide_continuity` applies a CLOSED list of impossibility reasons. One deserves the reviewer's attention: **`context_shedding_rotation`**. Resuming the same provider session after a context-pressure rotation would carry the very context the rotation exists to drop straight back into the successor, and S11.3 says the required behaviour is a brand-new explicitly identified session. That is a policy decision, listed explicitly in `CONTEXT_SHEDDING_REASONS` rather than inferred, so adding a rotation reason is a deliberate decision about continuity.

**The honest consequence:** in the assembled loop today, *every* rotation reason is either context-shedding (`context_threshold` and the S11.1 family) or cross-model (`model_downgrade`, the chain switch, the return-to-pin). So the production continuity decision is **always `reorientation`**, and it is recorded as such with its reason — which is precisely the point: the supervisor no longer pretends. Additionally, `--resume` is not behaviourally verified on this binary, so `resume_capability_unverified` would independently forbid it.

The resume path is nevertheless real, wired, and proved end to end: `decide_continuity` returns it, `SeamTurnover.execute` records it without archiving, `loop_turnover.actuate_resume` rebinds the runner, and `build_argv` emits `--resume <provider id>`. The loop-level test drives the real `_full_turnover` with reason `session_relaunch` — a same-model, non-shedding reason. **No trigger in the assembled loop produces that reason today.** I did not add one: inventing a rotation trigger to make a path fire would be a speculative supervisor feature (supervisor-freeze §1). Flagged in §8 as a judgment call.

### 3.3 What the deterministic verification actually proves (corrected — review U3)

**The first submission overstated this, and the correction is the honest scope.** The original text said the supervisor "re-derives every load-bearing field". It does not, and it could not have: `execute` builds the handoff FROM `facts` and then verified it against that same object, so no production divergence was reachable, and only 6 of the 14 fields were compared at all. G3 I-1 / G5 I3 / G4 F3 were right.

**What it is now, stated exactly** (and stated in the verdict record itself, under `scope`, so no reader has to infer it):

1. **Completeness** over all fourteen S11.3 fields — enforced by `rotation.validate_handoff`, which `verify_handoff` calls first. That part was always real.
2. **Authority-consistency** for the six fields the SUPERVISOR owns: task/stage, branch, worktree, exact next action, `authoritative_shas.HEAD`, and the structural prohibitions. This catches a handoff that took any of them from worker-supplied checkpoint text instead of from the task authority.
3. **Not re-derived at all:** the other eight fields (completed work, changed files, tests/CI, PR state, reviews, blockers, owner gates, evidence digests). Those originate in the worker's checkpoint and the supervisor holds no second copy, so comparing them here would compare a value to itself. Claiming otherwise was the defect.

**Which arm was taken, and why.** Both, honestly labelled. Arm (a) — the independent re-derivation — is IMPLEMENTED as the injected `FactSource` seam: when wired, values re-read from the world are authoritative, a divergence refuses the rotation, and the record says `deterministic:supervisor-independent-rederivation`. A source that raises is a refusal, not a downgrade. Three tests prove it can actually refuse, that an agreeing source is labelled as the stronger check, and that a raising source stops the rotation.

Production does **not** wire one, and that is arm (b) with the reason the correction asked for: the only genuinely independent source is repository I/O — `git rev-parse`, the packet on disk — executed INSIDE the rotation seam. Adding subprocess git to a seam that currently performs none is new behaviour with its own failure modes (a git that is slow, absent, or answering about the wrong worktree would newly be able to block a rotation), and the freeze lane authorises defect repair, not that. So the seam exists, is required when wired, and the label and the `scope` block say precisely what ran. `verified_by_model` can no longer imply an independent check: `deterministic:supervisor-consistency` says on its face that it is not one.

A test tampers with one field and asserts the verifier catches it, and asserts the untampered handoff passes — so neither arm is always-pass or always-fail.

### 3.4 Why `ALLOWED_SUCCESSOR_EFFORT` stays a constant

The directive says to remove "the pinned successor constant", meaning the MODEL pin. Effort is a different kind of thing: D-004-R159 permanently prohibits an effort key in every configuration file, and `config.assert_no_effort_key` refuses any file that carries one at any depth. Owner-approved protected config is therefore structurally unable to express an effort, so moving the effort there is impossible by design. It remains `ALLOWED_SUCCESSOR_EFFORT = "xhigh"`, unchanged in name and value, carried as invocation metadata (every `--effort` argv form is hard-denied by `process.assert_argv_safe`), and documented in place.

### 3.5 Two config spellings for one approved list

`[approved_models] models` is canonical and `[model_chain] orchestrator_preference` is retained as the legacy spelling of the same list. The alternative — replacing the section outright — would have silently broken every existing controller config and `harden_controller_config.ps1`. Two spellings is a real (small) smell, mitigated structurally: they are read by one function into one field, and naming BOTH with different contents is `approved_models_conflict`, refused rather than resolved by a precedence rule, because guessing which the owner meant is guessing which models are approved.

### 3.6 Scoping the IPC approved-list gate to `claude`

The approved list IS the Claude session/model chain. Requiring a Codex model change to appear in it would refuse every legitimate Codex change. The Codex provider therefore keeps `codex.allowed_models`, its own owner-authored list, unchanged; the new gate applies to `claude` only, and is documented as such in `assert_allowlisted`. A config that does not expose an approved surface at all is `approved_models_unavailable` — refused, never skipped. Gate 1 (process ancestry) is untouched and a test proves a worker-originated caller is denied `worker_origin_denied` **before** the approved-list check is reachable.

### 3.7 Modularity

`cli.py`, `loop.py`, and `rotation.py` are grandfathered oversized files that may not grow materially (`baseline + max(50, 10%)`). After the first implementation pass all three failed:

| File | Baseline | Limit | After pass 1 | Final |
|---|---:|---:|---:|---:|
| `cli.py` | 2685 | 2953 | 3101 | **2898** |
| `loop.py` | 1899 | 2088 | 2290 | **2080** |
| `rotation.py` | 746 | 820 | 834 | **623** |

Rather than request an owner exception, the growth was **extracted** into the four focused modules in §2.1 (`loop_turnover.py`, `turnover_wiring.py`, `handoff.py`, plus the three genuinely new domain modules). Every split preserves the public import surface: `rotation.Handoff`, `rotation.verify_handoff`, `rotation.RotationError` and friends are re-exported facades; `cli.run_orchestrator_watchdog` and the pre-split private helper names (`cli._build_worker_actuation_channel` and peers) are preserved as aliases. `python tools/modularity_check.py --check` → **`selected 280 files; failures 0; warnings 5`**, all five warnings pre-existing.

Note for the reviewer: `modularity_check` selects via `git ls-files`, so the six **untracked** new modules are not yet in its census. Each was measured directly (§2.1); the largest, `turnover_seam.py` at 452, is under the 600 warn line.

---

## 4. Acceptance scenarios

Per `docs/ACCEPTANCE_SCENARIO_STANDARD.md`. Execution method for all: `python -m pytest <module> -q` on Windows, Python 3.11.9. Cleanup for all: `tempfile.TemporaryDirectory` via `addCleanup`; nothing outside the temp directory is written.

**Evidence label (D-023-R021):** every scenario below is UNIT / FAKE-RUNNER proof. **No live Claude or Codex provider is contacted anywhere.** The exact-id live launch probe seam is exercised by injected fakes only. AS-1/AS-2 spawn a real OS process — a local Python script, not a provider.

| ID | Requirement | Preconditions | Exact input | Expected output | Invariant | Evidence |
|---|---|---|---|---|---|---|
| **AS-1** *(primary success — the §1.1 defect)* | D-023-R013 | Fake CLI emitting stream-json | `run_unit` against three stream shapes | init-only ⇒ id read; **result-only ⇒ id read** (was empty before); two ids ⇒ FIRST wins + `session_id_conflict` | The id `--resume` needs comes off the provider's own stream, and an ambiguous one is never usable | `test_..._turnover_live_seam.py::ProviderSessionParsingTests` (3) |
| **AS-2** *(primary success — the actuation half)* | D-023-R013 | `resume_capability_verified=True` | `with_resume("prov-session-1")` | `argv[argv.index("--resume")+1] == "prov-session-1"`; original runner untouched | A resume that does not reach the launch is not a resume | `…::ResumeActuationTests::test_with_resume_puts_the_provider_id_into_the_real_argv` |
| **AS-3** *(security / identity)* | AD-093 §1.1 | — | `with_resume(new_rotation_record_key())` | `RunnerError("internal_key_as_session_id")` | A supervisor-minted key can never be presented as a provider session | `…::ResumeActuationTests::test_a_supervisor_internal_rotation_key_can_never_be_resumed` |
| **AS-4** *(boundary — capability)* | S8.2 | capability NOT verified | `build_argv` on a resumed config | `RunnerError("resume_capability_unverified")` | An unprobed capability is never assumed | `…::ResumeActuationTests::test_an_unverified_resume_capability_still_refuses_to_emit_the_flag` |
| **AS-5** *(primary success — resume)* | D-023-R013 | recorded session, same model, non-shedding reason, capability verified | `decide_continuity(...)` | `mode == "resume"`, id named, no reason | The resume arm is real and reachable | `…::ContinuityDecisionTests::test_a_real_resume_when_everything_lines_up` |
| **AS-6** *(each impossibility, individually)* | D-023-R013 | a healthy baseline | flip each condition in turn | each yields its OWN named reason; all nine context-shedding reasons covered | A reorientation always says WHY | `…::ContinuityDecisionTests` (5 tests incl. a 9-case subTest) |
| **AS-7** *(ambiguous / conflicting)* | D-023-R013 | cross-model + shedding + unverified at once | `decide_continuity` | ALL THREE reasons reported, not just the first | The record is complete, not first-hit | `…::ContinuityDecisionTests::test_every_impossibility_is_reported_not_just_the_first` |
| **AS-8** *(null / missing input)* | CLAUDE.md §3 | recorded session with an epoch | no `max_age_seconds` vs `60.0` | unbounded ⇒ resume; bounded ⇒ `provider_session_expired` | No default session lifetime is invented | `…::ContinuityDecisionTests::test_an_age_bound_is_applied_only_when_a_caller_supplies_one` |
| **AS-9** *(unconstructible dishonest states)* | D-023-R013 | — | resume with no id; reorientation with no reason; unknown mode | all three RAISE | The dishonest record cannot be built | `…::ContinuityDecisionTests::test_a_resume_without_an_id_and_a_blank_reorientation_are_unconstructible` |
| **AS-10** *(the §1.2 defect — safe seam)* | D-007 S11.3 | open ask / pending effect / unknown SHA / unknown worktree | `SeamTurnover.execute` | `unsafe_seam`; **no** stored handoff, **no** archived session | Nothing durable is written before the moment is proved safe | `…::SeamTurnoverTests` (2) |
| **AS-11** *(the §1.2 defect — handoff)* | D-007 S11.3 | a safe seam | `execute` | a VERIFIED 14-field handoff is stored; all structural prohibitions present; `validate_handoff` passes | The full S11.3 handoff finally has a production caller | `…::SeamTurnoverTests::test_the_full_handoff_is_built_verified_and_stored` |
| **AS-12** *(verifier is not a stamp)* | S3.3 | good facts | verify a TAMPERED handoff, then a good one | tampered ⇒ finding naming `branch`; good ⇒ verified | Deterministic verification really detects a wrong handoff | `…::SeamTurnoverTests::test_the_deterministic_verifier_actually_detects_a_wrong_handoff` |
| **AS-13** *(dependency failure)* | D-007 S11.3 | a live verifier returning findings | `execute` | `handoff_unverified`; nothing stored | An unverified handoff never reaches a successor | `…::SeamTurnoverTests::test_an_unverified_handoff_is_never_carried_into_a_successor` |
| **AS-14** *(the rotation record carries BOTH identities)* | D-023-R013 | reorientation decision | `execute` | `rotation_record_key` starts `sup-rot-`; `previous_provider_session_id` named; `provider_session_id` empty WITH a reason; outgoing session archived, internal key NOT | The two identities are never conflated | `…::SeamTurnoverTests::test_a_reorientation_carries_both_identities_and_archives_the_old_session` |
| **AS-15** *(resume record)* | D-023-R013 | resume decision | `execute` | session named, **nothing archived**, **no** reorientation prompt | Archiving the session being resumed would make the resume illegal (S15) | `…::SeamTurnoverTests::test_a_resume_names_the_session_archives_nothing_and_sends_no_prompt` |
| **AS-16** *(security — archived session)* | S15 | session already archived | resume it | `archived_session_resume` | An archived session is never resumed | `…::SeamTurnoverTests::test_an_archived_session_can_never_be_resumed_by_a_later_rotation` |
| **AS-17** *(READY gate)* | D-007 S11.3 | armed gate | UNIT_COMPLETE, then READY | first ⇒ `rotation_ready_required` and the gate STAYS armed; second ⇒ cleared | Nothing is forwarded until the successor reports READY | `…::SeamTurnoverTests::test_the_ready_gate_blocks_until_a_ready_checkpoint_arrives` |
| **AS-18** *(READY gate — impostor)* | S11.3 / S15 | armed gate, reorientation | READY from the ARCHIVED session | `ready_from_archived_session` | A READY from the session the rotation replaced proves the rotation did not happen | `…::SeamTurnoverTests::test_a_ready_from_the_archived_session_never_satisfies_the_gate` |
| **AS-19** *(regression — ordinary cycle)* | D-007 S11.3 | no armed gate | `require_ready(UNIT_COMPLETE)` | passes | A run that never rotated is untouched | `…::SeamTurnoverTests::test_no_armed_gate_means_an_ordinary_cycle_is_untouched` |
| **AS-20** *(post-launch verification)* | D-023 item 2 | armed expectation | matching successor, then a wrong one | matching ⇒ ok; wrong ⇒ mismatches naming task_id, branch, worktree, starting_sha AND **model** | The successor must be the session that was commanded | `…::SeamTurnoverTests::test_post_launch_verification_names_every_mismatch` |
| **AS-21** *(empty approved list — the §1.3 defect)* | D-023-R013 | no approved models | `select` and `next_after` | `approved_models_empty`, refusal outcome `halted`, `Refusal.exit_code` 10, message says "populate" | An unpopulated config approves NOTHING and stops safely | `…::ApprovedModelRoutingTests::test_an_empty_approved_list_stops_safely_with_a_typed_refusal` |
| **AS-22** *(unlisted id)* | D-023-R013 | probe says the id is available | `select(UNAPPROVED)` | `model_not_approved`, outcome `unsafe` (`Refusal.exit_code` 11) | Availability never overrides approval | `…::ApprovedModelRoutingTests::test_an_unlisted_id_is_never_selectable_however_available` |
| **AS-23** *(no aliasing)* | D-004-R754 | approved list of one | case/whitespace/punctuation near-misses | none match; the exact id does | Ids are used verbatim | `…::ApprovedModelRoutingTests::test_membership_is_exact_with_no_aliasing_or_trimming` |
| **AS-24** *(unprobed model)* | D-023-R013 | listed, no probe seam | `select` | `model_probe_seam_missing` | Being listed is necessary and NOT sufficient | `…::ApprovedModelRoutingTests::test_a_listed_model_with_no_probe_seam_is_not_selectable` |
| **AS-25** *(probe failure / probe raises)* | D-004-R752 | probe returns not-ok / raises | `select` | `model_probe_failed`; the failure is RECORDED with its reason | A probe that could not prove availability proves nothing | `…::ApprovedModelRoutingTests` (2) |
| **AS-26** *(probe record identity)* | D-023-R013 | a recorded successful probe | read it under a different config digest, then a different CLI version | both read as NO probe ⇒ unselectable | A probe under another config or CLI proves nothing about this one | `…::ApprovedModelRoutingTests::test_a_probe_from_another_config_or_cli_makes_the_model_unselectable` |
| **AS-27** *(unsafe / malformed input)* | AD-025 | a garbage probe record in the journal | `successful(...)` | `None` | An unreadable record never makes a model selectable | `…::ApprovedModelRoutingTests::test_an_unreadable_probe_record_reads_as_no_probe` |
| **AS-28** *(chain exhaustion safe stop)* | D-023-R013 | every probe fails | `next_after` | `approved_chain_exhausted`, outcome `halted`, every attempt named | Exhaustion is a safe stop, never a fallback | `…::ApprovedModelRoutingTests::test_exhausting_the_approved_chain_is_a_typed_safe_stop` |
| **AS-29** *(turnover successor)* | D-023-R013 | approved chain, all probed | `TurnoverController.execute` | the NEXT APPROVED entry is launched; the audit row carries the probe evidence | The successor comes from the owner's list, with the reason it was permitted | `…::ApprovedSuccessorControllerTests::test_the_successor_is_the_next_approved_entry` |
| **AS-30** *(turnover safe stops)* | D-023-R013 | empty list; then a spent chain | `execute` | `NO_APPROVED_SUCCESSOR` both times; **nothing launched**; **dedup NOT consumed** | A safe stop leaves a genuine later attempt possible | `…::ApprovedSuccessorControllerTests` (2) |
| **AS-31** *(caller substitution refused)* | D-023-R013 | approved chain | `requested_model=UNAPPROVED`; `requested_effort="low"` | `INVALID_MODEL_REFUSED`, launcher never called | A caller can never substitute a model or an effort | `…::ApprovedSuccessorControllerTests` (2) |
| **AS-32** *(IPC — the non-config path)* | D-023-R013 | model IS on `claude.allowed_models` but NOT approved | `assert_allowlisted` | `model_not_approved` | A model from a NON-CONFIG path is held to the approved list too | `…::IpcApprovedModelTests::test_an_allowlisted_but_unapproved_model_is_refused` |
| **AS-33** *(IPC — ancestry unweakened)* | S3.2 rule 6 | a recorded worker pid as the caller, empty approved list | `endpoint.request_change` | `worker_origin_denied` — NOT `approved_models_empty` | Gate 1 still runs first; the new gate is additive | `…::IpcApprovedModelTests::test_the_process_ancestry_gate_still_runs_first_and_unweakened` |
| **AS-34** *(IPC — Codex unchanged)* | S3.2 rule 4 | Codex change | `assert_allowlisted` | passes on `codex.allowed_models` alone | The Codex path is untouched | `…::IpcApprovedModelTests::test_the_codex_provider_keeps_its_own_allowlist_unchanged` |
| **AS-35** *(end to end — reorientation delivered)* | D-007 S11.3 | real loop, fake runner, downgrade at cycle 1 | `loop.run(...)` | the second unit's prompt contains the reorientation header, the full handoff fields, AND the forwarded prompt | The handoff actually reaches the successor | `…::LoopLiveSeamTests::test_the_successor_receives_the_full_handoff_as_its_first_prompt` |
| **AS-36** *(end to end — READY gate blocks)* | D-007 S11.3 | successor answers UNIT_COMPLETE | `loop.run(...)` | `stopped == "rotation_ready_required"`; state PAUSED_RECOVERY; only the PRE-rotation forward happened; gate armed + refused events present | Nothing is forwarded after a rotation the successor did not acknowledge | `…::LoopLiveSeamTests::test_a_successor_that_does_not_report_ready_forwards_nothing` |
| **AS-37** *(end to end — model mismatch fail-closed)* | D-023 item 2 | READY successor reporting a DIFFERENT model | `loop.run(...)` | `stopped == "successor_identity_mismatch"`; audit names the model | A model mismatch stops the run; it is not a note | `…::LoopLiveSeamTests::test_a_successor_on_the_wrong_model_stops_the_run_fail_closed` |
| **AS-38** *(end to end — wrong worktree)* | D-023 item 2 | READY successor in another worktree | `loop.run(...)` | same fail-closed stop | Identity is checked on every axis, not just the model | `…::LoopLiveSeamTests::test_a_successor_in_the_wrong_worktree_stops_the_run` |
| **AS-39** *(end to end — unsafe seam)* | D-007 S11.3 | no known HEAD | `_rotate_at_seam` | paused, `rotation_refused`/`unsafe_seam`; **rotation still pending**; owner ask queued | A refused turnover never half-rotates | `…::LoopLiveSeamTests::test_an_unsafe_seam_refuses_the_turnover_and_pauses_for_the_owner` |
| **AS-40** *(end to end — both identities)* | D-023-R013 | real loop rotation | `loop.run(...)` | record carries `sup-rot-…` AND `sess-1`; the successor's own id is captured afterwards and differs from the key | The loop never stores the internal key as a session | `…::LoopLiveSeamTests::test_the_provider_session_is_recorded_and_the_internal_key_is_not` |
| **AS-41** *(end to end — ambiguous session)* | S8.2 | run result with a session conflict | `loop.run(...)` | nothing recorded; `_provider_session_id == ""` | An ambiguous identity is dropped, not recorded | `…::LoopLiveSeamTests::test_an_ambiguous_provider_session_is_dropped_not_recorded` |
| **AS-42** *(end to end — resume actuation)* | D-023-R013 | recorded session, same model, capability verified, `session_relaunch` | `loop._full_turnover(...)` | `continuity.resumed`; **`loop.runner.config.resume_session_id == "prov-1"`**; nothing archived; no prompt | The resume reaches the launch config | `…::LoopLiveSeamTests::test_a_resume_reaches_the_launch_or_the_seam_refuses` |
| **AS-43** *(dependency failure — no rebind seam)* | D-023-R013 | a runner with no `with_resume` | `_full_turnover` | `LoopError("resume_actuation_unavailable")` | A resume the launch cannot perform is a refusal, not a record | `…::LoopLiveSeamTests::test_a_runner_that_cannot_resume_is_a_refusal_not_a_claimed_resume` |
| **AS-43b** *(retry / crash-resume)* | D-023 item 2 | a completed turnover, then `_successor_expectation` cleared as a restart would | `_post_rotation_gates` with a wrong-task successor | still stops `successor_identity_mismatch` | A restart between the rotation and the successor's first checkpoint does not skip the identity check | `…::LoopLiveSeamTests::test_a_crash_between_the_rotation_and_the_successor_still_checks_identity` |
| **AS-44** *(regression guard — no code default)* | D-023-R013 | — | scan five supervisor modules + `cli.py` | no module-level assignment of either removed constant; no attribute; no literal `current_model` default; `ModelChain()`/`ApprovedModels()` construct EMPTY | A future edit cannot quietly reintroduce a default chain | `…::NoCodeDefaultModelTests` (3) |
| **AS-45** *(config — the §1.3 defect)* | D-023-R013 | config with no approved section | load, then select | loads fine; SELECTING refuses `approved_models_empty` with outcome `halted` | Absent means empty, and empty stops safely | `test_agent_supervisor_model_chain.py::ModelChainConfigTests::test_an_absent_section_approves_nothing_and_stops_safely` |
| **AS-46** *(config — conflicting spellings)* | D-023-R013 | both sections, different lists | load | `approved_models_conflict` | A silent precedence rule is a wrong model selection waiting to happen | `…::test_two_spellings_that_disagree_are_refused_not_resolved` |
| **AS-47** *(the §2.5 stale note)* | M0-T079 §8.7 | — | `disable_limited_auto` | note says "implemented", not "not implemented"; flag still False | The correction is wording only; the flag still asserts OFF | `…::NoCodeDefaultModelTests::test_the_stale_limited_auto_note_was_corrected` |

---

## 5. Test-run output

### 5.1 Baseline, before any change (this worktree, base `73f5b85`)

```
$ python -m pytest tools/ -k agent_supervisor -q
1707 passed, 2 skipped, 555 deselected in 205.42s
```

### 5.2 After the change

```
$ python -m pytest tools/ -k agent_supervisor -q          # first submission
1783 passed, 2 skipped, 555 deselected in 259.07s

$ python -m pytest tools/ -k agent_supervisor -q          # reviewed identity 8546a2e8
1833 passed, 2 skipped, 555 deselected in 148.16s

$ python -m pytest tools/ -k agent_supervisor -q          # after corrections U1-U15
1854 passed, 2 skipped, 555 deselected in 142.18s
```

```
$ python -m pytest tools/test_agent_supervisor_turnover_live_seam.py -q
88 passed in 1.95s
```

**Exact counts after the correction round: 1854 passed / 0 failed / 2 skipped.** Delta from the reviewed identity: **+21 net** (+24 new correction tests, −3 tests deleted with the dead `assert_ready_checkpoint` gate they covered, see U4). Delta from the pre-task baseline: **+147.** The two skips are the pre-existing platform-conditional skips, unchanged. The floor in `M0-T039-supervisor-freeze.md` (≥ 1165 tests, 0 failures) is exceeded. (`python -m unittest discover -s tools` does NOT work here — `tools/` is not an importable package — so the modules are named explicitly, as in the M0-T079 report.)

### 5.3 Modularity

```
$ python tools/modularity_check.py --check
selected 280 files; failures 0; warnings 5
```

All five warnings are pre-existing (`symbol_ceiling` on `apps/web/src/lib/surveyReview/types.ts`, `services/api/app/connectors/mappluto_geometry_arcgis.py`, `cli.py`, `policy.py`; `review_signal` on `tools/context_benchmark.py`).

### 5.4 The rest of the `tools/` suite, and two failures that are working-tree artifacts

```
$ python -m pytest tools/ -q -k "not agent_supervisor"
1 failed, 550 passed, 1 skipped, 1787 deselected in 2537.62s   # + the one deselected below
```

Two tests fail, both in `tools/test_context_integration.py` and both from ONE cause:

- `Proof1RealTaskCompile::test_real_paths_resolve_and_requirements_present`
- `Proof7EntryPoint::test_entry_point_invokes_integrated_compiler`

**Diagnosed to the mechanism: an artifact of the UNCOMMITTED working tree, not of the change.** `context_pack` includes `git_diff` as a material source. This worktree carries 204 462 bytes of uncommitted diff, and the pack's first sub-packet measures 249 123 bytes against a 256 000-byte effective bound, so it fails closed with `split_required` (exit 2 — which is the correct fail-closed behaviour, not a crash). 249 123 − 204 462 = 44 661 bytes, comfortably inside the bound once the diff is gone.

**Falsification test**, run to make sure the new modules were not the cause. A clean `git clone` of the committed HEAD, with all six new production modules and the new test module copied in as UNTRACKED files — so they are all present, and `git diff` is 0 bytes:

```
$ git status --porcelain | head -3
?? tools/agent_supervisor/approved_models.py
?? tools/agent_supervisor/handoff.py
?? tools/agent_supervisor/loop_turnover.py
$ git diff | wc -c
0
$ python -m pytest tools/test_context_integration.py -q
24 passed in 63.12s
```

All 24 pass with the new files present. The failures appear only with the uncommitted diff, which is the normal state of a producer handoff and resolves when the orchestrator commits. Recorded here rather than worked around; **neither test was modified.**

(For completeness, the earlier single-pack comparison: this worktree reports `dependency_breadth=40` where the committed HEAD reports `12`, but both land in the same `medium` tier and the effective bound is `min(--max-bytes, ceiling)` = 256 000 in both, so the tier is not what changed the outcome — the byte total is.)

### 5.5 Live CLI smoke (Windows, no provider contacted)

`doctor` reports the approved list and the probe evidence as data, including the honest empty case. Against a temp checkout whose `config.toml` declares `[controller] default_mode="shadow"` and two empty allowlists, with no `[approved_models]` and no `[model_chain]`:

```
$ python -m tools.agent_supervisor doctor --checkout <tmp> --runtime-base <tmp-rt> \
      --config <tmp>/config.toml --claude-executable C:/nonexistent/claude.exe --json

approved_models     | True | the controller config approves NO models ([approved_models]
  models is absent or empty). There is deliberately no built-in default list (D-023-R013),
  so every model-selection act - a rotation, a quota chain step, a turnover successor, an
  authenticated model change - will stop safely with a typed refusal until the owner
  populates protected config

model_launch_probes | True | recorded probes: (none). Selectable under THIS config identity
  and CLI version: (none). A probe recorded under a different controller config or a
  different provider CLI proves nothing about this one and is ignored; a model with no
  recorded successful probe is not selectable
```

Both are reported as PASSING checks with an explicit consequence, not as configuration errors: approving nothing is a legitimate state of the file, and what it costs is stated here rather than discovered when a rotation stops. No provider was contacted; the executable path is deliberately nonexistent, which is why the CLI identity — and therefore every probe's identity match — is empty.

---

## 6. Existing tests amended, and why each is a strengthening

The supervisor-freeze rule forbids weakening any existing check. The amendments fall into five groups; none removes a case, relaxes a tolerance, skips, or xfails.

1. **Five turnover modules re-point from a constant to the approved chain** (`turnover_controller`, `turnover_adapters`, `turnover_integration`, `turnover_live_signal`, `r595_actuation`). `ALLOWED_SUCCESSOR_MODEL_ID` is gone, so each module now DECLARES the owner-approved chain itself and asserts the launch used that id. **Strictly stronger:** the old assertion compared the launched id to the very constant the production code read, so it could not have failed even if the id were wrong; the new one compares it to a chain the test owns.

2. **`turnover_adapters`: two launcher tests re-pointed.** They asserted the launcher IGNORED the request's model and pinned the constant. That discipline MOVED UP a layer and got stronger: `TurnoverController` resolves the approved successor and refuses any differing caller preference (`INVALID_MODEL_REFUSED`, still asserted in the controller module) before the launcher is reached. The launcher's own duty is now to launch exactly the id it was given, and a **new** test asserts a request naming NO model is refused with nothing launched — a case that did not exist before.

3. **`rotation`: five ledger tests follow the new `complete_rotation` contract**, and **five NEW tests** were added alongside them (resume names the session and archives nothing; a resume with no id is refused; an unexplained reorientation is refused; resuming an archived session is refused; an unknown continuity mode is refused). `test_a_new_session_id_is_always_new` became `test_a_rotation_record_key_is_always_new_and_never_looks_like_a_session`, which additionally asserts the `sup-rot-` prefix and that the OLD name is gone — an alias would let a caller keep minting a fake session identity.

4. **`model_chain`: four config tests inverted, because they asserted the defect.** `test_the_default_chain_is_the_owners_order` asserted `DEFAULT_ORCHESTRATOR_MODEL_CHAIN` equalled three specific ids; it is now `test_there_is_no_built_in_default_chain_anywhere`, which asserts the constant is gone, the chain constructs EMPTY, and no model-id literal survives in `config.py`. `test_an_absent_section_falls_back_to_that_exact_order` became `…approves_nothing_and_stops_safely`. The `empty_model_chain` load-time error case moved to `…test_an_explicitly_empty_list_approves_nothing_rather_than_defaulting`, which asserts the refusal now happens where a model is SELECTED. Two new cases were added (the canonical section is read; two disagreeing spellings are refused), and one new malformed-key case.

5. **Fixtures now model the S11.3 contract.** `LoopTestBase.build` gained `head_sha` (a real run always knows its HEAD; a seam that cannot name one refuses). `FakeRunner` gained `with_resume`, mirroring the real runner. A new `LoopTestBase.successor_result` helper makes a post-rotation fake answer with a READY checkpoint reporting the task/branch/worktree/HEAD it was commanded onto. The chain fixture's fake CLI gained `FAKE_STATUS`/`FAKE_WORKTREE`/`FAKE_STARTING_SHA` (defaults preserve the old shape byte for byte; only the one fixture that crosses two rotation seams sets them). This makes the fakes MORE faithful to a live worker, not less demanding of one.

---

## 7. Owner-hold compliance

- Nothing here lifts **R595**. The supervisor stays SHADOW-ONLY; no new or expedited approval path was created.
- The **live launch probe is never run** by this build's production path: `_approved_model_router` takes the probe as an injected callable and `cli.py` passes none, so a model with no already-recorded successful probe is refused rather than probed. Running a real probe is an owner-checkpoint act on the controller.
- `RUNNABLE_MODES`, the bounded-mode owner gate, the four-tier policy, `job_object` containment, `run_budget` semantics, `github_flow.py`, `policy.py` tiers, and `process.py` containment are all untouched.
- The IPC's process-ancestry gate is unchanged and still runs first (AS-33).
- No new dependency was added. No S7 transition-table edge was added or altered.

---

## 8. Risks and judgment calls

1. **The resume path has no live trigger today (§3.2).** Every rotation reason the assembled loop produces is context-shedding or cross-model, so production always re-orients. The resume arm is real, wired, and proved through the real `_full_turnover`, but the loop-level test supplies the reason code `session_relaunch`, which nothing currently emits. I judged adding a trigger to be a speculative supervisor feature (freeze §1) and left it out. A reviewer may reasonably want that decision revisited as its own task.
2. **The READY gate is a genuine behaviour change with real blast radius.** After any rotation, the next cycle forwards nothing unless the successor returns a structured READY checkpoint. This is the S11.3 requirement finally enforced, but it changes what a supervised run does after every rotation, and it is why several existing fixtures needed the amendment in §6.5. This deserves an explicit reviewer look.
3. **Post-launch verification compares untrusted worker text.** `branch` and `worktree` come from the checkpoint, which is untrusted content. The comparison is exact-string against values the supervisor wrote down first, so a worker cannot widen anything — but a legitimately different path SPELLING (a symlink, a case difference, a trailing separator) would fail closed. The comparison is skipped when either side is empty; a reviewer may prefer canonicalization.
4. **Two config spellings for one list (§3.5).** Defensible and structurally guarded, but a smell. A follow-up task could retire `[model_chain]` once the owner's config is migrated.
5. **The `OPUS_UNAVAILABLE_SAFE_STOP` enum name is now model-generic.** Its value is a frozen machine contract from M0-T054 and possibly read by operators, so I did not rename it; the docstring says what it means. Renaming it is a separate migration decision.
6. **`turnover_seam.py` is 452 SLOC**, the largest new module, and holds five responsibilities that share one ordering. Splitting it further would scatter an order that must not be re-arranged. A future addition should probably split by gate rather than grow it.
7. **The six new modules are untracked**, so `modularity_check` has not censused them (§3.7). They will be covered the moment the orchestrator commits; measured counts are in §2.1.
8. **`cli.py` extraction touched pre-existing code.** Keeping `cli.py` under its growth limit required moving the whole R595 actuation-channel assembly (~250 SLOC, mostly pre-existing) into `turnover_wiring.py`. This is scope beyond the defect fix, taken because the alternative was an owner exception; every moved name is re-exported so no caller changed.
9. **`_check_probe_evidence` needs `--claude-executable` to bind a CLI identity.** Without it the identity is empty, every recorded probe fails the identity match, and nothing is selectable. That is the fail-closed direction, and `doctor` says so — but an operator running `doctor --config X` without naming the executable will see "(none)" selectable and should not read that as a defect.

---

## 9. Deliberately NOT done — later tasks own these

- **`github_flow.py`, `policy.py` tiers, `process.py` containment, `run_budget.py` semantics** — untouched, as instructed.
- **A new rotation trigger for the resume path** — not added (§8.1).
- **A real live launch probe in the production start path** — not wired. The seam exists and is REQUIRED; supplying a real probe is an owner-checkpoint act (§7).
- **Retiring `[model_chain]`** — not done; the legacy spelling is still read (§3.5).
- **Renaming `OPUS_UNAVAILABLE_SAFE_STOP`** — not done (§8.5).
- **Canonicalizing branch/worktree comparison** — not done (§8.3).
- **`remote_approvals.py` beyond the one note** — untouched; M0-T084 owns the rest.
- **`tools/model_routing.py` and `docs/MODEL_ROUTING_POLICY.md`** — read as context, unmodified. That router is the ORCHESTRATOR's complexity-based routing and is a different decision class from the supervisor's approved-chain selection; the policy doc explicitly says supervisor-side integration is its own qualifying-evidence task.
- **`docs/MODEL_ROUTING_POLICY.md` update for `[approved_models]`** — not made. The doc describes `tools/model_routing.py`, not the supervisor config, and editing it would widen scope; flagged here for whichever task owns the doc.
- **A measured 10-hour canary, or any live-provider claim** — not attempted, and none is made (D-023-R023).

---

## 10. Correction round U1-U15 (applied after G3 PASS / G4 PASS / G5 FAIL at `8546a2e8`)

One consolidated round per D-023-R016/R017. The through-line the reviewers named — a **fail-open family**, where an identity or continuity check SKIPS when a value is absent instead of treating absent as a mismatch — is closed at every site they found and at two they did not (the `require_ready` blank-session path and the both-models-unknown continuity case).

| U | Where | What changed |
|---|---|---|
| **U1** *(must-fix)* | `turnover_seam.py:459-517` (`require_ready`), `:520-580` (`verify_post_launch`) | An ABSENT identity field the supervisor has an expectation for is now a MISMATCH. `require_ready` refuses `ready_without_session_id` when the READY names no `claude_session_id`; the four unbacked axes (task_id, branch, worktree, starting_sha) report "successor reported NOTHING". The model axis keeps its guard and is documented as backstopped by the R739 per-event stream check. |
| **U2** | `session_continuity.py:278-289` | CROSS_MODEL no longer requires both ids non-empty: an unknown model on EITHER side forbids a resume (principle 3). |
| **U3** | `turnover_seam.py:51-72` (labels + `FactSource`), `:232-305` (`deterministic_verdict`), `:308-360` (`verify`) | `FactSource` independent-re-derivation seam added (arm a); the verdict states its own `scope`; the two deterministic labels are now distinct. Report §2.3/§3.3 corrected — see §3.3 for which arm was taken and why. |
| **U4** | `rotation.py:723-731` → removed (replaced by the comment now at `rotation.py:723`) | The dead duplicate READY gate is GONE, with its false docstring; report §1.2 corrected; a guard test asserts it cannot return. |
| **U5** | `approved_models.py:402-413` | A non-`ProbeOutcome` probe return is `ok=False`, not `ok=bool(outcome)`. |
| **U6** | `turnover_controller.py:356-380` (call site), `:538-563` (`_no_successor_record` / `_safe_append`) | `NO_APPROVED_SUCCESSOR` writes a `turnover_no_approved_successor` audit row; an unwritable chain degrades to `(unaudited: …)` rather than turning a safe stop into a crash. |
| **U7** | `approved_models.py:325-351` (`_attempts_sentence`), `:447-455` (the refusal) | The chain-exhaustion message is derived from the attempts' reason codes: "NOTHING was probed" vs "tried by an actual launch probe". |
| **U8** | `cli.py:2597-2607` (the identity), `:3308-3316` (`--claude-executable`) | `orchestrator-watchdog` gains `--claude-executable` and passes `_claude_cli_identity(...)` — the same probe identity `start` uses. |
| **U9** | `turnover_adapters.py:384-392` | The launcher-level effort pin is restored (`effort = ALLOWED_SUCCESSOR_EFFORT`, never the request's), with the adversarial test reinstated. |
| **U10** | `test_agent_supervisor_r595_actuation.py:395-416` | The self-referential assertion is replaced by assertions against real production values. |
| **U11** | `cli.py:3016-3029` | `ConfigError` from `_run_loop` is a typed refusal, not a traceback. |
| **U12** | `turnover_seam.py:634-660` | `arm_ready_gate` now runs BEFORE `complete_rotation`, so the crash window between the two durable writes fails CLOSED (armed gate, rotation still pending) instead of OPEN. |
| **U13** | `turnover_wiring.py:74-77/:239-241`, `cli.py:2569-2571/:2861-2863/:3288-3290`, `worker_turnover.py:19-21` | All six stale "pinned opus-4-8" claims corrected, including the self-contradicting `--authorize-turnover-actuation` help text. |
| **U14** | `session_continuity.py:228-238` (primary reason), `:166-184` (per-run scope); `loop.py:1398-1409`; `loop_turnover.py:91-94`; `approved_models.py:484-538` (doctor wording); `config.example.toml`; `turnover_seam.py:611-630` (ordering docstring); `test_..._turnover_adapters.py:267-270` | Primary `none_reason` validated; the provider-session read scoped per run; `LoopError` caught at the seam; doctor + example-config probe wording made accurate; the store-before-assert and arm-before-complete orderings documented; the dangling test-name reference fixed. |
| **U15** | this report | Figures corrected to the reviewed identity and re-measured after the round; the exit-10/11 claims relabelled as `Refusal` properties. |

**Nothing deferred.** All fifteen are applied.

### 10.1 Tests added or restored in this round

`tools/test_agent_supervisor_turnover_live_seam.py` (+21, now 88):
`test_a_ready_naming_no_session_can_never_clear_the_gate`,
`test_a_blank_session_cannot_smuggle_the_archived_one_past_the_gate`,
`test_a_blank_resume_session_cannot_satisfy_the_resume_gate`,
`test_an_omitted_identity_field_is_a_mismatch_not_a_pass`,
`test_each_identity_axis_fails_closed_on_its_own_omission`,
`test_an_axis_the_supervisor_never_commanded_is_not_invented` (U1);
`test_an_unknown_recorded_model_can_never_resume`,
`test_an_unknown_successor_model_can_never_resume`,
`test_both_models_unknown_can_never_resume` (U2);
`test_an_independent_fact_source_can_actually_refuse_the_rotation`,
`test_an_agreeing_independent_source_is_recorded_as_the_stronger_check`,
`test_a_fact_source_that_raises_refuses_instead_of_downgrading`,
`test_the_verdict_states_its_own_scope_rather_than_implying_more` (U3);
`test_an_unparseable_probe_result_is_never_read_as_availability` (U5);
`test_a_no_approved_successor_safe_stop_leaves_a_durable_audit_row`,
`test_an_unwritable_audit_never_turns_a_safe_stop_into_a_crash` (U6);
`test_an_exhaustion_message_never_claims_a_probe_that_did_not_happen` (U7);
`test_start_and_the_watchdog_share_one_probe_identity` (U8);
`test_a_crash_between_the_two_durable_writes_fails_closed` (U12);
`test_a_made_up_primary_none_reason_is_refused`,
`test_a_session_recorded_by_another_run_is_not_this_runs_session` (U14).

`tools/test_agent_supervisor_turnover_adapters.py`:
`test_a_caller_supplied_effort_is_ignored_by_the_launcher` (U9, restored).

`tools/test_agent_supervisor_model_chain.py`:
`test_a_config_conflict_is_a_typed_refusal_not_a_traceback` (U11).

`tools/test_agent_supervisor_rotation.py`:
`test_there_is_exactly_one_ready_gate_and_it_is_the_live_one` (U4, replacing the three tests deleted with the dead gate).

`tools/test_agent_supervisor_r595_actuation.py`:
`test_the_successor_is_never_caller_selectable` (U10, replacing the self-referential `test_successor_model_is_hard_pinned_opus_4_8`).

### 10.2 Modularity after the round

`cli.py` reached 2952 against its 2953 limit while applying U8/U11 — one SLOC of headroom, which is not headroom. The two model-routing doctor disclosures were therefore **extracted** into `approved_models.py` as `approved_models_disclosure` / `probe_evidence_disclosure` (the text describes what THAT module's list and ledger govern, so it changes when those rules change, not when the CLI's presentation does); `cli.py` keeps two-line `Check(*…)` wrappers. Fifteen imports in `cli.py` that the earlier `turnover_wiring.py` extraction had orphaned were also dropped (each verified unused in the file and unreferenced as `cli.<name>` anywhere in the suite). Final: `cli.py` **2898** (limit 2953, 55 free), `loop.py` **2080** (limit 2088), `rotation.py` **623** (limit 820). `python tools/modularity_check.py --check` → `selected 280 files; failures 0; warnings 5`, all pre-existing.
