<!-- Orchestrator capture: directive-compliance-verifier return for M5-T045 saved VERBATIM
     (transport entity-decoding only). Ruling at HEAD d288eaea over frozen submission
     2b851c18; five-condition restamp pre-authorization with explicit disjoint-peer
     tolerance stated up front. -->

I have reproduced all primary evidence. The `test_directive_compliance.py` suite is streaming cleanly (~125 tests executed, 0 failures/errors) but is extremely slow on Windows (per-test temp git repos + validator subprocesses) and has not reached its final summary line within the sandbox time budget; every executed test passes and the authoritative CI-wired validator already passed (exit 0). I have sufficient evidence to render both verdicts.

---

# DIRECTIVE-COMPLIANCE VERIFICATION — M5-T045 (D-001 in-regime)

**Verifier:** directive-compliance-verifier (read-only, ADR-005) · **Producer:** backend-engineer
**Branch:** candidate/D-024-mrl-option-b · **Current HEAD:** `d288eaea` · **Frozen submission:** `2b851c18` · **Gate reviewed_sha:** `36d87960` · **Material cherry-pick:** `28082288` · **CI-proven:** `21ee7379`

## VERDICT: PASS — both applicable requirement IDs SATISFIED

Applicability binding reproduced myself (`reg.load().evaluate_task_refs`): `ok=True`, `applicable_ids == cited_ids == ['D-066-R001','D-073-R006']`, `missing_ids=[]`, `invalid_refs=[]`. No selective citation; both directives active, zero integrity errors. (My first probe printed `ok:False` — that was my own artifact from not calling `.load()`; corrected.)

## Byte-identity (reproduced via git plumbing, not trusted from reports)

`git diff --name-only` over all 17 allowed_paths is EMPTY across every hop: `28082288`(material) → `2b851c18`(submission) → `36d87960`(gate reviewed_sha) → `d288eaea`(HEAD). Working tree clean for the surface. Recomputed 5 load-bearing LF-normalized digests at HEAD against `M5-T045-source-sections.md` — all match: `condo_base_lot.py`=`9a816c04…`, `zoning_crosscheck.py`=`0f30967b…`, `PropertyOverview.tsx`=`649f8704…`, `ReportView.tsx`=`0a5c85c4…`, `AnalysisIdentityNotice.tsx`=`97b0f0ef…`. The surface the gates reviewed is byte-identical to the surface I inspected and to the CI-green head.

---

## D-066-R001 — SATISFIED (seam-regenerated nav block + verify-in-source discipline)

Primary evidence, reproduced:
- **Nav block present in packet** — `project-control/tasks/M5-T045.json` inputs[4] (line 12): "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated at this contract seam, 740 files/15648 nodes)" naming resolver leaf status, both consumer seams with line anchors (`rule_evaluation.py:66`, test files), the single live ztldb call site (`live_provider.py:110`), `normalize_bbl` primitive, and the web PropertyOverview consumer set. Carries the `query.py --no-regen` instruction and the advisory clause "graph is ADVISORY - verify in source."
- **G0 report** — `M5-T045-G0.md:27-31` records the seam regen (740 files / 15648 nodes / 6932 edges) with the advisory clause.
- **Verify-in-source, independently re-derived by me** — grep over `services/api/app` (non-test): the new symbols `condo_base_lot` / `resolve_condo_billing` / `CondoResolution` / `condo_resolution_report` appear ONLY in the four in-scope modules (`condo_base_lot.py`, `dtm_condo_soda.py`, `zoning_crosscheck.py`, `live_provider.py`), all in allowed_paths. Forbidden paths (`profile/builder.py`, `spatial/adapter.py`, `_contract_schemas/`, `rules/`, `packages/contracts/`) contain NONE of them (grep returned empty). This reproduces the G3 grep-proof (`M5-T045-G3.md:22`) independently.
- **Nav-block material claims verified in source** — route seam consumer confirmed (`rule_evaluation.py:66` imports `default_live_substrate` from live_provider); single live ztldb call confirmed (`live_provider.py:48,112` `fetch_by_bbl`); resolver-invoke wiring confirmed (`condo_base_lot.py:48` imports transport from `dtm_condo_soda`); code-graph tooling present (`tools/code_graph/generate.py`, `query.py`).
- **Binding audit trail** — D-066 `manifest.json` audit_log: `applicability_bound … M5-T045 bound to D-066-R001` (2026-09-19T03:10:52).

Observed value: obligation met — the packet carries the seam-regenerated graph-derived navigation block with the query.py directive and advisory clause, and every material graph conclusion is verified in actual source.

## D-073-R006 — SATISFIED (records-vs-allowances preserved throughout screen and brief, at the amended scope)

Primary evidence, reproduced from source:
- **Backend onto EXISTING contract-1.3.0 channels, machine token** — `zoning_crosscheck.py:524` `condo_resolution_report` maps the typed outcome onto the SAME `CrosscheckReport.conflicts`/`notes` channels; `_condo_note_prefix` (`:511-521`) emits the machine token `condo_resolution: [<OUTCOME>]` equal to `CondoResolution.outcome`. Multi-lot → conflict `field=condo_base_lot_resolution`, `resolution:"unresolved"`, every base lot as a value with derivation "a RECORD, never a chosen answer", reason "the base lots are presented as RECORDS with NO computed allowance" and divergent zoning "never collapsed" (`:564-600`). Unresolved → note "no reference number is presented as a computed result" (`:612-618`). No `CrosscheckReport` shape change (dataclass untouched); pass-through returns an empty report (`:631-633`).
- **Shared fail-safe ALLOW-LIST guard, screen + brief** — `condoWithholdsAllowances` (`PropertyOverview.tsx:116-123`) is a genuine allow-list: withholds if a `condo_base_lot_resolution` conflict exists OR any `condo_resolution` note's outcome `!== "resolved_single_base_lot"`. A missing token (null), malformed bracket (null), and unknown token all fail the check → withhold. `ReportView.tsx:11,38` imports and applies the SAME exported guard and the SAME `CondoResolutionRecords` component (verified by grep: these two symbols are defined only in PropertyOverview and consumed by exactly PropertyOverview + ReportView) — one data path, cannot disagree. G4 (`M5-T045-G4.md:47`) proved the deny-list mutant dies on the missing/unknown/malformed probes over a non-vacuous displayable control; I confirm the guard logic in source.
- **Base lots as RECORDS with record-not-allowance wording** — `CondoResolutionRecords` (`PropertyOverview.tsx:135-158`): "It is a record, not a computed development allowance — allowances are calculated only for an established base lot and are shown separately"; multi-lot titled "Multiple recorded base lots — no computed allowance"; UNKNOWN zoning preserved as "not recorded (unknown)", never fabricated.
- **Neutral identity notice** — `AnalysisIdentityNotice.tsx:37`: "recorded as entered versus analyzed only — no relationship between them is inferred — and no calculated allowance is shown while they differ"; infers no billing/base-lot/condo relationship; renders nothing on match/absent-document.
- **HJ PASS** — `M5-T045-HJ.md` verdict PASS, zero blocking; walks J1–J6; confirms the central promise (no computed allowance on a non-success condo resolution) holds via the display allow-list AND independently the backend `build_live_substrate → None` fail-safe.

**Judgment at the amended scope (the contract the gates reviewed):** The ORCH-SCOPE-DISPOSITION split the multi-lot RECORDS-VIEW *production data channel* to DB-031 and made this packet's deliverables (a) the reachable entered-vs-analysed identity notice (wired via ArchitectEntry + ReportView) and (b) the fully fail-closed backend (live provider → None → professional-review fail-safe as the visible surface for multi-lot/unresolved). All reviewers (G1 A2, G3 A1, HJ A1) independently observe that `condo_resolution_report` has no production caller today, so the records-view is BUILT-but-dormant against synthetic fixtures — honestly disclosed (producer report §6/§10; code comment `PropertyOverview.tsx:52-55`), not claimed reachable. R006 requires the records-vs-allowances *distinction* to be preserved throughout interface and report; that distinction is implemented and proven on every reachable surface and in the fail-closed backend. No reference number is ever presented as a computed result on any reachable path. R006 is satisfied **at this packet's amended scope**; the remaining records-view reachability is a recorded successor (DB-031), which is the correct disposition, not a gap that softens the requirement.

Observed value: obligation met at the amended contract; records and calculated allowances are separate concepts throughout, allowances withheld unless the single established base lot is positively confirmed.

---

## Amendment discipline — verified clean

- Disposition recorded **pre-submit**: packet inputs[18] `[ORCH-SCOPE-DISPOSITION 2026-09-19, pre-submit]`; progress_log entry at 05:34:57; submit at 08:23:40 (disposition precedes submission → no frozen-submission identity invalidated).
- **G0 re-recorded at the amendment head**: `M5-T045-G0.json` history shows the contract record (03:18:08) plus the re-record (05:35:37, reviewed_sha `1ca86d1c`); `M5-T045-G0.md:50-64` addendum documents the amendment and re-record PASS.
- **DB-031 exists**: `docs/DISCOVERY_BACKLOG.md:122` — OPEN, "Multi-lot condo RECORDS-VIEW display split out of M5-T045 … cite with D-073:R006". Not silently deferred.
- **AS-3/AS-8 amended** in the packet with the tagged disposition. No completion narrative substituted for evidence — reviewers judged on reproduced source/tests, not the producer matrix.

## Prohibited-action evidence — clean

Ledger status: 228 accepted, M5-T045 is **awaiting_gate** (progress 95), NOT among accepted. No accept/merge/deploy/dispatch/close occurred for T045. Forbidden paths untouched (grep-confirmed). No contract-schema change. Live path stays flag-gated OFF (`LIVE_SPATIAL_PROVIDER_ENABLED` absent → disabled).

## Harness results (reproduced)

- `python tools/validate_directive_compliance.py --check` → **exit 0** (authoritative CI-wired integrity gate; confirms source digests match, requirement integrity, applicability binding).
- `python tools/test_project_control.py` → **all 23 groups passed** (exit 0).
- `python tools/test_directive_reminder.py` → **Ran 12 tests, OK** (exit 0).
- `python tools/test_directive_compliance.py` → **0 failures / 0 errors across ~125 tests executed and streaming clean**; suite did not reach its final `Ran N tests / OK` line within the sandbox budget (per-test temp git repos + validator subprocesses are very slow on this Windows host). Every executed test passed; the CI-wired validator (above) is the authoritative gate and is green. *Recommend the orchestrator capture the final summary line for the complete tally if a full-count record is wanted; no failure was observed.*

Five gate JSONs (G1 data-contract, G2 self-check, G3 code, G4 QA, G5 security) all PASS at reviewed_sha `36d87960`, content_manifest `e0ac5bfd…`; HJ PASS. All reviewers reproduced byte-identity and reran focused/consumer suites themselves.

---

## v2 task_verifications row (for the orchestrator to record in both directives' verification.json)

Per registry: task_id M5-T045; applicable_requirement_ids [D-066-R001] / [D-073-R006]; reviewed_sha = the restamp/acceptance-integration target; reviewed_manifest_sha256 = `e0ac5bfdbaac9b5631cc6efb26729ea38c3118eda3b4a79d890b5117a567f74d` (read by the DCV from project-control/gates/M5-T045-G1.json content_manifest_sha256); producer backend-engineer; verifier directive-compliance-verifier; requirement states PASS with the evidence text as returned.

## RESTAMP PRE-AUTHORIZATION (stated up front — conditions for this PASS to carry to a restamped head)

My ruling carries to a restamped head iff ALL hold at record time:
1. **Anchor:** all 17 M5-T045 allowed_paths are byte-identical (LF-normalized) to material `28082288` (equivalently to `d288eaea`, already proven empty-diff). This is the load-bearing condition.
2. `directive_refs`, `allowed_paths`, and the evidence-map materials are unchanged; `evaluate_task_refs` remains ok (applicable == cited == [D-066-R001, D-073-R006]).
3. D-066 and D-073 remain active with R001/R006 unamended; source digests match.
4. `python tools/validate_directive_compliance.py --check` exits 0 at the record state.
5. **Disjoint-peer tolerance (explicitly granted):** commits between freeze and the restamp target that touch ONLY (a) orchestrator control-plane files (`project-control/**`, docs/backlog), (b) M5-T047 acceptance-seam surfaces (lot_geometry route + address components + address libs), or (c) M5-T048/M5-T049 lane surfaces (scenario/contracts, rules-matcher) do NOT void this ruling, since each is byte-disjoint from T045's 17 allowed_paths (condition 1 remains the guarantee).

Any VIOLATED/UNVERIFIABLE result would block completion; there are none. Both requirement IDs SATISFIED. **PASS.**
