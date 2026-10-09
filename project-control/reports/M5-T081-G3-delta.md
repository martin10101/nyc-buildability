# M5-T081 — G3 delta re-review after the rework (code-reviewer "cr-cad", read-only)

> Transmission history: requested by SendMessage after the G3 FAIL (F1 BLOCKING $INSUNITS) rework
> (0ffe581c, cherry-pick of wt-m5t081 778bf8ca); pinned at f2870507 with the three T081 blobs verified
> byte-identical; delivered as two SendMessage parts (1/2, 2/2) ending with END-OF-REPORT; no truncation.
> Joined verbatim by the orchestrator (transport wrapper tags removed only). The original joint
> T081/T085 G3 report (T081 FAIL) stays in M5-T081-G3.md unchanged.

---

M5-T081 G3 DELTA RE-REVIEW (part 1/2). PIN verified: `git rev-parse HEAD` = f2870507 (the pin). Rework 0ffe581c is an ancestor of the pin; blobs match exactly (dxf_writer 152f1f2e, test 2aa45291, report 9a4d06ef); disk == rework blobs, tree clean. Scope: exactly the 3 allowed paths; no added import lines (stdlib only).

(1) F1 BLOCKING — CLOSED. `INSUNITS_US_SURVEY_FEET = 21` emitted at the header (was `INSUNITS_FEET = 2`); the false "cannot distinguish survey from international feet" comment is replaced with the correct citation (code 21 = US Survey Feet, added in the AutoCAD 2017 DXF ref, quoting docs/research/dxf-format-reference-2026-09.md §0.2/3/7, [HDR2026]/[HDR2017]). Header now consistent with the ANNOTATION "US SURVEY FEET" text. `test_as2_header_declares_drawing_unit` now asserts the HARDCODED `(70, "21")` (was `(70, str(d.INSUNITS_FEET))`, tautological) — externally pinning the exact code, which closes my weak-test note. GOLDEN_SHA256 re-anchored dbef79e1->2d8988d6; the live 24-pass run (incl. test_as1_golden_digest) confirms it is self-consistent, and the producer mutant table shows 21->2 reddens the pin test. All four axes you named (value / comment+citation / hardcoded (70,"21") / golden) satisfied.

(2) New bounds — correct, typed, fail-closed, no regression:
- `MAX_FLOORS = 2_000`: `len(floor_heights)` read BEFORE the heights tuple is built -> `floor_cap_exceeded` in O(1), no allocation. Building-ring cap -> `ring_cap_exceeded`; `edge_count * n_floors > MAX_ENTITIES` -> `entity_cap_exceeded`. The face pre-check is conservative (total entities >= faces, so it never false-refuses a case `doc.validate()` would accept), and `DxfDocument.validate()` still enforces the true total cap. Empty-floors (`no_floors`) and inf/<=0-height (`invalid_floor_height`) guards are preserved after the additive pre-checks.
- `MAX_COORD_ABS = 1e8` at `_format_real` (the single numeric choke point) -> `coordinate_out_of_range`. NYC 2263 coords ~1e6, far inside; golden fixture unaffected.

---

M5-T081 G3 DELTA RE-REVIEW (part 2/2).

No-partial-output on the mid-serialization magnitude refusal — CONFIRMED: `_GroupCodeStream` accumulates into an in-memory `_lines` list and `serialize_document` returns `s.render()` only at the very end; a `_format_real` refusal propagates out BEFORE `render()` is reached, so the caller receives the exception and NO string. Same holds for a runaway elevation (floor-height sum > 1e8) — fails closed at the choke point.

Test hardening (G4/G5 cluster), all mutant-verified in the producer red/green table:
- honesty literals now asserted as HARDCODED strings + the constants pinned (`test_as4_annotation_carries_required_labels`);
- sanitizer forbidden-byte coverage `\x00`/`\x1b`/non-ASCII (`test_as3_sanitizer_rejects_forbidden_bytes`) — a CR/LF-only weakening now reddens;
- claim-word guard proven load-bearing via a monkeypatched annotation (`test_as4_claim_word_guard_is_load_bearing`) + the 11-word `CLAIM_CLASS_WORDS` tuple pinned;
- floor-cap and magnitude refusals covered. The single sanitizer choke point, determinism, and section/entity emit are byte-unchanged from the baseline I reviewed.

Scope / harness (verified live, cwd services/api):
- `python -m ruff check app/cad/dxf_writer.py tests/cad/test_dxf_writer.py` -> All checks passed!
- `python -m pytest tests/cad/test_dxf_writer.py -q` -> 24 passed.
- `python tools/modularity_check.py --check` -> failures 0, exit 0; dxf_writer/cad NOT in the warn/fail list (787 raw lines, comment-heavy; SLOC not flagged).

ADVISORY (non-blocking, one minor note): `MAX_COORD_ABS` also governs elevations/text-height through `_format_real`, so a pathological floor-height sum > 1e8 surfaces as `coordinate_out_of_range` rather than a height-specific code — still a typed, fail-closed refusal with no partial output; acceptable.

No BLOCKING findings. F1 closed; the added bounds are correct and regression-free.

M5-T081 G3 VERDICT (rework delta): PASS

END-OF-REPORT
