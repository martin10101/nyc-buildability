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
