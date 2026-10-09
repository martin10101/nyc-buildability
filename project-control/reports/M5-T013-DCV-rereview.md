# M5-T013 — Directive-Compliance RE-REVIEW (DCV) vs D-038, at reworked SHA `209b9548`

`project-control/reports/M5-T013-DCV.md` (first review, at `29ca7bca`) stands intact as the record
of that SHA. This file is the re-issued verification at the reworked head.

Verifier: **directive-compliance-verifier** (independent). Reviewed SHA
`209b9548a18fa45f27c5b87f4af7989939645d81`; material identity
`5506a5947d0ec1997ebd581602c83e23ba0ea54ef83bc578c26cb56f4778c152`.

---

## DCV RE-REVIEW — task M5-T013 vs directive D-038 (independent)

**Verdict: PASS.** No BLOCKING directive finding. The verbatim-vs-interpret ruling **still holds and
is strengthened** (§5); `source_field_routing` **satisfies** the directive's honesty obligation (§6),
with one precise, non-blocking observation about how thinly that guard is held.

| field | value |
|---|---|
| `reviewed_sha` | `209b9548a18fa45f27c5b87f4af7989939645d81` (confirmed `git rev-parse HEAD`) |
| `reviewed_manifest_sha256` | `5506a5947d0ec1997ebd581602c83e23ba0ea54ef83bc578c26cb56f4778c152` (first 8: `5506a594`) |
| previous identity (now stale) | `ebf8f4d9…` at `29ca7bca` |
| applicable requirement set | exactly `{D-038-R003, D-038-R004}` |
| `D-038-R003` | **SATISFIED** |
| `D-038-R004` | **SATISFIED** |
| `validate_directive_compliance.py --check` | **EXIT 0** |
| accept simulation | `reasons: []`, `deferrals: []` |

### 0. Independence

Not the producer (`backend-engineer`), not any of the four gate reviewers (`code-reviewer` G1/G4,
`qa-engineer` G3, `security-reviewer` G5). Every claim below reproduced by me from primary evidence.
My only write is this file; I wrote no gate record, no packet, no `verification.json`.

### 1. Delta (reproduced)

`git diff --name-status 29ca7bca 209b9548` → **3 files, all in `allowed_paths`**:
`evidence.py` (M, +138/−…), `test_evidence_api.py` (M, +506/−…), producer report (M);
`--stat` total **749 insertions / 128 deletions**.

**18 unchanged-path probes, each `git diff --quiet`, all BYTE-UNCHANGED:** `main.py` (blob still
`128593c6`), `config.py`, `app/api/v1/{properties,rule_evaluation,scenario,scenario_analysis}.py`,
`app/profile/**`, `app/rules/**`, `app/scenario/**`, `app/spatial/**`, `app/connectors/**`,
`app/resilience/**`, `packages/contracts/**`, `apps/web/**`, `tools/**`, `supabase/**`,
`services/api/tests/scenario/**`, **`project-control/directives/**`**.

### 2. Applicable requirement set — re-derived: still exactly `{D-038-R003, D-038-R004}`

`evaluate_task_refs` → `ok: true`, `applicable_ids: [D-038-R003, D-038-R004]`, `missing_ids: []`,
`invalid_refs: []`, `unresolved: []`. The rework added **no file and no path**, so the path surface is
the one already cleared in §2 of `M5-T013-DCV.md`; the three `project-control/reports/`-intersecting
rows (`D-004-R222`, `D-004-R240`, `D-007-R610`) still fail their `task_types=['governance']` + M0
conjunction against a `backend`/`M5` task. R001/R002/R005/R006/R007 remain sentinel-bound
(`D-038-BOOTSTRAP`) → NOT_APPLICABLE.

### 3. Material content identity at `209b9548` — via the accept path's own routine

```python
import sys; sys.path.insert(0, "tools")
import project_control as pc
reg_mod = pc._resolver()
t = pc.load(pc.PC / "tasks" / "M5-T013.json")
identity, resolved_sha, ierr = pc._task_git_identity(reg_mod, t)   # reviewed_sha=None -> HEAD
```

```
identity     = 5506a5947d0ec1997ebd581602c83e23ba0ea54ef83bc578c26cb56f4778c152
first 8      = 5506a594
resolved_sha = 209b9548a18fa45f27c5b87f4af7989939645d81
error        = None
```

* **Function:** `tools/project_control.py::_task_git_identity(reg_mod, task_dict)`, `reviewed_sha=None`
  → HEAD — the exact call `accept()` makes via `_directive_accept_reasons` (`:532`, invoked at `:1254`),
  delegating to `directive_registry.frozen_git_identity(..., exclude_prefixes=('project-control/',),
  require_clean=True, control_plane_prefixes=('project-control/',), allow_empty_identity=False)`.
  `path_free_opt_in()` → `(False, None)`.
* **Blob composition (4 objects):**

  | component | path | blob | vs `29ca7bca` |
  |---|---|---|---|
  | raw-blob | `services/api/app/api/v1/evidence.py` | `cc1f089fa4f2f0983669f51b0710ac71e44850ee` | changed (was `dd69e05e`) |
  | raw-blob | `services/api/app/main.py` | `128593c65bc96a03b5a7e9c547880c6545b6732f` | **unchanged** |
  | raw-blob | `services/api/tests/api/test_evidence_api.py` | `2b8684b540778be091ef8bb24f52b0983dfa15ba` | changed (was `be001e8d`) |
  | control-plane | `project-control/reports/M5-T013-producer-report.md` | `f269218269eaff4c00eab6c4ddaa300eac75a35e` | changed (was `2c5e1899`) |

  Raw-blob component `4db0a2516d05b659807e6e7301de62ce5590e4cdb5147caa6983f88d5c6ad419`;
  `_hash_manifest_entries(raw_blobs + control_plane)` = `5506a594…`.
* **Dirt guard passed (`err = None`)** despite the working tree's pre-existing orchestrator/gate state
  (modified `state.json` and the packet, the four `M5-T013-G*.json` records, the gate reports,
  `.claude/agent-memory/*`, `scratchpad/`) — none is inside `allowed_paths`.
* `ebf8f4d9…` is now **stale** and must not be written into `verification.json`.

### 4. Re-run leaf classification on the ENLARGED document — the critical check

Method identical to the first review: rebuild the profile and rule_evaluation over the injected
seams, call `assemble_evidence_document`, then classify **every leaf** as TRANSPORTED (byte-equal by
type and value to some scalar present in either source document) or SERVER-AUTHORED.

```
29ca7bca : 1339 leaves -> 1332 TRANSPORTED /  7 SERVER-AUTHORED
209b9548 : 1413 leaves -> 1404 TRANSPORTED /  9 SERVER-AUTHORED      (+74 transported, +2 authored)
```

**The authored set grew by exactly two leaves, and both are the routing *declaration*, not content:**

| leaf | value | new? | what it is |
|---|---|---|---|
| `$.document_kind` | `'evidence_trail'` | | structural label |
| `$.overall_verification_status` | `'draft'` | | verification **down**-label |
| `$.rule_citations[0].claim_verification_status` | `'draft'` | | verification **down**-label |
| `$.verification_scope_note` | (disclaimer) | | self-describing limitation |
| `$.evidence_completeness` | `'professional_review_required'` | | epistemic marker |
| `$.gaps[0].kind` | `'professional_review_required'` | | typed gap marker |
| `$.gaps[0].subject` | `'coverage'` | | gap subject name |
| `$.source_field_routing.evaluations` | `'rich_citations'→`rule_citations`` | **NEW** | routing metadata |
| `$.source_field_routing.evaluated_input` | `'evaluated_input'` | **NEW** | routing metadata |

**Every one of the +74 newly carried leaves is TRANSPORTED.** Not one newly carried field is authored
or altered — which is precisely the risk the coordinator named (a restored-but-reformatted
qualification would be worse than the omission). Verified three independent ways:

1. **Wholesale subtree byte-equality — all True:**
   `source_coverage == {k: v for k, v in rule_evaluation.items() if k not in _RELOCATED_SOURCE_FIELDS}`;
   `evaluated_input == rule_evaluation["evaluated_input"]`;
   `profile_provenance == profile["provenance"]`; and every `rule_citations` group ==
   `{**trace, "claim_verification_status": <echo>}`.
2. **Key-set completeness, counted:** root `|source_coverage| = 18` + 2 routed = **20 == 20** source
   root keys; each citation group has **20** keys, which minus the single authored key == the **19**
   source trace keys; `evaluated_input` **4 == 4**. (Was 14/20 and 7/19 before the fix.)
3. **Per-field byte-equality and non-aliasing** on every restored field, with sizes to show nothing
   was truncated: `exceptions_applied` (808 B), `notes` (1,487 B), `computation_steps` (343 B),
   `rule_release` (171 B), `uncertainty` (250 B), `effective_window` (98 B), `evaluated_inputs` (52 B),
   `input_validation` (37 B), `determination`, `data_completeness`, `citations` (925 B), `outputs`
   (73 B) — **byte-equal=True, is-alias=False** for each; and at the root `zoning_district`,
   `lot_area_sq_ft`, `lot_area_source`, `rule_conflict`, `spatial_context`, `spatial_uncertainty` all
   byte-equal.

**Mutation safety re-proven:** appending to `doc["source_coverage"]["reasons"]` does **not** reach the
source (`"DCV-MUTATION" in json.dumps(rule_evaluation)` → **False**), and both source documents are
byte-unchanged after assembly. Transport is by deep copy, never by alias, so the larger payload cannot
corrupt the documents it reports on.

**Structural note on why this is now hard to regress.** The fix replaced a hand-picked allow-list with
a wholesale copy: `{**copy.deepcopy(trace), "claim_verification_status": …}` per trace, and
`source_coverage` as a comprehension over **all** `rule_evaluation.items()` minus the routed keys. A
field added to the source contract therefore flows through automatically instead of being dropped
until someone notices — the inverse of the failure mode that produced BLOCKING-1.

### 5. RE-RULING — verbatim transport vs interpretation

**Ruling: still HONOURED. Transports verbatim, adds no legal rule, NOT G6-relevant. Not a BLOCKING
finding.** The rework moved a great deal of legal text into the response and moved **none** of it
through an interpreting step.

* **The two highest-stakes strings are byte-equal and not summarised**, as specifically asked:
  * `exceptions_applied` — carries verbatim *"A higher maximum residential FAR (up to 2.00 for
    R5/R5A/R5B per ZR 23-21) applies to zoning lots that are 'qualifying residential sites'. Whether
    a specific lot qualifies is a separate legal determination and is not decided by this rule; when
    the site class is unknown or qualifying, the result is conditional…"* — 808 bytes, byte-equal to
    the trace, a deep copy, not truncated and not paraphrased.
  * `notes` — carries the qualification prose including *"…is not decided by this rule…"* — 1,487
    bytes, byte-equal, deep copy.
  * `rule_release.verified_eligible` → **`False`**, transported. The reader can now see the G6
    approval state directly.
* **No arithmetic and no rewriting exist in the module.** My scan for arithmetic operators,
  `round/sum/min/max/abs/float/int`, `.replace/.format/.join/.upper/.title`, and f-strings over
  `evidence.py` returns **zero** hits at this SHA. `build_scenario` **0**, `import math` **0**,
  `evaluate_property(` exactly **1** (the AS-1-mandated accepted rebuild, not a new rule).
* **The verification labels still only ever weaken a claim.** `_verification_status` remains the sole
  site able to emit `verified`, and only by echoing a literal source `"verified"`.
* **The G6 conclusion is, if anything, better supported than before.** The previous document omitted
  the very fields that disclose conditionality; restoring them verbatim means the response now
  *shows* that the 15,000 sq ft figure is conditional and not Verified-eligible, rather than
  presenting it bare. An evidence surface that transports the qualifications attached to a number
  asserts no new legal rule — it makes the existing one auditable, which is the opposite of a G6
  trigger.

### 6. RULING on `source_field_routing` — satisfies the honesty obligation

**Ruling: YES, the directive's honesty obligation is satisfied at this SHA. It is not a silent-omission
channel today, and it cannot become one silently.** Reasoning, with my own RED checks:

1. **There are zero genuine exclusions.** Both map entries are real relocations, and I verified each
   destination carries the complete relocated content byte-equal: `evaluations → rule_citations`
   (every group == the whole trace + one key; 19/19 source keys per trace) and
   `evaluated_input → evaluated_input` (the whole sub-document, 4/4 keys). So no field is excluded,
   and the "documented reason" obligation is not yet engaged.
2. **The map is visible to the caller**, emitted in-response as
   `{"evaluations": "rule_citations", "evaluated_input": "evaluated_input"}`, so a consumer can
   mechanically reconcile the document against the source contract — exactly the auditability the
   directive's honesty obligation is about.
3. **It cannot be widened silently — proven by RED check.** I injected a third entry that drops a
   real, high-stakes root field and ran the suite:
   * `_RELOCATED_SOURCE_FIELDS["coverage_status"] = "somewhere_else"` → **1 failed, 58 passed**,
     failing at `test_evidence_api.py:419`.
   * `_RELOCATED_SOURCE_FIELDS["coverage_status"] = "evaluated_input"` (an **existing** key, so the
     "destination exists" guard cannot fire) → **1 failed, 58 passed**, again at `:419`.
   Either way the omission is caught: a field cannot leave this document without someone editing a
   pinned literal assertion, which is a deliberate, reviewer-visible act rather than a silent drop.

**Non-blocking observation the gates should weigh (mine is the directive angle; G1/G3/G5 own the
depth-of-defence angle).** That guard is **single-stranded**. The two RED checks show only *one*
assertion fires — the literal pin
`assert routing == {"evaluations": "rule_citations", "evaluated_input": "evaluated_input"}` at
`:419`. The other completeness assertions are **map-relative** and pass when the map grows, because
both sides are derived through the map itself:
`set(doc["source_coverage"]) | set(routing) == ROOT_REQUIRED` (the field leaves `source_coverage` and
re-enters via `routing`), and the whole-subtree equality at `:1084`
(`source_coverage == {k: v for k, v in rule_eval.items() if k not in routing}`). Two consequences
worth a line of hardening, neither a violation today:
* Nothing asserts that a routed field's **content** actually arrived at its declared destination — the
  map says *where*, and only the literal pin says *which*. An assertion per routed entry that the
  source value is present and byte-equal at the destination would make omission detectable
  independently of the pin.
* The map is typed `dict[str, str]` (source → destination). The module comment says a genuine
  exclusion "belongs here with a documented reason", but this shape can only hold a destination
  string, so a future real exclusion would have to encode a reason as a pseudo-destination. If an
  exclusion is ever needed, the structure should carry an explicit reason field to meet the packet's
  "documented reason visible to the caller" rule.

### 7. D-038-R003 — **SATISFIED**

* Still the Evidence surface named in R003's own first clause ("user-facing screens
  (Compare/**Evidence**/report/reviewer UI)"), still `services/api/**` product code, milestone M5,
  `task_type=backend`; `tools/**` and `.claude/**` untouched. Not self-infrastructure.
* Still a normal G0 packet (`M5-T013-G0.json` PASS, administrative, intake report present).
* **Scenarios are materially more executable than at the prior SHA, and I ran them.** The test pack
  grew 878 → **1,292** lines and **37 → 59** collected items. Reproduced:
  * `python -m pytest services/api/tests/api` → **371 passed in 14.44s, exit 0** (312 pre-existing + 59)
  * `python -m pytest services/api/tests/scenario` → **388 passed in 1.64s, exit 0** — unchanged, **0 regression**
  * `python tools/modularity_check.py --check` → **failures 0, EXIT 0** (367 files); **no warning names
    `app/api/v1/evidence.py`**. (I ran it; the producer again correctly declined, `tools/**` being
    forbidden to it and not a documented test command.)
  * `ruff check app/api/v1/evidence.py tests/api/test_evidence_api.py` → **All checks passed!**
* **Route posture re-verified live at this SHA** (evidence.py changed 138 lines, so I did not assume):
  eight non-true flag tokens each → `404 {"detail":"Not Found"}` with no `X-Correlation-ID`;
  disabled response **byte-identical in body and header-set** to an unmounted sibling;
  `/openapi.json` **byte-identical off vs on** and containing no "evidence"; `POST/PUT/PATCH/DELETE`
  → **405**; malformed BBL → **422 `validation_error`**.
  `STATUS_STATE_MATRIX` minus the properties matrix = **`[]`** (no new pair) and equal to the accepted
  scenario route's matrix.
* **AS-6 re-verified by forcing raises:** `build_property_profile`, `evaluate_property`,
  `assemble_evidence_document` → `500 internal_error`; `_assert_json_safe` →
  `500 internal_contract_error`. All in-matrix, `application/json`, `X-Correlation-ID` present, and
  **no** secret/path/traceback in the body. Unserialisable transported content (unpaired surrogate,
  `NaN`, `Infinity`) → `500 internal_contract_error`, in-matrix. Clean 200 survives **both**
  `json.dumps(doc, allow_nan=False)` and `json.dumps(doc, ensure_ascii=False, allow_nan=False).encode("utf-8")`,
  no `" at 0x"` leak.

### 8. D-038-R004 — **SATISFIED** (re-proven, not inherited)

* **Negative grep** over the reworked `evidence.py` for
  `supabase|geoclient|requests\.|httpx|socket|urllib|os\.environ|getenv|subprocess|boto3|psycopg|sqlalchemy|open\(`
  → **0 matches**.
* **No new flag or credential surface.** `from app.config import internal_rule_eval_enabled`
  (`evidence.py:86`), gated at `:420`; `config.py` byte-unchanged across both reworks and still the
  pre-existing helper from `30d6e3b4`.
* **My own loopback-only egress block, re-armed at this SHA:** evidence suite → **59 passed in 3.10s**,
  non-loopback egress **`[]`**; **whole api suite → 371 passed in 11.72s**, egress **`[]`**; my
  assembly and route probes → egress **`[]`** throughout.
* Facts still come only from the injected `get_pluto_fetcher` / `get_spatial_substrate_provider` seams
  over the recorded-official PLUTO fixtures. `dependencies = [M5-T003]`; `supabase/**` byte-unchanged.
* The session's Supabase MCP server again failed to connect; **immaterial** to R004, and I used
  nothing from it.

### 9. Integrity — UNCHANGED and re-confirmed

* `python tools/validate_directive_compliance.py --check` → **EXIT 0** (silent pass).
* **CRLF-byte digest.** `requirements.json` on disk: **9,350 bytes, 260 CRLF, 0 bare LF**; `sha256` of
  those exact bytes, un-normalised = `f62c6fc8cec2497af0d6170d232559df79544fe06239f44b80bea1bea0f39f0b`
  == `manifest.requirements_content_digest_sha256`. ✓
* **Source digest** `a237dd50…` == `manifest.sources[0]`. ✓ `amendments: []`. ✓
* **`locked_requirement_ids` unchanged at `[R001..R007]`**, equal to on-disk ids and to
  `requirement_count` 7. ✓
* **Transition verified at both ends, across all four commits:** CRLF-encoded `requirements.json`
  hashes to `32f8d252` at `9a84d392^` (manifest claimed `32f8d252`) and to `f62c6fc8` at `9a84d392`,
  `29ca7bca` and `209b9548` (manifest claims `f62c6fc8`); `locked` = 7 and `audit_log` = 11 at all
  three post-append commits. The rework touched no directive file. ✓
* **audit_log[-1]** `2026-09-10T03:40:00+00:00`, `applicability_appended`, naming M5-T013 and the
  `32f8d252 → f62c6fc8` resync. ✓

### 10. Accept simulation

`reg.task_verification_result('D-038','M5-T013',{R003,R004},'5506a594…',reviewed_sha='209b9548…')`
with a row in the accepted M5-T012 minimal shape (container carries the attestation fields; each
requirement row carries `id`/`state`/`evidence`):

```
reasons  : []
deferrals: []
-> ROW SHAPE SATISFIES THE ACCEPT GATE (nothing to defer)
```

**Negative control** (the now-stale `29ca7bca` / `ebf8f4d9` pair against the new row) is correctly
refused, so the freshness check is live:

```
D-038/M5-T013: verification is stale -- recorded at content identity 5506a594..., current is ebf8f4d9...
D-038/M5-T013: verification reviewed_sha is stale -- recorded at commit 209b9548..., current reviewed commit is 29ca7bca... (fail closed)
```

### 11. BLOCKING (process, not code, and not a D-038 violation): every gate record is stale

| gate | reviewer | result | reviewed_sha | identity |
|---|---|---|---|---|
| G0 | orchestrator | PASS | `b3fa1736` | `5cbbdd13` |
| G1 | code-reviewer | **FAIL** | `29ca7bca` | `ebf8f4d9` |
| G3 | qa-engineer | PASS | `29ca7bca` | `ebf8f4d9` |
| G4 | code-reviewer | PASS | `29ca7bca` | `ebf8f4d9` |
| G5 | security-reviewer | PASS | `29ca7bca` | `ebf8f4d9` |

`accept()` iterates `required_gates = [G0,G1,G3,G4,G5]` and adds a reason for any gate without a PASS
record, so it will refuse on **G1** as it stands. G1 must be re-gated **PASS at `209b9548`**, and
G3/G4/G5 re-attested there — their PASS was given against the superseded content, and the rework
changed 749 lines including the whole assembly path. (`accept()` does not itself compare a gate
record's `content_manifest_sha256`, so G3/G4/G5 staleness is a review-integrity obligation on the
wave rather than a mechanical refusal; G1's FAIL is the mechanical refusal.) Also absent: the submit
report `project-control/reports/M5-T013.json`, which `accept()` compares against `5506a594…` — run
`submit` at this HEAD.

**No code-level BLOCKING remains.** I found no new blocking defect at `209b9548`, and the G1
BLOCKING-1 omission is reproduced as fixed (§4).

### 12. Non-blocking observations

* **`source_field_routing` single-stranded guard** — §6, the main one for G1/G3/G5 to weigh.
* **`_completeness_marker` coarsening** stands as recorded in the first review: distinct source states
  collapse into one label, losslessly, because the precise value rides alongside in
  `source_coverage.coverage_status` and is re-named in a typed gap marker.
* **My earlier digest-basis finding was acted on**, and I confirm the remedy is sound in principle:
  publishing both bases per file, labelled, removes the reproduction ambiguity. I did not re-verify
  every published digit at this SHA — the material identity in §3 is computed from git objects by the
  accept path's own routine and does not depend on the producer's table.
* **`tools/test_directive_compliance.py`: I did NOT run it and make no claim about it.** Integrity
  evidence in §9 rests on `validate_directive_compliance.py --check` → **EXIT 0**.

### 13. Worktree left as found

`git status --short` shows only pre-existing orchestrator/gate state (modified `state.json` and
`project-control/tasks/M5-T013.json`; untracked `M5-T013-G{1,3,4,5}.json`, their reports,
`M5-T013-DCV.md`, `.claude/agent-memory/qa-engineer/*`, `scratchpad/`) plus this report. I touched
nothing else. My probe scripts (`dcv_netblock.py`, `dcv_m5t013_rr_leaves.py`,
`dcv_m5t013_rr_route.py`, `dcv_routing_redcheck.py`, `dcv_routing_redcheck2.py`) live outside the
repository in the session scratchpad.
