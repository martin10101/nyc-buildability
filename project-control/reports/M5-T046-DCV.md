<!-- Orchestrator capture: directive-compliance-verifier return for M5-T046 saved VERBATIM
     (transport entity-decoding only: &lt;/&gt; decoded). Ruling at HEAD 535278da over frozen
     content identity c9113e09; six-condition restamp pre-authorization stated up front. -->

I have reproduced all primary evidence. Here is my complete verification report.

---

# Directive-Compliance Verification — M5-T046 (D-001, read-only)

**Verifier:** directive-compliance-verifier (read-only; I changed no state)
**Task:** M5-T046 — Address-to-lot identity honesty (DB-026)
**Branch:** candidate/D-024-mrl-option-b · **Frozen submission identity:** `c9113e09` · **HEAD at review:** `535278da`

## VERDICT: PASS

Both bound requirements independently reproduce as **SATISFIED** at the frozen identity. Amendment discipline holds. No completion narrative was substituted for evidence anywhere I checked.

---

## Identity claims — verified by me via git plumbing (not taken on faith)

- `c9113e09` exists (`git cat-file -t` → commit) and its parent is `fb7af67d` (`git rev-parse c9113e09^` = `fb7af67d…`).
- **All 10 M5-T046 allowed_paths are byte-identical `c9113e09 → HEAD`:** `git diff --stat c9113e09 535278da --` over the ten paths returned **empty**.
- **The 9 material web files are byte-identical `fb7af67d → HEAD`:** `git diff --stat fb7af67d 535278da --` over them returned **empty**. So the walkthrough/CI material at `fb7af67d` = the frozen submission material.
- The review wave + gate records landed at `064726f7` (6 files, +391, **all `project-control/**`** — control-plane only), i.e. no material web change after the freeze.
- `validate_directive_compliance.py --check` → **exit 0**; both D-066 and D-073 `source-001.md` digests match their manifests (LF-normalized); both directives `active`.

---

## D-066-R001 — code-graph contract-seam obligation → **SATISFIED (PASS)**

Requirement (registry `project-control/directives/D-066-code-graph-loop-wiring/requirements.json:11`): regenerate the graph at the seam, embed a graph-derived navigation block in the packet, instruct the producer to consult `query.py --no-regen`, and keep the graph advisory with every material conclusion verified in source. Applicability `task_ids` includes `M5-T046` (`requirements.json:31`).

Primary evidence I reproduced:
- **Nav block embedded in the packet, present at the frozen head:** `project-control/tasks/M5-T046.json` input index 3 (the `CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated at this contract seam, 743 files/15651 nodes)` text, with named consumers and the `python tools/code_graph/query.py --no-regen impact <path>` + "graph is ADVISORY - verify in source" instruction). `git show c9113e09:…M5-T046.json` grep counts: nav-block header = 1, `query.py --no-regen` = 1.
- **Graph regenerated at seam:** G0 report `project-control/reports/M5-T046-G0.md:28-30` records "graph regenerated at this seam (743 files / 15651 nodes / 6934 edges)". This is an orchestrator-recorded figure over an ephemeral (uncommitted) graph — consistent with the directive's advisory design; I could not re-derive the exact counts without regenerating, but that is not the load-bearing conclusion.
- **Advisory-verified-in-source — the material conclusion, reproduced by me independently:** the producer report §5 (`M5-T046-producer-report.md:117-136`) claims `resolveLotFromGeoSearch` has **no production importer** and that GeoSearch suggestions discard `pad.bbl`. I reproduced this with `git grep`: `resolveLotFromGeoSearch` appears in `apps/web/**` only in its definition (`address-search.ts`) and its test — every other hit is docs/registry/reports; there is **no `.tsx` production importer**. The four nav-block-named `address-search` consumers all exist and import it (`AddressAutocomplete.tsx:9`, `use-address-suggestions.ts:3`, plus the two test files), and `AddressConfirmCard.tsx:8-11` imports from `AddressAutocomplete` (the stated depth-2 edge). This is the exact finding that drove the ORCH-SCOPE-ADJUDICATION, and it holds in source.
- Tooling present: `tools/code_graph/generate.py` + `query.py`.

Evidence map claim (`M5-T046-evidence-map.json` D-066-R001) is reproduced, not merely accepted.

## D-073-R006 — records vs calculated allowances → **SATISFIED (PASS)**

Requirement (`project-control/directives/D-073-architect-outcome-next-phase/requirements.json:175`): preserve the records/allowances distinction across interface and report; a computed allowance shows only when its conditions are established; an unresolved computation is not represented by a reference number. Applicability `task_ids` includes `M5-T046` (`requirements.json:184`).

Primary evidence I reproduced:
- **Records-semantics display in source:** `apps/web/src/components/address/AddressConfirmCard.tsx:96-136` renders the entered input verbatim (`enteredInput`, `:96-107`, trim decides only blank-vs-not) beside the distinct matched city line (`confirm-address`, `:114-121`) and the BBL identity (`:161-171`). The comment block `:80-95` states explicitly: "This is a RECORD — it implies no computed value" and that the PLUTO address-of-record gap is "a reported discovery, not a built-around field (no server endpoint / contract change here)."
- **No computed allowance appears on this surface at all** — only records (entered input, matched address, BBL, ZoLa link). The records-vs-allowances risk here is that an address be mistaken for a computed value; the code + tests foreclose it.
- **Journey tests, verified in source:** `apps/web/src/components/address/__tests__/address-confirm.test.tsx` S8 (`:492-517`) asserts the verbatim entered input distinct from the normalized matched line with BBL as identity; S9 (`:536-639`) asserts the raw typed text (`"  1279 37 st bk  "`) renders in `<strong>` exactly, distinct from both the picked city-shaped label and the matched canonical line.
- **Record-address gap honestly reported, not built around:** `AddressConfirmCard.tsx:80-86`; `docs/research/source-registry-drafts/geosearch.json:49` (`known_limitations`) and `:60` (`open_questions` OQ-5); registry `match_discipline_verbatim_basis` at `:35` documents the equality gate as the records-grade discipline binding any future promotion.
- Packet AS-1/AS-4 (amended, library level), AS-6 (records display), AS-8 (walkthrough) carry the distinction (`M5-T046.json:51,54,56,58`); HJ report `M5-T046-HJ.md:20,28,34` PASS — "nothing on screen claims a protection that does not exist."

## Amendment discipline → verified

- **ORCH-SCOPE-ADJUDICATION recorded pre-submit with a G0 re-record.** The tagged input (packet input 17) + amended AS-1/AS-4 landed at `c3c690f7` with a G0 addendum (`M5-T046-G0.md:41-57`); G0 was re-recorded PASS at that head by commit `0aa3fc4d`. All present at the frozen head: `git show c9113e09:…M5-T046.json` shows `ORCH-SCOPE-ADJUDICATION` ×5 and `AMENDED per ORCH-SCOPE-ADJUDICATION` ×3.
- **[ORCH-CORRECTED] AS-5 change is test-only — confirmed independently.** `git diff --name-only c3c690f7 fb7af67d` = `apps/web/src/lib/__tests__/address-search.test.ts` (test) + `project-control/gates/M5-T046-G0.json`, `state.json`, `tasks/M5-T046.json` (control-plane). **No production source changed.** CI evidence `M5-T046-ci-evidence.md`: red at `c3c690f7` was exactly one test (`AS-5 … expected 'no_match' to be 'resolved'`); green at `fb7af67d` (run 35425516645 success).
- **No self-accept / no completion narrative as evidence.** Producer report §0/§8 explicitly refuses to self-accept a reduced objective and routes the scope conflict to the orchestrator; the orchestrator resolved it by recorded adjudication with reasoning, not a narrative. Producer disclaims self-certification (`M5-T046-producer-report.md:12-17`).

---

## Fields for the orchestrator to stamp (v2 `task_verifications` rows)

Two rows, one per registry. Shared values from the M5-T046 review gates (all five PASS at `064726f7`, identical `content_manifest_sha256`):

- **reviewed_manifest_sha256:** `1de6180b4891074b80756b2bdbda24f4947a3c8caeda5ca4f5dc9340ddeeec48`
- **producer:** `frontend-engineer` (material producer; material cherry-picked to `3182f0a2` under the no-commit posture)
- **verifier:** `directive-compliance-verifier`
- **reviewed_sha:** the accept-seam / restamp target (currently `535278da`), under the pre-authorization below; the reviewed **content identity** is `c9113e09`.

Row A → `D-066/verification.json`: `task_id` M5-T046, `applicable_requirement_ids` `["D-066-R001"]`, requirement `D-066-R001` state **PASS**, evidence = "Nav block present in the packet (`tasks/M5-T046.json` input 3) with `query.py --no-regen` + advisory clause, present at c9113e09; the load-bearing no-production-importer conclusion reproduced by git grep in source; consumers/edges verified; graph advisory-verified-in-source (producer report §5; G0 report §Nav)."

Row B → `D-073/verification.json`: `task_id` M5-T046, `applicable_requirement_ids` `["D-073-R006"]`, requirement `D-073-R006` state **PASS**, evidence = "Confirm-arc entered-vs-matched records line (AddressConfirmCard.tsx:80-136) with records-semantics comment and journey tests S8/S9 (address-confirm.test.tsx:492-639); no computed value on the surface; record-address gap reported as OQ-5 discovery, not built around; AS-6/AS-8 + HJ PASS."

Applicable == cited for both (D-066: only R001 lists M5-T046; D-073: only R006 lists M5-T046).

---

## RESTAMP PRE-AUTHORIZATION (stated up front, M5-T042 pattern)

This ruling **carries to a restamped head WITHOUT a fresh review** iff ALL hold at record time:

1. **Content identity byte-stable:** `git diff c9113e09 <restamp-target> --` over the ten M5-T046 allowed_paths is **empty** (currently empty at `535278da`).
2. **Binding stable:** packet `directive_refs` (`D-066-R001`, `D-073-R006`), `allowed_paths`, and the evidence-map `material_commit` unchanged; `evaluate_task_refs` ok (applicable == cited).
3. **Intervening commits are disjoint:** every commit between `c9113e09` and the target touches **only `project-control/**`** OR paths disjoint from the M5-T046 surface. **Explicit disjoint-peer tolerance:** a material M5-T045 commit (`services/api/**` and the architect display components `PropertyOverview.tsx` / `AnalysisIdentityNotice.tsx` / `ReportView.tsx` / `ZoningContextPanel.tsx` and their tests — all in M5-T046's `forbidden_paths`, zero overlap with its 10 allowed_paths) landing in that range does **not** void this ruling.
4. **Packet substance byte-stable:** the D-066 nav-block input and the amended AS-1/AS-4/AS-6/AS-8 scenarios remain byte-stable in the packet.
5. **Directive sources intact:** D-066 and D-073 `source-001.md` unchanged (digests match manifest), R001/R006 unamended, both directives `active`.
6. **Validator green:** `validate_directive_compliance.py --check` exit 0 at the record state.

If any condition fails (e.g. an M5-T046 allowed_path is edited after `c9113e09`, or a non-disjoint path is touched), a fresh delta-attestation is required before the row is stamped.
