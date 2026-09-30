---
name: serializer-mutation-resistant-pinning
description: For deterministic writer/serializer modules (DXF/PDF/etc.), tests that import a constant by value ship green when the constant is weakened — pin hardcoded literals in the serialized output; single-choke design.
metadata:
  type: feedback
---

For deterministic writer/serializer modules (services/api/app/cad/dxf_writer.py,
pdf_sheet_writer.py, and similar output builders) reviewers (G3/G4) fail tests that only
prove a constant equals itself. Apply these when writing or reworking such a module:

- **Pin HARDCODED literals in the SERIALIZED OUTPUT, not the constant.** A test that does
  `assert PROPOSED_LABEL in text` or `assert pairs[i] == (70, str(d.INSUNITS_FEET))` passes
  for ANY value of the imported constant — weakening the constant ships green. Instead assert
  the exact bytes: `assert "PROPOSED - NOT A CITY RECORD" in text`, `assert pairs[i] == (70, "21")`.
  Mirror the sibling writer's honesty tests. (M5-T081 G3 F1 / G4 F1.)
- **Guard-necessity (load-bearing) tests.** For every safety guard (sanitizer, claim-word
  screen, bounds), add a test that feeds a violating input through the real path and asserts
  the TYPED refusal, so neutering the guard reddens the suite. Pin whole allow/deny sets as
  literals (e.g. the full CLAIM_CLASS_WORDS tuple) so dropping one entry reddens.
- **Sanitizer coverage must exceed CR/LF.** One newline-injection test lets a CR/LF-only
  weakening survive. Parametrize NUL (\x00), ESC (\x1b) and a non-ASCII char through the emit
  choke point. Keep ONE numeric choke point (`_format_real`) mirroring the ONE string
  sanitizer; enforce coordinate-magnitude bound there (mirror the PDF writer's 1e8).
- **Bounds refuse BEFORE materializing** (G5). In a builder, check `len(inputs)` and the
  product (edges × floors) against caps and raise a typed error BEFORE allocating rings/faces;
  read `len()` before building the tuple so a 10M-element request refuses in O(1). Test with a
  count just over the cap (builds if the pre-check is removed → clean mutant, no OOM) AND assert
  the huge count refuses fast.

**Why:** these are exactly the G3/G4/G5 blocking findings on the CAD writers; CI green does
not catch by-value binding or a too-narrow sanitizer — external review is the only guard, so
build the mutation resistance in up front. **How to apply:** any new/edited deterministic
output serializer under services/api. See the T081 rework commit and mutant table.
