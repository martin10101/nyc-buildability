<!-- Saved VERBATIM from the directive-compliance-verifier agent return (transport entity-decoding only),
     orchestrator seq 122, 2026-09-20. Ruling identity: frozen submission 2b5edbc3. -->

# M5-T057 — Directive-Compliance Verification (DCV) report

**Verifier:** directive-compliance-verifier (independent; not the producer of any artifact reviewed)
**Repo:** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`
**Frozen submission sha:** `2b5edbc3b0a6231adbeec0cd1dc0a765b6cc160e` | **material:** `3dbd056d50d72e75992f508ca5aa07a31526fdb7` | **worktree producer commit:** `fcc58e24` | **CI:** run 35498218087 `success` at `f86ae7353c8b2ff99220c51766aad23d595cc66f`
**Repo HEAD at review time:** `18616ff5` (ledger-only commit; content identity unchanged — proven below)

---

## 0. RESTAMP PRE-AUTHORIZATION (stated up front, M5-T042 pattern)

**(a) My verification's content identity** — LF-normalized sha256 (`\r\n`→`\n`) of the 6 packet files at `2b5edbc3`, reproduced by me (identical at `3dbd056d`):

| # | path | LF-sha256 | lines |
|---|---|---|---|
| 1 | `services/api/app/api/v1/proposal_checks_api.py` | `e75bec6a3256aa5332054eaec4a207717eaadb7dab8dab22a2da56d7904186c9` | 593 |
| 2 | `services/api/app/main.py` | `97983f0ce86f119e495d618d91f3dc67653c74b153c07b481dbe8b2c39bbd9d6` | 210 |
| 3 | `services/api/tests/api/test_proposal_checks_api.py` | `a46d9e66681e6fea1cf820d3c4729f6f2a78786e4b9ddacd90d0a55b03583395` | 559 |
| 4 | `services/api/tests/api/test_proposal_validation_api.py` | `0c4fa2eb485c28d67eff2178b93636f5c065a968b3770baaaa29f4782b08192e` | 711 |
| 5 | `services/api/tests/rules/test_proposal_checks.py` | `9d150fa4a8d7a2151058f53992e4c1ecd565bbc16472a3200f240daa25dd70ce` | 782 |
| 6 | `project-control/reports/M5-T057-producer-report.md` | `7afaf9924e5a497662e2689c943b43a0ded824181c40bd975a82b2b2e2d7397c` | 253 |

CLI content identity (`directive_registry.frozen_git_identity` components, reproduced): **`de2891a4222895b8409f76c6c280f50108f4a55182c806fc041ec837b94a1d03`** at `2b5edbc3` — byte-equal to `project-control/reports/M5-T057.json → content_manifest_sha256`, and **unchanged at `18616ff5`**.

**(b) Pre-authorization:** my per-requirement **PASS/SATISFIED rows (D-076-R001, D-076-R002, D-077-R002, D-077-R003)** may be restamped to any future accept head **at or past `2b5edbc3`**, provided at that head (i) the 6 LF digests above are unchanged, and (ii) `git diff 2b5edbc3..<accept-head> -- <the 6 paths>` is EMPTY.
**(c)** Disjoint peer commits — anything outside the 6 paths, explicitly including the M5-T058 (`wt-m5t058`) and M5-T059 (`wt-m5t059`) lanes' allowed_paths and all `project-control/**` seam/ledger commits — do **not** void this pre-authorization.
**(d) What WOULD void it:** any edit to any of the 6 paths; any change to `source-001.md`/`requirements.json` for D-066-R001, D-076-R001/R002, D-077-R002/R003 (the 2026-09-20T07:53:11Z applicability appends + digest resyncs for M5-T058/M5-T059 are already at this head and do **not** affect T057's citations — resolver re-run below confirms); or any change to the packet's `allowed_paths`/`directive_refs`.
**D-066-R001 is NOT pre-authorized for restamp** — it is ruled VIOLATED below and needs a fresh delta attestation after correction.

---

## 1. Intake review (sources ↔ atomic matrix)

Files at `2b5edbc3` (`git ls-tree`): each of `D-066-code-graph-loop-wiring`, `D-076-proposal-editor-planning`, `D-077-release-pass-and-three-mvp-loops` contains exactly `manifest.json`, `requirements.json`, `source-001.md`, `verification.json` — **no amendment files exist**, so "every amendment reflected" is satisfied vacuously and verifiably.

Digests reproduced by me (LF-normalized, via `directive_registry.sha256_text_artifact` / sha256 of source bytes):

| directive | source-001 digest (recorded → computed) | requirements artifact digest (recorded → computed) |
|---|---|---|
| D-066 | `4cb05c942698d36f…` → same **MATCH** | `1cfd50766d183850…` → same **MATCH** |
| D-076 | `aca8907a65ea1f00…` → same **MATCH** | `fe4275edc8638ab8…` → same **MATCH** |
| D-077 | `35653195792e8364…` → same **MATCH** | `1bd42450bfdf6cdb…` → same **MATCH** |

`python tools/validate_directive_compliance.py --check` → **exit 0** (silent success; direct exit code, not through a pipe).

Source-to-matrix decomposition check (owner text read verbatim):
- **D-066** owner asks: make the map graph actually used → R001 (regen + nav block + `--no-regen` instruction + advisory clause); have Codex use it and report → R002; a small time/token test → R003; "don't get sidetracked… part of whatever's next" → R004 (prohibition). No item **missing**, none **weakened** (R003's "not a controlled benchmark" is an honesty limit, not a softening), none **combined** (each obligation has its own row), none **invented**.
- **D-076** ("Plan it", with the offer that defined the referent): plan authoring + phase order/grounding → R001; honesty/boundary rules → R002 (source_ref correctly points at the context section, with the owner text named as authority); precisely bounded hold release → R003. No missing/weakened/combined/invented items.
- **D-077**: release pass (owner-only) → R001; three loop lanes → R002; "rest of the MVP" scope boundary → R003; the resume-body's wiring preconditions → R004. The body's re-affirmations are explicitly noted as creating no new requirement. No missing/weakened/combined/invented items.

**Resolver agreement** (`directive_registry.load_registry().evaluate_task_refs(<M5-T057.json @ 2b5edbc3>)`):
`ok=True`, `applicable_ids == cited_ids == ['D-066-R001','D-076-R001','D-076-R002','D-077-R002','D-077-R003']`, `missing_ids=[]`, `invalid_refs=[]`, `unresolved=[]`.

**Intake verdict: PASS.**

---

## 2. Harness / test reproduction (run by me, not read from the report)

| command | cwd | result |
|---|---|---|
| `python -m ruff check .` | `services/api` | `All checks passed!` exit 0 |
| `python -m pytest tests/api -q` | `services/api` | **540 passed** exit 0 |
| `python -m pytest tests/rules -q` | `services/api` | **726 passed** exit 0 |
| `python tools/modularity_check.py --check` | repo root | exit 0; warn lines are pre-existing (`tools/agent_supervisor/*`, `tools/context_benchmark.py`); **`proposal_checks_api.py` not flagged** |
| `python tools/validate_directive_compliance.py --check` | repo root | exit 0 |
| `python tools/test_project_control.py` | repo root | `OK: all 23 project-control test groups passed` exit 0 |
| `python tools/test_directive_reminder.py` | repo root | `Ran 12 tests … OK` exit 0 |
| `python tools/test_directive_compliance.py` | repo root | **still executing at report time (>25 min, no output yet)** — see note |

Note on the last row: it is a tool self-test binding no requirement here; the authoritative registry-integrity check (`validate_directive_compliance.py --check`, exit 0) and the two other control-plane suites are green. I do not rule any requirement on the unfinished run, and no requirement's evidence depends on it.

Independent identity checks: `3dbd056d` is an ancestor of the CI head `f86ae735` (**material is in the CI-green tree**); `2b5edbc3` is an ancestor of current HEAD; the 5 code/test artifacts are **byte-identical between the worktree commit `fcc58e24` and the cherry-pick `3dbd056d`** (LF-sha256 5/5 MATCH). Material commit file set = **exactly 6 files** (`git show --stat 3dbd056d`), matching §8/§1 of the producer report.

---

## 3. Per-requirement rulings

| Req ID | Ruling | Primary evidence I reproduced (file · line/field · observed value) |
|---|---|---|
| **D-066-R001** | **VIOLATED** | See §3.1 — the nav-block and `--no-regen` conjuncts are satisfied; the **"at every contract seam the orchestrator regenerates the code graph"** conjunct was not performed at the T057 seam, and the evidence-map claim asserting it is contradicted by primary evidence. |
| **D-076-R001** | **SATISFIED** | `docs/PROPOSAL_EDITOR_PHASED_PLAN.md` phase-B packet table (B0–B5, lines 45–53; B3 row line 51; sequence line 83; owner checkpoint line 55) — committed, untouched in `848703a7..2b5edbc3`. Order honored: `project-control/tasks/M5-T054.json → status "accepted", accepted_at 2026-09-20T06:10:23Z`, T057 `created_at 2026-09-20T06:14:44Z`. Grounded in existing machinery, no parallel concept: `services/api/app/api/v1/proposal_checks_api.py:68-71` imports `check_proposal` from `app.rules.proposal_checks`; `:74-79` `LotContext`/`AttestedStreetLine` from `app.scenario.derivation`; `:80` `ProposedMassingError` from `app.scenario.proposal`; `:81` `validate_proposed_massing_input` from `app.scenario.proposal_input_gate`; `:61-66` reuses T053 body primitives. One mount only: `services/api/app/main.py:36` + `:200`. No new dependency/contract version (`git diff --name-only 848703a7 2b5edbc3 -- '*requirements*.txt' '*package*.json' 'pyproject.toml' '*.yml' 'render.yaml'` → empty). Non-blocking observation in §3.2. |
| **D-076-R002** | **SATISFIED** | Packet cites it (`M5-T057.json:91-96 directive_refs D-076 → ["D-076-R001","D-076-R002"]`) and carries the rules as binding text (`inputs[4]` SCOPE 1/3 items (3)(4)(6); `inputs[6]` PRESERVATION) with matching scenarios AS-1/AS-4/AS-5 (`acceptance_scenarios[0],[3],[4]`). **No emission:** `proposal_checks_api.py:583-593` returns `report.as_dict()` + `correlation_id` only, under the comment "BP-6 / DB-034(d): the response is the grouped check report ONLY - no scenario document, no contract version"; `grep` over the module finds `contract_version`/`1.1.0` only absent (no occurrences). Bound by `tests/api/test_proposal_checks_api.py:487-497` (`test_bp6_response_emits_no_scenario_document_or_contract_version`: asserts `contract_version`, `scenario_id`, `constraint_completeness` absent and `"1.1.0" not in blob`) — green in my 540-pass run. **Could-not-check channel present:** `app/rules/proposal_checks.py:374-390` top-level `as_dict` → `summary {"pass","fail","could_not_check","total"}`, `results[].could_not_check_reason` (`:324-338`), `unmapped_lot_facts`; route test `:169-199` asserts `summary == {"pass":1,"fail":1,"could_not_check":2,"total":4}`, coverage `shortfall == 0.125`, and the unattested case flips height to `could_not_check/allowance_unresolved`. **Third input class, never a record:** `app/scenario/derivation.py:79 SOURCE_CLASS = "proposed_derivation"` stamped on every result/report (`proposal_checks.py:630,721 → as_dict:378`); no aggregate "approved/compliant" field exists in the response. **Unmapped never fed:** `proposal_checks_api.py:280-293` ("else: unmapped -> not validated, never fed"), test `:424`. |
| **D-077-R002** | **SATISFIED** | **Three concurrent lanes, fresh run-ids, disjoint:** `C:\SupervisorController\autostart-launch.ps1:36-39` → packet `…\ctl24\project-control\tasks\M5-T057.json`, `$Repo = …\wt-m5t057`, `$Branch = task/M5-T057-proposal-check-route`, `$RunId = persistent-local-59-m5t057`; `C:\SupervisorController2\autostart-launch.ps1:37-40` → M5-T058 / `wt-m5t058` / `persistent2-local-22-m5t058`; `C:\SupervisorController3\autostart-launch.ps1:39-42` → M5-T059 / `wt-m5t059` / `persistent3-local-06-m5t059`. Set intersection of `allowed_paths`: T057∩T058 = ∅, T057∩T059 = ∅ (computed from the three task JSONs). **Full drill:** `project-control/gates/M5-T057-G0.json` → `result "PASS"`, `reviewed_sha 0099bbb2…`, manifest `56d0caeb…`; `project-control/reports/M5-T057-G0.md` "Pairwise disjointness" section (EMPTY/EMPTY vs frozen T055/T056); binds+digest resyncs in the same commit (manifest `audit_log` entries `2026-09-20T06:15:56Z` in D-066/D-076/D-077, digests reproduced MATCH in §1); claim seam `848703a7` "claimed (backend-engineer, FULL worktree path wt-m5t057), progress 20" with packet `worktree = C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t057` (full path); worktree branch at/past claim seam (`git merge-base --is-ancestor 0099bbb2 fcc58e24` → YES; branch log `848703a7 → fcc58e24`). **Harvest/cycle:** cherry-pick `3dbd056d` byte-identical to `fcc58e24` (5/5 LF digests), orchestrator suite capture in report §8.1 reproduced by me line-for-line (ruff 0 / 540 / 726 / modularity 0), submit record `project-control/reports/M5-T057.json` (`reviewed_sha 2b5edbc3…`, `content_manifest_sha256 de2891a4…` recomputed MATCH, `applicable_requirements` = the 5 cited ids), CI `35498218087 success` at `f86ae735` containing the material. |
| **D-077-R003** | **SATISFIED** | **Released, non-held queue only:** B2 accepted (see D-076-R001 row) then the B3 route slice; plan row `docs/PROPOSAL_EDITOR_PHASED_PLAN.md:51,83`. **No held scope touched:** material commit `3dbd056d` = exactly the 6 paths; `git diff --name-only 848703a7 2b5edbc3 -- .claude/rules/expansion-agent-dispatch-hold.md project-control/master_plan.json docs/PROPOSAL_EDITOR_PHASED_PLAN.md` → **empty**; no 3D/visual-massing, GDS, 19-task-pack, phase-C or phase-D artifact in the diff. **No new public surface:** `main.py:180-200` mounts under the existing `INTERNAL_RULE_EVAL_ENABLED` gate; route `include_in_schema=False` (`proposal_checks_api.py:443`), flag-off = generic 404 (`:211-214,449`), no new flag. **Prohibited-action evidence:** `git log --merges 848703a7..2b5edbc3` → none; `gh pr view 241` → `state OPEN, mergedAt null` (hold respected); `git merge-base --is-ancestor 2b5edbc3 origin/main` → NO (nothing merged); no dependency/lockfile/workflow/deploy file touched in the range; nothing dispatched/deployed/installed/purchased/closed by this task. **D-072 ceiling:** exactly three lanes (launchers + worktrees + ledger), not raised. |

### 3.1 D-066-R001 — VIOLATED (detail)

Requirement text (three conjuncts): *"At every contract seam the orchestrator **regenerates the code graph** (`tools/code_graph/generate.py --repo .`) **and embeds a graph-derived navigation block** … the packet **instructs the producer to consult `query.py --no-regen`** … The graph stays advisory: every material conclusion is verified in actual source."*

Satisfied conjuncts:
- Navigation block present and **accurate in source**: `project-control/tasks/M5-T057.json → inputs[4]` ("CODE-GRAPH NAVIGATION BLOCK (D-066-R001 …)"). Each named seam verifies: `check_proposal` exists (`app/rules/proposal_checks.py`), `proposal_input_gate.validate_proposed_massing_input`, `proposal.ProposedMassingError`, `derivation.LotContext` all imported by the route (`proposal_checks_api.py:68-81`); `proposal_validation` consumed by `main.py:37,187` and by its test file; `main.py` mounts routers (`:187,200`).
- Producer instruction present in the same inputs item ("Run `python tools/code_graph/query.py --no-regen impact <path>` before any sweep; the graph is ADVISORY - verify in source").

Failed conjunct — **no regeneration at the T057 contract seam (`0099bbb2`)**:
1. The contemporaneous primary record says so itself: `project-control/reports/M5-T057-G0.md` → "**Code graph (D-066-R001):** graph current at this seam (**regenerated at the D-077 contract seam** and unchanged since for these paths)". Compare the pattern used when a regen did happen: `M5-T054-G0.md` "regenerated at this seam (stale fingerprint → …)" and `M5-T058-G0.md:16` "graph regenerated at this seam: 764 files / 16164 nodes".
2. The D-066 manifest `audit_log` entry for the T057 bind (`2026-09-20T06:15:56Z`) records no regeneration; the **next** entry (`2026-09-20T07:53:11Z`, T058/T059) records "graph regenerated at this seam, 764 files/16164 nodes". Cache metadata corroborates: `…\AppData\Local\nyc-codegraph\346263e4677b-ctl24\graph.meta.json` `input_file_count = 764`, mtime `2026-09-20 03:46:28` (the T058/T059 seam, commit `2fba5ed3` 03:55), i.e. the regeneration immediately after T057's seam, not at it.
3. The relied-upon currency claim is **false**: between the last regen seam `29c5bc0b` and `0099bbb2`, 13 graph-input files changed, including the packet's own central seams — `services/api/app/rules/proposal_checks.py` was a **7-line seed** at `29c5bc0b` vs **751 lines** at `0099bbb2`, and `services/api/app/api/v1/proposal_checks_api.py` **did not exist** at `29c5bc0b`. A changed input set changes the fingerprint, so the cached graph was STALE at the T057 seam and `query.py --no-regen` would refuse for the producer — reproduced now: `python tools/code_graph/query.py --no-regen impact services/api/app/api/v1/proposal_checks_api.py` → `STALE (stale fingerprint): refusing to serve the cached graph`. (Consistently, the producer report contains **zero** mentions of "graph".)
4. Therefore the evidence-map claim `project-control/reports/M5-T057-evidence-map.json → requirements["D-066-R001"][0]`: *"Code graph regenerated at the T057 contract seam (commit 0099bbb2)"* is **contradicted by primary evidence** — it is a claim, and it does not reproduce.

Impact: control-plane/evidence-accuracy defect only. No code defect follows: the nav block's material content verifies in actual source (the directive's advisory clause holds), and the delivered route consumes exactly the named seams.

Minimal remedy (orchestrator, read-only me): (i) run `python tools/code_graph/generate.py --repo .` and re-derive/confirm the T057 consumer/impact set — expect confirmation, not a packet change; (ii) correct the `D-066-R001` row of `project-control/reports/M5-T057-evidence-map.json` (and the G0 line) to state what actually happened, as an `[ORCH-CORRECTED]` edit — that file is **outside** `allowed_paths`, so it moves no material identity and leaves the §0 pre-authorization for the other four rows intact; (iii) send me a delta attestation for the D-066-R001 row only.

### 3.2 Non-blocking observation (D-076-R001)

The plan's B3 row (`docs/PROPOSAL_EDITOR_PHASED_PLAN.md:51`) names a **frontend** packet with gates `G0,G1,G2,G3,G4,G5 + HJ`; this packet is a backend "B3 slice 1" with `G0,G2,G3,G4,G5` and no HJ. The split and the gate shape are recorded and justified contemporaneously in `project-control/reports/M5-T057-G0.md` ("route/recalculation seam only — the editor UI is the follow-on slice"; "No contract-schema touch → no G1 (T053 precedent…)"), the phase order B2→B3 is preserved, and no held scope is entered. I record it as an observation, not a finding; the UI slice must still carry G1/HJ if it touches contracts/UI.

---

## 4. Verdict

Four of five applicable requirements are SATISFIED on reproduced primary evidence. One — **D-066-R001** — is VIOLATED on the regeneration conjunct, with the evidence map asserting the opposite of what the repository shows. Per the DCV rule that any VIOLATED result prevents completion:

**VERDICT: FAIL**

Blocking item: **D-066-R001** only. On correction per §3.1 (graph regenerated + evidence-map/G0 row corrected to the facts) I expect to flip that row to SATISFIED on a short delta attestation; the other four rows and the §0 restamp pre-authorization stand unchanged at any accept head at-or-past `2b5edbc3` meeting conditions (b).

Key paths: `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M5-T057.json`, `…\project-control\reports\M5-T057-evidence-map.json`, `…\project-control\reports\M5-T057-producer-report.md`, `…\project-control\reports\M5-T057-G0.md`, `…\project-control\gates\M5-T057-G0.json`, `…\project-control\directives\D-066-code-graph-loop-wiring\{source-001.md,requirements.json,manifest.json}`, `…\services\api\app\api\v1\proposal_checks_api.py`, `…\services\api\app\main.py`, `…\docs\PROPOSAL_EDITOR_PHASED_PLAN.md`, `C:\SupervisorController\autostart-launch.ps1` (and `…Controller2`, `…Controller3`).


---

<!-- DELTA ATTESTATION saved VERBATIM from the resumed directive-compliance-verifier agent (transport entity-decoding only), orchestrator seq 122, 2026-09-20. Ruling identity: frozen resubmission a0cb3b79; fresh restamp pre-authorization in SSC. -->

# M5-T057 — DCV DELTA ATTESTATION at the rework identity

**Verifier:** directive-compliance-verifier (independent; read-only; produced none of the reviewed artifacts)
**New frozen submission sha:** `a0cb3b795ebc84792673ab5f43d3300f0ea90f33` (2026-09-20 05:19:17 -0400)
**Rework material:** `ca5c8895` (cherry-pick of worktree `c09f87d6`) · **initial material:** `3dbd056d` · **CI:** run 35501675264 `success` at `fd9c4a04`
**Repo HEAD at this review:** `fd62b08d` — content identity unchanged from the frozen sha (proven below)

---

## A. Identity reproduced (all digests computed by me, LF-normalized, `\r\n`→`\n`)

| # | path | LF-sha256 @ `a0cb3b79` | lines | vs my §0 table |
|---|---|---|---|---|
| 1 | `services/api/app/api/v1/proposal_checks_api.py` | `ccfe7c993a73ce6d03f414f2980c676bc977890f1bad60f35dca0ec64b3b96f6` | 721 | CHANGED (was `e75bec6a…`, 593) |
| 2 | `services/api/app/main.py` | `97983f0ce86f119e495d618d91f3dc67653c74b153c07b481dbe8b2c39bbd9d6` | 210 | unchanged |
| 3 | `services/api/tests/api/test_proposal_checks_api.py` | `0d1cd1acfe6ed566c8cefc3b99bb812578b51a289b66f54ebf61906b86362219` | 767 | CHANGED (was `a46d9e66…`, 559) |
| 4 | `services/api/tests/api/test_proposal_validation_api.py` | `cd3bf12ebc044107f8b916d1aaa1f67a93808b31884e1335c438664692be0a05` | 714 | CHANGED (was `0c4fa2eb…`, 711) |
| 5 | `services/api/tests/rules/test_proposal_checks.py` | `9d150fa4a8d7a2151058f53992e4c1ecd565bbc16472a3200f240daa25dd70ce` | 782 | unchanged |
| 6 | `project-control/reports/M5-T057-producer-report.md` | **`7aa2a199feb289ae941a5b72870d17b6e88445fb30d5387ae02d80a394951157`** | 302 | CHANGED (computed by me, as requested) |

All six are byte-identical between worktree `c09f87d6` and cherry-pick `ca5c8895` and at `a0cb3b79`. Rows 1/3/4 match the coordinator's quoted digests exactly; rows 1–5 match the report's §8.2 table.

CLI content identity (`directive_registry.frozen_git_identity` components, recomputed): **`c662a1cd6f34419ac384b10b2f11533b51d0765cfe3fe3ae566bbfcc82eab9f9`** at `a0cb3b79` — byte-equal to `project-control/reports/M5-T057.json → content_manifest_sha256` (`submitted_at 2026-09-20T09:19:19Z`, `reviewed_sha a0cb3b79…`) — and **identical at current HEAD `fd62b08d`**.

Scope of the rework: `ca5c8895` = **exactly 4 files**, all inside `allowed_paths` (route, its test pack, the T053 test file, the producer report). `app/rules/**`, `app/scenario/**`, `packages/contracts/**` are **untouched across the entire task range `0099bbb2..a0cb3b79`**. The two `apps/web/**` files in that range belong to peer lanes (`2fba5ed3` T058 seed, `05f1aea2` T055 correction), not to T057's materials. `main.py` byte-unchanged.

Registry stability: `git diff --name-only 2b5edbc3 fd62b08d -- project-control/directives/` → **empty**; the five requirement texts, applicability sets and digests are byte-identical to my first review. D-080's three requirements bind `['D-080-BOOTSTRAP']` only. Resolver at `a0cb3b79`: `ok=True`, `applicable == cited == ['D-066-R001','D-076-R001','D-076-R002','D-077-R002','D-077-R003']`, no missing/invalid/unresolved.

Reproduced at the current head: `ruff` **All checks passed! exit 0**; `pytest tests/api -q` → **552 passed** exit 0; `pytest tests/rules -q` → **726 passed** exit 0 (both from `services/api`); `tools/modularity_check.py --check` → **exit 0**, 21 warn lines, **none naming `proposal_checks_api.py`**; `tools/validate_directive_compliance.py --check` → **exit 0**. CI run 35501675264 `success` at `fd9c4a04`, which contains `ca5c8895` and is an ancestor of `a0cb3b79`.

---

## B. Per-requirement rulings at `a0cb3b79`

| Req ID | Ruling | Evidence I reproduced at this identity |
|---|---|---|
| **D-066-R001** | **SATISFIED** (deviation recorded, not hidden) | Remedy verified independently, not accepted as claim: (1) **regeneration executed** — cache metadata `…\AppData\Local\nyc-codegraph\346263e4677b-ctl24\graph.meta.json`: `input_file_count 772`, node total **16254**, edge total **7149**, mtime `2026-09-20 05:08:43` (between my report and the resubmission) — exactly the claimed figures. (2) **Impact set re-derived and confirmed in source by me**: consumers of `proposal_checks_api.py` = `services/api/app/main.py` (:36 import, :200 mount) + `tests/api/test_proposal_checks_api.py` — nothing else; importers of `app/rules/proposal_checks.py` = the route + `tests/api/test_proposal_checks_api.py` + `tests/rules/test_proposal_checks.py` (main.py's mention at :194 is a comment, not an import). This matches the packet's navigation block, so no packet change follows. (3) **False claim withdrawn and facts recorded in two durable places**: `project-control/reports/M5-T057-evidence-map.json` D-066-R001 row now opens "[ORCH-CORRECTED per DCV SS3.1 …] The regeneration conjunct was NOT performed at the T057 contract seam (0099bbb2) … The original row's assertion … was false and is withdrawn"; `project-control/reports/M5-T057-G0.md` gains a tagged addendum stating the same with **the original line preserved unedited** (verified by `git diff 2b5edbc3 a0cb3b79 -- …G0.md`: pure append). (4) The two originally-satisfied conjuncts still hold at this identity: navigation block in `M5-T057.json inputs[4]`, `--no-regen` instruction in the same item, advisory clause honored (every nav claim verified in source, twice, by me). **Recorded deviation:** the seam-timing conjunct cannot be retro-satisfied for `0099bbb2`; it is now truthfully on the record, the regeneration has been performed, and the later seam did comply (D-066 manifest audit `2026-09-20T07:53:11Z`: "graph regenerated at this seam, 764 files/16164 nodes"). No systemic exception is created; future contract seams must regenerate before the nav block is written. |
| **D-076-R001** | **SATISFIED (re-affirmed)** | Plan grounding unchanged and re-verified in the **new** route source: `proposal_checks_api.py:78-81` imports `check_proposal` from `app.rules.proposal_checks`; `:84-90` `LotContext`/`AttestedStreetLine`/`ProposedMassingError` from `app.scenario.*`; `:95` `proposal_input_gate`; `:71-77` reuses T053 primitives; one mount in byte-unchanged `main.py`. No parallel concept, no contract-schema change (`app/scenario/**`, `packages/contracts/**` untouched over the whole range). No new dependency: `git diff --name-only 2b5edbc3 a0cb3b79 -- '*requirements*.txt' '*package*.json' 'pyproject.toml' 'render.yaml' '.github/**'` → empty; the single new import `starlette.concurrency.run_in_threadpool` (:65) is a transitive FastAPI runtime already present. Order unchanged (B2 `M5-T054` accepted `06:10:23Z` → this B3 route slice). §3.2 observation from my first report stands unchanged (plan's B3 row is the UI packet; this backend slice's gate shape is justified in `M5-T057-G0.md`). |
| **D-076-R002** | **SATISFIED (re-affirmed; strengthened by the rework)** | Re-verified in the reworked source, not carried over: **single engine entry** — `check_proposal` called exactly once at `proposal_checks_api.py:688-690` (`await run_in_threadpool(functools.partial(check_proposal, …))`); `derive_proposal` appears only in the docstring (:37) and a comment (:142), never called; bound by `tests/api/test_proposal_checks_api.py:484 test_bp1_only_check_proposal_entry_is_called` (updated for the partial shape). **No emission** — `:712-721` returns `report.as_dict()` + `correlation_id` only, under the BP-6/DB-034(d) comment; module docstring `:9` names D-076-R002 explicitly; bound by `:495 test_bp6_response_emits_no_scenario_document_or_contract_version`. **Honesty channel intact** — the engine (`app/rules/proposal_checks.py`, byte-unchanged) still serializes `summary {pass, fail, could_not_check, total}`, per-result `could_not_check_reason`, `unmapped_lot_facts`, and `source_class = "proposed_derivation"` (`app/scenario/derivation.py:79`); no aggregate approval field. All of it green in my 552-pass run. The rework also **withdrew a false honesty claim** in the producer report §2 ("the original submission's claim that 'EVERY error path length-caps any embedded value' was FALSE for the refusal `field` key … and for the lot-side caller ids") and closed the class — that is the correct direction for this requirement, not a regression. |
| **D-077-R002** | **SATISFIED (re-affirmed, incl. the rework leg)** | Lane drill unchanged and still true (launchers `C:\SupervisorController{,2,3}\autostart-launch.ps1` → T057/`wt-m5t057`/`persistent-local-59-m5t057`, T058/`wt-m5t058`, T059/`wt-m5t059`; pairwise `allowed_paths` intersections ∅; FULL worktree path in packet; worktree at/past claim seam `848703a7`). **Rework leg verified as the drill, not an exception:** ledger walk in `M5-T057.json progress_log` is `in_progress 20 → rework 80 ("Wave complete at frozen 2b5edbc3: G3 FAIL …") → in_progress 80 → awaiting_gate 85` (the legal path; no `rework→awaiting_gate`); gate records `M5-T057-G0/G2/G3/G4/G5.json` present for the first wave; corrections landed as ONE tagged cluster `ca5c8895` (4 files, all in scope, `[ORCH-CORRECTED per …]` tags in code and report §8.2); resubmission at `a0cb3b79` with identity `c662a1cd…` reproduced; CI green at `fd9c4a04` containing the material. A gate FAIL handled by bounded rework + re-attestation is exactly "keep the lanes cycling … or a genuine stop condition". |
| **D-077-R003** | **SATISFIED (re-affirmed)** | Released, non-held queue only: no held-scope artifact in either material commit (`3dbd056d` 6 files, `ca5c8895` 4 files); `.claude/rules/expansion-agent-dispatch-hold.md`, `project-control/master_plan.json`, `docs/PROPOSAL_EDITOR_PHASED_PLAN.md` untouched across `848703a7..a0cb3b79`. No new public surface in the rework: `:565 @router.post("/proposal-checks", include_in_schema=False)`, `:571-572` fail-safe 404 on the **existing** `internal_rule_eval_enabled()` flag — no second flag, no auth change. Prohibited actions clear in the new range: no merge commits `2b5edbc3..a0cb3b79`; PR #241 `state OPEN, mergedAt null`; `a0cb3b79` not an ancestor of `origin/main`; no dependency/deploy/workflow file touched; nothing dispatched/deployed/installed/purchased/closed. D-072 ceiling still exactly three lanes. |

Non-blocking observations (carried, not findings): (1) `docs/DISCOVERY_BACKLOG.md` changed in the seam commit `fd9c4a04` — outside T057's `allowed_paths`, but it is an orchestrator control-plane sweep entry (DB-039), not producer material, and it is outside the content identity. (2) The route module grew 593→721 lines; `modularity_check --check` is exit 0 and the module is absent from all 21 warn lines, but it is now the largest single surface in this packet — the B3 slice-2 packet should check its boundary before growing it further.

---

## C. FRESH RESTAMP PRE-AUTHORIZATION (supersedes my §0)

**(a) Content identity of this verification** = the six LF-sha256 digests in §A at `a0cb3b795ebc84792673ab5f43d3300f0ea90f33`, equivalently the CLI identity **`c662a1cd6f34419ac384b10b2f11533b51d0765cfe3fe3ae566bbfcc82eab9f9`**.

**(b) Pre-authorization:** all five per-requirement rows above (including D-066-R001) may be restamped to **any accept head at or past `a0cb3b79`**, provided at that head (i) the six LF digests in §A are unchanged, and (ii) `git diff a0cb3b79..<accept-head> -- <the six paths>` is **EMPTY**.

**(c) Tolerated (do NOT void):** disjoint peer commits touching anything outside the six paths — explicitly the M5-T058 (`wt-m5t058`) and M5-T059 (`wt-m5t059`) lanes' allowed_paths, all `project-control/**` seam/gate/ledger/evidence-map commits (including `[ORCH-CORRECTED]` edits to the evidence map, `M5-T057-G0.md`, or gate reports, which lie outside the six paths and move no material identity), `docs/**` sweeps, and directive captures that bind only their own bootstrap sentinels.

**(d) Voiding conditions:** any edit to any of the six paths; any change to `source-001.md`, `requirements.json` (text or applicability) or the manifest digest for `D-066-R001`, `D-076-R001`, `D-076-R002`, `D-077-R002`, `D-077-R003`; any change to the packet's `allowed_paths` or `directive_refs`; an accept head that is NOT at-or-past `a0cb3b79`; or a re-introduction of the withdrawn D-066-R001 "regenerated at the T057 contract seam" claim in any record.

---

**VERDICT: PASS**

All five applicable requirement IDs are SATISFIED at `a0cb3b79` on primary evidence I reproduced myself (source, git objects, control-plane records, and re-run harnesses: ruff 0 / api 552 / rules 726 / modularity 0 / validator 0). D-066-R001's seam-timing deviation is permanently and truthfully recorded in both the evidence map and the G0 report, the regeneration has been performed (772/16254/7149) and its impact set independently confirmed in source, so nothing in this packet rests on an unverified navigation claim.
