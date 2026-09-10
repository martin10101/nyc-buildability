# M5-T012 — Directive-Compliance Verification (DCV) vs D-038 (verbatim verifier return)

Verifier: **directive-compliance-verifier** (independent). Reviewed SHA `aafc75fd1a490618f51cbc86af459412f594c983`;
material identity `c80cbb0cfbeb807ea3245b82792f367bea3c862a3fb090066b02aa042cc11aba`.

---

## DCV REPORT — task M5-T012 vs directive D-038 (independent)

**Verdict: PASS** (directive compliance) — **with one BLOCKING finding that forbids acceptance at this SHA** (see §8).

| field | value |
|---|---|
| `reviewed_sha` | `aafc75fd1a490618f51cbc86af459412f594c983` (confirmed `git rev-parse HEAD`; branch `candidate/D-024-mrl-option-b`) |
| `reviewed_manifest_sha256` | `c80cbb0cfbeb807ea3245b82792f367bea3c862a3fb090066b02aa042cc11aba` (first 8: `c80cbb0c`) |
| applicable requirement set | exactly `{D-038-R003, D-038-R004}` — derived, not assumed |
| `validate_directive_compliance.py --check` | **EXIT 0** |
| platform | Python 3.11.9, pytest 8.4.2, Windows 11. Read-only throughout. |

### 0. Independence statement

I am **not** the producer of any artifact under review and **not** any of the four gate reviewers.

* Producer of the code/tests/report at `edc43f4f` and the rework at `aafc75fd`: `backend-engineer`
  (build-loop worker), committed by the orchestrator under its worktree-commit duty.
* Gate reviewers recorded for this task: `code-reviewer` (G1 at `aafc75fd`, G4 at `aafc75fd`),
  plus `qa-engineer` / `security-reviewer` named in `reviewer_agents`. I recorded no gate, and I
  reproduced every claim below from primary evidence (git objects, the files themselves, and my own
  command runs) rather than from any producer or reviewer narrative. Where I cite the G1 report I
  state explicitly that I **independently reproduced** the claim (§8).
* Writes performed by me: **only** this report file. I did not touch product code, tests, the task
  packet, `state.json`, `verification.json`, `manifest.json`, `requirements.json`, or any gate
  record. I ran no `tools/project_control.py` write subcommand and no git/gh write command. The
  orchestrator writes the `verification.json` row from this return; I did not write it.

### 1. Scope / diff identity (reproduced)

`git diff --name-status c83206c2 aafc75fd` → exactly 4 paths, **all inside `allowed_paths`**, no
forbidden path touched:

```
A  project-control/reports/M5-T012-producer-report.md
A  services/api/app/api/v1/scenario_analysis.py
M  services/api/app/main.py
A  services/api/tests/api/test_scenario_analysis_api.py
```

Commit arc reproduced: `c83206c2` (packet contracted, G0 PASS) → `edc43f4f` (producer output,
+1564/-0 over the 4 paths) → `aafc75fd` (rework, 2 files: the test file +105/-12 and the producer
report +186/-1).

`services/api/app/main.py` is **additive only** (`git diff c83206c2 aafc75fd -- services/api/app/main.py`
= +8/-0): one `from app.api.v1.scenario_analysis import router as scenario_analysis_v1_router`, one
`application.include_router(scenario_analysis_v1_router)` placed after the existing
`include_router(scenario_v1_router)`, and a 6-line comment mirroring the M5-T003 registration. Every
pre-existing registration and its order is byte-unchanged. `app/config.py`, `app/api/v1/scenario.py`,
`app/api/v1/rule_evaluation.py`, `app/api/v1/properties.py`, `services/api/app/scenario/**`,
`packages/contracts/**`, `apps/web/**`, `tools/**` are all byte-unchanged across the arc.

### 2. Applicable-requirement set — DERIVED, not assumed: exactly `{D-038-R003, D-038-R004}`

I did not take R003/R004 on the orchestrator's word. Three independent derivations agree:

1. **Repo tooling.** `DirectiveRegistry.evaluate_task_refs(M5-T012 packet)`
   (`tools/directive_registry.py:651`) →
   `{"ok": true, "applicable_ids": ["D-038-R003","D-038-R004"], "cited_ids": ["D-038-R003","D-038-R004"],
   "missing_ids": [], "invalid_refs": [], "unresolved": [], "reasons": []}`.
2. **Whole-registry sweep I ran myself** over `reg.active_directives()` — **36 active directives,
   3,767 requirement rows** — calling `_applicability_matches()` per row against this packet
   (`task_id=M5-T012`, `task_type=backend`, `milestone_id=M5`, its 4 `allowed_paths`). Exactly **2**
   rows match, both in D-038: R003 and R004. Every other directive contributes **0**.
3. **Requirement text.** R001, R002, R005, R006, R007 each carry
   `applicability.task_ids = ["D-038-BOOTSTRAP"]` — the non-ledger loop-governance sentinel — so by
   the registry's conjunction semantics they bind the bootstrap sentinel, not this ledger task.

**The un-cited-applicability trap is CLEAR — no BLOCKING finding there.** `services/api/app/api/**`
is indeed a new path family for the D-038 product line (every prior D-038 product task touched only
`services/api/app/scenario/**`), so I checked it specifically. Only three requirements in the whole
active registry have a non-empty `applicability.paths` that intersects this packet's `allowed_paths`,
and all three intersect through the *shared* `project-control/reports/` entry, not through the new
API path family:

| requirement | intersecting path | why it does NOT attach |
|---|---|---|
| `D-004-R222` | `project-control/` | conjunction also demands `task_types=['governance']`, `task_ids=['D-004-PHASE0','M0-T028']`, `milestones=['M0']` |
| `D-004-R240` | `project-control/reports/` | also demands `task_types=['governance']`, `task_ids=['M0-T028']`, `milestones=['M0']` |
| `D-007-R610` | `project-control/reports/` | also demands `task_types=['governance']`, `task_ids=['D-007-BUILD','M0-T036']` |

M5-T012 is `task_type=backend`, `milestone_id=M5` → none attaches. **No hold-class requirement from
an un-cited directive is pulled in by this packet's paths**, so `accept()`'s fail-closed
selective-citation guard will not trip. `directive_refs = D-038:ALL` expands to exactly the
applicable set, `missing_ids = []`.

### 3. Per-requirement verdicts

#### D-038-R003 (positive product deliverable) — **SATISFIED**

R003 requires the loop's build target to be *actual PRODUCT engineering — user-facing screens,
additional deterministic rule families, **or the scenario/optimization engine** — contracted as a
normal G0 task packet with executable acceptance scenarios*.

* **It is product engineering, and it is within R003's terms.** `services/api/app/api/v1/scenario_analysis.py`
  (699 lines, new) exposes the four **accepted** optimization-engine functions over the internal
  product API: `post_sensitivity` (:556) → `analyze_scenario_sensitivity` (M5-T008), `post_ranking`
  (:589) → `rank_scenario_assumption_sets` (M5-T007), `post_comparison` (:624) →
  `compare_scenario_assumption_sets` (M5-T010), `post_threshold` (:657) → `find_scenario_threshold`
  (M5-T011). My judgement, stated plainly: *exposing the optimization toolkit over the internal API
  is squarely inside R003's third clause.* R003 names "the scenario/optimization engine" as a valid
  build target, and an engine reachable only from a Python REPL is not yet product; this module is the
  product surface of that engine — it is the consumable seam the parked Compare (Step-3) UI M5-T004
  needs, and it is the landing pad the incoming credentials plug into without re-shaping the surface.
  It is **not** supervisor/control-plane self-infrastructure: `allowed_paths` are three
  `services/api/**` product files plus one report; `forbidden_paths` explicitly exclude `tools/**`
  and `.claude` is untouched; milestone M5, `task_type=backend`.
* **It is a normal G0 packet.** `project-control/gates/M5-T012-G0.json` → `result=PASS`,
  `role=administrative`, `reviewed_at 2026-09-09T20:13:02Z`, `reviewed_sha 52e98d5e`, intake report
  `project-control/reports/M5-T012-G0-intake.md`. `required_gates = [G0,G1,G3,G4,G5]`,
  `reviewer_agents = [code-reviewer, qa-engineer, security-reviewer]`, `producer_agent = backend-engineer`.
* **The 8 acceptance scenarios are genuinely executable — verified, not assumed.**
  `services/api/tests/api/test_scenario_analysis_api.py` (816 lines) carries 21 test functions that
  parametrize to **75 collected items**, each named for its scenario (`test_as1_*` … `test_as7_*`),
  with real assertions against real HTTP responses through `TestClient`. I reproduced both
  packet-documented commands **to completion** on this machine:
  * `python -m pytest services/api/tests/api` → **216 passed in 23.79s, exit 0** (141 pre-existing + 75 new)
  * `python -m pytest services/api/tests/scenario` → **388 passed in 4.03s, exit 0** (identical to the
    M5-T011 accepted count → **0 regression**; no pre-existing test file was edited)
  * `python tools/modularity_check.py --check` → **exit 0**, 366 files selected, failures 0;
    `scenario_analysis.py` appears in **no** warning (the 15 warnings are pre-existing `tools/**`,
    `apps/web/**` and `app/scenario/breakeven.py` signals).
  The AS-7 rework is real and load-bearing: the deadlocking `monkeypatch.setattr(socket,'socket',…)`
  was replaced by egress-seam landmines (`pluto_soda._OPENER`, `resilience.transport.DEFAULT_OPENER`,
  `http.client.HTTP(S)Connection.connect`, `socket.create_connection`) that both **record** and raise,
  asserted as `egress == []` (test file :716-816). I proved the assertion is not vacuous by my own
  **RED check**: with the fixture seams removed, the same request path really does attempt
  `http.client.HTTPSConnection.connect → data.cityofnewyork.us`, which those landmines catch (§4).
* **Honest qualification (does not change this verdict).** AS-2's and AS-6's *contracted text* is
  violated at `aafc75fd` by the defect at §8 (a nested fact key is echoed, and the producer's own
  AS-6 helper then sees `'verified'`), and the AS-2/AS-6 tests pass only because they probe fact keys
  at the top level. That is a **product-quality defect owned by the G1–G5 gates**, not an R003
  violation: R003's obligation (`producer: orchestrator`, `required_evidence: "a contracted product
  task packet (G0) whose scope is user-facing/domain product, with acceptance scenarios; loop pointed
  at it"`) is about the *nature of the build target* and the *contracting*, and both are met. This
  follows the directive's own precedent: the M5-T011 DCV row records `R003/R004 PASS` at `bbf3267f`
  while G5 simultaneously held a BLOCKING `RecursionError`. I record the defect as a BLOCKING
  **acceptance** finding in §8 rather than laundering it into an R003 pass or duplicating G1.

#### D-038-R004 (no Supabase / no Geoclient; must build AND verify without the deferred credentials) — **SATISFIED**

* **Import inspection** (`scenario_analysis.py:62-101`): `json`, `logging`, `uuid`, `typing.Any`,
  `fastapi`, and in-repo `app.*` modules only. Negative grep over the whole module for
  `supabase|geoclient|requests\.|httpx|socket|urllib|os\.environ|getenv|subprocess|boto3|psycopg|sqlalchemy|open\(`
  → **0 matches** (exit 1). No env read, no file read, no network client, no credential.
* **No new flag, config untouched.** `from app.config import internal_scenario_enabled` (:79) — the
  *existing* M5-T003 helper; `app/config.py` is byte-unchanged across the arc (§1). All four routes
  gate on `if not internal_scenario_enabled(): return _not_found()` (:566/:599/:634/:667).
* **Facts come only from the trusted injected seams.** Each endpoint rebuilds server-side through
  `get_pluto_fetcher` → `build_property_profile` → `evaluate_property` → `serialize_rule_evaluation`
  → `build_scenario` with `get_spatial_substrate_provider` (`_rebuild_scenario` :411), i.e. the same
  FastAPI dependency seams the accepted M5-T003 route uses, which tests override with recorded-official
  PLUTO fixtures under `services/api/tests/fixtures/pluto`.
* **Independent offline proof (mine, not the producer's).** I armed a process-wide loopback-only
  egress block as a pytest plugin (landmines on `socket.socket.connect`, `connect_ex`,
  `socket.create_connection`, `socket.getaddrinfo`, `http.client.HTTPConnection.connect`,
  `HTTPSConnection.connect`; loopback allowed so anyio's blocking portal still works — the exact
  distinction the rework was about) and ran the new suite under it:
  `75 passed in 10.10s`, **non-loopback egress attempts: `[]`**. No Supabase, no Geoclient, no DNS,
  no outbound socket.
* **No credential can even be read.** The AS-7 test deletes `pluto_soda.APP_TOKEN_ENV_VAR` and then
  asserts it is absent from `os.environ` and that no `x-app-token` header reaches the transport
  (test file :810-816). `dependencies = [M5-T003, M5-T011]`; the packet declares no Supabase/Geoclient
  dependency, and its `forbidden_paths` include `supabase/**`.

#### Requirements NOT applicable to this task (stated with the reason, per the brief)

| id | class | applicable to M5-T012? | why |
|---|---|---|---|
| `D-038-R001` (keep the loop running nonstop; re-armed read-only break watcher; D-035 restart drill; relaunch DETACHED from `wt-controller-src`) | obligation | **NOT_APPLICABLE** | `applicability.task_ids = ["D-038-BOOTSTRAP"]` only. It is a **loop-governance** duty on the orchestrator/supervisor session, discharged by supervisor-liveness and watcher evidence, not by anything a backend task packet can produce. Nothing in M5-T012's scope (`services/api/**` + one report) can satisfy or violate it. |
| `D-038-R002` (PROHIBITION: no further supervisor/control-plane **self-infrastructure** as the build target while unblocked product work exists; do not advance to M0-T155) | prohibition | **NOT_APPLICABLE** *(and substantively honoured)* | Sentinel-bound (`task_ids=["D-038-BOOTSTRAP"]`), so it does not attach to this packet. **Confirmed anyway, as the brief asks:** M5-T012 is product, not self-infra — all three code paths are `services/api/**` product files, `tools/**` and `.claude/**` are untouched (§1), the packet is milestone M5 / `task_type=backend`, and M0-T155 is not this build target. The loop is pointed at product, exactly as R002 requires. |
| `D-038-R005` (OWNER DECISION / carry-forward: Supabase B-001 + Geoclient B-004 are the real unlock, deferred this session only; surface as the primary next-session ask) | decision, `binding: false` | **NOT_APPLICABLE** | Sentinel-bound, non-binding, and discharged by a **handoff record**, not by task code. It explicitly "does not block this session's product work". Consistent with this task: the packet's `business_reason` names it as the landing pad for the incoming credentials, and the manifest `audit_log[-1]` records the owner's signal that the credentials are arriving — but neither is R005 evidence produced by M5-T012. |
| `D-038-R006` (AUTHORITY / no-bypass: no push/PR/merge, never merge PR #241, R595 owner-only, expansion hold, supervisor SHADOW, launch only from `wt-controller-src`, normal G0–G7) | prohibition | **NOT_APPLICABLE** *(corroborated)* | Sentinel-bound. Corroborated read-only anyway: `git branch -r --contains aafc75fd` → **empty**, and `candidate/D-024-mrl-option-b` has **no upstream** → nothing was pushed; gates are being recorded through the normal wave (G0/G1/G4 records present) with no self-accept. |
| `D-038-R007` (RETURN REPORT to the owner, generated from the completed matrix) | return | **NOT_APPLICABLE** | Sentinel-bound; it is an owner-facing return obligation on the orchestrator, discharged at session return, not by a task packet. |

### 4. Load-bearing proof of the AS-7 rework (my own RED check)

With `app.dependency_overrides` cleared (no fixture fetcher, no fixture substrate) and my
loopback-only block armed, a live `POST /api/v1/properties/1000010100/scenario/comparison` recorded:

```
recorded non-loopback egress attempts: [('http.client.HTTPSConnection.connect', 'data.cityofnewyork.us')]
RED PROOF: LOAD-BEARING (real egress attempted)
status: 500            # typed, logged by correlation id — no traceback to the client
```

`http.client.HTTPSConnection.connect` is one of the five seams the AS-7 test landmines, so the
`egress == []` assertion genuinely fails the moment a real outbound path exists. The rework replaced a
deadlock with a real guarantee; it did not paper one over (no `sleep`, no timeout, no
`sys.setrecursionlimit`).

### 5. Integrity checks — ALL CONFIRMED

* `python tools/validate_directive_compliance.py --check` → **EXIT 0** (silent pass; ~4 min wall clock).
* **`requirements_content_digest_sha256` vs the on-disk bytes.** `requirements.json` on disk is
  **9,316 bytes, 258 CRLF, 0 bare LF**. `sha256` of those exact bytes, **not normalised**:
  `32f8d252e948164c2895c938c916426853471fb61e00446e16cd78fb0bf61c95` ==
  `manifest.requirements_content_digest_sha256`. ✓ (For the record: the LF-normalised digest is
  `7d78a261…`, which is the *git blob* sha — `.gitattributes:6` pins `project-control/directives/** text eol=lf`
  and `git check-attr` confirms `text: set, eol: lf`, so the git object is LF while the working file is
  CRLF and git reports it clean. The digest is over the **on-disk CRLF bytes**, as the brief states.)
* **Source digest unchanged.** `sha256(source-001.md)` (1,599 bytes) =
  `a237dd50672e4745aff5dc5b19cf79506252a0ff0742184576f99b29f7962212` == `manifest.sources[0].content_digest_sha256`. ✓
  No amendment files; `amendments: []`.
* **`locked_requirement_ids` unchanged; no id added, removed, or renumbered.** On-disk ids
  `[R001..R007]` == `locked_requirement_ids` == 7 == `requirement_count`. Reproduced across the append
  commit: at `c83206c2^` the ids were `[R001..R007]` with 7 locked; at `c83206c2` and at HEAD they are
  identical. ✓
* **The append was applicability-only.** `git diff c83206c2^ c83206c2 -- requirements.json` is exactly
  **two hunks, `+"M5-T012"` added to `applicability.task_ids` of R003 and of R004, nothing else** — no
  requirement text, classification, binding, dependency, or evidence field changed. ✓
* **audit_log note + digest transition.** `audit_log[-1]` = `2026-09-09T12:10:00+00:00`, actor
  `orchestrator`, action `applicability_appended`, and it records the M5-T012 append, the R003
  contracted-tasks mechanism, "No requirement id added, removed or renumbered (locked_requirement_ids
  unchanged); no source text changed", and the resync "from 37035a7d to 32f8d252". **Both ends verified
  against reality**, not just against each other: the CRLF-encoded `requirements.json` at `c83206c2^`
  hashes to `37035a7d…` and at HEAD to `32f8d252…`; the manifest at `c83206c2^` claimed `37035a7d` and
  at HEAD claims `32f8d252`; audit_log grew 9 → 10 entries. ✓

### 6. Material content identity — computed via the accept path's own routine

The accept path's check is, verbatim, `identity, resolved_sha, ierr = _task_git_identity(reg_mod, t)`
inside `tools/project_control.py::_directive_accept_reasons` (`:532`, called from `accept()` at `:1254`),
which compares `identity` against the submit report's `content_manifest_sha256` and then passes it as
`reviewed_manifest_sha256` into `DirectiveRegistry.task_verification_result`. **I called that same
function**, not a reimplementation:

```python
import sys; sys.path.insert(0, "tools")
import project_control as pc
reg_mod = pc._resolver()
t = pc.load(pc.PC / "tasks" / "M5-T012.json")
identity, resolved_sha, ierr = pc._task_git_identity(reg_mod, t)   # reviewed_sha=None -> HEAD
```

```
identity     = c80cbb0cfbeb807ea3245b82792f367bea3c862a3fb090066b02aa042cc11aba
first 8      = c80cbb0c
resolved_sha = aafc75fd1a490618f51cbc86af459412f594c983
error        = None
```

* **Exact function to reproduce:** `tools/project_control.py::_task_git_identity(reg_mod, task_dict)`
  with `reviewed_sha=None` (→ HEAD). It delegates to
  `tools/directive_registry.py::frozen_git_identity(allowed_paths, reviewed_sha=None, root=ROOT,
  exclude_prefixes=('project-control/',), require_clean=True,
  control_plane_prefixes=('project-control/',), allow_empty_identity=False)`.
  `path_free_opt_in()` → `(False, None)`, so the empty-identity guard stays armed (and is not needed:
  the manifest is non-empty).
* **Composition (4 objects, fully reproducible).** Raw-blob component `cd839f9b…` over
  `services/api/app/api/v1/scenario_analysis.py` blob `0a89fb3f`, `services/api/app/main.py` blob
  `071f7755`, `services/api/tests/api/test_scenario_analysis_api.py` blob `bffec62d`; control-plane
  material component over `project-control/reports/M5-T012-producer-report.md` blob `76150390`.
  `_hash_manifest_entries(blob_entries + control_plane_entries)` = `c80cbb0c…`.
* **Independent corroboration from the repo's own write path:** the two gate records the orchestrator
  wrote during my review, `project-control/gates/M5-T012-G1.json` and `-G4.json`, both carry
  `content_manifest_sha256 = c80cbb0cfbeb807ea3245b82792f367bea3c862a3fb090066b02aa042cc11aba` at
  `reviewed_sha = aafc75fd…`. Same value, produced by `gate()`'s call to the same helper.
* **Dirt guard passed (`err = None`)** even though the working tree carries the orchestrator's
  pre-existing `project-control/state.json`, `project-control/tasks/M5-T012.json`, the untracked
  `.claude/agent-memory/qa-engineer/*`, `scratchpad/`, and the newly written `M5-T012-G1/G4` records:
  none of them is inside this packet's `allowed_paths`, so none enters the scoped cleanliness check.
* **Row-shape simulation (in memory, no file written).** I appended a candidate M5-T012 row mirroring
  the M5-T011 row's shape (`applicable_requirement_ids: [R003,R004]`, `reviewed_sha aafc75fd…`,
  `reviewed_manifest_sha256 c80cbb0c…`, `verifier: directive-compliance-verifier`, both requirement
  rows `state: PASS` with `verified_by`/`verified_at`/`reviewed_sha`) to an in-memory copy of the
  registry and called
  `reg.task_verification_result('D-038','M5-T012',{R003,R004}, 'c80cbb0c…', reviewed_sha='aafc75fd…')`
  → **`reasons: []`, `deferrals: []`**. That row shape satisfies the accept gate's verification check
  with no acceptance-ordering deferral to record.
* **Validity window.** This identity binds **only** `aafc75fd`. Any rework commit that changes one of
  those four blobs (which the §8 fix will) produces a **different** identity, and this verification
  row must then be re-stamped at the new SHA before accept.

### 7. Submit/gate state observed (context for the orchestrator, not a D-038 finding)

At the time of this review the packet is `status: in_progress`, `progress_percent: 90`; there is **no**
`project-control/reports/M5-T012.json` submit report yet, so `accept()`'s frozen-evidence comparison has
nothing to compare against until `submit` stamps `content_manifest_sha256`. Gate records present:
`G0 PASS` (administrative, `52e98d5e`), `G1 **FAIL**` (code-reviewer, `aafc75fd`), `G4 PASS`
(code-reviewer, `aafc75fd`). `G3` and `G5` have no record yet. `required_gates = [G0,G1,G3,G4,G5]`, so
`accept()` will refuse on "required gate G1 has no PASS record" / "required gate G3 has no PASS record"
/ "required gate G5 has no PASS record" independently of anything in this report.

### 8. BLOCKING finding (acceptance): G1's BLOCKING-1 — independently reproduced

This is **not** a D-038-R003/R004 violation (§3), and it is **not** an applicability/citation problem
(§2). It is a blocking reason the task **must not be accepted at `aafc75fd`**, and I report it because I
reproduced it myself rather than relaying the gate report.

`FORBIDDEN_FACT_KEYS` is enforced **only at the top level** —
`scenario_analysis.py:348` `injected = sorted(FORBIDDEN_FACT_KEYS & set(body.keys()))` — while the
iterative walk at `:263-295` that already visits every nested key tests only string length. My
reproduction, offline, through the producer's own fixture harness, with my loopback-only egress block
armed (`non-loopback egress attempts: []`):

```
POST /api/v1/properties/1000010100/scenario/ranking
{"objective": "maximize_illustrative_usable_area",
 "assumption_sets": [[{"assumption_type": "utilization_factor", "value": 0.8,
                       "draft_zoning_floor_area_cap_sq_ft": 987654321,
                       "coverage_status": "verified", "verified": true,
                       "rule_evaluation": {"outputs": {"max_residential_floor_area_sq_ft": 987654321}}}]]}

-> status: 200
-> envelope["scenario_cap_sq_ft"]: 15000.0          (authoritative cap intact)
-> test module's own _coverage_values(envelope): ['conditional', 'verified', 'conditional', 'conditional']
-> AS-6 assertion "'verified' not in coverage"  WOULD: FAIL
-> attacker value 987654321 echoed in the 200 body under the canonical cap key name: True
-> the SAME keys sent at top level: 422           (so the boundary exists, at the wrong scope)
```

Consequences, stated precisely so this is not over-read: the **authoritative** cap is safe
(`scenario_cap_sq_ft` stayed at the server-rebuilt `15000.0`, because each engine merges caller data
only as `{**scenario_document, "assumptions": <caller data>}`). What is broken is the packet's own
contracted boundary: **AS-2** ("a body that supplies or attempts to override a fact … is REJECTED with
a typed 422 … and is NEVER merged into the server-rebuilt document") and **AS-6** ("no response is
marked Verified"). A 200 body that carries an attacker-chosen number under the exact canonical cap key
name alongside `"coverage_status": "verified"` is the forged-fact surface this task was shaped to
prevent, and any consumer that greps for those key names — including the parked Compare UI M5-T004 —
finds the forgery. The AS-2/AS-6 tests pass today only because no test sends a fact key one level down.

**Required before accept:** the fix (G1 specifies the minimal one — test each dict key against
`FORBIDDEN_FACT_KEYS` inside the existing iterative walk at `:285`, plus two new tests), then G1
re-gated PASS and G3/G5 recorded PASS. Because the fix changes blobs inside `allowed_paths`, the
material identity will move off `c80cbb0c…` and this verification row must be re-issued at the new SHA.

### 9. Non-blocking observations (for the orchestrator's backlog, outside R003/R004)

* **Pre-existing branch-wide lint red, not caused by M5-T012.** The producer report §7 discloses that
  `ruff check .` from `services/api` reports 27 errors, **none** in a file this task touched — all in
  `app/scenario/{comparison,ranking,sensitivity,breakeven}.py` and `tests/scenario/*`, i.e. files
  carried in from earlier *accepted* M5 work and all inside this packet's `forbidden_paths`. The CI job
  `api (ruff + pytest)` will stay red until they are cleaned up, independently of this task. No push is
  held on it (nothing is pushed at all).
* **Python 3.11 vs CI 3.12 gap** (pre-existing, disclosed): `app/documents/units.py:276` uses PEP-695
  generic syntax, so the wider `pytest -q` from `services/api` cannot be collected locally. Neither
  `tests/api` nor `tests/scenario` imports `app.documents`, so both packet-documented commands are
  unaffected; I ran both to completion on 3.11.9.
* **Producer report ↔ reality: no drift in the numbers.** The report claims 216 / 388 passed; I
  reproduced exactly 216 / 388. Its §8 rework account matches the code. Its two claims at `:108`
  ("Nothing is ever marked Verified") and `:98` ("Every non-disabled response carries
  `X-Correlation-ID`") are contradicted by §8 / G1's HIGH-1 respectively and should be corrected in the
  same pass as the fix.
* `python -m pytest tools/test_directive_compliance.py` was still running when this report was
  finalized (the registry harness is long-running on this machine; `validate_directive_compliance.py
  --check`, the brief's required command, completed with **EXIT 0**). I make no claim about its result.

### 10. Worktree left as found

`git status --short` at finish: ` M project-control/state.json`, ` M project-control/tasks/M5-T012.json`,
`?? .claude/agent-memory/qa-engineer/MEMORY.md`,
`?? .claude/agent-memory/qa-engineer/feedback_probe_separator_deleting_normalizations.md`,
`?? project-control/gates/M5-T012-G1.json`, `?? project-control/gates/M5-T012-G4.json`,
`?? project-control/reports/M5-T012-G1.md`, `?? project-control/reports/M5-T012-G4.md`,
`?? scratchpad/` — all pre-existing orchestrator/gate state that I did not touch (the G1/G4 records
appeared during my review, written by the concurrent gate wave). My only write is this file. My
scratch scripts (`dcv_netblock.py`, `dcv_red_egress.py`, `dcv_blocking1_repro.py`) live outside the
repository in the session scratchpad.
