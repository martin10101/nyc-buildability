# M5-T012 — G1 independent code review, RE-REVIEW after rework 2

**Verdict: PASS** (both of my findings resolved; 2 MEDIUM + 3 LOW carried forward, none blocking)

- **Reviewed SHA:** `12fda82f3f237f2432efc99614c903496a8b2e02` (branch `candidate/D-024-mrl-option-b`), confirmed with `git rev-parse HEAD`.
- **Previous verdict:** FAIL at `aafc75fd` — see `project-control/reports/M5-T012-G1.md`, left intact as the evidence of that gate.
- **Delta reviewed:** `git diff aafc75fd..12fda82f` — 3 files, 1093 insertions / 125 deletions, all inside `allowed_paths`.
- **Reviewer independence:** I am the same independent G1 reviewer; I am **not** the producer. I wrote no product or test code in this task and fixed nothing — this report and my original `M5-T012-G1.md` are the only files I have written. All repository commands were read-only (`pytest`, `ruff check`, `tools/modularity_check.py --check`, `git diff/log/rev-parse`). Probe scripts live outside the repository under the session scratchpad and only import the app read-only. I re-derived every conclusion below from my own reproductions; I did not accept a claim from the producer report or from the coordinator's summary.

---

## 1. Scope re-verified

```
$ git diff --name-status aafc75fd..12fda82f
M  project-control/reports/M5-T012-producer-report.md
M  services/api/app/api/v1/scenario_analysis.py
M  services/api/tests/api/test_scenario_analysis_api.py

$ git diff --name-only aafc75fd..12fda82f -- services/api/app/main.py services/api/app/config.py \
    services/api/app/scenario/ services/api/app/api/v1/scenario.py services/api/app/api/v1/rule_evaluation.py \
    services/api/app/api/v1/properties.py packages/contracts/ apps/web/ supabase/ tools/ services/api/tests/scenario/
[EMPTY]

$ git diff --name-only c83206c2..12fda82f     # whole branch since the packet was contracted
project-control/reports/M5-T012-producer-report.md
services/api/app/api/v1/scenario_analysis.py
services/api/app/main.py
services/api/tests/api/test_scenario_analysis_api.py
```

`main.py`, `app/config.py` and every `app/scenario/**` module are byte-unchanged by the rework, and the whole-branch diff is still only the four files the packet allows. No forbidden path touched. `internal_scenario_enabled` still reused; no new flag.

## 2. Measurements I personally observed

```
$ python -m pytest services/api/tests/api                                          312 passed in 37.66s
$ python -m pytest services/api/tests/api/test_scenario_analysis_api.py            171 passed in 21.71s
$ python -m pytest services/api/tests/api --ignore=.../test_scenario_analysis_api.py  141 passed in 17.94s
$ python -m pytest services/api/tests/scenario                                     388 passed in 4.33s
$ python tools/modularity_check.py --check    selected 366 files; failures 0; warnings 16   EXIT=0
$ (cd services/api && ruff check app/api/v1/scenario_analysis.py app/main.py tests/api/test_scenario_analysis_api.py)
                                             All checks passed!
$ (cd services/api && ruff check .)          Found 27 errors     [unchanged pre-existing baseline]
```

141 + 171 = 312; the 96 new tests are all in this task's own file (75 → 171). `tests/scenario` unchanged at 388, so the engines are untouched in behaviour as well as in bytes. Owned files still lint-clean; the pre-existing 27-error baseline is unmoved, so no lint regression.

---

## 3. My BLOCKING-1 (nested fact keys) — **RESOLVED**

Implementation: the top-level-only check was **deleted, not duplicated**, and fact-key rejection moved into the single iterative walk (`scenario_analysis.py:338-341`, inside `_structural_error`), with the message and `detail.rejected_keys` shape extracted to `_fact_injection_error` (`:279-288`). Docstrings corrected from "top-level" (`:24-27`, `:148-155`, `:286-290`, `:407-410`).

**My own exact repro from the FAIL report, re-run at `12fda82f`:**

```
POST /api/v1/properties/1000010100/scenario/ranking
{"objective":"maximize_illustrative_usable_area",
 "assumption_sets":[[{"assumption_type":"utilization_factor","value":0.8,
                      "draft_zoning_floor_area_cap_sq_ft":987654321,
                      "coverage_status":"verified","verified":true,
                      "rule_evaluation":{"outputs":{"max_residential_floor_area_sq_ft":987654321}}}]]}

  status: 422 | state: validation_error
  detail: {"rejected_keys":["coverage_status","draft_zoning_floor_area_cap_sq_ft","rule_evaluation","verified"]}
  forged cap 987654321 anywhere in body: False
  X-Correlation-ID: True | pair in STATUS_STATE_MATRIX: True
```

Previously a 200 echoing all of it. All four offending keys are named, the forged cap appears nowhere, and the pair is the documented `(422, "validation_error")`.

**Depth- and shape-independence, verified by me (not sampled from the producer's tests):**

```
nested one level deeper (sets>set>assumption>meta>deeper) -> 422 keys=['coverage_status']
comparison named-dict shape                               -> 422 keys=['draft_zoning_floor_area_cap_sq_ft']
sensitivity values[] carrying a fact dict                 -> 422 keys=['cap']
threshold domain[] carrying a fact dict                   -> 422 keys=['profile']
```

**Whole-set coverage, measured by iterating the live frozenset myself** — a fact key buried inside an assumption dict on `/ranking`, one request per key: **23 / 23 rejected, 0 failures**, each naming exactly that key. (The set has **23** entries, not 24 — see LOW-5.)

**No over-rejection — legitimate nested content still accepted:**

```
sensitivity  -> 200 sensitivity_response                    cap=15000.0
ranking      -> 200 ranked_scenario_assumption_sets         cap=15000.0
comparison   -> 200 scenario_assumption_set_comparison      cap=15000.0
threshold    -> 200 scenario_threshold_crossing             cap=15000.0
rich legit nested set (key/assumption_type/value/unit/rationale/source/tags) -> 200 scorable: [True]
```

**Precedence, message and detail shape unchanged** (the producer's claim, which I checked rather than accepted — the body object is the first node popped, so a top-level key is still reported before any nested or structural violation):

```
top-level multi-key                          -> 422 {'rejected_keys': ['cap','coverage_status']}   (sorted, as before)
top-level fact key + oversized string         -> 422 ['cap']        (fact still wins, as at aafc75fd)
message: "request body may carry only illustrative analysis parameters; it may not supply or overrid…"  (unchanged)
```

I also confirmed the string-boundary messages are byte-identical to the old ones (`"a string value exceeds the maximum length of 4096"` / `"a key exceeds …"`), so extracting `_string_boundary_error` introduced no error-contract drift.

**Test quality.** `test_as2_every_forbidden_fact_key_is_rejected_nested_too` iterates `sorted(FORBIDDEN_FACT_KEYS)` rather than a hardcoded sample, asserts `rejected_keys == [fact_key]` exactly, and runs under landmine seams (proving no fetch) — so a future key added to the set without walk coverage fails the suite. `nested_fact_body` buries the key inside the real assumption dict for ranking/comparison, i.e. it reproduces my attack shape rather than a weaker one. The old `_coverage_values` helper was **replaced, not removed**, by `_walk_envelope` + `assert_nothing_is_verified` (`:461-493`), which is strictly stronger: it scans every node at every depth for any string value equal to `"verified"` and requires every `VERIFICATION_CLAIM_KEYS` entry to be `False`/`None`, where the old helper inspected only `coverage_status` keys. No weakening.

## 4. My HIGH-1 (unguarded engine call) — **RESOLVED**

Implementation: `_guarded_analysis` (`:605-630`) wraps `engine_call()` **and** `_finish` in the same `except Exception → _internal_error_500` guard the rebuild stage uses; all four endpoints route through it with a `lambda` that only defers the call.

**Forced engine raise, all four endpoints (my probe, not the producer's test):**

```
sensitivity engine raises -> 500 state='internal_error' cid=True in_matrix=True
ranking     engine raises -> 500 state='internal_error' cid=True in_matrix=True
comparison  engine raises -> 500 state='internal_error' cid=True in_matrix=True
threshold   engine raises -> 500 state='internal_error' cid=True in_matrix=True
_finish raises            -> 500 state='internal_error' cid=True in_matrix=True
```

Previously `text/plain` `Internal Server Error` with no `state`, no correlation id and a pair outside the matrix. Content-type is now `application/json` on every one, and I scanned each body for `secret`, `Traceback`, `File "`, `token=abc123`, `RuntimeError` — **no leak on any endpoint** (the raise I injected carried `C:\secret\path\leak.py token=abc123`).

**The guard is NOT over-broad — this is the thing I was asked to check hardest, and it holds.** `_finish` still handles its own serialization failure internally and *returns* a response rather than raising, so the distinct `(500, "internal_contract_error")` pair still reaches the client and is not collapsed into the generic pair:

```
engine returns a non-serializable object -> 500 state='internal_contract_error'   (not masked)
engine returns NaN                       -> 500 state='internal_contract_error'   (not masked)
engine returns an unpaired surrogate     -> 500 state='internal_contract_error'   (not masked)
rebuild stage raises                     -> 500 state='internal_error'            (unchanged)
scenario-contract defect                 -> 500 state='internal_contract_error'   (unchanged)
```

So the guard catches only what nothing else types, and the four pre-existing 500 distinctions survive. It catches `Exception`, not `BaseException`, so `KeyboardInterrupt`/`SystemExit` still propagate.

**Test-integrity check (my own, because a broad new guard could silently swallow the landmine assertions the AS-2/AS-3/AS-5 tests depend on):**

```
fact-key 422 under landmine seams            -> 422 validation_error   (no fetch occurred)
valid body under landmine seams              -> 500 internal_error     (fetch WAS reached)
```

The landmines still discriminate, so the "rejected before any I/O" assertions remain load-bearing and were not neutered by the new guard.

**Facade / read-only engine property intact.** All five object identities against `app.scenario` still hold (`analyze_scenario_sensitivity`, `rank_scenario_assumption_sets`, `compare_scenario_assumption_sets`, `find_scenario_threshold`, `NOT_VERIFIED_DISCLAIMER`) — the `lambda` defers the call but still resolves the module globals, so the facade indirection is real, not a wrapper object. `tests/scenario` at 388 passed and a byte-empty `app/scenario/**` diff confirm the engines are still consumed read-only and unmodified. `STATUS_STATE_MATRIX` is still exactly the accepted scenario route's 9 pairs (`== SCENARIO_MATRIX: True`); every pair I produced across ~60 probe requests was a member.

## 5. Combined shape with the G5 surrogate fix — sane, and correctly scoped

I reproduced the G5 BLOCKING at its fix point. The request is 22 pure-ASCII bytes (`{"variable": "\ud800"}`), previously an untyped `text/plain` 500:

```
sensitivity / ranking / comparison / threshold (top-level value) -> 422 validation_error  cid=True  in_matrix=True
surrogate as a dict KEY                                          -> 422 validation_error
surrogate nested in values[]                                     -> 422 validation_error
surrogate inside an assumption rationale                         -> 422 validation_error
surrogate PAIR (valid astral char \ud83d\ude00)                   -> 200   (correctly NOT rejected)
legitimate non-ASCII ("café 中文 😀")                              -> 200   (correctly NOT rejected)
```

The encodability check is precisely scoped — it rejects only genuinely unencodable text and does not ban non-ASCII. The two halves of the fix are consistent with each other and with my HIGH-1 fix: `_finish` now proves the envelope with the renderer's own settings (`ensure_ascii=False` + `.encode("utf-8")`), `UnicodeEncodeError` subclasses `ValueError` so it maps to the existing `(500, "internal_contract_error")` handler (verified above: an engine-returned surrogate yields exactly that pair), and anything the boundary and `_finish` both miss would now land in `_guarded_analysis`'s typed 500 rather than escaping as plain text. Defence is layered, not duplicated, and no layer masks another.

## 6. No regression in anything I verified at the previous SHA

```
16 hostile bodies re-run: all 200/422, strict-JSON-safe, X-Correlation-ID present, no " at 0x" leak  -> True
NaN / Infinity / -Infinity / 1e400 tokens -> 200, strict re-dump OK
nesting 31 -> 200 | 32 -> 422 | 33 -> 422 | 600 -> 422          (cap boundary still exact)
flag OFF: POST analysis -> 404 {"detail":"Not Found"} ; unmounted POST -> 404 {"detail":"Not Found"}
  byte-identical: True | no X-Correlation-ID on the disabled 404: True
```

---

## 7. SLOC ruling (the new item)

**Ruling: acceptable with the recorded justification. No split is required for acceptance. I recommend the split as a separate follow-up task, with one condition attached.**

Measured independently with the checker's own metric:

```
$ python tools/modularity_check.py --check --json
thresholds: {'warn': 600, 'justify': 750, 'hard': 1000, 'symbol_ceiling': 40}
WARN: {"kind":"review_signal","path":"services/api/app/api/v1/scenario_analysis.py","sloc":666,
       "note":"above the warning threshold; consider the module boundary before growing it further"}
failures 0 ; EXIT 0
```

666 SLOC, exactly as disclosed (572 → 666). Reasons this is acceptable:

1. **The machine gate passes by its own definition.** I read `tools/modularity_check.py:413-440`: this file is not in `baseline` (it is new on this branch, not grandfathered), so the only failure mode in its branch is `new_oversized` at `sloc > HARD_SLOC` (1000). At 666 it emits a report-only `review_signal`. No baseline or exception file needs editing — which matters, because both live under `tools/**`, a forbidden path.
2. **The policy requires a justification only above 750.** `docs/CODE_MODULARITY_POLICY.md:51-52` defines Warning 600 as "new modules should normally stay below this; checker reports" and Justification 750 as the band that "requires an explicit cohesion justification recorded in review". Line 20 states line count "is a warning signal, never by itself proof that architecture is [wrong]", and lines 167-168 are explicit that "a file crossing the justification threshold with ONE responsibility and a recorded justification is healthier than a forced split". 666 sits in the band whose own instruction is "consider the module boundary before growing it further" — which the producer did, in writing, and named the seam.
3. **The responsibility genuinely did not change, and I checked this rather than taking it on trust.** I read the whole module at both SHAs. It is still one route-adapter: flag gate → correlation id → untrusted-body boundary → server-side rebuild over injected seams → facade engine call → envelope. No domain logic, no legal calculation, no storage, no serialization format. The +94 is three boundary helpers the gate itself demanded (`_fact_injection_error`, `_string_boundary_error`, `_guarded_analysis`) plus the rationale prose for them. 18 top-level symbols against a ceiling of 40.
4. **Forcing the split inside this packet would be worse.** It needs a new file, which busts `allowed_paths` — so the options were: break scope, or trim the explanations to get back under an advisory line. Shrinking reviewer-facing rationale to game a counter is the wrong trade, and the producer correctly refused it and disclosed the crossing instead, self-correcting its own earlier "well under the warn threshold" wording. I would have failed a silent crossing; a disclosed one with a named seam is what the policy asks for.

**Condition I attach:** the natural seam is the one named — the untrusted-body boundary (`_prepare_request`, `_structural_error`, `_string_boundary_error`, `_fact_injection_error`, the cap helpers and the cap constants) into a sibling input module, preserving the public names through the existing facade. The file is 84 SLOC from the justification band and the checker's note is "before growing it further", so **the next change that materially grows this module should perform that split first** rather than add to it. Recommend the orchestrator open that as a follow-up task now, while the seam is fresh, rather than waiting for the 750 trigger.

---

## 8. Findings carried forward and new (none blocking)

| # | Sev | Status | Summary |
|---|---|---|---|
| MEDIUM-1 | MEDIUM | **open, inherited** | Flag OFF, `GET`/`PUT` on an analysis path returns 405 while an unmounted sibling returns 404, so the four names are enumerable while disabled. Re-confirmed at `12fda82f` (`GET -> 405`). Identical on the accepted M5-T003 route (`POST /scenario -> 405`), so not a regression and, as at the first gate, **not gate-failing**. Fix belongs to a follow-up spanning both routes. |
| MEDIUM-2 | MEDIUM | **open** | `MAX_BODY_BYTES` still enforced after `await request.body()` buffers everything (`:322-323`); no `content-length` pre-check, no body-limit middleware. Re-confirmed: an 8 MiB body is fully read, then 422 in 0.02 s. Unauthenticated edge; memory amplification only. |
| LOW-1 | LOW | **open** | `_rebuild_scenario` still duplicates ~75 lines of `app/api/v1/scenario.py` (forced — forbidden path). Drift risk; extract a shared rebuild helper in a follow-up. |
| LOW-2 | LOW | **open, not addressed** | `/ranking` needs **bare-list** entries while `/comparison` accepts named dicts; `post_ranking`'s docstring (`:691`) is still one line and documents neither, and `_assumption_sets_cap_error` handles both shapes, implying both work. Behaviour stays honest and fail-closed (a named dict yields a not-scorable candidate, no fabricated score) — one docstring line closes it. |
| LOW-3 | LOW | **new (supersedes old LOW-3)** | The bare string `"verified"` can still reach a 200 body as a caller's own value — under a **case-variant** key (`{"Coverage_Status":"verified"}`) or under a **legitimate** engine field (`rationale`/`unit`/`value` equal to `"verified"`). I verified all four cases: 200, echoed under `$.result.candidates[0].assumption_set[0].*`, and the producer's own `assert_nothing_is_verified` **fails** on each if applied. Crucially, in every case the authoritative fields are intact (`coverage_status=conditional`, `cap=15000.0`, disclaimer present) and **no canonical fact key is forgeable** — which is why this is LOW and not a reopening of BLOCKING-1: `FORBIDDEN_FACT_KEYS` is exact-match lowercase, so a case variant is not the canonical key any machine consumer reads, and a free-text value is not a fact claim. It does mean the test's invariant ("no string value anywhere may be `verified`") is stricter than anything the product enforces for arbitrary input. Closure options: add a case-insensitive key comparison at the boundary, or narrow the documented AS-6 claim to canonical keys and authoritative fields so product and test agree. **Do not** ban the word in free-text rationale — that would be a worse contract than the residual. |
| LOW-4 | LOW | **new, cosmetic** | `FORBIDDEN_FACT_KEYS` holds **23** keys; the producer report says "all 24 keys" (`:150`) and "0/24 → 24/24" (`:452-453`). The test iterates the live frozenset, so coverage is genuinely complete (I measured 23/23) — only the prose count is wrong. |
| INFO | — | inherited | Non-200 bodies (connector-error payloads, `no_match` 404) are not passed through `_finish`'s renderer-matched serialization proof, so a hostile **upstream** string carrying a `\ud800` escape would still reach the renderer unchecked. Not caller-reachable (no caller string is echoed unsanitized into an error body: the BBL echo is `repr()`-sanitized and `rejected_keys` are the module's own constants), and the accepted M5-T003 route shares the exposure verbatim. Recorded for the backlog; explicitly **not** a finding against this packet. |
| INFO | — | explanatory | The string `verified` does appear in a fact-injection **422** body — as a rejected *key name* inside `detail.rejected_keys`. That is the module naming the offence from its own constant, not a verification claim, and `assert_nothing_is_verified` is applied only to 200 envelopes (it also requires `not_verified_disclaimer`, which error bodies do not carry). Not a defect. |

---

## 9. Verdict

**PASS at `12fda82f`.** Both findings from my FAIL are resolved in the product, verified by my own reproductions rather than the producer's reports: the nested-fact-key vector is closed at every depth across all 23 keys and all four endpoints with no over-rejection of legitimate content and no change to the documented precedence, message or `detail` shape; and the analysis stage is now inside the same typed generic-500 guard as the rebuild stage on all four endpoints plus `_finish`, without masking the `internal_contract_error` pair, without breaking the facade's read-only engine property, and without neutering the landmine assertions the offline/no-I/O tests rest on. The G5 surrogate fix composes correctly with mine. No defect was introduced by the rework; the residuals above are LOW/MEDIUM and none blocks acceptance. The 666-SLOC crossing is acceptable on the recorded justification, with the split recommended as a follow-up task and required before this module is grown further.

Per ADR-005 the reviewer is read-only and does not record gate results: this report is returned to the orchestrator, which records the gate. It and `M5-T012-G1.md` are the only files I have written; `M5-T012-G1.md` is left unmodified as the record of the FAIL.
