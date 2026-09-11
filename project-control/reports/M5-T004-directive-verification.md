# M5-T004 — Independent Directive-Compliance Verification (D-038)

**Verifier:** directive-compliance-verifier (independent; did not author the code, the
evidence map, any gate report, or the packet).
**Verified at:** 2026-09-11. Read-only on the repository throughout.
**Repo root:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`

---

## VERDICT: PASS

With one recorded OVERSTATEMENT that must be struck from the evidence map, and four
lesser imprecisions recorded below. The PASS does not rest on any of them: both
applicable requirements were confirmed against the tree directly.

---

## 0. Identity — verified, not taken on trust

| Claim | Verified |
|---|---|
| HEAD = `9b4178755facda932c19c893d4ff2710a0f0d86a` | YES — `git rev-parse HEAD` |
| Content manifest = `9f57ea9e886ef1909fd6f6260877c5e560e3b8af4740d7a9a0ef16cf97692c67` | YES — **recomputed independently** |
| Gates carry that manifest | YES — G1/G3/G4/G5 all `9f57ea9e…` at `9b417875` |

The manifest was not read off the gate records. I imported `tools/directive_registry`
and `tools/project_control` and called `_task_git_identity(dr, packet)` — the same
single function submit, gate and accept all use — against the live tree:

```
identity      = 9f57ea9e886ef1909fd6f6260877c5e560e3b8af4740d7a9a0ef16cf97692c67
resolved_sha  = 9b4178755facda932c19c893d4ff2710a0f0d86a
error         = None
```

`error = None` is itself load-bearing: the function runs with `require_clean=True`, so a
dirty tracked file or an untracked file inside `allowed_paths`, or a *material*
working-tree change to a control-plane file in scope, would have failed closed. The tree
IS dirty (`docs/MVP_AGENDA.md`, the four gate records, `state.json`, the packet, and two
untracked reports), but none of that intersects the task's allowed paths materially — the
packet diff is `status`/`progress_percent`/`updated_at`/`progress_log` bookkeeping plus one
mojibake-normalized `inputs` string, and the evidence map itself is not an allowed path.

Directive files also verified at this identity:
- `requirements.json` sha256 = `f62c6fc8cec2497af0d6170d232559df79544fe06239f44b80bea1bea0f39f0b`,
  **byte-equal to `manifest.json.requirements_content_digest_sha256`.**
- `locked_requirement_ids` = R001…R007, count 7, matching `requirement_count`.
- `python tools/validate_directive_compliance.py --check` → **EXIT 0**.
- Submitted report record `project-control/reports/M5-T004.json` carries the same
  `content_manifest_sha256` / `reviewed_sha` pair and names the evidence map.

No stale-identity condition. Proceeding.

---

## 1. APPLICABLE REQUIREMENTS

### **D-038-R003 and D-038-R004. Exactly those two. The evidence map is CORRECT.**

Three independent derivations agree:

**(a) The `authority_note` (governing).** `verification.json` states: *"loop-governance
requirements (R001/R002/R005/R006/R007) bind the non-ledger sentinel D-038-BOOTSTRAP.
Product-task rows accrue as tasks produce durable evidence."* That excludes five and
leaves two.

**(b) `requirements.json` applicability, read directly.** R003 and R004 each carry
`applicability.task_ids` = `["M5-T003" … "M5-T013"]`, which **contains M5-T004**.
R001, R002, R005, R006 and R007 each carry `applicability.task_ids` = `["D-038-BOOTSTRAP"]`
and nothing else. The manifest `audit_log` entry of 2026-09-08T14:52:30Z records the
append of M5-T004 to R003/R004 under R003's own contracted-tasks mechanism, with no
requirement id added, removed or renumbered.

**(c) The registry, executed.** The packet stamps `requirement_ids: "ALL"`, which resolves
to *all-applicable-to-this-task*, not all-seven. I ran the resolver:

```python
reg.evaluate_task_refs(json.load(open("project-control/tasks/M5-T004.json")))
→ ok = True
  applicable_ids = ['D-038-R003', 'D-038-R004']
  reasons = []
```

**Why R002 is excluded even though it is the most task-shaped of the five.** R002
prohibits *assigning the loop self-infrastructure as its build target while unblocked
product work exists.* It is a constraint on **target selection**, which is an act of the
loop, discharged once at dispatch — not a property a delivered artifact can carry. Its
`applicability.task_ids` says so explicitly. Its *substance* is nonetheless tested at the
task level, because R003 is the positive form of the same rule ("the loop's build target
must be actual PRODUCT engineering") and R003 declares `dependencies: ["D-038-R002"]`. So
the not-self-infra check is performed here — it is simply performed **under R003**, which
is where the evidence map correctly files it (the bullet sits inside the `D-038-R003` key,
even though its prose labels it "D-038-R002 prohibition satisfied"). See imprecision (4).

R006 deserves a note for the same reason: it prohibits push/PR/merge. That binds the
sentinel, and I did not evaluate it as a row. Observed in passing, without ruling on it:
`origin/candidate/D-024-mrl-option-b` sits at `0c810887`, so the first-round producer
output `84815a76` and the first-round gate records **are pushed**; the entire rework chain
(`dc68c761` → `9b417875`) is not. That push predates this verification and is recorded at
`02379432` ("FIRST EVER PUSH + FIRST EVER CI RUN"). Flagged for the sentinel's row, not
this one.

---

## 2. PER-REQUIREMENT

### D-038-R003 — Positive deliverable is PRODUCT engineering, contracted as a normal G0 packet with executable acceptance scenarios. **SATISFIED.**

**The deliverable is a user-facing product screen, and it is one of the three things
R003 names.** R003's text: *"user-facing screens (Compare/Evidence/report/reviewer UI),
additional deterministic rule families, or the scenario/optimization engine."* This is the
Compare screen, named first in that list and named again in the pivot plan recorded in the
manifest audit log ("Compare UI → Evidence view → rule families"). Files confirmed present
on disk at HEAD:

```
apps/web/src/app/property/compare/page.tsx
apps/web/src/components/compare/  CompareScreen · ScenarioCard · ScenarioResult ·
  CoverageMatrixSection · ScenarioConstraints · ScenarioAssumptions · ScenarioProvenance ·
  ScenarioReasons · ScenarioFailureStates · NoScenarioBlock
apps/web/src/lib/  scenario-api.ts · scenario-contract.ts · scenario-contract-checks.ts ·
  scenario-bounds.ts · scenario-display.ts
```

`page.tsx` was created by `84815a76`; the route did not exist before. The ConfirmScreen
dead-end rewire is real (`git show 84815a76 -- .../ConfirmScreen.tsx`, 15 lines changed at
the `next-action` section). Map claim confirmed.

**Contracted as a normal G0 packet with executable acceptance scenarios.**
`project-control/gates/M5-T004-G0.json` = PASS, reviewer orchestrator, at the contract-time
SHA `3879d4c4`. The packet carries **8** acceptance scenarios AS-1…AS-8, each written as an
executable assertion (AS-1 literally specifies *"test asserts the rendered value === the
body value"*). `required_gates` = G0/G1/G3/G4/G5; all five recorded PASS at `9b417875`.

**PRODUCT, not self-infrastructure — verified commit by commit, not by reading the map.**
I enumerated the seven work commits and took each one's file list:

| commit | scope |
|---|---|
| `84815a76` producer output | 12 × `apps/web/**` + `project-control/reports/M5-T004-producer-report.md` |
| `dc68c761` rework 1 | 21 × `apps/web/**` + the producer report |
| `26e35eb5` rework 2 | 4 × `apps/web/**` |
| `e7ad9b1d` rework 3 | 10 × `apps/web/**` |
| `104eaaef` rework 4 | 2 × `apps/web/**` |
| `41943cdf` rework 5 | 3 × `apps/web/**` |
| `9b417875` rework 6 | 2 × `apps/web/**` + the producer report |

**Zero files under `tools/`, `.claude/`, `services/`, `packages/contracts/`, `supabase/`,
or anywhere in the supervisor.** Every one of those is in the packet's `forbidden_paths`,
and none was touched. The map's claim — *"The diff is apps/web plus one producer report"* —
is exactly right, and it is the R002-substance check R003 depends on.

**The FAIL → rework → PASS arc is real and the map does not soften it.** First round at
`84815a76`: I opened all five reports and read the verdict line of each — G1 **FAIL**,
G3 **FAIL**, G4 **FAIL**, G5 **PASS**, DCV **FAIL**. That is FAIL 4–1, as claimed. The
four gate records carry those first-round verdicts in their `history[]` arrays, preserved
rather than overwritten. Re-review at `9b417875`: PASS 5–0
(`project-control/reports/M5-T004-rereview.md`), and the four gate records now read PASS at
manifest `9f57ea9e…`.

The headline numbers in the map are transcribed correctly from the source reports:
`191/515` is `M5-T004-DCV.md` line 21–22 verbatim; `656/665`, `0/96 → 96/96` and `45/45`
are the rereview headline table verbatim.

**Independence holds.** Producer is `frontend-engineer` (loop run persistent-local-20,
broker-blocked from git). Gate reviewers are `code-reviewer` (G1), `human-journey-reviewer`
(G3), `qa-engineer` (G4), `security-reviewer` (G5), plus an unrecorded fifth, the in-wave
DCV. None is `frontend-engineer`. See §5 for the one correction I make to the producer
label.

### D-038-R004 — Built AND verified with no Supabase, no Geoclient, no credentials. **SATISFIED.**

**AS-7 is the scenario that carries this, and its text says so.** Read from the packet
verbatim: *"AS-7 offline / no-credentials (proves D-038-R004): AS-1..AS-6 run entirely
under vitest with mocked/fixture endpoint responses (committed M5-T003 fixtures) and/or the
Playwright e2e against apps/web/e2e/harness/fixture_api.py - NO network, NO Supabase, NO
Geoclient."* The map's paraphrase is faithful.

**I re-audited the offline property myself at `9b417875` rather than relying on the cited
gate.** Across all four test files under `components/compare/__tests__/`:

- 49 call sites use either an injected `fetchImpl` or a `renderCompare`/`stubFetch` helper.
- Every `vi.stubGlobal("fetch", …)` site passes `vi.fn()` or a local spy —
  `compare-entry.test.tsx:36,55,70,87` and `compare-screen.test.tsx:593`.
- `vi.unstubAllGlobals()` runs in `afterEach` in both files that stub
  (`compare-entry.test.tsx:29`, `compare-screen.test.tsx:26`).
- **Zero bare `fetch(` calls** anywhere in the four files (regex `(^|[^.a-zA-Z])fetch\(`).

**The Playwright layer is local-only.** `apps/web/playwright.config.ts` pins
`baseURL: "http://127.0.0.1:3000"` and starts exactly two local servers:
`python e2e/harness/fixture_api.py` on `127.0.0.1:8000` and `npm run start` on
`127.0.0.1:3000`. No live backend, no cloud host.

**The harness-flag citation is exact.** The map says *"fixture_api.py:265 enables
INTERNAL_SCENARIO_ENABLED"*. Line 265 is literally
`os.environ[INTERNAL_SCENARIO_ENABLED_ENV_VAR] = "1"`, with a ten-line comment above it
explaining that the harness previously enabled only `INTERNAL_RULE_EVAL_ENABLED` (line 253)
and that no browser could reach `/property/compare` anywhere in the repo. Precise to the
line number.

**"First Playwright journeys anywhere in the repository that navigate to that route" —
true.** `grep -rn "property/compare" apps/web/e2e/` returns hits in exactly one spec file,
`compare-journey.spec.ts` (lines 45, 58, 96, 125, 144), plus two comment references. There
are 19 spec files; the other 18 contain no navigation to that route.

**No credentials in the fixtures.** `grep -rniE "token|secret|api[_-]?key|password|supabase|
geoclient|https?://"` over `__tests__/scenario-fixtures.ts` and `e2e/compare-journey.spec.ts`
returns **nothing**. The only network-shaped constant is the build-time `apiBaseUrl()`
default, as G5 recorded.

**Nothing in the client computes a legal or numeric document value.** Grepping for
`toFixed|toLocaleString|Math\.|parseFloat|parseInt|Number\(|Intl\.` across the compare
components and all five scenario lib modules returns exactly two hits, and neither touches
a document value: `ScenarioFailureStates.tsx:279` rounds the **client's own timeout
constant** into a sentence, and `scenario-api.ts:288` parses the **Content-Length header**
for the response-size guard. The display formatter is the pre-existing `./format` module
(outside this diff), and the first-round DCV already established its only transform is
en-US digit grouping, which changes no magnitude and no significant digit. See imprecision
(2) for the wording.

**The bounding claims are true to the constants.** `MAX_DOCUMENT_ARRAY_LENGTH = 64`
(`scenario-contract-checks.ts:35`), `MAX_REFLECTED_TEXT_LENGTH = 600` and
`MAX_TOKEN_LENGTH = 64` (`bounded.ts:20-21`), `MAX_RESPONSE_BYTES = 256 * 1024`
(`scenario-bounds.ts:72`). Arrays reject, free text truncates visibly, identifiers reject
rather than being sanitized — the module docstring at `scenario-bounds.ts:14-29` states
each policy and the code matches it.

**Contract validation runs before render.** `scenario-api.ts:331` calls
`validateScenarioDocument(body)` inside `fetchScenario`, before any component sees the
document; `scenario-contract.ts:533` pins `contract_version !== "1.0.0"` as a hard reject.
AS-4 as written.

---

## 3. OVERSTATEMENT CHECK

### **ONE overstatement. It must be struck.**

**The evidence map attributes to G4 an independent network audit that G4 never performed.**

`M5-T004-evidence-map.json`, `D-038-R003` bullet 5, final clause:

> "G5 audited every render and fetchScenario site and found zero reaching global fetch;
> **G4 independently audited every test for a real network call and found none.**"

The G5 half is **verbatim accurate** — `M5-T004-G5.md:45` enumerates 18 render/`fetchScenario`
sites, states **"Zero sites reach global `fetch`"**, notes `vi.unstubAllGlobals()`, and adds
"No credential, token, or real endpoint in the fixtures; the only network-shaped constant is
the build-time `apiBaseUrl()` default."

The G4 half is **not in G4's report, in any form.** I grepped
`real network|network call|no network|offline|AS-7|reach.*network|global fetch` across
`M5-T004-G4.md` and the rereview's G4 section. `M5-T004-G4.md` contains **no offline audit
and no AS-7 finding at all**; its only adjacent sentence is finding 5, which says the
opposite kind of thing — that `CompareEntry` has *zero* coverage, including "the guarantee
that no fetch is issued for an invalid parameter." G4's finding 6 is likewise a
*coverage-absence* finding about the e2e layer. G4 did not corroborate offline-ness; G4
reported gaps in it.

This is the specific failure mode this gate exists to catch: **a second, independent
corroboration was asserted where only one reviewer actually looked.** It manufactures
redundancy in the exact place — R004, the credential constraint — where redundancy is the
point.

**Why it does not carry the verdict.** R004 survives without it on two legs I hold myself:
G5's audit (real, verbatim, quoted above) and my own re-audit at `9b417875` in §2. So the
conclusion is sound and the citation is not. The remedy is to strike the clause, not to
fail the task — and the row's `note` records it permanently either way.

**Required before the row is appended:** delete `; G4 independently audited every test for a
real network call and found none` from `D-038-R003` bullet 5 of the evidence map. If the map
is appended unchanged, the `note` in §4 is the corrective record and must not be softened.

### Four lesser imprecisions — recorded, none disqualifying

**(1) The cited G5 audit is a FIRST-ROUND audit, presented without that qualifier.**
G5's AS-7 enumeration counted 18 sites in *one* file, `compare-screen.test.tsx`, at
`84815a76`. At `9b417875` there are four test files plus a new Playwright spec, and the
rereview's G5 section does **not** re-state the offline audit. So the map cites evidence
gathered at the superseded SHA as though it covered the reviewed one. I closed this gap
myself (§2) and the property still holds at HEAD — but the map should say which round it is
quoting.

**(2) "No legal or numeric value is computed, derived, rounded or defaulted anywhere in the
client" is literally false as written.** `Math.round(outcome.timeoutMs / 1000)`
(`ScenarioFailureStates.tsx:279`) rounds; `Number(declaredLengthHeader.trim())`
(`scenario-api.ts:288`) parses; `input.input_fingerprint ?? "not stated"`
(`ScenarioProvenance.tsx:145`) defaults; the shared formatter applies locale grouping. All
four are presentational and none touches a document legal value, so the **substance** is
right and the measured claim in the next bullet ("0 authored legal/numeric values") is the
one that matters. Tighten the wording to "no legal or numeric **document** value."

**(3) "the full provenance trail" is stronger than the measurement.** The measured figure
is 656 of 665 leaves transported (effective 659), with 9 authored — all
authored-presentational after rework 6, per the rereview's DCV section. "Full" overstates
by nine leaves. The exact number appears one bullet later, so the map does not conceal it.

**(4) The R002 label.** Bullet 3 is headed "(D-038-R002 prohibition satisfied)". Per the
`authority_note`, R002 binds the sentinel and is **not applicable to a ledger task**; no
R002 row may appear in this task's verification (the registry treats a non-applicable row as
contamination and fails closed). The evidence is correctly *filed* under the `D-038-R003`
key, so this is a prose label, not a structural claim — but it should read "R002 substance,
verified under R003, on which R003 declares a dependency."

### What the map does NOT overstate — checked and found honest

- It does **not** claim any test passed, any suite ran green, or any CI run exists.
- It does **not** claim "all findings addressed." It states the arc and the measured deltas.
- It does **not** claim the acceptance scenarios were sufficient. The rereview records the
  opposite — item 5, *"All 8 of this packet's acceptance scenarios PASSED at `84815a76`
  while four of five gates FAILED. The criteria under-specified the honesty bar"* — and I
  confirmed it at `M5-T004-DCV.md:126` ("Per-AS verdicts — ALL PASS") sitting under
  "VERDICT: FAIL" at line 11. That is a damaging fact about the packet's own criteria, and
  the re-review published it.
- The rereview names **three** orchestrator errors, not two — the uncommitted `allowed_paths`
  widening, a wrong reviewer brief about response caps (corrected by G5), and a wrong claim
  that a header check was stronger than a streaming read (corrected by G5). Self-reported.

---

## 4. "NO GREEN CLAIMED" — HONEST

`apps/web/node_modules` is **absent** (`ls` confirms; no `node_modules` anywhere within
three levels). Neither producer nor reviewers could have run
`npm --prefix apps/web run test | typecheck | test:e2e`.

The evidence map says so plainly, in `D-038-R004` bullet 3:

> "No node_modules is installed anywhere under the thin-client policy
> (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md), so neither the producer nor any of the
> five reviewers executed the documented test commands. **NO GREEN IS CLAIMED at
> acceptance; CI is the authority.** G4's CI prediction is static, derived from reading the
> configs, hand-checking every cross-module signature, and transcribing
> validateScenarioDocument into Python to run all four committed fixtures through it
> (4/4 PASS)."

Every part checks out. The policy file exists. The rereview header carries the same
disclosure independently: *"Not executed: apps/web/node_modules is absent under the
thin-client policy. No reviewer ran the suite; no green is claimed. CI is the authority."*
The first-round DCV said it too. The producer's own commit message at `84815a76` says
*"Producer did NOT run frontend tests … and claims NO green."* Four independent
disclosures, none hedged. **This is the standard the regime asks for and the map meets it.**

The G4 transcription is correctly labelled as what it is — a re-implementation of the
validator in Python run against the four committed fixtures, 4/4 — not as a suite run.

**One adjacent item the map is clean on but the packet is not.** The packet's own
`progress_log` entry of 2026-09-11T03:04Z contains: *"'no test was ever executed' was wrong
— compare-screen.test.tsx runs under npm run test at ci.yml:96 in the web-e2e job and
passed."* Read one way that asserts a passing CI run. It cannot refer to the reviewed SHA:
`origin` is at `0c810887` and the entire rework chain is unpushed, so no CI run for
`9b417875` can exist. The evidence map does **not** repeat or rely on this sentence — it is
a packet-record looseness, not an evidence-map overstatement, and I record it so it is not
inherited.

---

## 5. PRODUCER ≠ VERIFIER — HOLDS, with one correction to the label

| Role | Identity | Distinct from producer? |
|---|---|---|
| Producer (code) | `frontend-engineer`, loop run persistent-local-20, broker-blocked from git | — |
| G0 intake | orchestrator | contract-time, not a review of the code |
| G1 | `code-reviewer` | yes |
| G3 | `human-journey-reviewer` | yes |
| G4 | `qa-engineer` | yes |
| G5 | `security-reviewer` | yes |
| In-wave DCV | independent data-contract verifier ("read-only; did not author the code") | yes |
| Evidence map, rework brief, commits | orchestrator | — |
| **Directive verification (this row)** | `directive-compliance-verifier` | yes |

No producer verifies their own work anywhere in the chain.

**One correction I make in the proposed row.** The packet's `producer_agent` is
`frontend-engineer` alone, but the orchestrator authored the evidence map, wrote the rework
brief, committed every work commit, and made three recorded errors on this packet. Recording
the producer as `frontend-engineer` only would let the orchestrator be filed as a neutral
gate-runner. M5-T013's accepted row already handles this correctly, recording
`"producer": "backend-engineer/orchestrator"`. **I use `frontend-engineer/orchestrator`** for
the same reason — this is a change from the packet's label, made deliberately, and it still
satisfies the registry's independence check (`_identity_key` normalizes case and whitespace
only; the two strings do not collide).

**Naming collision worth recording:** the "DCV" in this packet's five-reviewer wave is
**Data-Contract Verification**, a code reviewer with no gate record file. It is **not** the
directive-compliance verifier. Those are different roles and the `gates/` directory holds
only G0/G1/G3/G4/G5. Anyone reading "DCV PASS" in the rereview must not read it as a
directive-compliance attestation; this row is that, and it did not exist until now.

---

## PROPOSED ROW

Append to `project-control/directives/D-038-build-product-not-self/verification.json`
under `task_verifications[]`. Schema-checked against `_v2_task_unresolved`: single row for
the pair, `producer` and `verifier` both present and non-equal, `reviewed_manifest_sha256`
and `reviewed_sha` both present and current, `applicable_requirement_ids` equal to the
derived set, no extra or cross-task rows, both states `PASS`.

```json
{
 "directive_id": "D-038",
 "task_id": "M5-T004",
 "applicable_requirement_ids": [
  "D-038-R003",
  "D-038-R004"
 ],
 "reviewed_sha": "9b4178755facda932c19c893d4ff2710a0f0d86a",
 "reviewed_manifest_sha256": "9f57ea9e886ef1909fd6f6260877c5e560e3b8af4740d7a9a0ef16cf97692c67",
 "producer": "frontend-engineer/orchestrator",
 "verifier": "directive-compliance-verifier",
 "schema_version": "directive_verification/v2",
 "verified_at": "2026-09-11T05:10:00+00:00",
 "note": "Independent DCV at HEAD 9b417875, content identity 9f57ea9e RECOMPUTED by the verifier from the live tree via the shared _task_git_identity path rather than read off the gate records; requirements.json digest f62c6fc8 re-confirmed byte-equal to the manifest; validate_directive_compliance --check EXIT 0. Applicable set re-derived three ways - the authority_note (R001/R002/R005/R006/R007 bind the non-ledger sentinel D-038-BOOTSTRAP), the requirements.json applicability blocks, and reg.evaluate_task_refs() executed - all three returning exactly R003+R004 from the packet's 'ALL' stamp. R002's PROHIBITION is not a row here because it constrains the loop's target SELECTION, an act discharged at dispatch; its substance is tested under R003, which declares R002 as a dependency, and it holds: the seven work commits (84815a76, dc68c761, 26e35eb5, e7ad9b1d, 104eaaef, 41943cdf, 9b417875) touch apps/web/** and project-control/reports/M5-T004-producer-report.md and NOTHING ELSE - zero files under tools/, .claude/, services/, packages/contracts/, supabase/ or the supervisor, every one of which is in this packet's forbidden_paths. DELIVERABLE: the Compare (Step 3) screen, first-named in R003's own list of product work and first in the pivot plan recorded in the manifest audit log (Compare UI -> Evidence view -> rule families). The route did not exist before 84815a76 and the Confirm screen dead-ended. ARC: gate wave at 84815a76 returned FAIL 4-1 - G1, G3, G4 and the in-wave data-contract reviewer FAIL, G5 PASS - on a SILENT PROJECTION, the M5-T013 defect class reproduced: 191 of 515 traced leaves reached the screen, 324 dropped, and the document's most-severe completeness verdict (missing_critical) never rendered while the milder coverage gloss did. Six reworks; re-review at 9b417875 PASS 5-0 with 656/665 leaves transported, 0 authored legal/numeric values, constraint leaves 0/96 -> 96/96 on the conflict fixture, 45/45 schema leaves rendering, tests ~13 -> 57+. ORCHESTRATOR ERRORS, all three self-reported in the re-review and recorded here so they are not inherited: (1) the allowed_paths widening for globals.css, property/error.tsx, e2e/harness/fixture_api.py and e2e/compare-journey.spec.ts was made in the working copy BEFORE the rework was dispatched and NOT COMMITTED until G4's re-review flagged it, so all five reviewers correctly read a 6-path packet and correctly reported four files as out of scope - not a producer violation, none of the four was ever in forbidden_paths, ratified at ab7478e1; (2) the reviewer brief wrongly stated the API caps responses at 64 KiB / 200 legs, corrected by G5; (3) the one-line Content-Length check was described as stronger than a streaming read, corrected by G5 (Content-Length is the COMPRESSED count and .json() decompresses transparently). NO TEST EXECUTION OCCURRED. apps/web/node_modules is absent under the thin-client policy (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md); neither the producer nor any of the five reviewers ran the three documented commands, and NO GREEN IS CLAIMED - four independent disclosures say so (producer commit message, first-round DCV method note, re-review header, evidence map). Verification was code reading, direct evaluation of pure functions, and one transcription of validateScenarioDocument into Python run against all four committed fixtures, 4/4. CI is the authority and no CI run can exist for this SHA: origin sits at 0c810887, so the first-round output is pushed but the entire rework chain is not. The packet progress_log of 2026-09-11T03:04Z contains a looser sentence ('compare-screen.test.tsx runs under npm run test at ci.yml:96 ... and passed') which cannot refer to this SHA; the evidence map does not repeat or rely on it. EVIDENCE MAP OVERSTATEMENT, recorded because the map is the cited artifact: R003 bullet 5 asserts 'G4 independently audited every test for a real network call and found none.' G4 performed NO such audit - M5-T004-G4.md contains no offline or AS-7 finding at all, and its nearest statements are coverage-ABSENCE findings (finding 5: CompareEntry untested including the no-fetch-on-bad-param guarantee; finding 6: no browser-level coverage of the route). The G5 half of that same sentence is verbatim accurate (G5.md:45, 'Zero sites reach global fetch'). The clause manufactures a second corroboration where one reviewer looked, and it must be struck from the map. R004 does NOT rest on it: this verifier re-audited offline-ness independently at 9b417875 - 49 injected-fetchImpl or stubbed sites across the four compare test files, every vi.stubGlobal passing vi.fn() or a local spy, vi.unstubAllGlobals in afterEach in both stubbing files, ZERO bare fetch( calls, playwright.config.ts bound to 127.0.0.1:3000 with only two local servers (e2e/harness/fixture_api.py on 127.0.0.1:8000 and npm run start), fixture_api.py:265 setting INTERNAL_SCENARIO_ENABLED exactly as cited, compare-journey.spec.ts the only one of 19 specs navigating to /property/compare, and no token, secret, key or URL anywhere in the compare fixtures or the new spec. LESSER IMPRECISIONS: the cited G5 offline audit is a FIRST-ROUND audit of 18 sites in one file and is presented without that qualifier (re-verified here at the reviewed SHA); 'no legal or numeric value is computed, derived, rounded or defaulted anywhere in the client' is literally contradicted by Math.round on the client's own timeout constant, Number() on Content-Length, one ?? 'not stated' absence marker and locale digit grouping, all presentational and none a document legal value; 'the full provenance trail' overstates 656/665 by nine authored-presentational leaves, the exact count appearing one bullet later; and the R002 label on bullet 3 should read 'R002 substance, verified under R003'. NO CREDENTIALS: fully offline, no Supabase (B-001), no Geoclient (B-004), consuming the accepted M5-T003 endpoint behind INTERNAL_SCENARIO_ENABLED over committed fixtures - both fixture-based tests and public-connector reads explicitly permitted by R004's own text. CARRIED, not defects in this packet: the same authored-temporal-claim defect ('to present' for an absent end date) lives on the ACCEPTED RuleEvaluationResult.tsx:251, outside allowed_paths, recorded in docs/MVP_AGENDA.md C1; a dormant assumptions[].key normalization landmine, C2; the transport-shell clone now in three copies needing its own extraction task; the compressed-response bound per G5's carry-forward; no web-layer gate, no CSP and no auth on /property/compare, where flag gating is the only containment; and the sufficiency lesson that ALL EIGHT acceptance scenarios PASSED at 84815a76 while four of five gates FAILED, which the re-review published against itself and M4-T009's packet was written against. NAMING: the 'DCV' in this packet's five-reviewer wave is Data-Contract Verification, a code reviewer with no gate record; it is NOT the directive-compliance verifier. This row is that, and it did not exist until now. Producer recorded as frontend-engineer/orchestrator per the M5-T013 convention: the orchestrator authored the evidence map, the rework brief and every commit, so it is a co-producer here and not a neutral gate-runner. Verifier independent of both, and of all five reviewers.",
 "requirements": [
  {
   "id": "D-038-R003",
   "state": "PASS",
   "evidence": [
    "apps/web/src/app/property/compare/page.tsx + 10 modules under apps/web/src/components/compare/ (CompareScreen, ScenarioCard, ScenarioResult, CoverageMatrixSection, ScenarioConstraints, ScenarioAssumptions, ScenarioProvenance, ScenarioReasons, ScenarioFailureStates, NoScenarioBlock) - all confirmed present on disk at 9b417875. The Compare (Step 3) USER-FACING SCREEN, first-named in R003's own list of qualifying product work and first in the pivot plan recorded in the D-038 manifest audit log. page.tsx was created by 84815a76; before it the route did not exist and ConfirmScreen dead-ended (rewire confirmed by git show 84815a76 -- ConfirmScreen.tsx, 15 lines at the next-action section)",
    "PRODUCT, NOT SELF-INFRASTRUCTURE - verified commit by commit rather than from the evidence map. All seven work commits enumerated and their file lists taken: 84815a76 (12 apps/web + producer report), dc68c761 (21 + report), 26e35eb5 (4), e7ad9b1d (10), 104eaaef (2), 41943cdf (3), 9b417875 (2 + report). ZERO files under tools/, .claude/, services/, packages/contracts/, supabase/ or the supervisor - every one of those is in this packet's forbidden_paths and none was touched. This is the R002-substance check R003 depends on",
    "Contracted as a normal G0 packet with EXECUTABLE acceptance scenarios: gates/M5-T004-G0.json PASS at contract-time SHA 3879d4c4; 8 scenarios AS-1..AS-8 each written as an assertion (AS-1 specifies 'test asserts the rendered value === the body value; the client NEVER recomputes it'); required_gates G0/G1/G3/G4/G5 all recorded PASS at reviewed_sha 9b417875 and content identity 9f57ea9e, with each record's first-round FAIL preserved in its history[] rather than overwritten",
    "FAIL 4-1 -> six reworks -> PASS 5-0, verdict lines read from the reports themselves: M5-T004-G1.md FAIL, -G3.md FAIL, -G4.md FAIL, -G5.md PASS, -DCV.md FAIL at 84815a76 on a silent projection (191/515 leaves transported, 324 dropped, the document's missing_critical completeness verdict never rendering while the milder coverage gloss did); M5-T004-rereview.md PASS 5-0 at 9b417875 with 656/665 transported, 0 authored legal/numeric values, constraint leaves 0/96 -> 96/96, 45/45 schema leaves rendering. The 191/515 figure is DCV.md lines 21-22 verbatim; the rest is the re-review headline table verbatim",
    "No legal or numeric DOCUMENT value is computed in the client: grepping toFixed|toLocaleString|Math.|parseFloat|parseInt|Number(|Intl. across all compare components and all five scenario lib modules returns exactly two hits, neither on a document value - Math.round(outcome.timeoutMs / 1000) on the client's own timeout constant (ScenarioFailureStates.tsx:279) and Number(declaredLengthHeader.trim()) on the Content-Length guard (scenario-api.ts:288). Contract validation precedes render: scenario-api.ts:331 calls validateScenarioDocument inside fetchScenario, and scenario-contract.ts:533 hard-rejects any contract_version other than '1.0.0' (AS-4). Response bounding confirmed against the constants: MAX_DOCUMENT_ARRAY_LENGTH 64, MAX_REFLECTED_TEXT_LENGTH 600, MAX_TOKEN_LENGTH 64, MAX_RESPONSE_BYTES 256 KiB, with arrays rejecting, free text truncating visibly and identifiers rejecting rather than being silently sanitized"
   ]
  },
  {
   "id": "D-038-R004",
   "state": "PASS",
   "evidence": [
    "Fully OFFLINE with none of the deferred owner-only credentials: no Supabase (B-001), no Geoclient (B-004), no live backend. The consumed endpoint is the accepted M5-T003 route behind INTERNAL_SCENARIO_ENABLED, served in tests from committed fixtures and in e2e from a local harness - fixture-based tests and BBL reads against already-accepted public connectors are both explicitly permitted by R004's own text. AS-7 carries this and says so verbatim in the packet: 'AS-1..AS-6 run entirely under vitest with mocked/fixture endpoint responses (committed M5-T003 fixtures) and/or the Playwright e2e against apps/web/e2e/harness/fixture_api.py - NO network, NO Supabase, NO Geoclient'",
    "OFFLINE RE-AUDITED BY THIS VERIFIER at the reviewed SHA rather than taken from the gate reports, because the map's only cited audit was gathered at the superseded SHA 84815a76: across the four test files under components/compare/__tests__/, 49 sites use an injected fetchImpl or a renderCompare/stubFetch helper; every vi.stubGlobal('fetch', ...) passes vi.fn() or a local spy (compare-entry.test.tsx:36,55,70,87 and compare-screen.test.tsx:593); vi.unstubAllGlobals() runs in afterEach in both stubbing files (:29 and :26); and there is NOT ONE bare fetch( call in any of the four. G5's first-round audit (M5-T004-G5.md:45, 'Zero sites reach global fetch') is accurate for the round it covers and agrees",
    "The e2e layer never leaves the loopback: playwright.config.ts pins baseURL http://127.0.0.1:3000 and starts exactly two local servers, 'python e2e/harness/fixture_api.py' on 127.0.0.1:8000 and 'npm run start' on 127.0.0.1:3000. fixture_api.py:265 is literally os.environ[INTERNAL_SCENARIO_ENABLED_ENV_VAR] = '1' - the map's line citation is exact - fixing the gap where the harness set only INTERNAL_RULE_EVAL_ENABLED (:253) and no browser could reach /property/compare anywhere in the repo. compare-journey.spec.ts is the only one of 19 spec files that navigates to that route (:45, :58, :96, :125, :144)",
    "No credential, token, key or URL appears in apps/web/src/components/compare/__tests__/scenario-fixtures.ts or apps/web/e2e/compare-journey.spec.ts - a grep for token|secret|api_key|password|supabase|geoclient|https?:// over both returns nothing. The only network-shaped constant is the build-time apiBaseUrl() default. No configuration or credential surface was added anywhere: the diff is apps/web plus one producer report",
    "NO TEST EXECUTION AND NO GREEN CLAIMED, verified rather than accepted: apps/web/node_modules is absent (no node_modules anywhere within three levels), so none of the three documented commands could run. Four independent disclosures say so unhedged - the producer's own 84815a76 commit message ('Producer did NOT run frontend tests ... and claims NO green'), the first-round DCV method note, the re-review header ('No reviewer ran the suite; no green is claimed. CI is the authority.'), and the evidence map. G4's contribution is correctly labelled static: config reading, cross-module signature checks, and one transcription of validateScenarioDocument into Python run against the four committed fixtures, 4/4. No CI run can exist for this SHA - origin/candidate/D-024-mrl-option-b is at 0c810887 and the whole rework chain is unpushed. Directive-file integrity re-verified at this identity: requirements.json digest f62c6fc8 byte-equal to the manifest, locked_requirement_ids R001..R007 count 7, validate_directive_compliance.py --check EXIT 0"
   ]
  }
 ]
}
```

---

## WHAT I VERIFIED

**Executed (read-only):**
- `git rev-parse HEAD`, `git status --porcelain`, `git rev-parse --abbrev-ref HEAD`
- `git show --stat` on all seven work commits plus `ab7478e1`, `d0d6c12b`, `5983ecb7`, `0c810887`
- `git diff HEAD` (working tree) and `git diff HEAD -- project-control/tasks/M5-T004.json`
- `git remote -v`, `git log --oneline -1 origin/candidate/D-024-mrl-option-b`, `git branch -r --contains 84815a76`
- **`pc._task_git_identity(dr, packet)`** — independent recomputation of the content manifest
- **`reg.evaluate_task_refs(packet)`** — independent derivation of the applicable set
- `hashlib.sha256` over `requirements.json` — digest vs manifest
- **`python tools/validate_directive_compliance.py --check` → EXIT 0**
- Targeted greps: `fetch(`/`stubGlobal`/`unstubAllGlobals` in the compare tests;
  `toFixed|toLocaleString|Math.|parseFloat|parseInt|Number(|Intl.` in components and lib;
  `??` defaults in components; `MAX_*` constants; `property/compare` across all 19 e2e specs;
  `INTERNAL_SCENARIO_ENABLED` across `apps/web/e2e/`; credential patterns in the fixtures and
  the new spec; `real network|network call|no network|offline|AS-7|global fetch` across all
  six M5-T004 reports

**Read:**
- `project-control/directives/D-038-build-product-not-self/{requirements,manifest,verification}.json`
  — all seven requirement texts and applicability blocks, the `authority_note`, the full
  audit log, and M5-T013's row as the shape and note-writing standard
- `project-control/tasks/M5-T004.json` — `allowed_paths`, `forbidden_paths`, all 8 acceptance
  scenarios, `directive_refs`, `required_gates`, `producer_agent`, `reviewer_agents`,
  all three `path_notes` including the `ab7478e1` ratification, `documented_test_commands`,
  `test_evidence_capture_note`, `progress_log`
- `project-control/reports/M5-T004-evidence-map.json` (the artifact under verification)
- `project-control/reports/M5-T004-rereview.md` (all 118 lines)
- `project-control/reports/M5-T004-{G1,G3,G4,G5,DCV}.md` — verdict lines, G4's findings and
  headings in full, G5's AS-7 row, DCV's leaf-classification table and per-AS verdicts
- `project-control/reports/M5-T004.json` (submitted report record)
- `project-control/gates/M5-T004-{G0,G1,G3,G4,G5}.json` including `history[]`
- `tools/project_control.py` (`_task_git_identity`, `_directive_submit_check`,
  `_directive_accept_reasons`) and `tools/directive_registry.py`
  (`task_verification_result`, `_v2_task_unresolved`, `_identity_key`) — to confirm the row
  schema and the independence check before proposing the row
- Source under `apps/web`: `playwright.config.ts`, `e2e/harness/fixture_api.py` (250-275),
  `e2e/compare-journey.spec.ts`, `src/lib/scenario-{api,contract,contract-checks,bounds,display}.ts`,
  and the four `components/compare/__tests__/` files

**Not done:** no test suite was run (impossible — `node_modules` absent), no repository file
was created, edited or deleted, and no mutating git command was issued. The only file
written is this report, in the session scratchpad.
