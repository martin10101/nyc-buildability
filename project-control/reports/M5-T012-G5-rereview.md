# M5-T012 — G5 independent security RE-REVIEW (post-rework)

- **Task:** M5-T012 — internal flag-gated scenario optimization-toolkit API
- **Re-reviewed SHA:** `12fda82f3f237f2432efc99614c903496a8b2e02` (branch
  `candidate/D-024-mrl-option-b`), confirmed with `git rev-parse HEAD`
- **Previous verdict:** FAIL at `aafc75fd` — see `M5-T012-G5.md` (left intact as evidence)
- **Reviewer:** G5 security-reviewer (independent, read-only)
- **Date:** 2026-09-09

## Verdict: **PASS** at `12fda82f`

BLOCKING-1 is fixed, both halves, exactly at the boundary I specified, and I re-verified it
independently rather than on the producer's evidence. HIGH-1 and MEDIUM-1 are fixed and verified.
No new defect was introduced by the rework. Five findings remain open as coordinator-directed
backlog; none is blocking and my view on their severity has not hardened. The no-auth containment
finding stands unchanged and is restated in full in §6.

---

## 0. Independence re-statement

I did not produce, fix, or advise on the code in this rework beyond the published finding in
`M5-T012-G5.md`. My only repository writes across both reviews are the two report files. Every
result below comes from probes I wrote and ran **outside** the repository
(`…/scratchpad/g5t012/`), driving the real ASGI app. I did not take the producer's RED/GREEN
numbers on trust: I reproduced the RED state myself with an in-memory pytest plugin that
neutralizes one half of the rework at a time (§3.4), and I re-ran my own 32-combination matrix and
1,600-case fuzz against the shipped code. `git status --short` confirms the worktree is unchanged
except for this new report and other gates' artifacts; no product file, test, or fixture was
touched, and I ran no write-producing command.

## 1. Counts observed (match the expected values)

| Command | Observed | Expected |
|---|---|---|
| `python -m pytest services/api/tests/api` | **312 passed** in 38.64s, exit 0 | 312 ✅ |
| `python -m pytest services/api/tests/scenario` | **388 passed** in 4.10s, exit 0 | 388 ✅ |
| `python tools/modularity_check.py --check` | **failures 0, EXIT 0**, warnings 16 (was 15; the new one is `review_signal: services/api/app/api/v1/scenario_analysis.py`) | 0 / exit 0 ✅ |
| `ruff check` on the three packet files | All checks passed | — |
| Diff scope | 3 files, 1093 insertions / 125 deletions, all in `allowed_paths`; `main.py`, `app/scenario/**`, `app/config.py` absent from `git diff --name-only aafc75fd..12fda82f` | ✅ |

## 2. Per-finding resolution status

| # | Finding | Status at `12fda82f` | My verification |
|---|---|---|---|
| **B-1** | unpaired surrogate → unhandled `UnicodeEncodeError`, text/plain 500, no cid, off-matrix pair | **FIXED — verified** | 32/32 position×endpoint combinations now typed 422; 0 crashes; RED proof reproduced |
| **H-1** | engine call + `_finish` outside any guard | **FIXED — verified** | `_guarded_analysis` routes all four; a raising engine → `(500,"internal_error")`, `application/json`, cid, in-matrix, 0 leaks, on all four endpoints |
| **M-1** | `FORBIDDEN_FACT_KEYS` top-level only; echo-planting into a 200 body | **FIXED — verified** | all my echo-planting bodies now 422 at depths 3–7; no planted value reaches any body |
| M-2 | whole body buffered before the 64 KiB cap | open (coordinator backlog) | re-measured identical: 20 MB body → 422 with a 20.1 MiB `tracemalloc` peak |
| M-3 | ×437 output amplification + caller-controlled CPU | open (coordinator backlog) | re-measured identical (table in §5); **partially mitigated** by the new early rejection |
| L-1 | 405/404 wrong-method existence oracle | open (inherited posture) | unchanged; identical on accepted M5-T003/M4-T005 |
| L-2 | flag-off timing delta | open (inherited posture) | unchanged: new 6.18 ms vs unmounted 3.82 ms; accepted 6.70 vs 3.86 |
| L-3 | unbounded raw-BBL reflection in the 422 body | open (inherited, forbidden path) | unchanged |
| L-4 | AS-7 egress landmine covered 1 of 4 endpoints | **FIXED** | `test_as7_full_analysis_runs_fully_offline` is now `@parametrize(ANALYSES)` — 4 passed, still asserting `egress == []` |
| L-5 | request `Content-Type` unenforced | open (coordinator backlog) | unchanged (`text/plain`, absent CT and BOM-prefixed bodies still parsed) |

## 3. BLOCKING-1 — full re-verification

### 3.1 The fix matches the prescription

`_string_boundary_error` (`scenario_analysis.py:291-315`) performs `value.encode("utf-8")` for every
string **value** and every dict **key**, inside the pre-existing iterative walk, returning the
existing `(422,"validation_error")` pair — no new constant, no new matrix pair. `_finish:593` now
validates with `json.dumps(envelope, ensure_ascii=False, allow_nan=False).encode("utf-8")`, i.e. the
exact encoder settings Starlette's renderer uses, so the two can no longer disagree. Both halves, as
specified.

### 3.2 The hostile matrix, re-run by me (probe `p13_rereview.py`)

8 surrogate positions × 4 endpoints = 32 combinations, each sent as pure-ASCII wire bytes
(`json.dumps(ensure_ascii=True)` emits `\ud800`; the server's `json.loads` turns it back into a lone
surrogate — construction asserted in the probe itself):

```
  variable                 sens:422/cid/m/a  rank:422/cid/m/a  comp:422/cid/m/a  thre:422/cid/m/a
  candidate value          sens:422/cid/m/a  rank:422/cid/m/a  comp:422/cid/m/a  thre:422/cid/m/a
  dict KEY in a candidate   sens:422/cid/m/a  rank:422/cid/m/a  comp:422/cid/m/a  thre:422/cid/m/a
  objective                sens:422/cid/m/a  rank:422/cid/m/a  comp:422/cid/m/a  thre:422/cid/m/a
  assumption key           sens:422/cid/m/a  rank:422/cid/m/a  comp:422/cid/m/a  thre:422/cid/m/a
  assumption unit          sens:422/cid/m/a  rank:422/cid/m/a  comp:422/cid/m/a  thre:422/cid/m/a
  named set name           sens:422/cid/m/a  rank:422/cid/m/a  comp:422/cid/m/a  thre:422/cid/m/a
  response_metric          sens:422/cid/m/a  rank:422/cid/m/a  comp:422/cid/m/a  thre:422/cid/m/a
  => crashes=0/32  non-422=0/32
```

(`cid` = `X-Correlation-ID` present; `m` = the pair is in `STATUS_STATE_MATRIX`; `a` = the response
body is pure ASCII; no row shows `ECHO`, i.e. the offending string is never reflected.)

My own earlier 36-case hostile matrix (`p5_raise.py`) re-run at this SHA: **0/36 unhandled raises**
(was 6/36); the six surrogate cases are now `422 validation_error`.

*Methodology note, stated because it matters for trusting the numbers:* my first attempt at this
matrix double-escaped the backslash and therefore tested the literal 6-character text `\ud800`
rather than a surrogate — it reported a misleading 32/32 "200". I caught it via an echo column in
the probe output, corrected the construction, and added in-probe assertions
(`json.dumps({"x": S}).encode("ascii") == b'{"x": "\\ud800"}'` and
`ord(json.loads(...)["x"]) == 0xD800`) so the wire bytes are proven before any conclusion is drawn.
All figures above are from the corrected run.

### 3.3 The fix is precise, not a blanket ban (no over-rejection)

| Input | Result |
|---|---|
| U+D800, U+DBFF, U+DC00, U+DFFF (all four surrogate-range extremes) | 422 `validation_error` |
| a **valid surrogate pair** spelled as two escapes, `"😀"` (😀) | **200** |
| `é中😀`, Cyrillic, `’`, smart quotes, em dash — values, keys, names and echoed rationales | 200, strict-JSON-safe, surrogate-free, round-tripped intact |

So the predicate really is "not encodable text", not "contains an escape" and not "non-ASCII".

### 3.4 Independent RED/GREEN proof that the new tests are load-bearing

Run with a pytest plugin loaded from my temp dir that patches the module in memory after collection
(the repository is never modified); selected with `-k`, never `--deselect`:

| Neutralized | Command | Result |
|---|---|---|
| nothing (GREEN) | `-k surrogate` | **33 passed** |
| encodability check **and** the aligned pre-send guard | `RED_MODE=surrogate … -p redplugin -k surrogate` | **33 failed, 0 passed** |
| fact-key scan restricted to depth 1 (pre-rework semantics) | `RED_MODE=factdepth … -k "fact or nested or verified_claim"` | **26 failed, 17 passed** — the 17 survivors are exactly the top-level cases |
| `_guarded_analysis`'s `except Exception` removed | `RED_MODE=guard … -k "as4 or engine"` | **5 failed, 14 passed** — the 5 are the engine-raise / finish-stage-defect tests |

This confirms the producer's RED/GREEN claim shape independently, and additionally shows the
fact-depth tests discriminate between top-level and nested enforcement rather than passing for
either.

### 3.5 Residual paths I checked around the fix

- **Engine-produced** (not caller-supplied) surrogate: simulated by replacing an engine with one
  that returns `{"engine_emitted": "\ud800"}` → `500 application/json state=internal_contract_error`
  with a correlation id, in-matrix. The aligned guard catches it, as designed.
- **Engine that raises** (all four): `500 application/json state=internal_error`, cid present,
  in-matrix, and `"hostile"` / `"secret-internal-path"` / `Traceback` / `File "` all absent from the
  body.
- **Rejection happens before any I/O:** with landmine fetcher/substrate seams installed, the
  surrogate, nested-fact and oversized-string bodies all return 422 and neither seam is invoked.
- **No residue:** a legitimate request immediately after a surrogate 422, a nested-fact 422, and a
  40,000-level parser `RecursionError` 422 each returns 200 with the correct canonical cap.
- **The 422 body reflects no caller text:** `detail.rejected_keys` is the intersection with the
  server's own `FORBIDDEN_FACT_KEYS` frozenset, so only server-defined names can ever appear; the
  planted value `1000000000` is absent from the response, and the error names no JSON path (good —
  it gives the caller the reason without echoing their structure).
- **Precedence preserved:** for `{"cap":1,"values":[{"coverage":1}],"deep":"x"*5000}` the reported
  error is still the top-level fact key (`rejected_keys:["cap"]`), as the docstring claims.

### 3.6 Re-run of the wider probe set at this SHA

| Probe | Result |
|---|---|
| Seeded fuzz, 1,200 bodies (same seed 20260909) | `{(422,"validation_error"): 777, (200,None): 423}` — **0 unhandled raises, 0 off-matrix pairs, 0 missing correlation ids, 0 non-JSON-safe 200s, 0 `' at 0x'`/path/traceback leaks.** (The 403→777 shift in 422s is the expected consequence of at-any-depth fact-key rejection: the fuzzer's key pool contains forbidden keys.) |
| Seeded fuzz with surrogate strings, 400 bodies | `{(422,…): 275, (200,None): 125}`, same four zeros |
| Flag off (unset/``""``/`0`/`false`/`off`/`maybe`), POST real vs unmounted, 4 endpoints | 404 both, **body byte-identical, header set identical**, no `X-Correlation-ID` |
| OpenAPI with flag on and off | no scenario path; `sensitivity` / `scenario_analysis` appear nowhere in the spec |
| Byte-cap boundary 65,536 / 65,537 | 422 / 422 (`exceeds the maximum of 65536 bytes`) |
| Nesting 31 / 32 / 33 / 64 / 500 / 5,000 / 20,000 / 60,000 | 200 / 422 / 422 / 422 / 422 / 422 (parser) / 422 (parser) / 422 (size) — no `RecursionError`, no hang, no residue |
| NaN / Infinity / 1e400 / 1e308 / 4300-digit int / 4301-digit int / bools / nulls / non-list containers | unchanged: typed 200 or 422; no NaN/Inf/ZeroDivisionError in any response |
| Client-supplied `X-Correlation-ID: attacker\r\nX-Injected: 1` | ignored; fresh server uuid4; no injected header (no CRLF vector) |
| Content types (form, XML, truncated, trailing garbage, latin-1, gzip, array/scalar/null/string, BOM, `text/plain`, absent) | unchanged from `aafc75fd` (see L-5) |

## 4. NEW defects introduced by the rework: **none found**

I looked specifically for regressions the broader walk could introduce:

- **False positives against the route's own vocabulary:** `FORBIDDEN_FACT_KEYS` has no intersection
  with any legitimate parameter name (`variable`, `values`, `objective`, `assumption_sets`,
  `domain`, `target`, `response_metric`, `name`, `assumptions`) or the assumption schema (`key`,
  `assumption_type`, `value`, `unit`, `rationale`). The 312-test suite, which includes at-cap
  legitimate bodies, is green.
- **Cost of the per-dict-node set comprehension:** a dict-heavy at-cap body (22,318 B, **1,281 dict
  nodes**, 256 candidates) returns 200 in a 463 ms median — in line with the other 256-candidate
  shapes, no super-linear behaviour. Trivial-request median 255 ms vs 251 ms at `aafc75fd` (noise).
- **Walk bail-out:** the same 22 KB body with one top-level fact key returns 422 in **9.8 ms**, i.e.
  the walk stops at the first violation and never pays the ~250 ms rebuild.
- **Unguarded `_json` call sites that remain:** `_not_found`, `_validation_error`, and the
  connector-error response built inside `_rebuild_scenario`'s `except` block are still outside a
  guard. These are safe, and I verified why rather than assuming: their strings are server-fixed
  constants, the server's own frozenset names, or upstream text already decoded with
  `errors="replace"` (`resilience/transport.py::_bounded_read`), and the BBL arrives through
  Starlette's `unquote(..., errors="replace")` — confirmed by probing `%ED%A0%80` and `%80%81` BBLs
  on all four new routes plus the three accepted ones: every one returns a clean typed 422. No
  surrogate can reach those paths. Noted for the record, not as a finding.
- **Docstring/comment honesty:** the module docstring, the `FORBIDDEN_FACT_KEYS` comment and
  `_finish`'s docstring were all updated to describe the new behaviour; I found no stale claim in
  the *code*.

Two **report-only** (not code) staleness items, LOW and non-blocking:
`M5-T012-producer-report.md:53` still says "A **top-level** body key … is REJECTED" (§9 describes
the at-any-depth fix correctly), and the caps table at `:67` still reads "checked on raw bytes
BEFORE parsing" — accurate but incomplete; "before parsing, after buffering" is the honest wording,
and §"Explicitly carried as backlog" does document the buffering. Worth a one-line correction each
so the evidence record cannot be read as contradicting itself.

## 5. Ruling 1 — is the deliberately broader rejection right?

**Ruling: yes. Keep it. Do not narrow it.** The broader rule is the more secure and the more
maintainable of the two, and it rejects nothing legitimate.

1. **"A field this endpoint never reads" is not a stable property, and the producer's own RED run
   proves it.** 28 of 33 RED positions returned **200** — the hostile string was *silently dropped*
   because that endpoint happens not to read that field today. Which fields are read differs per
   endpoint (`values` vs `domain` vs `assumption_sets`), and which fields are *echoed* is decided
   inside the engines (`ranking` passes raw values to `derive`, `comparison` sanitizes first). A
   narrow rule would be a per-endpoint, per-engine allowlist that must be re-derived every time an
   engine changes what it echoes — and the day it drifts, those 28 silent drops become 28 crashes
   again. The whole-body predicate cannot rot that way.
2. **Validate-then-use beats use-then-discover.** One total, documented predicate over the parsed
   body, evaluated before any engine and before any I/O (verified: landmine seams are never
   invoked), is auditable in a single read. That is precisely what the original defect lacked.
3. **Nothing legitimate is rejected.** An unpaired surrogate is not text: it cannot be encoded to
   UTF-8, stored, rendered, or round-tripped through any UTF-8 channel. No caller needs to send one
   in a read field or an unread one. Measured precision (§3.3): all four surrogate extremes
   rejected; a *valid* surrogate pair (😀) accepted; full non-ASCII accepted and round-tripped.
4. **Rejecting is more honest than ignoring.** A 422 naming the reason tells the caller their
   parameter was wrong. Silently dropping it risks a caller believing an analysis honored input it
   discarded — in a domain where the whole point is that a number's provenance is legible, the
   silent-drop behaviour is the worse failure mode.
5. **It costs nothing.** The walk already visits every node for depth and length, so the checks are
   O(1) per node; measured at-cap latency is unchanged and hostile bodies now bail ~25× faster than
   a full request.

One forward-looking caveat to record, not a defect: the *fact-key* half of the broader rule is a
behavioural change visible to legitimate callers — a body that merely uses a forbidden name as a
dict key anywhere (say a caller labelling their own nested metadata `{"coverage": …}`) is now a 422
where it used to be a 200. There is no consumer today (the Compare UI M5-T004 is parked and the flag
is off everywhere), so there is no compatibility cost. If a future client genuinely needs free-form
metadata, the right answer is one explicitly-scoped, documented passthrough key excluded from the
fact scan — **not** loosening the walk, and never excluding it from the *encodability* scan.

## 6. Ruling 2 — does the boundary code still sit coherently, or should it move?

**Ruling: it sits coherently; keep it in one module now — and extract the boundary *as a unit*
(validator **plus** the pre-send encodability check) the moment a fifth endpoint or a second body
shape arrives.** Splitting it today would make the code less safe, not more.

Measured facts:

| Metric | Value |
|---|---|
| Tool SLOC (non-blank, non-comment) | 666 — over `WARN_SLOC` 600, **under** `JUSTIFY_SLOC` 750, far under `HARD_SLOC` 1000 |
| Of which docstring lines | ~140 (21% of counted SLOC) |
| Actual executable lines | ~526 |
| Total / blank / comment | 808 / 91 / 51 |
| Largest function | `_rebuild_scenario` 101 lines — the *trusted rebuild mirror*, not the new boundary |
| Whole untrusted-body boundary | 166 lines across 6 named single-purpose helpers (`_fact_injection_error` 10, `_string_boundary_error` 25, `_structural_error` 37, `_prepare_request` 59, `_candidate_domain_cap_error` 12, `_assumption_sets_cap_error` 23) |
| modularity_check | failures 0, EXIT 0; one `review_signal` warning ("a signal, not a verdict") |

Reasoning:

1. **The security argument points *against* splitting right now.** The defect I found was a
   disagreement between two places that each decided "what is serializable" — `_finish`'s
   `json.dumps` and Starlette's renderer. The fix makes the boundary validator and the pre-send
   check agree. Moving the validator into another module increases the distance between those two
   halves and adds an import seam across which a future change can update one side only. The single
   refactor that would re-open exactly my BLOCKING-1 class of bug is "extract the validation, leave
   `_finish` behind." Co-location is what currently makes the invariant checkable in one read, along
   with the cap constants, `FORBIDDEN_FACT_KEYS` and `STATUS_STATE_MATRIX` that must stay mutually
   consistent.
2. **The module is still one responsibility**: adapt an untrusted request into a trusted engine call
   and back. The boundary is the first half of that responsibility, already factored into small,
   individually-auditable helpers with no cross-talk.
3. **The growth is mostly explanation, not complexity.** 21% of the counted SLOC is docstrings, and
   the added prose is precisely the reasoning about the surrogate/encoder mismatch that a future
   maintainer needs in order not to reintroduce it. Penalising that prose via a line metric would be
   the wrong incentive; the real complexity delta is ~40 executable lines in two tiny helpers.
4. **The warning is about the next change, and I agree with it as such.** My recommended trigger:
   when a fifth endpoint or a second untrusted body shape lands, extract the caps,
   `FORBIDDEN_FACT_KEYS`, `_string_boundary_error`, `_structural_error`, `_prepare_request` **and**
   the `_finish` pre-send encodability assertion together into one shared
   `app/api/v1/_untrusted_body.py` usable by every future body-accepting route — so the validator
   and the renderer-agreement check move as a single unit and can never drift apart. Until then the
   file has 84 SLOC of headroom before a cohesion justification is even required.

## 7. Restated: the no-authentication containment finding (unchanged, and the most important item for future exposure)

**The service has no authentication of any kind** (`app/main.py` module docstring; M0-T007/T008
blocked on the owner's Supabase credential). For these four endpoints the *only* containment is the
`INTERNAL_SCENARIO_ENABLED` feature flag.

1. **The flag is genuinely fail-safe and is off in every deployed environment.**
   `internal_scenario_enabled()` returns True only for `{1,true,yes,on}` after strip/lower; unset,
   empty and unrecognized tokens are off. `INTERNAL_SCENARIO_ENABLED` is **not declared anywhere in
   `render.yaml`** or any CI workflow — it appears only under `services/api/app/`,
   `services/api/tests/` and `project-control/`. Re-verified at this SHA: flag off ⇒ a generic 404
   byte-identical to an unmounted path, body not even read (0.1 MiB peak on a 20 MB body), neither
   injected seam invoked.
2. **Flag reuse couples two very different surfaces.** The packet required reusing the existing flag,
   so the one token that enables the accepted **body-less, read-only GET** scenario route also
   enables **four POST endpoints that parse an untrusted body**. Anyone who sets
   `INTERNAL_SCENARIO_ENABLED=1` to demo or debug the GET route simultaneously exposes the whole
   untrusted-body surface. That is a consequence of the packet's design instruction, not a producer
   error — but it changes what that flag means and must be recorded wherever the flag is documented.
   Post-rework this is materially safer than it was: the body boundary now fails closed on
   unencodable text, fact keys at any depth, and every documented cap, and every raise path is typed.
3. **My judgement, updated:** flag gating is now *adequate interim* containment for this surface —
   the reachable unhandled-exception path that made me say otherwise at `aafc75fd` is gone. It is
   **not** a substitute for authentication, and two properties will still be live the moment the
   service is exposed:
   - **no rate or size limiting** — an anonymous (later: any authenticated) caller can spend ~0.4 s
     of server CPU and draw ~0.9 MB per ~2 KB request (M-3), and can drive memory proportional to
     whatever it uploads before the 64 KiB cap applies (M-2);
   - **no per-caller attribution** — the correlation id is per-request, so there is nothing to
     throttle or ban on.
   **When auth lands, these endpoints need a rate/size limit, not only an identity check** —
   authentication bounds *who* can amplify, not *how much*.
4. The existing M1-T005 G5 condition stands and I re-affirm it: the service must not be publicly
   exposed until the auth/organization layer lands. Flipping this flag in any environment reachable
   from outside the operator's own machine should remain a deliberate, reviewed act.

## 8. Carried backlog — has my view hardened? (No.)

Per the coordinator's instruction these are not re-raised as blocking. My severity view is unchanged
on all five; two points are worth recording:

- **M-2 (full-body buffering before the 64 KiB cap)** — re-measured identical (20 MB → 20.1 MiB
  peak, then 422). Still MEDIUM. Correctly scoped as backlog: the clean fix is a `Content-Length`
  pre-check plus a streaming read with early abort, which is middleware-shaped work. Mitigating
  facts re-confirmed: flag-off requests never read the body, and a malformed BBL is rejected before
  the read.
- **M-3 (×437 output amplification, caller-controlled CPU)** — re-measured identical:
  trivial 51 B → 5,852 B / 255 ms; 256 floats 2,097 B → 847,466 B / 412 ms; 256 × 29-deep
  16,174 B → 775,266 B / 690 ms; threshold 256 2,118 B → **925,029 B** / 426 ms. Still MEDIUM, and
  **slightly improved** by this rework: fact-key and surrogate bodies now bail in ~10 ms instead of
  paying the ~250 ms rebuild, so the malformed-traffic amplification surface shrank. The ~250 ms
  floor is the inherited server-side rebuild, not new work.
- **L-1 / L-2 (405 oracle, timing delta)** — unchanged and still identical on the accepted
  M5-T003/M4-T005 routes; correctly recorded as posture-wide rather than packet defects. The
  producer report now acknowledges the 405 behaviour explicitly, which is the right disposition.
- **L-3 (raw-BBL reflection)** — unchanged; lives in a forbidden path (`app/connectors/bbl.py`),
  shared with the accepted routes. Backlog alongside SEC-L1.
- **L-5 (`Content-Type` unenforced)** — unchanged. Still LOW: read-only endpoints, no cookies or
  credentials to ride on, strict parse. Revisit when CORS origins are populated, since a
  `text/plain` POST is a CORS simple request and skips preflight.

## 9. Bottom line

**PASS at `12fda82f`.** The one BLOCKING defect is fixed at the right layer, with both halves
(boundary rejection *and* encoder-agreement), verified by my own 32-combination matrix, a
1,600-case fuzz, a three-way RED/GREEN neutralization proof, and precision controls showing no
over-rejection. HIGH-1 and MEDIUM-1 are fixed and verified; L-4 is fixed. No new defect. The
remaining items are the coordinator's recorded backlog, and the no-auth containment conditions in §7
must travel with this surface to whoever eventually exposes it.
