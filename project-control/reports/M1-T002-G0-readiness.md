# M1-T002 — G0 Definition-of-Ready Review

- **Task:** M1-T002 — PLUTO SODA connector (64uk-42ks) with provenance and contract tests
- **Gate:** G0
- **Reviewer:** orchestrator (definition-of-ready; producer has not started)
- **Date:** 2026-07-16
- **Verdict:** PASS

## Checklist

| G0 criterion | Evidence |
|---|---|
| Objective unambiguous | Packet objective + 8 acceptance scenarios pin retrieval, normalization, provenance, error taxonomy, and contract binding; connector plan pre-approved in accepted research §7 item 1 |
| Dependencies accepted | M1-T001 accepted 2026-07-16 (G0/G1/G3 PASS); M0-T009 accepted 2026-07-16 (contracts v1 on main, CI green) |
| File scope exclusive | `services/api/app/connectors/**` + its tests/fixtures do not exist yet (verified: services/api contains only main.py, test_health.py, packaging). No other active or backlog task touches services/api. M0-T005-R1 scope (.github/scripts, docs/SECRETS_POLICY.md) is disjoint |
| Inputs and outputs defined | Packet `inputs` (6 concrete artifacts, all in-repo) and `outputs` (6 concrete paths) |
| Acceptance scenarios exist | S1–S8 cover normal, boundary, missing/null, ambiguous/conflicting, failure, retry/idempotency, provenance-completeness, regression — matches the connector scenario pack in docs/ACCEPTANCE_SCENARIO_STANDARD.md |
| Source documentation available | Accepted research doc + registry draft + G3 carry-forwards in repo; official dataset live-verified 4× on 2026-07-16 (G3 W7–W10) |
| Credentials | None required: SODA endpoint is tokenless-capable (official Socrata app-token doc, research §5.2/E7). Optional production `SOCRATA_APP_TOKEN` recorded as a human action in docs/HUMAN_ACTIONS_REQUIRED.md — not a blocker for this task |
| Required gates assigned | G0/G1/G2/G3/G4/G5; reviewers: data-contract-verifier (G1), code-reviewer (G3), security-reviewer (G5); G4 = CI on main after merge, recorded by orchestrator |
| Execution location + disk | Producer edits source-only in worktree `.claude/worktrees/M1-T002` (repo is ~KB-scale text; free disk 2.27 GB, below the 4 GB floor — so NO local dependency installation: producer may run pytest only if the environment already has pytest; otherwise tests execute in GitHub Actions CI. Fixtures limited to KB-scale JSON. No citywide dataset download under any circumstance |
| Cleanup / durable routing | Worktree + branch removed after acceptance (per convention); durable artifacts = git-committed source, fixtures, reports. Nothing persistent outside the repo |

## Notes

- F7 (rate-limit fixture) must be synthetic-from-official-doc, clearly labeled — an intentional burst against the shared tokenless IP pool is prohibited (terms + neighborliness).
- F11 (MapPLUTO bulk manifest) explicitly excluded — deferred to the M2 mappluto-bulk importer with OQ-4/OQ-10.
- Live fixture capture (a handful of single-record GETs) is permitted from the producer sandbox if network is available; otherwise the orchestrator captures fixtures per the evidence-capture rule and the producer builds against stored evidence.
