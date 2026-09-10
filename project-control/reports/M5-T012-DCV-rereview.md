# M5-T012 — Directive-Compliance RE-REVIEW (DCV) vs D-038, at reworked SHA `12fda82f`

Supersedes nothing: `project-control/reports/M5-T012-DCV.md` (first review, at `aafc75fd`) stands
intact as the record of that SHA. This file is the re-issued verification at the reworked head.

Verifier: **directive-compliance-verifier** (independent). Reviewed SHA
`12fda82f3f237f2432efc99614c903496a8b2e02`; material identity
`e5c95c27d20943ba24a1aebbca9ba77f7fe129ff4b5c68b857f86a50817fabb0`.

---

## DCV RE-REVIEW — task M5-T012 vs directive D-038 (independent)

**Verdict: PASS** (directive compliance at `12fda82f`). **Every code-level BLOCKING defect from the
first review is independently verified FIXED.** One **BLOCKING process finding remains** and it is
not about the code: the gate records are stale at the superseded SHA, two of them FAIL (§8).

| field | value |
|---|---|
| `reviewed_sha` | `12fda82f3f237f2432efc99614c903496a8b2e02` (confirmed `git rev-parse HEAD`; branch `candidate/D-024-mrl-option-b`) |
| `reviewed_manifest_sha256` | `e5c95c27d20943ba24a1aebbca9ba77f7fe129ff4b5c68b857f86a50817fabb0` (first 8: `e5c95c27`) |
| previous identity (now stale) | `c80cbb0c…` at `aafc75fd` — moved exactly as predicted |
| applicable requirement set | exactly `{D-038-R003, D-038-R004}` — re-derived, not carried over |
| `D-038-R003` | **SATISFIED** |
| `D-038-R004` | **SATISFIED** |
| `validate_directive_compliance.py --check` | **EXIT 0** |
| accept simulation | `reasons: []`, `deferrals: []` |
| platform | Python 3.11.9, pytest 8.4.2, Windows 11. Read-only throughout. |

### 0. Independence (unchanged, restated)

I am not the producer (`backend-engineer`) and not any gate reviewer (`code-reviewer` G1/G4,
`qa-engineer` G3, `security-reviewer` G5). Every claim below was reproduced by me from primary
evidence — git objects, the files, and my own command runs. Where the coordinator's message or a
gate report asserts something, I say explicitly that I reproduced it. My only write is this file.
I did not touch product code, tests, the packet, `state.json`, `verification.json`, the directive
files, or any gate record; I ran no `project_control.py` write subcommand and no git/gh write.

### 1. What moved (reproduced)

`git diff --name-status aafc75fd 12fda82f` → **3 files, all inside `allowed_paths`**:

```
M  project-control/reports/M5-T012-producer-report.md
M  services/api/app/api/v1/scenario_analysis.py
M  services/api/tests/api/test_scenario_analysis_api.py
```

`git diff --stat` → **1,093 insertions / 125 deletions**, matching the coordinator's statement.

Byte-unchanged across `aafc75fd..12fda82f`, verified individually with `git diff --quiet`:
`services/api/app/main.py` (blob still `071f7755`), `services/api/app/config.py`,
`services/api/app/api/v1/scenario.py`, `services/api/app/scenario/**`,
`services/api/tests/scenario/**`, `packages/**`, `apps/web/**`, `tools/**`, and
**`project-control/directives/**`** — so no directive file was touched by the rework, as claimed.

### 2. Applicable requirement set — RE-DERIVED at the new SHA: still exactly `{D-038-R003, D-038-R004}`

1. `DirectiveRegistry.evaluate_task_refs(packet)` → `ok: true`,
   `applicable_ids: ["D-038-R003","D-038-R004"]`, `cited_ids: ["D-038-R003","D-038-R004"]`,
   `missing_ids: []`, `invalid_refs: []`, `unresolved: []`, `reasons: []`. Registry load errors `[]`.
2. **Whole-registry sweep re-run**: 36 active directives, **3,641 requirement rows** scanned with
   `_applicability_matches()` against the packet (`task_id=M5-T012`, `task_type=backend`,
   `milestone_id=M5`, the 4 `allowed_paths`) → exactly **2** matches, both D-038: R003
   (`obligation`) and R004 (`prohibition`). No `UNRESOLVED` row anywhere.
   *Correction to my first report, for the record:* I stated "3,767" rows there; the correct total is
   **3,641** (my earlier figure was an arithmetic slip in summing the per-directive counts). The
   sweep itself, and its conclusion, are unchanged — the count is descriptive, not load-bearing.
3. **Un-cited-applicability trap re-checked, still CLEAR.** The rework added **no new file and no new
   path**, so the path surface is identical to the one I cleared before; I re-ran the check anyway.
   Only three rows in the whole active registry have an `applicability.paths` intersecting this
   packet, all via the shared `project-control/reports/` entry, and all three fail the conjunction:
   `D-004-R222` (also needs `task_types=['governance']`, `task_ids=['D-004-PHASE0','M0-T028']`,
   `milestones=['M0']`), `D-004-R240` (`governance`, `['M0-T028']`, `['M0']`), `D-007-R610`
   (`governance`, `['D-007-BUILD','M0-T036']`). M5-T012 is `backend`/`M5` → none attaches.
   **No hold-class requirement from an un-cited directive is pulled in**; `directive_refs = D-038:ALL`
   expands to exactly the applicable set; `missing_ids = []`.
4. R001, R002, R005, R006, R007 remain `applicability.task_ids = ["D-038-BOOTSTRAP"]` →
   **NOT_APPLICABLE** to this ledger task; the per-requirement reasoning in §3 of `M5-T012-DCV.md` is
   unchanged and still holds (R002 substantively honoured: all three changed paths are
   `services/api/**` product files, `tools/**` and `.claude/**` untouched; R006 corroborated —
   `git branch -r --contains 12fda82f` → empty, branch has no upstream → nothing pushed).

### 3. D-038-R003 (positive product deliverable) — **SATISFIED**

* **Still product engineering, still within R003's "scenario/optimization engine" clause.** The four
  endpoints remain thin adapters over the four **accepted** engine functions through the public
  `app.scenario` facade: `post_sensitivity` (:642), `post_ranking` (:682), `post_comparison` (:722),
  `post_threshold` (:760). No engine module changed (§1). Milestone M5, `task_type=backend`, not the
  M0 self-infra line.
* **Still a normal G0 packet.** `project-control/gates/M5-T012-G0.json` → `result=PASS`,
  `role=administrative`, intake report present. `required_gates=[G0,G1,G3,G4,G5]`.
* **Acceptance scenarios are more executable than before, and I ran them.** The test file grew
  816 → 1,442 lines; collection grew **75 → 171 items**. Reproduced to completion:
  * `python -m pytest services/api/tests/api` → **312 passed in 37.13s, exit 0** (was 216)
  * `python -m pytest services/api/tests/scenario` → **388 passed in 3.99s, exit 0** — identical to
    the M5-T011 accepted count, **0 regression**, no pre-existing test file edited (§1)
  * `python tools/modularity_check.py --check` → **failures 0, EXIT 0** (366 files selected)
* **The qualification I recorded against R003 last time is now DISCHARGED.** At `aafc75fd` I recorded
  that AS-2's and AS-6's contracted text was violated and that their tests probed only top-level fact
  keys. At `12fda82f` both are enforced and tested at depth: `nested_fact_body()` (:427) builds the
  nested attack per endpoint; `test_as2_nested_fact_key_at_any_depth_is_typed_422` (:644) is
  parametrized over all four endpoints × the fact-key set;
  `test_as2_every_forbidden_fact_key_is_rejected_nested_too` pins **the whole `FORBIDDEN_FACT_KEYS`
  set** nested (so adding a key without extending the walk cannot pass); and
  `test_as2_nested_verified_claim_never_reaches_a_200_body` (:677) is my exact finding as an
  executable regression. AS-6's helper was replaced by `assert_nothing_is_verified()` (:474) driving
  `_walk_envelope()` (:461) over **every node at every depth** against `VERIFICATION_CLAIM_KEYS` —
  strictly stronger than the `coverage_status`-only scan it replaces.
* **`STATUS_STATE_MATRIX` still introduces no pair**, checked programmatically at the new SHA:
  `set(scenario_analysis.STATUS_STATE_MATRIX) == set(scenario.STATUS_STATE_MATRIX)`; `B - A == []`.
* **AS-3 posture re-verified live at the new SHA.** With the flag ON, `/openapi.json` lists **0**
  paths mentioning scenario/sensitivity/ranking/comparison/threshold (2 documented paths total); all
  four routes carry `include_in_schema=False` (:642/:682/:722/:760). With the flag empty, the
  disabled response body is **byte-identical** to an unmounted sibling path
  (`404 {"detail":"Not Found"}` in both cases), and the disabled response carries **no**
  `X-Correlation-ID` (no hint the feature exists). The existing `app.config.internal_scenario_enabled`
  is reused (:92); `config.py` is byte-unchanged; **no new flag**.

### 4. D-038-R004 (no Supabase / no Geoclient) — **SATISFIED** (re-proven, not carried over)

The rework changed the request-handling path, so I redid the proof rather than reusing it.

* **Negative grep re-run** over the reworked `scenario_analysis.py` for
  `supabase|geoclient|requests\.|httpx|socket|urllib|os\.environ|getenv|subprocess|boto3|psycopg|sqlalchemy`
  → **0 matches** (grep exit 1). No env read, no network client, no credential, no storage.
* **My own loopback-only egress block, re-armed at the new SHA** (landmines on
  `socket.socket.connect`, `connect_ex`, `socket.create_connection`, `socket.getaddrinfo`,
  `http.client.HTTPConnection.connect`, `HTTPSConnection.connect`; loopback permitted so anyio's
  blocking portal still works):
  * new file alone → **171 passed in 22.19s**, non-loopback egress attempts **`[]`**
  * **whole api suite** → **312 passed in 38.48s**, non-loopback egress attempts **`[]`**
* **RED proof re-run — the egress assertion is still load-bearing.** With
  `app.dependency_overrides` cleared and all four endpoints driven, my landmines recorded
  `[('http.client.HTTPSConnection.connect', 'data.cityofnewyork.us')]`. (The `sensitivity` and
  `threshold` probes returned 422 *before* any fetch — correct: fact-key rejection precedes I/O —
  while `ranking`/`comparison` reached the fetch and attempted real egress.) The AS-7 test now
  parametrizes the egress assertion over **all four** endpoints rather than only `comparison`.
* **No credential can be read.** The AS-7 test still deletes `pluto_soda.APP_TOKEN_ENV_VAR` and
  asserts its absence from `os.environ` and that no `x-app-token` reaches the transport. Facts come
  only from the injected `get_pluto_fetcher` / `get_spatial_substrate_provider` seams with the
  recorded-official PLUTO fixtures. `dependencies=[M5-T003, M5-T011]`; `supabase/**` is a
  `forbidden_path` and is byte-unchanged.

### 5. The three BLOCKING fixes — each independently reproduced at `12fda82f`

**(a) Nested fact-key echo (the defect I reproduced at `aafc75fd`) — FIXED.** I replayed my *exact*
former attack body verbatim:

```
POST /api/v1/properties/1000010100/scenario/ranking
{"objective":"maximize_illustrative_usable_area","assumption_sets":[[{"assumption_type":"utilization_factor",
 "value":0.8,"draft_zoning_floor_area_cap_sq_ft":987654321,"coverage_status":"verified","verified":true,
 "rule_evaluation":{"outputs":{"max_residential_floor_area_sq_ft":987654321}}}]]}

aafc75fd -> 200, body carried 987654321 under the canonical cap key; coverage scan saw 'verified'
12fda82f -> 422  state='validation_error'
             rejected_keys = ['coverage_status','draft_zoning_floor_area_cap_sq_ft','rule_evaluation','verified']
             '987654321' appears NOWHERE in the response (raw-text check: False)
```

Nested rejection confirmed on **all four** endpoints, each with `X-Correlation-ID` and each using the
existing `(422,"validation_error")` pair: `sensitivity` → `['coverage_status']`, `ranking` and
`comparison` → all four keys, `threshold` → `['cap']` (nested three containers deep). A clean body is
still a clean 200: `scenario_cap_sq_ft == 15000.0 == TRACE_CAP`,
`assert_nothing_is_verified(envelope)` **holds**, disclaimer present,
`json.dumps(envelope, allow_nan=False)` OK, no `" at 0x"` leak.

**(b) Unpaired-surrogate crash (G5 BLOCKING-1) — FIXED.** Raw-byte bodies carrying a lone surrogate:

```
{"variable":"\ud800","values":[0.8]}                         -> 422 state='validation_error' xcid=True
{"\ud800":1,"variable":"utilization_factor","values":[0.8]}   -> 422 state='validation_error' xcid=True
```

Both the string **value** and the dict **key** paths are covered, with the existing
`(422,"validation_error")` pair — not a framework 500. `_finish` now validates with
`json.dumps(envelope, ensure_ascii=False, allow_nan=False).encode("utf-8")` (:594), the same encoding
Starlette's renderer uses, so validator and renderer can no longer disagree.

**(c) Unguarded engine call (G1/G5 HIGH-1) — FIXED.** All four endpoints now route through
`_guarded_analysis` (:605, called at :671/:711/:751/:795) whose `except Exception` returns
`_internal_error_500` (:624-630). I forced each engine to raise
`RuntimeError(r"SECRET C:\Users\MLFLL\token deadbeef")` in turn:

```
sensitivity / ranking / comparison / threshold
  -> 500 state='internal_error'  in_MATRIX=True  xcid=True
     leak_secret=False  leak_path=False  leak_traceback=False
```

Typed, in-matrix, correlated, and leaking no secret, filesystem path, or traceback — on all four.

### 6. Integrity — UNCHANGED and re-confirmed

* `python tools/validate_directive_compliance.py --check` → **EXIT 0** (silent pass; ~5 min).
* **CRLF-byte digest.** `requirements.json` on disk: **9,316 bytes, 258 CRLF, 0 bare LF**. `sha256`
  of those exact bytes, **un-normalised** =
  `32f8d252e948164c2895c938c916426853471fb61e00446e16cd78fb0bf61c95` ==
  `manifest.requirements_content_digest_sha256`. ✓ (LF-normalised would be `7d78a261…` — the git
  blob sha, not the digest; `.gitattributes` pins `project-control/directives/** text eol=lf`.)
* **Source digest** `sha256(source-001.md)` (1,599 B) = `a237dd50…` == `manifest.sources[0]`. ✓
  `amendments: []`.
* **`locked_requirement_ids` untouched.** On-disk ids `[R001..R007]` == `locked_requirement_ids` ==
  `requirement_count` 7. ✓
* **Nothing drifted across either rework.** Reproduced at all three commits — `c83206c2`,
  `aafc75fd`, `12fda82f` — the `requirements.json` blob is the *same object* (LF sha `7d78a261`,
  CRLF-encoded `32f8d252`), the manifest claims `32f8d252` at each, `locked` = 7 at each, and
  `audit_log` = 10 entries at each. ✓
* **audit_log still reflects reality.** `audit_log[-1]` = `2026-09-09T12:10:00+00:00`, actor
  `orchestrator`, action `applicability_appended`; its note names M5-T012, asserts no id
  added/removed/renumbered and no source change, and states the `37035a7d → 32f8d252` resync. Both
  ends re-verified against the bytes: CRLF-encoded `requirements.json` hashes to `37035a7d…` at
  `c83206c2^` and `32f8d252…` at `c83206c2`/`aafc75fd`/`12fda82f`. ✓

### 7. Material content identity at `12fda82f` — via the accept path's own routine

```python
import sys; sys.path.insert(0, "tools")
import project_control as pc
reg_mod = pc._resolver()
t = pc.load(pc.PC / "tasks" / "M5-T012.json")
identity, resolved_sha, ierr = pc._task_git_identity(reg_mod, t)   # reviewed_sha=None -> HEAD
```

```
identity     = e5c95c27d20943ba24a1aebbca9ba77f7fe129ff4b5c68b857f86a50817fabb0
first 8      = e5c95c27
resolved_sha = 12fda82f3f237f2432efc99614c903496a8b2e02
error        = None
```

* **Function:** `tools/project_control.py::_task_git_identity(reg_mod, task_dict)` with
  `reviewed_sha=None` — the exact call `accept()` makes through `_directive_accept_reasons`
  (`project_control.py:532`, invoked at `:1254`). It delegates to
  `directive_registry.frozen_git_identity(allowed_paths, reviewed_sha=None, root=ROOT,
  exclude_prefixes=('project-control/',), require_clean=True,
  control_plane_prefixes=('project-control/',), allow_empty_identity=False)`.
  `path_free_opt_in()` → `(False, None)`.
* **Composition (4 objects, reproducible).** Raw-blob component `d66154c7…` over
  `services/api/app/api/v1/scenario_analysis.py` blob **`d8ee33d1`** (was `0a89fb3f`),
  `services/api/app/main.py` blob **`071f7755`** (unchanged),
  `services/api/tests/api/test_scenario_analysis_api.py` blob **`c9e6d330`** (was `bffec62d`);
  control-plane material component over `project-control/reports/M5-T012-producer-report.md` blob
  **`9a563e9a`** (was `76150390`). `_hash_manifest_entries(blobs + control_plane)` = `e5c95c27…`.
* **Dirt guard passed (`err = None`)** despite the working tree's pre-existing orchestrator state
  (` M project-control/state.json`, ` M project-control/tasks/M5-T012.json`, the untracked
  `.claude/agent-memory/qa-engineer/*`, `scratchpad/`, and the gate records and reports): none is
  inside this packet's `allowed_paths`, so none enters the scoped cleanliness check.
* `c80cbb0c…` is now **stale** and must not be written into `verification.json`.

### 8. Accept simulation + the remaining BLOCKING finding

**Verification-row simulation (in memory; no file written).** Appending a candidate M5-T012 row in
the M5-T011 shape — `applicable_requirement_ids: [D-038-R003, D-038-R004]`,
`reviewed_sha: 12fda82f…`, `reviewed_manifest_sha256: e5c95c27…`,
`verifier: directive-compliance-verifier`, both requirement rows `state: PASS` with
`verified_by`/`verified_at`/`reviewed_sha` — then calling
`reg.task_verification_result('D-038','M5-T012',{R003,R004},'e5c95c27…',reviewed_sha='12fda82f…')`:

```
reasons  : []
deferrals: []
-> ROW SHAPE SATISFIES THE ACCEPT GATE (nothing to defer)
```

**Negative control** (the same row, queried at the superseded identity/SHA) is correctly refused,
which proves the check is real and not vacuous:

```
D-038/M5-T012: verification is stale -- recorded at content identity e5c95c27..., current is c80cbb0c...
D-038/M5-T012: verification reviewed_sha is stale -- recorded at commit 12fda82f..., current reviewed commit is aafc75fd... (fail closed)
```

**BLOCKING (process, not code, and not a D-038 violation): the gate records are stale, and two FAIL.**
Read from `project-control/gates/` at the time of this review:

| gate | reviewer | role | result | reviewed_sha | identity |
|---|---|---|---|---|---|
| G0 | orchestrator | administrative | PASS | `52e98d5e` | `160e076c` |
| G1 | code-reviewer | independent_review | **FAIL** | `aafc75fd` | `c80cbb0c` |
| G3 | qa-engineer | independent_review | PASS | `aafc75fd` | `c80cbb0c` |
| G4 | code-reviewer | independent_review | PASS | `aafc75fd` | `c80cbb0c` |
| G5 | security-reviewer | independent_review | **FAIL** | `aafc75fd` | `c80cbb0c` |

`accept()` iterates `required_gates = [G0,G1,G3,G4,G5]` and adds a reason for any gate without a
`PASS` record, so it will refuse on **G1** and **G5** as they stand. G1/G5 must be re-gated **PASS at
`12fda82f`**, and G3/G4 re-attested there (their PASS was given against the superseded content —
`accept()` does not itself compare a gate record's `content_manifest_sha256`, so that staleness is a
review-integrity obligation on the gate wave rather than a mechanical refusal; the two FAILs are the
mechanical refusal). A `M5-T012-G4-rereview.md` report appeared in `project-control/reports/` while I
was finalizing this, so the re-gate wave is evidently already under way. Also still absent: the
submit report `project-control/reports/M5-T012.json`, which `accept()` compares against
`e5c95c27…` — `submit` must be run at this HEAD.

**No code-level BLOCKING remains.** I found no new blocking defect at `12fda82f`, and all three
previously reported ones are reproduced as fixed (§5).

### 9. Non-blocking observations

* **New, disclosed modularity warn signal.** `modularity_check --check` → failures **0**, EXIT **0**,
  but `scenario_analysis.py` now draws `warn review_signal: above the warning threshold` (the
  producer report §7 records 572 → 666 SLOC against `WARN_SLOC = 600`; raw `wc -l` is 807). This is a
  **signal, not a failure**, it is outside R003/R004, and whether it warrants a follow-up split is
  G1's/G5's call — I note only that the module remains a single route-adapter responsibility
  (flag-gate → validate → rebuild → call engine → envelope) and that the growth is the three
  security fixes plus their documentation, not new responsibility.
* **Pre-existing branch-wide `ruff check .` red** (27 errors, all in `app/scenario/*` and
  `tests/scenario/*` files from earlier *accepted* M5 work, all inside this packet's
  `forbidden_paths`) — unchanged by the rework, unrelated to this task, and nothing is pushed.
* **Python 3.11 vs CI 3.12 gap** (pre-existing): `app/documents/units.py:276` uses PEP-695 syntax, so
  the wider `pytest -q` from `services/api` cannot collect locally. Neither packet-documented command
  touches `app.documents`; I ran both to completion.
* **Producer report ↔ reality: no drift.** It records 312 / 388 — exactly what I reproduced — and
  candidly corrects its own earlier "well under the 600-SLOC threshold" wording. The two claims I
  flagged as false at `aafc75fd` ("Nothing is ever marked Verified"; "Every non-disabled response
  carries `X-Correlation-ID`") are now **true**, verified by my own probes in §5.
* **`python -m pytest tools/test_directive_compliance.py` produced NO result — the run was KILLED.**
  The background run I started during the first review never emitted a byte (zero-length output file)
  and was terminated before completion, so there is **no pass/fail to report** and I make **no claim**
  about it. It is not a packet-documented command and not required by the brief; it is named only in
  the `directive-compliance-verifier` role file's "final review" list. The brief's required command,
  `tools/validate_directive_compliance.py --check`, completed with **EXIT 0** at this SHA, and that is
  the integrity evidence §6 rests on. Should the orchestrator want this harness as additional
  evidence, it must be run to completion separately — no conclusion may be drawn from the killed run.

### 10. Worktree left as found

`git status --short` at finish shows only pre-existing orchestrator/gate state — ` M project-control/state.json`,
` M project-control/tasks/M5-T012.json`, the two untracked `.claude/agent-memory/qa-engineer/*`
files, `project-control/gates/M5-T012-{G1,G3,G4,G5}.json`,
`project-control/reports/M5-T012-{G1,G3,G4,G4-rereview,G5}.md`, `M5-T012-DCV.md`, `scratchpad/` —
plus this new report. I touched none of them. My probe scripts (`dcv_netblock.py`,
`dcv_rereview_probes.py`, `dcv_guard_probe.py`, `dcv_red_egress.py`) live outside the repository in
the session scratchpad.
