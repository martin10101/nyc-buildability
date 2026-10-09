# D-024 Amendment 48 — Journey-launcher path-wiring correction + terminal-visibility confirmation (owner directive, 2026-09-03)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-047-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-03, one message after the first journey
  attempt was refused pre-provider)
- **Context:** the owner typed `run_first_supervised_journey.ps1`; the launch was refused
  BEFORE provider contact with `cwd_mismatch: launch bound to
  C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, but M0-T107 declares
  C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t107` — the R335/R336 cwd guard
  (`tools/agent_supervisor/launch_seam.py`, CWD_MISMATCH) working as designed against a
  launcher-script wiring defect (the script bound the control-plane worktree instead of the
  packet's isolated worker worktree). No provider was contacted; no run dir or audit refusal
  row was produced; a stale ctl24-bound `journey_launch_manifest.json` remains at
  `C:\SupervisorController\mrl\` (overwritten by the corrected draft). The journal already
  rests at PREFLIGHT (the J4 `resume-after-answer` exit succeeded — audit seq 69–70).
- **Base identity at capture:** worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
  `candidate/D-024-mrl-option-b`, HEAD `e157eff0a0c020e1876486d77021ad5343d70631`, tree clean.
  Frozen accepted candidate `3f4cee86` installed. M0-T140 + M0-T143 accepted; M0-T107 claimed.

## Verbatim owner directive

> Apply one narrow launcher correction only.
>
> The first real journey was refused before provider contact with:
>
> cwd_mismatch: launch bound to C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, but M0-T107
> declares C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t107.
>
> Treat this as a launch-script path-wiring defect, not a commissioning failure. Do not reopen
> accepted tasks, create another stabilization tranche, modify production controller code,
> weaken the cwd guard, rerun canaries, or contact either provider.
>
> First verify read-only that wt-m0t107 exists, is clean, and matches M0-T107’s declared
> branch and task authority. If it matches, regenerate the existing
> run_first_supervised_journey.ps1 so every worker-repository binding—repo root, cwd,
> worktree, branch, live HEAD, and clean status—comes from wt-m0t107. Keep
> C:\SupervisorController as the installed controller and ctl24 as the control-plane
> repository where appropriate; do not confuse either with the worker worktree.
>
> Run only:
>
> 1. PowerShell parser validation.
> 2. Read-only worktree identity/status validation.
> 3. A local inspection proving the generated manifest/start arguments bind the worker to
>    wt-m0t107.
> 4. No provider call.
>
> Atomically replace the same activation script and return its SHA-256 plus exactly one
> owner-run PowerShell command. If the worktree itself does not match the task packet, stop
> and report every observed-versus-expected mismatch together.
>
> End with JOURNEY_LAUNCHER_PATH_CORRECTED.Do not build another subsystem or reopen
> stabilization. Before launching the first real supervised task, confirm exactly what live
> information the owner will see in the foreground PowerShell terminal. The run must remain
> attached to the terminal and display concise, real-time events for each Fable execution,
> Codex review, controller decision, cycle transition, refusal, and final state. Do not expose
> hidden reasoning or secrets. If this visibility already exists, identify the exact
> one-command launch and show a representative output sample from existing code. If it does
> not exist, report that honestly; do not implement anything without owner approval.
