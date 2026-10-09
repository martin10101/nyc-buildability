# M5-T064 producer report — max-envelope engine slice 1 (D-082-R002) — corrected evidence handoff

Producer: scenario-optimization-engineer. Worktree: `wt-m5t064`. Branch: `task/M5-T064-max-envelope`.
Base (claim seam) HEAD: `f98924e5`. All work is UNCOMMITTED in the working tree; commit, push, CI, the
LF-normalized sha256 digest-binding of the full file contents, and acceptance are the orchestrator's.

**What this revision is.** Evidence repackaging only — this handoff establishes NO implementation defect
and this unit changes NO code: it edits ONLY this report (allowed_path #5); the four source/test files
(#1–#4) are UNTOUCHED by this unit. The gaps being corrected are evidence-presentation gaps, not
implementation defects. This revision, staying inside the five allowed_paths:

1. **specifies the supervisor's digest-bound body repackaging** (§"Handoff — digest-bound body sections")
   so a reviewer can read the COMPLETE implementation and test bodies as their own bounded, digest-bound
   sections instead of scrolling past this report to find them in the aggregate diff — the report keeps
   concise path + line anchors, the bodies ride the harvest sections;
2. **fixes the byte-unchanged claim**: producers do not run hashing (ADR-005 + native-tool preference),
   so byte-identity vs the prior submission is labeled UNVERIFIED at the producer level and routed to the
   harvest digest binding (§"Byte-identity"); what IS producer-verifiable — that this unit touched no
   code — is stated as such;
3. records MY **freshly re-collected (this unit)** self-check outcomes for all four documented commands
   with explicit cwd (§"Self-check");
4. preserves the wrong-cwd failed transcripts as SEPARATE, prior-recorded outcomes (§"Preserved failed
   transcripts") — NOT reproduced this unit, NOT fixed;
5. retains the bounded accepted checker/registry parity excerpts (§"Accepted-source excerpts"), the
   cohesion justification (§"Cohesion"), and the provenance/honesty record (§"Provenance").

Per the packet REPORT DISCIPLINE the four allowed_paths are referenced here by path + line anchors, not
embedded verbatim; their complete digest-bound contents are the supervisor's harvest collection
(§"Handoff — digest-bound body sections"). CI is explicitly PENDING and is the orchestrator's to establish.

## Changed surface — the five allowed_paths (reference + line anchors; nothing outside scope)

| # | Path | Lines | Role / key anchors |
|---|---|---|---|
| 1 | `services/api/app/scenario/max_envelope.py` | 999 | engine (new). Public entry `derive_max_envelope` L938-998; dimension table `ENVELOPE_DIMENSIONS` L226-265; resolution `_build_rule_inputs` L405-422 / `_family_traces` L425-435 / `_select_binding` L448-510 / `_conflict_advisory` L513-529 / `_resolve_dimension` L532-574; geometry `_lot_rectangle` L624-691 / `_footprint_area` L694-704 / `_shoelace_area` L715-726 / `_rect_coverage` L729-734 / `_shrink_depth_to_cap` L737-756 / `_height_levels` L759-772 / `_build_candidate` L775-897; consistency proof `_verify_consistency` L900-930; mirror seams `_USABLE_COVERAGE` L118, `_SATURATING_CHECK_IDS` L269-272 |
| 2 | `services/api/app/api/v1/max_envelope_api.py` | 343 | flag-gated UNMOUNTED route (new). Status matrix `MAX_ENVELOPE_STATUS_STATE_MATRIX` L98-106; fail-safe 404 `_not_found` L140-143; bounded refusals `_bounded_field` L146-151 / `_validation_error` L154-166; route caps `_enforce_route_caps` L195-214; handler `post_max_envelope` L217-342 (flag gate L222-223; bounded body L228-242; typed refusals L268-300; single engine call off-loop L304-333) |
| 3 | `services/api/tests/scenario/test_max_envelope.py` | 643 | engine acceptance pack (new). Drift guard L148-149; AS-1 L157-229; AS-2 L248-281; AS-3 L289-305; AS-4 L313-414; fitted-placement L424-566; AS-5 L574-580; AS-6 L588-643 |
| 4 | `services/api/tests/api/test_max_envelope_api.py` | 275 | route acceptance pack (new). Happy path L99-138; flag-off/UNMOUNTED L146-164; bounded/typed refusals L172-232; determinism L240-245; gap paths L248-274 |
| 5 | `project-control/reports/M5-T064-producer-report.md` | this file | this report |

`main.py`, `app/rules/**`, `proposal*.py`, `proposal_checks_api.py`, `_proposal_fact_domains.py`,
`site_definition/**`, contracts, and `apps/web/**` are unchanged (imported read-only).

## Self-check — MY outcomes (freshly re-collected THIS UNIT; explicit cwd)

Each is a `documented_test_command` run EXACTLY as documented, standalone (never chained onto another
command). `cd services/api` first (cwd persists) for ruff + both pytest; the modularity check runs from
the worktree root.

| # | Command (documented) | cwd | Outcome (this unit) |
|---|---|---|---|
| 1 | `python -m ruff check .` | `services/api` | `All checks passed!` (exit 0) |
| 2 | `python -m pytest tests/scenario/test_max_envelope.py tests/api/test_max_envelope_api.py -q` | `services/api` | `56 passed in 3.82s` (exit 0) |
| 3 | `python -m pytest tests/api tests/scenario tests/rules -q` | `services/api` | `1949 passed in 59.67s` (exit 0) |
| 4 | `python tools/modularity_check.py --check` | worktree root | `selected 472 files; failures 0; warnings 21` (exit 0 — PASS; `max_envelope.py` carries a `review_signal` warning, justified in §"Cohesion") |

**Local ≠ CI (binding distinction).** These four are VERIFIED LOCAL outcomes at the uncommitted
working-tree state — NOT a CI claim. AS-6's "CI green at the pushed head" is PENDING and is the
ORCHESTRATOR's to establish AFTER commit and push. Nothing here marks CI as passed. The supervisor
RE-COLLECTS these at harvest as the gate evidence.

## Preserved failed transcripts — wrong-cwd artifacts (separate outcomes; prior-recorded; NOT fixed)

Preserved separately per instruction. These were recorded in a PRIOR handoff and are NOT reproduced this
unit (this unit ran the four documented commands only, each from its correct cwd — §"Self-check"). They
are real wrong-cwd invocation artifacts — NOT implementation defects, and NOT in the five allowed_paths:

- `python -m ruff check .` from the **worktree root** → exit 1, `Found 45 errors.` EVERY finding is in
  out-of-scope repo-root scripts (`tools/**`, `project-control/reports/**` — e.g.
  `tools/modularity_check.py`, `tools/project_control.py`, `tools/agent_supervisor/*`); ZERO are in
  `services/api` and NONE are in the five allowed_paths. From `services/api` the identical command is
  `All checks passed!` (self-check row 1). These repo-root files are out of scope and deliberately NOT
  fixed here (packet: surface out-of-scope findings, never fix in-packet); "fix unrelated root lint" is
  explicitly out of scope for this task.
- `python -m pytest tests/api tests/scenario tests/rules -q` from the **worktree root** → exit 4,
  `file or directory not found: tests/api … no tests ran` (the `tests/` tree lives under
  `services/api/tests`). From `services/api` the identical command is `1949 passed` (self-check row 3).
  Matches CODING_RULES ("run api pytest from `services/api` cwd").

Conclusion: the failed transcripts are wrong-cwd invocation artifacts plus pre-existing out-of-scope
repo-root lint; they establish no defect in the five allowed_paths. The documented commands are ALWAYS
run from `services/api` (ruff + pytest) / the worktree root (modularity) per the COMMAND CWD binding.

## Accepted-source excerpts — for parity + provenance (READ-ONLY; verify against source)

Bounded excerpts of the accepted, read-only sources the engine mirrors, each with an exact path + line
anchor so a reviewer can verify arithmetic parity and provenance at the exact seams the engine consumes
(the anchors were current at this handoff; treat line numbers as advisory and confirm the symbol).

### 1. `app/rules/proposal_checks.py` — the checker the engine mirrors

Usable-coverage set (L285) — the engine's `_USABLE_COVERAGE` (`max_envelope.py` L118) is bound
byte-identical to this by the drift-guard test `test_usable_coverage_matches_accepted_checker`
(`test_max_envelope.py` L148-149):

```python
# proposal_checks.py L264
RULE_INPUT_LOT_AREA_SOURCE = "lot_context.area_sq_ft"
# proposal_checks.py L270-279
CALLER_RULE_INPUT_NAMES = (
    "zoning_district", "street_width_class", "site_class", "overlay_present",
    "special_district_present", "historic_district", "large_site", "lot_depth_ft",
)
# proposal_checks.py L285
_USABLE_COVERAGE = frozenset({cov.COVERAGE_CONDITIONAL, cov.COVERAGE_VERIFIED})
```

Input assembly (L525-542) — the engine's `_build_rule_inputs` (`max_envelope.py` L405-422) mirrors this
exactly: lot area is the single source of truth `lot_context.area_sq_ft`, and only keys in
`CALLER_RULE_INPUT_NAMES` are fed; any other key is recorded unmapped and NEVER fed:

```python
# proposal_checks.py L533-542
    inputs: dict = {_LOT_AREA_INPUT: float(lot.area_sq_ft)}
    bindings: dict[str, str] = {_LOT_AREA_INPUT: RULE_INPUT_LOT_AREA_SOURCE}
    unmapped: list[str] = []
    for key, value in lot_rule_facts.items():
        if key in CALLER_RULE_INPUT_NAMES:
            inputs[key] = value
            bindings[key] = f"caller_lot_fact:{key}"
        else:
            unmapped.append(key)
    return inputs, bindings, tuple(sorted(unmapped))
```

### 2. `app/scenario/derivation.py` — the coverage arithmetic the candidate must satisfy

Shoelace area (L302-311) — the engine's `_shoelace_area` (`max_envelope.py` L715-726) is the IDENTICAL
operation in the IDENTICAL float order, so the coverage the engine computes to size the footprint is
byte-equal to the coverage the checker computes on the SAME outline:

```python
# derivation.py L302-311
def _shoelace_area(closed_ring: Sequence[_Point]) -> float:
    total = 0.0
    for i in range(len(closed_ring) - 1):
        x1, y1 = closed_ring[i]
        x2, y2 = closed_ring[i + 1]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0
```

Coverage denominator (L450) — the checker divides the footprint area by the AUTHORITATIVE recorded lot
area; the engine's `_rect_coverage` (`max_envelope.py` L729-734) uses the same `shoelace / lot_area`:

```python
# derivation.py L442-451  (inside _derive_coverage)
    lot_area = float(lot.area_sq_ft)
    ...
    return EvidenceRecord(
        value=footprint_area / lot_area,
        unit="ratio",
        method="footprint_over_lot_area",
```

### 3. `app/rules/registry.py` — evaluation, conflict detection, coverage honesty

The engine's `_family_traces` (`max_envelope.py` L425-435) calls `family_coverage` then
`evaluate(...).export()`; `_conflict_advisory` (L513-529) calls `detect_conflicts` (getattr-guarded, so
a test double without it returns `None`); neither ever picks a conflict winner:

```python
# registry.py L189-197
    def detect_conflicts(self, family, inputs, as_of_date=None) -> dict | None:
        """FH-2: detect a strictly fail-closed same-family rule conflict ... never picks a winner."""
        self._ensure()
        return detect_rule_conflicts(self._by_family.get(family, []), inputs, as_of_date)
# registry.py L199-214
    def family_coverage(self, family: str) -> dict:
        """Coverage honesty (RE-S7): a family with no implemented rule is a VISIBLE unsupported ..."""
        self._ensure()
        if family not in self._by_family:
            return {"family": family, "coverage_status": cov.COVERAGE_UNSUPPORTED, "note": "..."}
        return {"family": family, "coverage_status": cov.COVERAGE_CONDITIONAL, "note": "...",
                "rule_ids": [r.rule_id for r in self._by_family[family]]}
```

`family_coverage` returning no `rule_ids` is exactly the engine's `FAMILY_UNSUPPORTED` honest-gap path
(`_family_traces` returns `supported=False`); it is never turned into a fabricated ceiling.

### 4. `app/rules/models.py` — provenance fail-closed on every exported value

Every binding value the engine emits is a rule OUTPUT taken through `RuleResult.export()`; export FAILS
CLOSED if any citation lacks resolvable snapshot provenance (PRD s19), so no material value can leave
without provenance:

```python
# models.py L203-212
    def export(self) -> dict:
        for citation in self.trace.citations:
            prov = citation.get("provenance")
            if not prov or not prov.get("content_digest_sha256"):
                raise ProvenanceError(
                    f"rule {self.trace.rule_id}: citation for snapshot "
                    f"{citation.get('snapshot_id')!r} has no resolvable provenance; "
                    "a material rule value may not be exported without it (PRD s19)."
                )
        return self.trace.as_dict()
```

**Parity summary.** `me._USABLE_COVERAGE` ≡ `pc._USABLE_COVERAGE` (test-pinned); `me._build_rule_inputs`
≡ `pc._build_rule_inputs` shape; `me._shoelace_area` ≡ `derivation._shoelace_area` (byte-order
identical); `me._rect_coverage` = `shoelace / lot_area` ≡ the checker's `footprint_area / lot_area`;
family resolution flows through `registry.family_coverage` + `registry.evaluate().export()`; conflicts
surface via `registry.detect_conflicts` and are never resolved here. This is why the candidate the
engine emits PASSes `check_proposal` at the derived values (AS-4).

## Cohesion — `max_envelope.py` justification (modularity review record)

`max_envelope.py` is 999 lines — above the justification threshold, below the 1000-SLOC hard-fail;
`modularity_check.py --check` reports `failures 0` (PASS) with a `review_signal` on this file (self-check
row 4). Per `.claude/rules/code-architecture.md` item 6 the cohesion justification: the module is ONE
responsibility — deriving the deterministic maximum envelope for the single rectangle-prism massing
class — behind ONE public entry (`derive_max_envelope`). Its private helpers are three tightly-coupled
stages of that single computation: (a) registry-derived dimension resolution (`_build_rule_inputs`,
`_family_traces`, `_select_binding`, `_conflict_advisory`, `_resolve_dimension`); (b) candidate geometry
construction (`_lot_rectangle`, `_footprint_area`, `_shoelace_area`, `_rect_coverage`,
`_shrink_depth_to_cap`, `_height_levels`, `_build_candidate`); (c) the generator-checker consistency
proof (`_verify_consistency`). These are not separable concerns: the geometry helpers exist ONLY to
saturate the resolved binding values in a shape whose coverage — computed by `_shoelace_area`/
`_rect_coverage` in the SAME float order `check_proposal` uses — is byte-consistent with the checker
that (c) then runs on the result. Splitting the geometry helpers into a separate module would FORK that
shoelace/float-order contract away from its single consumer and its consistency proof, with no
independent reuse today. There is no unrelated domain logic, persistence, external I/O, or CLI/API
wiring here: the HTTP seam is the separate `max_envelope_api.py`, and serialization is confined to small
`as_dict` methods on the co-located result dataclasses. A future extraction of the geometry stage
(carried with a shared shoelace-parity test against `check_proposal`) is routed as a discovery below
rather than done in this scope-locked slice.

## Provenance / honesty (D-076-R002)

Every binding value is a rule OUTPUT taken through `RuleResult.export()` (resolvable provenance, fail-
closed per §"Accepted-source excerpts" item 4); no hand-copied constant exists. The envelope carries a
fixed disclosure (`ENVELOPE_DISCLOSURE`, `max_envelope.py` L100-109): a deterministic rules-derived
ESTIMATE, not a record/permit/approval/determination; the tightest-rule intersection is conservative and
where rules compete which governs is surfaced for professional review, not resolved. FAR and rear-yard
are ALWAYS honest gaps (`semantic_gap`, L206-217, L253/L263): the prism's geometric gross is not a zoning
floor area and the prism designates no rear lot line. The candidate is FITTED to the lot's actual
EPSG:2263 geometry — anchored at the lot's real SW corner, scaled to the lot's proportions, and PROVEN
contained. At the lot's real large-magnitude 2263 coordinates the honest guarantee is `coverage <= cap`
while saturating it (`_shrink_depth_to_cap`; a +epsilon mutation still FAILs the checker), NOT an
exact-float byte-equality claim.

## Acceptance scenarios → tests (evidence pass)

All six acceptance scenarios map to named regression tests across the two test files (56 tests, all
passing in self-check rows 2/3):
- **AS-1** registry-derived binding values + honest-gap-not-invented-ceiling —
  `test_as1_*` (`test_max_envelope.py` L157-229), incl. the drift guard L148-149.
- **AS-2** per-dimension binding + out-competed provenance with a mutation-flip —
  `test_as2_*` L248-281.
- **AS-3** enumerate-the-dimensions honest gaps in engine + route —
  `test_as3_*` L289-305; route body `test_200_returns_the_envelope` (`test_max_envelope_api.py` L117-120).
- **AS-4** generator-checker consistency (candidate PASSes `check_proposal`; +epsilon FAILs; ambiguous
  multi-rule family tolerated as `could_not_check`) — `test_as4_*` L313-414.
- **AS-5** determinism + route discipline (bounded/typed refusals, flag-off 404 sentinel, UNMOUNTED
  absent from openapi) — `test_as5_deterministic` L574-580; `test_max_envelope_api.py` L146-245.
- **AS-6** preservation (full api suite green, ruff clean, modularity exit 0 — CI at the pushed head is
  the orchestrator's) — self-check rows 1/3/4; `test_route_is_unmounted_in_the_real_app` L157-164.

## Discovery routing (D-069; surfaced, not fixed in-packet)

- Only the axis-aligned rectangle lot class is a supported candidate placement target in slice 1;
  non-rectangular lots emit an explicit typed `LOT_GEOMETRY_UNSUPPORTED` gap (no fabricated candidate).
  General parcel-polygon fitting is deferred to a later slice / the map-drawing editor.
- In the REAL registry today `lot_coverage` and `rear_yard` have no implemented rule, so a real-lot
  envelope gaps coverage (`FAMILY_UNSUPPORTED`) → no candidate until a `lot_coverage` rule is published;
  FAR is a non-commensurable gap (`test_real_registry_compatibility` L628-643). A developer-facing
  "maximum buildable floor area" would need a legal designation equating zoning floor area to geometric
  gross — deferred, not made here.
- A future extraction of the geometry stage of `max_envelope.py` (with a shared shoelace-parity test
  against `check_proposal`) is a candidate if the module grows further — routed here, out of scope.
- Out-of-scope repo-root ruff findings (45, in `tools/**` and `project-control/**`) surfaced by the
  wrong-cwd invocation are pre-existing and NOT in this packet's scope; surfaced here, not fixed.

## Byte-identity — producer-verifiable vs harvest-bound (R5)

- **Producer-verifiable (this unit):** this unit edits ONLY this report (allowed_path #5). It runs no
  Edit/Write against the four code files (#1–#4); it makes no code change. That is stated as fact, not as
  a byte-identity claim.
- **UNVERIFIED at the producer level:** whether the four code files are byte-identical to the PRIOR
  submission's frozen copies is NOT producer-verified. Producers do not run hashing (ADR-005 +
  native-tool preference: the only commands run through the broker are this task's four documented
  commands; `git hash-object`/`sha256` are not among them). No prior/current digest pair is asserted
  here; the earlier "byte-unchanged" wording is withdrawn and replaced by this label.
- **Routed to harvest:** the supervisor establishes the LF-normalized sha256 of each of the four files
  over the working-copy bytes (strip `\r` before hashing — the working copy is LF and `git diff --stat`
  warns LF→CRLF on checkout) and, if a prior-submission digest set exists, states prior==current or
  prior≠current explicitly. That digest binding is the authoritative parity record; this report does not
  substitute prose for it.

## Handoff — digest-bound body sections (supervisor repackaging spec)

So the COMPLETE implementation and test bodies are reviewable as their OWN bounded, digest-bound sections
— visible on their merits rather than scrolled past this report in the aggregate diff — the harvest
collection presents each of the four allowed_path bodies as a delimited section, in this order, each
headed by its path, line count, and its LF-normalized sha256 (computed by the supervisor per §"Byte-
identity"), then the full file body verbatim:

1. `services/api/app/scenario/max_envelope.py` (999) — engine.
2. `services/api/app/api/v1/max_envelope_api.py` (343) — flag-gated UNMOUNTED route.
3. `services/api/tests/scenario/test_max_envelope.py` (643) — engine acceptance pack.
4. `services/api/tests/api/test_max_envelope_api.py` (275) — route acceptance pack.

This report deliberately keeps concise path + line anchors (§"Changed surface") and the read-only parity
excerpts (§"Accepted-source excerpts") only; the four full bodies are NOT duplicated into this report
(REPORT DISCIPLINE) — they are the harvest sections above. Because those sections are digest-headed and
presented on their own, a reviewer evaluates the actual code and tests directly, not a paraphrase and not
a diff in which this report sorts first and hides them.

Remaining, and structurally the supervisor's / orchestrator's (producers do not run git, hashing, or CI
— ADR-005 + the native-tool preference):

1. **Digest-bound body sections + digests** for the four allowed_paths (spec above; §"Byte-identity").
2. **Commit, push, and CI** — CI at the pushed head (AS-6) is explicitly PENDING and the orchestrator's
   to establish; nothing here claims it.
3. **Gate records** (G0,G2,G3,G4,G5) recorded by the orchestrator from the re-collected evidence.

Resubmit-ready: the packet now carries the supervisor digest-bound body repackaging spec, the corrected
byte-identity labeling, the freshly re-collected command evidence with explicit cwd, the preserved
wrong-cwd transcripts, the bounded accepted-source parity excerpts, and the cohesion justification. No
source or execution evidence is substituted by prose; no code was changed by this unit.
