# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 25: M0-T110 AND M0-T111 ACCEPTED; NEXT = M0-T112 (final golden re-certification)

1. **Generated:** 2026-08-28 ~23:30Z · orchestrator session `session_01HfptKuEs3RDxaxsSHJjc7t`
   (this single session claimed and accepted BOTH Amendment-8 capability units). **Seam
   reason:** task acceptance (LEAN trigger e). **Sub-agents in flight:** none (eight reviewer
   assignments — 4 per unit — all completed reviews AND delta re-attestations; reports
   committed verbatim).
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **25**), accept-time head `42e4e58`.
3. **M0-T110 (unit K, /loop-codex) = ACCEPTED** (deliverable `ba25516`+`c8b38ba`, DCV 13/13 at
   `79098ae`, manifest `0c97eb77`) — see seq-24 handoff in git history for detail.
   **M0-T111 (unit L, Telegram sink) = ACCEPTED** (deliverable `c9b3b9a`, corrections
   `8574c58`, gate wave `f263ab4`, DCV 10/10 at `42e4e58`, manifest `925e1901`): one-way
   sink over the frozen S13.10 boundary — closed 8-condition vocabulary; env-only secrets
   (`SUPERVISOR_TELEGRAM_BOT_TOKEN`/`CHAT_ID`), repr-redacted, status-bucket-only errors;
   owner-gated live send (`--live-canary-authorized-by-owner`, NEVER fired, no socket in any
   test); bounded retries + FIFO dedup + `already_queued` outage suppression + 3500-char
   outbound cap + identifier redaction; read-only discovery of the two durable sources.
   L-pack 35/35; mutation 18/18; suites supervisor 2690/0 (2 skipped) + non-supervisor 559/1;
   CI 20/20 twice; one consolidated correction round; all four delta re-attestations PASS.
   Reports: `project-control/reports/M0-T111-*`.
   **Pinned residuals (non-blocking):** `_already_queued` digest normalization (stored
   post-builder summary vs raw — best-effort growth bound for redaction-altered summaries;
   all three delta reviewers converged; fix at the seam); unit-I `live_observation.py:296`
   one-liner; unit-K boundary queue write-only/inert; unit-K report line-count nit.
4. **EXACT next action:** claim M0-T112 (deps M0-T110+M0-T111 accepted) — Amendment-8 unit M,
   **final golden re-certification at the FINAL frozen post-addition identity (R247)**.
   Both additions touched `tools/agent_supervisor/**` + the operator channel, invalidating
   the M0-T096-era certification. Re-run AT THE FINAL FROZEN IDENTITY: the FULL golden-run
   pack (`test_agent_supervisor_golden_run.py`), the affected packs (operator-channel,
   K-pack, L-pack, adversarial/endurance/phase1, reviewer), the WHOLE supervisor suite
   (freeze baseline), and CI on the pushed SHA; then REFRESH-ONLY the activation package's
   identity/evidence items (`M0-T096-activation-package.md` items 10–12). **ONLY AFTER
   M0-T112 is accepted may the R187/R595 activation package be PRESENTED** — presentation is
   a separate owner-facing step; activation itself stays owner-gated. M0-T107 (unit J)
   trails non-blocking. Run `evaluate_task_refs` at claim (expected rows:
   R231/R232/R246/R247/R248/R249 — confirm against the resolver).
5. **Mechanics (proven twice this session):** ONE consolidated correction round + SendMessage
   delta re-attestations from the SAME four reviewers; commit reports BEFORE gates; gate
   `--sha` == live HEAD; verification entry stamped at the **accept-time HEAD**
   (fill → validate → ACCEPT → commit together — committing the entry first forces a restamp
   cycle); registry JSON LF; `modularity_check` after `git add`; fake tokens need BOTH
   `gitleaks:allow` and `secretscan:allow`; a follow-up push auto-cancels the prior CI run
   (judge the tip); reviewer packs importing the unit-G harness keep one harness authority.
6. **Environment:** long python runs are externally killed — foreground chunks; the
   directive-compliance validator pack needed a 4-way class-group split when the workstation
   slowed (73+16+18+13 = 120); never mutate during a live suite.
7. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous-mode
   activation owner-gated (R187/R595; supervisor SHADOW-ONLY); Amendment-3 prohibitions;
   Amendment-7 no-wait/no-provoke + labeling; Amendment-8 sequencing (M0-T112 before the
   activation package is presentable, R232/R247); Telegram one-way/secrets/live-canary
   (R242/R243/R245 — the live canary command exists but remains owner-typed only);
   Bootstrap Gate 0 every session; supervisor commits cite `D-024-R###`; repo PUBLIC;
   never `name:` on producers; expansion-planning hold; `.claude/hooks` untouchable sans G5.
8. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 25);
   `project-control/tasks/M0-T112.json`;
   `project-control/directives/D-024-fable-codex-loop/source-008-amendment.md` (+ owner
   report `D-024-amendment-8-owner-report.md`);
   `project-control/reports/M0-T096-activation-package.md` (the document M0-T112 refreshes);
   `docs/LEAN_OPERATING_PROCESS.md`.
9. **Stop/change conditions:** Gate-0 failure; validator non-zero; reviewer FAIL/BLOCKED
   (consolidated round → delta re-attestations; M0-T110/T111 are the freshest worked
   examples); anything owner-only (credentials, payment, production, legal, PR #241,
   activation, Telegram secrets/live send, live-canary exact-command, and the activation-
   package PRESENTATION decision itself).
10. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD,
    tree, and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md,
    docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the §8 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git + the
    ledger (they win over prose). Continue the campaign seq-25 NEXT: claim M0-T112
    (Amendment-8 unit M — the final golden re-certification at the FINAL frozen
    post-addition identity, R247): full golden-run pack + affected packs + whole supervisor
    suite + CI at that identity; refresh-only the activation package's identity/evidence
    items; then 4-reviewer gates → DCV → accept. Only after that acceptance may the
    R187/R595 activation package be PRESENTED to the owner — presentation and activation
    stay owner-gated. Foreground chunks; never mutate during a live suite. Do not merge
    PR #241 or any pre-existing PR; supervisor stays SHADOW-ONLY; guards inside
    .claude/hooks are untouchable without G5. Stop for anything owner-only. The standard
    D-010 R113/R114 ~400k rotate-at-seam ceiling governs your session."*
