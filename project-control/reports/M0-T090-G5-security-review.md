# M0-T090 — G5 Independent Security Review

> Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
> (transport entity-decoding only). Verdict: PASS (4 MINOR + 3 NIT; none blocking).
> Reviewer preamble: "All evidence gathered: working tree matches frozen SHA e8b21d1 exactly,
> 53/53 tests pass, modularity exit 0, imports are exactly as specified, no actuation surface,
> no sensitive content."

# Gate Report

- Gate ID: G5 (security review)
- Task ID: M0-T090 (D-024 Phase C1 — bounded subagent contracts + structural workload sizing)
- Reviewer: security-reviewer (independent; read-only)
- Producer: orchestrator
- Result: **PASS** (PASS-with-findings; 4 MINOR + 3 NIT; none blocking)
- Clean environment/worktree used: yes — reviewed at frozen content commit `e8b21d1`; `git diff --stat e8b21d1 -- tools/agent_supervisor tools/test_agent_supervisor_bounded_contracts.py` is empty (working tree byte-identical to frozen SHA for every reviewed file). Content identity `content_manifest_sha256 = 3e726a0fcc3ea574337d8e2166d3710322586806232fc52506372362f820baba` confirmed consistent across `project-control/reports/M0-T090.json` and `project-control/gates/M0-T090-G2.json`, and matches the frozen identity named in the packet.

## Acceptance criteria reviewed

Task `acceptance_scenarios` is empty; the security acceptance surface is the six dimensions in the review charter (owner-policy invariants R045/R056/R595, concurrency/lease integrity, injection surfaces, data hygiene, supply-chain/modularity, public-repo posture). Each is addressed under Regression/security/provenance findings. Files reviewed: `tools/agent_supervisor/{workload_classifier,subagent_contracts,startup_overhead,spawn_decision,workload_sizing}.py`, `tools/test_agent_supervisor_bounded_contracts.py`, `project-control/reports/M0-T090-bounded-contracts.md` (plus the reused `tools/agent_supervisor/telemetry_records.py` for the to_record hygiene claim).

## Directive/requirement verification

Security-relevant D-024 requirements independently re-derived at content identity `3e726a0f…` (full per-requirement DCV is the separate `directive-compliance-verifier` pass; below are the security-load-bearing ones this G5 verified directly):

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024-R045 (no worker-facing quota/countdown/pressure) | 3e726a0f… | PASS (with NIT N1) | `_QUOTA_PATTERNS` (10 classes) applied per worker-facing str/tuple field via `worker_text_fields()` in `validate_assignment`, AND re-applied to the whole rendered prompt (`assert_worker_text_clean("rendered_prompt", …)` at subagent_contracts.py:539). Test `test_quota_language_rejected_fail_closed` (8 phrasings incl. "About 3.5k tokens should suffice", "Stay under 20% of your context window"), `test_quota_guard_covers_every_worker_field`, `test_worker_prompt_contains_no_quota_language` (independent scan). Re-ran pack: 53 passed. |
| D-024-R056 (envelope numbers/band vocabulary never in worker text) | 3e726a0f… | PASS (with MINOR M1/M2) | Primary control is structural: `render_worker_prompt` interpolates ONLY assignment fields into a fixed literal template (subagent_contracts.py:463–541); zero envelope field is a template input. Backstop `assert_no_envelope_leak` scans band names + `health_bands.numeric_strings()` + window + detector counters. See M1/M2 for two backstop gaps (both non-load-bearing given the structural control). |
| D-024-R079/R080 (stale graph reported, never acted on) | 3e726a0f… | PASS | `WorkloadFeatures.graph_stale=True` → `classify_workload` returns `unknown-recon-first` with reason_code `graph_stale`; `GraphNeighborhood.stale` → `tier_signals` raises `SizingError("stale_graph")` rather than sizing from stale breadth. Tests `test_stale_graph_is_reported_never_used`. |
| D-024-R081 (preserve/reuse graph + tier system, never redefine) | 3e726a0f… | PASS | `workload_sizing._budget()` LAZY-imports `tools.context_pack_budget` and reuses `select_tier`/`TierSignals`/`TIER_TARGET_TOKENS`; no tier table copied; fail-closed `SizingError("budget_unavailable")`. Test `test_tier_selection_reuses_the_accepted_tiers_exactly`, `test_medium_without_justification_stays_withheld`. |
| D-024-R101 (Phase C supervisor-freeze qualifying evidence) | 3e726a0f… | PASS | Cited in packet §Authority, in every one of the 5 module docstrings, and in commit `e8b21d1` message. |
| R595 / shadow-only (nothing spawns/resumes/stops/messages/reconfigures an agent) | 3e726a0f… | PASS | See "no actuation surface" below; `decide_spawn`/`assert_grantable`/`packet_plan` return inert dataclasses. No external importer wires the 5 modules into any runtime loop (grep confirmed). |

## Steps independently executed

- `git log --oneline -1 e8b21d1`; `git rev-parse HEAD` (68d6f02); `git diff --stat e8b21d1 -- …` → empty (working tree == frozen SHA).
- `python -m pytest tools/test_agent_supervisor_bounded_contracts.py -q` → **53 passed in 0.16s** (Python 3.11.9).
- `python tools/modularity_check.py --check` → **failures 0, warnings 5; EXIT=0**. None of the 5 new modules appear in the warnings (warnings are pre-existing files outside this diff: apps/web types.ts, mappluto connector, agent_supervisor/cli.py, agent_supervisor/policy.py, context_benchmark.py). Largest new module `subagent_contracts.py` = 587 SLOC (< 600 warn line).
- Import inventory of all 5 modules: only `dataclasses, hashlib, json, re, statistics, collections.abc, typing`, package-internal (`.telemetry_records`, `.workload_classifier`, `.startup_overhead`), and the lazy `from tools import context_pack_budget`. **Exactly the allowed set; no shell/subprocess/network/filesystem imports.**
- Actuation/IO token scan (`subprocess|os.system|socket|urllib|requests|httpx|open(|Path(|.write|json.dump(|Popen|exec(|eval(|Task(|Agent(|threading|asyncio`): every hit is a vocabulary label / field name (`write_owner_count`, `write_lease_paths`, `spawn-new`) inside strings/identifiers — **no actuation call**.
- External-importer scan of the 5 module names across `tools/` → **none** outside their own cross-references and the test pack. Not wired into a runtime loop.
- Sensitive-content scan (`MLFLL|C:\Users|/Users/|Downloads|password|secret|api[_-]?key|token=|BEGIN … PRIVATE`) across all 7 files → **no matches**.
- `python -c` and shell file-writes are blocked by the read-only guard; the two fail-open/false-positive guard behaviors (M1, M2) and the path-normalization gaps (M3) were established by exact hand-trace of the deterministic source, cross-checked against the module's own tested cases (e.g., the tested `services/api/app` vs `services/api/app/routes.py` overlap, and the tested `0.7` leak) which anchor the trace.

## Expected versus actual

Expected: pure, inert, fail-closed controller-planning schemas with no actuation and no worker-facing quota/countdown surface. Actual: matches. All fail-closed guards fire as designed; unknown/stale/unmeasured always resolve conservatively (`unknown-recon-first`, `None` never zero, refuse-on-stale). Two secondary backstops (envelope-leak guard variants) and lease-path normalization have narrow gaps that do not affect the primary controls (see Defects).

## Evidence paths

- `tools/agent_supervisor/subagent_contracts.py` (R045 guard, R056 leak guard, `assert_grantable`, `_normalized_lease`/`_scopes_overlap`, `render_worker_prompt`, `_digest`)
- `tools/agent_supervisor/workload_classifier.py`
- `tools/agent_supervisor/startup_overhead.py` (`to_record`, in-memory `OverheadLedger`)
- `tools/agent_supervisor/spawn_decision.py`
- `tools/agent_supervisor/workload_sizing.py`
- `tools/test_agent_supervisor_bounded_contracts.py`
- `tools/agent_supervisor/telemetry_records.py` (reused sanitize surface; `to_record` target)
- `project-control/reports/M0-T090-G2-self-check.md` (orchestrator-captured composite suite baseline: 2653 passed / 3 skipped / 0 failed; ruff clean; gitleaks clean)

## Human-style walkthrough findings

Not a UI task. Traced the realistic controller flow: build `WorkerAssignment` + `SupervisionEnvelope` → `validate_pair` → `render_worker_prompt` → `assert_worker_text_clean` + `assert_no_envelope_leak`. The worker prompt is assembled from assignment fields only; the private envelope (bands, window, detectors, telemetry confidence) is never a template input, so a worker literally cannot receive quota/countdown/band data through the intended path. `decide_spawn`/`assert_grantable`/`packet_plan` produce record objects the shadow controller would log — no side effects.

## Regression/security/provenance findings

1. **Owner-policy invariants (R045 / R056 / R595).** R045: the no-quota guard covers every worker-facing `str` and every `str` element of every `tuple` field (`worker_text_fields()` at subagent_contracts.py:161–172); the current dataclass has only `str`/`tuple[str,…]`/`bool` fields, so no worker-facing free-text field escapes today, and the whole-rendered-prompt re-scan is a second net. R056: structural control is sound (envelope never interpolated). R595: **nothing in the diff can spawn, resume, stop, message, or reconfigure an agent** — verified by import inventory, actuation-token scan, and the absence of any external importer.
2. **Concurrency/lease integrity.** `assert_grantable` is honest snapshot validation, not a lock (see M4). Path normalization handles backslash forms and Windows case folding (tested) but does NOT resolve dot segments / leading `./` / absolute-vs-relative (see M3).
3. **Injection surfaces.** No shell/subprocess/network/file-path execution anywhere. `render_worker_prompt` uses `str.format` with keyword args against a FIXED literal template — substituted assignment values are inert data (Python `.format` does not re-expand `{}` inside substituted values), so there is **no format-string injection**. Trust model is internal: the assignment author is the controller itself. One forward-looking note (N3) on markdown structural injection if assignment fields ever carry untrusted content.
4. **Data hygiene.** `_digest` uses canonical JSON (`sort_keys=True, separators=(",",":"), ensure_ascii=True`) then `encode("ascii","backslashreplace")` — deterministic, ASCII-stable, no raw home paths (it digests controller-provided content; the module injects nothing). `StartupObservation.to_record()` attributes are `{size_class, resolved_model, packet_tier, outcome}` (closed-vocabulary/model-name strings) and `task_id = assignment_id` — **no path or username field**; numeric measurements only. Nothing in these modules writes a file; `OverheadLedger` is in-memory with bounded oldest-first eviction and a counted `evicted_observations`. Redaction remains the accepted Phase B journal's job on write (reused, not rebuilt).
5. **Supply chain / modularity.** No new dependency; lazy fail-closed reuse of `tools.context_pack_budget`; leaf package preserved (no import of index/graph machinery). Largest new module 587 SLOC < 600 warn; `modularity_check --check` EXIT=0. D-024-R101 freeze-evidence cited in packet, all docstrings, and commit. Suite baseline (2653/3/0) is orchestrator-captured stored evidence in `M0-T090-G2-self-check.md`; I independently reproduced the 53-test pack and modularity exit 0.
6. **Public-repo posture.** No home paths, usernames, or secrets in any of the 7 files.

**Standard G5 checklist items that are Not Applicable to this diff (stated honestly):** cross-tenant RLS isolation, service-role secret handling, private Storage bucket access, SSRF, SQL/command injection, and upload controls — none apply, because this diff has no database/RLS surface, no network client, no Storage/HTTP, no untrusted input, and no file upload. The only injection-adjacent surface (prompt templating) is covered above.

## Defects

None blocking. Findings (severity: MINOR / NIT):

- **M1 (MINOR — R056 leak-guard fail-open variant).** `HealthBands.numeric_strings()` emits the percent form without a space (e.g. `"70%"`) and `assert_no_envelope_leak` uses a literal substring test, so a spaced form of a band threshold escapes. Repro (hand-traced against default bands where prepare=0.70): `assert_no_envelope_leak("you are at 70 % now", envelope)` does NOT raise, though 70% is the private `prepare_to_land` threshold. Non-load-bearing because the envelope is never interpolated into the worker prompt (defense-in-depth backstop only). Remediation: normalize whitespace before the substring test, or add a generic `\b\d{1,3}\s*%` check for values matching a band percentage.
- **M2 (MINOR — R056 leak-guard false positive; functional).** The band-name check `if band in lowered` for bands `"observe"` and `"land"` matches common English substrings. Repro (hand-traced): `render_worker_prompt` on an assignment whose `exact_change` is `"Repair the landing page hero section."` raises `ContractError("envelope_leak")` (`"land"` ∈ `"landing"`); likewise `"island"`, `"flatland"`, and `"please observe …"` (`"observe"`). This is fail-closed (never leaks), but once contracts are actuated it would spuriously refuse legitimate prompts. Remediation: match only the qualified private tokens (`"prepare_to_land"`, `"emergency_stop"`) and drop the bare common words `"observe"`/`"land"` from the substring scan, or gate them behind band-ish context.
- **M3 (MINOR — lease overlap normalization gap).** `_normalized_lease` lowercases and converts backslashes but does not resolve `..`, leading `./`, or `/./`, nor canonicalize absolute vs relative. Hand-traced dodges where `_scopes_overlap` returns None though both resolve to the same real path: `("pkg/../other",)` vs `("other",)`; `("./pkg",)` vs `("pkg",)`; `("pkg/./sub",)` vs `("pkg/sub",)`. Lease paths are controller-authored (internal trust) and the supervisor is shadow-only, so no live exploit — but harden before runtime lease enforcement: canonicalize with a `posixpath.normpath`-style pass and reject absolute/traversal lease paths prior to overlap comparison.
- **M4 (MINOR — TOCTOU / documentation).** `assert_grantable` validates a candidate against a caller-supplied snapshot of active writers; it does not register the grant, so two candidates checked against the same snapshot can both pass and then overlap (it is validation, not mutual exclusion). The module docstring says it "defines and validates contracts; runtime enforcement belongs to later units," which covers the direction generally, but the specific snapshot-not-a-lock semantics of `assert_grantable` are not called out. Remediation: document explicitly that the future runtime must serialize grants and fold each granted candidate into the active set before checking the next.
- **N1 (NIT — R045 forward-compat).** `worker_text_fields()` scans only `str` and `tuple`-of-`str`; a future `dict`/`list`/nested-dataclass/`frozenset` worker-facing field would be silently skipped by the per-field guard. No such field exists today, and the whole-prompt re-scan catches anything interpolated, so no live gap. Harden by making `worker_text_fields()` fail closed (raise) on any field type it cannot scan, forcing an explicit decision when a non-`str`/`tuple` worker field is added.
- **N2 (NIT — R045 percent scope, intentional).** `assert_worker_text_clean`'s `percent_of_window` pattern only fires when the percent is followed by context/budget/window/capacity; a bare `"50 %"` with no noun passes. This is a deliberate false-positive/false-negative trade to avoid rejecting legitimate percentages; recorded for completeness, not a defect.
- **N3 (NIT — forward-looking prompt-injection).** The Markdown prompt template offers no delimiter fencing for substituted assignment values. Safe today (assignment author = controller, trusted). If assignment fields ever carry untrusted content (e.g., end-user task text), a crafted value could forge `## Duties`-style sections; fence/escape untrusted substitutions when that day comes.

## Required rework

None for this gate (no blocking or major finding). M1–M4 and N1–N3 are recommended hardening to fold into the follow-up Phase C runtime-enforcement unit that first consumes these schemas (the lease/leak guards graduate from contract-level validation to runtime enforcement there); they do not block acceptance of the schema/definition unit. Per the "PASS with required corrections" convention, the orchestrator may record these as blocking for the runtime unit rather than for M0-T090 acceptance.

## Reviewer conclusion

**PASS (PASS-with-findings).** At frozen content identity `3e726a0fcc3ea574337d8e2166d3710322586806232fc52506372362f820baba` (commit `e8b21d1`), the diff is a pure, inert, fail-closed set of controller-planning schemas with **no actuation surface** (R595 shadow-only preserved — verified), a sound structural R045 no-quota control plus per-field and whole-prompt guards, a structurally-correct R056 envelope-privacy control, conservative stale/unknown handling (R080), genuine tier reuse (R081), clean data hygiene (no path/username in `to_record`, in-memory ledger, deterministic ASCII digests), no new dependency, modularity green, and no sensitive content in a public-repo posture. The four MINOR findings are narrow gaps in defense-in-depth backstops and a documentation/TOCTOU clarification that become relevant only when the later runtime-enforcement unit turns these validators into live enforcement; none is exploitable in this shadow-only schema unit. No critical or high-severity issue. Recommend acceptance, carrying M1–M4/N1–N3 forward to the runtime-enforcement follow-up.
