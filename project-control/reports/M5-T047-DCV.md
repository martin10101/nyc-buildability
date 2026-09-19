<!-- Orchestrator capture: directive-compliance-verifier return for M5-T047 saved VERBATIM
     (transport entity-decoding only). Ruling over frozen content identity ca94b2c3 at
     HEAD 7c935d25; four-condition restamp pre-authorization with explicit disjoint-peer
     tolerance stated up front. -->

I now have all primary evidence reproduced. Frozen submission record confirms reviewed_sha `ca94b2c3`, content_manifest `9c6050a5…` (identical to every gate record), applicable_requirements `[D-066-R001, D-073-R006]` (== packet citations); T047 is `awaiting_gate` (no acceptance commit, no blocker references it). Here is my verdict.

---

# Directive-Compliance Verification — M5-T047 (D-001, read-only)

**Verifier:** directive-compliance-verifier (producer ≠ verifier; producer = backend-engineer)
**Task:** M5-T047 "Record-address display channel (DB-032)" — status `awaiting_gate`, progress 95
**Branch:** candidate/D-024-mrl-option-b — HEAD `7c935d25`
**Reviewed content identity:** frozen submission `ca94b2c3` (reports/M5-T047.json `reviewed_sha`); gates G1–G5 recorded at live head `7bd3dd0a`; both carry the same path-scoped manifest `9c6050a5…`.

## VERDICT: PASS

Both bound requirements SATISFIED on reproduced primary evidence; amendment/correction discipline SATISFIED. Any VIOLATED/UNVERIFIABLE would block completion — none found for the two bindings. One general harness (`test_directive_compliance.py`) is UNVERIFIABLE-in-sandbox for a benign environment reason (see Harness), not a defect and not M5-T047-specific.

### Identity reproduced myself (git plumbing)
- Material producer commit `7ecdcbf4` touched exactly the 9 built allowed-paths (10th, `AddressResolutionScreen.tsx`, deliberately UNCHANGED). `git show --stat`.
- Correction `d27a6a83` touched exactly ONE file, `apps/web/src/components/address/__tests__/address-resolution.test.tsx` (a consumer test NOT in the 10 allowed_paths).
- **Surface byte-identity** (10 allowed_paths + the corrected consumer test): `git diff --stat` is EMPTY for `d27a6a83..7bd3dd0a`, `7bd3dd0a..7c935d25`, `d27a6a83..7c935d25`, and `ca94b2c3..7c935d25`. The CI-green corrected head **is** the frozen material and the current-HEAD material.
- Intervening non-control-plane changes `d27a6a83..7c935d25` are exclusively M5-T045 (architect/, condo connectors, spatial/live_provider, profile/zoning_crosscheck) and M5-T049 (rules named_street_override matcher) — **zero** overlap with T047's 10 allowed paths. Disjoint-peer claim confirmed.

---

### D-066-R001 — SATISFIED (code-graph loop wiring)
Applicability: `requirements.json` task_ids include M5-T047 (line 32); packet cites D-066-R001; applicable == cited.

Primary evidence reproduced:
1. **Nav block embedded** — `tasks/M5-T047.json` inputs[3] ("CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated at this contract seam, 743 files/15656 nodes)"): carries lot_geometry.py consumers, the LotOutlineMap consumer set **including the load-bearing PropertyOverview→LotOutlineMap edge**, AddressConfirmCard consumers, the read-only pluto path, the `query.py --no-regen impact` instruction, and the "graph is ADVISORY — verify in source" clause. Corroborated in `M5-T047-G0.md:26-28`.
2. **Load-bearing edge verified in source (not from the claim):** `apps/web/src/components/architect/PropertyOverview.tsx:10` — `import { LotOutlineMap } from "@/components/address/LotOutlineMap";` — this is the edge that drove the LotOutlineMap + architect/ prohibition protecting the live M5-T045 lane. Other pointers re-verified: `app/main.py:33` (lot_geometry router mount), `tests/api/test_lot_geometry_api.py:35` (imports from lot_geometry), `AddressResolutionScreen.tsx:19` (imports AddressConfirmCard), `AddressConfirmCard.tsx:17` (imports LotOutlineMap).
3. **Consumer sweep OUTCOME:** the one affected consumer `address-resolution.test.tsx` (outside allowed_paths) was caught by CI (3/1064 at `7ecdcbf4`, per `M5-T047-ci-evidence.md`) and corrected at `d27a6a83` with a one-line side-stub extension (`|| url.includes("/record-address")`) following the file's own M5-T023 precedent. `M5-T047-G3.md` Surface 5 independently rules it precedent-consistent, hiding no defect, sweep complete — "D-066-R001 … Honored in code."
4. Graph tooling present (`tools/code_graph/generate.py`, `query.py`); advisory-verified-in-source honored (producer report §0 = git-status 9 files; G3; HJ).

Caveat (non-blocking): the exact regen counts 743/15656 are an orchestrator process assertion I cannot recompute without mutating the graph cache; the requirement's *material conclusions* (the consumer/impact edges, esp. the load-bearing one) are all verified in source, which is the binding standard ("every material conclusion is verified in actual source").

### D-073-R006 — SATISFIED (records vs computed allowances)
Applicability: `requirements.json` task_ids include M5-T047 (line 185); packet cites D-073-R006; applicable == cited.

Primary evidence reproduced:
1. **Route returns a RECORD with provenance + honest absence** — `services/api/app/api/v1/lot_geometry.py`: `_record_source` (L351-360) → source_id, dataset_id, `dataset_version` (PLUTO version), retrieved_at, request_url; three honest typed outcomes `address_of_record` / `no_address_of_record` / `no_record`, each `address=null` on absence (L432-464); SODA key-absence → `no_address_of_record` (L443-455); connector fault → typed error, never fake absence (L400-421); BBL validated before any network (L378-396); comment L278-283 "no value is derived from it … never a fabricated or empty-string line."
2. **Client library RECORD-NOT-MEASUREMENT** — `apps/web/src/lib/record-address.ts:23-27`: "RECORD, NOT MEASUREMENT: this module transports an official RECORD … derives no value; the confirm card shows the record only when it differs from the city-matched frontage … honestly nothing otherwise (D-073-R006)."
3. **Card record line** — `AddressConfirmCard.tsx:198-204`: "City record address: **{recordAddress}**. This is the address the city's official tax record (PLUTO) carries for this lot; it can differ from the matched frontage." Rendered only under `showRecordAddress` (differs from matched). HJ A2 layout-neutral copy L191-195; HJ A3a display-trim L188-189 (`title`/`aria-label` carry raw `enteredInput`; text shows `.trim()`).
4. **No computed value implied / honest absence** — `M5-T047-HJ.md` PASS: "none of the three implies a computed value — they are all records (D-073-R006)"; it closes its own T046 A1/A2/A3a findings.
5. **Amended-scenario integrity** — NO amendment occurred on T047: packet `acceptance_scenarios` AS-1..AS-8 are clean (no `[ORCH-…]` tags, no "amended" markers). The only tagged packet-fix in the wave (ORCH-PACKET-FIX glob fix) is on the **disjoint M5-T048** packet (commit `2b851c18`), not T047 — contrast M5-T045/M5-T046 which amended their own scenarios.

### Amendment / correction discipline — SATISFIED
Single `[ORCH-CORRECTED per M5-T047]` commit `d27a6a83`: test-only (one consumer test, +8/-2), **outside allowed_paths**, tagged, documented in `M5-T047-ci-evidence.md` and adjudicated in `M5-T047-G3.md` Surface 5, precedent-consistent (M5-T023 side-stub). No production or in-scope change. No completion narrative substituted for evidence — every requirement is backed by reproduced source/test/git evidence, not by the producer matrix.

### Registry integrity (intake side)
`validate_directive_compliance.py --check` → **exit 0** (CI-wired fail-closed check; enforces source `content_digest_sha256`, `locked_requirement_ids`, requirements digest, matrix/citation c-checks). D-066 and D-073 both have `amendments: []`, so "every amendment reflected in the matrix" is vacuously met. No missing/weakened/combined/invented requirement found for the two bound rows.

### Prohibited-action evidence
T047 is `awaiting_gate` — no acceptance commit, nothing merged/deployed; correction lives on the candidate branch only; no open blocker references M5-T047. Clean.

### Harness
- `validate_directive_compliance.py --check` exit 0; `test_project_control.py` OK (23 groups); `test_directive_reminder.py` OK (12 tests).
- `test_directive_compliance.py`: **UNVERIFIABLE in this sandbox** — general D-001 registry harness (140 subprocess/git-heavy adversarial cases in temp dirs), zero M5-T047 references, exceeded a 20-min bound on Windows. Environment performance limit, not a defect; the authoritative CI-wired integrity gate (the validator) passed. Recommend the orchestrator confirm the last control-plane CI run of this job is green rather than treat the local timeout as blocking.

---

## v2 task_verifications rows to stamp

Read `reviewed_manifest_sha256` myself from `project-control/gates/M5-T047-G1.json` `content_manifest_sha256` = `9c6050a5ffcf743061cbbfed94e60d2a6434c3862bc49bb177bd24a2fb2c53de` (identical across G1–G5 and reports/M5-T047.json). Frozen reviewed content identity = `ca94b2c3` (== gate-record head `7bd3dd0a` for the T047 surface, byte-identical). `reviewed_sha` in the rows = the restamp target (the acceptance-seam head the orchestrator produces); valid under the pre-authorization. Rows: per registry, applicable_requirement_ids [D-066-R001] / [D-073-R006], producer backend-engineer, verifier directive-compliance-verifier, schema directive_verification/v2, requirement state PASS with the evidence text as returned.

## Restamp pre-authorization (stated up front)
This PASS carries to a restamped acceptance-seam head **without fresh review** when ALL hold at record time:
1. **Anchor:** all 10 M5-T047 allowed_paths are byte-identical between `ca94b2c3` and the restamp target (`git diff --stat ca94b2c3 <target> -- <10 paths>` empty). The corrected consumer test `address-resolution.test.tsx` also stays byte-identical.
2. Packet `directive_refs`, `allowed_paths`, and the evidence-map `material_commit` unchanged; `evaluate_task_refs(M5-T047)` applicable == cited (D-066-R001, D-073-R006).
3. D-066 and D-073 remain `active`, R001/R006 unamended, source digests match.
4. `validate_directive_compliance.py --check` exit 0 at the record state.

**Explicit disjoint-peer tolerance** — the following intervening commits do NOT void this authorization, since none touches any of T047's 10 allowed paths (verified: only architect/, condo connectors, spatial, profile, rules-matcher, and control-plane files appear in `d27a6a83..HEAD`):
(a) orchestrator control-plane commits (project-control/**);
(b) M5-T045 acceptance-seam commits (condo connectors / spatial/live_provider / profile/zoning_crosscheck / architect display components — zero overlap);
(c) M5-T048 / M5-T049 lane commits (proposal scenario/contracts and named_street_override matcher surfaces — zero overlap).
If any commit in the restamp range modifies a T047 allowed_path (condition 1 fails), the carry is void and a fresh delta-attestation is required.

I changed no state. Orchestrator: record the two v2 rows and the gate result per ADR-005 after validating this ruling.
