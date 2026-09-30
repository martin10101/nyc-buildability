---
name: m5-address-arc-provenance-test-gap
description: G4 QA pattern for the M5 address-entry arc — provenance-disclosure tests under-assert secondary rows even when security-critical rows are covered
metadata:
  type: project
---

In the M5 address-entry UI arc (M5-T015 Packet 1, M5-T016 Packet 2 confirm card), the
provenance-disclosure ("Where this came from" `<details>`) tests reliably cover the
security-critical rows (endpoint HOST-only vs full-URL, connector-correlation-id labeled
distinct from HTTP reference id, `\bVerified\b` absence, withheld-reason verbatim, request-param
and source-fact escaped text) but tend to OMIT assertions on the secondary rows that design
spec section 4 also lists: the retrieval timestamp and the in-disclosure Geosupport return-code
lines (grc/grc2). Those render correctly but no test pins them, so a "drop the retrieved-at row"
or "drop the disclosure GRC lines" mutant survives.

**Why:** M5-T016's confirm-test S5 (address-confirm.test.tsx) asserted 6 of 8 disclosure field
types; retrieved_at and the disclosure GRC codes were unasserted (the warnings-block
`warning-grc-message` is a different element/testid than the disclosure GRC line, which has no
testid). The producer's own named-mutant table also omitted these two mutants — a tell that
they are uncovered.

**How to apply:** When gating any address/provenance-disclosure packet, cross-check the spec
section-4 field list against the S5 test assertions row-by-row; flag retrieved_at and
disclosure-GRC as the usual gaps. Feature is typically correct (fields render) so this is a
required-correction (add assertions), not a FAIL.
