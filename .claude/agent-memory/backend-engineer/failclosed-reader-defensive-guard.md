---
name: failclosed-reader-defensive-guard
description: Fail-closed parser/reader pattern in services/api (refusal-as-VALUE + catch-all guard) and how it shapes mutation tests
metadata:
  type: feedback
---

Fail-closed readers in `services/api/app` (e.g. `app/drawings/dxf_reader.py`, mirroring
`app/documents/units.py`/`taxonomy.py`) return a typed refusal VALUE, never an exception:
raise a private `_Refuse(reason, detail)` marker internally, convert it to a frozen
`*Refusal` dataclass at the public boundary, and end that boundary with a catch-all
`except Exception -> refusal(MALFORMED_STRUCTURE, "unexpected ...")` so no exception ever
escapes. Enums are frozen/closed; bounds live in an injectable frozen `*Limits` dataclass;
units/values are REPORTED with provenance, never assumed.

**Why:** the platform's fail-closed principle (a bad/oversized/malformed input is a visible
value, not a crash) plus phase-C honesty (no assumed units/tolerances).

**How to apply:** when writing a mutation test that proves a specific bound, assert the
SPECIFIC `reason`, not just `isinstance(result, Refusal)`. The catch-all guard means dropping
a guard often still yields a refusal — but via `MALFORMED_STRUCTURE` (e.g. a dropped
pair-parity check lets the pairing loop IndexError, caught as MALFORMED_STRUCTURE) rather than
the specific reason. `isinstance(..., Refusal)` would stay green and the mutation would NOT
redden. Asserting `result.reason is <SpecificReason>` reddens correctly. Ruff on this repo is
`line-length=100`, `select=E,F,I,UP,B` — wrap long `raise _Refuse(...)` calls; `raise ... from
None` inside an `except` (B904). See also [[env-producer-sandbox-no-exec]].
