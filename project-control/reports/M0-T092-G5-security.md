# M0-T092 — G5 independent security review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
(report-preservation rule; transport entity-decoding only). Reviewer: security-reviewer
(read-only). Recorded by: orchestrator.

---

# Gate Report

- **Gate ID:** G5 (independent security review)
- **Task ID:** M0-T092 — D-024 Phase D unit F (controller state machine, safe seams, exact-once succession, outage handling)
- **Reviewer:** security-reviewer (read-only)
- **Producer:** fable-orchestrator-session
- **Result:** PASS (with LOW/ADVISORY defense-in-depth notes; none blocking)
- **Clean environment/worktree used:** Reviewed at deliverable content identity `b940c90`; live HEAD `8234479` carries only control-plane records (in-regime submit + G2 self-check) on top. All source re-derived from the committed tree via `git show b940c90:...`, not from the producer's conclusions.

## Acceptance criteria reviewed

Security scope only (the full 65-requirement directive pass is the `directive-compliance-verifier`'s lane, recorded in `verification.json`). I independently verified the seven named security focus items against the actual diff: public-repo hygiene, fail-closed integrity, authority boundaries, injection surfaces, worker protection (R045), dependency policy, and supervisor-freeze compliance.

## Directive/requirement verification (security-relevant subset, re-derived at b940c90)

| Requirement ID | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| R102 (Phase-D freeze / evidence citation) | b940c90 | PASS | Cited in packet objective, commit message, and every new module docstring; guard packs in `forbidden_paths` and untouched (diff name-list carries no `.claude/**`). |
| R028/R030/R031 (bounded epoch lease, single-winner, crash recovery) | b940c90 | PASS | `epoch_lease.py` CAS via `durable_state.compare_and_swap_state` inside `BEGIN IMMEDIATE`; live-predecessor never taken over (`epoch_lease.py:245-251`); malformed lease refused (`:102-119`). |
| R026/R027 (owner stop-intent + precedence) | b940c90 | PASS | `stop_intent.py` emergency>graceful>pause; non-owner clear refused (`:97-102`). |
| R033 (transient/blocking, bounded backoff, bounded idle) | b940c90 | PASS | `outage_policy.py` unknown->BLOCKING (`:92-98,101-111`), attempts bounded (`:156-161`), idle ceiling (`:292-297`), split permissions (`:327-343`). |
| R125–R128 (Bootstrap Gate 0) | b940c90 | PASS | `bootstrap_gate.py` unknown MCP/root/added-dir all fail closed; `may_write`/`assert_may_write` gate writes. |
| R066 (children-reconciled seam) | b940c90 | PASS | `rotation.py` additive `children_unreconciled` in `UNSAFE_MOMENT_CHECKS`; `turnover_seam.py` wires `unreconciled_children`. |
| R021/R022/R023 (Codex read-only boundary) | b940c90 | PASS | No reviewer-authority/argv/flag change in diff; no mutation path added. |

## Steps independently executed

1. Enumerated the 23 changed files in `b940c90`; read all four new modules and every additive edit (`durable_state`, `state_machine`, `rotation`, `turnover_seam`, `event_drift`) in full from the committed tree.
2. **Hygiene scan** across every added line for `MLFLL`, `C:\Users`, `/Users/`, `myhappybook`, `sk-ant`, `Bearer`, `session_01H`, and 32+/40+ char token runs — zero raw-identifier hits (only sha256 help-text hashes, test names, and the standard `Claude-Session` commit trailer).
3. Read all three new fixtures and all four reports; scanned the 130-line pytest log for `rootdir`/absolute paths.
4. Confirmed the four new modules' import graph (only `test_agent_supervisor_controller_succession.py` imports them — no live-loop wiring) -> SHADOW-ONLY holds.
5. Grepped new/edited modules for `subprocess|socket|urllib|requests|os.system|exec(|eval(|Popen` and for R045 scarcity language (`token|remaining|countdown|quota`).
6. Confirmed guard packs / hooks / settings / requirements / lockfiles absent from the commit's file list.

## Expected versus actual

- **Public-repo hygiene:** Expected [HOME] masking to hold on live-captured artifacts. Actual: PASS. `capability_probe_live_2026-08-27_m0t092_2_1_248.json` stores binaries as `[HOME]\.local\bin\claude.EXE` etc. and help text as `output_sha256` only (never raw help output, which could carry paths). The `native_runtime_detection` and `hook_event_catalog_2_1_248` fixtures carry only flag/verb/event names, version strings, and `[HOME]`-masked references. Reports and the suite log are clean; the single path-like hit in the log (`M0-T092-full-suite-T1.txt:45`) is already `[HOME]\AppData\Roaming\npm\codex`. The one raw path in the repo (`project-control/tasks/M0-T092.json` `worktree: C:/Users/MLFLL/...`) is **pre-existing** (present at parent `4002a2c`), a control-plane convention, and not introduced by this diff — the git author email is likewise already in every commit. Not a new leak.
- **Fail-closed integrity:** Expected every uncertain path to refuse. Actual: PASS on all four named surfaces (bootstrap_gate, outage_policy, epoch_lease, stop_intent). The CAS primitive correctly distinguishes stored-JSON-`null` from absence (`expected is None` => row-absent only), backed by test `test_a_stored_null_is_not_absence`.
- **Authority boundaries:** Expected no weakening of guards/SHADOW-ONLY/Codex boundary and no new dangerous surface. Actual: PASS. New modules import only `dataclasses`/`typing` + local modules; no subprocess/network/exec anywhere; the sole `state_machine.py` "subprocess" string is a pre-existing transition description, not code.
- **Worker protection (R045):** PASS. No token countdowns/quotas in any composed text; the two `budget` hits are a clock-module reference and a docstring about bounded *retry attempts*, both supervisor/owner-facing, not worker-facing.
- **Dependency policy:** PASS. Zero new dependencies; no requirements/lockfile touched.
- **Supervisor-freeze:** PASS. R102 cited in packet + commit + docstrings; scope stays within `tools/agent_supervisor/**` and the four test files added to `allowed_paths` (state-count and drift-pointer updates only). Module sizes 149/180/343/375 SLOC — all under the 600 warn threshold; no dumping-ground modules.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\bootstrap_gate.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\epoch_lease.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\outage_policy.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\stop_intent.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\durable_state.py` (added `compare_and_swap_state`)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\capability_probe_live_2026-08-27_m0t092_2_1_248.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\native_runtime_detection_2026-08-27_m0t092.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\hook_event_catalog_2_1_248.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_controller_succession.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T092-controller-succession.md`

## Regression/security/provenance findings

No CRITICAL, HIGH, or MEDIUM findings. Three LOW/ADVISORY defense-in-depth notes, all mitigated by the SHADOW-ONLY posture (none of the four new modules is wired into any live-dispatch path yet — verified) and therefore non-blocking:

- **LOW-1 — `outage_policy.classify_reason_text` transient-first keyword ordering can misclassify BLOCKING->TRANSIENT.** `outage_policy.py:59-72,101-111`. `_REASON_KEYWORDS` is scanned transient-causes-first with first-match-wins, so a genuine blocking failure whose bounded reason string also contains a transient token is classified transient and enters the retry loop. Concrete case: `provider_failure_reason` = `"Authentication error: connection refused by auth endpoint (401)"` -> `"connection"` (network) matches before `"authentication"`/`"401"` -> returns `("network", TRANSIENT)`, so a real auth failure is retried instead of immediately blocked-with-handoff. Impact is bounded: `max_attempts` caps the wasted retries and it then escalates to `record_blocked_with_handoff`, and the module's own docstring already prescribes the safe path ("a caller that KNOWS the cause passes it directly to `classify_cause` and never sniffs text"). Remediation before this module drives any live dispatch: evaluate BLOCKING keywords before TRANSIENT, or gate the dispatch decision on an explicit `classify_cause(known_cause)` and treat text-sniffing as advisory-only. Add a collision test (auth text containing `connection`/`timeout`/a 5xx code) alongside the existing `test_the_classification_is_closed_and_fails_closed`.
- **ADVISORY-2 — `outage_policy` persists the `reason` string verbatim.** `outage_policy.py:213-216,259-266`, and `epoch_lease`/`stop_intent` audit `detail`. Reason/notes are written into the durable journal and audit log without re-redaction; the module relies on the documented contract that its input is the already-bounded/redacted `codex_reviewer.provider_failure_reason` output (report §S11 confirms this boundary). Both sinks are local (SQLite journal / audit log, not committed), so this is a boundary-hardening note, not a leak: keep the invariant that callers only ever pass the redacted `provider_failure_reason` string, never raw provider text.
- **ADVISORY-3 — `bootstrap_gate` diagnosis echoes inputs unsanitized.** `bootstrap_gate.py:123-135`. `actual_launch_directory`, `intended_worktree_root`, `dirty_uncommitted_paths`, and `attached_mcp_servers` are copied verbatim into the diagnosis dict that a failed Gate 0 renders to a terminal/report. Control characters or ANSI escapes in a cwd or a crafted MCP-server name would pass through to the display layer. Very low likelihood (inputs originate from the owner's own environment), consistent with the codebase's existing diagnosis pattern; note for whoever renders the diagnosis to escape it. The related `reached_via_added_dir` default of `False` is acceptable — the primary `canonical_checkout_path` cwd-equality check independently catches added-dir access, so the flag is redundant belt-and-suspenders, not a fail-open.

## Defects

None blocking. The three items above are non-blocking hardening notes to address before any of these modules is wired past SHADOW-ONLY.

## Required rework

None required for G5. Recommended (non-blocking, to land before live wiring under a future R595 activation): fix LOW-1 keyword ordering / prefer explicit `classify_cause` for dispatch decisions, and add a collision-classification test.

## Reviewer conclusion

The diff is a clean, additive, fail-closed extension that preserves every security-relevant invariant: guard packs, hooks, settings, and the Codex read-only boundary are untouched; the four new modules are pure stdlib libraries with no subprocess/network/exec surface and are not yet wired into any live loop (SHADOW-ONLY / R595 posture intact); zero new dependencies; supervisor-freeze evidence (D-024-R102) is cited in packet, commit, and every module docstring, with scope confined to `tools/agent_supervisor/**`. Public-repo hygiene holds — all three live-captured fixtures and all four reports are `[HOME]`-masked and store help text as sha256 only; the single raw user path in the repo is a pre-existing control-plane field, not introduced here. Fail-closed integrity is verified on every named path (unknown MCP/launch-root/added-dir, unknown/exhausted outage causes, CAS-loss, live-predecessor takeover, malformed stored lease, non-owner stop clears). The only findings are LOW/ADVISORY defense-in-depth notes that are bounded and moot while shadow-only.

VERDICT: PASS
