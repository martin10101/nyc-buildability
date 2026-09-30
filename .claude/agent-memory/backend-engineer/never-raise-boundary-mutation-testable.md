---
name: never-raise-boundary-mutation-testable
description: Make a "public API never raises" contract's boundary try/except in-process mutation-testable by extracting it into a named helper
metadata:
  type: feedback
---

To prove a "public API never raises on caller data" contract is load-bearing with an
IN-PROCESS mutation (the repo standard; a try/except cannot be monkeypatched in place),
extract the boundary `try/except` from the public function into a named module-level
helper (e.g. `pdf_sheet_writer._finish`, which catches the private `_RenderRefused`
carrier that `_num` raises on a non-finite number and returns a typed refusal). A test
then `monkeypatch.setattr(writer, "_finish", <no-catch variant>)` in the CONSUMING
namespace and asserts the public API now RAISES — reddening the never-raise contract.

**Why:** M5-T105 (D-087 PKT-B1, DB-053 b) had to make the honest never-raise contract
mutation-provable. The functional guard already existed (M5-T091: `_num` raises, boundary
catches); the gap was an honest docstring + a reddening mutation. A pure structural
extraction of the existing try/except left output byte-identical (golden + owner sample
unchanged) while making the catch swappable.

**How to apply:** Any "never raises / always returns a typed refusal" surface in this
repo (the cad writers, dxf/pdf readers — several carry that docstring). Pair it with:
(1) `pytest.raises(<private carrier>)` on the inner fn to prove it really raises
internally, (2) a public-API test asserting a returned refusal (real code), (3) the
no-catch mutant asserting the raise now escapes. See also [[in-process-mutant-technique]]
and [[worktree-vs-shared]]. For a specific-code guard (e.g. y-only finiteness), the probe
must assert the EXACT `reject_code`, not just `isinstance(refusal)` — a backstopped guard
(a dropped y-check still refuses downstream under a DIFFERENT code) survives an
isinstance-only test (M5-T091 G4 EX2 survivor).
