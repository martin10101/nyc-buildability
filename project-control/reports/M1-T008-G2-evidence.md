# G2 Self-Check Record — M1-T008 (DOB-wide legacy source research)

- **Gate:** G2 producer self-check (recorded by the orchestrator with reviewer label `orchestrator`, stored role `self_check` per the hardened CLI; can never satisfy an independent gate)
- **Producer:** official-source-researcher
- **Recorded:** 2026-07-17 (late recording — see note)

## Late-recording note

The producer's self-check evidence was submitted through the agent-return channel and embedded in `project-control/reports/M1-T008-producer-report.md` (§3 scenario table, §4 commands, §5 surprises disclosed) before the hardened CLI required a discrete G2 gate record. This record registers that evidence; it adds no new claims.

## Producer self-check evidence (original submission, commit 4535b18)

- All task scenarios S1–S7 executed by the producer with live tokenless queries against `data.cityofnewyork.us`; commands and expected-vs-actual recorded in the producer report §3–§4.
- Fixture capture: per-dataset samples, positive/no-match BIN probes, min/max hazard probes, drift-signature probe (HTTP 400), catalog sweeps, metadata extracts, query logs — committed under `services/api/tests/fixtures/dob_legacy/`.
- G2 permits submission only; independent verification was performed at G1 (data-contract-verifier, PASS with blocking corrections D1/D2) and G3 (code-reviewer, FAIL → rework → delta PASS).

## Rework self-check evidence (rework commit 0a45aa5, documentation-only)

Producer self-verification before resubmission (recorded in the rework return packet and reflected in the updated producer report):

- Recounted the fixture directory: 44 files = 43 fixtures (146,865 bytes fixtures-only) + README; measurements independent of the correction prompt.
- Residual-claim greps over the three edited files: no sole-window "16:15–16:21" capture claim, no "26 files"/"77 KB" outside explicit correction notes, no unscoped "all 200"/"VERBATIM", epoch 1784304931 present only in the removal record.
- `git status --porcelain` (read-only): exactly the three allowed files modified; `git diff --stat HEAD -- services/api/tests/fixtures/dob_legacy/` → README.md only (all 43 fixture files byte-identical).
- No git/gh/control-CLI writes by the producer; no network requests during the rework.

Result: PASS (self-check permits submission; independence provided by G1/G3).
