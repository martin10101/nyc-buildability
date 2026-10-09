# M5-T012 — G3 QA re-attestation (independent)

**Gate:** G3 (QA / acceptance-test adequacy) — re-review of the gate-wave rework
**Reviewed SHA:** `12fda82f3f237f2432efc99614c903496a8b2e02` (branch `candidate/D-024-mrl-option-b`)
**Previous review:** `project-control/reports/M5-T012-G3.md` at `aafc75fd` (left intact)
**Reviewer:** qa-engineer (independent gate; read-only)
**Reviewed:** 2026-09-09

---

## 1. Verdict

**PASS.**

All seven coverage holes I found at `aafc75fd` are genuinely closed. I re-ran the producer's claimed
mutation matrix myself rather than accepting the table: **21 of 21 mutations CAUGHT, 0 survived**,
matching the producer's claim exactly. The 96 added tests are substantive, not padding — the new
cardinality, literal-cap, at-boundary, nested-fact and surrogate tests are the specific shape needed
to make each defect visible, and every typed rejection now asserts `state` as well as status.

I then attacked the **new** tests with fresh mutations and found **five residual gaps** (four
mutations that still survive, plus one reachable-but-untested 200 body). None is an unmet acceptance
scenario, none re-opens a closed finding, and all are cheap to close. They are recorded as **required
corrections, non-blocking for this gate** — except that **R-1 needs a decision, not just a test**,
because it is the pack's own invariant that is violable rather than a missing assertion.

Most valuable new finding (**R-1**): an untrusted caller can get the exact string `"verified"` echoed
into a 200 analysis body as an assumption-set name, and the pack's own `assert_nothing_is_verified`
helper **would fail** on that response — but no test exercises it. See section 6.

---

## 2. Counts I personally observed at `12fda82f`

```
$ git rev-parse HEAD
12fda82f3f237f2432efc99614c903496a8b2e02

$ python -m pytest services/api/tests/api
312 passed in 36.95s                                 (141 pre-existing + 171 new)

$ python -m pytest services/api/tests/scenario
388 passed in 3.88s                                  (unchanged, 0 regression)

$ python -m pytest services/api/tests/api/test_scenario_analysis_api.py
171 passed in 22.00s                                 (was 75)

$ python -m pytest services/api/tests/api -k "not scenario_analysis"
141 passed, 171 deselected in 17.36s                 (pre-existing files untouched)

$ python tools/modularity_check.py --check
exit 0 — "selected 366 files; failures 0; warnings 16"
  warn review_signal: services/api/app/api/v1/scenario_analysis.py

$ cd services/api && python -m ruff check app/api/v1/scenario_analysis.py app/main.py \
      tests/api/test_scenario_analysis_api.py
All checks passed!   (ruff 0.13.0, exit 0)
```

Determinism: the pack run 3x back-to-back with `-p no:cacheprovider` -> `171 passed` in 21.30s /
21.52s / 21.33s. No flake, no order dependence.

Delta scope: `git diff --stat aafc75fd..12fda82f` -> 3 files, 1093 insertions / 125 deletions, all
inside `allowed_paths`. I verified independently that
`git diff --name-only aafc75fd..12fda82f -- services/api/app/main.py services/api/app/config.py
services/api/app/scenario/` returns **nothing** — `main.py`, `config.py` and every `app/scenario/**`
module are byte-unchanged, as claimed.

---

## 3. Re-run mutation matrix — the producer's 21 claims, independently reproduced

Method unchanged from the first review: apply one deliberate defect to an out-of-repo scratch copy,
run the full 171-test pack, revert in a `finally:`. **"CAUGHT" = at least one test went RED.**

| # | Mutation | Result | Tests RED |
|---|---|---|---|
| C1a | sensitivity `values` -> `None` | **CAUGHT** | 4 (`as1_endpoint[sensitivity]`, `as1_result_cardinality[sensitivity-2/3/7]`) |
| C1b | ranking `assumption_sets` -> `None` | **CAUGHT** | 4 |
| C1c | comparison `assumption_sets` -> `None` | **CAUGHT** | 7 |
| C1d | threshold `domain` -> `None` | **CAUGHT** | 6 |
| C2 | assumption-set cap emits `(422,"too_many_sets")` | **CAUGHT** | 3 |
| C3 | envelope gains `verified: True` + `verification_status: "verified"` | **CAUGHT** | 9 |
| C4 | `MAX_BODY_BYTES` check deleted entirely | **CAUGHT** | 2 (`as5_oversized_body`, `as5_body_byte_cap_is_exact`) |
| C5a | `MAX_BODY_BYTES` 64 KiB -> 256 KiB | **CAUGHT** | 2 (incl. `as5_documented_caps_are_the_literal_values`) |
| C5b | `MAX_CANDIDATE_DOMAIN_LENGTH` 256 -> 1024 | **CAUGHT** | 1 |
| C6a | off-by-one `>` -> `>=` body bytes | **CAUGHT** | 1 |
| C6b | off-by-one nesting depth | **CAUGHT** | 1 |
| C6c | off-by-one string length | **CAUGHT** | 1 |
| C6d | off-by-one assumption sets | **CAUGHT** | 2 |
| C6e | off-by-one candidate domain | **CAUGHT** | 2 |
| C6f | off-by-one assumptions per set | **CAUGHT** | 1 |
| C7 | `main.py` registers the analysis router FIRST | **CAUGHT** | 1 (`as7_analysis_routes_are_registered_last_and_in_order`) |
| C9 | threshold default response metric POINT -> MAX | **CAUGHT** | 1 |
| B1a | revert the surrogate/encodability check | **CAUGHT** | **33** |
| B1b | revert `_finish` to `ensure_ascii=True` | **CAUGHT** | 1 (`as6_unencodable_engine_result...`) |
| B2 | revert the nested fact guard to top-level only | **CAUGHT** | **26** |
| B3 | revert the `_guarded_analysis` try/except | **CAUGHT** | 5 (all four endpoints + the `_finish` half) |

**21 applied, 21 caught, 0 survived.** The producer's table is accurate.

Two results worth singling out because they prove the two biggest new test blocks are load-bearing
rather than decorative: reverting the encodability check turns **33** tests RED (the 32 surrogate
cases plus the "tiny body" proof), and reverting the nested-fact walk to top-level-only turns **26**
RED (24 parametrised cases plus the whole-frozenset test plus the G1 regression test). Neither block
is padding.

---

## 4. Is each of C1–C7 / C9 genuinely closed?

| Finding | Closed? | How I verified it, beyond the mutation |
|---|---|---|
| **C1** (HIGH) engine args not load-bearing | **Yes, with a residual** | `CARDINALITY` asserts `result[count_field] == len(body[request_key])` in the AS-1 envelope test *and* in a dedicated test at three counts (2/3/7) per endpoint, so a hardcoded or defaulted count cannot satisfy it. Residual: only small counts are pinned — see **R-2**. |
| **C2** undocumented pair on the cap path | **Yes** | `test_as5_assumption_set_caps` now asserts `state == "validation_error"` on both halves; the at-boundary variants assert it too. |
| **C3** never-Verified checked only on `coverage_status` | **Yes** | `_walk_envelope` + `assert_nothing_is_verified` scan every node at every depth. I stress-tested the shape separately — section 5. Residual: which responses the scan is *applied to* — see **R-3**. |
| **C4** byte cap not isolated | **Yes** | The oversized body is now `["q"*100] * 1200` (many short strings in an uncapped field) and asserts `"bytes" in payload["message"]`, so no other cap can fire in its place. Deleting the cap now fails 2 tests. |
| **C5** caps self-referential | **Yes** | `test_as5_documented_caps_are_the_literal_values` pins all six literals. Both loosening mutations fail it. |
| **C6** no cap tested at exactly N | **Yes** | Six at-boundary tests with byte-exact builders. I verified the builders are honest: `body_of_exact_size(n)` asserts its own length internally, and I confirmed at-cap requests really do reach a 200 with **full** cardinality (`point_count: 256` at the 256 cap; `candidate_count: 50` at the 50 cap), so the at-cap leg is a real acceptance, not an accidental one. |
| **C7** registration order unpinned | **Yes** | `test_as7_analysis_routes_are_registered_last_and_in_order` pins both the order of the four analysis paths and that all three pre-existing routes precede them. Reordering `main.py` now fails it. |
| **C9** threshold default unexercised | **Yes** | Asserts the defaulted case resolves to `usable_range_point` *and* equals `ThresholdResponseMetric.USABLE_RANGE_POINT.value`, plus an explicit non-default case so the value cannot be hardcoded downstream. |

Every one of C1–C7/C9 is closed. C1 and C3 each carry a narrow residual (R-2, R-3) that does not
re-open the original finding.

---

## 5. The C3 verification-claim shape — asked to confirm it cannot be fooled

The producer's design: keys in `VERIFICATION_CLAIM_KEYS` (`verified`, `is_verified`,
`verification`, `verification_status`) must **deny** verification (`value in (False, None)`), and no
string value anywhere may equal `"verified"` after `.strip().lower()`.

**The shape is right, and for a reason stronger than the producer stated.** I confirmed the domain
discovery and the constraint that forces the design:

* The accepted engine marker is real and I located it exactly: a genuine threshold 200 carries
  `$.result.crossing.illustrative_bracket_midpoint.verified = False`. So forbidding the key outright
  would have broken accepted M5-T011 behaviour, and the claim-key branch of the scan is **genuinely
  exercised by a real response body** — not dead code waiting on a hypothetical.
* `NOT_VERIFIED_DISCLAIMER` literally begins `"DRAFT scenario - not a Verified determination. ..."`.
  A substring scan for `"verified"` is therefore **impossible** — it would fail on the canonical
  disclaimer the pack simultaneously requires to be present. Exact-equality on the whole string value
  is not laziness; it is the only workable shape. This is worth recording because it also bounds what
  any value-based scan can ever catch (see R-5).

Fooling attempts, each run as a mutation of `_finish`:

| Injected into the envelope | Caught? | Correct? |
|---|---|---|
| `verified: True` + `verification_status: "verified"` | **CAUGHT** (9 tests) | yes |
| `verified: "false"` (string) | **CAUGHT** | yes — fails closed on a non-boolean denial |
| `verified: []` | **CAUGHT** | yes — fails closed |
| `is_verified: True` buried at `$.result.audit.nested[0]` | **CAUGHT** (9 tests) | yes — depth is no escape |
| `coverage_status: "verified"` / any `"Verified"` string | **CAUGHT** | yes — `.strip().lower()` handles case and padding |
| `verified: 0` | **SURVIVED** | **yes, correctly.** `0 == False` in Python, so `0 in (False, None)` is True. `0` *denies* verification, so passing is the right answer, not a hole. |
| `determination: "VERIFIED BY DOB"` (free prose, key not in the set) | **SURVIVED** | inherent limit — see **R-5** |

**Conclusion: the check cannot be fooled into accepting a claim.** Every truthy value fails; the only
values that pass are `False`, `None`, `0`, `0.0` — all denials. It errs toward failing closed on
ambiguous non-booleans. The only way past it is free prose under a key nobody enumerated, which no
value-equality scan can catch while the canonical disclaimer itself contains the word.

---

## 6. Are the 96 new tests specific, or vacuous? — and the residual gaps

Applying the same lens that found the status-without-state gap last time.

**Specific, and better than required:**

* **33 surrogate cases** — each asserts status 422, `content-type: application/json`, `state ==
  "validation_error"`, `"surrogate" in message`, a present `X-Correlation-ID`, that the pair is a
  member of `STATUS_STATE_MATRIX`, and that no `Traceback` appears. That is six assertions per case,
  each of which a plausible regression would break differently. The companion
  `test_as5_surrogate_body_is_tiny_and_under_every_cap` pre-empts the obvious objection by proving
  the hostile body is <32 bytes and under every cap, so only encodability can reject it — this is the
  C4 lesson (isolate the boundary under test) applied unprompted. And the two positive tests
  (legitimate accents/CJK/astral emoji/smart quotes still 200, plus non-ASCII text round-tripping
  into the response body) guard the *other* direction, which a lazier fix would have broken.
* **24 nested-fact cases** — assert 422, `state`, that `detail["rejected_keys"]` names the offending
  key, a correlation id, and matrix membership; across all four endpoints. Reinforced by
  `test_as2_every_forbidden_fact_key_is_rejected_nested_too`, which walks the **whole**
  `FORBIDDEN_FACT_KEYS` frozenset (closing my old C8) and asserts `rejected_keys == [fact_key]`
  exactly, and by `test_as2_nested_verified_claim_never_reaches_a_200_body`, which asserts the forged
  cap value `987654321` appears **nowhere** in the response text. That last one is the right shape: it
  tests the consequence, not just the status code.
* **At-boundary tests** — byte-exact builders that assert their own arithmetic
  (`body_of_exact_size` raises if it mis-builds), N accepted and N+1 rejected with `state` asserted,
  and landmined seams on the rejection leg proving it happens before any I/O.
* **500-guard tests** — assert `content-type` is JSON (i.e. *not* Starlette's `text/plain`), the
  typed `state`, matrix membership, `correlation_id == X-Correlation-ID`, and that the planted
  hostile string, `"hostile"`, `"secret-internal-path"` and `"Traceback"` are all absent.

### Residual gaps (new findings)

**R-1 — MEDIUM — an untrusted caller can put the literal token `"verified"` into a 200 body, and the
pack's own invariant would FAIL there, but no test runs it.**
Probing the shipped code: `POST /scenario/comparison` with
`{"assumption_sets": [{"name": "baseline", "assumptions": []}, {"name": "verified", "assumptions": []}]}`
returns **200**, and the caller's string is echoed at `$.result.sets[1].name`. Running the pack's own
`assert_nothing_is_verified` on that response **fails**:
`AssertionError: a 'verified' status value at $.result.sets[1].name`.
The fact-key guard rejects forbidden *keys* at any depth, but a forbidden *status string* supplied as
a caller **value** is echoed verbatim. In substance AS-6 still holds — `coverage_status` is
`conditional`, `scenario_kind` is `preliminary`, the disclaimer is present, and the path makes the
string visibly caller-supplied — so this is not a forged fact and not a verdict-changing defect. But
the suite asserts an invariant that an untrusted caller can falsify on an untested path, which must
not be left standing. Two honest resolutions, and this needs a **decision**, not just a test:
(a) extend the untrusted-input boundary to reject a caller string that *is* a verification status —
symmetric with `FORBIDDEN_FACT_KEYS` and more consistent with "assumptions yes, facts never"; or
(b) narrow the invariant to exempt caller-echoed label paths and document why.
**Important:** this is why R-3's fix must not be applied naively — see there.

**R-2 — MEDIUM — C1's cardinality guard is pinned only at small counts, so silent truncation of a
large request survives.** Two mutations still ship green on all 171 tests:
* truncating the caller's candidate domain to 128 before the engine
  (`services/api/app/api/v1/scenario_analysis.py:672-674`);
* truncating `assumption_sets` to 25 (`:713-715`).
`test_as1_result_cardinality_tracks_the_request` uses counts 2/3/7, and the at-cap boundary tests
(256 candidates, 50 sets) assert only `status_code == 200`. A later "performance guard" that clamped
a large domain would therefore be invisible — exactly the C1 defect class, just above the tested
range. *Minimal fix, and it is free:* in `test_as5_candidate_domain_length_cap`,
`test_as5_assumption_set_count_cap_is_exact_at_the_boundary` and
`test_as5_assumptions_per_set_cap_is_exact_at_the_boundary`, assert the cardinality on the at-cap
200 leg as well as the status. I confirmed the expected values hold today (`point_count == 256`,
`candidate_count == 50`), and the engine work is already being done, so this costs no runtime.

**R-3 — LOW/MEDIUM — the never-Verified scan is applied to only 9 of the pack's many 200 responses.**
`assert_nothing_is_verified` is invoked at three call sites only (lines 529, 703, 1244). It is **not**
run on the `no_scenario` 200 envelope, nor on the NaN/Inf, non-ASCII, or at-cap 200s. Consequence: a
mutation adding `verified: True` **only** on the `no_scenario` path survives all 171 tests — and the
no-scenario / professional-review outcome is arguably where a spurious verification claim would do
the most harm, since it is the response for a property the system is declining to analyse. I
confirmed the `no_scenario` envelope passes the scan today, so adding
`assert_nothing_is_verified(envelope)` to `test_as4_no_scenario_is_a_normal_200_typed_result`
(line 755) is safe and closes it in one line. *Do not* blanket-apply the scan to every 200 until R-1
is decided — applying it to a caller-echoed response would surface R-1 as a failure.

**R-4 — LOW — the at-cap 200 legs assert status only.** The generic form of R-2: six at-boundary
tests establish "N is accepted" purely as `status_code == 200`. Accepted-and-correct is the property
that matters; asserting the result kind (and per R-2 the count) on the accept leg makes these tests
prove acceptance rather than mere non-rejection.

**R-5 — LOW, inherent — a verification claim in free prose under an unenumerated key is not
catchable by this scan.** `{"determination": "VERIFIED BY DOB"}` survives. As established in
section 5, exact-equality is forced by the canonical disclaimer containing "not a Verified
determination", so this residual cannot be closed by tightening the string comparison. If it is ever
worth closing, the only workable shape is a word-boundary regex plus an explicit allowlist of the
canonical disclaimer/label strings. I would **document the limit rather than chase it** — the engines'
prose is gated elsewhere, and an allowlist-based scan is a maintenance burden that fails noisily.

No other new hole: I found nothing vacuous in the surrogate or nested-fact blocks, and the 500-guard,
literal-cap, registration-order and default-metric tests are each minimal and load-bearing.

---

## 7. The two questions put to me

**Modularity — is a split needed?** `modularity_check --check` is `failures 0`, exit 0, with a new
`warn review_signal` for `scenario_analysis.py`. My QA read of the numbers: the file is 807 lines, of
which **136 are multi-line docstrings and 51 are comments** — roughly **530 lines of actual code**
across 22 top-level definitions, four of which are the near-identical endpoint handlers. The WARN
crossing is therefore driven mostly by the explanatory prose this very gate wave demanded (the
surrogate and nested-fact rationales, the `_guarded_analysis` asymmetry note). Cohesion has not
degraded: it is still one responsibility — adapt an untrusted request onto a trusted rebuild and an
accepted engine — with one validation walk. **I would not split it on this evidence**, and I would be
wary of a split that moved the validation walk away from the route it defends. G1/G5 own the call;
this is my input, not a finding.

**Runtime — 25s -> 36s, fair trade?** **Fair; do not trim.** But the attributed cause is not what the
data shows. `--durations=12` on the pack: the slowest single test is 0.76s
(`test_as4_every_emitted_pair_is_in_the_matrix`), and the at-cap boundary tests the slowdown was
attributed to cost only 0.43s / 0.42s / 0.31s / 0.29s — the twelve slowest tests together are ~5.1s
of 21.5s. The real driver is **test count** (75 -> 171): each test pays a fixed per-request cost to
rebuild the profile, rule evaluation and scenario through the injected seams, so ~171 x ~0.12s
dominates. Trimming the at-cap tests would recover roughly 1.5s while deleting the only thing that
catches the six C6 off-by-ones — a bad trade. If anyone insists on trimming, the cheapest honest
saving is parametrisation breadth where the product has a single shared enforcement path: all 32
surrogate cases and all 24 nested-fact cases flow through the same `_prepare_request` ->
`_structural_error` walk, so the x4 endpoint fan-out is largely redundant. I would still keep it: the
fan-out is what would catch a future fifth endpoint that forgets to call `_prepare_request`, and 36s
for a 312-test suite is not a problem worth paying coverage for.

---

## 8. Worktree left byte-identical

I wrote exactly one file: this report. `M5-T012-G3.md` is untouched.

* `git rev-parse HEAD` before and after: `12fda82f3f237f2432efc99614c903496a8b2e02`.
* sha256 of the three files under review, diffed against the fingerprint taken before I began —
  **identical**:
  * `services/api/tests/api/test_scenario_analysis_api.py`
    `4d984114be1a06cb42313532241e4e0e2ecf245170111f480c8b2725895542b7`
  * `services/api/app/api/v1/scenario_analysis.py`
    `0b10d508d29db77cc584e0451ce9d3986952de4059b973b3e87050256c602d07`
  * `services/api/app/main.py`
    `c0dcac8c8f2af0f2585cc2a0aa10d3035174c0459583368f92cfdab2a93ad317`
* All 29 mutations (21 re-runs + 8 new hole-hunting mutations) and all behavioural probes were
  applied to a **fresh** out-of-repo scratch copy of `services/api` taken at `12fda82f`, reverted in
  a `finally:` block, with the scratch tree re-verified green (`171 passed`) before use.
* No `git` write command, no `tools/project_control.py`, no commit, stash or push; nothing installed.
* Independence: I re-derived every number here from my own runs. I read the producer's rework section
  only to enumerate the 21 claims I was asked to reproduce, and I did not read the G1, G4, G5 or DCV
  reports — the three BLOCKING fixes were re-tested from the code, not from their write-ups.
