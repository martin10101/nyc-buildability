# M5-T097 — G3 DELTA re-review after the FAIL (code-reviewer "cr-t097", the SAME reviewer, read-only)

> Transmission history: requested by SendMessage after the round-2 rework (cherry-pick e04c2b5b) and the re-freeze (identity
> 88431c2d); pinned at 851c4e63; delivered as two parts (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined
> verbatim (transport wrapper tags removed only). B1 CLOSED: the splitter is linear for LF, CR and CRLF (200k LF lines
> 6.32 s -> 0.53 s), semantics identical to str.splitlines for every terminator case. The first-round report stays at
> M5-T097-G3.md.

---

M5-T097 G3 DELTA re-review (read-only) - Part 1/2. B1 is CLOSED; verdict PASS at end of Part 2.

PIN HEAD 851c4e63; reader blob at HEAD == e04c2b5b (94895927, verified identical). Method: reader+test delta 9a281517->e04c2b5b; from services/api ran ruff (clean) + pytest (61 passed, 6.55s); RE-TIMED the splitter at HEAD; independently checked str.splitlines parity.

B1 CLOSED. _iter_dxf_lines now uses ONE precompiled _LINE_TERMINATOR = re.compile(r"\r\n|\r|\n") with a single .search(text, pos) per line and match.start()/end(); no per-line rescan for an absent terminator. Re-timed at HEAD (50k/100k/200k single-char lines):
  pure-LF: 0.131 / 0.241 / 0.527s  (~2x per doubling = LINEAR)
  pure-CR: 0.130 / 0.246 / 0.568s  (LINEAR)
  CRLF:    0.125 / 0.296 / 0.543s  (LINEAR)
Round-1 pure-LF was 0.49 / 1.44 / 6.32s (~4x per doubling); 200k is now ~12x faster. The O(n^2) is gone for all three terminator styles.

Check 1 (single-pass O(n)): confirmed by the timing above and by reading the code - one search(), no double-find. CRLF-first alternation makes a CRLF one break (start at \r, end past \n), never CR + an empty line.

Check 2 (semantic identity): I independently compared list(_iter_dxf_lines(t)) to t.splitlines() for lone CR ("a\rb"), CRLF, "\n\r", trailing CR at EOF ("a\r"), empty final line, "\r\n\r\n", and mixed "a\r\nb\nc\rd" - ALL MATCH. Control chars \x0b \x0c \x1c \x1d \x1e are kept in-value (new = ['A\x0cB']) while splitlines splits them - so no pairing shift. All prior 49 reader + 7 round-trip tests pass unchanged. No behaviour change for any valid file. Part 2/2 follows.

---

M5-T097 G3 DELTA re-review - Part 2/2 (verdict).

Check 3 (time guards robust + really redden): the two new guards use a machine-speed-INDEPENDENT 4x-input time RATIO (n vs 4n lines) with min-over-reps to damp scheduler noise and an 8.0 ceiling (linear ~4x, quadratic ~16x = 2x margin), so a loaded CI runner slows both measurements proportionally and the ratio stays stable. test_t097_b1_mutation_double_find_reddens_time_guard rebinds the consumed splitter to the round-1 double-find and asserts ratio >= 8.0 - it PASSED here (the double-find measured quadratic, ~16x), and the real splitter passes the same check, so the guard genuinely reddens under the old code and is not a no-op. Residual flake risk is low; ADVISORY only: if it ever flakes on CI, widen the ceiling/reps rather than delete it (that slow mutation test is 3.98s, the suite's slowest).

Check 4 (new issues / scope / deps): none. The delta also adds exact-edge max_lines+1 / max_line_chars+1 probes plus an off-by-one (B6/B7) mutation with real teeth (both edge files slip through under `> max+1`; baseline refuses). Scope unchanged: same allowed paths, test_dxf_roundtrip.py untouched; zero new dependencies (re is stdlib, module-level compile). My round-1 advisory A1 is FIXED - the docstring drops the blanket "verbatim" and documents the strip-to-'' nuance for a value made solely of such control chars. Round-1 advisories A3 (round-trip/writer coupling) and A4 (reader in the modularity WARN band, --check warnings-only) are unchanged and remain non-blocking; not affected by this delta.

Ruling: the single blocking defect from round 1 (B1 O(n^2) DoS) is fixed correctly and cheaply (stdlib regex, O(n)), semantic identity is preserved, and the fix is now permanently guarded by a mutation-backed complexity test - exactly the coverage whose absence let B1 pass round-1 CI.

M5-T097 G3 VERDICT: PASS

END-OF-REPORT
