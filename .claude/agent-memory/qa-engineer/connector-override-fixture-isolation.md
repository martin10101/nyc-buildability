---
name: connector-override-fixture-isolation
description: G4 lesson - when reviewing a fail-closed override that layers on top of a pure classifier, verify each override trigger has a fixture that ISOLATES it (or a reason-fragment assertion that binds it), and that the override never over-fires
metadata:
  type: feedback
---

For a connector that applies a fail-closed override on top of a pure classifier (M4-T015 DCM
street-width: a segment that is not `Feat_Type=Mapped_St`, or `Paper_ST='Y'`/`Record_ST='Y'`, never
classifies wide regardless of the width text), check BOTH directions of the override binding:

1. **Each trigger isolated / reason-bound.** The paper fixture must be a MAPPED street with only the
   paper flag set (`Feat_Type=Mapped_St, Paper_ST=Y, raw "80"`) so dropping the paper check flips it
   to wide and fails the test. M4-T015's paper (Jay Place 599) and unmapped/former fixtures isolate
   cleanly; the RECORD fixture (Woodvale 16549) was NOT isolated (`Feat_Type=Not_mapped` AND
   `Record_ST=Y`), so two triggers were live - but the test asserts `"Record_ST" in override_reason`
   and the reason-ordering (is_record checked before the Feat_Type-not-mapped else) means removing
   the record check flips the reason to "Feat_Type=" and the test still fails. Reason-fragment
   assertions can rescue a non-isolated fixture; verify the branch ORDER makes that hold. Advisory:
   a `Record_ST=Y` + `Feat_Type=Mapped_St` fixture would be strictly stronger.
2. **Override doesn't over-fire.** A genuinely-wide mapped street with no flags must STAY wide
   (test_clean_wide_segment... asserts effective=wide, override_reason=None); an already-narrow
   segment + a flag must be unchanged with override_reason=None (nothing wide to suppress). Both
   present in M4-T015.

Also confirm the raw classifier read is preserved separately (`width_classification`) and only the
`effective_*` fields are overridden - provenance of the raw text/read is never discarded.

**Boundary binding for a >=75 fail-closed classifier:** the tests must assert BOTH sides at the
exact cutoff: "75" wide vs "74.99" narrow; "<75" confident-narrow vs "<=75" ambiguous; "75-90" wide
vs "60-75"/"74-75.3" straddle; ">75" wide vs ">60" ambiguous. Because the code uses one shared
`WIDE_THRESHOLD_FT` constant (plus a `== 75.0` assertion), a constant mutation is caught even where a
near-boundary inequality test (e.g. ">74.9") is absent. See [[gate-reproduce-producer-numbers]].
