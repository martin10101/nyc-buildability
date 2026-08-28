# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 19: M0-T094 (unit G) ACCEPTED; NEXT = M0-T093 (unit H1)

1. **Generated:** 2026-08-28T04:00Z · orchestrator session `session_01HfptKuEs3RDxaxsSHJjc7t`
   (the same session that resumed at seq 18 and delivered unit G end-to-end). **Sub-agents in
   flight:** none (3 gate reviewers + DCV all landed, delta-re-attested, and final-identity-acked).
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **19**). Installed CLI 2.1.248.
3. **M0-T094 (unit G) = ACCEPTED** (deliverable `f6edf11` + corrections `db689c8` + prose
   `ca3318d`, final content identity `e893209e`): operator channel — `graceful-stop` +
   `ask` verbs (NEW `operator_ask.py` bounded read-only Codex ask with durable `oper_*`
   request-id fallback + `--show`/`--resubmit`; `operator_channel_cli.py` holds both verbs +
   the moved `open_runtime`/`emit_payload` helpers; cli.py net +34 lines, modularity 0
   failures), section-14 labeled status (`operator_status.py`, unknown-never-zero, `--json`
   redacted after correction C1), additive `durable_state.ask_by_id`, 8 thin user-only
   `/loop-*` skills, feature-detected `loop_command_interceptor.py` (UserPromptSubmit
   selected per the 2.1.248 fixture; UserPromptExpansion honestly UNPROVEN; C3 added a `--`
   separator for `/loop-ask`), R035 alias doc. Matrix 54/54; mutation 10/10 non-equivalent
   killed (1 documented equivalent); composed whole-suite 2971 passed / 3 skipped / 0 failed
   (chunked same-tree; single background runs are EXTERNALLY KILLED on this box — compose,
   and lean on the CI supervisor-bridge run) + CI all green; G0/G2/G3/G4/G5 PASS + delta
   re-attestations + DCV 54/54 PASS, all re-affirmed at the final identity
   (`M0-T094-final-identity-acks.md`).
4. **Residuals carried (non-blocking):** unit-G C1 live interception canary is OWNER-GATED
   (R192/R197 exact-command): zero-context proof + queued-input behavior are
   `pending-owner-C1` in `fixtures/loop_interception_detection_2_1_248.json`; the
   second-terminal CLI is the advertised real-time path (R088). G5 ADVISORY-3 (POSIX
   process-group kill for the hook child) + ADVISORY-4 ([HOME] masking) → M0-T109 backlog.
5. **EXACT next action:** claim M0-T093 (unit H1) via the standard cycle: read its packet
   (`project-control/tasks/M0-T093.json`), G0, prove-first reuse boundary + scenario pack,
   implement, matrix test file, 4-reviewer gates → DCV → accept. Sequence after:
   M0-T095 (H2) → M0-T096 (I golden run; **R187 HOLD after**) → M0-T107 (J). M0-T109
   guard-hardening backlog stays non-blocking parallel.
6. **Accept-mechanics facts (all re-proven this session):** commit BEFORE in-regime submit;
   an allowed_paths report edit AFTER submit moves the identity → rework→resubmit (+ delta
   acks from every verifier); verification.json `reviewed_sha` must equal HEAD at accept —
   restamp it in the WORKING TREE to current HEAD, accept, then commit both together;
   gates recorded after committing reports, `--sha` == live HEAD, original→delta two-step;
   assemble verification rows in the orchestrator from the DCV's machine-parsable lines;
   the correction-round pattern (consolidated fixes → delta re-attestations via SendMessage
   to the SAME reviewer agents) worked twice.
7. **Environmental facts:** long background python runs (pytest, validators) are externally
   killed on this workstation — run in foreground chunks (`test_directive_compliance.py`
   alone needs ~25 min, run it by class groups); never run a mutation pass while a suite
   is in flight (a polluted run was stopped and disclosed in G2).
8. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous-mode
   activation owner-gated (D-024 §18/R595; supervisor SHADOW-ONLY); Amendment-3
   prohibitions; Bootstrap Gate 0 every fresh session; supervisor commits cite
   `D-024-R###`; repo PUBLIC; never `name:` on producers; expansion-planning hold in
   force; guards inside `.claude/hooks` untouchable without G5 (unit G ADDED
   `loop_command_interceptor.py` under its own G5 — the guard packs are untouched).
9. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 19);
   `project-control/tasks/M0-T093.json`; `docs/LEAN_OPERATING_PROCESS.md`.
10. **Stop/change conditions:** Gate-0 failure; validator non-zero; reviewer FAIL/BLOCKED
    (consolidated correction round → delta re-attestations; M0-T094 is the latest worked
    example); anything owner-only (credentials, payment, production, legal, PR #241,
    activation, live-canary exact-command).
11. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD,
    tree, and `/mcp` empty (Bootstrap Gate 0) before any change. Read CLAUDE.md,
    docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the §9 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git + the
    ledger (they win over prose). Continue the campaign seq-19 NEXT: claim and implement
    M0-T093 (unit H1) from its packet — prove-first per R018, scenario pack, matrix test
    file, then the 4-reviewer gate cycle → DCV → accept — and proceed through M0-T095 →
    M0-T096 (golden run; R187 hold after) → M0-T107. Stop for anything owner-only. The
    standard D-010 R113/R114 ~400k rotate-at-seam ceiling governs your session."*
