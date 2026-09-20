# M5-T059 producer report — D-078 pair 2/2: multi-lot condo site-definition confirmation, slice 1

Task: **M5-T059** (backend). D-078 pair 2/2. Record substrate + unmounted flag-gated internal API
+ read-only condo-records surfacing + DB-038(f) riders. **NO calculation-path change.**

Base (claim-seam head): `f86ae7353c8b2ff99220c51766aad23d595cc66f` on `task/M5-T059-site-definition`.
Producer edits are uncommitted working-tree changes on top of that base (the orchestrator integrates;
the producer never commits — ADR-005).

Content-identity note (honesty about digest binding): under the producer native-tool command allowlist
only the packet's documented test commands and enumerated read-only git verbs run; `sha256sum` /
`git hash-object` / `Get-FileHash` are refused by the broker, so this report binds every reviewable
claim to an **exact file + line anchor** at the working-tree state and hands the executable identity
to the supervisor: **bounded per-file / segmented diffs** and a **full-file sha256 per changed file**
are collected by the orchestrator/supervisor at the frozen submission head (§9). No long source
section is embedded in this report, and **no digest is invented here** — the digest column is left for
the orchestrator to bind (the established "digest-bound by orchestrator" pattern). The three offline
validation commands are documented by exact argv + explicit cwd for supervisor reproduction (§10); web
CI and the gates stay PENDING until the orchestrator-collected results exist (§11).

---

## 1. What this unit did (delta on top of the claimed working tree)

The claim-seam working tree already carried the backend record + store + unmounted API + condo-records
surfacing + web parser + the backend/lib test packs (see `git diff --stat` below). This unit closed the
two remaining gaps and the validation pass:

1. **Fixed `services/api/tests/api/test_site_definition_api.py:62` E501** (line-length 100). The
   `_multi_lot` fixture signature was 107 chars on one line; it is now wrapped across three lines
   (`test_site_definition_api.py:62-65`). `ruff check .` from `services/api` is now clean.
2. **Completed the component (screen/brief) tests** for the site-definition surfacing and the
   DB-038(f)-1 billing-lot collapse in
   `apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx`:
   - The existing billing-class label test now asserts the **DB-038(f)-1 collapse**: for a
     billing-class input where the entered BBL IS the recorded billing lot, the two identical lines
     collapse into ONE (`condo-entered-lot` carries the billing-class parenthetical) and the separate
     `condo-billing-lot` element is **gone** (`condo-resolution-display.test.tsx` "(f)-1 … COLLAPSES …").
     The unit-input case above it (billing status `unknown`) still keeps the two lines distinct — the
     honest non-redundant case.
   - A new describe block `CondoSiteDefinitionRecord — recorded site-definition surfacing (M5-T059,
     D-078)` renders `CondoRecordsChannelSection` with a multi-lot doc carrying a `site_definition`
     block and proves: active-confirmation rendering **with a fractional-second timestamp**; the loud
     **self-attested refusal** note (including the fail-safe case where the payload claims
     `refused_for_calculation: false`); **absent vs revoked/superseded history** (the `data-history`
     attribute + honest copy); a **malformed / non-active** confirmation failing safe to unconfirmed;
     the **surfaced parcel discrepancy** (never a status change); and the **calculation/refusal
     regression** — a confirmed site definition still shows `Not calculated` for FAR and the cap
     (records never unlock allowances).

Nothing else in the working tree was changed by this unit. `main.py` remains byte-unchanged (the
route stays unmounted — §5).

## 2. Module boundaries (modularity policy)

- **New package `services/api/app/site_definition/`** owns the record substrate with three focused
  modules, each a single responsibility:
  - `records.py` — the typed immutable value types + pure builders + the read-only block assembler
    (`SiteDefinitionConfirmation`, `StatusTransition`, `ConfirmationView`,
    `ResolutionProvenanceSnapshot`, `create_confirmation`, `build_site_definition_block`,
    `normalize_parcels`, `make_confirmer`, the typed error hierarchy). Pure — it touches no store.
  - `store.py` — the append-only lifecycle: `SiteDefinitionStore` ABC + `InMemorySiteDefinitionStore`
    + the single process-wide `default_site_definition_store()` binding. Depends on `records.py` only.
  - `__init__.py` — the package facade re-exporting the public surface both API modules import.
- **`api/v1/site_definition.py`** — HTTP wiring only (the unmounted write API): flag gate, body
  ceiling, typed-refusal serialization, injected resolver + store. It imports the domain from the
  package; it owns no record logic.
- **`api/v1/condo_records.py`** — grew by an **import + one small additive block** only
  (`condo_records.py:100-104` import; `:222-238` the store dependency; `:667-676` the additive
  `site_definition` block on the multi-lot document). The assembly lives in the package, so the file
  stays under its tier (modularity `failures 0`, and `condo_records.py` is **not** in the warning list).
- **Web:** `lib/condo-records.ts` owns the read-only parser (`siteDefinitionView`,
  `activeConfirmationView`, `siteDefinitionConfirmationView`, `boundedParcels`); `PropertyOverview.tsx`
  owns the presentation (`CondoSiteDefinitionRecord` renders inside the multi-lot records section).
  `bbl.ts` / `bounded.ts` / `LotOutlineMap.tsx` are byte-untouched (forbidden paths honored).

## 3. Ephemeral storage (B-001 deferral, stated plainly in code)

`InMemorySiteDefinitionStore` is a plain in-process dictionary + append-only transition list: **no
database, no persistence, no concurrency safety; its confirmations DO NOT survive a process restart**
(`store.py:1-18, 84-88`). Production binds to the `SiteDefinitionStore` ABC; the durable
implementation is deferred under B-001 on the `documents/storage.py` precedent. The single shared
`default_site_definition_store()` (`store.py:235-257`) is what makes write-then-read coherent across
the (unmounted) write API and the condo-records read document — one store, one truth — but because the
write route is unmounted it is never reachable in production, so the read document honestly shows
`unconfirmed`. Implying durability would be a false-provenance defect and is avoided in both code and
this report.

## 4. Self-attestation limits (loud and typed)

Identity authentication is B-001-blocked, so the attestation vocabulary has exactly ONE member,
`unauthenticated_self_attested` (`records.py:119-136`), it is **server-set and never read from a
caller payload** (`records.py:481-494`, `api/v1/site_definition.py` `create_confirmation` call), and
`SiteDefinitionConfirmation.refused_for_calculation` is a derived property that is `True` for that
status (`records.py:280-285`). Slice 1 has **no calculation path at all**, so this is a loud label,
not a live gate — proven by the prohibition tests (§6). The web parser makes the refusal **fail-safe**:
a self-attested confirmation is forced `refusedForCalculation = true` regardless of what an untrusted
body claims (`condo-records.ts:429-455`), and the screen renders the loud refusal note
(`PropertyOverview.tsx:238`).

## 5. Unmounted-router disposition (the safe state, recorded)

The write API (`api/v1/site_definition.py`) is **deliberately NOT mounted in `main.py`**
(module docstring `:10-18`). Production-unreachable is the SAFE state for a write-shaped endpoint whose
store is ephemeral (B-001) and whose identity is self-attested (B-001): a confirmation cannot yet be
durably or authentically recorded, so it must not be reachable in production. The one-line mount lands
in a later packet, and `main.py` is a forbidden path here (also held by the live M5-T057 lane — wiring
it would be a scope breach + lane collision). Because the route is unmounted, its discipline is proven
by a **locally-built `FastAPI()` app** in `tests/api/test_site_definition_api.py` (the first
local-FastAPI-test precedent in this suite; `app.dependency_overrides` works identically on a locally
built app) — flag-off generic 404, malformed BBL 422, over-ceiling 413, non-multi-lot 422, the full
append-only lifecycle, and the shared-store integration proving a write surfaces on the condo-records
read document. `test_router_is_not_mounted_in_main_app` asserts `app.main` exposes no
`site-definition-confirmations` path.

**Bounded unmounted-router evidence (two facts, no full-file embed):**
1. **Source negative** — `services/api/app/main.py` contains **zero** `site_definition` /
   `site-definition` references: the router is never imported, and never `include_router`-mounted
   (confirmed by search over the whole file; the file is a forbidden path and is byte-unchanged —
   not in `git status`).
2. **Test assertion** — `services/api/tests/api/test_site_definition_api.py:319-321`
   (`test_router_is_not_mounted_in_main_app`) imports the **real** application
   (`from app.main import app as main_app`, `:53`) and asserts no `route.path` on `main_app.routes`
   contains `site-definition-confirmations`. The route's URL builder (`_url`, `:126-127`) targets
   `/api/v1/properties/{bbl}/site-definition-confirmations`, so the assertion is over the exact
   production path that would exist IF the router were mounted.

`main.py` is a forbidden path here (also held by the live M5-T057 lane); the one-line mount is a
deliberate slice-2 item. Production-unreachable is the recorded SAFE disposition.

## 6. Prohibitions as tests (D-078-R002 — the hard boundary)

- **No calculation-path change / no auto-selection.** `build_site_definition_block` only SURFACES a
  recorded human confirmation; it never selects a site and never changes a status
  (`records.py:497-552`). The multi-lot document is byte-identical with and without a confirmation
  except for the additive block (`test_condo_records_api.py::test_prohibition_surfacing_is_additive_only`).
  On the web, a confirmed site definition still yields `Not calculated`
  (`condo-resolution-display.test.tsx` "regression: … NEVER unlocks the withheld allowances").
- **Status changes only by a human act.** A later differing resolver set is a **surfaced discrepancy**,
  never a status change (`records.py:535-551`;
  `test_site_definition_records.py::test_a_later_differing_resolver_set_is_a_surfaced_discrepancy_not_a_status_change`;
  web `condo-site-definition-discrepancy`).
- **Append-only, never edited in place.** A created record is immutable (frozen dataclass); supersede =
  new record + appended transition; the frozen original is untouched
  (`test_site_definition_records.py::test_supersede_chains_a_new_active_and_leaves_the_frozen_original_untouched`,
  `::test_the_record_is_immutable_a_mutation_attempt_raises`).
- **Strict parcel binding.** Confirmed parcels must equal the resolver's `base_bbls` exactly; subset /
  superset / divergent = typed `ParcelSetMismatchError`; order alone never refuses
  (`records.py:463-466`; `test_site_definition_records.py` AS-2 pack; API
  `test_divergent_parcel_set_is_typed_422`).
- **Refused-for-calculation label rides the self-attested status** (§4).

## 7. DB-038(f) riders

- **(f)-1 (HJ A4):** entered==recorded-billing collapses to one billing-class line
  (`PropertyOverview.tsx:302-314`); bound by the updated component test (§1) and unaffected for the
  unit-input non-redundant case.
- **(f)-2 (G3-1):** `substitutionRecord`'s entered fallback uses the strict `enteredBblValue`
  (validateBblInput-backed) parser instead of the looser `boundedBbl`
  (`condo-records.ts:352-365`); bound by
  `condo-records.test.ts::"a non-canonical substitution entered_bbl is an explicit null …"`.
- `apps/web/src/lib/bbl.ts` and `bounded.ts` are **byte-untouched** (verified: not in `git status`).

## 8. Digest-bound reference map (line anchors, no embedded verbatim)

Per REPORT DISCIPLINE this section references files + line anchors only; reviewers read the behavior
in source at the frozen head against the bounded per-file diffs and full-file digests the orchestrator
binds there (§9). No long verbatim block is embedded, so the handoff fits the packet budget.

| Behavior (the reviewable claim) | File : line anchor |
|---|---|
| Strict parcel binding — submitted set must equal resolver `base_bbls`; mismatch = `ParcelSetMismatchError` | `services/api/app/site_definition/records.py:463-466` |
| Server-set attestation — `UNAUTHENTICATED_SELF_ATTESTED` never read from a caller payload | `records.py:481-494` |
| `refused_for_calculation` derived property (rides the self-attested status) | `records.py:280-285` |
| Read-only block assembly — surfaces, never selects; later differing resolver set = surfaced `parcel_discrepancy`, never a status change | `records.py:514-552` |
| One-active-per-`condo_key` invariant (`DuplicateActiveConfirmationError`) + append-only supersede (new record + chain links + appended `SUPERSEDED` transition; frozen original never mutated); status derived from the transition log | `store.py:148-212` (`_current_status` `store.py:95-100`) |
| Unmounted write route create — flag gate → `_normalize_bbl_or_422` → body ceiling → `_resolve_multi_lot` (422 if not multi-lot) → `create_confirmation` (attestation server-set) → `store.create` → 201 | `services/api/app/api/v1/site_definition.py:349-395` |
| Typed-refusal uniform serialization (`_refuse`; fail-closed to 422 for an unmapped `SiteDefinitionError`, never a 500) | `site_definition.py:213-230` |
| Additive condo-records surfacing — multi-lot document gains `site_definition` via `build_site_definition_block` (assembly lives in the package) | `services/api/app/api/v1/condo_records.py:667-676` |
| Web parser hardening — self-attested refusal forced `refusedForCalculation = true`; a non-active/record-id-null confirmation never renders active | `apps/web/src/lib/condo-records.ts:436-473` |
| Screen render — `CondoSiteDefinitionRecord`: confirmed group (`condo-site-definition` + `-status`/`-confirmer`/`-refused`/`-discrepancy`) or unconfirmed line (`condo-site-definition-unconfirmed`, `data-history` = `none` \| `revoked-or-superseded`) | `apps/web/src/components/architect/PropertyOverview.tsx:226-247` |

## 9. Bounded diff handoff (supervisor-collected) + full-file digest binding

No long source is embedded here. The executable identity is handed to the supervisor as TWO
artifacts, both collected at the frozen submission head:

**(a) Bounded per-file / segmented diffs.** The supervisor collects a SEPARATE bounded diff per
file (or per cluster), so no single blob dominates the handoff. Requested grouping — the reviewable
clusters named in the handoff request:

| Cluster | Files (one bounded diff each) |
|---|---|
| Backend record substrate | `services/api/app/site_definition/records.py` · `store.py` · `__init__.py` |
| Backend unmounted API | `services/api/app/api/v1/site_definition.py` |
| Condo-records assembly + web parser | `services/api/app/api/v1/condo_records.py` · `apps/web/src/lib/condo-records.ts` |
| Prohibition + route + records tests | `services/api/tests/site_definition/test_site_definition_records.py` · `tests/api/test_site_definition_api.py` · `tests/api/test_condo_records_api.py` · `apps/web/src/lib/__tests__/condo-records.test.ts` · `apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx` |
| Presentation | `apps/web/src/components/architect/PropertyOverview.tsx` |
| Producer report | `project-control/reports/M5-T059-producer-report.md` |

**(b) Full-file digest binding.** For EACH changed file the orchestrator binds a full-file sha256 at
the frozen head. The producer cannot compute a digest (broker refuses `sha256sum` / `git hash-object`
/ `Get-FileHash`), so the digest column is left for the orchestrator — nothing is invented here:

| # | Changed file (allowed_path) | full-file sha256 (orchestrator-bound at frozen head) |
|---|---|---|
| 1 | `services/api/app/site_definition/records.py` | `cddcb3b819f7a758ba91fa2ad17f891564e242b82925f9e5a56cce24cd7e8fd5` |
| 2 | `services/api/app/site_definition/store.py` | `b24e3c5f3075eacdabbbbc6fc8c1bc88a9ab5dcddc579886841a1c539fd1e5e8` |
| 3 | `services/api/app/site_definition/__init__.py` | `4af8d97c2c6baf67112e0c19075f0ac4f139abf26151133a1b4e6435dc833b63` |
| 4 | `services/api/app/api/v1/site_definition.py` | `bdb4f90487486feded57d96a2b05a4a0af58cc3b1ec573e68dab11a7dbb5472a` |
| 5 | `services/api/app/api/v1/condo_records.py` | `6b06fa4d5eb8ad79a95a81cca0ca341b7868783625407ff5b8a3ce3f93028025` |
| 6 | `apps/web/src/lib/condo-records.ts` | `c27d7559245579b2e18aeec5566f313c7ed090733e539639fb01172066c906ab` |
| 7 | `services/api/tests/site_definition/test_site_definition_records.py` | `181c45a58f1ecda342da78766fefe92e719438c467942113617564391c5bfea2` |
| 8 | `services/api/tests/api/test_site_definition_api.py` | `a1e3890b4a7b805a8fb75ec6c51a65622c277fb44caf11f5199948c931e4ce35` |
| 9 | `services/api/tests/api/test_condo_records_api.py` | `128ff45819e2aec57a410976c44feccf1b2ed4148c14c83332a1f4b647081da1` |
| 10 | `apps/web/src/lib/__tests__/condo-records.test.ts` | `0cce838c1b3d4140485f5d4f8f83339cf819ec9fc1cb297e8dd9a8e4fdec9377` |
| 11 | `apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx` | `e2c8b6de9ac1630f59134a978ad064012348a843ab5271eebdedf13acb40faaa` |
| 12 | `apps/web/src/components/architect/PropertyOverview.tsx` | `8028be9d36ec9f27957421b155c089179b72f11c4fc314595ad1d40d0c707baf` |
| 13 | `project-control/reports/M5-T059-producer-report.md` | bound content-addressably by the harvest commit (a report digest cannot self-embed - M5-T013 precedent) |

(`services/api/tests/site_definition/__init__.py` is the committed package seed — present, clean, and
byte-stable, so it carries no diff and is not in the change set; the suite collects the package.)

**Producer-observed change magnitudes** (from `git diff --stat`, bounded — no source embedded; the
authoritative per-file diffs are the supervisor's collection above):

```
 apps/web/.../PropertyOverview.tsx                         |  49 ++
 apps/web/.../__tests__/condo-resolution-display.test.tsx  | 175 ++++++-
 apps/web/src/lib/__tests__/condo-records.test.ts          | 204 ++++++++
 apps/web/src/lib/condo-records.ts                         | 169 ++++++-
 services/api/app/api/v1/condo_records.py                  |  37 ++
 services/api/app/api/v1/site_definition.py                | 534 +++++++++++++-
 services/api/app/site_definition/__init__.py              |  69 ++-
 services/api/app/site_definition/records.py               | 553 ++++++++++++++-
 services/api/app/site_definition/store.py                 | 257 +++++++++-
 services/api/tests/api/test_condo_records_api.py          | 105 ++++
 services/api/tests/api/test_site_definition_api.py        | 377 +++++++++++-
 services/api/tests/site_definition/test_..._records.py    | 334 ++++++++++-
 12 files changed, 2847 insertions(+), 16 deletions(-)
```
(This report is the 13th changed file; it is not self-counted in the `--stat` above.)

## 10. Supervisor transcripts (argv + explicit cwd) — orchestrator-collected

The offline proof is THREE documented commands. Each is recorded here by exact argv AND explicit cwd
so the supervisor/orchestrator reproduces it and stores the authoritative transcript at the frozen
head. The producer-observed outcome is the expected result for that reproduction — it is a self-check,
**not** a substitute for the supervisor-collected transcript, which stays PENDING (§11):

| # | argv | cwd (explicit) | producer-observed | authoritative transcript |
|---|------|----------------|-------------------|--------------------------|
| T1 | `python -m ruff check .` | `…\wt-m5t059\services\api` (the api CI job's cwd) | exit 0 · `All checks passed!` | supervisor-collected — **PENDING** |
| T2 | `python -m pytest tests/site_definition tests/api -q` | `…\wt-m5t059\services\api` | exit 0 · `578 passed` (`in 25.35s`; timing varies) | supervisor-collected — **PENDING** |
| T3 | `python tools/modularity_check.py --check` | `…\wt-m5t059` (repository root) | exit 0 · `selected 460 files; failures 0; warnings 20` | supervisor-collected — **PENDING** |

**Retained failed run (a SEPARATE outcome — deliberately NOT repaired):**

| # | argv | cwd (explicit) | producer-observed | disposition |
|---|------|----------------|-------------------|-------------|
| R1 | `python -m ruff check .` | `…\wt-m5t059` (repository ROOT) | exit 1 · `Found 45 errors.` — ALL in `project-control/reports/**` + `tools/**` | **retained as a distinct outcome; root/tools lint is pre-existing, outside this task's `allowed_paths`, and is NOT repaired** per the handoff request |

Notes:
- **T1 and R1 are the SAME documented argv at two different cwds** — the ONLY difference is cwd. T1
  (the api CI job's actual cwd) is clean; R1 (repo root) surfaces the pre-existing `reports/**`+`tools/**`
  lint that is out of scope. Both are kept as separate outcomes; neither is collapsed into the other,
  and R1 is not "fixed" to make the root run green. The in-scope E501 at `test_site_definition_api.py:62`
  is fixed (§1).
- **T2:** 578 passed — no failures, errors, or skips reported by `-q`; matches the recorded suite.
- **T3:** `failures 0`; the 20 warnings are pre-existing signals on OTHER modules. Neither the new
  `services/api/app/site_definition/**` package nor `condo_records.py` is in the warning list —
  `condo_records.py` stays under its tier (assembly extracted to the package).
- These are offline PRODUCER self-checks under the thin-client policy. The AUTHORITATIVE transcripts
  (by argv + cwd, above) and the full-file digests (§9) are collected by the orchestrator/supervisor at
  the frozen head; CI + gates remain the authoritative proof and are collected there (§11).


## 10.1 [ORCH-CAPTURED] Authoritative transcripts + digest binding (2026-09-20, seq 122)

Orchestrator reproduction at the harvested working tree (loop-3 run persistent3-local-06-m5t059;
unit complete at the consecutive_revision_loops breaker stop; zero unanswered asks). Raw
transcript retained in the session capture file. Explicit cwd per line:

- T1 cwd `wt-m5t059/services/api`: `python -m ruff check .` -> "All checks passed!", exit 0
- T2 cwd `wt-m5t059/services/api`: `python -m pytest tests/site_definition tests/api -q` ->
  **578 passed** in 34.33s, exit 0
- T3 cwd `wt-m5t059` (repo root): `python tools/modularity_check.py --check` -> exit 0
  (pre-existing `tools/*` warns only; neither the site_definition package nor condo_records.py flagged)
- REGRESSION (beyond the three documented commands) cwd `wt-m5t059/services/api`:
  `python -m pytest tests/rules -q` -> **726 passed**, exit 0

The SS9(b) digest column above is orchestrator-bound (LF-normalized sha256, CRLF->LF before
hashing) over this same snapshot; the material commit's digests match the table
content-addressably and the cherry-pick sha onto candidate is named in the evidence map at
submit. Web CI at the pushed head remains the PENDING web proof (SS11 unchanged).

## 11. Web CI + gates — PENDING (held for orchestrator-collected results)

Per thin-client policy and CODING_RULES, the web (vitest) suites are **not** run locally and are **not**
claimed verified from local reasoning. Web behavior — the DB-038(f)-1 collapse, the site-definition
rendering pack, and the lib parser pack — proves ONLY in CI on the orchestrator-pushed head.

- **Web CI status: PENDING** — proves only in CI at the orchestrator-pushed head; not asserted here.
- **Gates (G0, G2, G3, G4, G5) status: PENDING** — the required-gate set is recorded by the
  orchestrator; the reviewer wave (`code-reviewer`, `qa-engineer`, `security-reviewer`,
  `human-journey-reviewer`, `directive-compliance-verifier`) runs against the frozen submission head
  after the orchestrator collects the bounded diffs (§9), the full-file digests (§9), and the three
  supervisor transcripts (§10). Nothing in this report records or self-certifies a gate.

This unit does not commit, push, merge, accept, or change project-control state; it prepares the
revised evidence handoff and leaves resubmission for substantive review to the orchestrator.

## 12. Out-of-scope / discovery (D-069)

None new this unit. The site-definition **mount line in `main.py`** and the **mutation client + confirm
button + multi-parcel map** are the deliberately-deferred slice-2 items (recorded here, not fixed
in-packet); calculations-on-confirmed-combined-land is a later slice after this substrate and the
M5-T058 substitution stamp both land.

## 13. Directive compliance (task `directive_refs`)

- **D-078-R001/R002/R003** — substrate + read-only surfacing + honest limits, with D-078-R002 (system
  never auto-selects / never changes a status by an automated act) enforced as prohibition tests on both
  the api and web sides (§6).
- **D-077-R002/R003** — pairwise-disjoint lane; no `main.py` change; no forbidden-path edits.
- **D-066-R001** — code-graph consumed read-only for the seam map; verified in source.

## 14. Preservation checklist

`main.py`, `app/connectors/**`, `app/documents/**`, `app/spatial/**`, `app/rules/**`, `app/profile/**`,
`app/scenario/**`, the forbidden `api/v1/*` siblings, `packages/contracts/**`,
`apps/web/src/lib/{bbl,bounded,rule-evaluation-contract}.ts`, `LotOutlineMap.tsx`,
`AnalysisIdentityNotice.tsx` — all untouched (confirmed against `git status`). No new dependency, no new
flag (reuses `INTERNAL_RULE_EVAL_ENABLED`). Unmounted route preserved; calculation boundaries preserved.
Not committed / pushed / merged / accepted — left for orchestrator integration.

## 12.1 [ORCH-CORRECTED] Rework identity + capture (wave findings G3-C1/G5-F1, G4-C-1, G4-C-2; 2026-09-20, seq 122)

The independent wave at frozen f58f4d89 ruled G3 PASS w/ blocking C1, G4 PASS w/ blocking C-1 +
C-2, G5 PASS (F1 = the same revoke defect, ruled a mount precondition), HJ PASS, DCV PASS (F-1
evidence-map count corrected outside the material identity; the R003 accept-time condition -
M5-T058 accepts first - stands). The blocking findings were repaired as ONE tagged cluster
([ORCH-CORRECTED per ...] comments in code):

- G3-C1/G5-F1: `revoke` is now BOUND to the addressed property's condo - the route re-reads the
  resolver for the path BBL (mirroring supersede) and `SiteDefinitionStore.revoke` takes a
  REQUIRED `condo_key` the in-memory impl enforces (typed not-found on a cross-condo attempt);
  bound by the record-layer test and the end-to-end cross-condo API regression (404 `not_found`,
  record stays active, bound revoke still succeeds).
- G4-C-1: `list_for_condo_key` now carries a monotone insertion-sequence secondary sort key, so
  the ABC's newest-first contract is TRUE on a same-instant `confirmed_at` tie (the prior
  comment's reverse-insertion claim was false under a stable sort and is corrected); bound by a
  same-instant supersession-chain ordering test.
- G4-C-2: `store.create` refuses a `supersedes_id`-carrying record with the new typed
  `OrphanSupersedeError` (reject_code `supersede_via_create_refused`; exported via the facade) -
  supersession is the only path that appends the replaced record's status flip; bound by a test.

Changed files (6; the other 8 packet paths byte-unchanged from SS9): corrected LF-sha256:

| Artifact | LF-sha256 |
|---|---|
| `services/api/app/site_definition/records.py` | `1b27ba9aac485eb6f2cb2b178e2e3889ab91cc622c451f48f041d3aea17a57e3` |
| `services/api/app/site_definition/store.py` | `55373905c6cfbee41f1df2fd77dd61fb6f862b28aec9a320d2cf644970e829ff` |
| `services/api/app/site_definition/__init__.py` | `5d1cb028563f47fdc89c7f4d7671c4ce2c0ba2fbc1d5eb84b87ff88203c32614` |
| `services/api/app/api/v1/site_definition.py` | `06fced165e84f4896dcfc29b02886bb6cc6e262ac2d1fe7f0b02407a0c3dba59` |
| `services/api/tests/site_definition/test_site_definition_records.py` | `212281fb4d185e2b9096742adda9f2521317ae4e31aca99891e1fc3660e24bf0` |
| `services/api/tests/api/test_site_definition_api.py` | `d58690cbe9d47030c5e3980796c48fd259d4ee147df4b5a1c76d5d175940622a` |

Orchestrator re-capture at this snapshot (explicit cwd): `python -m ruff check .` clean exit 0;
`python -m pytest tests/site_definition tests/api -q` -> **582 passed** (578 + 4 rework
bindings); `python -m pytest tests/rules -q` -> **726 passed**; `python
tools/modularity_check.py --check` exit 0 (pre-existing tools/* warns only). Advisory findings
NOT taken in-packet (G3 F-2..F-8, G4 A-1..A-8, G5 F2..F7, HJ-1..11) route to the discovery
backlog / slice 2. CI at the pushed rework head is the remaining PENDING proof.
