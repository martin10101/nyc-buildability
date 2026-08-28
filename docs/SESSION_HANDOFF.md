# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 23: M0-T096 (unit I) ACCEPTED; D-024 Amendment 8 captured; NEXT = M0-T110

1. **Generated:** 2026-08-28 ~20:00Z (header finalized ~20:45Z) · orchestrator session
   `session_01HfptKuEs3RDxaxsSHJjc7t` (the seq-22 successor). **Turnover reason
   (verbatim):** owner invoked `/session-handoff` with no stated reason — landed at the
   clean seq-23 acceptance seam already reached under the standard D-010 R113/R114
   rotate-at-seam ceiling (same pattern as seq 20→21→22→23). **Sub-agents in flight:**
   none (all four reviewers — G3 code-reviewer, G4 qa-engineer, G5 security-reviewer,
   DCV — completed their bounded assignments AND their delta re-attestations naturally;
   reports committed verbatim; no producer or background task is running). **CI on the
   tip `5615d3e`: all checks green** (confirmed complete; the corrected-identity wave
   `6dede15` was 20/20 green, and the reviewed wave `1a935fb` was 20/20 green).
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **23**).
3. **M0-T096 (unit I) = ACCEPTED** (deliverable `5ff7f08`, corrections `635fac5`, gate wave
   at `9f93587`, manifest `0d999749`): `golden_run.py` (disposable-checkout harness, exact
   owner-command argv, sequenced fake providers with REAL git effects, INJECTED marker) +
   `live_observation.py` (Amendment-7 passive watcher + `pending_live_observation` register:
   CAS-idempotent, closed `injected`/`live_candidate` vocabulary, NO `verified_live` write
   path) + `cli.py` wiring (**discovered defect fixed:** the accepted H1
   `GuardrailBridgeIntegration` was never constructed in `_run_loop`; + the R226 epilogue
   scan, nested-finally cleanup) + 40-test golden pack: two-unit golden run from the exact
   owner command crossing one safe rotation; injected controller restart exact-once;
   refusal/quota/ambiguous-effect/double-start faults; watcher matrix; executable
   16.9(a–m)/R186(1–15)/R118-ladder registers. Suites: supervisor 2,584/0 (2 skipped) +
   non-supervisor 559/1 foreground-chunked; mutation 12/12; CI 20/20 green; ONE consolidated
   correction round (G3 fake-git env, G4 six-discovery-branch coverage, G5 nested finally +
   scalar sanitization) with all four SendMessage delta re-attestations PASS; G0/G2/G3/G4/G5
   PASS + DCV 83/83 (Amendment-7 rows R220–R230 included). Verbatim reports:
   `project-control/reports/M0-T096-{G3-code-review,G4-qa,G5-security,DCV}{,-delta}.md`.
   **Pinned residual (immaterial, G5-attested non-sensitive):** `live_observation.py:296`
   stores raw `source_record_key` — one-line cleanup for the next supervisor unit.
4. **D-024 Amendment 8 captured mid-unit** (owner 2026-08-28; verbatim
   `source-008-amendment.md`; rows **R231–R249**; validator EXIT=0; owner report
   `project-control/reports/D-024-amendment-8-owner-report.md` answers the five R249
   items): a persistent same-terminal **Codex-only discussion channel** (`/loop-codex`) and
   a **one-way Telegram notification sink** are REQUIRED BEFORE continuous-mode activation
   (R232); never claim /btw-equivalence without measured proof (R233 — ordinary commands
   queue until the turn ends; second terminal stays the honest real-time path);
   supervisor/operator-channel changes after a golden-run identity invalidate the affected
   certification, so **M0-T112 must re-run the golden certification at the FINAL frozen
   post-addition identity BEFORE the R187/R595 activation package is presented** (R247).
   M0-T096's scope was NOT broadened (R246). New tasks contracted: **M0-T110** (unit K,
   Codex discussion channel, 13 applicable reqs), **M0-T111** (unit L, Telegram sink,
   10 reqs — one-way; secrets only in an approved local mechanism, R243; live send
   owner-gated, R245), **M0-T112** (unit M, re-certification, 6 reqs).
5. **EXACT next action:** claim M0-T110 (deps: M0-T096 accepted): `/loop-codex`
   new/continue/show/promote/close over the unit-G skill + UserPromptSubmit interception
   architecture (blocked+erased pre-model, zero-context proof or truthful fallback, R235);
   per-turn bounded context (durable thread summary + recent exchanges + fresh
   supervisor/campaign state + evidence refs + read-only deep inspection, R236) reusing
   codex_reviewer/evidence-packet/redaction/token-budget/durable_state-CAS machinery
   (R237); stable refs over line numbers (R238); closed dispositions
   ADVICE_ONLY/QUEUE_NEXT_BOUNDARY/REVISE_CURRENT_TASK/PROPOSE_NEW_TASK/URGENT_PAUSE/
   STOP_FOR_OWNER with no automatic Fable-instruction change and owner-gated promotion
   (R239/R240). Prove-first over the unit-G operator-channel pack; then 4-reviewer gates →
   DCV (13 rows) → accept. Then M0-T111 → M0-T112 → ONLY THEN present the R187/R595
   activation package (`M0-T096-activation-package.md`, refreshed items 10–12). M0-T107
   (unit J) trails non-blocking.
6. **Mechanics (worked this session):** ONE consolidated correction round + SendMessage
   delta re-attestations from the SAME four reviewers; rework→resubmit moves identity;
   verification entry REPLACES the pending placeholder in place (reviewed_sha = gate-wave
   HEAD; manifest from `pc._task_git_identity`); registry JSON written LF; run
   `modularity_check` only AFTER `git add`; `evaluate_task_refs` FIRST at claim
   (selective-citation guard); amendment capture needs ledger tasks + verification
   placeholders + manifest digests (`amendments` = filename list) or the validator fails
   c5/c14/c17.
7. **Environment:** long background python runs are externally killed — foreground chunks;
   never run a mutation pass while a suite is in flight (2 directive-compliance tests
   flaked under a mid-suite registry write and re-passed on the settled tree); CI on the
   pushed SHA is the confirming whole-suite run.
8. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous-mode
   activation owner-gated (R187/R595; supervisor SHADOW-ONLY; injected runners); Amendment-3
   prohibitions; Amendment-7 no-wait/no-provoke + labeling rules (register:
   `pending_live_observation`, zero live candidates; only the 4.8-bridge actuation is gated
   on live observation); Amendment-8 sequencing (item 4); Bootstrap Gate 0 every session;
   supervisor commits cite `D-024-R###`; repo PUBLIC; never `name:` on producers;
   expansion-planning hold; `.claude/hooks` untouchable sans G5.
9. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 23);
   `project-control/tasks/M0-T110.json`;
   `project-control/directives/D-024-fable-codex-loop/source-008-amendment.md` (+ owner
   report `D-024-amendment-8-owner-report.md`); `docs/LEAN_OPERATING_PROCESS.md`.
10. **Stop/change conditions:** Gate-0 failure; validator non-zero; reviewer FAIL/BLOCKED
    (consolidated round → delta re-attestations; M0-T096 is the freshest worked example);
    anything owner-only (credentials, payment, production, legal, PR #241, activation,
    Telegram secrets/live send, live-canary exact-command).
11. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop,
    HEAD, tree, and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md,
    docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the §9 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git +
    the ledger (they win over prose). Continue the campaign seq-23 NEXT: claim M0-T110
    (Amendment-8 unit K, /loop-codex discussion channel; 13 applicable reqs) — prove-first
    over the unit-G operator-channel pack; honest interception limits (R233/R235); closed
    dispositions; owner-gated promotion; then 4-reviewer gates → DCV → accept; then
    M0-T111 → M0-T112 before any R187/R595 activation-package presentation. Foreground
    chunks; never mutate during a live suite. Do not merge PR #241 or any pre-existing PR;
    supervisor stays SHADOW-ONLY; guards inside .claude/hooks are untouchable without G5.
    Stop for anything owner-only. The standard D-010 R113/R114 ~400k rotate-at-seam
    ceiling governs your session."*
