# M0-T121 — G2 self-check (orchestrator verification of producer evidence)

Recorded 2026-08-30 at control head `668c824` (the cherry-picked work commit `49efc90`
from the producer worktree; base `04216dd`). VERDICT: **PASS** — every producer headline
claim was independently re-executed by the orchestrator, not taken from the report.

| # | Check | Producer claim | Orchestrator re-verification |
|---|---|---|---|
| 1 | Worktree identity | reset to `04216dd` | `git rev-parse HEAD` in the worktree = `04216dd` ✓; changed files exactly the allowed set (+2 agent-memory files) ✓ |
| 2 | cli.py bounded wiring | +2 SLOC net | `git diff --stat` = `cli.py | 2 ++` ✓ (one import, one `register_restart_verbs` call) |
| 3 | Imports / symbol existence | — | `import tools.agent_supervisor.cli` OK; `restart_channel.register_restart_verbs` present ✓ (a transient IDE-diagnostic snapshot mid-write had suggested otherwise; disproven by execution) |
| 4 | New suite | 31 passed | re-run in worktree: **31 passed** ✓; re-run on the CONTROL checkout at `668c824`: **31 passed** ✓ |
| 5 | Required minimum + golden | 410 passed | re-run in worktree (restart_channel+invariants+recovery+crash+loop+endurance+golden_run): **410 passed, 0 failures** ✓ |
| 6 | Modularity | exit 0, failures 0 | re-run: no failures; only the two pre-existing warn signals (repair_gate.py, context_benchmark.py — untouched by this task) ✓ |
| 7 | Scope | all changes in allowed_paths | verified file list against the packet ✓; forbidden paths untouched; live runtime dir untouched (all tests on constructed temp journals) ✓ |
| 8 | Model identity (R323 interim) | — | mid-run transcript grep: 105/105 events `claude-opus-4-8`; authority D-004-R735 via byte-stable frontmatter (`8b1b386`); report `M0-T121-producer-model-identity.md`; final re-read owed at accept |
| 9 | R319 discipline | no operability claim | producer report explicitly disclaims continuous-operability; the live-journey standard (R320) remains owed after M0-T122 ✓ |

Noted for the gate wave (not self-check failures):
- The producer closed a THIRD latent F-2 edge (`owner_answer_validated`, `WAIT_FOR_OWNER -> PREFLIGHT` via `resume-after-answer`) discovered by the mechanical sweep — authorized by R303's "complete reproduced F-2 defect class"; G3 should verify the scope-extension reasoning (producer report §3/§9).
- R308 reads "exactly one surface per intended operator-recovery EDGE": the `owner_explicit_restart` TRIGGER backs two distinct edges (HALTED→IDLE, EMERGENCY_STOPPED→IDLE), one surface each. Reviewers should confirm the per-edge reading and the meta-test pinning the derived set.
- R311 identity-drift precondition: the command checks the recorded pinned identity; the live drift probe remains `start`-preflight territory (documented deferral, producer risks §). G3/G5 verify nothing was silently skipped.
- Red proof was produced via an in-tree registration edit (producer is git-write-barred), captured verbatim in the producer report.
