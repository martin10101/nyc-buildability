# M0-T134 producer report — MRL Tranche A (D-024 Amendment 39)

**Producer evidence — not an acceptance record.** M0-T134 is not self-accepted; this report is
submitted for independent gate review (G3/G4/DCV). Author identity = this engineering session
(orchestrator+producer under owner authorization 2026-09-01).

## 1. Identity
- Branch `stabilization/D-024-mrl`, created from control head `ad22e4dc` (control branch + its 5
  commits preserved unmodified as historical evidence).
- Candidate HEAD (final verification): **`5e89175d`**, working tree clean (code); `origin/main` frozen
  `d8b3899f`; `6f5d12a6` = the clean remote candidate base (its own modularity gate was RED — it is the
  starting point, not a "green"/"stabilized" head).
- **Nothing pushed. No PR created/modified. PR #241 and all remote branches untouched. No live
  Claude/Codex/GitHub call. No loop launched.**

## 2. Commits (this branch, oldest→newest)
| SHA | Cluster |
|---|---|
| `f5ed116d` | Governance: capture D-024 Amendment 39 (R489–R514); replan M0-T134; restore `modularity_exceptions.json` to `6f5d12a6`; supersede PHASE-1 reports; mark handoff historical |
| `93cfd1fd` | Cluster 1 — behavior-neutral split `claude_runner.py`→`checkpoint_extraction.py` (R509/R500) |
| `6386e8c1` | Cluster 2 — controller-authoritative data contracts C8/C9/C11 (R501–R505) |
| `bf3ee956` | Cluster 3 — one-shot transport C7 + executable-chain identity C3 (R509/R511) |
| `eb8ce26c` | Cluster 4 — raw gate-evidence recorder `gate_runner.py` C12 (R510/R514) |
| `5e89175d` | Cluster 5 — reconcile independent-review observations (R500/R504/R511) |

## 3. Requirement → production file → test mapping (R507)
| Requirement | Production file | Test file | Positive + mutants |
|---|---|---|---|
| R509/R500 split | `agent_supervisor/checkpoint_extraction.py`, `claude_runner.py` | `test_agent_supervisor_checkpoint_extraction_split.py` (10) | facade identity; missing/conflicting/multiple/invalid checkpoint |
| R501/R503 WorkerResult + ClaudeCheckpoint builder | `agent_supervisor/mrl_worker_result.py` | `test_agent_supervisor_mrl_worker_result.py` (15) | unknown/forged field, wrong type, bad enum, length, non-object; controller-observed facts |
| R502/R503/R504/R505 ReviewVerdict + CodexDecision | `agent_supervisor/mrl_codex_decision.py` | `test_agent_supervisor_mrl_codex_decision.py` (16) | dup/fabricated/non-controller id, cardinality, APPROVE≠COMPLETE (incl. truthy-non-bool), malformed SHA/ref |
| R505 remote freshness | `agent_supervisor/mrl_remote.py` | `test_agent_supervisor_mrl_remote.py` (6) | empty url/ref, no-sha, non-hex sha |
| C7 one-shot transport | `agent_supervisor/mrl_transport.py` | `test_agent_supervisor_mrl_transport.py` (8) | forbidden flags, no fallback, budgets, single-spawn, no re-spawn on continuation |
| R511 exec identity | `agent_supervisor/mrl_exec_identity.py` | `test_agent_supervisor_mrl_exec_identity.py` (11) | same-size+restored-mtime replacement rejected; reorder; updater; runtime model/version |
| R510/R514 gate recorder | `tools/gate_runner.py` | `test_gate_runner.py` (11) | direct + real PowerShell (independently corroborated); shell-string refused; pipe cannot mask; mutation semantics |

Schemas (declarative contracts, `additionalProperties:false` where closed):
`schemas/{worker_result,review_verdict,mrl_claude_checkpoint,mrl_codex_decision}.schema.json`.
No allowed_paths were expanded during implementation; the four §6-removed paths
(`modularity_baseline.json`, `next_task.py`, `cli.py`, `loop.py`) are forbidden and untouched.

## 4. Verification (all at `5e89175d`, clean tree)
- **Tranche-A suite through `gate_runner`** (raw, unpiped): recorded **returncode 0**; machine record in
  `M0-T134-tranche-a-evidence.json` (repo_head `5e89175d`). 77 Tranche-A tests.
- **Full supervisor suite** (behavior-neutrality / freeze baseline): **3144 passed, 2 skipped, 0
  failures**.
- **Unpiped `modularity_check.py --check`**: raw exit **0**, 0 failures. `claude_runner.py` 1432→**1319**
  SLOC (under its retained 1410 ceiling); new modules 148/159/71/155/98/107/167 SLOC (all ≤ HARD 1000, no
  exception). The pass comes from the split, **not** a policy-file edit.
- **Byte comparisons**: `modularity_exceptions.json` sha256 `dba91e16…1792c7` and
  `modularity_baseline.json` sha256 `8830a47d…31ca5` are **byte-identical to `6f5d12a6`**.
- **Mutation tests**: every fail-closed mutant listed above is present and red-without-the-guard; the
  `gate_runner --mutation` CLI reports a killed mutant as exit 0 and a survivor as exit 1.
- ruff: clean across all 15 Tranche-A files.
- Initial modularity was recorded honestly RED (1432 vs restored 1410, single expected failure) before
  the split.

## 5. Independent review
A read-only reviewer (Opus 4.8) adversarially re-derived and re-proved all eight contracts with its own
inputs: **PASS, no confirmed defect, no bypass.** Four non-blocking observations were raised; three were
reconciled in cluster 5 (`5e89175d`): the "discharge" wording corrected to "reduced under retained
ceiling"; strict `is True` on the R504 controller gates; an empty-version test. The fourth is recorded
below as a Tranche-B obligation.

## 6. Remaining limitations / Tranche-B obligations (not defects)
- The `claude_runner.py` 1410 exception is **retained** (byte-identical to `6f5d12a6`); it now sits above
  the file's current 1319 SLOC and can be retired in a later governance step. The split did not delete it
  (the owner required the policy file unchanged).
- `mrl_exec_identity.bind_executable_chain` is a pure primitive that hashes whatever ordered links it is
  given; it does not itself require the three named roles. Tranche-B wiring must supply and re-verify the
  full wrapper→runtime→entrypoint chain and the live runtime model/version probe.
- No live launch was performed: `_default_spawn`, `_default_run` (ls-remote), and the live model/version
  probe are injectable and never invoked in Tranche A. Tranche B wires them under the manifest launcher.
- The MRL contract modules are additive and **not yet wired** into `cli.py`/`loop.py`/`next_task.py`
  (out of Tranche-A scope; no live launch).

## 7. Next owner action
Route M0-T134 to independent G3/G4 + DCV at `5e89175d` for formal acceptance; do not push or create a PR
(the integration branch is not created — Option-B planning only). Tranche B remains unauthorized.
