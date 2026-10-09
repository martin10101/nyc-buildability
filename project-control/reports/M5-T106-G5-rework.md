# M5-T106 — G5 DELTA re-review, required-corrections round 2 (security-reviewer "sec-t106", read-only)

> Transmission history: pinned at 8273c688 (delta = 42526c66, identity 074a9f7b), delivered as ONE SendMessage part ending
> with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only). Verdict
> PASS: MED-1 closed on both paths, LOW-1 closed, INFO closed; no new untyped path.

---

M5-T106 G5 DELTA RE-REVIEW (read-only, sec-t106) — round-2 corrections

PIN: HEAD 8273c688 (matches expected). Delta = `git show 42526c66` only (cherry-pick of wt-m5t106 f9cad218): module +51/-15, test +160/-0 (append-only — numstat confirms 0 test deletions; no existing test edited), producer report. Module blob at HEAD 68e062e5 == the delta result; test 6971be8a. proposal.py untouched; no new module import; still unwired (no importer under app). ruff clean; pytest tests/scenario/test_massing_model.py = 81 passed (was 75; +6 test_t106r2_*). Method: clean-diff read + re-run of the round-1 hostile probes at HEAD.

MED-1 (huge-int OverflowError) — CLOSED, both paths.
- Lot: _is_finite_number now try math.isfinite / except OverflowError -> False (:243-262). Probe: _is_finite_number(10**400)=False; lot 10**400 AND 10**309 -> TYPED non_finite (bounded); 1e300 float still -> coordinate_out_of_range (magnitude precedence preserved).
- Footprint: added `except OverflowError` on the B0 try/except (:834-843) -> TYPED non_finite; a 10**400 outline vertex AND a 10**400 floor height both -> TYPED non_finite. Root overflow stays in read-only proposal.py; typed at the in-scope boundary. No untyped escape either path.

LOW-1 (echo bounds) — CLOSED. B0 re-echo now _preview(exc) (:834): a 200,000-char footprint vertex -> 186-char message (was 200,144). No-candidate placement detail now _preview(detail) (:956-961): a 200,000-char detail -> 251-char message. All other caller-input echoes (lot/footprint vertex, source, height, count, shapely exc) remain bounded.

INFO (_preview never raises) — CLOSED. try repr / except Exception -> "<unrepresentable value>" (:224-231). Probe: _preview(hostile __repr__) and _preview(5000-deep nested) -> placeholder, no raise; a lot vertex that is a hostile-__repr__ object OR a deep-nested list now -> TYPED non_finite (was UNTYPED RuntimeError / RecursionError). BaseException intentionally not swallowed; not reachable via JSON.

G4-ADV1: GeometryTypeError (a second, genuine non-GEOS ShapelyError) -> wrapped geometry_engine_error (probe + test_t106r2_second_...).

NEW UNTYPED PATHS: none found. Regression cases (NaN/inf/bytes/200k-string/2e6 raw-range spike) still typed; valid build unchanged (both goldens byte-identical, test_t106_as6). Docstring now states the exact bounded set accurately.

M5-T106 G5 VERDICT: PASS

END-OF-REPORT
