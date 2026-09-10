# M5-T013 — Directive-Compliance Verification (DCV) vs D-038, at reviewed SHA `29ca7bca`

Verifier: **directive-compliance-verifier** (independent). Reviewed SHA
`29ca7bca83c163957f6b0aa2ddc9a48b7f158a57`; material identity
`ebf8f4d9ac73ca23df20891b29284f2af9a18d5de9187f8d30c00ee3e7ebdc68`.

---

## DCV REPORT — task M5-T013 vs directive D-038 (independent)

**Verdict: PASS.** No BLOCKING directive finding. The verbatim-vs-interpret question is ruled
**HONOURED — transports verbatim, adds no legal rule, NOT G6-relevant** (§5, decided on an
exhaustive leaf-by-leaf classification rather than on the producer's or any reviewer's claim).

| field | value |
|---|---|
| `reviewed_sha` | `29ca7bca83c163957f6b0aa2ddc9a48b7f158a57` (confirmed `git rev-parse HEAD`; branch `candidate/D-024-mrl-option-b`) |
| `reviewed_manifest_sha256` | `ebf8f4d9ac73ca23df20891b29284f2af9a18d5de9187f8d30c00ee3e7ebdc68` (first 8: `ebf8f4d9`) |
| applicable requirement set | exactly `{D-038-R003, D-038-R004}` — derived, not assumed |
| `D-038-R003` | **SATISFIED** |
| `D-038-R004` | **SATISFIED** |
| `validate_directive_compliance.py --check` | **EXIT 0** |
| accept simulation | `reasons: []`, `deferrals: []` |
| platform | Python 3.11.9, pytest 8.4.2, Windows 11. Read-only throughout. |

### 0. Independence

I am not the producer (`backend-engineer`) and not any of the four gate reviewers
(`code-reviewer`, `qa-engineer`, `security-reviewer`, and whoever records G4). Every claim below was
reproduced by me from primary evidence — git objects, the files themselves, and my own command runs.
Where the coordinator's message or the producer report asserts something, I say so explicitly and
then reproduce it. My only write is this file. I did not touch product code, tests, the packet,
`state.json`, `verification.json`, the directive files, or any gate record; I ran no
`project_control.py` write subcommand and no git/gh write command.

### 1. Scope / diff identity (reproduced)

`git diff --name-status 9a84d392 29ca7bca` → **4 paths, all inside `allowed_paths`**:

```
A  project-control/reports/M5-T013-producer-report.md
A  services/api/app/api/v1/evidence.py
M  services/api/app/main.py
A  services/api/tests/api/test_evidence_api.py
```

`git diff --stat` → **1,549 insertions / 0 deletions** (evidence.py 518, test file 878, main.py +8,
report 145).

**Every forbidden path probed individually with `git diff --quiet 9a84d392 29ca7bca -- <path>`, all
BYTE-UNCHANGED:** `app/config.py`, `app/api/v1/{properties,rule_evaluation,scenario,scenario_analysis}.py`,
`app/profile/**`, `app/rules/**`, `app/scenario/**`, `app/spatial/**`, `app/connectors/**`,
`app/resilience/**`, `packages/contracts/**`, `apps/web/**`, `tools/**`, `supabase/**`,
`services/api/tests/scenario/**`.

`main.py` is **additive only** (+8/−0): one `from app.api.v1.evidence import router as evidence_v1_router`,
one `application.include_router(evidence_v1_router)` placed last (after `scenario_analysis_v1_router`),
and a 6-line mirroring comment. Every pre-existing registration and its order is byte-unchanged.

### 2. Applicable requirement set — DERIVED, not assumed: exactly `{D-038-R003, D-038-R004}`

1. **Repo tooling.** `DirectiveRegistry.evaluate_task_refs(M5-T013 packet)` →
   `ok: true`, `applicable_ids: ["D-038-R003","D-038-R004"]`,
   `cited_ids: ["D-038-R003","D-038-R004"]`, `missing_ids: []`, `invalid_refs: []`,
   `unresolved: []`, `reasons: []`. Registry load errors `[]`.
2. **Whole-registry sweep I ran myself**: 36 active directives, **3,641 requirement rows**, each
   evaluated with `_applicability_matches()` against this packet (`task_id=M5-T013`,
   `task_type=backend`, `milestone_id=M5`, its 4 `allowed_paths`) → exactly **2** matches, both in
   D-038: R003 (`obligation`) and R004 (`prohibition`). No `UNRESOLVED` row anywhere.
3. **Requirement text.** R001, R002, R005, R006, R007 all carry
   `applicability.task_ids = ["D-038-BOOTSTRAP"]`, the non-ledger loop-governance sentinel, so by the
   registry's conjunction semantics they bind that sentinel, not this ledger task.

**The un-cited-applicability trap is CLEAR — re-checked on the exact entry the coordinator flagged.**
`project-control/reports/M5-T013-producer-report.md` in `allowed_paths` is what makes three rows
path-intersect, and all three still fail the conjunction for a `backend`/`M5` task:

| requirement | intersecting path | also requires | attaches? |
|---|---|---|---|
| `D-004-R222` | `project-control/` | `task_types=['governance']`, `task_ids=['D-004-PHASE0','M0-T028']`, `milestones=['M0']` | **no** |
| `D-004-R240` | `project-control/reports/` | `task_types=['governance']`, `task_ids=['M0-T028']`, `milestones=['M0']` | **no** |
| `D-007-R610` | `project-control/reports/` | `task_types=['governance']`, `task_ids=['D-007-BUILD','M0-T036']` | **no** |

`services/api/app/api/v1/evidence.py` is a new file but sits in the `services/api/app/api/**` family
already cleared at M5-T012; **no** active directive scopes by those paths. So no hold-class
requirement from an un-cited directive is pulled in, and `accept()`'s fail-closed selective-citation
guard will not trip: `directive_refs = D-038:ALL` expands to exactly the applicable set,
`missing_ids = []`.

### 3. D-038-R003 (positive product deliverable) — **SATISFIED**

R003 requires the build target to be *actual PRODUCT engineering — user-facing screens, additional
deterministic rule families, or the scenario/optimization engine — contracted as a normal G0 task
packet with executable acceptance scenarios.*

* **It is product engineering, and it is the strongest R003 fit of the series so far.** R003's first
  clause names "user-facing screens (Compare/**Evidence**/report/reviewer UI)" explicitly. This is
  the Evidence surface itself — the one named in the original pivot plan and never built. It makes
  the product's central credibility claim inspectable: that every number traces to an official source
  and that nothing is presented as legally settled when it is not. `GET /api/v1/properties/{bbl}/evidence`
  (`evidence.py:375`) returns an `evidence_trail` @ `1.0.0` document carrying the profile provenance
  records, every rule citation with its own source-snapshot provenance, the evaluated-input
  provenance, and a per-claim DRAFT/Verified status. Not self-infrastructure: the three code paths
  are `services/api/**`; `tools/**` and `.claude/**` are untouched; milestone M5, `task_type=backend`.
* **It is a normal G0 packet.** `project-control/gates/M5-T013-G0.json` → `result=PASS`,
  `role=administrative`, `reviewer=orchestrator`, `reviewed_at 2026-09-10T03:40:49Z`,
  `reviewed_sha b3fa1736`, intake report `project-control/reports/M5-T013-G0-intake.md`.
  `required_gates = [G0,G1,G3,G4,G5]`, `reviewer_agents = [code-reviewer, qa-engineer, security-reviewer]`.
* **The 8 acceptance scenarios are genuinely executable — verified by running them.**
  `services/api/tests/api/test_evidence_api.py` (878 lines) collects **37 items**, each named for its
  scenario (`test_as1_*` … `test_as8_*`) with real assertions against real HTTP responses through
  `TestClient`. Reproduced to completion:
  * `python -m pytest services/api/tests/api` → **349 passed in 43.64s, exit 0** (37 evidence + 312 pre-existing)
  * `python -m pytest services/api/tests/scenario` → **388 passed in 4.09s, exit 0** — unchanged from
    the accepted M5-T012 count, **0 regression**; no pre-existing test file edited (§1)
  * `python tools/modularity_check.py --check` → **failures 0, EXIT 0** (367 files). `evidence.py`
    draws **no** warning (the one `evidence`-named warning is the pre-existing, unrelated
    `tools/agent_supervisor/evidence.py`). This also discharges the producer report's
    "ORCHESTRATOR ACTION REQUIRED" item — the producer correctly declined to run a `tools/**` command
    from a packet where `tools/**` is forbidden and it is not a documented test command; I ran it.
  * `ruff check app/api/v1/evidence.py tests/api/test_evidence_api.py` from `services/api` →
    **All checks passed!**
* **AS-5 matrix claim verified programmatically, not read.** `evidence.STATUS_STATE_MATRIX` minus
  `properties.STATUS_STATE_MATRIX` = **`[]`** — it introduces no pair; it is the property matrix
  *minus* `(500, "unsupported_contract_version")`, which the rebuild path collapses into the shared
  `(500, "internal_contract_error")`. It is also **exactly equal** to the accepted scenario route's
  matrix. The test `test_as5_every_documented_pair_is_driven` asserts `emitted == STATUS_STATE_MATRIX`
  — exhaustive in both directions, which is a stronger bar than membership.
* **AS-4 posture verified live.** Nine flag tokens (`None`, `""`, `"0"`, `"false"`, `"off"`,
  `"maybe"`, `"2"`, `"  "`, `"TRUE-ish"`) each yield `404 {"detail":"Not Found"}` with **no**
  `X-Correlation-ID`, and the disabled response is **byte-identical in body and header-set** to an
  unmounted sibling path. `/openapi.json` is **byte-identical with the flag off and on**, contains no
  occurrence of "evidence", and documents 2 paths.
* **AS-3 body-less — proven, with a control.** Two identical no-body GETs already differ in 67
  `profile_provenance[*].observation_id` leaves, because the accepted profile builder embeds the
  per-request correlation id in `obs:<correlation_id>:<bbl>:<field>` (a property of the accepted
  builder, not of this route). So I compared diff *sets*: a GET carrying a hostile body
  (`coverage_status:"verified"`, `max_residential_floor_area_sq_ft:999999`,
  `overall_verification_status:"verified"`, `gaps:[]`, `profile_provenance:[]`) produces a diff set
  **identical** to the no-body control — `999999` appears nowhere, `overall_verification_status` stays
  `'draft'`, and neither `gaps` nor `profile_provenance` is emptied. `POST/PUT/PATCH/DELETE` → **405**;
  a malformed BBL → **422 `validation_error`** with no connector call.
* **AS-6 fail-closed verified by forcing raises.** I forced a `RuntimeError(r"SECRET C:\Users\MLFLL\tok deadbeef")`
  in each stage: `build_property_profile` → `500 internal_error`; `evaluate_property` →
  `500 internal_error`; `assemble_evidence_document` → `500 internal_error`; `_assert_json_safe` →
  `500 internal_contract_error`. All four: in-matrix, `application/json`, `X-Correlation-ID` present,
  and **no** secret, filesystem path, or traceback in the body. Non-serialisable transported content
  (unpaired surrogate `\ud800`, `NaN`, `Infinity`) → `500 internal_contract_error`, in-matrix, with a
  correlation id — never an untyped `text/plain` 500. The clean 200 survives **both**
  `json.dumps(doc, allow_nan=False)` and `json.dumps(doc, ensure_ascii=False, allow_nan=False).encode("utf-8")`,
  with no `" at 0x"` leak. M5-T012's two gate findings are genuinely carried forward up front, not
  merely claimed.

### 4. D-038-R004 (no Supabase / no Geoclient) — **SATISFIED** (proven independently, not inherited)

* **Negative grep** over `evidence.py` for
  `supabase|geoclient|requests\.|httpx|socket|urllib|os\.environ|getenv|subprocess|boto3|psycopg|sqlalchemy|open\(`
  → **0 matches** (grep exit 1). No env read, no file read, no network client, no credential, no
  storage. Imports are `copy`, `json`, `logging`, `uuid`, `fastapi`, and in-repo `app.*` only.
* **No new flag, no new credential surface.** `from app.config import internal_rule_eval_enabled`
  (`evidence.py:79`) — the **pre-existing** helper (`config.py:52`, last touched at `30d6e3b4`, the
  M5-T003 integration, long before this task). `config.py` is byte-unchanged (§1) and still defines
  exactly 3 functions. The route reuses the rule-evaluation flag rather than minting one, which is
  the right choice: it surfaces that route's trail.
* **My own loopback-only egress block** (landmines on `socket.socket.connect`, `connect_ex`,
  `socket.create_connection`, `socket.getaddrinfo`, `http.client.HTTPConnection.connect`,
  `HTTPSConnection.connect`; loopback permitted so anyio's blocking portal still works):
  * evidence suite alone → **37 passed in 9.28s**, non-loopback egress attempts **`[]`**
  * **whole api suite** → **349 passed in 43.37s**, non-loopback egress attempts **`[]`**
  * my direct `assemble_evidence_document` and live-route probes → egress **`[]`** throughout
* **Facts come only from the injected seams.** `get_pluto_fetcher` / `get_spatial_substrate_provider`
  are overridden with the recorded-official PLUTO fixtures under `services/api/tests/fixtures/pluto`
  plus M2-T013 substrate dicts — the same offline harness the accepted routes' tests use.
  `dependencies = [M5-T003]`; `supabase/**` is a `forbidden_path` and byte-unchanged. The packet
  declares no Supabase/Geoclient dependency.
* For the record: the session's Supabase MCP server failed to connect during this review. That is
  **immaterial** to R004 — which requires the work to need no such credential — and I used nothing
  from it.

### 5. THE DIRECTIVE RULING — verbatim transport vs interpretation

**Ruling: the implementation HONOURS "transports existing citations verbatim and adds no legal rule."
It is NOT G6-relevant. This is not a BLOCKING finding.**

I did not take this from the producer report or from AS-2's own test. I rebuilt the profile and
rule_evaluation over the injected seams exactly as the route does, called
`assemble_evidence_document`, and then **classified every leaf** of the resulting document as
TRANSPORTED (byte-equal, by type and value, to some scalar present in either source document) or
SERVER-AUTHORED:

```
evidence doc leaves: 1339   TRANSPORTED: 1332   SERVER-AUTHORED: 7
```

**The complete server-authored surface — all 7 leaves, nothing elided:**

| leaf | value | what it is |
|---|---|---|
| `$.document_kind` | `'evidence_trail'` | structural transport label |
| `$.overall_verification_status` | `'draft'` | verification **down**-label (see below) |
| `$.rule_citations[0].claim_verification_status` | `'draft'` | verification **down**-label |
| `$.verification_scope_note` | (long disclaimer) | self-describing limitation of the above |
| `$.evidence_completeness` | `'professional_review_required'` | epistemic completeness marker |
| `$.gaps[0].kind` | `'professional_review_required'` | typed gap marker |
| `$.gaps[0].subject` | `'coverage'` | the gap's subject name |

Why none of those is a legal claim, and why that settles the G6 question:

1. **Not one of the 7 is a legal value.** No cap, floor area, FAR, district, lot dimension, section
   reference, citation text, source id, dataset id, or retrieval timestamp is server-authored. Those
   all land in the TRANSPORTED set. Spot-proofs against the source documents:
   `rule_citations[0].outputs == trace["outputs"]` **True** (and a deep copy, not an alias);
   `rule_citations[0].citations == trace["citations"]` **True** (deep copy);
   `profile_provenance == profile["provenance"]` **True** (deep copy);
   `evaluated_input.input_provenance ==` source **True**; `not_verified_disclaimer ==` source **True**;
   the canonical cap `max_residential_floor_area_sq_ft` = **15000.0**, byte-equal to the trace.
   Notably `$.gaps[0].reason` is **transported** (`'conditional'`, the source `coverage_status`), not
   authored.
2. **No arithmetic and no rewriting exist in the module.** My own scan for arithmetic operators,
   `round/sum/min/max/abs/float/int`, `.replace/.format/.join/.upper/.title/.capitalize`, and
   f-strings over `evidence.py` returned **zero** hits. I independently confirmed the producer's
   AS-2 source claims: `build_scenario` **0** occurrences, `import math` **0**, `evaluate_property(`
   exactly **1** (at `:482`).
3. **The verification labels can only ever weaken a claim.** `_verification_status` (`:206-214`) is
   the **only** site where `_VERIFICATION_VERIFIED` can be produced (grep: the constant appears at
   its definition `:128` and at `:213` only). It returns `'verified'` **only** when the source
   `coverage_status` is literally `"verified"` case-insensitively, and `'draft'` otherwise. It is a
   monotone, fail-closed echo: it cannot up-label, only down-label. Corroborating the claim that
   `'verified'` is structurally unreachable today, the canonical contract's **invalid**-fixture set
   contains `packages/contracts/fixtures/invalid/rule_evaluation/coverage_status_verified.json` — a
   draft rule_evaluation asserting `verified` is a contract violation, not a state the pipeline can
   produce. My probe observed `'draft'` at both sites.
4. **The derived markers are epistemic, not legal, and they are auditable.**
   `_completeness_marker` (`:217`) and `_gap_markers` (`:233`) classify the *state of the evidence
   trail* — complete / thin / conflicting / professional-review-required; not_available /
   not_applicable / professional_review_required / data_conflict. They say nothing about what may be
   built on the lot; they say how much of the trail is present. Decisively, **every input to those
   labels is transported verbatim alongside them**: I confirmed `source_coverage.coverage_status`,
   `.needs_review`, `.professional_review_required`, `.fail_safe`, `.fail_safe_reason` are each
   present and byte-equal to the source. A consumer can therefore always recompute or contradict the
   derived label from the document itself, which is the property that keeps a derived label from
   becoming an unauditable assertion.
5. **It mutates nothing.** After assembly, both source documents are byte-unchanged
   (`json.dumps(..., sort_keys=True)` before/after identical), and the embedded sub-structures are
   deep copies rather than aliases — so the evidence view cannot corrupt the documents it reports on.
6. **On "no new rule evaluation" and the `evaluate_property` call.** The route does call
   `evaluate_property` once (`:482`). That is not a contradiction and not a new legal rule: AS-1
   *requires* the server-side rebuild `build_property_profile → evaluate_property →
   serialize_rule_evaluation`, and it is the same accepted evaluator the accepted rule-evaluation
   route invokes, followed by `validate_rule_evaluation_document`. "No new rule evaluation" means the
   module performs no *independent* evaluation of its own, which the single call site and the
   zero-arithmetic scan together establish.

**Conclusion:** the evidence endpoint adds no legal rule and asserts no legal conclusion. It
transports, labels its own transport, and is honest about gaps. The packet's and the audit log's
"NOT G6-blocked" characterisation is correct on the evidence.

### 6. Integrity — ALL CONFIRMED

* `python tools/validate_directive_compliance.py --check` → **EXIT 0** (silent pass).
* **CRLF-byte digest.** `requirements.json` on disk: **9,350 bytes, 260 CRLF, 0 bare LF**. `sha256`
  of those exact bytes, **un-normalised** =
  `f62c6fc8cec2497af0d6170d232559df79544fe06239f44b80bea1bea0f39f0b` ==
  `manifest.requirements_content_digest_sha256`. ✓ (The LF-normalised value is `0e9de4cc…`, the git
  blob sha — not the digest; `.gitattributes` pins `project-control/directives/** text eol=lf`, so
  the committed object is LF while the working file is CRLF and git reports it clean.)
* **Source digest** `sha256(source-001.md)` (1,599 B) = `a237dd50…` == `manifest.sources[0].content_digest_sha256`. ✓
  `amendments: []`.
* **`locked_requirement_ids` unchanged at `[R001..R007]`**, equal to the on-disk ids and to
  `requirement_count` 7; no id added, removed, or renumbered. ✓
* **Digest transition verified at BOTH ends against the actual bytes**, not just against the note:
  CRLF-encoded `requirements.json` hashes to **`32f8d252`** at `9a84d392^` (where the manifest
  claimed `32f8d252`) and to **`f62c6fc8`** at `9a84d392` and at `29ca7bca` (where it claims
  `f62c6fc8`). `locked` = 7 at all three; `audit_log` 10 → 11 entries. ✓
* **The append was applicability-only.** `git diff 9a84d392^ 9a84d392 -- requirements.json` is exactly
  **two hunks, `+"M5-T013"` added to `applicability.task_ids` of R003 and of R004** — no requirement
  text, classification, binding, dependency, or evidence field changed. ✓
* **audit_log[-1]** = `2026-09-10T03:40:00+00:00`, actor `orchestrator`, action
  `applicability_appended`; its note names M5-T013, describes the endpoint, asserts "No requirement
  id added, removed or renumbered (locked_requirement_ids unchanged); no source text changed", and
  states the resync "from 32f8d252 to f62c6fc8". Both ends verified above. ✓

### 7. Material content identity at `29ca7bca` — via the accept path's own routine

```python
import sys; sys.path.insert(0, "tools")
import project_control as pc
reg_mod = pc._resolver()
t = pc.load(pc.PC / "tasks" / "M5-T013.json")
identity, resolved_sha, ierr = pc._task_git_identity(reg_mod, t)   # reviewed_sha=None -> HEAD
```

```
identity     = ebf8f4d9ac73ca23df20891b29284f2af9a18d5de9187f8d30c00ee3e7ebdc68
first 8      = ebf8f4d9
resolved_sha = 29ca7bca83c163957f6b0aa2ddc9a48b7f158a57
error        = None
```

* **Function:** `tools/project_control.py::_task_git_identity(reg_mod, task_dict)` with
  `reviewed_sha=None` — the exact call `accept()` makes through `_directive_accept_reasons`
  (`project_control.py:532`, invoked at `:1254`). It delegates to
  `directive_registry.frozen_git_identity(allowed_paths, reviewed_sha=None, root=ROOT,
  exclude_prefixes=('project-control/',), require_clean=True,
  control_plane_prefixes=('project-control/',), allow_empty_identity=False)`.
  `path_free_opt_in()` → `(False, None)`, so the empty-identity guard stays armed.
* **Blob composition (4 objects, reproducible):**

  | component | path | blob |
  |---|---|---|
  | raw-blob | `services/api/app/api/v1/evidence.py` | `dd69e05e12a59033f860b5340159de23382932bd` |
  | raw-blob | `services/api/app/main.py` | `128593c65bc96a03b5a7e9c547880c6545b6732f` |
  | raw-blob | `services/api/tests/api/test_evidence_api.py` | `be001e8dc923c668d085698a9dd93827b37bd596` |
  | control-plane material | `project-control/reports/M5-T013-producer-report.md` | `2c5e1899046d220a19045f5d71cde3f40e256567` |

  Raw-blob component = `9a33cc44ea25e9ef7340ab72f3eff0ccec63429f9e91d7d3102a6dabcfb521b4`;
  `_hash_manifest_entries(raw_blobs + control_plane)` = `ebf8f4d9…`.
* **Dirt guard passed (`err = None`).** The worktree is clean apart from three untracked items
  (`.claude/agent-memory/qa-engineer/*`, `scratchpad/`), none inside `allowed_paths`.
* **Validity window:** this identity binds **only** `29ca7bca`. Any rework touching one of those four
  blobs produces a different identity, and the verification row must then be re-issued.

### 8. Accept simulation

Appending a candidate M5-T013 row and calling
`reg.task_verification_result('D-038','M5-T013',{R003,R004},'ebf8f4d9…',reviewed_sha='29ca7bca…')`:

```
reasons  : []
deferrals: []
-> ROW SHAPE SATISFIES THE ACCEPT GATE (nothing to defer)
```

Confirmed for **both** row shapes: the full shape, and the **exact minimal shape the accepted
M5-T012 row uses** (container carries `applicable_requirement_ids`, `reviewed_sha`,
`reviewed_manifest_sha256`, `producer`, `verifier`, `schema_version`, `verified_at`, `note`; each
requirement row carries only `id`, `state`, `evidence`). Both return `reasons: []`, `deferrals: []`.

**Negative control** (the accepted M5-T012 identity/SHA queried against the M5-T013 row) is correctly
refused, proving the check is live rather than vacuous:

```
D-038/M5-T013: verification is stale -- recorded at content identity ebf8f4d9..., current is e5c95c27...
D-038/M5-T013: verification reviewed_sha is stale -- recorded at commit 29ca7bca..., current reviewed commit is 12fda82f... (fail closed)
```

### 9. Gate/lifecycle state observed (process context, not a D-038 finding)

The packet is `status: claimed`, `progress_percent: 10`. Only **G0** is recorded
(`M5-T013-G0.json`, PASS, administrative). **G1, G3, G4 and G5 have no record yet**, and there is no
submit report `project-control/reports/M5-T013.json` — so `accept()` would currently refuse on the
four missing gates and on the frozen-evidence comparison, independently of anything in this report.
That is the normal pre-gate position for a task whose producer output has just landed; the gate wave
and `submit` at this HEAD are the remaining steps. Nothing here blocks the D-038 verdict.

### 10. Non-blocking observations

* **Producer digest claims use two different line-ending bases, and the report does not say which.**
  Its table claims `evidence.py` = `0329a469…`, which matches the **git blob (LF, 23,676 B)** — not
  the on-disk CRLF bytes (`8742057…`); and `main.py` = `97be9148…`, which matches the **on-disk CRLF
  bytes (7,495 B)** — not that file's git blob (`b6930f0c…`). Both digests are genuine digests of the
  real content, so there is **no drift and no tampering**; the likely cause is mixed line endings in
  the producer's own worktree (`wt-m5t013`). But a reviewer reproducing with the one-liner the report
  itself supplies (`pathlib.read_bytes()`, which yields CRLF on this machine) will see `evidence.py`
  **mismatch** and `main.py` match, which reads alarming and is not. Worth one clarifying line in the
  report stating the basis per row. Outside R003/R004.
* **`_completeness_marker` coarsens, losslessly.** Distinct source states collapse into one label —
  e.g. `coverage_status` `"unsupported"` and `"not_applicable"` both map to `thin`. That is a
  coarsening, not a meaning change, because the precise machine value rides alongside verbatim in
  `source_coverage.coverage_status` **and** is named again in a typed `not_applicable` gap marker
  carrying `reason: <coverage>`. Worth a reviewer's eye for UI consumers that might key off the coarse
  label alone; not a directive issue.
* **Producer report ↔ reality: no drift in substance.** It records **349 / 388** — exactly what I
  reproduced — its post-trim line spans resolve, and its candid "ORCHESTRATOR ACTION REQUIRED"
  modularity item is now discharged (I ran the check: failures 0, exit 0, `evidence.py` unwarned). Its
  self-reported "comment-only trim" claim is consistent with what I verified independently (the AS-2
  source-scan invariants hold: `build_scenario` 0, `import math` 0, `evaluate_property(` exactly 1).
* **`tools/test_directive_compliance.py`: I did NOT run it, and make no claim about it.** My earlier
  attempt in this session was killed without producing a byte. It is not a packet-documented command
  and not required by the brief; the integrity evidence in §6 rests on
  `tools/validate_directive_compliance.py --check` → **EXIT 0**.

### 11. Worktree left as found

`git status --short` at finish shows only the three pre-existing untracked items
(`.claude/agent-memory/qa-engineer/MEMORY.md`,
`.claude/agent-memory/qa-engineer/feedback_probe_separator_deleting_normalizations.md`,
`scratchpad/`) plus this report. I touched nothing else. My probe scripts (`dcv_netblock.py`,
`dcv_m5t013_verbatim.py`, `dcv_m5t013_route.py`, `dcv_m5t013_bodyless.py`) live outside the
repository in the session scratchpad.
