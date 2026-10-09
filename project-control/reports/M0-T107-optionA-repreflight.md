# Option A executed: wt-m0t107 fast-forwarded + complete section-2 re-preflight + corrected Step-2 command (D-024-R417/R418/R419)

Orchestrator, 2026-08-31, session `session_01SfXcRw7emzdojCDJmKxNTM`. Authority:
Amendment 27 (`source-027-amendment.md`, owner reply "a" selecting OPTION A of the
seq-57 decision; rows R417-R419; validator EXIT=0 at capture).

## 1. The authorized R417 act (one-time narrow R413 lift)

`git -C wt-m0t107 merge --ff-only c5c6ff7` — branch `task/M0-T107-plugin-portability`
fast-forwarded `796e18f` -> `c5c6ff7` (the Amendment-27 capture commit; pure
fast-forward, ancestry pre-proven). Worktree clean BEFORE and AFTER; only that branch
ref moved; the control branch, packet content authority, PR #241, and the journal were
untouched. Its ledger copy now reads M0-T107 `claimed` — the exact fact
`probe_task_authority` corroborates. No other wt-m0t107 change was made; the R413 hold
otherwise stands. (wt-m0t107 sits 2-3 control-plane commits behind the final pushed
tip — report/campaign commits only; the probe compares task_id + status, identical at
both identities, so the residual lag is immaterial and disclosed.)

## 2. Complete section-2 preflight, re-run after the fast-forward (R418)

| # | Row | Result |
|---|---|---|
| 1 | tree clean; HEAD == origin tip; CI green | **PASS** — verified at the pushed seq-58 tip; CI conclusions checked live post-push (session record); material identity unchanged (`de18f27`) |
| 2 | `HEAD:tools/agent_supervisor` | **PASS** — `b392100930bd4213cab90eb02aafa6d0d568f849` |
| 3 | CLI identities | **PASS** — claude.exe 2.1.251 `d6f6c29a8ac6b3cf...` (217,360,032 B, undrifted); codex-cli 0.146.0 |
| 4 | `verify-controller` | **PASS** — "controller verified, including the external config.toml binding" |
| 5 | `doctor` | **PASS** — overall PASS; OS-ACL PROTECTED; journal integrity ok (transitions 23 = the owner's Step-1 clear-recovery; audit 55 = +2 rows from the owner's refused Step-2, both owner acts, no orchestrator journal writes) |
| 6 | `supervisor_command_doc_check.py` | **PASS** — 12 commands, 0 failures, exit 0 |
| 7 | `wt-m0t107` | **PASS** — clean at `c5c6ff7`, branch `task/M0-T107-plugin-portability` (identity updated by the owner-authorized R417 fast-forward; supersedes the `796e18f` preservation row) |
| 8 | queue + section-3 prerequisites | **PASS** — real-engine verdict ELIGIBLE re-confirmed post-ff; queue sha256 `11eaa5a7...` and packet digest `371bed1a...` UNCHANGED |

**Corrected-shape semantics, proven LIVE against the post-ff worktree:**
`probe_task_authority(packet, repo_root=wt-m0t107)` -> **PASS** ("claimed in both the
packet and the ledger, no open blocker");
`enforce_launch_bindings(wt-m0t107, wt-m0t107, wt-m0t107, ctl24)` -> **ALLOWED**;
corrected Step-2 parses via `build_parser()` and `dispatch_inputs_missing` -> **EMPTY**
(R408 re-discharged). Journal rests at **PREFLIGHT** — Step 1 does NOT need re-typing
(R419).

## 3. The corrected Step-2 command (ONE value changed: `--repo`; OWNER-TYPED ONLY)

`! python -m tools.agent_supervisor start --mode limited-auto --owner-enable-bounded-auto --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 --repo C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107 --branch task/M0-T107-plugin-portability --worktree C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107 --max-cycles 3 --max-tasks 3 --packet-queue C:/Users/MLFLL/Downloads/nyc-zoning/commissioning-queue.json --claude-executable C:/Users/MLFLL/.local/bin/claude.exe --codex-executable C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd --task-packet project-control/tasks/M0-T107.json --config "C:/Program Files/SupervisorConfig/config.toml" --model-selection C:/SupervisorController/model_selection.toml --manifest C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json`

Semantics unchanged from `M0-T129-commissioning-protocol.md` section 4 (evidence and
the Codex reviewer now bind to the WORKER'S tree — the D2-correct shape). Any live
failure: R394 — stop without retry, preserve byte-for-byte, one consolidated
assessment. The orchestrator never executes this command (R409/R414/R419). Standing
gates untouched; never merge PR #241. Option B (the AD-093 probe-root defect task —
`task_authority` should arguably read the ledger from `--checkout`, not `--repo`)
remains a follow-up candidate regardless of this journey's outcome.
