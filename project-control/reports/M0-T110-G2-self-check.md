# M0-T110 — G2 producer self-check (unit K, `/loop-codex`)

Producer: fable-orchestrator-session. Deliverable identity: `ba25516` (implementation
`e632da2` + one CI-red correction: a `secretscan:allow` pragma with justification on the
deliberately fake `ghp_` token in the K6 leak-absence test — the only red check).
Supervisor-freeze qualifying evidence: D-024-R232/R234.

## Commands run (all foreground, settled tree)

| Check | Command | Result |
|---|---|---|
| K-pack | `python -m pytest tools/test_agent_supervisor_codex_channel.py -q` | **52 passed** |
| Affected packs | `pytest tools/test_agent_supervisor_{operator_channel,golden_run,reviewer}.py -q` | **175 passed** |
| Supervisor suite (freeze baseline) | 3 alphabetical chunks over all 58 `test_agent_supervisor_*.py` | **2,654 passed, 2 skipped, 0 failed** |
| Non-supervisor tools suite | 3 chunks over the other 26 `tools/test_*.py` | **559 passed, 1 skipped** (== accepted baseline) |
| Mutation pass | 14 hand-rolled mutants, one at a time, killing test each (scratchpad driver; table in the unit report §6) | **14/14 KILLED** (1 first-round survivor → new CAS-conflict test → killed) |
| Lint | `ruff check <changed files>` (ruff 0.13.0, the CI version) | clean |
| Modularity | `python tools/modularity_check.py --check` after `git add` | exit 0 |
| Secret scan | `python .github/scripts/secret_scan.py` | PASS |
| CI on pushed SHA | 20 contexts at `ba25516` | **20/20 success** |
| CLI smoke | `python -m tools.agent_supervisor codex show cxt_zzz --json` | typed `unknown_thread` refusal |

## Self-check assertions

1. **Scope:** every changed path is inside `allowed_paths`; the untouchable guard hooks and
   every forbidden path are untouched (`git show --stat e632da2 ba25516`).
2. **No actuation surface:** `codex_channel.py` imports no stop-intent/repair-gate/ledger/
   GitHub write surface (K4 import-scan test enforces this permanently).
3. **Reuse, not re-implementation:** interception, sanitization, identity validation,
   read-only argv, process containment, model resolution, redaction, CAS persistence, and
   the answer-file rule are all the accepted unit-F/G/I surfaces (one public rename:
   `operator_ask.read_answer_file`, call-site updated, no behavior change).
4. **Honesty:** no `/btw` equivalence claim; the pending-owner-C1 zero-context canary is
   stated as pending in the unit report §1; the skill documents the in-session fallback's
   context cost.
5. **Known bounds (documented, deliberate):** the interception path inherits the hook's 45 s
   subprocess timeout (as `/loop-ask` does — a longer turn lands on the second terminal);
   threads cap at 40 stored messages with a typed "new thread" refusal; the boundary queue
   caps at 32 with a visible `queue_full` result.
6. **Incomplete work:** none inside this packet. The unit-I pinned residual
   (`live_observation.py:296` raw `source_record_key`) was NOT addressed here — it is a
   separate one-line follow-up owned by the next supervisor unit per the acceptance record.

Verdict: **PASS** (producer self-check; independent G3/G4/G5 + DCV follow).
