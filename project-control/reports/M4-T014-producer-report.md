# M4-T014 Producer Report — A1 wave 1b: R3/R4-series height/setback draft rule families

Task: M4-T014 (D-045:D-045-R001,R008,R009 + D-046 wave-1). Producer: rules-engineer.
Status requested: **awaiting_gate**. Nothing here is a Verified determination; every
rule is `needs_review` (DRAFT); G6 qualified-human approval remains the only path past
`needs_review` (D-045-R009 preserved verbatim).

## Setup guards (executed in order)

1. `git rev-parse --show-toplevel` →
   `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-a755bdcc29b159b8a`
   (NOT ctl24 — guard passed).
2. `git reset --hard 5450d39f` → `HEAD is now at 5450d39f M4-T014 G0 PASS + claimed`.
   (Only permitted git write; no push/commit/project_control.py run.)

## What was built (file inventory)

New ruleset files (`services/api/app/rules/rulesets/`, all `needs_review`, full provenance):
- `r3_r4_pitched_height.rule.json` — §23-421 pitched envelope for R3A/R3X/R3-1/R3-2/R4/R4-1/R4A.
- `r3_2_r4_flat_height.rule.json` — §23-422 flat envelope for R3-2/R4 (residences not subject to §23-421).
- `r4b_height.rule.json` — §23-422 flat envelope for R4B (flat-only).

New ZR snapshots (canonical `docs/research/zr-snapshots/v1/`, synced byte-identically to the
runtime bundle `services/api/app/_zr_snapshots/v1/` via the established `sync_zr_snapshots` mechanism):
- `zr-23-42.snapshot.json`, `zr-23-421-r3-r4.snapshot.json`, `zr-23-422-r3-r4.snapshot.json`.

New tests: `services/api/tests/rules/test_r3_r4_height.py` (90 cases).

Reports: this file + `project-control/reports/M4-T014-source-capture.md`.

No engine/evaluator/api/scenario/connectors/schema file was touched (see scope-compliance below).

## Variant list with anchors (authoritative, from fresh in-task capture)

- §23-421 pitched (opening district-list anchor): **R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A R5A**;
  R3/R4 members in scope R3A/R3X/R3-1/R3-2/R4/R4-1/R4A → uniform 25 ft perimeter wall + 35 ft ridge.
- §23-422 flat (opening district-list + per-statement anchors): **R3-2 R4 R4B R5 R5B R5D**;
  R3-2/R4 → 35 ft building height; R4B → 25 ft building height.
- Asymmetry (recorded, never symmetrized): R4B flat-only; R3A/R3X/R3-1/R4-1/R4A pitched-only;
  R3-2/R4 dual-section (building type selects the envelope). R1/R2 excluded (B-023); R5A/R5/R5B/R5D
  belong to the accepted M4-T006 pilot.

## Provisions that became TYPED A2 GAPS (D-045-R008; never numeric)

- §23-421 sloping-plane setback geometry → exception `pitched_plane_setback_professional_review`,
  effect `documented_limitation` (surfaced, never a numeric setback output).
- `building_type` (pitched-vs-flat selection) → REQUIRED input, no canonical property_profile field,
  unavailable in practice ⇒ `professional_review_required` with no value.
- §23-424/§23-425 qualifying-site / large-site increases; §23-426/§23-44 historic-district /
  special-district / commercial-overlay modifications → limitations + PRR exceptions; base-plane
  determination noted as a separate professional input. No street-width-conditional value entered
  the R3/R4 caps (the §23-423 10/15-ft depth is not triggered by these single flat caps).

## Design note — grouping vs per-file separation

The R3/R4 pitched variants share ONE uniform §23-421 envelope under ONE source enumeration, so
they are encoded as one `in_set` rule — mirroring the ACCEPTED precedent `r1-r2-r3-residential-far`
(which groups R1-2A…R3-2 under one in_set when the source gives one value). The R5 pilot split
R5/R5A/R5B/R5D because their VALUES differ; here values differ across the three groupings
(pitched 25/35 vs flat 35 vs R4B 25), so those three are separate rules. Per-variant + cross-section
isolation is fully tested regardless (NC-1/NC-2/NC-8).

## Acceptance scenarios — evidence

**S1 per-variant extraction with provenance** — PASS. Each grouping gets its own scoped constraints;
every value carries ZR section/clause, amendment date 2024-12-05, and snapshot id+digest;
`res.export()` fails closed without provenance. Tests: `test_as1_*`, `test_as2_*`.

**S2 typed min/max separation** — PASS. Pitched emits TWO separate typed constraints
(`max_perimeter_wall_height=25.0`, `max_building_height=35.0`); flat emits `max_building_height`
only (no base/setback invented); units explicit (`feet`). DSL schema UNCHANGED (no additive
extension needed). Tests: `test_as1_pitched_confident_wall_and_ridge_separate`,
`test_as1_flat_*`, `test_as1_r4b_*`.

**S3 fail-closed gaps** — PASS. `building_type` unavailable → PRR, no value; districts outside the
enumerations → not_applicable; sloping-plane setback → documented_limitation (never a number).
Tests: `test_nc4_*`, `test_nc1_*`, `test_nc8_pitched_setback_is_documented_limitation_not_numeric`.

**S4 negative controls** — PASS. Cross-variant isolation (pitched rule not_applicable to
R5A/R4B/R1/R2/R5/R5B/R5D/R3; R4B rule scoped to R4B only); cross-SECTION isolation (R4 flat 35 never
becomes a pitched constraint and vice versa; R4B's 25 never merges with R3-2/R4's 35); effective-date
discipline (before 2024-12-05 → not_applicable); mutation-style value binding (25 vs 35 vs 25
distinct). Tests: `test_nc1_*`, `test_nc2_*`, `test_as3_*`, `test_nc8_*`.

**S5 draft posture and language** — PASS. Every rule `needs_review`; `qualified_human_approval:
pending`; family coverage conditional, never verified; a grep-style test asserts no
buildable-envelope / feasible / massing / compliance language in the new rulesets. Tests:
`test_as5_*`.

**S6 regression and determinism** — PASS locally. Full `tests/rules` suite **458 passed**;
byte-identical export determinism proven; engine untouched; `modularity_check.py --check` EXIT 0;
`sync_zr_snapshots.py --check` EXIT 0; ruff clean on the new test file. CI `api` job is the
executable authority on the pushed head.

## Self-check output (real)

```
$ python -m pytest tests/rules/test_r3_r4_height.py -q
90 passed in 3.15s

$ python -m pytest tests/rules -q
458 passed in 9.17s

$ python tools/modularity_check.py --check    ; echo EXIT=$?
EXIT=0   (only pre-existing warnings in unrelated files; none in the new files)

$ python services/api/scripts/sync_zr_snapshots.py --check   ; echo EXIT=$?
OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (10 file(s)).
EXIT=0

$ python -m ruff check services/api/tests/rules/test_r3_r4_height.py
All checks passed!
```

Note on the 3.11-vs-3.12 caveat (M2-T015): local pytest COLLECTED and passed cleanly in this
sandbox (no PEP 695 collection failure in the rules suite), so local evidence stands; CI remains
the authority.

## Disclosures / assumptions / limitations

1. **`raw_html_verified = false`** on all three new snapshots. The verbatim excerpts were captured
   by direct `curl` of the official portal on 2026-09-13 and tag-stripped, but NOT re-verified
   byte-for-byte against raw HTML, and nothing is G6-approved. `extraction_status = extracted_draft`.
2. **Invented input axis, disclosed.** `building_type` values `attached`/`other` are the engine's
   representation of §23-422's own NEGATIVE definition ("residences not subject to the provisions of
   Section 23-421"); they are NOT source-named building types. This is a modeling axis for
   fail-closed section selection ONLY — the numeric law (35 ft) is fully sourced, and because
   building_type has no canonical field the rules fail closed to PRR in practice. Flagged for
   reviewer/G6 attention. (The source-named pitched forms detached/semi_detached/zero_lot_line come
   verbatim from §23-421.)
3. **Scope note — canonical snapshot path outside literal `allowed_paths`.** The established
   `sync_zr_snapshots` mechanism (and its CI guard `test_zr_snapshot_bundle`) require every snapshot
   to exist in the CANONICAL source `docs/research/zr-snapshots/v1/` and be byte-identical to the
   runtime bundle `services/api/app/_zr_snapshots/v1/`. The packet `allowed_paths` lists only the
   bundle path; `docs/research/zr-snapshots` is NOT in `allowed_paths` but is also NOT in
   `forbidden_paths`. Writing snapshots to the bundle alone would FAIL the bundle guard (orphan).
   I therefore wrote the three canonical files and synced the bundle, so the guard passes. This is
   the only write outside the literal allowed list; disclosed for the orchestrator's confirmation.
4. **Family name.** New family `residential_height_setback_r3_r4` (distinct from the R5 pilot's
   `residential_height_setback`) so the R5 family-membership test stays green (S6). The pitched rule
   spans both R3 and R4 districts (one source provision), so a single R3/R4 family is the natural fit.
5. **Not modeled (typed gaps, by design):** sloping-plane setback geometry, qualifying-site/large-site
   increases, historic/special/overlay modifications, base-plane determination, and any future
   base-height/setback split. These are A2 territory (D-045-R008) or Section-20 legal context (G6).
6. **B-023 untouched.** R1/R2 remain blocked; no R1/R2 rule or snapshot was created. M4-T012 must not
   resume while these scopes were in flight (D-046-R002) — this producer only wrote R3/R4 artifacts.

## Scope-compliance confirmation

- No edits to engine/evaluator (`services/api/app/rules/engine*`, `evaluator*`), `api/**`,
  `scenario/**`, `connectors/**`, `apps/web/**`, `packages/**`, `tools/**`, `.github/**`,
  `render.yaml`, `requirements*.txt`, `pyproject.toml`, `project-control/directives|tasks|state`,
  or `docs/MVP_ARCHITECT_REVIEW_QA.md`. No DSL schema change (S2). `git status` shows exactly the 10
  new files listed above (3 rulesets + 3 canonical snapshots + 3 bundle snapshots + 1 test) — no
  forbidden path modified. Work left UNCOMMITTED in the worktree per instructions.

---

## Rework round 1 — surgical provenance correction (G3 supplemental ruling)

**Trigger:** G3 was revised from PASS to FAIL on newly surfaced evidence
(`project-control/reports/M4-T014-G3-supplemental-ruling.md`, orchestrator-preserved
verbatim from the reviewer). A peer-verified tooling hazard, independently grounded by
the reviewer in `docs/ARCHITECT_REVIEW_QUESTIONS.md` lines 48-51 (owner-verified
2026-09-13), established that the zr.planning.nyc.gov HTML render LOSES §23-421
paragraph (g) in text extraction on both official mirrors across four attempts. My
`zr-23-421-r3-r4` snapshot's `capture_method` is exactly that HTML-curl channel, so it
provably could not have read paragraph (g) — yet notes[1]/notes[2] asserted (g) content
(the 5 ft reference-plane provision, the R1/R2-no-suffix scope, the "(a) through (g)"
lettering, the apex-point/≤80° geometry) without naming a source that could actually see
it, and `M4-T014-source-capture.md` lines 53-55 presented (g) text INSIDE quotation
marks as though it were an in-task §23-421 quote. The true basis was always my prior-task
agent memory (analogous to the torn-down `zr-r1-r2-height-setback-source-facts.md`,
preserved in blocker B-023) — a legitimate basis, but it had to be NAMED, and the
pseudo-verbatim quoting had to go (permanent principles 2 and 3: provenance and no
guessed source meanings).

**Correction applied (Option (b) of the ruling — keep the information, fix its
provenance; NO rule-value change):**

1. `docs/research/zr-snapshots/v1/zr-23-421-r3-r4.snapshot.json` (canonical) — rewrote
   notes[1] and notes[2] to (i) state explicitly that this HTML capture channel could not
   render §23-421 paragraphs (a)-(g) and that the excerpt deliberately stops before them;
   (ii) attribute every (g)-content statement by name to the preserved rules-engineer
   agent memory (`.claude/agent-memory/rules-engineer/zr-r1-r2-height-setback-source-facts.md`,
   preserved in blocker B-023) and the owner-verified record
   (`docs/ARCHITECT_REVIEW_QUESTIONS.md`, section A1/A3) — never as content of this
   capture; (iii) state the owner-verified (g) trigger conditions accurately (zoning lot
   area ≥9,500 sq ft AND width ≥100 ft, OR slope ≥5% measured street-wall-line to
   rear-wall-line — either condition sufficing, per the exact owner-verified wording in
   `docs/ARCHITECT_REVIEW_QUESTIONS.md`) and marked owner-verified-elsewhere, not
   captured here. `verbatim_excerpt` and `content_digest_sha256` were NOT touched;
   recomputed `sha256(verbatim_excerpt)` still equals the stored digest
   `68e4d147a351188ce0df06d8609b1c3766c76776e0a87482e04ac2cc9459e046` (verified below).
   `services/api/app/_zr_snapshots/v1/zr-23-421-r3-r4.snapshot.json` (bundle) re-synced
   byte-identical via `sync_zr_snapshots.py`.
2. `project-control/reports/M4-T014-source-capture.md` — removed the quotation marks
   around the (g) passage (former lines 53-55) and reframed it as a provenance-qualified
   description citing the same two named sources; extended the adjacent sloping-plane/A2-gap
   bullet with the same disclosure for internal consistency (it carried the same
   unsourced "apex-point/≤80°"/"(a) through (g)" assertions); added a completeness note
   that ZR §23-421 full-text (print/PDF) proof is owed before any rule citing this
   snapshot advances toward G6 (carried forward from the M4-T012 packet, per owner
   directive).
3. This addendum.

**Note on the trigger-condition phrasing:** the coordinator's forwarding message
paraphrased the owner-verified conditions as "≥9,500 sq ft AND (≥100 ft width OR ≥5%
slope)". Reading `docs/ARCHITECT_REVIEW_QUESTIONS.md` directly (lines ~48-56), the
owner-verified text is "(1) zoning-lot area ≥9,500 sq ft AND width ≥100 ft; or (2) slope
≥5% ... (either suffices)" — i.e. (area AND width) OR (slope), not area AND (width OR
slope). I used the source document's exact grouping (consistent with the B-023 blocker's
independent phrasing: "lot area of at least 9,500 square feet and lot width of at least
100 feet; or ... a slope ... of at least five percent"), disclosed here in case the
paraphrase reflected information I do not have access to.

**Self-check (real output, rework round):**

```
$ python -c "recompute sha256(verbatim_excerpt) vs stored digest"
recomputed: 68e4d147a351188ce0df06d8609b1c3766c76776e0a87482e04ac2cc9459e046
stored    : 68e4d147a351188ce0df06d8609b1c3766c76776e0a87482e04ac2cc9459e046
MATCH

$ python services/api/scripts/sync_zr_snapshots.py && python services/api/scripts/sync_zr_snapshots.py --check
synced 10 files (incl. zr-23-421-r3-r4.snapshot.json)
OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (10 file(s)).
EXIT=0

$ python -m pytest services/api/tests/rules -q
458 passed in 7.31s
```

No test in `services/api/tests/rules/test_r3_r4_height.py` (or the rest of the suite)
asserted the old note wording (grep for "apex-point", "paragraphs (a)", "reference
plane", "large or sloped lots" across `services/api/tests` returned no matches), so no
test expectation required a change. Only the two files named above were edited; no
rule/parameter value, applicability, schema, engine, or test file changed. Work remains
UNCOMMITTED in the worktree; no git write beyond the read-only `git fetch`/`git show`
used to retrieve the ruling and `docs/ARCHITECT_REVIEW_QUESTIONS.md` from
`origin/candidate/D-024-mrl-option-b` (both explicitly authorized, read-only, no working-tree effect).
