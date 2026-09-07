# G2 Self-Check — M0-T152 (D-033 T-A: supervisor gate-wave engine)

**Recorder:** orchestrator (G2 self-check gate; producer = supervised-loop-fable-worker under
the supervised loop, runs persistent-local-08/09; S6 amendment commit authored by the
orchestrator per D-033-R007's named producer).
**Content identity:** frozen candidate `cc25bdc15e4e982259a71f6903f370e6d1d8adf9`
(task/M0-T152-gate-wave-engine), merged to `candidate/D-024-mrl-option-b` at `9f0c0110` with
all seven content blobs verified byte-identical across the merge (git ls-tree compare, this
session).

## Executable evidence (all captured verbatim, all exit 0)

1. **Four documented commands** at frozen cc25bdc1 —
   `reports/M0-T152-documented-commands-cc25bdc1.txt`:
   - `python -m pytest tools/test_agent_supervisor_gate_wave.py -q` → **63 passed**, exit 0
   - `python -m pytest tools/test_agent_supervisor_loop.py -q` → **127 passed**, exit 0
   - `python -m ruff check` (five packet files) → **All checks passed!**, exit 0
   - `python tools/modularity_check.py --check` → **failures 0** (13 warnings), exit 0 —
     including the verbatim unfiltered recapture appended per G3 observation D-1
     (`selected 358 files; failures 0; warnings 13`).
2. **Supervisor-suite re-baseline** (freeze-rule section 4 duty) at frozen cc25bdc1 —
   `reports/M0-T152-supervisor-suite-cc25bdc1.txt`:
   `python -m pytest tools -q -k "agent_supervisor"` → **3726 passed, 2 skipped, 571
   deselected in 317.04s**, `PYTEST EXIT: 0`. +31 tests vs the M0-T149 baseline (3695) = the
   new gate-wave/loop tests; **0 failures**, far above the ≥1165 floor.
3. **Producer unit evidence:** producer report (`M0-T152-producer-report.md`, at HEAD) with
   the section-2.1 coverage map; 9 valid worker checkpoints across runs 08/09 in the
   supervisor journal (seq 204-263), every cycle live-reviewed by gpt-6-astra.

## Scope check

Diff 0e067b6a..cc25bdc1 touches only the packet's allowed_paths (plus the orchestrator's own
control-plane packet-note sync 382abf6d, confirmed benign by G3 §2). Working trees clean at
both the worktree and ctl24 after merge.

G2 self-check outcome: **PASS** (self-check only; never satisfies an independent gate —
G3/G5 recorded separately from independent reviewers).
