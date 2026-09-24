# M5-T097 — G5 DELTA re-review after the FAIL (security-reviewer "sec-t097", the SAME reviewer, read-only)

> Transmission history: requested by SendMessage after the round-2 rework (cherry-pick e04c2b5b; identity 88431c2d);
> pinned at 851c4e63; delivered as two parts (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim
> (transport wrapper tags removed only). Finding 1 CLOSED: linear at the default caps (2M LF lines ~8.3 s) and at the clamp
> ceiling; the terminator regex is ReDoS-free; every round-1 protection intact. The residual (run the parse off the
> request thread with a timeout at the import route) goes to PKT-F. The first-round report stays at M5-T097-G5.md.

---

M5-T097 G5 DELTA re-review — Finding 1 (O(n^2) splitter DoS) is CLOSED. Part 1/2.

PIN: HEAD 851c4e63 at start. Round-2 commit e04c2b5b touches exactly the 3 allowed files (dxf_reader.py, test_dxf_reader.py, producer-report.md), no forbidden path; the only added import is stdlib `re` (zero new package deps, no requirements change); reader still unwired (grep of app/apps/packages shows no production importer). All probes run from services/api.

FIX: the per-line double `find("\n")`+`find("\r")` is replaced by one precompiled `_LINE_TERMINATOR = re.compile(r"\r\n|\r|\n")` with `.search(text, pos)`; `end=match.start()`, `nxt=match.end()` absorbs a CRLF in one match. Exactly the single-pass fix recommended. `_decode`, `DxfLimits.__post_init__`, and the caps are untouched (surgical delta).

1) FINDING 1 CLOSED — now LINEAR, seconds not minutes:
- DEFAULT caps (8MB / 2M lines) pure-LF: 500k=1.86s, 1M=4.29s, 2M=8.30s (~2x per doubling). pure-CR: 500k=2.16s, 1M=3.77s, 2M=8.76s (~2x). Round-1 was ~3.7x/doubling (quadratic → tens of minutes). The regression is gone.
- Clamp ceiling (64MB / 8M lines), pure-LF ~64MB single parse: 26.7s, refuses TOO_MANY_LINES. Linear, proportional to input, no amplification.
Bounded in seconds at every cap.

2) ReDoS — NONE. The pattern is an alternation of fixed literals (no nested quantifiers, so no catastrophic backtracking), and `re.search` scanning is linear. Empirically confirmed: long CR-run `"\r"*k` at 500k/1M/2M = 1.44/2.74/6.09s (~2x); mixed `"\r\n\r"*k` and `"\n\r"*k` also ~2x per doubling. CRLF is absorbed correctly via match.end() (no spurious empty line).

Part 2 (protections intact, no-new-issue, residual advisory, verdict) follows.

---

M5-T097 G5 delta re-review Part 2/2 — protections, no new issue, residual, verdict.

3) Protections still hold (delta only touched `_iter_dxf_lines`):
- Streaming caps still fire DURING the scan: max_lines=1000 on a 1,000,000-line input -> too_many_lines; a 5000-char line with max_line_chars=4096 -> line_too_long. Still one line at a time, no full list materialised.
- Byte-cap-before-decode, clamp (all 5 fields clamp to ceiling; `_LIMIT_CEILINGS` keys == dataclass fields), `<1` raise, str-path binary-sentinel + isascii, non-bytes/str typed refusal, and nan/inf -> bad_coordinate all still PASS (unchanged by the delta).
- CR / LF / CRLF parse byte-identically for a real LINE doc (ok=True, same primitive, same coords).

4) No new issue in the delta. The new tests are meaningful: a real red/green time-scaling guard (asserts the double-find mutant scales quadratically while the shipped regex stays sub-quadratic) plus exact-edge max_lines / max_line_chars probes with off-by-one mutations. Suite was green in round 1 and the delta only adds cases.

RESIDUAL — ADVISORY, for the later import/wiring packet (NOT blocking this module): the parse is now linear but still ~8s at the DEFAULT cap (2M lines / 4MB) and ~27s at the clamp ceiling (8M lines / 64MB) for a fully-consumed worst case. This is normal O(n) parser cost with no amplification, so it is a wiring concern, not a defect here: the import route must run read_dxf off the request thread (a worker/job) with a timeout and enforce an upload byte limit, and may set a lower DEFAULT max_lines for its deployment. Your prior advisories A1-A4 (control-char sanitization on output, bounded refusal-detail reflection, huge-int digit cap, bytes-only input) remain correctly deferred to that same packet.

Bottom line: the sole blocking defect from the first review is fixed correctly and proven linear + ReDoS-free; scope, deps, and unwired status are clean; no regression to the round-1 defenses.

M5-T097 G5 VERDICT: PASS

END-OF-REPORT
