# M5-T081 — G5 security re-ruling after the rework (security-reviewer "sec-write", read-only)

> Transmission history: requested by SendMessage after the G3/G4 FAIL rework (0ffe581c, cherry-pick of
> wt-m5t081 778bf8ca); pinned at f2870507 with the dxf_writer.py (152f1f2e) and test (2aa45291) blobs
> verified byte-identical; delivered as two SendMessage parts (1/2, 2/2) ending with END-OF-REPORT; no
> truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only). The reviewer's
> first T081 G5 (PASS, joint with T085/T082) stays in M5-T081-G5.md unchanged.

---

M5-T081 G5 RE-RULING after rework (1/2). PIN VERIFIED: HEAD f2870507; dxf_writer.py blob 152f1f2e and test_dxf_writer.py blob 2aa45291 both byte-identical to the pin. Delta reviewed: git diff 4fd58a98..0ffe581c.

F2 (coordinate-magnitude bound) — CLOSED. MAX_COORD_ABS=1e8 is enforced in `_format_real` (L211-216), the single numeric choke point through which EVERY emitted coordinate flows (`s.real`→`_format_real` in header/polyline/face/line/text, including text height). It is ordered AFTER the `math.isfinite` check, so NaN/inf are refused first as `non_finite_coordinate` and `abs()` never sees a NaN; a finite over-bound value raises typed `coordinate_out_of_range`. It raises DURING serialization, but the accumulated `_GroupCodeStream` is a local discarded on raise (`render()` runs only on success) → no partial output. 1e8 >> NYC 2263 (~1e6), so no false refusal of real geometry. Mutation-guarded by test_as3_coordinate_magnitude_bound_refused.

F1 (pre-materialization amplification) — the dangerous path is CLOSED. `build_site_plan_document` (L683-701) now reads `n_floors=len(floor_heights)` and refuses `floor_cap_exceeded` BEFORE the heights tuple or any ring/face/line is built (10M floors → O(1) refuse, no allocation), and refuses `entity_cap_exceeded` when `edge_count*n_floors` would exceed MAX_ENTITIES before the faces list is built. The catastrophic multiplicative blowup (edges×floors) is gone; downstream materialization is bounded (faces ≤50k, lines ≤10k, rings ≤2003) and `doc.validate()` stays the authoritative total-count backstop. Guarded by test_as3_builder_refuses_over_cap_floor_count_before_allocating.

F1 RESIDUAL (LOW, ADVISORY — non-blocking). The `_normalize_ring(lot)` / `_normalize_ring(building)` calls (L682-683) still coerce the FULL raw input to a list (`pts = [(float,float) for p in raw]`, L567) BEFORE the edge_count / Ring.validate vertex cap. So the producer's "ring pre-check before any list is built" holds for the FLOOR path but not literally for the ring: a huge raw lot/building sequence is transiently materialized (~2× the caller's own input) before refusal. This is LINEAR and NON-amplifying (a JSON attacker supplies an already-materialized list; no small-input→huge-allocation) and unreachable (part 2), so it does not block. Full match to the claim: add `len(lot)`/`len(building)` raw pre-checks mirroring `len(floor_heights)`.

(continued 2/2)

---

M5-T081 G5 RE-RULING after rework (2/2).

SANITIZER + ALL OTHER SECURITY PROPERTIES — INTACT. The diff does not touch `_sanitize_value`, `_GroupCodeStream.pair`/`real`/`render`, `_validate_layer_name`, or `_write_text`'s emit-time `pair(1, text.text)`; no new `_lines.append`. The ONE string sanitizer (allowlist 0x20–0x7E; CR/LF/control/DEL/non-ASCII → typed `DxfSanitizationError`, no scrub-and-continue) remains the sole string path, and the numeric choke point is now STRENGTHENED (magnitude bound). Determinism (LF EOL, `.6f`, -0.0→0.0, no clock/random) and zero info-leak (fixed provenance constants) unchanged. New tests add real mutation guards: NUL/ESC/`é` rejection (test_as3_sanitizer_rejects_forbidden_bytes), honesty literals in serialized output, and the full pinned claim-word set.

NEW NaN/inf CHECK — SOUND. The pre-checks operate on ints only (`len(...)`, `edge_count*n_floors` big-int compare — no float, no overflow); floor VALUE finiteness is still enforced by the existing `math.isfinite(h)` loop, so a NaN floor height passes the count pre-check and is caught there. No NaN/inf reaches or defeats any new check.

NO DEPENDENCY / ROUTE / SCOPE CHANGE (claim 3) — CONFIRMED. Import section unchanged (`from __future__ import annotations`; `import math`; `collections.abc`; `dataclasses`) — no new dependency. Grep of services/api/app for any importer of `dxf_writer` / `render_site_plan_dxf` / `build_site_plan_document` finds ONLY the definitions inside dxf_writer.py itself — no route or service consumes the module, so no route/scope change and NO untrusted input reaches it at this HEAD (the F1 residual stays latent).

$INSUNITS 2→21 (`INSUNITS_US_SURVEY_FEET`) — a format-semantics correction (US survey vs international feet) for G1/G3 to confirm against the DXF reference; OUTSIDE G5 scope. Security impact nil: emits "21" through the sanitizer, deterministic, golden sha re-anchored.

CONCLUSION: F2 closed; F1 amplification closed with a LOW non-blocking linear residual in `_normalize_ring`; the sanitizer choke point and every other security property from the first review hold; no new NaN/inf, dependency, route, or scope path introduced.

M5-T081 G5 VERDICT (rework): PASS

END-OF-REPORT
