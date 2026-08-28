# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 22: M0-T095 (unit H2) ACCEPTED; D-024 Amendment 7 captured; NEXT = M0-T096 (unit I)

1. **Generated:** 2026-08-28T08:05Z (header finalized ~08:15Z) · orchestrator session
   `session_01HfptKuEs3RDxaxsSHJjc7t` (the seq-21 successor). **Turnover reason
   (verbatim):** owner invoked `/session-handoff` with no stated reason — landed at the
   clean seq-22 acceptance seam already reached under the standard D-010 R113/R114
   rotate-at-seam ceiling (same pattern as seq 19→20→21). **Sub-agents in flight:** none
   (all four reviewers — G3 code-reviewer, G4 qa-engineer, G5 security-reviewer, DCV —
   completed their bounded assignments naturally, returned delta attestations, and their
   reports are committed verbatim; no producer or background task is running; CI on the
   tip `dc2bc04` is 20/20 green).
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **22**, frozen f26771b).
3. **M0-T095 (unit H2) = ACCEPTED** (deliverable identity `a3030ba`; gates at reports commit
   `7ec184c`, manifest `b1933009`; accept commit `f26771b`): `repair_gate.py` (R076
   8-predicate RepairRecord gate; R078 closed 6-question checkpoint, never-auto-accept
   disposition; patch-stacking rejection; R077 CompatibilityException, injected-fact
   expiry-blocks-acceptance; R091 review-identity validity + consolidated-round
   drip-feeding refusal; E10/E11 effect-free closed-vocabulary PR classification incl.
   the #241 owner-hold fixture; R017/E13 freeze-citation validator; record-only
   `checkpoint_section` → `build_packet(extra_sections)`) + the 78-test matrix with the
   **executable prove-first registers** (16.6 T1–T9; 16.8 E1–E14 — existing
   github_flow/policy/contract proofs CITED and source-verified, only genuine gaps
   built). Suite 2563/0 chunked; mutation 12/12; CI 20/20 green at `a3030ba`; ONE
   consolidated correction round (report modularity wording → true 625-SLOC/warn result,
   Gate-0/MCP attestation §4.4, docstring redaction caveat) with all four delta
   re-attestations PASS; G0/G2/G3/G4/G5 + DCV 46/46 PASS. Verbatim reports:
   `project-control/reports/M0-T095-{G3-code-review,G4-qa,G5-security,DCV}.md`.
4. **D-024 Amendment 7 captured this session** (owner mid-turn instruction, verbatim in
   `source-007-amendment.md`; rows **R220–R230**; validator EXIT=0; owner report
   `project-control/reports/D-024-amendment-7-owner-report.md`): two-lane golden-run
   evidence split — lane 1 (injected/deterministic proof) proceeds NOW inside M0-T096's
   existing scope (R186/R182/R106); lane 2 (natural Fable 5 refusal/quota/model-turnover
   observation) DEFERRED as `pending_live_observation` with a bounded passive watcher
   over the existing sanitized telemetry (R225/R226) and a compare-then-graduate
   protocol per feature (R227/R228). **Never wait for or provoke a natural event
   (R220/R221); never label injected evidence as live (R223).** Only ONE feature is
   gated on live observation: the automatic 4.8 bridge's actuation (already double-gated
   measured-live AND R595 — accepted H1 machinery, fail-safe). Rows bind to
   M0-T096/M0-T107 only; M0-T096's applicable set is now **83**.
5. **EXACT next action:** claim M0-T096 (unit I; deps M0-T093/T094/T095 all accepted):
   fault-injected deterministic suites; two-unit golden run from the exact owner start
   command; forced safe-seam rotation + injected controller restart without duplicate
   work; ambiguous-effect recovery; host-restart canary or truthful limitation report;
   soak via accelerated counters; activation package (continuous mode default-off,
   section-20 items 1–14); PLUS the Amendment-7 watcher deliverable +
   pending_live_observation register. Prove-first over the existing crash/recovery/
   rotation/turnover packs; then 4-reviewer gates → DCV (83 rows;
   `M0-T095-evidence-map.json` + the M0-T095 verification entry are worked templates)
   → accept. **R187 HOLD after the golden run.** Then M0-T107 (J).
6. **Mechanics re-proven this session:** report/code edits after submit move the content
   identity → rework→resubmit cycle (progress --status rework, submit, accept — this
   seam is the worked example); ONE consolidated correction round + SendMessage delta
   re-attestations from the SAME four reviewers; verification entry REPLACES the staged
   pending placeholder (do not append a duplicate); registry JSON must be written
   LF (`newline='\n'`) or the manifest content digests break on LF checkouts; run
   `modularity_check` only AFTER `git add` (untracked files are excluded from selection).
7. **Environment:** long background python runs are externally killed — foreground
   chunks; never run a mutation pass while a suite is in flight; CI on the pushed SHA is
   the confirming whole-suite run (supervisor-bridge job).
8. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous-mode
   activation owner-gated (R187/R595; supervisor SHADOW-ONLY; injected runners);
   Amendment-3 prohibitions; Amendment-7 no-wait/no-provoke rules; Bootstrap Gate 0
   every fresh session; supervisor commits cite `D-024-R###`; repo PUBLIC; never
   `name:` on producers; expansion-planning hold; `.claude/hooks` untouchable sans G5.
9. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 22);
   `project-control/tasks/M0-T096.json`;
   `project-control/directives/D-024-fable-codex-loop/source-007-amendment.md` (+ owner
   report `D-024-amendment-7-owner-report.md`); `docs/LEAN_OPERATING_PROCESS.md`.
10. **Stop/change conditions:** Gate-0 failure; validator non-zero; reviewer FAIL/BLOCKED
    (consolidated round → delta re-attestations; M0-T095 is the freshest worked
    example); anything owner-only (credentials, payment, production, legal, PR #241,
    activation, live-canary exact-command).
11. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop,
    HEAD, tree, and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md,
    docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the §9 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git +
    the ledger (they win over prose). Continue the campaign seq-22 NEXT: claim M0-T096
    (unit I golden run + activation package + Amendment-7 watcher/pending_live_observation
    register; 83 applicable reqs) — prove-first over the existing crash/recovery/rotation
    packs per R018, lane-1 injected proofs only (never wait for or provoke a natural
    Fable event, never label injected as live), then 4-reviewer gates → DCV → accept;
    R187 HOLD after the golden run; then M0-T107. Long background python runs are
    externally killed — foreground chunks; never mutate during a live suite. Do not
    merge PR #241 or any pre-existing PR; supervisor stays SHADOW-ONLY; guards inside
    .claude/hooks are untouchable without G5. Stop for anything owner-only. The standard
    D-010 R113/R114 ~400k rotate-at-seam ceiling governs your session."*
