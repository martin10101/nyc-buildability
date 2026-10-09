# M5-T097 — G4 DELTA re-review (qa-engineer "qa-t097", the SAME reviewer, read-only)

> Transmission history: requested by SendMessage after the round-2 rework (cherry-pick e04c2b5b; identity 88431c2d);
> pinned at 851c4e63; delivered as two parts (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim
> (transport wrapper tags removed only). The off-by-one mutants B6/B7 now die; all 14 earlier kills still die; the two
> scaling-ratio guards are non-vacuous (real 3.4-5.7x vs double-find ~12.8x, ceiling 8.0). Flake watch is advisory.
> The first-round report stays at M5-T097-G4.md.

---

M5-T097 G4 DELTA re-review (qa-engineer, read-only). Part 1/2.

HEADS: started at HEAD 851c4e63 (seam); working tree == round-2 commit e04c2b5b for dxf_reader.py (verified). Round-1 review was 9a281517. Delta reviewed via `git diff 9a281517 e04c2b5b -- <3 T097 paths>`. Baseline: `pytest tests/drawings/test_dxf_reader.py tests/drawings/test_dxf_roundtrip.py -q` -> 61 passed (56 + 5 new). T097 delta confined to dxf_reader.py + test_dxf_reader.py + producer report; test_dxf_roundtrip.py unchanged; no forbidden path.

SPLITTER REWRITE: the O(n^2) per-line double-find is replaced by one precompiled `_LINE_TERMINATOR = re.compile(r"\r\n|\r|\n")` + `search(text, pos)` — O(n); CRLF absorbed via alternation order (\r\n tried first); `end=match.start()`, `nxt=match.end()`; bounds logic unchanged.

ITEM 1 — off-by-one caps now DIE (round-1 ADVISORY-1 closed):
- B6 max_lines `>max`->`>max+1` -> new test_t097_as2_max_lines_exact_edge_refuses_at_limit_plus_one FAILS -> KILLED (was SURVIVED round 1). Exact edge pinned: max_lines=20 on a 20-line file parses; max_lines=19 refuses TOO_MANY_LINES.
- B7 max_line_chars `>max`->`>max+1` -> new max_line_chars exact-edge probe FAILS -> KILLED. Edge pinned: max_line_chars=30 on a 30-char line parses; 29 refuses LINE_TOO_LONG.

ITEM 3 — earlier kill set re-run against the NEW splitter; ALL still KILLED, no guard weakened, every must-stay-PASS invariant intact:
- A1 splitlines-restore, A2 M3 isinf-only (inf stays PASS), A3 M4a + A4 M4b neg-bulge (pos-bulge stays PASS), A5 M5 closed-flag (flag-129 stays PASS), A6 clamp, A7 lenient-str, A8 insunits-pop -> all KILLED.
- B3 clamp-skip-max_bytes, B4 str-sentinel-dropped (non-ASCII stays PASS = independent), B5 insunits-22/23-swapped -> KILLED.
- C1 max_vertices, C2 max_entities, C3 str-size -> KILLED.
- B1/B2 re-expressed for the regex splitter: B1new CRLF-not-absorbed (`match.end()`->`match.start()+1`) -> KILLED (control-char probe correctly stays PASS); B2new CR-not-a-terminator (LF-only regex) -> KILLED. (continued 2/2)

---

M5-T097 G4 DELTA re-review. Part 2/2.

ITEM 2 — the two new scaling-ratio time guards:
- Redden under a double-find rebind: YES. Committed test_t097_b1_mutation_double_find_reddens_time_guard passed 8/8 when I ran it repeatedly. Independent check (my own local timing, no module rebind): a round-1-style double-find scales 12.8x on 4x input vs the real regex splitter 5.7x, ceiling 8.0 — the ceiling sits cleanly between them, so the behaviour guard `assert ratio < 8.0` reddens under the double-find and passes for the real code.
- Non-vacuous: real and mutant straddle the ceiling; the mutation test also carries a must-stay-PASS (real < ceiling) assertion.
- FLAKE: LOW-MODERATE. Both guards passed 8/8 via pytest. Real ratio across ~12 measured runs: 3.4-5.7x (worst 5.7 vs ceiling 8.0 = ~1.4x headroom). Design is sound (min-over-reps damps upward noise; ratio is machine-speed-independent; 60-240 KB inputs are cache-friendly so no cache-cliff between N and 4N; helper also asserts total==text.count(term)). It is still a wall-clock guard, so a rare heavily-loaded CI runner could theoretically inflate the ratio past 8.0. ADVISORY (non-blocking): if it ever flakes, raise the ceiling toward ~10 (well below the ~13x quadratic signal) or add reps.

ITEM 4 — vacuity / new gaps: none blocking.
- Exact-edge probes are non-vacuous (assert BOTH at-limit parses AND limit+1 refuses; the combined off-by-one mutation confirms both directions redden).
- New splitter correctness is under test: CRLF absorption (B1new teeth), CR-as-terminator (B2new teeth), control-char-verbatim (unchanged, A1 teeth), plus the helper's per-run total==count consistency check.
- Round-1 ADVISORY-1 is now closed by the exact-edge probes; ADVISORY-2 (INSUNITS 22-24 [recalled-verify], G1 scope) is unchanged and out of G4 scope.

DELTA SUMMARY: splitter rewrite is behaviour-preserving and now provably ~linear; the two new time guards are non-vacuous and empirically stable; the two exact-edge probes close my prior advisory; every prior kill (14) still dies and no guard was weakened. Only residual is the wall-clock-guard flake watch (advisory).

M5-T097 G4 VERDICT: PASS

END-OF-REPORT
