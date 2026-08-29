# M0-T120 — G0 readiness (orchestrator, administrative)

Recorded 2026-08-29 at the Amendment-14 capture (`47f9037`), campaign seq 32.

| # | Check | Result |
|---|---|---|
| 1 | Packet completeness | PASS — objective (R290/R291/R292/R293/R294/R295/R296 scope + supervisor-freeze citation D-024-R291), outputs, AS-1..AS-5, allowed_paths (11 entries; tracked at HEAD: recovery_probes.py, claude_runner.py, prompts/claude_checkpoint.md, test_agent_supervisor_recovery_probes.py, test_agent_supervisor_command_authority.py — the new module/fixture/prompt/report files are the named deliverables), gates G0/G2/G3/G4/G5, four-reviewer roster, directive_refs `D-024:ALL` |
| 2 | Dependencies | PASS — depends on M0-T118 (ACCEPTED at `5251c73`); M0-T117's autoupdater controls active (machine belt live-verified; four constructed-env seams forced) — the live probes run drift-proofed at the admitted 2.1.251 |
| 3 | Directive resolver | PASS — `evaluate_task_refs` ok=true; applicable set exactly {R289, R290, R291, R292, R293, R294, R295, R296}; capture-time verification skeleton matches (8 pending rows); validator EXIT=0 at capture |
| 4 | Qualifying evidence (supervisor-freeze §2/§3) | PASS — cited D-024-R291; AD-093 grounds: reproduced live defect class (three ASK-held shell discovery proposals in run_M0_T107_unitJ = inability to complete an authorized product task without owner touches) + provider CLI drift lineage |
| 5 | Live-probe authorization + bounds | PASS — R292 explicitly orders the empirical proof; packet bounds it: non-forwarding (deny-everything handler), every request recorded+denied, zero file writes, ≤3 provider calls; runs under the exact controller launch construction (build_argv + claude_child_env) |
| 6 | Isolation | PASS — producer worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t120` created at `47f9037` on branch `task/M0-T120-shell-routing-compat`; no overlapping lease (T119 held, claimed by the orchestrator itself on the control checkout with disjoint path-free scope; T117/T118 accepted); allowed_paths disjoint from every active claim |
| 7 | Prohibitions loaded | PASS — R293 stamped (broker/classifier byte-untouched except test additions; no broad shell allowances; no owner-gate change); R280 still stands (no DISABLE_UPDATES/downgrade); R273 (no journal edits) unchanged |
| 8 | Sequencing | PASS — R296/R297 recorded: this unit completes and is accepted BEFORE the single M0-T119 recertification re-runs at the one final identity |

**VERDICT: G0 PASS — ready to claim.**
