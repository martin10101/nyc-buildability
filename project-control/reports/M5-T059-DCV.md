<!-- Saved VERBATIM from the directive-compliance-verifier agent return (transport entity-decoding only),
     orchestrator seq 122, 2026-09-20. Ruling identity: frozen submission f58f4d89.
     (The harness transcript file for this agent was empty; saved from the delivered return.) -->

# M5-T059 — Directive-Compliance Verification (DCV)

**Verifier:** directive-compliance-verifier (read-only; producer ≠ verifier)
**Date:** 2026-09-20
**Repo:** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` (branch `candidate/D-024-mrl-option-b`)
**Frozen submission identity:** `f58f4d89e858521b936f4d60fcb2a84fd50391af`
**Material:** `2fbd661e0afdd664d5d83daafd46ebf9ef9bfec1` (cherry-pick of worktree `48fe290b`)
**Web/CI proof:** run `35502941971` = success at `fc2910af` (ancestry verified: `2fbd661e` → `fc2910af` → `f58f4d89`; `git diff fc2910af f58f4d89 -- apps/web services/api` EMPTY)
**Inspected at:** primary checkout HEAD `ee07a10d` (content of the 14 packet paths byte-identical to `f58f4d89` — `git diff --stat f58f4d89 HEAD -- <14 paths>` EMPTY; working tree clean on those paths)

## 1. Intake review (sources vs atomic matrix)

| Check | Result |
|---|---|
| Amendments present | NONE for D-066 / D-077 / D-078 (`manifest.amendments = []`; only `source-001.md` in each directory) — nothing to reflect |
| Source digests | MATCH at `f58f4d89` and at HEAD — I re-derived every `content_digest_sha256` and `requirements_content_digest_sha256` for all **78** indexed directives using `directive_registry.normalize_text_artifact_bytes` over git blobs: **0 problems at both revs** |
| Missing source items | None. D-078 source's one-click/map/confirm/calc-on-combined-land/evidence-trail all live in R001; the boundary paragraph → R002; pairing/sequencing → R003. D-077's two instructions are separate rows (R001 release, R002 three loops), scope boundary R003, wiring preconditions R004 |
| Weakened | None. R001 retains "every calculation runs on the confirmed combined land"; R002 retains "NEVER auto-selects, infers, or defaults"; D-066-R001 retains all four conjuncts (regen at every seam · nav block in packet · producer instructed to use `query.py --no-regen` · advisory/verify-in-source) |
| Combined | None — release vs loops vs scope are distinct rows; D-078 obligation / prohibition / sequencing are distinct |
| Invented | None without anchor. D-077-R003/R004 and D-078-R003 are orchestrator interpretation, labelled as such in the capture context; each **tightens** (scope boundary, preconditions, order) and never adds a licence |
| `tools/validate_directive_compliance.py --check` | **exit 0** at the settled head (direct exit code, no pipe) |

**Transient observed and resolved (F-4, non-blocking):** an earlier run returned exit 1 with three c14 mismatches (D-066/D-076/D-077) while the M5-T060 contract seam was mid-write. I proved no *committed* head was ever invalid: declared == actual at `f58f4d89`, at `5b4836be`, and at `ee07a10d`. Signature matches the documented "requirements lands before manifest" transient.

## 2. Resolver agreement (reproduced)

`DirectiveRegistry().load().evaluate_task_refs(json.load(project-control/tasks/M5-T059.json))` →
`ok=True`, `applicable_ids == cited_ids == ['D-066-R001','D-077-R002','D-077-R003','D-078-R001','D-078-R002','D-078-R003']`, `missing/invalid/unresolved` all empty; registry `errors=[]`; D-066/D-077/D-078 index status `active`.

## 3. Content identity — the 14 allowed_paths at `f58f4d89` (LF-normalized sha256)

| # | Path | sha256 (LF) |
|---|---|---|
| 1 | `services/api/app/site_definition/__init__.py` | `4af8d97c2c6baf67112e0c19075f0ac4f139abf26151133a1b4e6435dc833b63` |
| 2 | `services/api/app/site_definition/records.py` | `cddcb3b819f7a758ba91fa2ad17f891564e242b82925f9e5a56cce24cd7e8fd5` |
| 3 | `services/api/app/site_definition/store.py` | `b24e3c5f3075eacdabbbbc6fc8c1bc88a9ab5dcddc579886841a1c539fd1e5e8` |
| 4 | `services/api/app/api/v1/site_definition.py` | `bdb4f90487486feded57d96a2b05a4a0af58cc3b1ec573e68dab11a7dbb5472a` |
| 5 | `services/api/tests/site_definition/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty seed) |
| 6 | `services/api/tests/site_definition/test_site_definition_records.py` | `181c45a58f1ecda342da78766fefe92e719438c467942113617564391c5bfea2` |
| 7 | `services/api/tests/api/test_site_definition_api.py` | `a1e3890b4a7b805a8fb75ec6c51a65622c277fb44caf11f5199948c931e4ce35` |
| 8 | `services/api/app/api/v1/condo_records.py` | `6b06fa4d5eb8ad79a95a81cca0ca341b7868783625407ff5b8a3ce3f93028025` |
| 9 | `services/api/tests/api/test_condo_records_api.py` | `128ff45819e2aec57a410976c44feccf1b2ed4148c14c83332a1f4b647081da1` |
| 10 | `apps/web/src/lib/condo-records.ts` | `c27d7559245579b2e18aeec5566f313c7ed090733e539639fb01172066c906ab` |
| 11 | `apps/web/src/lib/__tests__/condo-records.test.ts` | `0cce838c1b3d4140485f5d4f8f83339cf819ec9fc1cb297e8dd9a8e4fdec9377` |
| 12 | `apps/web/src/components/architect/PropertyOverview.tsx` | `8028be9d36ec9f27957421b155c089179b72f11c4fc314595ad1d40d0c707baf` |
| 13 | `apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx` | `e2c8b6de9ac1630f59134a978ad064012348a843ab5271eebdedf13acb40faaa` |
| 14 | `project-control/reports/M5-T059-producer-report.md` | `4d77bcdfe5c7ba5b5edba92b7514949a0cc62387dbdde8bb4d736eed10bf2263` |

- **§9 digest table reproduced:** rows 1–12 of the producer report's orchestrator-bound table match my independent LF digests **exactly**. Row 13 (the report) is self-referential by the M5-T013 precedent; I bind it above as `4d77bcdf…`.
- **13-file material set verified:** `git show --name-only 2fbd661e` = exactly 13 files, **all** inside `allowed_paths` (path 5, the empty test-package seed, correctly carries no diff). No forbidden path in the material commit (`proposal_checks_api.py` in a seam→material range diff belongs to M5-T057's `ca5c8895`, not to this commit).
- **Cherry-pick fidelity:** worktree `48fe290b` vs `f58f4d89` over all 14 paths → **zero differences**.
- **Seeds:** all 14 paths tracked at the contract commit `2fba5ed3` (`git cat-file -e` each).

## 4. Per-requirement rulings (primary evidence, reproduced)

| ID | Ruling | Primary evidence I reproduced |
|---|---|---|
| **D-066-R001** | **SATISFIED** | Nav block: `project-control/tasks/M5-T059.json` `inputs[3]` — "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated at this contract seam, 764 files/16164 nodes)" + "Run `python tools/code_graph/query.py --no-regen impact <path>` before any sweep; graph ADVISORY - verify in source." Regen conjunct: D-066 `manifest.json` `audit_log` entry `at=2026-09-20T07:53:11+00:00` — "Bound M5-T058 + M5-T059 … (graph regenerated at this seam, 764 files/16164 nodes; navigation blocks embedded in both packets) … Digest resynced 8a30c29f -> 1cfd5076 SAME commit (c14)" — regen precedes the packet write (packet `created_at 07:51:22`, seam commit `2fba5ed3`); corroborated by `M5-T059-G0.md:18` "Code-graph navigation block embedded (same seam regen)". Advisory-verified-in-source (I re-checked 6 anchors at `f58f4d89`): `condo_base_lot.py:77 OUTCOME_MULTI_LOT="multi_lot_set"`, `:87 @dataclass(frozen=True)`, `:108 condo_key`, `:247-252` multi-lot construction with `resolved_base_bbl=None`; `documents/storage.py:1-16` B-001 deferral docstring; `proposal_validation.py` body-ceiling helpers `_bounded_message/_payload_too_large/_declared_content_length/_read_body_within_ceiling` + `include_in_schema=False`. `connectors/**` and `documents/**` untouched (absent from the 13-file material set). **The T057 deviation does not apply here — the conjunct is met.** |
| **D-077-R002** | **SATISFIED** (one non-blocking claim correction, F-1) | Contract `2fba5ed3` (binds + digest resyncs + seeds + both G0s) → claim seam `f86ae735` ("both claimed … FULL worktree paths wt-m5t058 / wt-m5t059, progress 20"). Packet `worktree` = full path `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t059`; `git -C wt-m5t059 log` shows `48fe290b` → `f86ae735` → `2fba5ed3`, i.e. created **at** the claim seam. Disjointness re-derived mechanically from the three packets' `allowed_paths`: T057∩T059 = ∅ (7×14), T058∩T059 = ∅ (19×14), T057∩T058 = ∅ — matching `M5-T059-G0.md:35-39`. Three lanes live: T057 accepted (240th, `fc2910af`), T058 `in_progress` (`wt-m5t058`), T059 `awaiting_gate`; fresh run-id corroborated by an independent committed control-plane record — D-080 `manifest.json` audit entry `2026-09-20T08:10:00+00:00` naming `persistent2-local-21-m5t058, persistent3-local-06-m5t059`. Cycling leg completed: harvest → cherry-pick (byte-identical) → CI 35502941971 all 18 jobs success → submit at `f58f4d89` → this wave. **F-1:** the evidence map says "10 seeded placeholders"; `git show --name-status 2fba5ed3` added **8** T059 files (7 code/test + report). The underlying obligation holds (all 14 paths tracked at the contract commit); the count is an overstatement to correct in the map, not a violation. |
| **D-077-R003** | **SATISFIED** | Queue class is the R003-named "subsequent released lanes contracted at seams under existing directives" — contracted under active D-078 (owner-authorized 2026-09-20), `directive_refs` cited, G0 PASS. No held scope: the 13 material files are condo-records/site-definition surfaces only (no 3D/massing, no GDS P1–P8, no master-plan change); PR #241 still open, title's DO-NOT-MERGE hold intact; PR #64 untouched. No new dependency (no lockfile/manifest in the 13 files). No new flag: `app/api/v1/site_definition.py:51` imports the pre-existing `internal_rule_eval_enabled` (present at `2fba5ed3:services/api/app/config.py:52`); `config.py` not in the material set. No new public surface: all four routes `include_in_schema=False` and flag-gated (`:356/:408/:448/:503`), router unmounted (`app/main.py` has zero `site_definition` occurrences at `f58f4d89`; `tests/api/test_site_definition_api.py:319-321` asserts no `site-definition-confirmations` path in `main_app.routes`). D-072 ceiling = exactly three lanes. |
| **D-078-R001** | **SATISFIED for this packet's contracted share** (slice 1); directive-level flow remains open at later slices, explicitly recorded | `records.py` at `f58f4d89`: frozen `SiteDefinitionConfirmation` (`:254-306`) with `record_id, condo_key, billing_bbl, entered_bbl, parcels, confirmer, attestation_status, confirmed_at, provenance, supersedes_id, reason, note`; `ResolutionProvenanceSnapshot` (`:232-251`) is a byte-copy of the resolution provenance ("recorded verbatim, never re-derived"); parcels normalized to a **sorted tuple** (`normalize_parcels :359-382`); strict equality vs the resolver's `base_bbls` enforced at create (`ParcelSetMismatchError :466`); tz-aware `confirmed_at` (naive refused, `_confirmed_at_iso :424-434`). Store: `SiteDefinitionStore` ABC (`store.py:43-82`, 5 abstract methods) + `InMemorySiteDefinitionStore` (`:84-243`) + `default_site_definition_store()` (`:252`), B-001 deferral stated on the `documents/storage.py:1-16` precedent. Surfacing: `condo_records.py:664-674` additive `site_definition` block for `OUTCOME_MULTI_LOT` only; `apps/web/src/lib/condo-records.ts` parses it; `PropertyOverview.tsx` `CondoSiteDefinitionRecord` renders confirmer + role + timestamp + recorded parcels, else an explicit "not confirmed". Deferred parts recorded, not dropped: packet objective, report §12, `docs/DISCOVERY_BACKLOG.md:152,154`. **Orchestrator note:** stamp the D-078 `verification.json` row as *task-verified for M5-T059*, never as completing R001 — map display, one-click confirm, and calculations-on-combined-land are undelivered by design. |
| **D-078-R002** | **SATISFIED** | Prohibition surface checked **directly in source** at `f58f4d89`: `git grep "site_definition\|SiteDefinition"` over `app/spatial`, `app/rules`, `app/scenario`, `app/profile`, `app/documents`, `app/connectors`, `app/main.py` → **ZERO hits**; the only non-package consumer is `condo_records.py` (read-only, additive). Web: the material diff of `condo-records.ts` contains **no** `channelWithholdsAllowances` line; the `PropertyOverview.tsx` hunk `@@ -212,6 +214,38 @@` appends a new component *after* `deriveCondoSurface`'s closing brace (body lines are context — unchanged). Never auto-selects: create re-reads the resolver seam (`site_definition.py:319-343`), requires caller parcels ≡ `resolution.base_bbls`, server-sets attestation, and 422s a non-multi-lot outcome. Append-only: immutable frozen record with status derived from the transition log (`test_the_record_is_immutable_a_mutation_attempt_raises:225`; `test_supersede_chains_a_new_active_and_leaves_the_frozen_original_untouched:198`), reason required on supersede/revoke (`:192`, `:231`), duplicate active = typed refusal / 409 (`:185`, api `:238`). Staleness surfaced only: `test_a_later_differing_resolver_set_is_a_surfaced_discrepancy_not_a_status_change:317` + web "surfaces a parcel discrepancy … WITHOUT changing the confirmation (D-078-R002)". Self-attested loudly typed and fail-safe refused (`refused_for_calculation` property `:281-285`; web "stays refused-for-calculation even if the payload supplies false", "a missing flag defaults to refused"). Unconfirmed refusal unchanged: `test_block_is_unconfirmed_with_no_active_record:282` + web "a recorded site-definition confirmation NEVER unlocks the withheld allowances — records only". Reproduced green locally (57 T059-owned tests) and in CI for the web pack. |
| **D-078-R003** | **SATISFIED at the submitted identity** — with a blocking accept-time condition | Ledger: `project-control/tasks/M5-T056.json` `status=accepted`, `accepted_at=2026-09-20T07:07:56.471075+00:00`, present in `state.json.accepted_tasks`; `M5-T059.json` `created_at=2026-09-20T07:51:22.695811+00:00`, claim log entry `2026-09-20T07:55:52.317679+00:00` → contract/claim strictly **after** T056's acceptance. Per-packet G0 disjointness records exist and reproduce (§ above). Pair order: M5-T058 is `in_progress`; **neither packet has landed**, so nothing violates the order at submit. The plan holding this packet's acceptance behind M5-T058's is recorded in `project-control/reports/M5-T059-G0.md:46-49` and `docs/DISCOVERY_BACKLOG.md:154` ("its ACCEPT stays sequenced AFTER M5-T058 per D-078-R003"). **Ruling: the recorded sequencing plan satisfies R003 at SUBMIT time.** **ACCEPT-TIME CONDITION (blocking):** M5-T059 must not be accepted before M5-T058 is accepted; accepting T059 first flips R003 to VIOLATED. |

No requirement is VIOLATED, BLOCKED, or UNVERIFIABLE.

## 5. Harness / test outputs (run by me unless noted)

| Command | cwd | Result |
|---|---|---|
| `python tools/validate_directive_compliance.py --check` | repo root | **exit 0** (direct exit code) |
| `python tools/test_project_control.py` | repo root | `OK: all 23 project-control test groups passed` |
| `python tools/test_directive_reminder.py` | repo root | `Ran 12 tests … OK` |
| `python tools/test_directive_compliance.py` | repo root | 94 cases passing, **zero failures**, before the sandbox killed the run twice (>35 min each; each negative case spawns a full validator). Authoritative green = CI 35502941971 job `control-plane (workflow regression test, ADR-005)` **success** at `fc2910af`, which runs this exact script (`.github/workflows/ci.yml:444`) at a head containing the material. Verified-by-captured-evidence per the ADR-005 evidence-capture division — **not** unverifiable. |
| `python -m ruff check .` | `services/api` | `All checks passed!` exit 0 |
| `python -m pytest tests/site_definition tests/api -q` | `services/api` | **590 passed** in 32.61s. (Producer/orchestrator recorded 578 in `wt-m5t059`; the +12 are M5-T057's accepted binding tests now present in `tests/api` at HEAD — consistent, F-5, not a discrepancy.) |
| `python -m pytest tests/site_definition tests/api/test_site_definition_api.py tests/api/test_condo_records_api.py -q` | `services/api` | **57 passed** (the T059-owned surface) |
| `python tools/modularity_check.py --check` | repo root | **exit 0** (direct, unpiped); `selected 466 files; failures 0; warnings 20`; no warning names `condo_records.py` or `app/site_definition/**` |
| CI 35502941971 @ `fc2910af` | GitHub | success — all 18 jobs, incl. `web (lint + typecheck + build)`, `web-e2e (vitest + Playwright)`, `api (ruff + pytest)`, `modularity`, `control-plane`, `code-graph` |

## 6. Prohibited-action evidence

| Action | Observed |
|---|---|
| Merged | NO — `git branch -r --contains 2fbd661e` = `origin/candidate/D-024-mrl-option-b` only; not on `main` |
| Accepted | NO — `M5-T059.json.status = awaiting_gate`; absent from `state.json.accepted_tasks` |
| PR opened/closed/merged | NO new PR; open PRs unchanged: #241 (DO-NOT-MERGE hold intact), #64 |
| Deployed / flag-flipped | NO — router unmounted, existing `INTERNAL_RULE_EVAL_ENABLED` reused, `config.py` untouched |
| Dispatched / installed / purchased | NO — no dependency manifest or lockfile in the 13-file material set |
| Directive source edited | NO — all source + requirements digests match at `f58f4d89` and HEAD |

## 7. Findings (all non-blocking)

- **F-1** `project-control/reports/M5-T059-evidence-map.json` (D-077-R002 row): "10 seeded placeholders" — the contract commit `2fba5ed3` seeded **8** T059 files. Correct the count; the obligation itself is satisfied.
- **F-3 (advisory, slice 2)** `default_site_definition_store()` is a process-global in-memory store; safe today only because the write route is unmounted (production reads an empty store → honest "unconfirmed"). The mount must not ship before durability + authentication (already recorded in the packet and report §12).
- **F-4** Run the validator only at settled heads: I captured a real transient c14 INVALID during the M5-T060 seam write window; no committed head was affected.
- **F-5** 590 vs 578 pytest count is explained by M5-T057's accepted tests, not by drift.

## 8. Restamp pre-authorization (stated up front, M5-T042 pattern)

**(a) Content identity** — the 14 LF-normalized sha256 digests listed in §3 at `f58f4d89`.

**(b) Pre-authorization** — I pre-authorize restamping this DCV verdict (and the v2 verification rows for D-066-R001, D-077-R002, D-077-R003, D-078-R001, D-078-R002, D-078-R003) to **any accept head at or past `f58f4d89`**, provided at that head:
1. all 14 digests in §3 are unchanged (LF-normalized, `\r` stripped), and
2. `git diff --name-only <accept-head> f58f4d89 -- <the 14 paths>` is **EMPTY**, and
3. `python tools/validate_directive_compliance.py --check` exits **0** at that head (run at a settled head, per F-4), and
4. M5-T058 has been accepted **before** M5-T059 (the D-078-R003 accept-time condition).

**(c) Disjoint peers explicitly tolerated** — landing between freeze and accept, in any number or order:
- M5-T058's lane files (`wt-m5t058`, its 19 `allowed_paths`) **and M5-T058's own acceptance records** (gates, reports, evidence map, `state.json`, `tasks/M5-T058.json`, acceptance snapshot);
- the M5-T060 web-editor lane: new `apps/web` proposal-editor files plus `ArchitectEntry`/`navigation`/`ArchitectShell`/`architect.css` touches (all disjoint from the 14 paths) and its contract/claim seam commits;
- `project-control/**` seam commits (tasks, gates, reports, `state.json`), directive registry appends + digest resyncs (including binds of other tasks onto D-066/D-077/D-078), `docs/DISCOVERY_BACKLOG.md` sweeps, `docs/SESSION_HANDOFF.md`, `.claude/agent-memory/**`;
- any CI re-run at those heads.

**(d) What voids it** — any of: a change to any of the 14 digests in §3 (including an `[ORCH-CORRECTED]` edit inside `allowed_paths`); a mount of the `site_definition` router in `main.py` or any edit to a forbidden path folded into this packet's identity; acceptance of M5-T059 before M5-T058's acceptance; a directive source or requirements edit for D-066/D-077/D-078 without a recorded amendment + same-commit digest resync (validator non-zero at the accept head); or a v2 row stamping D-078-R001 as *directive-complete* rather than task-verified for M5-T059. Any of these requires a fresh delta attestation from me before accept.

## 9. Files cited (absolute)

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M5-T059.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M5-T059-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M5-T059-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M5-T059-G0.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-066-code-graph-loop-wiring\{source-001.md,requirements.json,manifest.json}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-077-release-pass-and-three-mvp-loops\{source-001.md,requirements.json}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-078-condo-site-definition-flow\{source-001.md,requirements.json,verification.json}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-080-nonstop-three-loop-build\manifest.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\site_definition\{records.py,store.py,__init__.py}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\api\v1\{site_definition.py,condo_records.py}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\site_definition\test_site_definition_records.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\api\{test_site_definition_api.py,test_condo_records_api.py}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\condo-records.ts` and `...\lib\__tests__\condo-records.test.ts`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\architect\PropertyOverview.tsx` and `...\architect\__tests__\condo-resolution-display.test.tsx`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\docs\DISCOVERY_BACKLOG.md` (lines 152, 154)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.github\workflows\ci.yml` (lines 432–446)

VERDICT: PASS


---

<!-- DELTA ATTESTATION saved VERBATIM from the resumed directive-compliance-verifier agent (transport entity-decoding only), orchestrator seq 122, 2026-09-20. Ruling identity: frozen resubmission 03882888; fresh pre-authorization in SS7. -->

All evidence reproduced at the corrected identity. Here is the delta attestation.

---

# M5-T059 — DCV DELTA ATTESTATION (corrected identity)

**Verifier:** directive-compliance-verifier (read-only; producer ≠ verifier)
**Supersedes:** my PASS at `f58f4d89` (my §8(d) voiding condition fired — 6 of the 14 allowed_paths changed)
**New frozen resubmission:** `03882888659429516f5bf66df80393b53e8235ba`
**Rework material:** `30bc53491a47182a68d953b390d23bf1609b80a3` (worktree `4afcebd0` in `wt-m5t059`)
**CI:** run `35509631275`/`35509631154`/**`35509631131` (CI) all success at `03882888` — **18/18 jobs, zero non-success**, incl. `api`, `web`, `web-e2e`, `modularity`, `code-graph`, `control-plane (workflow regression test, ADR-005)`
**Inspected at:** HEAD `56814549` — `git diff --stat 03882888 HEAD -- <14 paths>` **EMPTY**, working tree clean on those paths, so local reruns reproduce the frozen identity exactly.

## 1. Delta identity — reproduced independently

| Check | Result |
|---|---|
| Material scope | `git show --name-only 30bc5349` = **7 files**, **0 outside `allowed_paths`** (6 code/test + the producer report) |
| Changed vs my §3 table | Exactly the 6 named + the report; the remaining **7** paths byte-identical (incl. the empty `tests/site_definition/__init__.py` seed, `condo_records.py`, `test_condo_records_api.py`, and all four `apps/web` files) |
| §12.1 digest table | **Matches my independent LF digests on all 6 rows** |
| Packet contract fields | `inputs`, `outputs`, `acceptance_scenarios`, `required_gates`, `reviewer_agents`, `documented_test_commands`, `worktree`, `directive_refs`, `allowed_paths`, `forbidden_paths`, `dependencies` — **all IDENTICAL** to `f58f4d89` |
| Resolver agreement at `03882888` | `ok=True`, `applicable == cited == ['D-066-R001','D-077-R002','D-077-R003','D-078-R001','D-078-R002','D-078-R003']`; missing/invalid/unresolved empty |

**F-6 (non-blocking, claim correction):** the coordinator note and report §12.1 both say "the other **8** packet paths byte-unchanged" — it is **7** (the producer report is the 14th path and it changed). Arithmetic only; the digest set is correct.

### Corrected content identity — the 14 allowed_paths at `03882888` (LF-normalized sha256)

| # | Path | sha256 (LF) | vs f58f4d89 |
|---|---|---|---|
| 1 | `services/api/app/site_definition/__init__.py` | `5d1cb028563f47fdc89c7f4d7671c4ce2c0ba2fbc1d5eb84b87ff88203c32614` | CHANGED |
| 2 | `services/api/app/site_definition/records.py` | `1b27ba9aac485eb6f2cb2b178e2e3889ab91cc622c451f48f041d3aea17a57e3` | CHANGED |
| 3 | `services/api/app/site_definition/store.py` | `55373905c6cfbee41f1df2fd77dd61fb6f862b28aec9a320d2cf644970e829ff` | CHANGED |
| 4 | `services/api/app/api/v1/site_definition.py` | `06fced165e84f4896dcfc29b02886bb6cc6e262ac2d1fe7f0b02407a0c3dba59` | CHANGED |
| 5 | `services/api/tests/site_definition/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same (empty seed) |
| 6 | `services/api/tests/site_definition/test_site_definition_records.py` | `212281fb4d185e2b9096742adda9f2521317ae4e31aca99891e1fc3660e24bf0` | CHANGED |
| 7 | `services/api/tests/api/test_site_definition_api.py` | `d58690cbe9d47030c5e3980796c48fd259d4ee147df4b5a1c76d5d175940622a` | CHANGED |
| 8 | `services/api/app/api/v1/condo_records.py` | `6b06fa4d5eb8ad79a95a81cca0ca341b7868783625407ff5b8a3ce3f93028025` | same |
| 9 | `services/api/tests/api/test_condo_records_api.py` | `128ff45819e2aec57a410976c44feccf1b2ed4148c14c83332a1f4b647081da1` | same |
| 10 | `apps/web/src/lib/condo-records.ts` | `c27d7559245579b2e18aeec5566f313c7ed090733e539639fb01172066c906ab` | same |
| 11 | `apps/web/src/lib/__tests__/condo-records.test.ts` | `0cce838c1b3d4140485f5d4f8f83339cf819ec9fc1cb297e8dd9a8e4fdec9377` | same |
| 12 | `apps/web/src/components/architect/PropertyOverview.tsx` | `8028be9d36ec9f27957421b155c089179b72f11c4fc314595ad1d40d0c707baf` | same |
| 13 | `apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx` | `e2c8b6de9ac1630f59134a978ad064012348a843ab5271eebdedf13acb40faaa` | same |
| 14 | `project-control/reports/M5-T059-producer-report.md` | `c27c55bb9e6a7cb8250edf661f1e8fb8063102f2ecb465add8b5c41444c9d56b` | CHANGED (computed by me) |

## 2. The correction cluster, read in source (not from the report)

| Finding | Change verified at `03882888` | Directive reading |
|---|---|---|
| G3-C1 / G5-F1 (revoke not condo-bound) | `store.py` ABC `revoke(record_id, *, condo_key, reason, actor, at)` — `condo_key` now REQUIRED, docstring binds implementations; impl `revoke` does `record = self._require_active(record_id)` then `if record.condo_key != condo_key: raise ConfirmationNotFoundError(...)`. Route `site_definition.py:497-529` gains `resolve: SiteDefinitionResolver = Depends(...)`, re-reads `_resolve_multi_lot(canonical, ...)` exactly as supersede does, and passes `condo_key=resolution.condo_key or canonical`. Only production caller of `.revoke(` is that route (`git grep "\.revoke(" 03882888 -- services/api` → 1 app call + 7 test calls) — no consumer left red by the signature change. | **Strengthens D-078-R002**: adds a REFUSAL path; removes a cross-property route by which a caller could terminate another condo's recorded human decision. No system-driven status change is introduced. |
| G4-C-1 (newest-first false on ties) | `_insertion_seq`/`_next_seq` + `_record_insert()`; `list_for_condo_key` sorts on `(confirmed_at, insertion_seq)` reverse; the false "reverse of insertion order" comment corrected in place. | Read-ordering only; **no status semantics touched**. Inside R002's spirit. |
| G4-C-2 (orphan supersede via create) | New typed `OrphanSupersedeError` (`records.py:193-200`, `reject_code = "supersede_via_create_refused"`), exported through the `__init__.py` facade (additive); `store.create` refuses any `supersedes_id`-carrying record before the duplicate-active check. | **Strengthens R002's append-only clause**: supersession stays the only path that appends the replaced record's status flip; create can no longer mint an ACTIVE record whose chain reference the log never flipped. |
| DCV F-1 | Applied outside the 14 paths: `project-control/reports/M5-T059-evidence-map.json:11` now reads "8 seeded T059 files (7 code/test + report; the `tests/site_definition/__init__.py` seed carries no diff) `[ORCH-CORRECTED per DCV F-1]`" — matches what I re-derived from `git show --name-status 2fba5ed3`. | Claim corrected. |

**Binding tests are real red-without-fix bindings** (read, not assumed): `test_revoke_is_bound_to_the_condo_key_of_the_addressed_property` calls `store.revoke(..., condo_key=...)` — a kwarg that did not exist pre-fix (TypeError) — and asserts the record stays `ACTIVE`; `test_create_refuses_a_supersedes_id_carrying_record` expects `OrphanSupersedeError`, a class that did not exist pre-fix; `test_same_instant_pair_lists_newest_first` asserts `[second, first]` on an equal `confirmed_at`, which a stable reverse sort returned as `[first, second]` pre-fix; `test_cross_condo_revoke_is_a_typed_refusal_and_leaves_the_record_active` drives two locally-built apps over ONE shared store and asserts `404`/`state == "not_found"` with the record still `confirmed` afterwards.

## 3. Per-requirement rulings at `03882888`

| ID | Ruling | Primary evidence reproduced at the corrected identity |
|---|---|---|
| **D-066-R001** | **SATISFIED** | Packet `inputs[3]` byte-identical to the frozen original: "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated at this contract seam, 764 files/16164 nodes)" + "Run `python tools/code_graph/query.py --no-regen impact <path>` before any sweep; graph ADVISORY - verify in source." Regen conjunct re-read from D-066 `manifest.json` `audit_log` entry `2026-09-20T07:53:11+00:00` ("graph regenerated at this seam, 764 files/16164 nodes; navigation blocks embedded in both packets … Digest resynced 8a30c29f -> 1cfd5076 SAME commit (c14)") — the regen precedes the packet write (`created_at 07:51:22`, seam `2fba5ed3`); the T057 deviation does not apply. Nav-block anchors re-verified in source. `connectors/**` and `documents/**` untouched by the rework (7 material files). CI `code-graph (determinism --check + fixture tests)` success at `03882888`. |
| **D-077-R002** | **SATISFIED** | Lane drill unchanged and re-verified: contract `2fba5ed3` → claim `f86ae735` (FULL worktree path `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t059`, still the packet value) → worktree at/past the claim seam → harvest → **rework leg executed inside the same lane and scope** (7 files, zero outside `allowed_paths`, zero forbidden-path edits) → CI green at `03882888` → resubmit (ledger walk visible in `progress_log`: `rework` 11:59:06.148, `in_progress` 11:59:06.517, then `awaiting_gate` at `56814549`). Three lanes still disjoint (packet path sets unchanged ⇒ T057∩T059 = T058∩T059 = ∅). Cycling obligation demonstrated end-to-end: harvest → wave → blocking findings → tagged correction → re-freeze → re-review. F-1 count claim corrected. |
| **D-077-R003** | **SATISFIED** | No scope widened by the rework: no new dependency (no manifest/lockfile among the 7 files), no new flag (`internal_rule_eval_enabled` still the only gate; `config.py` untouched), no new public surface — router still `include_in_schema=False` on all four routes and still **unmounted** (`git grep site_definition 03882888 -- services/api/app/main.py` → EMPTY; `test_router_is_not_mounted_in_main_app` retained). No held work touched; PR #241 (DO-NOT-MERGE) and #64 unchanged; nothing on `main` (`git branch -r --contains 30bc5349` → `origin/candidate/D-024-mrl-option-b` only). D-072 ceiling unchanged. |
| **D-078-R001** | **SATISFIED for this packet's contracted share (slice 1)** — framing unchanged: **task-verified, NOT directive-complete** | Record substrate intact and now stricter: frozen `SiteDefinitionConfirmation` with who/when/which-parcels + byte-copied `ResolutionProvenanceSnapshot`, sorted-tuple parcels, strict equality vs the resolver's `base_bbls`, tz-aware `confirmed_at`, status derived from the append-only transition log; `SiteDefinitionStore` ABC + in-memory impl with the B-001 deferral stated; unmounted flag-gated create/list/supersede/revoke; read-only `site_definition` block on the multi-lot condo-records document + `PropertyOverview` surfacing (both files byte-unchanged from the identity I already verified). **Orchestrator note (unchanged):** stamp the D-078 `verification.json` row as *task-verified for M5-T059*; map display, one-click confirm, and calculations-on-confirmed-combined-land remain undelivered by design and recorded as later slices. |
| **D-078-R002** | **SATISFIED — enforcement strictly stronger than at `f58f4d89`** | Prohibition surface re-checked **directly in source at `03882888`**: `git grep "site_definition\|SiteDefinition"` over `app/spatial`, `app/rules`, `app/scenario`, `app/profile`, `app/documents`, `app/connectors`, `app/main.py` → **ZERO hits**; only consumer remains `condo_records.py` (byte-unchanged read-only additive block). Web prohibition evidence carries by byte-identity (all four `apps/web` paths unchanged; `channelWithholdsAllowances` and `deriveCondoSurface` untouched; the "records NEVER unlock the withheld allowances" regression retained) and is re-proven by `web-e2e` success at `03882888`. New enforcement lands **inside** the prohibition's spirit: every added behaviour is a REFUSAL (cross-condo revoke → typed `ConfirmationNotFoundError`/404 with the record left ACTIVE; orphan supersede via `create` → typed `OrphanSupersedeError`), status still changes only by an explicit human act recorded as an appended `StatusTransition`, and the tie-break touches read ordering only. Reproduced green: 61 T059-owned tests pass (was 57; +4 bindings). |
| **D-078-R003** | **SATISFIED at the resubmitted identity** — with the same blocking accept-time condition | `M5-T056.json` `accepted_at = 2026-09-20T07:07:56.471075+00:00` still precedes this packet's contract (`created_at 07:51:22`) and claim (`07:55:52`). `M5-T058` is still `in_progress`; `M5-T059` is **not** in `state.json.accepted_tasks` — neither has landed, so the pair order is intact. The recorded plan (G0 §Sequencing; `docs/DISCOVERY_BACKLOG.md:154`) still holds this packet's acceptance behind M5-T058's. **ACCEPT-TIME CONDITION (blocking, unchanged): M5-T059 must not be accepted before M5-T058 is accepted; accepting T059 first flips R003 to VIOLATED.** |

No requirement is VIOLATED, BLOCKED, or UNVERIFIABLE.

## 4. Harness outputs at the corrected identity

| Command | cwd | Result |
|---|---|---|
| `python -m ruff check .` | `services/api` | `All checks passed!` exit 0 |
| `python -m pytest tests/site_definition tests/api -q` | `services/api` | **594 passed** in 23.48s (§12.1 records 582 in `wt-m5t059`; +12 are M5-T057's accepted tests already at HEAD — same +12 delta I explained at the first freeze) |
| `python -m pytest tests/site_definition tests/api/test_site_definition_api.py tests/api/test_condo_records_api.py -q` | `services/api` | **61 passed** (57 + the 4 rework bindings) |
| `python tools/modularity_check.py --check` | repo root | **exit 0** (direct, unpiped); `selected 466 files; failures 0; warnings 20`; no warning names `app/site_definition/**` or `condo_records.py` despite `store.py` growth (11,304 → 14,157 B) and `records.py` (23,399 → 23,873 B) |
| `python tools/validate_directive_compliance.py --check` | repo root | **exit 0** at the settled head (direct exit code) |
| `tools/test_project_control.py`, `tools/test_directive_compliance.py`, `tools/test_directive_reminder.py` | CI | all three run by the `control-plane` job (`.github/workflows/ci.yml:432-446`) = **success at `03882888`** — the authoritative reproduction at this exact identity (my local runs of `test_project_control.py` (23 groups OK) and `test_directive_reminder.py` (12 OK) from the first pass still apply; `test_directive_compliance.py` exceeds this sandbox's runtime, 94 cases green before kill) |
| CI 35509631131 | GitHub | success at `03882888`, 18/18 jobs |

## 5. Prohibited-action evidence (re-checked)

Nothing merged (`30bc5349` contained only in `origin/candidate/D-024-mrl-option-b`); nothing accepted (`M5-T059` absent from `state.json.accepted_tasks`, status `awaiting_gate`); no PR opened/closed/merged (#241 hold intact, #64 unchanged); nothing deployed and no flag flipped (route unmounted, existing flag, `config.py` untouched); nothing installed/purchased (no dependency manifests in the material); no directive source or requirements edited without digest sync (validator exit 0).

## 6. Findings carried forward

- **F-1** — CLOSED (correction verified in the evidence map).
- **F-3 (advisory, slice 2)** — `default_site_definition_store()` is a process-global in-memory store; safe only while the route is unmounted. The revoke binding now also makes the mount precondition explicit. Unchanged recommendation: no mount before durability + authentication.
- **F-4** — run the validator only at settled heads (the M5-T060 seam transient).
- **F-5** — pytest 594 vs §12.1's 582 is the M5-T057 delta, not drift.
- **F-6 (new, non-blocking)** — "the other 8 packet paths byte-unchanged" is **7**; digest set itself is correct.

## 7. FRESH restamp pre-authorization (supersedes my earlier §8)

**(a) Content identity** — the 14 LF-normalized sha256 digests in §1 at `03882888` (the §12.1 six + the report's `c27c55bb…` + the seven unchanged).

**(b) Pre-authorization** — I pre-authorize restamping this verdict and the v2 verification rows for **D-066-R001, D-077-R002, D-077-R003, D-078-R001, D-078-R002, D-078-R003** to **any accept head at or past `03882888`**, provided at that head:
1. all 14 digests in §1 are unchanged (LF-normalized, `\r` stripped), and
2. `git diff --name-only <accept-head> 03882888 -- <the 14 paths>` is **EMPTY**, and
3. `python tools/validate_directive_compliance.py --check` exits **0** at that head, run at a **settled** head (F-4), and
4. **M5-T058 has been accepted before M5-T059** (the D-078-R003 accept-time condition, unchanged).

**(c) Disjoint peers explicitly tolerated** — in any number or order between freeze and accept:
- the M5-T058 lane (`wt-m5t058`, its 19 `allowed_paths`) **and M5-T058's full acceptance records** (gates, reports, evidence map, `state.json`, `tasks/M5-T058.json`, acceptance snapshot);
- the M5-T060 lane: new `apps/web` proposal-editor files plus `ArchitectEntry`/`navigation`/`ArchitectShell`/`architect.css`, its packet fixes, contract/claim seams and any relaunch commits;
- **this packet's own control-plane wave records** — `project-control/gates/M5-T059-*.json`, `project-control/reports/M5-T059-{G2,G3,G4,G5,HJ,DCV}*`, `M5-T059-evidence-map.json`, `tasks/M5-T059.json` lifecycle walks, `state.json` (all outside the 14);
- `project-control/**` seam commits generally, directive-registry appends + same-commit digest resyncs (including binds of other tasks onto D-066/D-077/D-078), `docs/DISCOVERY_BACKLOG.md`, `docs/SESSION_HANDOFF.md`, `.claude/agent-memory/**`;
- CI re-runs at those heads.

**(d) What voids it** — any of: a change to any of the 14 digests in §1 (including a further `[ORCH-CORRECTED]` edit inside `allowed_paths`); mounting the `site_definition` router in `main.py`, or any edit to a forbidden path folded into this packet's identity; acceptance of M5-T059 before M5-T058's acceptance; a directive source/requirements edit for D-066/D-077/D-078 without a recorded amendment + same-commit digest resync (validator non-zero at a settled accept head); or a v2 row stamping D-078-R001 as *directive-complete* rather than task-verified for M5-T059. Any of these requires a fresh delta attestation from me before accept.

## 8. Files cited (absolute)

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\site_definition\{records.py,store.py,__init__.py}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\api\v1\{site_definition.py,condo_records.py}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\site_definition\test_site_definition_records.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\api\test_site_definition_api.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M5-T059-producer-report.md` (§12.1)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M5-T059-evidence-map.json` (line 11, F-1 correction)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M5-T059-G0.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\{M5-T059.json,M5-T058.json,M5-T056.json}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-066-code-graph-loop-wiring\manifest.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\docs\DISCOVERY_BACKLOG.md` (line 154)

VERDICT: PASS
