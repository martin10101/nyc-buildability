# M5-T013 — G1 independent code review, RE-REVIEW after rework

**Verdict: PASS** (BLOCKING-1 and HIGH-1 both resolved; 2 carried-forward LOW + 3 new LOW, none blocking)

- **Reviewed SHA:** `209b9548a18fa45f27c5b87f4af7989939645d81` (branch `candidate/D-024-mrl-option-b`), confirmed with `git rev-parse HEAD`.
- **Previous verdict:** FAIL at `29ca7bca` — see `project-control/reports/M5-T013-G1.md`, left intact as the record of that gate.
- **Delta reviewed:** `git diff 29ca7bca..209b9548` — 3 files, 749 insertions / 128 deletions, all inside `allowed_paths`.
- **Independence:** I am the same independent G1 reviewer and am **not** the producer. I wrote no product or test code and fixed nothing; this report and `M5-T013-G1.md` are the only files I have written. All repository commands were read-only. My mutation plugin and probe scripts live **outside** the repository under the session scratchpad and patch only in-memory module attributes; no repository file was modified at any point. Every conclusion below is my own reproduction — I did not accept a figure from the producer report or from the coordinator's summary.

---

## 1. Scope and measurements

```
$ git diff --name-only 29ca7bca..209b9548 -- services/api/app/main.py services/api/app/config.py \
    services/api/app/profile/ services/api/app/rules/ services/api/app/scenario/ \
    services/api/app/api/v1/properties.py services/api/app/api/v1/rule_evaluation.py \
    services/api/app/api/v1/scenario.py services/api/app/api/v1/scenario_analysis.py \
    packages/contracts/ apps/web/ supabase/ tools/ services/api/tests/scenario/
[EMPTY]                      # main.py byte-unchanged; every forbidden path clean

$ git diff --name-only 9a84d392..209b9548      # whole branch since the packet
project-control/reports/M5-T013-producer-report.md
services/api/app/api/v1/evidence.py
services/api/app/main.py
services/api/tests/api/test_evidence_api.py
```

```
$ python -m pytest services/api/tests/api                                     371 passed in 10.31s
$ python -m pytest services/api/tests/api/test_evidence_api.py                 59 passed in  2.34s
$ python -m pytest services/api/tests/api --ignore=.../test_evidence_api.py   312 passed in  8.81s
$ python -m pytest services/api/tests/scenario                                388 passed in  1.08s
$ python tools/modularity_check.py --check          failures 0 ; EXIT 0
    warnings naming "evidence": only tools/agent_supervisor/evidence.py (sloc 603, pre-existing)
    app/api/v1/evidence.py warned: False
$ modularity_check.source_lines(app/api/v1/evidence.py)   ->  418   (warn 600, justify 750, hard 1000)
$ (cd services/api && ruff check app/api/v1/evidence.py app/main.py tests/api/test_evidence_api.py)
    All checks passed!
$ (cd services/api && ruff check .)                 Found 27 errors   [pre-existing baseline, unmoved]
```

Every figure the coordinator reported is confirmed: 371 = 312 pre-existing **unchanged** + 59 evidence (was 37), 388 scenario, failures 0 with no warning naming the route module, 418 SLOC, lint clean on the owned files with the pre-existing 27 unmoved.

---

## 2. My BLOCKING-1 (silent projection dropped 18 contract fields) — **RESOLVED**

The fix is the one I specified: each citation group is `{**copy.deepcopy(trace), "claim_verification_status": …}` (`evidence.py:337-348`), `source_coverage` is a wholesale deep copy of the root (`:372-376`), `evaluated_input` is the whole sub-document (`:380`). The hand-picked key lists are gone, not supplemented.

**Re-measured against my own original counts (root 14/20, trace 7/19):**

```
ROOT:            source keys 20 | represented 20 | MISSING []
TRACE:           source keys 19 | evidence keys 20 | MISSING []
                 extra key (must be exactly the server-authored one): ['claim_verification_status']
EVALUATED_INPUT: 4 vs 4 | MISSING []
```

**The 12 trace qualification fields and the 6 root fields I named are all present AND byte-equal** (`all 12 present and byte-equal: True`; `my 6 named root fields present and byte-equal: True`). Spot-checks of the material that was previously suppressed:

```
exceptions_applied[0].description: "A higher maximum residential FAR (up to 2.00 for R5/R5A/R5B per ZR 23-21) applies to zoning lot…"
computation_steps[1]: {"step_id":"floor_area","op":"multiply","resolved_args":[10000.0,1.5],"result":15000.0,
                       "note":"Maximum residential floor area = lot area (sq ft) x FAR."}
cap still verbatim: 15000.0 == 15000.0
```

The qualified figure is now presented **with** its qualifications: the conditional higher-FAR exception, the documented per-dwelling-unit limitation, the "NOT an evidence-based determination" note, the derivation with both factors, `rule_release` (`verified_eligible: false`), `effective_window`, and the root district / lot area / lot-area source / spatial context / spatial uncertainty. Values are deep-copied, not aliased.

I also re-checked for any transformation introduced by the rework: the only `str()` / `.strip()` / `.lower()` calls in the module remain at `:237` (`_verification_status`, the case-insensitive comparison AS-7 requires) and `:245` / `:263` (classification locals). No transported value is transformed; there is no `round(`, no f-string building a material value, no `sorted(` or `.sort(` over citations, and no slicing or joining of a transported value.

### Ruling on `source_field_routing` — **approve as shipped**

**(a) The map is honest.** Exactly two entries, and both destinations really hold the content:

```
source_field_routing = {"evaluations": "rule_citations", "evaluated_input": "evaluated_input"}
  'evaluations'     -> 'rule_citations':   destination is a top-level key: True | non-empty: True
  'evaluated_input' -> 'evaluated_input':  destination is a top-level key: True | non-empty: True
  'evaluations' content really in rule_citations: True
  'evaluated_input' content really at root:      True
  map size is exactly 2: True      deep copy, not an alias: True
```

Combined with root key-set equality (20/20), nothing is excluded at all today — the map describes relocation only, which is exactly what it claims.

**(b) It cannot become a loophole.** I tested the attack directly — parking a real field in the map with a plausible-sounding destination:

```
G1_MUT=park:zoning_district  ->  2 failed, 57 passed
    FAILED test_as1_document_carries_every_source_contract_field
    FAILED test_as1_the_qualifications_that_make_the_cap_honest_travel_with_it
```

The mechanism is sound. `test_as1_document_carries_every_source_contract_field` pins the map with **exact literal equality** — `assert routing == {"evaluations": "rule_citations", "evaluated_input": "evaluated_input"}` — then asserts each destination exists in the document, then asserts root key-set equality *both* against the app's own bundled `rule_evaluation.schema.json` (`ROOT_REQUIRED`) *and* against the live rebuilt document, plus per-trace key-set equality with `strict=True`. A field therefore cannot be parked silently: doing so requires editing a literal assertion, which is a visible, deliberate act in the diff. The packet's rule — a genuine exclusion must carry a reason visible to the caller — is satisfied, and the routing entry is itself emitted in the response.

One forward-looking note (LOW-3 below): the map's values are destination keys with no slot for a *reason*, while the comment at `:156-163` promises that a genuinely excluded field "belongs here with a documented reason". No exclusion exists today, so nothing is wrong now; if one is ever needed the shape should become `{source_key: {"location": …, "reason": …}}` with the test literal updated, rather than overloading the destination string.

### Independent mutation battery — I re-ran it myself rather than trusting the table

15 mutations of my own design, injected in-memory from the scratchpad, each run against the producer's 59-test pack:

| mutation | result |
|---|---|
| *(baseline, none)* | 59 passed |
| `drop_root:zoning_district` — **single-field drop** | **2 failed** |
| `drop_trace:exceptions_applied` — **single-field drop** | **2 failed** |
| `drop_trace:computation_steps` | 2 failed |
| `drop_trace:rule_release` | 3 failed |
| `drop_trace:notes` | 2 failed |
| `drop_eval_input:input_fingerprint` | 2 failed |
| `park:zoning_district` (routing-map loophole) | 2 failed |
| `stringify_cap` (cap to `"15000.0"`) | 2 failed |
| `perturb_cap` (cap + 0.5) | 2 failed |
| `strip_quote` (truncate a citation quote) | 2 failed |
| `drop_one_provenance` | 1 failed |
| `round_cap` (`15000.0` to `15000`) | **59 passed — survived** |
| `reorder_citations` | 59 passed — **vacuous** |
| `titlecase_section` | 59 passed — **vacuous** |
| `drop_gap_detail` | 59 passed — **mis-targeted by me** |

The two single-field drops the coordinator asked me to verify personally — `zoning_district` and `exceptions_applied` — **both fail**, each caught by `test_as1_document_carries_every_source_contract_field` and `test_as1_the_qualifications_that_make_the_cap_honest_travel_with_it`. The assertion that holds BLOCKING-1 shut is genuinely load-bearing.

I checked every survivor for vacuity rather than reporting it as a hole:

- `reorder_citations` — the fixture yields **one** citation per group, so reversing the list is a no-op. Vacuous, not a barrier failure.
- `titlecase_section` — the only section value is `'23-21'`, and `'23-21'.title() == '23-21'`. Vacuous.
- `drop_gap_detail` — no gap carries a `detail` on this fixture (`rule_conflict` is null there), and the conflict tests bind `assemble_evidence_document` / `_gap_markers` by direct import (test file lines 48-50), so my module-attribute patch never reached them. **Mis-targeted by me, not a barrier hole** — a real code edit is caught, as section 3 shows.
- `round_cap` — **genuine survivor**, reported as LOW-4 with an exact bound.

---

## 3. My HIGH-1 (`rule_conflict` dropped; `_gap_markers` had no branch) — **RESOLVED**

The marker is at `evidence.py:285-300`: `{kind: "data_conflict", subject: "rule_conflict", reason: conflict.get("note"), detail: copy.deepcopy(conflict)}`, additive to the generic posture markers. `rule_conflict` is *also* now carried verbatim inside `source_coverage` by the BLOCKING-1 fix, so it is doubly present.

**First I confirmed the trigger against the real contract** — the thing the producer could not exercise live. `$defs/rule_conflict` has `required: ['as_of_date','competing_output_names','competing_rules','conflict','family','note']` with `additionalProperties: false`, and `app/rules/registry.py:92-112` builds it with `"conflict": True` plus that note. So `isinstance(conflict, dict) and conflict.get("conflict")` is a correct, reliable gate and `conflict.get("note")` is the real note — not a guessed key.

**Then I went further than the producer and drove a live conflict through the entire HTTP route**, injecting a schema-valid `rule_conflict` at the serializer seam so the route's own `validate_rule_evaluation_document` had to accept it and the real renderer produced the response:

```
injected rule_conflict PASSES the canonical rule_evaluation schema: True
HTTP status: 200 | cid: True
rule_conflict gap marker present: True
  kind   : data_conflict
  reason : "multiple same-family rules are simultaneously in effect and independently applicable to the sam…"
  detail byte-equal to the source object: True
  names the competing rule ids: ['zr_23_21_r5_far', 'zr_23_21_r5_far_alt']
  carries each rule's effective window: [('2024-12-05', None), ('2025-06-01', None)]
generic posture markers ALSO still present (additive): ['coverage', 'rule_conflict']
rule_conflict ALSO carried verbatim in source_coverage: True
response strict-JSON-safe under BOTH dumps: True
```

A reviewer is now told *which* rules compete, over which outputs, and over which effective windows — exactly the gap I raised.

**Ruling on evidence adequacy: the producer's direct pure-function assertion is adequate, and no fixture-backed path is required.** `_gap_markers` is a pure function of the rebuilt document; its trigger matches the real contract (verified above); and `test_as1_rule_conflict_gets_its_own_gap_marker_naming_the_competing_rules` asserts the full `marker["detail"] == _CONFLICT`, the competing rule ids, `detail is not _CONFLICT` (deep copy, no alias), and that the generic markers still fire. That is a complete regression barrier for this behaviour, and my end-to-end run independently confirms it composes correctly through the route, the schema validator and the renderer. One LOW recommendation (LOW-5): promote one conflict assertion to the HTTP path so the route-level pack covers it too — the absence of any route-level conflict document is precisely why my `drop_gap_detail` probe found nothing to bite on.

---

## 4. My MEDIUM-2 (AS-1 test overclaimed its name) — **RESOLVED**

The overclaiming test was renamed to `test_as1_deterministic_provenance_and_citations_transport_byte_equal`, and the guarantee is now carried by assertions rather than by a name: key-set equality driven off the app's **own bundled** schema (so a field added to the source contract and then dropped also fails — I confirmed the test reads `ROOT_REQUIRED` / `TRACE_REQUIRED` / `EVALUATED_INPUT_REQUIRED` from it), whole-subtree equality with an aliasing check, and a `_stable_view` whole-document comparison with exactly one volatile leaf masked. My battery confirms the barrier bites on single-field drops, on the routing-map loophole, on a stringified cap, on a perturbed cap, on a truncated quote and on a dropped provenance record.

---

## 5. Zero regression in what I had already passed

I re-ran my full posture sweep at `209b9548`; every result is identical to `29ca7bca`:

- **AS-3 body-less** — handler params `['bbl','fetcher','substrate_provider']`; no `Request`, `request.body`, `request.json`, `Query(`, `Body(`, `query_params` or `await`; a body-carrying GET returns a byte-identical response; POST/PUT/DELETE give 405. (The query-string response differing is again only the per-request `observation_id`, which differs between two *plain* requests too; the `"999"` present is coincidental digits inside digests, present in the plain response as well.)
- **AS-4 flag posture** — all 8 non-true values give `404 {"detail":"Not Found"}`, indistinguishable from an unmounted path in body *and* header set, with no `X-Correlation-ID`; OpenAPI byte-identical off vs on; `/evidence` absent from it.
- **AS-5 matrix** — 9 pairs; `== accepted scenario-route matrix`; `== properties − {(500,'unsupported_contract_version')}`; subset of properties; extra `[]`, unused `[]`.
- **AS-6 guards** — raises forced in all three stages plus `_assert_json_safe` each give a typed `application/json` 500 with a correlation id and an in-matrix state, with no leak of the filesystem path, token, env-var name, traceback or exception class I planted. Both dumps still enforced: NaN, Infinity **and an unpaired surrogate** in the assembled document each give `(500, internal_contract_error)`.
- **AS-7** — unchanged and correct.

---

## 6. Findings

| # | Sev | Status | Summary |
|---|---|---|---|
| BLOCKING-1 | — | **RESOLVED** | Whole-trail transport: root 20/20, trace 19/19 (+1 server-authored key), evaluated_input 4/4, all byte-equal. |
| HIGH-1 | — | **RESOLVED** | `rule_conflict` marker verified end-to-end through the HTTP route, naming competing rule ids and effective windows. |
| MEDIUM-2 | — | **RESOLVED** | Barrier is now schema-driven key-set equality; verified load-bearing on single-field drops. |
| MEDIUM-1 | MEDIUM | **backlog, view unchanged** | Rebuild chain still duplicated (`build_property_profile` in 5 modules). The rework correctly did **not** edit a fifth copy. My view has not hardened: it needs its own extraction task, and touching it here would have been out of scope. |
| LOW-1 | LOW | carried forward | `_gap_markers` still emits a `.strip().lower()`-normalised echo of `coverage_status` as the `reason` on three markers (`:281`, `:303`, `:312`). Benign (the canonical vocabulary is already lowercase) and non-blocking. Worth noting that the **new** conflict marker uses `conflict.get("note")` verbatim with a deep-copied `detail` — the better discipline; the three older sites were simply not revisited. |
| LOW-2 | LOW | carried forward | `evidence.py:270` still aliases `fail_safe_reason` by reference while the same value is deep-copied into `source_coverage`. Harmless for a read-only response, inconsistent with the module's otherwise-uniform deepcopy discipline. |
| LOW-3 | LOW | **new** | `_RELOCATED_SOURCE_FIELDS` values are destination keys with no slot for a reason, while the comment at `:156-163` promises a documented reason for a genuine exclusion. No exclusion exists today, so nothing is wrong now; if one is ever needed the map should carry `{"location": …, "reason": …}`. |
| LOW-4 | LOW | **new** | The barrier's "byte-equality" is `==` **value**-equality, so a numeric *type*-narrowing of a legal value survives the whole 59-test pack: `round(15000.0)` to `15000` passes (`15000 == 15000.0` is True, though `json.dumps` differs: `15000` vs `15000.0`). Bounded precisely by my own probes — **value drift is caught** (`cap + 0.5` gives 2 failed; `str(cap)` gives 2 failed); only `==`-preserving type drift is not. Closure: compare `json.dumps(..., sort_keys=True)` of the subtrees, or assert `type(...)` on the cap. |
| LOW-5 | LOW | **new (coverage)** | The fixture yields **one** citation per group and a section of `'23-21'`, so no test can currently detect citation **re-ordering** or a `.title()` of a section reference — two transformation classes the packet names explicitly. Neither is a live defect (I confirmed the module does no sorting and no case transformation of a transported value), but the barrier has no teeth there. A fixture with two or more citations per group, plus one conflict document driven through the HTTP path, would close this and the sibling gap noted in section 3. |

### Ruling on renaming `source_coverage`

**Do not rename at this gate.** The producer's judgement was right. It is cosmetic; accepted AS-5/AS-7 assertions address that key; and the contents are now unambiguous and *machine*-verifiable from the response itself (`source_field_routing` plus root key-set equality), which is a stronger remedy than a better name. Against that, renaming a response key is a consumer-visible change to a versioned document that deserves its own change with the `EVIDENCE_CONTRACT_VERSION` implications considered deliberately — not a drive-by edit during a re-gate, where it would also make this diff harder to audit. Put it in the backlog next to MEDIUM-1 (a name such as `source_rule_evaluation` would fit what it now carries), to be taken with the version bump.

---

## 7. Verdict

**PASS at `209b9548`.** Both of my findings are resolved in the product and, more importantly, each is now held shut by an assertion I verified is load-bearing through my own mutation testing — including the two single-field drops that represent the realistic future regression. `source_field_routing` is honest and cannot become a silent loophole, because the map is pinned by exact literal equality and parking a field fails two tests. The `rule_conflict` marker is correct against the real contract shape, and I confirmed it end-to-end through the full HTTP route, which is stronger evidence than the packet required. Nothing I had already passed regressed, and the rework introduced no defect: the five remaining items are LOW, two carried forward and three new, and none blocks acceptance.

Per ADR-005 the reviewer is read-only and does not record gate results: this report is returned to the orchestrator, which records the gate. It and `M5-T013-G1.md` are the only files I have written; `M5-T013-G1.md` is unmodified as the record of the FAIL.
