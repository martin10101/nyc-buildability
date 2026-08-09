---
name: m1-t008-g3-carryforward
description: M1-T008 DOB legacy research G3 delta PASS @0a45aa5 (was FAIL @4535b18); two-session provenance now honest; M2 legacy-parser hazards list; one LOW residual (producer-report 160,263-byte stale total)
metadata:
  type: project
---

M1-T008 (DOB-wide legacy source research) G3 delta re-review PASS 2026-07-17 at rework commit 0a45aa5 (docs-only: research doc, fixtures README, producer report; all 43 fixtures byte-identical, verified via git diff + independent byte count 146,865).

D1/D2/D3 all RESOLVED; D4 addressed. Verified against committed artifacts myself: catalog extract 10:55Z with 71/342 resultSetSize + 43/34 DOB-attributed; views extract 10:56Z with eabe rowsUpdatedAt epoch 1784220573 = 2026-07-16T16:49:33Z (arithmetic re-done); logs 11:01:25–11:03:54; headers Date 11:04:48 GMT and Last-Modified = 3h2n rowsUpdatedAt epoch 1784223622; HTTP 500 tag c4361147 at key-probes 59–62; 3h2n 19011215→20260715/31 garbage and 6bgk 19101004→20260714/64 garbage at 34–52; cast_ipu4 at counts-log 132–135. README now documents all 43 fixtures (programmatic cross-check: zero missing); e98g duplicate documented as byte-identical 3-byte `[]`. Every second-session (~16:15–16:21Z) observation is explicitly labeled "no committed artifact".

**Residual (LOW, non-blocking, carry to acceptance/next touch):** producer report §1/§11 states post-rework directory total "160,263 bytes" but committed tree measures 160,480 on disk (README 13,615, not 13,398) — README grew ~217 bytes after the producer measured it (self-referential). Fixtures-only figure (146,865) is exact and the report itself disclaims the directory total as variable. Also §11 line phrasing "44 files / 146,865 fixture bytes" mildly conflates counts (correct in §1).

**Why:** delta closed the M2-T004-precedent provenance-narrative failure; the reconciliation pattern (authoritative committed-artifact timestamps + explicit no-artifact labels for session-only observations) is now the repo's model example.

**How to apply:** at M2 Stage A/B connector reviews enforce the doc §7 hardening list: BIN-primary fan-out, reject 7-char BBLs, 5/5 vs 5/4 vs unpadded block/lot, four date encodings + mixed-column, TEST-record quarantine (block 99999/house TEST), future-date window (2105 CO), 3h2n↔855j dedup mandatory, eabe snapshot-diff (single dobrundate), `::floating_timestamp` casts need a 500-fallback (proven fail on ic3t, tag c4361147), classify 5xx separately from the 400 no-such-column drift signature, `:@computed_region_*`/`location` excluded from provenance facts, 6bgk respondent PII redaction. Unfixtured quantifiers to re-verify at connector build: eabe count(distinct dobrundate)=1, 3h2n violation_category group-by, 6v9u code=I2, AHV 28-result catalog probe.

Related: [[m1-t007-g3-carryforward]] (binding directives §2–§6, anchor BIN 1006014), [[m2-t004-g3-carryforward]] (stale-assertion FAIL precedent — now with a resolved counterexample).
