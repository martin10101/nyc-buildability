# M5-T107 — G1 DELTA re-review, rework round 2 (data-contract-verifier "dc-t107", read-only)

> Transmission history: pinned at bf504772 (delta = 2c52ac6d, identity a367f548), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: ADV-1 closed (height_unit_basis and height_reference threaded verbatim from the connector), the
> extended escaping is meaning-preserving, the huge-int refusal typed, the round-1 datum facts unchanged.

---

M5-T107 G1 DELTA re-review (data-contract-verifier, READ-ONLY) - part 1/2

PIN: HEAD bf504772. Delta = 2c52ac6d (ancestor of HEAD); `git diff 2c52ac6d..HEAD` on all 6 source/test files is EMPTY -> HEAD == the re-frozen delta content. (a367f548 is the producer-worktree harvest id, not a local object; the re-frozen head bf504772 carries byte-identical source.) Connector production file building_footprints_arcgis.py is UNCHANGED in round 2, so my round-1 G1 PASS stands. Official facts re-confirmed live 2026-09-25 (City dictionary + FGDC) still hold.

DELTA VERIFICATION

1. ADV-1 CLOSED - faithful. New HEIGHT_PROVENANCE block (scene_assembler.py:140-149) imports HEIGHT_UNIT_BASIS + HEIGHT_REFERENCE DIRECTLY from the connector (one source of truth) and threads them as context_buildings.height_provenance (:494). At HEAD the two constants read: HEIGHT_UNIT_BASIS = "INFERENCE (research RQ-1), not a published unit: neither the City dictionary nor the service's FGDC metadata tags a unit on HEIGHT_ROOF or GROUND_ELEVATION. Feet rests on the US-foot EPSG:2263 source CRS..."; HEIGHT_REFERENCE = "HEIGHT_ROOF is the height of the roof above the ground elevation, not height above sea level (City dictionary); zero or NULL means the information was not available." Both match my live re-fetch (no per-field unit tag; dictionary above-ground wording). test_as1_context_height_provenance_is_threaded_from_the_connector pins equality + the "INFERENCE" / "not height above sea level" substrings. MATCH.

2. Escaping extended - source faithfully represented, not altered in meaning. _escape_untrusted_mapping now escapes string KEYS and values (numeric/null pass through); applied to attributes_escaped, each gap incl. gaps[].raw (:445), and _escape_untrusted mapped over drift_signals (:506) and geometry_findings (:432). The escape = strip control chars + U+2028/29, html.escape(quote=True), 512-bound: reversible entity encoding, meaning-preserving; the pinned official attribute keys and the fixed gap field/code keys are ASCII so they escape to themselves (server literals unchanged). Tests prove a hostile key `<img onerror>` is encoded and the raw key is absent, gaps[].raw "'<b>boom</b>'" -> entities with field "HEIGHT_ROOF" unchanged, geometry_findings / drift_signals encoded, OBJECTID 123 passes through. No source VALUE is altered in meaning - only non-data control chars stripped and markup entity-encoded. MATCH.

-> part 2/2

---

M5-T107 G1 DELTA re-review - part 2/2 (items 3-4, findings, verdict)

3. Coordinates - huge int refused typed. _coerce_coordinate now wraps the int/float float() in try/except OverflowError -> None -> typed SceneAssemblyError(reason=unparseable_coordinate), so a JSON int beyond float range (10**400) becomes a 422, never an untyped 500; a huge numeric STRING already resolves to inf and is refused by the isfinite check. String-coordinate parsing is otherwise unchanged. A mutation test restores the pre-fix unguarded body and asserts the untyped OverflowError leaks, proving the guard is load-bearing. MATCH - no silent coercion, mirrors the connector's _finite() OverflowError guard.

4. Round-1 items UNCHANGED. The delta adds HEIGHT_PROVENANCE AFTER the datum block; GROUND_DATUM_DECISION (the datum choice, both official definitions, navd88_attribution, unverified_ground_policy) and _ground_status / _context_building base_z & roof_z derivations are untouched. So the datum decision, NAVD88-only-to-dictionary attribution, zero/unverified-ground disclosure, and HEIGHT_ROOF = above-ground (roof_z_ft = (ground - site_ground) + height_roof) all stand from round 1. The delta ADDITIVELY adds a ground_status_is_authoritative disclosure noting base_z_grounded is true even for an unverified zero ground, so ground_status (grounded / ground_zero_unverified / ground_elevation_missing / site_ground_not_supplied) is the authoritative field - accurate against the code and it strengthens the zero-ground honesty.

FINDINGS
- No BLOCKING findings. My prior ADV-1 is RESOLVED.
- No new overclaim: the D-083 claim-word screen still runs over the new strings; the new provenance/disclosure text draws no legal conclusion and asserts nothing beyond the sources (RQ-1/RQ-2 residuals stay labelled).
- ADV-2 (round 1, non-material): the connector docstring's FGDC-HEIGHT_ROOF gloss is in the untouched connector file; still out of this packet's scope, DB-073(h).

Provenance: HEIGHT_PROVENANCE strings trace verbatim to the connector constants (imported), which trace to the live City dictionary + FGDC (re-fetched 2026-09-25); all reviewed content is byte-stable at 2c52ac6d == HEAD bf504772.

M5-T107 G1 VERDICT: PASS

END-OF-REPORT
