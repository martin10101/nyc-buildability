# NYC Buildability — Rules Engine Architecture (M4-T001)

Canonical architecture for the **reusable** zoning-rules system: a versioned JSON rule DSL, a
deterministic evaluator with full calculation + citation traces, section-level Zoning Resolution
(ZR) source snapshots with provenance, a rule lifecycle whose `published`/`Verified` terminus is
reachable only through a qualified-human G6 approval, and coverage honesty for unimplemented
families. This is **not** a one-off R5 FAR calculator — R5 residential FAR is merely the first
family; a structurally different family (a rear-yard rule) is representable with **zero engine
changes**.

> **Permanent boundary (owner directive 2026-07-20 item 5; PRD §10–§12; G6).**
> AI retrieves, classifies, and drafts candidate rule representations. Deterministic code calculates.
> A qualified human approves legal interpretations. **No rule is `published` and no result is
> `Verified` without a recorded G6 qualified-human approval.** Agent consensus can never substitute.

## 1. Module map (`services/api/app/rules/`)

| File | Responsibility |
|---|---|
| `lifecycle.py` | Rule statuses + transitions; `G6Approval`; `publish()` refuses without a G6 approval. |
| `coverage.py` | The six PRD-§12 coverage statuses + three completeness statuses (identical to the canonical `coverage_status` contract; a test asserts no drift) + `most_severe()`. |
| `operations.py` | Two closed, pure vocabularies: numeric `COMPUTE_OPS` and boolean `PREDICATE_OPS`. No `eval`, no string-expression parser. |
| `snapshots.py` | Loads section-level ZR snapshots, verifies content digests (tamper-evidence), exposes provenance. |
| `models.py` | `RuleDefinition`, `EvaluationTrace`, `RuleResult` (with the fail-closed provenance export invariant). |
| `dsl.py` | Loads + validates a rule document (JSON Schema + lifecycle guard + referential integrity) into a `RuleDefinition`. |
| `evaluator.py` | Pure deterministic evaluation → full trace; missing-data + uncertainty handling; coverage derivation. |
| `registry.py` | Loads the ruleset directory; indexes by id/family; answers coverage queries honestly. |
| `schemas/v1/` | `rule_definition.schema.json`, `evaluation_trace.schema.json` — the versioned contracts. |
| `rulesets/` | Production rule documents (`*.rule.json`). First: `r5_residential_far.rule.json`. |

Source snapshots live under **`docs/research/zr-snapshots/v1/`** (see §5). Second-family
representability proof + its synthetic snapshot live under `services/api/tests/rules/fixtures/`.

## 2. The versioned rule DSL

A rule is a JSON document validated against `schemas/v1/rule_definition.schema.json`. It is
**family-agnostic**: a FAR rule, a yard rule, and a height rule all use the same shape and the same
closed op set, so families are **data, not code**. Key sections:

- **Identity/versioning**: `rule_id`, `rule_version` (semver, `-draft` suffix allowed), `family`,
  `jurisdiction`, `status`, `title`, `description`.
- **`citations[]`**: each binds the rule to a `snapshot_id` (§5), a `section`, a verbatim `quote`,
  and the section's `last_amended` (effective/amendment) date.
- **`inputs[]` / `outputs[]`**: typed, unit-tagged, with `required` flags and optional `enum`s.
- **`parameters[]`**: named scalars **or** key→number maps (e.g. district→FAR), each with a
  `citation_ref` to the snapshot that sources the value.
- **`applicability`**: a recursive predicate tree (`equals` / `in_set` / `exists` / `compare`, with
  `all` / `any` / `not` combinators).
- **`computation`**: an ordered list of **structured steps** — each step names one op
  (`identity`, `add`, `subtract`, `multiply`, `divide`, `min`, `max`, `round`, `clamp`) and its
  arguments; an argument is a `const`, an `input`, a `param`, a `param_select` (map lookup keyed by
  an input), or an earlier `step`. `outputs` map output names to steps. **There is no expression
  string and no `eval`** — every calculation is fully inspectable and reproducible.
- **`exceptions[]`**: documented exception branches with an optional `condition` predicate and an
  `effect` (`conditional_alternative` | `professional_review_required` | `documented_limitation`).
  Exceptions are **surfaced, never silently applied or dropped**.
- **`special_district_interactions[]`**: the general-rule↔special-rule interaction points (stubs
  now; the modifier rule is a later task).
- **`uncertainty_policy`** + **`limitations[]`**: how geometric uncertainty maps to coverage, and
  the rule's honest known gaps.

## 3. Deterministic evaluation + traces

`evaluator.evaluate(rule, inputs, snapshots, spatial_context=None, g6_approval=None)` returns a
`RuleResult` wrapping an `EvaluationTrace`. The trace records: resolved inputs, the applicability
decision with per-predicate reasoning, every computation step with resolved args + result, the
citations **with their embedded source-snapshot provenance**, the coverage + completeness labels,
propagated uncertainty, and applied exceptions. Same rule version + same inputs + same snapshots →
**byte-identical** trace (internal results quantized to 10 dp for cross-platform determinism).

`RuleResult.export()` is the only sanctioned accessor and **fails closed** if any citation lacks a
resolvable provenance block with a content digest (PRD §19: no material value leaves without
provenance).

### Coverage derivation (PRD §12)

| Situation | `coverage_status` | `data_completeness` |
|---|---|---|
| Required input missing | `professional_review_required` | `missing_critical` — **no value computed** |
| Rule not applicable | `not_applicable` | complete / `missing_noncritical` |
| Family has no rule | `unsupported` (visible) | — |
| Applicable, draft rule, clean | `conditional` | complete / `missing_noncritical` |
| Geometric uncertainty (§4) | `professional_review_required` | — |
| Geometric data conflict (§4) | `data_conflict` | — |
| **Published rule + matching G6 approval** | `verified` | complete |

A **draft rule tops out at `conditional`**; `verified` is structurally unreachable from an
agent-run evaluation — it requires `status == published` (only reachable via `lifecycle.publish()`
with a `G6Approval`) **and** a matching approval passed at evaluation time.

## 4. M2-T013 uncertainty propagation (never collapse)

The evaluator accepts an optional `spatial_context` shaped like an M2-T013
`LotIntersectionRecord` (its `lot_overall_class`, `professional_review_required`, `coverage_note`).
When the geometric basis for the district is anything other than `single_district_confident`
(i.e. `boundary_uncertain`, `sliver_ambiguous`, `split_lot_confident`, `invalid_geometry_review`)
or `professional_review_required` is set, coverage is **downgraded** to
`professional_review_required`; a `data_conflict` class downgrades to `data_conflict`. The trace's
`uncertainty.collapsed_into_definitive_district` is **always `False`**: the rule never turns
uncertain or split geometry into a single definitive district conclusion (owner directive item 8;
`.claude/rules/geospatial.md`). Uncertain facts stay facts-with-uncertainty.

## 5. Section-level ZR source snapshots + provenance

Snapshots under `docs/research/zr-snapshots/v1/*.snapshot.json` capture a small section-level
extract with the **same provenance discipline the future M3 corpus will use** (per the accepted
M1-T004 research, `docs/research/zoning-resolution-2026-07-16.md`): `request_url`, `retrieved_at`,
the section's `Last Amended` date, a document-currency note, a `verbatim_excerpt`, and a
`content_digest_sha256` verified on load (tamper-evidence). Each snapshot carries an
`extraction_status` and an explicit `raw_html_verified` flag.

**First snapshot — `zr-23-21`** (NYC ZR §23-21 *Floor Area Regulations for R1 Through R5
Districts*, Last Amended 2024-12-05) was captured from the official DCP portal. Per M1-T004 §5.5,
an AI-summarized markdown capture is **not** a raw-HTML byte capture: `zr-23-21` is therefore an
`extracted_draft` with `raw_html_verified: false` — a drafted candidate pending raw-HTML
verification **and** G6 professional approval before any citing rule is published. This is fully
consistent with the AI boundary: the engine retrieved and drafted; a human verifies and approves.

**M3 alignment.** `docs/research/zr-snapshots/v1/` is the documented legal-corpus snapshot layout;
M3 corpus ingestion should adopt it (per-section records, `Last Amended`, content digests,
document-currency banners) rather than fight it. Bulk/full-corpus ingestion remains an M3 task; this
slice captures only the specific sections its rules implement.

## 6. Rule lifecycle + the G6 boundary

`discovered → extracted_draft → needs_review → (G6 human approval) → published`. The canonical
lifecycle names an `approved` step (`.claude/rules/legal-rules.md`); here the **`G6Approval` record
is that approval event**, and `lifecycle.publish()` consumes it to reach `published`. Agents/the
engine may author only up to `needs_review` (`assert_agent_authorable`); the DSL loader rejects any
authored rule declaring `published`. Only a `published` rule evaluated with its matching G6 approval
emits `verified`.

## 7. Coverage honesty

`RuleRegistry.family_coverage(family)` returns a **visible** `unsupported` for any family with no
implemented rule (RE-S7) — never silence. Implemented families report `conditional` (draft) with the
contributing rule ids.

## 8. Promotion path for the rule contracts

`rule_definition.schema.json` and `evaluation_trace.schema.json` are **engine-owned** versioned
contracts today because no cross-tier consumer (UI/report) exists yet (`apps/web/**` is out of scope
for M4-T001). When the reviewer UI or report layer first consumes rule/trace documents, these
schemas should be **promoted into `packages/contracts/schemas/v1/`** through the accepted M2-T010
tooling (additive, byte-identical bundle + generated TS), so the whole platform shares one canonical
rule + evaluation-trace contract. Until then they are validated at load via `jsonschema` and by the
acceptance pack. This is a documented, deliberate altitude choice — not a competing/forked schema.

## 9. Testing

The legal-rule acceptance pack (`services/api/tests/rules/test_rules_engine.py`) covers RE-S1…RE-S8
and the `docs/ACCEPTANCE_SCENARIO_STANDARD.md` legal-rule cases (applies+passes, applies+fails,
not-applicable, threshold boundary, missing input, general-modified-by-special, exception
applies/does-not, effective-date/citation + rule-version assertions), plus DSL integrity guards,
snapshot tamper-evidence, and a diff-provable "families are pure data" check (no engine file
mentions any family or district name). All tests are offline and deterministic.

## 10. Known limitations (this slice)

- `zr-23-21` is a summarizer-mediated draft capture pending **raw-HTML verification + G6**; the R5
  rule is `needs_review`, never `Verified`.
- Only standard-zoning-lot R5 FAR is computed; the qualifying-residential-site FAR and the
  single-dwelling-unit 0.60 equivalent-FAR cap are surfaced (conditional / documented limitation),
  not computed.
- Special-district FAR modifiers are interaction-point stubs, not implemented rules.
- The client R5 benchmark-sheet validation is blocked on **B-010** (owner-provided); all
  architecture/engine/snapshot/fixture work proceeds without it.
