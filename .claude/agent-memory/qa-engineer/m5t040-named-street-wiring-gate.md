---
name: m5t040-named-street-wiring-gate
description: M5-T040 G4 QA verdict (PASS) — named-street override wiring + DB-023 hardening + DB-025 display gating; where the strong/weak tests live
metadata:
  type: project
---

M5-T040 (named-street override WIRING + DB-023 hardening + DB-021 ceilings +
DB-025 display gating) passed independent G4 QA at sha b4865d1c (material
987930a2 + 751a1826; CI run 35407153078 success at 4d8847c6 == material identity,
751a1826..4d8847c6 code diff empty).

**Why:** Documents which tests are load-bearing so a later rework or consumer
change can be re-judged fast.

**How to apply:**
- DB-023(a) is proven by DIFFERENTIAL/source-bound tests in
  test_named_street_override.py: `test_db023a_all_signals_stripped_refusal_is_
  source_bound` (conditional-source REFUSED, unconditional-source ALLOWED) and
  `test_db023a_narrowed_source_quote_to_omit_condition_refused` (match=
  "COMPLETE sentence span"). These are the exemplary ones — they prove the refusal
  is tied to the digest-covered source, not merely to `matched_override` presence.
- AS-4 wiring truth table fully forced in test_wide_street_wiring.py: matched→PR
  with provenance asserted exactly (`test_matched_override_forces_professional_
  review_with_provenance` + `..._carries_distinct_provenance`), INDETERMINATE/
  missing-bounds/non-string/list-CD → unresolved, all-NOT_MATCHED → attested.
- DB-025(d) multi-page digest fixture IS present (not missing):
  `test_db025d_multipage_each_segment_carries_its_own_page_digest` in
  test_wide_street_live_provider.py — page-2 segment carries page-2's digest.
- DB-021(e) branches: `test_db021e_unexpected_wide_geometry_error_returns_none`
  and the parametrized `test_db021e_attested_lot_rejects_every_unusable_subbranch`
  (5 sub-branches + positive companion).
- Non-blocking ADVISORY residue: (A1) CalculationEvidence review-label gating not
  independently forced from null-FAR (relies on server invariant; DB-025c label
  test covers the sibling); (A2) untested benign combo all-narrow + may-touch →
  NOT_WITHIN with exceptions_checked=False (conservative, not escalated); (A3)
  unreachable `prov is None` defensive branch on MATCHED_OVERRIDE; (A4)
  wide_street_wiring.py over the modularity WARNING threshold (0 failures,
  disclosed — G3 cohesion signal).

See [[wide-street-display-gating-test-adequacy]].
