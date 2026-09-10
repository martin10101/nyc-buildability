# M5-T013 — G5 independent security RE-REVIEW (post-G1-rework)

- **Task:** M5-T013 — evidence / provenance endpoint (`GET /api/v1/properties/{bbl}/evidence`)
- **Re-reviewed SHA:** `209b9548a18fa45f27c5b87f4af7989939645d81` (branch `candidate/D-024-mrl-option-b`),
  confirmed with `git rev-parse HEAD`. Delta reviewed = `29ca7bca..209b9548`.
- **Previous verdict:** PASS at `29ca7bca` (see `M5-T013-G5.md`, left intact)
- **Reviewer:** G5 security-reviewer (independent, read-only)
- **Date:** 2026-09-10

## Verdict: **PASS** at `209b9548`

The G1 fix enlarges the response surface by ~7.9% and replaces hand-picked keys with wholesale deep
copies. I re-ran my entire disclosure battery against the enlarged document and it is **clean on
every axis** — including a seven-canary credential test and an individual scan of each newly
restored subtree. The security property that makes "copy everything" sound rather than reckless is
one I verified rather than assumed: the source contract is **closed** and validated before assembly.
Every AS-6, body-less, matrix and egress property re-confirms. Two LOW items, both about the new
`source_field_routing` mechanism and the contract's open sub-objects; neither blocking.

---

## 0. Independence statement

I am not the producer and wrote no product code, test, or configuration for this task or its rework.
My only repository writes across all three reviews are the report files. Every result below comes
from probes I wrote and ran **outside** the repository (`…/scratchpad/g5t013/`). I did not take the
producer's claims on trust: where the producer asserted a property in a comment (the closed-contract
bound, the non-shadowing of `claim_verification_status`, the serialisation behaviour being unchanged),
I verified it against the bundled schema or by behavioural probe, and I re-ran the RED neutralisation
suite to confirm the tests still fail without each guarantee. `git diff --name-only` confirms
`main.py` byte-unchanged; `git status --short` shows no product file, test, or fixture modified by me.

## 1. Counts observed (all confirm the coordinator's verification)

| Check | Observed | Expected |
|---|---|---|
| `python -m pytest services/api/tests/api` | **371 passed**, 15.08s, exit 0 | 371 (312 + 59 evidence) OK |
| `python -m pytest services/api/tests/scenario` | **388 passed**, 1.28s, exit 0 | 388 OK |
| `python tools/modularity_check.py --check` | **failures 0, EXIT 0**; 367 files, 16 warnings; **0 warnings naming `api/v1/evidence`** | OK |
| module SLOC | **418** (was 410) | 410 -> 418 OK |
| `ruff check` on the three owned files | All checks passed | OK |
| diff scope | 3 files, 749 insertions / 128 deletions, all in `allowed_paths`; **`main.py` absent from the diff**; forbidden paths clean | OK |
| evidence test count | 37 -> **59** | OK |

## 2. Findings

| Severity | # | Finding |
|---|---|---|
| BLOCKING | 0 | — |
| HIGH | 0 | — |
| MEDIUM | 0 | — |
| LOW (new) | 2 | N-1 `source_field_routing`'s omission check is closed only by a pinned test literal, not by a content-reachability invariant, and the response carries no relocation *reason* · N-2 five sub-objects inside the closed source contract are themselves open, so their contents are published unconstrained (clean today; the residual is future content) |
| LOW (carried) | 3 | L-1 / L-2 / L-3 unchanged — inherited from forbidden paths, correctly backlogged; **no view hardened** |
| LOW (closed) | 1 | L-4 closed — confirmed (section 7) |

### N-1 (LOW) — `source_field_routing` is an auditability feature whose omission guard is human-dependent

**Where:** `services/api/app/api/v1/evidence.py:162-168` (`_RELOCATED_SOURCE_FIELDS`), emitted at
`:368` as `source_field_routing`; asserted at
`services/api/tests/api/test_evidence_api.py:418-426`.

See section 5 for the full ruling, the mechanical demonstration, and the recommended fix. In short:
parking a real source field at an existing document key makes it vanish from the response while two
of the three assertions still pass; the only guard that fires is the **exact-equality pin** on the
routing literal. Content-reachability at the declared target is never asserted, and the map carries
a destination key rather than the "documented reason" the module comment promises.

### N-2 (LOW / advisory) — the closed source contract has five open sub-objects

**Where:** `services/api/app/_contract_schemas/v1/rule_evaluation.schema.json` —
`$defs.evaluation_trace.properties.outputs`, `.uncertainty`, `.evaluated_inputs`,
`.applicability_trace.items`, and `$defs.citation.properties.provenance` each omit
`additionalProperties`, so their **contents** are unconstrained by the contract.

**Why it matters now:** the rework publishes these sub-objects verbatim by wholesale deep copy. The
key-level bound I verified (section 4.2) therefore does **not** extend inside them: whatever the
rules engine places in `outputs`, `uncertainty`, `evaluated_inputs`, `applicability_trace[]` or a
citation's `provenance` reaches the caller without any schema gate.

**Exploit scenario:** not exploitable by a caller — this is a future-change risk. A rules-layer change
that adds a debug field inside one of those maps (a resolved file path, a timing, an internal id)
would be published by this endpoint with no contract change and no test failure. I scanned all five
as they stand today and they are clean (section 4.3), carrying only FAR values, derivation steps,
district shares and coverage notes.

**Recommendation (not this packet):** close those sub-objects in `packages/contracts` (a contract
change with its own review), or add the disclosure-pattern scan I run here to the test pack so a
future internal field fails a test rather than shipping. `packages/contracts/**` is a forbidden path
here.

## 3. NEW defects introduced by the rework: **none at product level**

Beyond N-1/N-2 above (a control-strength gap and a contract-shape advisory, neither a runtime
defect), I specifically looked for regressions the wholesale-copy change could introduce:

- **Disclosure-by-default:** addressed — bounded by the closed contract (section 4.2).
- **Key shadowing:** `{**copy.deepcopy(trace), "claim_verification_status": …}` applies the
  server-authored key **after** the spread, so it *would* override a same-named source field. I
  proved the ordering with a synthetic trace carrying `claim_verification_status:
  "SOURCE-SUPPLIED-VALUE"` -> the document emitted `"draft"`, i.e. the source value is lost.
  **Unreachable today, verified against the bundled schema rather than taken from the comment:**
  `claim_verification_status` is absent from `$defs.evaluation_trace.properties` **and** that object
  is `additionalProperties: false`, so a validated trace can never carry the key. The producer's
  comment is accurate. Worth remembering if that contract is ever opened.
- **`_expected_failure`:** the one root key the schema permits but the evaluator never emits (a
  fixture-only annotation, per its own schema description). A wholesale copy would publish it if
  present; confirmed **absent** from the live document.
- **New `rule_conflict` gap marker** (`evidence.py:285-300`) deep-copies the whole competing-rules
  object. Null in the F01 fixture, so I drove it synthetically: clean on all 12 disclosure patterns,
  content is rule ids / versions / effective windows / competing output names, and the copy is not
  aliased to the source object. Its single `token` pattern hit is the phrase "a blanket **token** scan
  is falsifiable" inside the server-authored `verification_scope_note` — a false positive, resolved by
  locating the substring rather than waving it through.
- **Cost/amplification:** re-measured, still inside the accepted ungated benchmark (section 6).

## 4. Disclosure re-run on the enlarged document

The document grew **59,561 B -> 64,262 B (+7.9%, +4.7 KB)**; root keys 13, `source_coverage` 18 keys
(= 20 root required − 2 relocated), each citation group 19 trace keys + 1 server-authored key.

### 4.1 Whole-body pattern scan (probe D1b, re-run)

| Pattern | Result |
|---|---|
| object address `' at 0x'` | clean |
| traceback marker (`Traceback`, `File "`) | clean |
| Windows drive path / POSIX system path | clean |
| repo fragment (`services/api`, `site-packages`, `_zr_snapshots`, `rulesets`, `_contract_schemas`) | clean |
| `.py` filename | clean |
| `.schema.json` / `.snapshot.json` / `.rule.json` | clean |
| credential word (`app_token`, `api_key`, `secret`, `password`, `bearer`) | clean |
| private host (`localhost`, `127.0.0.1`, `.internal`, `svc.cluster`) | clean |
| vendor host (`supabase`, `render.com`, `onrender`, `geoclient`) | clean |
| module dotted path (`app.rules`, `app.connectors`, …) | clean |
| object/function repr | clean |
| username / `Users` | clean |
| env var name | two **false positives** only — the field names `fact_key` and `request_url` match my `_(KEY|URL)` pattern; no actual env var name |

**Identical to the projected-document result.** The enlargement introduced no new disclosure class.

### 4.2 Why wholesale copying is sound here — the closed-contract bound (new verification)

This is the property that decides whether an enlarged surface is safe, so I checked the schema rather
than reasoning from the diff:

```
rule_evaluation.schema.json  $                         additionalProperties=False   21 props / 20 required
                             $defs.evaluation_trace    additionalProperties=False   19 props
                             $defs.evaluated_input      additionalProperties=False    4 props
                             + evaluated_input, spatial_context, spatial_uncertainty, family_coverage,
                               rule_conflict, competing_rule, rule_release, effective_window,
                               determination, input_validation, computation_step, citation: all False
```

and `validate_rule_evaluation_document(rule_evaluation)` runs at `evidence.py:488` **before**
`assemble_evidence_document` at `:497`. So the response's key space is bounded by a closed, validated
canonical schema: a future rules change cannot introduce an undeclared internal field into this
endpoint's output without first amending the canonical contract, which is a `packages/contracts`
change with its own review. That converts "copy everything" from disclosure-by-default into
contract-bounded transport, and it is the structural reason this rework does not widen risk. The one
gap in that bound is N-2 (five open sub-objects).

### 4.3 Each newly carried subtree, scanned individually (probe R1b)

All **clean** on 12 patterns including the URL pattern — so no subtree introduced a URL or host:

```
source_coverage.zoning_district / lot_area_sq_ft / lot_area_source / spatial_context /
spatial_uncertainty / rule_conflict / contract_version                       -> clean
rule_citations[0].rule_release / effective_window / input_validation /
determination / uncertainty / applicability_trace / computation_steps /
evaluated_inputs / exceptions_applied / notes / data_completeness            -> clean
gaps / source_field_routing / evaluated_input                               -> clean
```

Content review of the subtrees most likely to carry an artefact confirms they are evidential, not
internal: `rule_release` = lifecycle/approval states + `verified_eligible: false`;
`effective_window` = ZR effective dates; `computation_steps` = the lot-area x FAR derivation;
`applicability_trace` = the district in-set test and the value seen; `spatial_uncertainty` = district
shares and the coverage note; `input_validation` = `{valid: true, invalid_inputs: []}`.

### 4.4 Seven-canary credential test (probe R1a)

With `SOCRATA_APP_TOKEN`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL` (a fake
`postgres://u:p@h/db`), `GEOCLIENT_SUBSCRIPTION_KEY`, `ANTHROPIC_API_KEY`, `SENTRY_DSN` and
`API_CORS_ALLOWED_ORIGINS` all set to canary values:

```
every canary: value_in_body=False  value_in_headers=False  NAME_in_body=False
any 'CANARY' substring anywhere (body or any header): False      VERDICT: no canary leaked
```

### 4.5 URL inventory and length oracle

```
URLs in the body: exactly 2, unchanged
  https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1000010100
  https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21

length oracle: {'token set': 64262, 'token unset': 64262} -> identical
```

No new URL, host or internal reference entered with the restored fields, and body size still does not
reveal whether a credential is configured.

## 5. Ruling on `source_field_routing`

**Ruling: an auditability feature, and a clear net improvement over the silent projection it
replaced — but its omission guard is a pinned test literal rather than a self-enforcing invariant,
and it does not carry the "reason" its own documentation promises. Keep it; strengthen the assertion.**

### What I demonstrated (probes R2, R3)

Parking a real source field at a document key that **exists**:

```
routing = {... , "fail_safe": "gaps"}
  fail_safe in source_coverage            : False   (18 -> 17 keys)
  fail_safe retrievable at doc["gaps"]    : False   <- the field has effectively disappeared
```

Assertion by assertion, against `test_evidence_api.py:418-426`:

| Assertion | Parked at an existing key | Parked at a missing key |
|---|---|---|
| (1) `routing == {"evaluations": …, "evaluated_input": …}` (exact pin) | **FAILS** | **FAILS** |
| (1) every target key exists in the document | passes | fails |
| (2) `set(source_coverage) \| set(routing) == ROOT_REQUIRED` | passes | passes |
| *not asserted:* the parked field's **content** is reachable at its target | — (False) | — (False) |

RED runs confirm the suite does catch both today: `park_existing` -> 1 failed, `park_missing` ->
1 failed (GREEN 59 passed).

### The judgement

1. **It is genuinely better than what it replaced.** The prior state dropped 18 contract fields with
   no declaration at all. Now every source field is either present or *named in the response*, which a
   consumer can read — that is a real auditability gain, and the right instinct.
2. **But the guard that closes the loophole is the exact-equality pin, not the routing logic.** The
   existence check only proves the destination key exists; the union check is satisfied merely by
   *naming* the field in the map. So the natural way to add a third relocation — add the map entry and
   update the pinned literal in the same commit — would also silently disable the omission check for
   that field, leaving "named in the map + destination key exists" as the whole protection. The
   invariant depends on a reviewer noticing a changed literal.
3. **No reason reaches the caller.** The map's value is a destination key, not a reason
   (`{"evaluations": "rule_citations", "evaluated_input": "evaluated_input"}`); the response contains
   no `reason`/`note`/`why` anywhere in it. The module comment says a genuinely excluded field
   "belongs here with a documented reason", but the structure has nowhere to put one. A caller can see
   **where** a field went, never **why**, and cannot distinguish "relocated" from "parked".
4. **It is not a runtime vulnerability.** Exploiting it requires a maintainer to change product code,
   so this is control strength, not an attack surface — hence LOW, not MEDIUM.

### Recommended fix (cheap, non-blocking)

In the key-set test, assert **content reachability through the map** so the invariant holds
independently of the pin: for each `source_key -> document_key`, check that the document's value at
`document_key` is actually derived from the source value — identity for `evaluated_input`; same length
plus per-element key-superset for `evaluations`; and for any future entry, that the source field's
value is present at the declared target. Optionally make the map's value
`{"destination": …, "reason": …}` so the response carries the reason the docstring promises. The test
pack already performs the equivalent checks for the two real relocations ((3),(4),(5) of the same
test) — they are simply not wired **through** the routing map, which is what leaves the map itself
unguarded.

## 6. Updated amplification and no-auth position

Measured in a single run (cross-round timings are **not** comparable — this machine was ~4x faster
today, the api suite running in 15.08s vs 44.78s last round; the relative position is what matters):

| Surface | Response | Median | Amplification |
|---|---|---|---|
| **evidence (this endpoint, flag-gated)** | **64,262 B** | **58 ms** | **x1004** from a 64 B request |
| accepted `/properties/{bbl}` — **completely ungated** | **74,804 B** | 54 ms | — |
| accepted `/properties/{bbl}/rule-evaluation` (same flag) | 6,505 B | 47 ms | — |
| evidence, flag off | 22 B | 1.31 ms | rebuild never reached |

**My M5-T012 comparison still holds, so the no-auth recommendation is unchanged.** The enlarged
document rose from x930 to x1004, but it is **still smaller than the already-accepted, completely
unauthenticated** `/properties/{bbl}`, and its CPU cost is indistinguishable from its siblings. There
is still **no caller-controlled multiplier** — response size is a function of the property's official
record alone — so M5-T012's M-3 (caller-steered x437 amplification) has no analogue here.

Restated position: containment today is real (flag fail-safe across nine non-true token variants,
byte-identical 404 with no correlation id, not declared in `render.yaml` or any CI workflow, wrong
flag cannot open it). What the endpoint newly exposes is audit value, not secrets — and the rework
*increases* that audit value, which is the point. When auth lands it needs (a) authentication **and**
authorisation with access logging, since a provenance view is exactly where "who looked at this"
matters, and the restored trail now includes rule lifecycle and approval state that is more
reconnaissance-useful than the projected version; (b) a per-caller rate limit shared with the other
property routes, not an endpoint-specific one; (c) nothing body-related — there is still no body,
query parameter or header input. The M1-T005 G5 condition (not publicly exposed until the
auth/organisation layer lands) stands and I re-affirm it.

## 7. Re-confirmation of every other property at the new SHA

| Property | Result |
|---|---|
| **Body-less, structural** | `query_params: []`, `header_params: []`, `cookie_params: []`, `body_params: []`, `body_field: None`, `request_param: None`, `methods: ['GET']`, `include_in_schema: False` — unchanged |
| **Body-less, behavioural** | clean-vs-clean byte-identical after masking only the per-fetch uuid (62,520 B), proving that is the sole volatile; then **full-document identical** across all 11 variants (JSON body with fact keys, 1 MB body, surrogate body, `?bbl=` shadowing, `?verified=true`, duplicate query, `X-Correlation-ID`, `Cookie`, `Authorization`, `Accept: text/html`, `X-Forwarded-*`); injected `1000000000` / `zzqq-canary` / `CANARY_BODY` absent |
| **Nine forced-raise stages** | all **typed JSON 500**, in-matrix, with `X-Correlation-ID`, `leaks=[]` (no `hostile`, `secret-internal-path`, `Traceback`, `File "`): fetch, 6 rebuild steps, assembly -> `internal_error`; `_assert_json_safe` -> `internal_contract_error`; raising substrate provider -> `internal_error` |
| **Hostile content through the seams** | 16 cases all typed and in-matrix: surrogate in a value / in a field name -> `internal_error` (connector digest, `pluto_soda.py:255`); bare NaN / Infinity / 1e400 -> `internal_contract_error` (the new check, end-to-end through the real pipeline); `"NaN"` / `"Infinity"` / `"0"` / `""` / 4300-digit strings -> 200 both forms OK; malformed/empty body -> 503; object-not-array -> 502 |
| **Both `json.dumps` forms load-bearing** | on a real assembled document: surrogate **passes** `allow_nan=False` but **raises** under `ensure_ascii=False` + `.encode("utf-8")`; NaN/Inf raise under both. RED `onlyfirstform` (the exact M5-T012 mistake) -> **1 failed**; RED `jsonsafe` -> **3 failed** |
| **Render raise still inside the guard** | RED with `_assert_json_safe` disabled: surrogate content still returns typed `500 internal_error` with `application/json` + cid — `return _json(200, …)` remains inside the `try` |
| **`STATUS_STATE_MATRIX`** | unchanged (9 pairs); emitted set **equals** the matrix exactly, fully driven, **none beyond**; still no pair the rule-evaluation route does not emit |
| **Egress** | 200 with `egress == []` on all four recording-landmine seams (`pluto_soda._OPENER`, `transport.DEFAULT_OPENER`, `http.client.HTTP(S)Connection.connect`, `socket.create_connection`) |
| **Flag containment** | 404 byte-identical body **and** headers vs an unmounted path for all nine non-true variants, no correlation id; `1/true/TRUE/yes/on/" 1 "` serve; scenario flag on + rule-eval off -> 404; `/openapi.json` byte-identical off vs on with `evidence` absent |
| **Never Verified (AS-7)** | `_verification_status` echoes only a literal verified token (`verified_by_expediter` -> draft, non-strings -> draft); live statuses `['draft','draft']`; disclaimer and scope note present |
| **RED: the G1 projection reintroduced** | -> **3 failed**, so the whole-trail guarantee is regression-protected |
| **RED: `_verification_status` always "verified"** | -> **6 failed** (was 4 at `29ca7bca`) — the suite got stronger |

### Views on the carried LOWs — none hardened

- **L-1** (503 body naming `SOCRATA_APP_TOKEN`): unchanged, still emitted identically by four accepted
  routes from a forbidden path. Correctly backlogged. Severity unchanged — the **value** never leaks,
  re-proved here with seven canaries.
- **L-2** (unbounded raw-BBL reflection, x2.0): unchanged, inherited from `bbl.py`. Correctly backlogged.
- **L-3** (405/404 wrong-method oracle): unchanged, posture-wide. Correctly recorded.
- **L-4 — closed, confirmed.** `_stable_view` is gone; the AS-3 test now compares the whole document
  with exactly one volatile leaf masked. My independent check agrees that is sound: clean-vs-clean is
  byte-identical once the per-fetch uuid is masked, so `observation_id` really is the only differing
  leaf, and the assertion is now the stronger form I recommended.

## 8. Required actions

None blocking. Recommended, none inside this packet's `allowed_paths` except (1):

1. **N-1:** wire the key-set assertion's content check **through** `source_field_routing` so a parked
   field fails regardless of the pinned literal; optionally carry a `reason` alongside each
   destination so the response delivers the documented reason the module comment promises.
2. **N-2:** close `evaluation_trace.outputs` / `.uncertainty` / `.evaluated_inputs` /
   `.applicability_trace.items` and `citation.provenance` in `packages/contracts`, or add a
   disclosure-pattern assertion over those sub-objects to the test pack.
3. Carry forward the three inherited LOWs (L-1, L-2, L-3) as already routed.
4. Previously recommended and still open: one sentence in the `evidence.py` docstring noting that the
   connector digest — not `_assert_json_safe` — is what stops surrogates arriving from the SODA seam
   today, so the two-form check is not mistaken for redundant; and a note in `config.py`'s flag comment
   that the flag now governs two routes.
