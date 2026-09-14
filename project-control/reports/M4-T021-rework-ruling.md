# M4-T021 — consolidated rework record and orchestrator ruling on the G3/G4 disagreement

Recorded by the orchestrator 2026-09-14 at review head `2231227a`. Both independent reviews
returned; per CLAUDE.md permanent principle 17 (defect convergence) the COMPLETE failure
surface is inventoried here and clustered before any fix is made, rather than repairing one
finding and re-running.

## Complete failure surface (3 blocking items, 2 reviewers)

| ID | Source | Defect | Cluster |
|---|---|---|---|
| **G3-F1** | code-reviewer | EC-5 `Ec5AttestedPreconditions` is a presence-gate only; a caller passing `(False, False, "not yet checked")` still receives `STATUS_COMPUTED` | Contract fidelity — attestation semantics |
| **G3-F2** | code-reviewer | The module and producer report state `BUFFER_QUAD_SEGS = 8` matches "shapely's implicit default"; the API actually called (`BaseGeometry.buffer`) defaults to **16**. Reproduced live: 67 vs 35 vertices, 33365.48 vs 33214.45 sq ft on the same line | Truthful documentation + untested end-cap path |
| **G4-F1** | qa-engineer | `source_retrieved_at` / `source_raw_digest` are required **input** fields but exist on **no output** dataclass — retrieval identity and raw digest are silently dropped between validation and result construction | Provenance retention (permanent principle 2) |

Common root cause across G3-F2 and G4-F1: claims in the producer report were written from
intent rather than from a read of the shipped surface (the `quad_segs` default was checked
against the wrong shapely API; "carried through unmodified into the result" was asserted for
fields that never reach the result). G3-F1 is a separate, substantive contract-reading dispute.

## RULING 1 — EC-5 attestation: G3-F1 STANDS. The value gate must be implemented.

The two reviewers reached opposite conclusions on the same question, so the orchestrator rules.

- **G3 position (blocking):** the packet names a specific precedent — "the D-052/M4-T019
  `AttestedPreconditions` precedent" — and G3 *read that precedent's source*
  (`dcm_street_width_policy.py:337-364, 384-402`), finding that its analogous
  `exceptions_checked` attestation is a genuine **value gate**: when `False`,
  `classify_street_width_policy` returns `DECISION_UNRESOLVED` and refuses to classify.
- **G4 position (non-blocking, NB-2):** the packet's words "cannot silently skip them" require
  only that the attestation cannot be omitted, which the no-default dataclass already enforces.

**Ruling: G3 prevails, on three independent grounds.**

1. **Evidence beats reading.** The packet does not merely describe a behavior in prose — it
   names an existing accepted module as *the* precedent. When a contract incorporates a named
   precedent, that precedent's actual mechanism is the specification. G3 verified the mechanism
   from source; G4 decided the question from the packet's prose without reading the cited
   module. On a conflict of this shape the source-verified reading governs.
2. **The failure mode the packet names is exactly what ships today.** A caller who has done no
   legal verification and a caller who has done it correctly currently receive answers that are
   indistinguishable in shape and status. "Silently skipped" describes that outcome precisely,
   whatever the mechanism of skipping.
3. **Direction of the fix is fail-closed, and costs nothing.** The remedy is not "refuse to
   ship B4" — it is to return a typed unresolved state (mirroring `DECISION_UNRESOLVED`) when
   the attestation is not affirmative, exactly as the accepted sibling module does. That makes
   an honest state visible instead of issuing a computed-looking number on unverified
   preconditions, which is the same discipline D-059 was raised to enforce elsewhere in the
   product. The producer's practical concern (the named-street override table does not exist
   yet, so `True` is not always available) is answered by this design, not defeated by it: the
   caller gets a clearly-typed "preconditions not attested" result rather than silence.

The producer's disclosure of this judgment call was exemplary and is the reason the question
reached a reviewer at all; this ruling is on the substance, not on the disclosure.

## RULING 2 — G3-F2 `quad_segs`: correct the claim; set the value to 16.

The false statement must go regardless — a permanent code comment asserting a library default
that is not the default is exactly the kind of claim this project forbids. On the value itself:
there is no source-derived justification for 8, and 16 is the real default of the API actually
called, so the module adopts **16** (higher arc fidelity, no silent divergence from the library)
and documents that it is set explicitly for determinism. An end-cap-proximate test is required,
since G3 confirmed every current fixture deliberately keeps end caps away from the lot, leaving
this path untested.

## RULING 3 — G4-F1 provenance: implement remedy (a), not (b).

G4 offered either threading the fields through or disclosing the omission. Disclosure is not
acceptable here: permanent principle 2 requires every material fact to retain provenance, and
this module's entire purpose is to produce a provenance-carrying geometry fact for a future
rule (B7) and for audit. A result that cannot be traced to the fetch that produced it fails that
purpose. Thread `source_retrieved_at` / `source_raw_digest` from both attested inputs onto
`SegmentContribution` and `WideStreetBufferResult`, in both the computed and empty-set branches,
with covering tests.

## Carried forward as non-blocking candidates (not rework)

G3 A1 (report wording overstates CRS "re-validation" — the check is against a caller-declared
pair, since `SegmentPolyline` carries no per-feature CRS), A2 (`ec5_preconditions` has no
consumer until B7), A3 / G4 NB-1 (no multipolygon/holes lot fixture — both reviewers judged the
module's own handling geometry-agnostic; add a fixture before B7 consumes this for
production-shaped lots), G4 NB-4 (modularity check not independently reproduced by G4 —
the orchestrator ran it at the integration head: `selected 405 files; failures 0; warnings 17`,
neither new file among them, and G3 reproduced it independently as well).

## Process record

Gate records: G3 recorded **PASS** with F1/F2 blocking (gate-verdict semantics — the CLI
supports PASS/FAIL/BLOCKED only, and "PASS with required corrections" is recorded as PASS with
the corrections blocking acceptance). G4 recorded **FAIL**. Acceptance is blocked until all
three findings are corrected, validated, and committed, and both reviewers have re-reviewed the
corrected head (delta-attestation to the same reviewer agents). No DCV will be requested and no
acceptance attempted before then.
