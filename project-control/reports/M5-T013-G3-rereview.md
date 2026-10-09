# M5-T013 — G3 QA re-attestation (independent)

**Gate:** G3 (QA / acceptance-test adequacy) — re-review of the gate-wave rework
**Reviewed SHA:** `209b9548a18fa45f27c5b87f4af7989939645d81` (branch `candidate/D-024-mrl-option-b`)
**Previous review:** `project-control/reports/M5-T013-G3.md` at `29ca7bca` (left intact)
**Reviewer:** qa-engineer (independent gate; read-only)
**Reviewed:** 2026-09-10

---

## 1. Verdict

**PASS.**

All five blocking findings (H-1..H-5) are genuinely closed. I re-ran my own matrix rather than
accepting the producer's table: **37 mutations applied, 30 caught, 7 survived** — and every one of
the seven original H-1 survivors is now caught, as are the two single-field drops
(`zoning_district`, `exceptions_applied`) that this gate was specifically asked to probe, plus a
third I added (`computation_steps`). The H-1 closure is not cosmetic: the mechanism changed from
hand-picked re-keying to wholesale deep copy in the product, and from hand-picked projections to
whole-subtree byte-equality plus schema-anchored key-set equality in the pack. That is the right fix
at the right layer.

**Ruling on `source_field_routing`: not a loophole against any single-sided change, but it carries one
real residual.** Three naive parking attempts were all caught, by three different assertions. However
parking a *real* root field that the domain test does not name (`coverage_source`,
`rule_lifecycle_statuses`) while updating the pack's pinned literal in the same change **ships green
on all 59 tests**, and I proved the field genuinely vanishes from `source_coverage` while the response
declares it was relocated there. The destination is checked for key **existence**, never for content
**reachability**. That is narrower than the original H-1 (it needs a two-sided edit) but it is the one
mechanism H-1's closure rests on, and it is the same "asserted against a constant the producer also
controls" pattern I flagged on M5-T012. Recorded as **R-1, the top required correction for the next
round — non-blocking for this gate.**

Four other new residuals (R-2..R-4 plus the unchanged backlog items) are below.

---

## 2. Counts I personally observed

```
$ git rev-parse HEAD
209b9548a18fa45f27c5b87f4af7989939645d81

$ python -m pytest services/api/tests/api
371 passed in 10.81s                      (312 pre-existing + 59 new)

$ python -m pytest services/api/tests/scenario
388 passed in 1.20s                       (unchanged, 0 regression)

$ python -m pytest services/api/tests/api/test_evidence_api.py
59 passed in 2.46s                        (was 37)

$ python -m pytest services/api/tests/api -k "not evidence"
312 passed, 59 deselected in 9.24s        (pre-existing files untouched)

$ python tools/modularity_check.py --check
exit 0 — "selected 367 files; failures 0; warnings 16"   (no warn names the new module)

$ cd services/api && python -m ruff check app/api/v1/evidence.py app/main.py \
      tests/api/test_evidence_api.py
All checks passed!   (ruff 0.13.0, exit 0)
```

Every figure matches your verification, **including the timing** — this run the api suite was
10.81s, the pack 2.46s. Thank you for chasing the discrepancy down: your contention explanation is
confirmed from this side, since the identical command on the identical SHA gave me 44.08s during the
earlier concurrent-reviewer window and 10.81s now. Both measurements were real; neither was a scoping
error. Recording it so the spread is on the record rather than looking like drift.

Determinism: pack run 3x with `-p no:cacheprovider` → `59 passed` in 2.24s / 2.27s / 2.33s. A
reordered subset (`-k "as8 or as7 or as1"`) → `11 passed, 48 deselected`. No flake, no order
dependence.

Delta scope: `git diff --stat 29ca7bca..209b9548` → 3 files, 749 insertions / 128 deletions, all in
`allowed_paths`. I verified independently that
`git diff --name-only 29ca7bca..209b9548 -- services/api/app/main.py services/api/app/config.py
services/api/app/profile/ services/api/app/rules/ packages/contracts/` returns **nothing** —
`main.py`, `config.py`, the profile and rules packages and the contracts package are all
byte-unchanged, as claimed.

Fixture hygiene re-verified: injecting a mid-test `AssertionError` after overrides were installed and
running the whole api suite produced exactly **+1** failure against the same tree's baseline
(8 failed / 354 passed / 9 errors vs 7 / 355 / 9 — the pre-existing failures are scratch-copy
artifacts, the copy lacking `packages/contracts`), and the only evidence-pack failure was the injected
test. `app.dependency_overrides` does not leak, including on failure.

---

## 3. Re-run mutation matrix

Method unchanged: one deliberate defect per run against a **fresh** out-of-repo scratch copy of
`services/api` taken at `209b9548`, full 59-test pack, revert in a `finally:`.

### The seven original H-1 survivors — all now CAUGHT

| # | Mutation (survived at `29ca7bca`) | Result | Caught by |
|---|---|---|---|
| H1a | `source_coverage.reasons` joined into a string | **CAUGHT** | as8_direct_assembly |
| H1b | `source_coverage.data_completeness` → `{}` | **CAUGHT** | as8_direct_assembly |
| H1c | `source_coverage.family_coverage` → `[]` | **CAUGHT** | as8_direct_assembly |
| H1d | `source_coverage.rule_lifecycle_statuses` → `[]` | **CAUGHT** | as8_direct_assembly |
| H1e | `evaluated_input.bbl` → `"9999999999"` | **CAUGHT** | as8_direct_assembly |
| H1f | `evaluated_input.profile_contract_version` → `"0.0.0"` | **CAUGHT** | as8_direct_assembly |
| H1g | citation group drops `rule_version` + `family` | **CAUGHT** (2) | as1_every_source_contract_field, as8_direct_assembly |

### Single-field drops — the realistic future regression

| # | Mutation | Result | Caught by |
|---|---|---|---|
| SFD-1 | root **`zoning_district`** dropped | **CAUGHT** (3) | key-set equality, the qualifications test, as8_direct_assembly |
| SFD-2 | trace **`exceptions_applied`** dropped | **CAUGHT** (3) | same three |
| SFD-3 | trace **`computation_steps`** dropped (mine) | **CAUGHT** (3) | same three |

Three independent assertions fire on each single-field drop, which is the defence-in-depth this
needed. Key-set equality against the app's own bundled `rule_evaluation.schema.json` is doing the work
it claims to.

### `source_field_routing` — the loophole probe

| # | Mutation | Result | Why |
|---|---|---|---|
| L1 | park a **non-root** key (`notes`) in the map → `rule_citations` | **CAUGHT** | `set(source_coverage) \| set(routing) == ROOT_REQUIRED` fails in the *nothing-invented* direction |
| L2 | park a **real root** field (`zoning_district`) → `source_coverage` | **CAUGHT** (2) | the pinned literal, and the domain test asserting `source_coverage["zoning_district"] == "R5"` |
| L3 | routing map **emptied** | **CAUGHT** | the pinned literal |
| L4 | park `notes` **and update the pinned literal** in the same change | **CAUGHT** | the nothing-invented direction still fails (`notes` is not a root required key) |
| **L5** | park real root **`coverage_source`** → `source_coverage`, literal updated | **SURVIVED** | see R-1 |
| **L6** | park real root **`rule_lifecycle_statuses`** → `source_coverage`, literal updated | **SURVIVED** | see R-1 |

### H-2 / H-3 / H-4 / H-5 closures

| # | Mutation | Result | Caught by |
|---|---|---|---|
| H2 | **fetch-stage** generic guard removed | **CAUGHT** | as6_fetch_stage_raise (new) |
| H3a | server-authored `verified: True` at the document **root** | **CAUGHT** | as7_no_server_authored_claim_is_verified |
| H3b | `verified: True` nested in **every citation group** | **CAUGHT** (3) | as7, as1_key_sets, as8_direct_assembly |
| H3c | `verification_status: "verified"` **deep** inside `source_coverage` | **CAUGHT** (3) | as7, as1_key_sets, as8_direct_assembly |
| H4 | handler gains a `terse` **query parameter** stripping `profile_provenance` | **CAUGHT** | as3_route_declares_no_query_parameter_and_no_body |
| H5a | completeness labels swapped (`complete` ↔ `thin`) | **CAUGHT** (5) | completeness_marker unit tests |
| H5b | `data_conflict` branch removed | **CAUGHT** | completeness_marker unit tests |
| H5c | `fail_safe` no longer yields `thin` | **CAUGHT** | completeness_marker unit tests |
| H5d | missing-profile-provenance gap suppressed | **CAUGHT** | as5_missing_profile_provenance_is_a_named_gap |
| H5e | `rule_conflict` gap marker suppressed | **CAUGHT** (2) | the two rule-conflict tests |

### Regression spot-checks (previously caught — still caught)

| # | Mutation | Result |
|---|---|---|
| REG-1 | drop one provenance record | **CAUGHT** (2) |
| REG-2 | cap `str()` coercion | **CAUGHT** (3) |
| REG-3 | disabled 404 gains a header | **CAUGHT** (8) |
| REG-4 | **aliasing** instead of deep copy in `source_coverage` | **CAUGHT** (2) |

### New hole hunting on the 22 added tests

| # | Mutation | Result |
|---|---|---|
| N4 | `verified: "Verified"` (string, mixed case) | **CAUGHT** |
| **N1** | handler takes `Request` and echoes a **request header** into the document | **SURVIVED** (R-2) |
| **N2** | `"verified"` claim under an **unlisted key** (`determination_status`) | **SURVIVED** (R-3, documented limit) |
| **N3** | `verified: 1` (truthy **number** rather than `True`) | **SURVIVED** (R-4) |

### Backlog items re-checked (your question)

| # | Mutation | Result |
|---|---|---|
| H7 | cap `round()` coercion | **CAUGHT** — but see the note in §5 |
| H8 | `EVIDENCE_CONTRACT_VERSION` constant bumped → `9.9.9` | **SURVIVED** (unchanged) |
| H6 | emit only the **first** evaluation group | **SURVIVED** (no-op at n=1; unchanged) |

---

## 4. Are H-1..H-5 genuinely closed?

**Yes, all five.** Each closure was verified by reproducing the original surviving mutation and by
reading the mechanism rather than the claim:

* **H-1 — closed, and closed at the right layer.** The product no longer re-keys a chosen subset: it
  deep-copies `rule_evaluation` wholesale (`services/api/app/api/v1/evidence.py:369-373`), copies each
  trace entire plus one added key (`:337-347`), and copies `evaluated_input` entire (`:381`). So a
  field added to the source contract *flows through automatically* — the class of bug is designed out,
  not merely asserted against. On the test side the three claimed assertions are all real and all
  load-bearing: schema-anchored key-set equality in both directions
  (`services/api/tests/api/test_evidence_api.py:418-437`), whole-subtree byte-equality plus an
  explicit aliasing check (`:1084-1105`), and `_stable_view` now comparing the entire document with a
  single empirically-determined volatile leaf masked (`:523-537`). I confirmed `observation_id` is
  indeed the only volatile leaf, and the masking is one leaf key rather than a subtree, so the
  comparison really is total.
* **H-2 — closed.** `test_as6_fetch_stage_raise_is_typed_internal_error_500` (`:819-845`) drives a
  non-`PlutoConnectorError` out of the injected fetcher and asserts the documented pair, JSON
  content-type, the correlation-id match and four separate non-leak conditions.
* **H-3 — closed, and better than I asked for.** The 4-path enumeration is replaced by
  `_verification_claims` (`:324-335`), and the test additionally asserts the walk **reaches** the
  top-level, per-group and deeply-nested claim keys (`:932-941`) — so the walk cannot silently stop
  working and pass vacuously. That reach-assertion is the detail that makes this a real fix rather
  than a different enumeration.
* **H-4 — closed.** `test_as3_route_declares_no_query_parameter_and_no_body` (`:566-592`) asserts the
  route's own FastAPI `dependant` view — `query_params`/`body_params`/`header_params`/`cookie_params`
  empty, `body_field is None`, `path_params == ["bbl"]`, methods `["GET"]` — and repeats the check for
  both `Depends` seams so a parameter cannot enter through a dependency.
* **H-5 — closed.** Both pure classifiers are unit-tested directly over a synthetic
  `rule_evaluation` dict (`:1106+`), covering all four completeness outcomes (three unreachable
  through any fixture) and every gap branch. No fixtures, no HTTP, no measurable runtime — the right
  way to test a pure classifier, and breaking any branch now fails.

I also note two things the rework got right that were not required of it: the `rule_conflict` gap
marker carries the competing-rules object verbatim so a reviewer is told *what to look at* rather than
merely that review is needed, and the overclaiming test name was fixed
(`test_as1_deterministic_provenance_and_citations_transport_byte_equal`).

---

## 5. Findings (new this round)

### Required correction for the next round (non-blocking for this gate)

**R-1 — MEDIUM — `source_field_routing` destinations are checked for key existence, not content
reachability, so a real root field can be parked there and disappear.**
Product: `_RELOCATED_SOURCE_FIELDS` (`services/api/app/api/v1/evidence.py:160-169`) drives the
`source_coverage` exclusion filter (`:369-373`). Test: the routing check is
`assert document_key in doc` (`services/api/tests/api/test_evidence_api.py:418-421`) plus a pinned
literal (`:419`).
Adding `"coverage_source": "source_coverage"` (L5) or `"rule_lifecycle_statuses": "source_coverage"`
(L6) to the map and updating the pinned literal in the same change leaves **all 59 tests green**. I
confirmed the consequence directly against the running app: with `coverage_source` parked,
`"coverage_source" in doc["source_coverage"]` is **False** while `source_field_routing` declares it
lives in `source_coverage` — a self-contradictory declaration that no assertion tests. The field is
gone and the response asserts it was relocated.
Why the other four parking attempts were caught and these two were not: the nothing-invented direction
of `set(source_coverage) | set(routing) == ROOT_REQUIRED` catches only keys that are *not* root
required fields; the pinned literal catches only a map the test author did not update; and the domain
test catches only the root fields it happens to name (`zoning_district`, `lot_area_sq_ft`). A real
root field outside that set, declared in a consistent-looking way, passes everything — and
`test_as8_direct_assembly_is_pure_transport` computes its expected dict *from the document's own
routing map* (`:1084-1086`), so it excludes the parked field too.
This requires a two-sided edit, so it is a weaker threat model than the original H-1 — but it is the
plausible shape of a future change ("I relocated a field and declared it properly"), and declaration
is currently accepted in place of verification.
*Minimal fix (not applied):* assert each routed source field's **content** is reachable at its
declared destination — for `evaluated_input`, the existing equality already does it; for
`evaluations`, the existing zip-strict group comparison already does it; so the gap is only that a
*third* entry would have no such check. The cheapest robust form is one line:
`assert set(routing) <= {"evaluations", "evaluated_input"}` with a comment that any new entry must
arrive with its own content-reachability assertion — or, better, derive the permitted routing set from
the checks that actually verify reachability rather than from a literal.

### Non-blocking

**R-2 — MEDIUM/LOW — AS-3's "zero untrusted-input surface" does not cover a directly-read request
header.** Taking `request: Request` and echoing `request.headers.get("user-agent")` into the document
(N1) leaves all 59 tests green. `test_as3_route_declares_no_query_parameter_and_no_body` inspects
`dependant.query_params` / `body_params` / `header_params` / `cookie_params` — a `Request` parameter is
none of those, so it is invisible to that introspection; and
`test_as3_request_body_cannot_influence_the_response` issues both comparison requests from the same
`TestClient`, so an echoed header is *identical* in both and the stable-view equality holds.
*Minimal fix:* send the second comparison request with deliberately different headers (a custom
`user-agent` plus an arbitrary `X-` header) so any header echo breaks the whole-document equality; a
one-line change that also strengthens the existing body assertion. Optionally assert the handler
declares no `Request` parameter.

**R-3 — LOW, inherent and already documented — a `"verified"` claim under an unenumerated key
survives.** `determination_status: "verified"` (N2) ships green: `_verification_claims` inspects only
keys in `_VERIFICATION_CLAIM_KEYS` (`:310-322`). This is exactly the limit AS-7 instructs the producer
to *document rather than chase*, and it is documented both in the helper comment and in the response's
`verification_scope_note`. Recording it as a known limit, not a defect. One asymmetry worth noting:
M5-T012's final shape also scanned every string *value* for exact `"verified"`, which would have
caught this; here that value-scan was dropped in favour of the key-walk. A blanket value scan is
impossible (the canonical disclaimer contains "not a Verified determination" and citation quotes carry
free prose), but a value scan restricted to the **server-authored** subtrees — the root scalars and
`claim_verification_status` — would harden it cheaply without touching transported prose.

**R-4 — LOW — `verified: 1` survives because the assertion is `value is not True`.** A truthy number
passes both `value is not True` and the string comparison (`:927-930`). M5-T012's proven shape
(`value in (False, None)`) caught truthy numbers; that exact form is wrong here because
`coverage_status` and `claim_verification_status` legitimately hold vocabulary strings, so the fix is
to assert the value *denies* — `False`/`None` or a member of the documented draft vocabulary — rather
than merely "is not the literal `True`".

### Backlog items — my ruling now that the document carries the full trail

You asked whether any of H-6..H-10 should be reconsidered. My answers, each re-tested rather than
recalled:

* **H-6 ("every citation" only ever at n=1) — reconsider, and it is now nearly free.** Re-tested: the
  document still carries **1 rule_citations group with 1 citation** post-rework, so emitting only the
  first group remains a no-op and the mutation survives necessarily. Aggregation and ordering across
  multiple rules/citations are still structurally unexercised. What changed is the *cost of fixing
  it*: the pack now has `_synthetic_rule_eval` and the precedent of calling the assembler and the pure
  classifiers directly, so a synthetic 2-rule / 2-citation `rule_evaluation` passed to
  `assemble_evidence_document` with assertions on count and order is a handful of lines, no fixture
  and no runtime. I would promote it from backlog and do it alongside R-1.
* **H-7 (type fidelity) — partially closed; I will not overclaim.** My `round()` mutation is now
  CAUGHT, but only because `round(1.5) = 2` changes `max_residential_far`'s *value*. A
  value-preserving type coercion (`15000.0 → 15000`) would still pass, because `==` on dicts is
  type-insensitive in Python. So the narrow type-fidelity case remains open; its priority is unchanged
  (low).
* **H-8 (version constant self-referential) — unchanged, still survives.** Bumping
  `EVIDENCE_CONTRACT_VERSION` keeps the pack green. One pinned literal closes it. Low.
* **H-9 (the grep-based "no arithmetic" test) and H-10 (the redundant `allow_nan=False` half)** —
  unchanged, both still informational. H-9's weakness is reconfirmed by the H-7 note above: the real
  guard is the value-equality assertions, not the source grep.

---

## 6. Worktree left byte-identical

I wrote exactly one file: this report. `M5-T013-G3.md` is untouched.

* `git rev-parse HEAD` before and after: `209b9548a18fa45f27c5b87f4af7989939645d81`.
* sha256 of the three files under review, diffed against the fingerprint taken before I began —
  **identical**:
  * `services/api/tests/api/test_evidence_api.py`
    `45c22b984439c5ed9c3827da3d8e3b50ee1cb14e67a611540923ff8bc3afdc62`
  * `services/api/app/api/v1/evidence.py`
    `fa37a6b834e690a405104b678d9866ee2ec2c4702f2da6206085b6f9a5637c15`
  * `services/api/app/main.py`
    `97be914803e6ea93a4e8c9a603eedf2b59a78b762bf5c40a7c04b2f2e10ce875`
* All 37 mutations and every behavioural probe ran against a fresh out-of-repo scratch copy of
  `services/api` taken at `209b9548`, each reverted in a `finally:` block with the restore verified by
  content comparison, and the scratch tree re-verified green (`59 passed`) before use.
* The only worktree delta during my review is orchestrator-authored, not mine:
  `project-control/reports/M5-T013-DCV-rereview.md` and `M5-T013-G4-rereview.md` appeared. I neither
  created nor read them.
* No `git` write command, no `tools/project_control.py`, no commit, stash or push; nothing installed.
* Independence: I am not the producer of any file under review and edited none of them. Every number
  here is from my own runs. I read the packet and the two owned files; I did not read the producer
  report or the concurrent DCV / G1 / G4 / G5 artifacts, so the 24 claims were re-derived from the
  code rather than copied from the table.
