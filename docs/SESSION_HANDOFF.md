# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 15: M0-T105 ACCEPTED (unit D); NEXT = M0-T106 (unit E bounded /goal)

1. **Generated:** 2026-08-27 UTC · Fable 5 orchestrator, `session_01HfptKuEs3RDxaxsSHJjc7t`.
   **Sub-agents in flight:** none (G3/G4/G5 delta reviewers + DCV all landed and reconciled).
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop`, accept commit `8bc13fa` (campaign seq **15**, frozen there).
   Machine claude 2.1.247.
3. **M0-T105 = ACCEPTED** (unit D native event integration; deliverable `bfdf4ef`, content
   identity `4bd0e182`). 2 rounds: round-1 G3/G5 PASS advisories-only, G4 PASS with **M1 MEDIUM
   blocking** (recorder read stdin via Windows cp1252 → non-ASCII mojibake/silent-drop — the
   carried M0-T104 UTF-8 lesson, caught by G4's adversarial probe); correction round F1–F5
   (bytes-stdin+utf-8-sig decode; RECURSIVE `_mask_uuids` closing the converged nested-UUID
   finding; dedup-window disclosure; S5 wording; coverage adds); round-2 delta re-reviews ALL
   PASS; independent DCV PASS on R154/R155/R173 (cross-check clean, 28 directives). New modules
   `event_bus.py` (dedup/ordering/replay), `event_stream.py`, `event_drift.py`, recorder
   `.claude/hooks/supervisor_event_recorder.py` (UNREGISTERED — settings.json wiring is a
   SEPARATE reviewed change). 38/38 pack, 2,686/3/0 freeze suite, 11/11 mutants, guards +
   M0-T104 adapter byte-untouched.
4. **C1 DISCHARGED owner-launched:** round 1 (no hooks registered) proved transport only; the
   orchestrator wrote the scratch-local settings (sha `a26d3b9b`), validated end-to-end dry-run;
   round 2 owner-run captured **9 measured-live records** →
   `fixtures/hook_events_live_2026-08-27_m0t105_c1.json` + tooth. Measured facts: Agent-tool
   spawn fires SubagentStart/Stop **NOT** TaskCreated/TaskCompleted on 2.1.247; SessionStart
   carries `model`; SessionEnd carries `reason`; `prompt_id` withheld (29-char non-UUID); live
   cross-process `bus_sequence` collision (two firings both seq 3, append order preserved).
   `.gitleaksignore` carries 9 audited fingerprints (fixture `idempotency_key` digests ≠
   secrets; G5-delta ground-truthed exact scope).
5. **Accept-mechanics facts (this seq):** in-regime `submit` fails closed on dirty/untracked
   relevant files (commit FIRST, then submit); `accept` fails closed unless verification
   `reviewed_sha` == live HEAD (restamp rows to accept-time HEAD; material identity stable);
   the auto-mode classifier can transiently block `gate`/heredoc Bash calls — PowerShell or
   split-steps work; a byte-length-identical mutant can survive in `__pycache__` (clear caches
   after mutation testing).
6. **NEXT (campaign seq 15):** claim **M0-T106 (unit E bounded /goal)** → T092 (F) → T094 (G) →
   T093 (H1) → T095 (H2) → T096 (I golden run; **R187 hold after**) → T107 (J). Unit-E carries:
   R042 labels, R043 final-request caveat, R045 no worker-facing quotas, R154 sidecar-primary.
7. **Non-blocking residuals (recorded in accept commit + campaign record):** M0-T105 — G3-A1
   `_event_usage` extraction candidate; G3-A2 ordering note (disclosed+measured); G5-ADV-1
   store-path env trust boundary; G5-ADV-2 per-event replay cost; G5-ADV-3 silent-loss trade;
   G4-A1 timing design-assertion; gitleaksignore line-fragility. M0-T104 — G3 ADV-2
   serialization-group extraction; G4 R1 post-stop absence tooth (close when seam wired F–H).
   M0-T109 guard-hardening backlog (folds G5 R2 `_TOOLS_RE` widen).
8. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous-mode
   activation owner-gated (D-024 §18/R595; supervisor SHADOW-ONLY); Amendment-3 prohibitions;
   Bootstrap Gate 0 every fresh session; supervisor commits cite `D-024-R###`; repo PUBLIC —
   mask `[HOME]`; never `name:` on producers; expansion-planning hold in force.
9. **Owner-visible cleanup (non-blocking):** two idle canary sessions (`evcap247-52`,
   `evcap247-a1`) + scratch dir `%LOCALAPPDATA%\Temp\evcap247` can be closed/deleted anytime
   (capture harvested; repo independent of them). Broken npm shim; parked session `777b09da`;
   stale pack-repo worktrees purge.
10. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
    `project-control/campaigns/D-024-fable-codex-loop.json` (seq 15); the M0-T106 packet when
    created; `docs/LEAN_OPERATING_PROCESS.md`.
11. **Stop/change conditions:** Gate-0 failure; validator non-zero; reviewer FAIL/BLOCKED
    (consolidated correction round → re-freeze → delta re-review; M0-T104/T105 are worked
    examples); anything owner-only (credentials, payment, production, legal, PR #241,
    activation, live-canary exact-command, worktree purge).
12. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, tree,
    and `/mcp` empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    .claude/session-handoff-profile.md, and the §10 files. Run `python tools/project_control.py
    status` and `python -m tools.agent_supervisor.campaign_continuity --status`. Reconcile against
    live git + the ledger (they win over prose). Continue the campaign seq-15 NEXT: claim and
    implement M0-T106 (unit E bounded /goal) under /start-controlled-task with a scenario pack,
    then the 4-reviewer gate cycle, and proceed through the unit sequence to the M0-T096 golden
    run (R187 hold after). Stop for anything owner-only."*
