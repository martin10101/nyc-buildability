# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 43: Amendments 16–20 arc COMPLETE; ONE new live attempt AUTHORIZED; NEXT = preflight + present both commands

1. **Generated:** 2026-08-30 ~09:4x UTC · orchestrator session
   `session_01SfXcRw7emzdojCDJmKxNTM`. **Turnover reason (owner, verbatim in
   `source-020-amendment.md`):** authorize exactly one post-Amendment-19 live-loop attempt;
   preflight first (every row, no action unless all pass); present both exact certified
   commands fresh (owner executes separately, in order); eight-point live proof from primary
   evidence; no repin/budget-reset/history-clear/journal-edit/PR #241/policy loosening; on
   preflight mismatch or any post-dispatch stop — no restart/retry/clear, preserve
   everything, full system-level assessment for a new owner decision; no continuous-autonomy
   claim unless the complete journey succeeds. **Sub-agents:** every spawn this session
   (2 producers, 3 reviewers, 1 DCV — reused via SendMessage across waves) completed its
   bounded assignment naturally; none stopped; reports/attestations committed verbatim.
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **43**), tip at write = the Amendment-20
   capture commit (local == origin after push; tree clean; CI 20/20 at every prior tip).
3. **This session end-to-end:** cycle-2 owner start refused (HALTED edge unreachable) →
   Amendment 16/17/18 → **M0-T121** (restart channel: owner-restart /
   acknowledge-emergency-stop / resume-after-answer + edge-granular sweep) + **M0-T122**
   (fourth recert) ACCEPTED → owner-restart **worked live** (HALTED→IDLE exactly-once) →
   cycle-2 start DISPATCHED then S14 counted stop → root cause: rotation-at-seam never fired
   (session resumed at 640,224 tok) + resumed worker cwd = primary checkout; terminal event
   RECOVERED (`max_turns_reached` 13/12 — context-limit hypothesis abandoned) → Amendment 19
   (S16.7 excess dispositioned as measurement-only; resume-path class authorized) →
   **M0-T123** (launch_seam: unconditional 400k ceiling + packet-worktree cwd binding at the
   sole worker Popen + pre-first-dispatch shed; 64-test pack; preserved evidence byte-identical
   throughout) + **M0-T124** (fifth recert + R347 stop/presentation) ACCEPTED → Amendment 20
   captured (this handoff). Suite chain 2,780→2,814→2,889 (0 failures, triple-sourced).
4. **EXACT next action — successor (campaign seq-43 NEXT has the full text):**
   (a) **R350 preflight** at the then-current clean pushed tip, EVERY row reported, the R276
   pattern: tree clean local==origin; CI 20/20 at tip; anchors intact (material `16e1b3b`,
   tree `a72a53b8…`, golden `c54fd0d2…`, launch-seam `1a77b904…`); `executable_identity` ==
   `d6f6c29a…` exact + codex 0.146.0; config/model-selection digests; manifest 121 files
   `47293127…` + verify-controller + doctor overall PASS; drift tooth green; `wt-m0t107`
   clean @ `796e18f`; journal readback PAUSED_RECOVERY / transitions 18 / audit 43 / 0 asks
   / 0 effects. NO recovery or start action unless ALL pass.
   (b) **R351 presentation** on all-pass: BOTH commands fresh (step 1 `clear-recovery
   --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` — the PAUSED_RECOVERY exit, NOT
   owner-restart; step 2 the certified item-3 start, NO repin flag, forward-slash paths,
   config path quoted — verbatim source: `M0-T124-recertification.md` §4). Owner executes
   separately, in order. (c) Verify the **eight-point proof** (R352–R359) from primary
   evidence on the attempt; record honestly.
5. **Failure protocol (R361/R362, BINDING):** preflight mismatch or ANY post-dispatch stop /
   live-journey failure → NO restart, NO retry, NO second clear-recovery, NO automatic
   repair window; preserve everything; full system-level assessment for a NEW owner
   decision; never claim continuous autonomy unless the COMPLETE journey succeeds.
6. **Standing restrictions:** NEVER merge PR #241 (gh-confirmed OPEN); owner-only: autostart,
   C1 canary, Telegram live send, natural-event graduation, OS-ACL; R286/R287 admission
   discipline permanent (CLI 2.1.251 `d6f6c29a…` undrifted — any drift = admission event,
   never silent); R293 never broadly allow shell; Bootstrap Gate 0 every session; supervisor
   commits cite `D-024-R###`; never `name:` producers; never resume a killed producer;
   expansion hold; S16.7 measurement + touch history preserved (R349).
7. **Task states:** M0-T113/T117–T124 accepted; M0-T107 claimed (checkpoint 1 delivered;
   the authorized attempt is its lifecycle); M0-T109 backlog. Follow-up candidates carried:
   launch OSError re-typing, F2 wrapper-evasion, F1, F-LIVE-1, mode-guard, T120 hygiene.
8. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 43);
   `project-control/directives/D-024-fable-codex-loop/source-020-amendment.md` (the
   authorization, R348–R362); `project-control/reports/M0-T124-recertification.md` (§4 =
   the certified command package); `project-control/reports/M0-T107-cycle2-live-journey.md`.
9. **Stop/change conditions:** Gate-0 failure; validator non-zero; any preflight row not
   PASS; any owner-only item; any CLI drift (admission event). The eight-point proof and the
   attempt outcome are recorded on M0-T107 + the campaign — never as chat-only claims.
10. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD,
    tree, and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md,
    docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the §8 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git + the
    ledger (they win over prose). Amendments 16–20 are complete: M0-T121/T122/T123/T124
    accepted, the fifth certification stands, and the owner has authorized EXACTLY ONE new
    live-loop attempt (D-024-R348–R362). Execute the seq-43 NEXT: run the complete R350
    preflight at the then-current clean pushed tip and report every row; if and only if all
    rows pass, present the owner BOTH certified commands fresh (clear-recovery, then the
    certified start — verbatim in M0-T124-recertification.md §4); the owner executes them.
    Then verify the eight-point live proof (R352–R359) from primary evidence. On preflight
    mismatch or any post-dispatch stop: no restart, no retry, no second clear-recovery, no
    automatic repair window — preserve everything and report the full system-level
    assessment for a new owner decision (R361). Never claim continuous autonomy unless the
    complete journey succeeds (R362). Never use --repin-cli-identity, reset budgets, clear
    history, edit the journal, touch PR #241, or loosen any policy (R360). The standard
    D-010 ~400k rotate-at-seam ceiling governs your session."*
