---
name: complexity-regression-scaling-ratio-guard
description: How to write a robust, non-flaky test guard against an O(n^2)-vs-O(n) time regression (used for the M5-T097 DXF splitter)
metadata:
  type: feedback
---

To guard a parser/scanner against a quadratic-time regression without a flaky wall-clock, assert a
machine-independent SCALING RATIO, not an absolute time.

**Why:** the repo's CODING_RULES forbid flaky tight wall-clock tests; an absolute-seconds ceiling
either flakes on a loaded CI runner or has to be so loose it misses the regression. A ratio cancels
machine speed. (M5-T097: the round-1 DXF splitter called both `text.find("\n")` AND `text.find("\r")`
per line, so a pure-LF/pure-CR file rescanned to EOF each line -> O(n^2); both G3 and G5 FAILED on it.)

**How to apply:**
- Parse N and 4N single-char lines; assert `t(4N)/t(N) < CEIL` with `CEIL` set between linear (~4x)
  and quadratic (~16x) - 8.0 gives a 2x margin over linear. Linear stays ~4x regardless of hardware.
- Use MIN over a few reps to damp scheduler noise; add a sanity assert that every line was consumed
  (`total == text.count(term)`).
- Pair it with an in-process mutation: rebind the CONSUMED module global (`_reader_mod._iter_dxf_lines`)
  to the old quadratic implementation and assert the SAME ratio now `>= CEIL` (the guard reddens),
  plus a must-stay-PASS that the real code is `< CEIL`. Keep the mutant's large size bounded (N=30k
  -> ~2s) since it runs the slow path.
- The real fix for CR/LF/CRLF splitting: one precompiled `re.compile(r"\r\n|\r|\n").search(text, pos)`
  (CRLF alternative FIRST so `match.end()` absorbs a full CRLF) is byte-identical to a correct
  double-find and O(n). Prove parity on ~20 edge cases (empty, lone CR at EOF, `\n\r`, blank lines).

See also [[in-process-mutant-technique]].
