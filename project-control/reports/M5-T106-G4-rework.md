# M5-T106 — G4 DELTA re-review, required-corrections round 2 (qa-engineer "qa-t106", read-only)

> Transmission history: pinned at 8273c688 (delta = 42526c66, identity 074a9f7b), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: the producer's 6 new mutants and 4 own mutants all redden; both round-1 advisories closed.
> Advisories A1 (994/1000 lines) and A2 (the B0 OverflowError field label) are routed at the accept seam.

---

M5-T106 G4 DELTA re-review (qa-engineer, READ-ONLY) — part 1/2

PIN: HEAD 8273c688 at start. Round-2 material commit 42526c66 (frozen identity 074a9f7b); re-froze at a102b537. Verified NO commit after 42526c66 touches the two T106 files.

METHOD: same in-process reinject harness (text-mutated module into sys.modules before the by-value imports resolve; non-vacuity guard = each pattern must match exactly 1x). Baseline (unmutated inject) GREEN across all 6 new tests + AS-2 + AS-1 spike + AS-6 goldens → harness faithful. The delta is append-only: 6 new tests, ZERO removed lines across the whole rework (966cca75..HEAD); goldens byte-identical (test_t106_as6 both hashes PASS; hashes unchanged in diff).

PRODUCER'S 6 NEW MUTANTS — all reproduce, each reddens its specific new test:
| mutant | mechanism | target | result |
|---|---|---|---|
| medlot | drop _is_finite_number OverflowError guard | r2_huge_int_lot | RED — OverflowError escapes untyped |
| medfoot | drop the B0 except OverflowError | r2_huge_int_footprint | RED — OverflowError escapes untyped |
| low1echo | revert B0 re-echo to {exc} | r2_b0_error_echo | RED — unbounded (AssertionError) |
| detail | revert to {detail or ''} | r2_no_candidate_detail | RED — unbounded (AssertionError) |
| sibling | except (GEOSException, TopologicalError) | r2_second_sibling | RED — GeometryTypeError escapes |
| preview | drop the repr try/except | r2_preview_never_raises | RED — hostile __repr__ escapes |

KEY CLOSURES (my round-1 advisories):
- ADVISORY-1 CLOSED: the sibling mutant now reddens the new second-sibling test (GeometryTypeError, a genuine ShapelyError that is neither GEOS nor Topological) WHILE test_t106_as2 stays GREEN — the two sibling tests are complementary and the base-class catch is now locked.
- ADVISORY-2 CLOSED: the detail mutant now reddens; a short detail is still surfaced (bound transparent).
(continued 2/2)

---

M5-T106 G4 DELTA — part 2/2

MY 4 OWN DISTINCT MUTANTS — all RED, each adds adequacy depth:
| mutant | finding |
|---|---|
| medfoot + assert medlot stays PASS | the two OverflowError guards are INDEPENDENT — no cross-masking (medfoot reddens ONLY the footprint test; the lot test stays green) |
| _is_finite_number `except OverflowError: return True` | RED (AssertionError) — r2_huge_int_lot pins the SPECIFIC reason non_finite, not just "some typed refusal" |
| _preview `except Exception` → `except RecursionError` | RED — the hostile-__repr__ (RuntimeError) case is load-bearing; the guard must be broad Exception, not only recursion |
| B0 re-echo `{_preview(exc)}` → `{exc!r}` | RED — low1echo also catches the `!r` maintainer alternative, not only `{exc}` |

SCOPE / AS-6 VERIFIED INDEPENDENTLY at HEAD:
- Full tests/scenario: 770 passed (matches harvest; includes T107/T108/T109 scene tests). All round-1 T106 tests still green (behavior preserved).
- No unbounded caller-input echo remains: grep finds no `!r}` / bare `{exc}` / `{detail or}` — every echo (lot/footprint vertex, source, height, B0 error, detail) routes through _preview. Round-2 docstring + report AS-4 wording now accurate.
- ruff two files → All checks passed (rc 0); modularity_check → failures 0, EXIT 0.
- No existing test edited; goldens byte-identical.
- Public API unchanged (only private-helper bodies + the two builders' internals changed; __all__ and signatures intact; the already-landed M5-T107 imports it and its scene tests pass).

FINDINGS (both ADVISORY, non-blocking):
- A1: massing_model.py is now 994/1000 SLOC — only 6 lines of headroom under the hard cap. modularity exit 0 today, but the NEXT substantive touch should split with a facade or record an expiring exception.
- A2: the B0 `except OverflowError` labels field="proposed_massing.outline" even if the overflowing coord sits in a LEVEL outline — minor labeling imprecision; the reason (non_finite) is correct and it fails closed.

Both round-1 advisories are genuinely closed; every new guard has a reddening mutation; scope is clean.

M5-T106 G4 VERDICT: PASS
END-OF-REPORT
