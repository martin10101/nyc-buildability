# M4-T012 Producer Report - R1/R2-series Height/Setback Draft Rule Families (D-049 definitive scope)

Producer: rules-engineer (claude-sonnet-5), worktree `wt-m4t012-r2`, base commit
`dbd07817758de97ab6150b43f27e47e22aa9ad32` on `candidate/D-024-mrl-option-b`.

This is a producer evidence submission. It does not declare the task complete or
compliant - an independent gate judges that. Full source-capture detail (URLs,
timestamps, hashes, the 9,500-present check, and the required discrepancy
disclosure) is in `project-control/reports/M4-T012-source-capture.md`; this file
summarizes the implementation and self-check evidence.

## Objective addressed

D-049 (owner decision, 2026-09-13) definitive rescope of D-045-R001/D-048:
- **R001** R1-1, R1-2, R1-2A, R2A, R2X share the ZR 23-421 25/35 pitched envelope via
  ZR 11-25 suffix inheritance, carrying OWNER-DECISION provenance, never an express
  per-variant citation. Bare R1/R2 encoded from the express 23-421 enumeration.
- **R002** R2X's 23-21 FAR row is a floor-area-only exception; does not modify height.
- **R003** 23-421(g) as an explicit conditional (no-letter-suffix R1-1/R1-2/R2;
  trigger area>=9,500 & width>=100, OR slope>=5%); missing input -> explicit
  professional-review flag, never a silent apply/omit.
- **R004** Site-specific modifiers (23-424, 23-425, 23-426(a), 23-443(b), 119-212,
  113-523) surfaced as conditions/flags/typed gaps, never silent; pitched envelope
  never rendered as a requirement.
- **R005** Every derived output carries owner-decision provenance + DRAFT/needs-review.

## STEP 2 binding capture-completeness proof - result

**PASS.** Full detail in `M4-T012-source-capture.md`. Summary: section 23-421 was captured
via the official portal's print/PDF render (`entityprint/pdf/node/18075`, 8 pages,
sha256 `b5777618fe2136b26f63b281db0715e2de2174f6962f0a28c46bc4957c1d706d`), read
page-by-page. Paragraph (g) renders in full including the figure **9,500** (page
7-8): "In R1 and R2 Districts without a letter suffix ... lot area of at least 9,500
square feet and lot width of at least 100 feet ... or ... slope ... at least five
percent ... the reference plane ... may be located up to five feet above the base
plane." This matches `docs/ARCHITECT_REVIEW_QUESTIONS.md`'s owner-verified verbatim
word-for-word.

**Discrepancy disclosed:** a direct HTTPS GET of the human-readable HTML page for the
same section, inspected at the RAW BYTE level (not via a text-extraction tool), ALSO
contains paragraph (g) in full, contradicting the packet's stated premise that "the
official zr site's HTML render provably LOSES paragraph (g)". I disclose this rather
than silently reconciling it; per the task's BINDING instruction I nonetheless used
the PDF channel as the citation channel of record for `zr-23-421-g`, and recorded the
raw-HTML byte finding as an additional corroborating cross-check in that snapshot's
`source.capture_channel_note`. My best (unconfirmed) explanation: the prior sessions'
"HTML extraction" step likely used a readability/text-conversion tool that truncated
after a large embedded base64 PNG data URI immediately preceding paragraph (g) in the
raw markup, not a limitation of the raw HTTP response itself.

## Files created

**Canonical ZR snapshots** (`docs/research/zr-snapshots/v1/` - outside the packet's
listed `allowed_paths`, but not in `forbidden_paths`; writing here is REQUIRED by the
established `sync_zr_snapshots.py` mechanism the packet names as the only entry point
for new snapshots, per the precedent already disclosed and accepted on M4-T014. I
flag this scope note explicitly per the packet's disclosure requirement):
- `zr-11-25.snapshot.json` - digest `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b`
- `zr-23-421-r1-r2.snapshot.json` - digest `1bce881805d9ee4d79253432ad86128b7203f81f2054ff25e1ba8dfb1dad1e8b`
- `zr-23-421-g.snapshot.json` - digest `52dd8aab6e2a7e53f65c953157b70e899f7be94438d0c3456731ff430c626536`
- `zr-23-424-r1-r2.snapshot.json` - digest `336ba2cbbe73689e8b24caf3b3d8bb396eaee5d3b8a89b018328213801c798cc`

**Runtime bundle** (`services/api/app/_zr_snapshots/v1/` - in `allowed_paths`):
the same four files, produced via `python services/api/scripts/sync_zr_snapshots.py`
(write mode), byte-identical to canonical, verified via `--check` (exit 0) and via
`test_zr_snapshot_bundle.py` (6/6 passed).

**Rulesets** (`services/api/app/rules/rulesets/` - in `allowed_paths`), family
`residential_height_setback_r1_r2`, all `status: needs_review`:
- `r1_r2_bare_pitched_height.rule.json` (`r1-r2-bare-pitched-height`) - bare
  R1/R2, express citation, 25/35 ft envelope.
- `r1_r2_suffix_variants_pitched_height.rule.json`
  (`r1-r2-suffix-variants-pitched-height`) - R1-1, R1-2, R1-2A, R2A, R2X, ZR 11-25
  owner-decision citation, same 25/35 ft envelope, R2X FAR-parity note (R002).
- `r1_r2_reference_plane_23421g.rule.json` (`r1-r2-reference-plane-23421g`) -
  R1-1, R1-2, R2, explicit conditional per 23-421(g), all three geometry inputs
  (area/width/slope) required (fail-closed by design, disclosed as conservative).
- `r1_r2_qrs_height.rule.json` (`r1-r2-qrs-height`) - R1-1, R1-2, R1-2A, R2, R2A,
  R2X on a qualifying residential site, 23-424 alternative (35/35 ft), competes
  with the base envelope rules for `max_building_height` (same-family conflict,
  proven by test - never a silent precedence pick).

No engine/schema files were touched (`services/api/app/rules/schemas` untouched - no
new constraint shape was needed; the existing DSL vocabulary covers every constraint
in this wave). `services/api/app/rules/engine*` / `evaluator*` were not touched.

**Tests** (`services/api/tests/rules/` - in `allowed_paths`):
`test_r1_r2_height_setback.py` (new, 100 tests) covering AS-1 through AS-6 and NC-1
through NC-8 per the packet's acceptance scenarios (S1-S6): per-variant extraction
with provenance, typed min/max separation, fail-closed gaps, negative controls
(wrong-district, letter-suffix exclusion from (g), cross-variant isolation, effective
date, mutation-style trigger-boundary checks), draft-posture/language guard, and
regression/determinism/modularity.

**Report files** (`project-control/reports/` - the two allowed report paths):
`M4-T012-source-capture.md`, this file.

## Discretionary design decisions disclosed

1. **New `zr-23-421-r1-r2` snapshot instead of reusing the accepted `zr-23-421-r3-r4`.**
   Both capture overlapping text of the same official section (enumeration + wall/ridge
   sentence). I chose an independent, purpose-named capture for R1/R2 rather than
   citing the R3/R4-named snapshot, for reviewer clarity; both are byte-verified
   against the print/PDF artifact and neither modifies the other.
2. **Paragraph (g) captured as its own snapshot (`zr-23-421-g`)**, separate from the
   enumeration/envelope snapshot, so the (g)-conditional rule's citation is
   unambiguous and independently hash-verified, and so the SNAPSHOT HONESTY RULE
   (never assert unread content) is easy to audit per-snapshot.
3. **All three geometry inputs on the (g) rule are REQUIRED**, even though the source
   states an OR (either path suffices). This is intentionally conservative: it never
   produces a wrong value, but a lot known to satisfy the area+width path with an
   unmeasured slope still fails closed to `professional_review_required` rather than
   emitting the value from the known-satisfied path. Relaxing this would require
   either a second competing rule (risking a spurious same-family conflict against
   this rule, since both would share the output name) or an engine change (forbidden
   path in this task). Disclosed in the ruleset's own `limitations` array and in the
   test suite's NC-5/NC-8 sections, not silently accepted.
4. **section 119-212 and section 113-523 are folded into the existing `special_district_present`
   flag** (both are special-purpose-district provisions) rather than given their own
   input flags, to avoid inventing untested new flags beyond what D-049-R004 requires
   as a minimum ("surface as conditions/flags/typed gaps" - the existing flag already
   achieves this, with the specific sections named in the flag's description text).
5. **`docs/research/zr-snapshots/v1/` and `services/api/scripts/sync_zr_snapshots.py`
   were written to / executed**, respectively, though neither path is explicitly
   listed in this task's `allowed_paths`. Neither is in `forbidden_paths` either, and
   both are structurally REQUIRED by the established, already-accepted (M4-T006,
   M4-T014) snapshot mechanism the packet itself names as the only entry point for new
   snapshots. I ran (not edited) the sync script; I did not modify it.

## Self-checks (verbatim commands + exit codes)

```
$ cd services/api && PYTHONPATH="." python -m pytest tests/rules -q
558 passed in 13.37s
Exit: 0
```

```
$ python -m pytest services/api/tests/rules/test_r1_r2_height_setback.py -q   [run from services/api with PYTHONPATH=.]
100 passed in 3.11s
Exit: 0
```

**Environment note (M2-T015 pattern, disclosed honestly):** running
`python -m pytest services/api/tests/rules` exactly as documented, from the repo
root, with no `PYTHONPATH` set, fails collection with `ModuleNotFoundError: No module
named 'app'` in this sandbox - this is a PRE-EXISTING environment characteristic (it
reproduces identically on every unmodified test file in the directory, e.g.
`test_rules_engine.py`, not something introduced by this change) because the API
package is not `pip install`-ed in this sandbox the way CI installs it
(`pip install --no-deps ./services/api`). Setting `PYTHONPATH=services/api` (repo
root) or running from inside `services/api` resolves it identically; both are shown
above. All 558 rules tests (my new 100 plus the 458 pre-existing) pass. CI's `api`
job (which installs the package) is the executable authority per the repo's
documented pattern; this sandbox run is `PYTHONPATH`-equivalent evidence.

```
$ python tools/modularity_check.py --check
selected 399 files; failures 0; warnings 16 (all 16 warnings are PRE-EXISTING, in
files this task did not touch: apps/web/src/lib/surveyReview/types.ts,
services/api/app/api/v1/scenario_analysis.py,
services/api/app/connectors/mappluto_geometry_arcgis.py,
services/api/app/scenario/breakeven.py, and 12 tools/agent_supervisor/* files)
Exit: 0
```

```
$ python services/api/scripts/sync_zr_snapshots.py --check
OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (14 file(s)).
Exit: 0
```

## Acceptance-scenario mapping (S1-S6, packet)

- **S1** per_variant_extraction_with_provenance - proven by `test_as1_*` (every
  variant gets its own scoped constraint set; every value cites a snapshot id +
  digest; the authoritative enumeration is recorded in the source-capture report).
- **S2** typed_minmax_separation - proven by `test_as1_*` outputs (perimeter-wall
  height and ridge/building height are separate typed outputs; no schema change was
  needed).
- **S3** fail_closed_gaps - proven by `test_nc1_*`, `test_nc4_*`, `test_nc5_*`
  (unsupported districts -> not_applicable; missing inputs -> professional_review_required,
  never a guessed value).
- **S4** negative_controls - proven by `test_nc1_*` (wrong district),
  `test_nc2_*` (letter-suffix exclusion from (g) - cross-variant isolation), `test_as3_*`
  (effective-date discipline), `test_nc8_trigger_boundary_values` (mutation-style
  binding at the exact 9,500/100/5 boundaries).
- **S5** draft_posture_and_language - proven by `test_as5_*` (every rule
  `needs_review`; banned-phrase grep finds nothing after the `massing` -> `building
  form` correction I made after my own test caught it; D-045-R009 preserved).
- **S6** regression_and_determinism - proven by the full 558-test rules-suite run,
  `test_as4_determinism_byte_identical`, and the modularity check; CI's `api` job on
  the pushed head is the authority I could not run from this sandbox (no `git push`
  permission here - the orchestrator integrates).

## Uncertainty / limitations I am disclosing (not resolving myself)

- The professional-confirmation ask for section 11-25's application to this family REMAINS
  OPEN at `docs/ARCHITECT_REVIEW_QUESTIONS.md` section A1; nothing here closes it -
  every suffix-inherited value carries owner-decision provenance, not a qualified
  sign-off.
- Whether "without a letter suffix" in section 23-421(g) also covers a hypothetical bare "R1"
  district is NOT decided by me; I followed the owner-verified enumeration exactly
  (R1-1, R1-2, R2 eligible) and did not extend it to bare R1, since neither
  `docs/ARCHITECT_REVIEW_QUESTIONS.md` nor the D-049 packet names bare R1 as eligible.
- The full sloping-plane setback geometry (23-421 paragraphs a-f) remains a typed A2
  gap (D-045-R008) on every envelope rule, never computed.
- I did not verify the discrepancy's root cause (which prior tool/extraction step
  produced the "HTML loses (g)" finding); I disclose the contradiction and my best
  unconfirmed explanation rather than asserting a cause.

## Status

**COMPLETE** (producer-side). I am not declaring this compliant or accepted - that is
an independent gate's determination (G0/G2/G3/G4/G5 per the packet's
`required_gates`).
