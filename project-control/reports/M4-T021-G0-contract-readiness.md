# M4-T021 G0 — contract readiness (orchestrator)

- Task: M4-T021 — B4 wide-street 100-ft buffer/intersection engine (EPSG:2263)
- Gate: G0 (contract readiness) · Reviewer: orchestrator · Result: **PASS**
- Date: 2026-09-14 · Directive refs: `D-045:D-045-R002,D-045-R008,D-045-R009;D-046:D-046-R001,D-046-R002`

## Readiness checks

1. **Spec pinned to accepted evidence, nothing guessed.** The contract quotes the accepted
   M4-T016 A2 research: Part 4.3 item 2 (the B4 decomposition line), Part 2.2 steps A–D (the
   buffer/intersection design), Part 2.3 (CRS/unit evidence — EPSG:2263 both sides, US survey
   foot independently confirmed), Part 2.4 EC-1..6 (each edge case bound to a typed requirement
   in the objective). The legal constant (100.0 ft) cites ZR 23-22 footnote 1 as already pinned
   verbatim in `r6_r7_r8_wide_street_conditional_far.rule.json`. Width classification and the
   named-street/alternate-width §12-10 questions are explicitly OUT of scope (EC-5 typed
   attested-preconditions input; B7 wires later, LAST — accepted wave-5 queue).
2. **Dependencies accepted.** B3 (M4-T020) ACCEPTED this session (207th, DCV 5/5, seam
   98d09541); mappluto_geometry_arcgis (M2-T009), dcm_street_width_classifier (M4-T015) and
   the D-052 policy layer (M4-T019) all accepted. `depends: [M4-T020]` recorded.
3. **Zero new dependencies.** shapely==2.0.7 is ALREADY ADMITTED (services/api/pyproject.toml
   pin with GEOS-determinism assertions); the packet forbids dependency files and requires the
   determinism assertions in the module's own tests. §G untouched.
4. **Scope disjoint by construction.** Two NEW files + own report; forbidden_paths fence every
   accepted connector, all rules, dependency files, and the control plane. No open task shares
   any allowed path (M4-T020/M5-T025/M5-T026 all accepted; no other claimed task touches
   services/api/**).
5. **Directive binding verified.** `evaluate_task_refs(M4-T021)` → ok, applicable == cited ==
   exactly the five IDs; digests resynced (D-045 8944c6be→9de82f18, D-046 ba17c674→40e99052)
   with audit_log entries in this same seam commit (c14 discipline).
6. **Placeholders seeded.** Both new allowed_paths files committed as one-line placeholders
   (ruff-clean) so the gate identity has tracked files (zero-tracked-files fail-closed guard).
7. **Acceptance scenarios executable.** S1–S5 are offline synthetic-fixture scenarios with
   documented test commands (focused file, full connectors suite, ruff, modularity) — the same
   verification profile the loop worker auto-approves (M4-T020 precedent).
8. **Loop-dispatch fit.** Packet sized for one unit (single module + test file); path_notes
   record the shift-2 dispatch intent (run persistent-local-35, sole writing producer,
   worker claude-fable-5 via EXTRA USAGE per D-058-R004).

## Verdict

**PASS** — contract ready for claim and loop dispatch.
