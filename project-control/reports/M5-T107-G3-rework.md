# M5-T107 — G3 DELTA re-review, rework round 2 (code-reviewer "cr-t107", read-only)

> Transmission history: pinned at bf504772 (delta = 2c52ac6d, identity a367f548), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: G5 F-1..F-4 and A1/A2/A4/A5 plus the G4/G1 advisories correctly and testably closed; no
> regression for valid input. The reviewer's identity question: a367f548 is the path-scoped content-manifest digest, not
> a git object; it is re-derived by project_control._task_git_identity at accept.

---

M5-T107 G3 DELTA re-review (READ-ONLY) — PART 1 of 2. HEAD bf504772. Delta = 2c52ac6d, confirmed an ancestor of HEAD; the only commit between them (bf504772) is a harvest/re-freeze seam; scene_assembler.py + scene_api.py are BYTE-IDENTICAL at 2c52ac6d and HEAD (diff empty). Scope: exactly 6 allowed-path files; connector production file, massing_model.py, and app/main.py untouched.

EVIDENCE at HEAD (cwd services/api): ruff = All checks passed; pytest tests/scenario tests/connectors = 1842 passed (+19 vs round 1's 1823); modularity_check --check exit 0 (scene_assembler 594 lines, scene_api 374 — neither flagged).

Each item verified against my A1/A2/A4/A5 and the G5 failures:

- G5 F-1 (huge int) — _coerce_coordinate wraps float() in try/except OverflowError (scene_assembler.py:240-249), so 10**400 → None → typed unparseable_coordinate 422, never a 500. Correct: only the int/float branch overflows; a huge STRING already resolves to inf and is caught by math.isfinite. Tests: test_as1_huge_int_coordinate_is_refused_typed_never_a_500 (lot ring AND a proposal outline vertex), test_422_huge_int_coordinate_is_typed_not_a_500 (route), and an in-process mutation reverting to the unguarded body that reddens with the untyped OverflowError. Strong.

- G5 F-2 / G3 A1 (escape keys+diagnostics) — _escape_attributes replaced by _escape_untrusted_mapping which escapes BOTH keys and values (:383-390); gaps[] via the same mapping escape (:448); geometry_findings (:435) and drift_signals (:506) each escaped element-wise. The module docstring and the untrusted_source_text_escaped disclosure are corrected to name exactly these fields — now accurate. Tests: test_as3_hostile_attribute_key_gap_raw_and_drift_name_are_escaped (hostile KEY, gap raw, drift name, findings; asserts no raw markup anywhere in the dumped scene) + an identity-mutation of _escape_untrusted that reddens. My A1 fully closed.

- G5 F-3 / G3 A2 (limiter memory bound) — SCENE_RATE_LIMIT_MAX_KEYS=4096 (:98-102); _evict_empty_keys sweeps expired keys; _rate_limit_allows pops a caller whose window emptied, and a NEW caller at the ceiling triggers a sweep then fail-closes if still full (:142-172). I traced the state machine: the dict never exceeds MAX_KEYS; existing active callers are unaffected. Thread-safe (runs entirely on the event loop before any await). Tests: key-ceiling test with clock/window/ceiling monkeypatched + a reddening large-ceiling mutation, and a single-key eviction test. My A2 closed. (A3 shared-limiter module stays a PKT-H note.)

Part 2 (F-4, A4, A5, G4/G1 advisories, no-regression, matrix, massing interplay, verdict) next.

---

M5-T107 G3 DELTA — PART 2 of 2.

- G5 F-4 (honest cancel docstrings) — module docstring, SCENE_MAX_SECONDS comment, and the _deadline_exceeded message now state the truth: the AWAIT is cancelled and a 504 returned, while the worker thread cannot be force-killed and runs to completion, independently bounded by the connector's own wall-clock deadline + interactive single-attempt + byte/vertex caps. Accurate; no behaviour change (message text only; the (504, deadline_exceeded) pair is unchanged).
- G3 A4 (non-dict context) — scene_api.py:322-331: absent/null context stays honest not_requested (200); a non-dict is a typed 422 field=context. Test test_422_non_dict_context_is_refused_typed covers string/list/int + the None→200 case. Closed.
- G3 A5 (ground_status authority) — new disclosure ground_status_is_authoritative (:190-199) tells consumers not to read base_z_grounded alone; test pins it plus the zero-unverified pairing. Closed.
- G4 adv 1/2/4 — the not-wired AST test gains a traversal FLOOR (len(seen)>1 and a known main-reachable module present) so it can't pass vacuously; a route caplog test proves a hostile caller string reaches NO log line (only field=lot_ring[0] + cid, both server-derived); two tests exercise the (500, internal_error) pair (assemble-stage RuntimeError and a NaN scene through the serialization guard), asserting no secret text leaks. All genuine.
- G1 ADV-1 — HEIGHT_PROVENANCE threads the connector's height_unit_basis + height_reference into the layer (:140-148, :494). Verified HEIGHT_UNIT (connector:153) == VERTICAL_UNIT (massing:124) == us_survey_foot, so height_unit is consistent; the basis discloses the unit is an inference (RQ-1). Additive.

NO REGRESSION for valid input: normal int/float coords unchanged; for a CLEAN official response gaps/drift are empty and official keys carry no special chars, so all new escaping is a no-op (the strict golden test_as1_golden_context_building_shape_is_pinned still passes) — escaping only alters output when diagnostics are populated, which by definition is non-clean upstream. MATRIX unchanged and still the single source of truth; every new emitted pair ((500,internal_error),(422,validation_error)) is in it; test_every_emitted_pair_is_in_the_matrix green. MASSING interplay at HEAD (M5-T106 r2 in): the assembler codes only against the massing public API and the full suite builds real massing models green; the assembler's overflow guard fires before the massing coordinate_out_of_range check — both typed, consistent.

Residuals (negligible, non-blocking): key escaping strips control chars, so two pathological keys differing only by a control char could collide (last-wins) — realistic official keys are unaffected and this is strictly better than emitting raw keys. One flag for you: the stated frozen identity a367f548 does NOT resolve as an object in this worktree; I reviewed 2c52ac6d (in HEAD's ancestry, scene files byte-identical to HEAD) — please confirm the frozen identity maps to this exact content before accept.

All of F-1..F-4 and A1/A2/A4/A5 (and the G4/G1 advisories) are correctly and testably closed.

M5-T107 G3 VERDICT: PASS

END-OF-REPORT
