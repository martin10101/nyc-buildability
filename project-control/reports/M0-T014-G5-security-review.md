<!-- Verbatim reviewer return (agent-return channel; agentId aab3369bdbb4135d9, security-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. -->

# Gate Report

- Gate ID: G5 (Security and privacy)
- Task ID: M0-T014 — Project-control CLI hardening (owner code-audit P0)
- Reviewer: security-reviewer (independent; not the producer)
- Producer: backend-engineer
- Result: **PASS**
- Clean environment/worktree used: yes — reviewed branch `task/M0-T014-control-hardening` @ `3e5e6e5` in `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T014`; all probes executed against disposable temp-project copies only; no ledger writes, no git writes, no gh (ADR-005).

## Acceptance criteria reviewed

Task packet `project-control/tasks/M0-T014.json` scenarios S1–S7 plus the seven G5 security charges from the dispatch: spoofing surface, G2 bypass analysis, path containment, atomic writes, fail-closed behavior, secrets/dependencies, regression.

## Steps independently executed

1. Read full diff scope (`git diff main...HEAD --stat`): exactly the three allowed files — `tools/project_control.py` (687 diff lines), `tools/test_project_control.py` (860), `project-control/reports/M0-T014-producer-report.md` (355). No forbidden paths touched.
2. Line-by-line read of `gate()` and `accept()` code paths (bypass analysis).
3. Ran the producer's suite myself: `python tools/test_project_control.py` in the worktree → all 9 groups OK, **exit code 0**.
4. Ran 15 self-authored adversarial probes (new vectors not in the suite) against a temp-project copy of the CLI. All 15 behaved fail-closed or as documented.

## Findings table (charge → evidence → result)

| # | Charge | Evidence (file:line, worktree-relative) | Result |
|---|---|---|---|
| 1a | Honest-identity documentation | `tools/project_control.py:6-12` (module docstring "IDENTITY IS PROCEDURAL, NOT CRYPTOGRAPHIC"), `:559-569` (argparse epilog), `:590-627` (per-argument help); asserted by `test_docs_honesty` (`tools/test_project_control.py:837-851`) | PASS |
| 1b | Producer accepting own task | `:459` `if a.agent != "orchestrator": fail`; test `:720-721` | PASS (rejected in code) |
| 1c | Producer gating own task | `:391` reviewer==producer rejected; `:397-399` unrostered rejected — rejection is in code, not only tests; tests `:464-466`, `:724-726` | PASS |
| 1d | Self-review via renamed --agent | roster membership check `:393-399` rejects any name not in `reviewer_agents`; even a rostered producer is rejected (`:391` runs first; test `:474-480`) | PASS |
| 1e | Producer progress→100 / status accepted | `:310-311` percent 0–99; `:600-602` argparse choices exclude `accepted`; `:313-315` in-code defense in depth; tests `:734-742` | PASS |
| 2 | G2 narrowness / no bypass branch | `gate()` `:377-400`: three exhaustive branches keyed on frozensets over argparse-restricted gate ids; `role` is **derived**, never caller-supplied; no flag, no default-permit path. `accept()` `:479-489`: for G1/G3/G4/G5/G6 a record with `role: self_check` is rejected (`:481-483`), any other non-`independent_review` role rejected (`:484-486`), reviewer==producer re-checked at accept time (`:487-489`). The CLI cannot write a G1/G3/G4/G5/G6 record with role `self_check` (role follows gate class), and gate files are per-(task, gate-id) so a G2 record can never occupy an independent gate's slot. Structurally confirmed: **no general reviewer-validation bypass exists** | PASS |
| 3 | Path containment on every subcommand | Task id regex `:82`, enforced via `load_task` on claim/progress/submit/gate/accept (`:214-223`), explicitly in `new_task` incl. `--depends` (`:257-264`); `task_path()` raises on unvalidated id (`:171-175`). Report path validation `:181-211` (relative-only, both separators split, no `.`/`..`, drive/drive-relative/UNC/absolute rejected, `is_relative_to` resolve double-check) applied on submit (`:346`) and gate (`:401`). Gate ids argparse-restricted `:616`; checkpoint ids `:83`, `:528-530`. `status`/`init` take no path args | PASS |
| 4 | Atomic writes | `save()` `:141-159`: serialize first, `mkstemp` in destination dir, `os.replace` with bounded Windows-sharing retry (`:129-138`), temp unlinked on any failure; reader-side `PermissionError` retry `:117-126`. Interrupted-write and serialization-failure behavior proven by S5 (`test:669-699`); concurrency harness green. Symlink/rename races: mkstemp has no predictable name; pre-placing a symlink at the destination requires repo write access, which already equals full ledger control — out of threat model for a local single-user procedural tool. Realistic assessment: adequate | PASS |
| 5 | Fail-closed on corrupt ledger | Blocker scan: unreadable JSON → explicit fail-closed reason `:504-507`; missing/empty status → blocking `:509-510`. My probes: corrupt gate record at accept → traceback, exit 1, task NOT accepted; corrupt task file → exit 1; blocker file that is a JSON *list* → `AttributeError`, exit 1, task not accepted. All fail closed (some via crash rather than a clean reason — see D3) | PASS (with low-severity note D3) |
| 6 | Secrets/logging/dependencies | Imports `:76-77` stdlib only (argparse, datetime, json, os, re, sys, tempfile, time, pathlib); test file stdlib only. No network, no env reads, no secrets handled or printed; output is ids/statuses only | PASS |
| 7 | Regression | `python tools/test_project_control.py` run by me in the worktree: 9/9 groups OK, exit 0, incl. S7 (115 real ledger files parse; 21 accepted tasks visible; legacy role-less records still accept) | PASS |

## New-vector attempts and outcomes (reviewer-authored probes, all in temp project)

| Vector | Outcome |
|---|---|
| G2 with reviewer `"orchestrator "` (trailing space) | Rejected (exact-match, fail-closed) |
| G3 with reviewer `"reviewer-y "` / `"Reviewer-Y"` (whitespace/case) | Rejected (roster is exact-match) |
| `accept --agent "orchestrator "` | Rejected |
| Gate for nonexistent task `M9-T999` | Rejected ("Unknown task"), no file created |
| Overwrite semantics: G3 PASS → FAIL by rostered reviewer | Allowed with same validation rules; prior record preserved in `history` (`:409-414`); latest record is authoritative. Gates can NEVER be recorded on a terminal task (`:372-373`), so a post-acceptance flip is impossible via the CLI |
| Reviewer records G3 on unclaimed task, then claims the task itself | Gate recorded (producer None, vacuous check), but **accept-time recheck `:487` caught it** — accept rejected. Defense in depth works |
| NTFS ADS report path `probe.json:stream` | Passes structural containment (still inside reports/), then rejected at `exists()` because the stream does not exist; tool never writes to report paths. No escape (see D4) |
| Corrupt gate record / corrupt task file at accept | Traceback, exit 1, task not accepted — fail-closed |
| Blocker file containing a JSON list | AttributeError, exit 1, accept rejected — fail-closed (ugly, see D3) |
| `new-task --gates "G9,bogus"` (unvalidated gate names) | Task created but permanently unacceptable (no record can ever be produced for `bogus`) — fail-closed (see D2) |
| Rework-id gate cross-match (`M9-T906` gates satisfying `M9-T906-R1`) | Rejected — glob `{task_id}-G*.json` cannot cross-match between base and rework ids |
| `"orchestrator"` placed on `reviewer_agents` roster | An independent gate CAN then be recorded by reviewer `"orchestrator"` with role `independent_review` (see D1) |

## Regression/security/provenance findings

- Gate records now carry an honest `role` field and full overwrite `history` — provenance improved.
- Terminal-task immutability closes the pre-existing demotion hole (submit/gate could previously knock an accepted task back).
- Backward compatibility is validate-on-write by explicit design; legacy role-less records satisfying accept is a documented, owner-directed tradeoff (packet input 4), not a defect.
- Inherent residual (documented in-tool, correctly): `--agent`/`--reviewer` are unauthenticated labels and anyone with filesystem write access can edit ledger JSON directly. The tool's rails are integrity checks on the ADR-005 procedure, not an authentication boundary. This is stated honestly in docstring, epilog, and per-argument help.

## Defects

| ID | Severity | Blocking | Description | Remediation |
|---|---|---|---|---|
| D1 | Low | NO | If a task packet lists `"orchestrator"` in `reviewer_agents`, the CLI records an independent gate (G1/G3/G4/G5/G6) by reviewer `"orchestrator"` with role `independent_review`, blurring the self-check/independent class boundary. Requires an orchestrator packet-authoring error; within the procedural trust model. Repro: `new-task --reviewers reviewer-y,orchestrator`, then `gate --gate-id G3 --reviewer orchestrator --result PASS` → exit 0 | In `gate()` independent branch, reject `--reviewer orchestrator` (or reject `"orchestrator"` at roster authoring in `new_task`) |
| D2 | Low / informational | NO | `new-task --gates` accepts arbitrary gate names; a task with an unknown required gate is silently unsatisfiable (fail-closed, but a confusing dead end). Repro: `new-task --gates G9,bogus` then any accept | Validate `--gates` entries against `GATE_IDS` in `new_task()` |
| D3 | Low / informational | NO | Corrupt task/gate JSON or non-dict blocker files at accept fail closed via unhandled traceback (exit 1) rather than a clean fail-closed reason; a corrupt `state.json` in `sync_state()` after a successful accept write yields exit≠0 with the task already accepted (partial-success signaling). No integrity impact | Wrap accept-path `load()` calls and `_blocker_references` input in try/except mirroring the existing blocker handler; optionally warn-and-continue in `sync_state` |
| D4 | Informational | NO | ADS-form report names (`name.json:stream`) pass structural validation (they remain contained in reports/ and the tool never writes report paths); they are only usable if such a stream already exists | Optionally reject `:` in report-path components for tidiness |

No critical or high findings. **No contract-breaking or architectural defect found** — the gate-class structure, accept preconditions, and terminal immutability match the packet contract exactly, and the S7 backward-compatibility contract (validate-on-write, no retro-rejection of the 21-accepted ledger) is proven against a copy of the real ledger.

## Required rework

None blocking. D1 and D2 are recommended hardening follow-ups suitable for a minor rework or a future hygiene task; D3/D4 are optional polish. None gate acceptance.

## Reviewer conclusion

The hardened CLI structurally rejects every spoofing vector in the packet's S6 matrix in code (not just tests), the G2 self-check rule is narrow with no bypass branch (role is derived, accept re-validates role AND reviewer≠producer), containment is enforced on every id/path-taking subcommand, writes are atomic with proven interrupted-write behavior, and corrupt-ledger conditions fail closed. Fifteen reviewer-authored adversarial probes beyond the suite all behaved correctly. Suite rerun independently: exit 0.

Key evidence paths (absolute):
- `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T014\tools\project_control.py`
- `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T014\tools\test_project_control.py`
- `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T014\project-control\reports\M0-T014-producer-report.md`

PASS
