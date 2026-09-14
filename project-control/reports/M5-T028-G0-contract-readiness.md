# M5-T028 G0 — contract readiness (orchestrator)

- Task: M5-T028 — Dependable answers 2 (D-059-R003 completion): remove the hardcoded ZR 23-21 section label from the five live-wired scenario-analysis modules
- Gate: G0 (contract readiness) · Reviewer: orchestrator · Result: **PASS**
- Date: 2026-09-14 · Directive refs: `D-059:D-059-R003;D-046:D-046-R001,D-046-R002`

## Readiness checks

1. **Origin is an independent reviewer finding, not a self-report.** This packet exists because
   the M5-T027 G3 reviewer (code-reviewer, independent of the producer) found advisory A1: the
   D-059-R003 defect class survives in five sibling modules outside M5-T027's allowed_paths.
   The reviewer also proved the surfaces are LIVE: `main.py` mounts `scenario_analysis_v1_router`,
   whose handlers route through `derive.py`'s `derive_practical_usable_range`.
2. **Finding independently reproduced by the orchestrator before contracting.** `grep` at the
   live head confirms all six occurrences: `derive.py:82`, `breakeven.py:155`,
   `comparison.py:118` and `:129`, `ranking.py:114`, `sensitivity.py:128` — each hardcoding
   "ZR 23-21" in prose that is emitted regardless of the district family evaluated.
   `derive.py:82` is the `DERIVED_RANGE_LABEL` constant emitted unconditionally as the label of
   every `derived_practical_usable_range` document (not a fallback path).
3. **Reuse, not a second mechanism.** The contract requires reusing the derivation seam M5-T027
   established (`constants.py` `_residential_far_family_label` / `coverage_matrix_rows`,
   `builder.py` `_cap_citation_section`) rather than inventing a parallel one; those two files
   are FORBIDDEN here so the accepted seam cannot be mutated by this packet.
4. **Fail-safe direction specified.** Where a surface genuinely lacks evaluated-rule context at
   string-construction time, the contract requires taking the derived value from the caller or
   stating the section generically — explicitly never defaulting to 23-21. This prevents the fix
   from re-introducing the same class of silent assertion.
5. **Provenance prose protected.** S3 requires the surrounding reviewed wording (DRAFT labelling,
   transported-verbatim statements, typed-assumption language) to stay byte-identical apart from
   the section reference — this is a reference correction, not a rewrite of reviewed text.
6. **Scope disjoint under D-046.** The five modules + their five test files are disjoint from
   M5-T027's scope (forbidden here), from the M4-T021 connectors lane, and from every other open
   task. Concurrency stays at or below the ceiling of 3.
7. **Directive binding verified.** `evaluate_task_refs(M5-T028)` → ok, applicable == cited ==
   {D-059-R003, D-046-R001, D-046-R002}; digests resynced (D-059 9bceb56c→1ec1fdbe, D-046
   5b0706d4→d8991faf) with audit_log entries in this same seam commit (c14). Validator exit 0.
8. **No placeholder seeding needed.** All ten source/test files exist and are tracked; only the
   producer report is new.
9. **Dependency recorded.** `depends: [M5-T027]` — this packet builds on the derivation seam that
   task established; M5-T027 is gated PASS/PASS at contract time with DCV + accept remaining.

## Verdict

**PASS** — contract ready for claim and producer dispatch.
