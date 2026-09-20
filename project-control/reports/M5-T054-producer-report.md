# M5-T054 producer report — ORCHESTRATOR HARVEST RECORD (phase B2 proposal-conditioned rule checks)

**Provenance note (report-preservation rule):** the loop-1 worker (run
`persistent-local-58-m5t054`, 3 cycles, 4285s) completed the implementation but the run
stopped `no_valid_checkpoint` before the worker's own evidence pass was written — the
seeded placeholder was never replaced by the producer. This file is therefore the
ORCHESTRATOR'S harvest assessment (the documented S14/assess-for-harvest pattern,
seq-119 T049 precedent), written from the worktree evidence, not a worker return. No
worker prose exists to preserve; the worker's in-code documentation (module docstring,
test-file header, fixtures README) is the producer's own voice and is part of the
material identity below.

## 1. Material identity

- Task branch commit (wt-m5t054): `f43a9de8`; cherry-picked material commit on
  `candidate/D-024-mrl-option-b`: **`ba0cf6b0`** (9 files, +1601/−8).
- LF-normalized sha256 (first 16) at `ba0cf6b0`:
  - `b8e0878e083aba0c` services/api/app/rules/proposal_checks.py
  - `b66da70ba3671f75` services/api/tests/rules/test_proposal_checks.py
  - `aaa49209e5896b48` tests/rules/fixtures/proposal_checks/README.md
  - `a2944e93ba06515a` tests/rules/fixtures/proposal_checks/rectangle_case.json
  - `27c178f59478ee2a` rulesets/pc-height-setback-demo.rule.json
  - `5877f261c4cc919b` rulesets/pc-lot-coverage-demo.rule.json
  - `00e0c0edd9de1078` rulesets/pc-rear-yard-demo.rule.json
  - `126d117f3b538db7` rulesets/pc-residential-far-demo.rule.json
  - `6371e29966500178` snapshots/pc-demo-synthetic.snapshot.json
- All 9 paths inside allowed_paths; no other file changed in the material commit.

## 2. What was built (against SCOPE 1/2 + 2/2)

`app/rules/proposal_checks.py` (754 lines + module docstring): the FIRST production
caller of `derive_proposal`. Preconditions gate BEFORE derivation (MAX_LOT_LINE_SEGMENTS
1000, MAX_STREET_LINES 500, coordinate/area finiteness, `_capped_repr` at 120 chars —
T051-G5 + DB-034(b)); an EXPLICIT declared fact-mapping table (`PROPOSAL_CHECKS`, frozen
dataclasses; derived PROVIDED facts are compared against rule OUTPUTS only, never fed as
rule INPUTS); evaluation through the EXISTING evaluator/registry (no rule logic, no
ruleset edits — the four fixture rules are test fixtures, not production rulesets);
results typed PASS / FAIL / COULD_NOT_CHECK with `CouldNotCheckReason`
(provided_fact_absent / provided_fact_not_commensurate / no_applicable_rule /
allowance_unresolved / family_unsupported / ambiguous_rule); every result carries
scenario label, proposal id, derivation record ids, source_class
`proposed_derivation`; numeric shortfalls carry provided/required/unit.

DB-034(d): the module builds NO scenario document and emits NO contract version
(imports only derivation symbols + rules registry/coverage) — the
emits-1.1.0-only-when-block-present invariant rides to the first EMITTING packet (B3).

## 3. Self-check results (run by the orchestrator in wt-m5t054 at `f43a9de8`)

- `python -m ruff check .` (services/api cwd): **All checks passed, exit 0**.
- `python -m pytest tests/rules -q`: **722 passed** (81.3s).
- `python -m pytest tests/scenario -q`: **568 passed** (11.8s) — B1 suites untouched.
- `python tools/modularity_check.py --check` (repo root): **exit 0** (only the two
  pre-existing tools/** warns; proposal_checks.py below the hard tier).
- CI on the pushed material head `ba0cf6b0`: **success** (run 35491182686), plus
  context-budget and secret-scan green.

## 4. AS-1 CONTRACT CONFLICT — escalated by the producer, adjudicated by the orchestrator

AS-1 as contracted asks the rectangle fixture to show "one yard-class PASS and one
coverage-class FAIL". The producer implemented and escalated (test-file header, §AS-1
comment): a generic minimum wall-to-lot-line setback is NOT a rear-yard depth — no rear
lot line is designated anywhere in the B1 facts, and designating one is a legal
interpretation the module must never make (D-076-R002; permanent principle 1; D-051).
The module therefore surfaces `rear_yard_depth` as COULD_NOT_CHECK
(provided_fact_not_commensurate) BY DESIGN — even with a yard rule present and
computing a number — and demonstrates the commensurable-PASS path via
`building_height` (feet vs feet, attestation-gated) and the FAIL path via
`lot_coverage_ratio` (hand-computed 0.625 > 0.5, shortfall 0.125).

**[ORCH-SCOPE-DISPOSITION]** (T048 AS-3 precedent; recorded here and in the G2 record;
the frozen packet is not edited): AS-1 is satisfied by the commensurable PASS
(building_height) + commensurable FAIL (lot_coverage_ratio) + the STRUCTURAL yard
refusal, which is the honesty behavior the directives require. The refusal is a
deliberate, tested outcome, not a coverage gap. A yard-class PASS becomes producible
only when a future packet adds a caller-designated rear-lot-line input to the B1
derivation — routed to the discovery backlog at the acceptance seam, NOT fixed here
(out of allowed_paths).

## 5. Acceptance scenarios (producer-side status; the wave verifies independently)

- AS-1: PASS under the §4 disposition (hand-computed values exact; label propagation proven).
- AS-2: PASS — unattested street width ⇒ height COULD_NOT_CHECK (allowance_unresolved,
  names the missing attestation); proven against BOTH the synthetic registry and the
  REAL production registry (r5-height), attested and unattested variants.
- AS-3: PASS — ceilings, finiteness (NaN/inf refused pre-derivation, exact dotted field),
  capped reprs; all tested.
- AS-4: PASS — provided vs required explicit; summary always carries could_not_check
  count; no permitted/required/allowed conflation (grep-tested in-suite).
- AS-5: PASS — PROPOSAL_CHECKS is declared frozen data; unmapped families surface
  typed (family_unsupported / no_applicable_rule), never silent PASS.
- AS-6: PASS — no scenario-document construction/emission (import + grep proof in-suite);
  §2 disposition recorded for B3.
- AS-7: PASS — pure parameters; stdlib + B1 derivation + rules registry/coverage only;
  bounded iteration.
- AS-8: PASS — §3 numbers above.

## 6. Routed discoveries (D-069; NOT fixed in-packet)

- (a) Rear-lot-line designation as a future caller input to B1 derivation (unlocks a
  true commensurable yard check) — route to backlog at the seam.
- (b) Residential zoning floor area vs geometric gross: same commensurability class;
  a future explicit inclusions/exclusions mapping (legal review) would unlock FAR checks.
- (c) The checkpoint-envelope stop (`no_valid_checkpoint` after 3 cycles) repeats the
  known S14 class; controller-side, R247-gated — not per-run fixable.
