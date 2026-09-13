# Wave-3 DCV verification — M4-T016 + M4-T017 (verbatim verifier return + addenda)

Recorded by the orchestrator from the independent directive-compliance-verifier's return.
Frozen verification head 7c2761c2; restamp to 920110be under the verifier's conditional
pre-authorization (ruling appended as Addendum B). Verdict: **PASS — all ten rows SATISFIED**.

---

## Verbatim verifier return

# D-001 Directive-Compliance Verification — M4-T016 + M4-T017 (wave-3 pair)

## (1) Frozen-head confirmation

`git rev-parse HEAD` = **`7c2761c2913f1809e4c923866c591b0e13716aa6`** — CONFIRMED, matches the
frozen verification head. I read all control-plane state from DISK. Uncommitted files present
are the expected orchestrator frozen-head pattern (agent-memory, scratchpad, `state.json`,
`tasks/M4-T016.json`, `tasks/M4-T017.json`, `reports/M4-T017.json`, `reports/M4-T016.json`,
`gates/M4-T016-G1.json`, `gates/M4-T017-G1.json`, the two G1 report files,
`reports/M4-T017-G1-research-review.md`). The two **research reports**
(`M4-T016-a2-geometry-mechanics-research.md`, `M4-T017-c-district-research.md`) are **clean vs
HEAD** (`git diff HEAD` empty; both tracked blobs) — so what I read equals the committed
material.

Material-identity chain reproduced by `git show --stat`:
- **eac7b42a** = M4-T016 producer report, touches ONLY
  `.../M4-T016-a2-geometry-mechanics-research.md` (+506/−4). `git diff eac7b42a 7c2761c2 --
  <that report>` = **EMPTY** → material unchanged from its commit through HEAD, so reviewing at
  reviewed_sha=HEAD is content-equivalent.
- **9fe63924** = M4-T017 producer report, touches ONLY
  `.../M4-T017-c-district-research.md` (+440/−4).
- **7c2761c2** (HEAD) = M4-T017 G1 rework + gate report + evidence maps; touches ONLY
  `M4-T016-evidence-map.json`, `M4-T017-G1-research-review.md`,
  `M4-T017-c-district-research.md` (+20/−5), `M4-T017-evidence-map.json`. I reproduced the
  report diff 939ca72b→7c2761c2: it is EXACTLY the three F5/F6 `[ORCH-CORRECTED]` edits (§1
  over-claim correction, new §7 item 7, §9 "19→20 rows"), no change to any verified
  quote/table — the delta-attestation is accurate.

## (2) Per-(task, requirement) verdicts

Applicability (c6 selective-citation) verified programmatically: for BOTH tasks and BOTH
directives, **applicable set == cited set** (no uncited-applicable, no cited-not-applicable).
D-045 & D-046 `source-001.md` content digests both MATCH their manifests.

### M4-T016 (material eac7b42a; unchanged through HEAD)

- **D-045-R002 — SATISFIED.** Report maps R6–R12 geometry mechanics (23-432 base table /
  23-433 setback / 23-73 series sky-exposure / 23-411 obstructions) with section #, title,
  districts, wide/narrow dependence, §12-10 terms, each with URL+retrieval-date+sha256
  provenance. OQ-4 designed from the quoted ZR 23-22 footnote-1 text, which I confirmed
  verbatim in the rule file. Data-input fit stated from actual code, all four code claims
  reproduced offline. §12-10 "wide street" 3/26/2026 amendment conflict kept VISIBLE and
  routed as OQ-4-a/b/c, never resolved (perm. principle 4). OQ-3 kept fail-closed.
  Evidence: report §0–§4; `r6_r7_r8_wide_street_conditional_far.rule.json:21` ("For zoning
  lots, or portions thereof, located within 100 feet of a wide street.");
  `dcm_street_centerline_arcgis.py` (returnGeometry absent; `build_segment_query_url:295`,
  `outSR=2263:397`, `parse_segment_page:768` reads `feature["attributes"]:797` only);
  `mappluto_lot_outline.py:1-22` (display-only, EPSG:4326); `mappluto_geometry_arcgis.py:215`
  (`BOUNDARY_TOLERANCE_FT=20.0`, EPSG:2263);
  `tests/fixtures/dcm_street_centerline/MANIFEST.json:153`.
- **D-045-R008 — SATISFIED.** Bounded gated packet: `gates/M4-T016-G0.json` PASS
  (orchestrator/administrative, reviewed 1cf2c488) + `gates/M4-T016-G1.json` PASS (reviewer
  `data-contract-verifier` ≠ producer `official-source-researcher`, reviewed_sha=HEAD, report
  present). `required_gates=[G0,G1]`. `allowed_paths` = single report file.
- **D-045-R009 — SATISFIED.** Material commit touches only the report; 7c2761c2 touches only
  report/evidence-map files — no rule/snapshot/code/dependency changed. DRAFT-until-G6 posture
  explicit (report §4.2/Part 4; OQ-3 routed to G6-class ruling). No hold lifted; commits touch
  no PR/gh state (PR #241 untouched) and no `apps/web/**` (expansion hold untouched).
- **D-046-R001 — SATISFIED.** Parallel wave recorded: dispatch commit **8de6ad9f** ("M4-T016 +
  M4-T017 producers running parallel in isolated worktrees … both pinned to 6dbf65fa"); both
  task `progress_log`s show 18:30 dispatch into `wt-m4t016`/`wt-m4t017`. Producer commit
  232a889b authored in a separate worktree, integrated sequentially by orchestrator
  (cherry-pick → eac7b42a). Matches the requirement's `required_harness`.
- **D-046-R002 — SATISFIED.** `allowed_paths` = `[M4-T016-a2-geometry-mechanics-research.md]`
  vs M4-T017's `[M4-T017-c-district-research.md]` — **zero shared files**. Material commit
  touches only its own report.

### M4-T017 (material 9fe63924; corrected at HEAD 7c2761c2)

- **D-045-R005 — SATISFIED.** Report answers RQ-002's four parts with captured evidence:
  commercial FAR (33-12/33-121, standalone 33-122/33-123 structural-only), overlay governing
  rule (34-111), residential equivalents table (34-112, incl. C4-6→R10 correction), suffix
  rules (11-25/11-121); each with section #, verbatim quote, URL, node id, PDF sha256. The
  **F5 correction IS present at HEAD** (§1 standalone-half over-claim corrected + new §7 item
  7 disclosing the structural-only deferral) — reproduced in the 939ca72b→7c2761c2 report
  diff. OQ-1..OQ-5 routed to architect/D-048, none resolved. OQ-3 factual premise confirmed
  offline (`r6_r12_residential_far.rule.json:36`: `"R9A":7.52`, matching the 7.50-vs-7.52
  flag).
- **D-045-R008 — SATISFIED.** `gates/M4-T017-G0.json` PASS (orchestrator/admin, 1cf2c488) +
  `gates/M4-T017-G1.json` PASS (reviewer ≠ producer; reviewed_sha=HEAD; report present with
  embedded delta-attestation confirming F5/F6 corrections satisfied at 7c2761c2).
  `required_gates=[G0,G1]`; single-file `allowed_paths`.
- **D-045-R009 — SATISFIED.** 9fe63924 touches only the report; 7c2761c2 touches only
  report/evidence/gate-report files — no rule/snapshot/code/dependency. DRAFT-until-G6
  explicit. No hold lifted; PR #241 & expansion hold untouched.
- **D-046-R001 — SATISFIED.** Same wave-3 dispatch (8de6ad9f); M4-T017 producer 46a8a110
  authored in separate worktree, cherry-picked → 9fe63924, integrated sequentially.
- **D-046-R002 — SATISFIED.** `allowed_paths` disjoint from M4-T016 (zero shared files);
  material commit touches only its own report.

**Evidence caveat (disclosed, does not change verdicts):** The byte-exactness of the
*web-fetched* ZR verbatim quotes/tables (23-432/23-433/23-736, §12-10 wide-street text;
33-12/33-121/34-111/34-112 PDFs) is not re-fetchable from this read-only sandbox (no network).
For those, my basis is: (a) the reports record complete provenance (URL, retrieval date, byte
count, sha256), (b) the independent `data-contract-verifier` reproduced them byte-exact via
live fetch (G1 reports F1–F8), and (c) every *offline-anchored* claim I could reproduce
(footnote-1 quote, connector code, MANIFEST note, R9A=7.52) checked out exactly. No
contradiction surfaced. These are research-half tasks (map/design/route), and the reproducible
surface is clean, so SATISFIED stands.

## (3) Discrepancies found

**One discrepancy — registry-wide, in D-050, independent of both tasks.**
`python tools/validate_directive_compliance.py --check` reports the registry **INVALID
(1 error)**:
> `c14 [D-050] requirements.json content digest mismatch (manifest 72532b6e4d52.. actual
> b42ef23d5d0b..): a requirement body was edited without a recorded amendment`

Characterization (reproduced): D-050's `manifest.json` `requirements_content_digest_sha256` =
`b42ef23d…` = the actual `requirements.json` hash = the HEAD-committed value (all internally
consistent); the stale `72532b6e…` is the pre-amendment-2 digest, surviving only in D-050's
`manifest.audit_log` notes ("Digest resynced 72532b6e → b42ef23d"). The validator's expected
value still resolves to the pre-resync `72532b6e` — a c14 index/manifest resync gap after
D-050 amendment-2 (source-003 / R006). **Note the earlier `EXIT=0` was `tail`'s exit, not the
validator's — the validator itself reports INVALID.**

Why it matters here, and why it does NOT fail any M4-T016/M4-T017 row: it is entirely scoped
to **D-050**; the validator flagged **no** error against D-045, D-046, M4-T016, or M4-T017;
D-045/D-046 source digests match; applicability==cited is clean; none of the three material
commits touch D-050. BUT both task packets list the validator as a `documented_test_command`
and it is fail-closed — recommend the orchestrator resync before relying on the validator/CI
gate at acceptance. This is control-plane hygiene on a different directive, not an
M4-T016/M4-T017 compliance defect.

No other discrepancies: gate reviewed_shas correct (G1=HEAD for both; G0=1cf2c488
contract-readiness), reviewer≠producer, no missing files, no SHA/gate-report mismatch, no
wrong-commit references.

## (4) Conditional restamp pre-authorization

I **pre-authorize** the orchestrator to restamp the `reviewed_sha` of my ten SATISFIED rows
above from `7c2761c2913f1809e4c923866c591b0e13716aa6` to a later commit **C** **if and only if
ALL of the following hold at restamp time**, each mechanically checkable:

1. `git diff 7c2761c2 C -- project-control/reports/M4-T016-a2-geometry-mechanics-research.md
   project-control/reports/M4-T017-c-district-research.md` is **empty**; AND
2. `git diff 7c2761c2 C -- project-control/directives/D-045-citywide-rule-coverage/requirements.json
   project-control/directives/D-046-parallel-family-production/requirements.json` is **empty**; AND
3. `git diff --stat 7c2761c2 C` shows changes ONLY under `project-control/` control-plane
   records (task JSONs, `state.json`, `gates/**`, `reports/**` evidence-map / gate-report /
   verification files) — i.e., **no** change to any `services/**`, `apps/**`, `packages/**`,
   `tools/**`, `.github/**`, rule ruleset, or `docs/research/zr-snapshots/**`, and no
   dependency/lockfile change (preserving D-045-R009); AND
4. C lifts no hold and does not touch PR #241 or any merge/deploy/accept-of-out-of-scope-work
   state.

Under those conditions the material and directive identity my verdicts rest on is provably
unchanged and my PASS carries to C. If any condition fails, a fresh verification pass is
required.

## Overall verdict: **PASS**

All ten rows (5 per task) are **SATISFIED** on reproduced primary evidence; applicability is
clean; material identity is frozen and confirmed at HEAD. The sole open item is the D-050
registry-digest resync (section 3) — out-of-scope control-plane hygiene, not an
M4-T016/M4-T017 requirement failure.

---

## Addendum A (orchestrator, evidence-backed): the section-3 D-050 discrepancy was a transient mid-write artifact

The verifier's validator run overlapped the companion session's live write of D-050
amendment 2 into this shared checkout (requirements.json updated before manifest.json — the
same transient signature observed during amendment 1 earlier today). The amendment landed as
commit 920110be; at that settled head the orchestrator re-ran
`python tools/validate_directive_compliance.py --check` with a direct exit code:
**VALIDATOR_EXIT=0**. Independent spot-check: D-050 manifest digest == recomputed
requirements.json digest (match: True). No resync gap exists; no remediation required.

## Addendum B (verifier ruling on restamp target C=920110be)

Received from the verifier (directive-compliance-verifier), verbatim (ruling portion):

> ### ITEM 2 — restamp ruling: **RESTAMP-AUTHORIZED for 920110be**
>
> I reproduced every gate mechanically at C = `920110be2ee4e4d82b7d9671d31a6c570b9aa100`
> (current HEAD): complete diff `7c2761c2..920110be` is exactly 4 files
> (`docs/RESEARCH_REQUESTS.md`, `D-050/{manifest.json, requirements.json,
> source-003-amendment.md}`); Cond 1 — both material report files: diff **EMPTY**; Cond 2 —
> cited D-045 & D-046 `requirements.json`: diff **EMPTY**; Cond 4 — holds intact, PR #241
> untouched, no accept/merge/deploy state; prohibited-surface scan **NONE** (no `services/`,
> `apps/`, `packages/`, `tools/`, `.github/`, no ruleset, no zr-snapshot, no
> dependency/lockfile); c6 safety — D-050 (now R001–R006) has **zero** requirements applicable
> to M4-T016/M4-T017, so restamping introduces no uncited-applicable requirement.
>
> **Explicit ruling on the Condition 3 literal gap**: My Condition 3 was written to guarantee
> the *intent* "no code/rule/snapshot/dependency/prohibited-surface change so D-045-R009
> preservation holds," which I enumerated (imperfectly) as "only under `project-control/`."
> Commit 920110be exceeds that literal text on exactly two benign axes — (a) a **non-cited
> directive's** registry files (D-050, which has no applicability to either task and whose
> requirements the tasks correctly do not cite) and (b) one **docs/ queue file**
> (`docs/RESEARCH_REQUESTS.md`) that is not a ruleset, zr-snapshot, code, or dependency.
> **The intent of Condition 3 is fully satisfied.** I therefore **extend my pre-authorization**
> and restate the governing condition as: Restamp is authorized to a later commit C iff:
> (1) both material report files are byte-identical to 7c2761c2; (2) the cited D-045/D-046
> `requirements.json` are byte-identical; (3′) C touches **no** prohibited surface and adds no
> requirement applicable to M4-T016/M4-T017 without citation (c6 clean); (4) C lifts no hold,
> leaves PR #241 unmerged, and records no accept/merge/deploy of out-of-scope work.
> Commit **920110be satisfies all four** as reproduced above.
>
> **RESTAMP-AUTHORIZED for 920110be** — the orchestrator may restamp the `reviewed_sha` of all
> ten SATISFIED rows (M4-T016 and M4-T017 × {D-045-R002/R005, D-045-R008, D-045-R009,
> D-046-R001, D-046-R002}) from `7c2761c2` to `920110be`. My PASS verdicts carry unchanged.

The verifier also independently corroborated Addendum A (ITEM 1): its original INVALID came
from a long-running validator read overlapping the companion's mid-write (requirements.json
before manifest.json — the stale 72532b6e is the amendment-1 digest caught pre-resync); the
settled committed state at 920110be is internally consistent, and the orchestrator's direct
re-run at that head returned VALIDATOR_EXIT=0.
