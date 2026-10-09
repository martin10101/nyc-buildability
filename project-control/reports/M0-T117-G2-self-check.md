# M0-T117 — G2 self-check (orchestrator, producer-side verification before independent review)

Recorded 2026-08-29 at the material identity `fa16560` (cherry-pick of worktree commit
`2cd9c5c`; worktree `wt-m0t117` @ base `dca3817`).

| # | Check | Result |
|---|---|---|
| 1 | Scope | PASS — delta spans exactly 8 files, all inside the packet's allowed_paths; nothing else modified (worktree porcelain verified before commit) |
| 2 | Injection correctness | PASS — orchestrator read the seams directly: `claude_child_env()` in process.py applies the forced pair LAST; both claude Popen sites use it (worker ~1103, probe ~1549); import switched; codex paths untouched |
| 3 | Tests (independent re-run) | PASS — orchestrator re-ran the touched modules in the worktree: **38 passed, 1 skipped** (matches producer exactly) |
| 4 | Whole suite (orchestrator-launched) | PASS — **2722 collected = 2712 (M0-T116 baseline) + 10 new; 2717 passed, 2 skipped, 3 failed**; the 3 failures are the pre-existing live drift teeth (capability_probe / event_bus / native_adapter) asserting installed == 2.1.248 while 2.1.251 is installed — AD-093 drift belonging to M0-T118, deliberately untouched |
| 5 | Red/green (AS-4) | PASS — producer captured RED on the unmodified seam (7 failed, `None != '1'`), GREEN after; removal of the single `env.update(FORCED_CLAUDE_CHILD_ENV)` line re-reds the pack (recorded verbatim in M0-T117-autoupdater-evidence.md) |
| 6 | AS-6 fail-closed choice | PASS — forced-pair-wins over a conflicting `extra_env`, with rationale (an unconditional value cannot regress to fail-open; a typed refusal would add an error path and fail launches on config typos); documented in the helper docstring and reports |
| 7 | Owner boundary (R288/R280) | PASS — no environment mutation executed by any agent; command pack recorded verbatim and labeled owner-executed; no DISABLE_UPDATES anywhere; claude not downgraded (still 2.1.251) |
| 8 | Docs | PASS — README + runbook §13 carry the admission-event discipline (upgrade → recapture → recertify → only then repin; never silent drift) |
| 9 | Modularity | PASS — one small helper in process.py (owning module for env construction); claude_runner.py grew by 2 call-site swaps + 2 comments only |
| 10 | Known open item | The workstation half of R278 completes on the owner's typed confirmation ("autoupdater env set"); acceptance is held until then — fail closed, recorded in the evidence map |

**VERDICT: G2 PASS — ready for the independent G3/G4/G5 wave at this identity.**
