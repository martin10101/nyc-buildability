<!-- Saved VERBATIM by the orchestrator from the directive-compliance-verifier agent-return
     channel (transport entity-decoding only). Verified at HEAD 91d38a4, material identity
     7d8195b. -->

All required harness outputs are green:
- `validate_directive_compliance.py --check` → EXIT=0
- `test_directive_compliance.py` → 120 tests, OK, EXIT=0
- `test_project_control.py` → 23 groups OK, EXIT=0
- `test_directive_reminder.py` → 12 tests, OK, EXIT=0

I have completed independent primary-evidence verification of all 8 applicable requirement rows. Here is my report.

---

# DCV GATE REPORT — M0-T120 (D-024 Amendment 14: shell-routing compatibility)

**Verifier:** directive-compliance-verifier (independent, read-only; producer ≠ verifier)
**Reviewed identity:** material commit `7d8195b454d956cc739cbed4d422828ea2f5645b`; current HEAD `91d38a4` — the intervening commits (`a0c48b0`, `e00aab2`, `91d38a4`) are control-plane only. I confirmed `git diff --name-only 7d8195b HEAD -- tools/` is **empty**, so production content is byte-stable across the gate wave (path-scoped content identity verified).
**Delta:** `git show --stat 7d8195b` = **14 files, +2165/-8**; production files limited to `claude_runner.py`, `golden_run.py`, `recovery_probes.py`, `routing_probe.py`, `start_gate.py`, new `prompts/claude_native_tools.md`, new fixture. `policy.py`, `broker.py`, `cli.py`, `process.py`, production `command_authority` NOT in the delta.
**Registry integrity:** `validate_directive_compliance.py --check` EXIT=0 (source digests match, locked requirement IDs enforced, Amendment 14 reflected). Applicable rows for M0-T120 = the 8-row resolver set R289–R296 (R297 applies to M0-T119 only). Forward-trace in `source-014-amendment.md` is one-to-one (9 sentences → R289–R297); requirements.json carries exactly R289–R297 at `amendment_sequence: 14` — no missing/invented/combined rows.

## Per-requirement verdicts (primary evidence reproduced)

**D-024-R289 — Finish M0-T118 through DCV + acceptance — PASS**
Primary evidence I reproduced: `project-control/tasks/M0-T118.json` status=`accepted`, accepted_at 2026-08-29T21:23:16Z. `verification.json` M0-T118 block = 5 rows (R277/R279/R280/R281/R282) all `state: PASS`, `verified_by: directive-compliance-verifier`, reviewed_sha `69e1d04`. Accept commit `5251c73` exists (`git show`), message "ACCEPTED (5-row DCV verification PASS … gates G0/G2/G3/G4/G5 PASS)". M0-T118 gate records G0/G2/G3/G4/G5 all `result: PASS`. **Timing honesty confirmed:** accept commit `5251c73` (2026-08-29 17:23:17 -0400) PREDATES the Amendment-14 capture commit `47f9037` for `source-014-amendment.md` (17:43:16 -0400), and `5251c73` is an ancestor of the amendment base `85cbcc4` (`git merge-base --is-ancestor` = YES). The timing disclosure is honest. *Non-material note:* the disclosure's "~35 minutes earlier" for the M0-T119 claim is loose — the claim commit `85cbcc4` is 17:24 vs the amendment commit 17:43 (~19 min by commit time); this describes owner-message arrival, not commit time, and does not affect R289.

**D-024-R290 — Reconcile bashFirst / issue #88041 — PASS**
The reconciliation finding is recorded in `source-014-amendment.md` (lines 20-30). I independently grepped `project-control/tasks/` + `project-control/directives/` for `bashfirst|bash-first|shell-first|shell-routing|88041|native-tool-routing`: matches are ONLY Amendment-14-era files (`M0-T120.json`, `source-014-amendment.md`, `manifest.json`, `requirements.json`) plus `M0-T119.json` — and M0-T119's sole match (line 86) is the R297 HOLD reference (contemporaneous, not a prior resolving task). ZERO prior tasks addressed shell-first worker routing → gap genuinely missing. Gap resolved empirically: the measured fixture exists with a genuine verdict (`native_preferred`, 3 native / 0 shell).

**D-024-R291 — Separate bounded task before T119 completes — PASS**
M0-T120 has its own packet (task_id M0-T120), own worktree (`wt-m0t120`), own commits (material `7d8195b`, cherry-pick of worktree `4e0d307`). M0-T119 still held: `project-control/tasks/M0-T119.json` status=`claimed`, progress 15%, R297 HOLD recorded in its progress_log (line 86). No T119 submission/gates since the hold — only `M0-T119-G0.json` exists; no G2/G3/G4/G5 records for M0-T119.

**D-024-R292 — Empirical routing proof at 2.1.251 under exact live config — PASS**
Fixture `tools/agent_supervisor/fixtures/shell_routing_2026-08-29_m0t120_2_1_251.json`: `measured:true`, `provider_calls_made:3` (ceiling 3), `no_worker_file_write_observed:true`, `claude_version "2.1.251"`, tool stream Grep(native)→Read(native)→Edit(native, `brokered:true`, present in `brokered_denials`, `files_written:false` = denied), `verdict native_preferred`. I independently re-hashed the installed binary via `process.executable_identity('C:/Users/MLFLL/.local/bin/claude.exe')` → digest `d6f6c29a8ac6…889ed8` = the fixture `cli_identity` EXACTLY. `routing_probe.py` uses `build_argv` (L395) + `claude_child_env` (L401) + delegates to `deny_everything` (L157); `MAX_PROVIDER_CALLS=3` with a backstop (L66/L436) — the certified construction.

**D-024-R293 — Broker/owner gates preserved; nothing broadly allowed — PASS (prohibition honored)**
`git show 7d8195b --name-only` confirms `policy.py`/`broker.py`/`cli.py`/`process.py` are NOT in the delta (byte-untouched). The 13 Windows-shape additions (`WindowsShapeCoverageTests` + `test_finding_f1_*`/`test_finding_f2_*`) — I ran them: **13 passed** — assert ASK or HARD_DENY, never AUTO. F1 (`… | sh` → ASK) and F2 (`powershell -Command "Remove-Item -Recurse …"` → ASK) are recorded-not-fixed with pinning tests asserting current ASK behavior; both remain gated, never AUTO. No new AUTO class, no classifier loosening.

**D-024-R294 — Native-tool preference; validation brokered — PASS**
`prompts/claude_native_tools.md` exists: names native Read/Grep/Glob/Edit/Write, routes validation exclusively through the packet's `documented_test_commands`, and states it carries no quota/percentage/countdown (worker-text-clean, D-024-R045). Folded into `build_checkpoint_contract` (`claude_runner.py:888-913`, appends `NATIVE_TOOLS_GUIDANCE` at L913). I ran the guidance-appended-exactly-once + worker-text-clean tests → **2 passed**.

**D-024-R295 — Pre-dispatch drift tooth — PASS (my independent judgment)**
`start_gate.py:228-231` ANDs `cli_capability_manifest` with `answers["shell_routing"].passes` when `mode == MODE_LIMITED_AUTO`; identity source `_claude_identity_digest` (L94-107) = `executable_identity(...).digest` (file hash, no spawn), supplied as `installed_cli_identity` (L197). Fails closed on absent/stale/undetermined. Gate-level tests I ran: `ShellRoutingGateFold` **5 passed**; golden `routing_tooth_bites` **1 passed** (certified start REFUSES with evidence cleared → `UNSAFE_OR_DRIFTED`, `dispatched:false`). **Independent judgment on the mode-scoping ruling:** I verified in `loop.py` that `unattended` is true iff `mode == MODE_LIMITED_AUTO` (L354), `forwards` = supervised-or-limited-auto (L342, shadow forwards nothing), and `OWNER_GATED_MODES == (MODE_LIMITED_AUTO,)` (L143). Limited-auto is therefore the ONLY unattended self-forwarding mode; supervised holds every prompt for a human, shadow forwards nothing — so the only path by which changed shell-routing could *silently* enter a certified run is limited-auto, exactly the scoped mode. R295's text ("cannot silently enter a certified run") is satisfied; the tooth still runs and reports its verdict in every mode, only the hard gating effect is scoped. Recorded forward-looking caveat (G4-MINOR-3 / G5-SEC-INFO-3): the fold hardcodes `== MODE_LIMITED_AUTO` rather than set-membership, so a hypothetical future unattended mode would escape — the invariant holds today; non-blocking for this identity.

**D-024-R296 — Keep separate; single recert at one final identity — PASS (sequencing honored)**
Unit is separate (own commits `4e0d307`→`7d8195b`, own packet/reviews). Consequence recorded (supervisor tree + golden blob move, certified by the single M0-T119 recertification): packet `scope_extension_note`, producer report §6e, evidence-map R296 row. M0-T119 not yet run (status claimed, only G0); M0-T120 not yet accepted — the single recert has not consumed the final identity, sequencing intact.

## Gate records and carried notes
G0 PASS (`47f9037`), G2 PASS (`7d8195b`), G3 PASS (code-reviewer), G4 PASS (qa-engineer), G5 PASS (security-reviewer) — all recorded. Carried non-blocking items are **recorded, not hidden**: F1, F2 (SEC-MINOR wrapper-evasion), F-LIVE-1 (2.1.251 reports `permissionMode=default` despite `--permission-mode manual`; mutating tools still brokered+DENIED, no write), mode-invariant regression guard (G4-MINOR-3/G5-SEC-INFO-3), and report-hygiene counts (G4-MINOR-1/MINOR-2).

**G4 MINOR-2 judgment (stale intermediate counts):** `routing-evidence.md` §3 (`routing_probe 27`) and §4 (`2773/2/2775, +49`) are stale intermediate snapshots that contradict the final authoritative §6b / producer self-check (`2780/2/2782, +56`). This does NOT block any requirement row: the correct final numbers are present in the same report (§6b), were independently reproduced by all three reviewers (G4 full suite 2782/2780/2/0), and no requirement is proven by a written count — each row is verified by the fixture, the delta, the source folds, and removal-sensitive tests I re-ran directly. Acceptable as a carried report-hygiene note.

## Prohibited-action evidence
M0-T120 status = `awaiting_gate`, NOT in `accepted_tasks` (132 accepted; M0-T120 absent). M0-T119 NOT accepted (held). No merge commits in `7d8195b..HEAD` (all control-plane). Nothing accepted/merged/dispatched/deployed/installed/purchased/closed — this DCV precedes acceptance.

## Relevant absolute paths
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/directives/D-024-fable-codex-loop/source-014-amendment.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/directives/D-024-fable-codex-loop/requirements.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/directives/D-024-fable-codex-loop/verification.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/tasks/M0-T120.json`, `.../M0-T119.json`, `.../M0-T118.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T120-evidence-map.json`, `.../M0-T120-producer-report.md`, `.../M0-T120-routing-evidence.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T120-G3-code-review.md`, `.../M0-T120-G4-qa-review.md`, `.../M0-T120-G5-security-review.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/fixtures/shell_routing_2026-08-29_m0t120_2_1_251.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/routing_probe.py`, `.../start_gate.py`, `.../claude_runner.py`, `.../recovery_probes.py`, `.../loop.py`, `.../prompts/claude_native_tools.md`

**Every one of the 8 applicable rows (R289, R290, R291, R292, R293, R294, R295, R296) = PASS. All required gates PASS. All harness outputs green.**

**DCV VERDICT: PASS at 7d8195b**
