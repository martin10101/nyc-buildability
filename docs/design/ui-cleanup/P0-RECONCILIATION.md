# D-086 P0 reconciliation — UI deep-dive assessment vs the current head

Task **M5-T080** (D-086 phase P0, docs only). Produced by the frontend-engineer producer in
worktree `wt-m5t080` at pinned head **`b56f3d5b40171bcb6b760f97eb0eef574995f8ae`**
(branch `task/M5-T080-p0-reconcile`). This file carries the GLOBAL reconciliation items; the
row-by-row disclosure-migration ledger is `disclosure-ledger-a.json` (sections 3–6 families,
PART A) and `disclosure-ledger-b.json` (sections 7–9 families, PART B, written concurrently in
`wt-m5t080b`).

**Spec source (binding, input not authorization — D-086-R001):** `docs/UI_DEEP_DIVE_ASSESSMENT.md`,
frozen at `dc5a763e`, LF-normalized sha256 `c6d1b25779c2dd3fb4699d6a99ca50d9695d82f7afc05986fe58de5cf8504b84`
(matches the capture-commit `1cb14c4e` cited value `c6d1b257…`; verified this seam with
`tr -d '\r' < docs/UI_DEEP_DIVE_ASSESSMENT.md | sha256sum`). The on-disk CRLF sha differs
(`ed94df52…`) — expected on Windows checkout, not drift.

---

## 1. Per-cited-file drift (assessed `dc5a763e` → pinned head `b56f3d5b`)

**How checked (authoritative):** `git diff --stat dc5a763e b56f3d5b -- apps/web` returns **0 changed
files**, and `git diff --name-only dc5a763e b56f3d5b -- apps/web | wc -l` = **0**. Every inventory
source span and every cited test lives under `apps/web/**`, so **drift = `unchanged` for all 381
inventory rows and every copy-wall/no-loss test the assessment cites.** The assessment's own note
("apps/web byte-identical between `dc5a763e` and the pinned head") is confirmed, not assumed. Each
row's `assessed_source` and `current_source` therefore carry the same `path:line` span.

| Cited surface (representative) | Drift | Evidence |
|---|---|---|
| All 97 non-test `apps/web/src/**/*.tsx` (assessment §16 register) | unchanged | `git diff --stat dc5a763e b56f3d5b -- apps/web` = 0 files |
| Cited libs: `lib/bbl.ts`, `lib/disclaimer.ts`, `lib/format.ts`, `lib/coverage.ts`, `lib/missing-inputs.ts`, `lib/architect/{proposal-draft,max-envelope-api,zoning-context}.ts`, `lib/{outline-bridge-api,proposal-checks-api,address-api,address-search}.ts` | unchanged | same diff (0 files under apps/web) |
| Cited copy-wall / no-loss tests: `e2e/{honesty,proposal-editor,development-limits,architect-workspace,rule-evaluation,partial-and-conflict}.spec.ts`; `src/components/**/__tests__/*.test.tsx` | unchanged | same diff; existence + span content spot-checked on disk (see §6 note) |
| `docs/UI_DEEP_DIVE_ASSESSMENT.md` | added since audit (assessment itself committed at `1cb14c4e`) | content byte-frozen; sha matches |

**Non-`apps/web` files the assessment references that DID change `dc5a763e`→`b56f3d5b`** (relevant to the
reconciliation, not to any inventory row):

| File | Drift | What changed / reconciliation note |
|---|---|---|
| `docs/DISCOVERY_BACKLOG.md` | changed (+8 lines) | Head adds `DB-051`, `DB-052`, and sweeps 256th–259th (T076/T074/T075/T073 accepts). See §3. |
| `.claude/rules/expansion-agent-dispatch-hold.md` | changed (+ §2.3) | Head adds **§2.3 (D-087 scoped release, 2026-09-24)** which also names D-082 inline — this **reconciles the assessment's flagged "hold has no D-082 subsection" documentary mismatch** (§11). See §4. |
| `project-control/directives/` | added D-086, D-087 records | D-082 and D-087 directive records exist at head; boundary check in §4. |

No source, test, copy, rule, or assessment file is edited by this task; only the four
`allowed_paths` change.

---

## 2. Reachable route + state map (verified in source at the pinned head)

Verified with `find apps/web/src/app -name page.tsx` and by reading `app/property/page.tsx:38-46`,
`lib/architect/navigation.ts:1-11`, and the assessment §3 route table (byte-identical source). The
code-graph navigation block (D-066-R001, graph regenerated at the contract seam) was available;
routes were confirmed in actual source rather than relying on the advisory graph.

| Route / surface | Entry file | Composition & flag | State families (inventory home) |
|---|---|---|---|
| `/` | `app/page.tsx` | Welcome/entry (not a result) | landing header, env/review badge → SH-02 |
| `/property` | `app/property/page.tsx:39-46` | `ArchitectEntry` when `ruleEvaluationSurfaceEnabled({ruleeval})`, else `PropertyLookup` | entry/BBL, identity, loading, mismatch/withheld, failure → SH-03..SH-14, A/F/E/§7-8 |
| `/property/confirm` | `app/property/confirm/page.tsx` | architect overview (BBL required) OR legacy `ConfirmScreen` | address confirm/identity/map, legacy confirm → AC*, M*, LC* |
| `/property/compare` | `app/property/compare/page.tsx` | architect scenarios OR legacy `CompareScreen` | scenario/limits/records, compare states → SW*, ZC*, ME*, §7 A/C, §8 LS-C |
| `/property` error | `app/property/error.tsx` | route error boundary | one failure/trust/recovery state → SH-14 |
| Architect workspace views | `ArchitectEntry.tsx:114-165`; `navigation.ts` | `WORKSPACE_VIEWS` = overview, facts, zoning, scenarios, **proposal**, evidence, documents, issues, report, **envelope/units/financials** (Planned) | proposal editor/drawing/limits, evidence, report → §5 PE/DR/PC/PV/ME, §7 E/R |
| Proposal | `ArchitectEntry.tsx:44-50,162-164` | `MaxEnvelopePanel` before `ProposalEditor` | limits-first then editor → ME*, PE*, DR*, PC*, PV* |
| `/survey/review`, `/survey/review/[documentId]` | `app/survey/review/*` | inbox + document review (internally gated) | inbox/doc/fact/decision → §9 SR* |
| `/dashboard` (+ `error.tsx`) | `app/dashboard/*` | internal owner observability | mission/map/work/roadmap/activity → §9.8 DB01–DB22 |

Planned views (`envelope`, `units`, `financials`) render honest planned-state handling — an
unavailable capability is **not** a populated result (assessment §11; ledger F07/A02 note in PART B).
No route drift: the route set at head equals assessment §3.

---

## 3. Latest DISCOVERY_BACKLOG disposition for every DB item the assessment cites (§10.4)

Read from `docs/DISCOVERY_BACKLOG.md` **at the pinned head** (rows + all later Sweep lines; later
sweeps override earlier OPEN cells, per D-069). "Latest" reflects head through the 259th acceptance
seam (seq 128). Items are the discovery-backlog `DB-0xx` namespace (distinct from the §9.8 dashboard
`DB01–DB22` inventory rows).

| DB item | Latest status (head) | Note relevant to P0 |
|---|---|---|
| DB-001 | **OPEN** | Split-lot apportionment; legal-research class. Keep unresolved scope + all districts. |
| DB-002 | **RESOLVED** | Research + resolver M5-T042 (225th); live wiring via DB-029 (230th). |
| DB-003 | **WATCH** | Source-stale dataset; freshness cue must survive. |
| DB-005 | **RESOLVED** | ZoLa-link unification (M5-T036). |
| DB-006 / DB-007 / DB-009 | **RESOLVED** | Address retry/label + tests (M5-T038). |
| DB-008 | **WATCH** | 6 s address deadline vs slow-but-healthy latency. |
| DB-010 | **RESOLVED** | Named-street override matcher (M5-T039) + wiring (M5-T040). |
| DB-011 | **WATCH** | Tangency legal tolerance; G6 queue. |
| DB-014 / DB-015 / DB-020 | **RESOLVED** | Wide-street serialization + provider (M5-T035/T037). |
| DB-016 | **RESOLVED** | Zoning-context panel (M5-T036) — governs ledger ZC-01. |
| DB-017 | **OPEN** | Flood/transit/split-zone flag carrier decision (design). |
| DB-018 | **OPEN** | Two ZoLa affordances consolidation (design). |
| DB-019 | **RESOLVED** | aria-hidden glyphs + honest null-BBL note (M5-T038). |
| DB-021 / DB-023 | **RESOLVED** | M5-T040 (legal halves fold into DB-011 at G6). |
| DB-024 | **RESOLVED** | Circular-recovery copy (M5-T041) — governs AD12. |
| DB-025 | **RESOLVED** | (a-d M5-T040; e M5-T041; f note). Owner-question rider persists as **DB-030(a) OPEN** (whole-evaluation review banner). |
| DB-026 | **RESOLVED** | Address→lot identity (recon + M5-T046, 228th); residual = DB-032. |
| DB-027 | **OPEN** | Small a11y/test polish riders. |
| DB-028 | **RESOLVED** | Wiring hardening build items (M5-T043); riders → DB-030. |
| DB-029 | **RESOLVED** | Condo billing-BBL live wiring fully (M5-T044/T045, 230th). |
| DB-030 | **OPEN** | (f) matcher cohesion RESOLVED (M5-T049, 231st); (a) owner question + (b-e) watch remain. |
| DB-031 | **RESOLVED** | Multi-lot condo records view (M5-T052, 234th) — governs PART-B C*. |
| DB-032 | **RESOLVED** | Record-address channel (M5-T047, 229th); polish → DB-033. Governs AC10. |
| DB-033 | **RESOLVED** | T047-wave polish (M5-T050, 233rd). Governs AC02. |
| DB-035 | **RESOLVED** | CLS/late-insert riders (M5-T055, 238th). |
| DB-036 | **RESOLVED** | Slash-district sanitizer (a)+(e) M5-T063 (245th); rest earlier. Governs ZC-02, PART-B condo. |
| DB-037 | **OPEN** | (a)/(b) rode T057; (d) site-definition slice-1 T059; confirm-UX/map/combined-land slices remain. |
| DB-038 | **OPEN** | (b)/(c) closed (245th); (a) bbl.py precond + (d) future-sink + (e) rename-carry + (f) remain. |
| DB-040 | **OPEN** | api-side closed (246th/249th/252nd); (f) auth deferred (B-001), (m)/(o)/(p) confirm-UX slice, (t) posture remain. |
| DB-042 | **OPEN (partial)** | (c)/(d)/(e) closed (245th); (a)/(b) bound to the T059 slice-2/mount packet. |
| DB-043 | **OPEN** | Proposal-editor polish riders; contract AFTER the D-076-R003 owner checkpoint; (a) focus applied T065/T066. Governs PE/DR/PV. |
| DB-044 | **OPEN** | T063 announcer riders. |
| DB-045 | **OPEN** | (a) real-parcel bridge **delivered bounded** (M5-T073, 259th; **3/8 pass**, refusals = capacity+ambiguity); (c) server-500 proof (M5-T074, 257th); riders folded here for the MOUNT packet. Governs DR/ME mount. |
| DB-046 | **RESOLVED** | Max-engine test hardening (a)-(f) (M5-T068, 251st); (i) public-exposure. |
| DB-047 | **OPEN (partial)** | (d)/(e) closed (253rd, T071); head DB-047 row = the M5-T066 adoption/street-line/finiteness cluster (a)-(c),(f)-(j) remain. Governs DR-05/DR-08. |
| DB-048 | **RESOLVED** | Flaky AS-1 sync spec rewritten (M5-T071, 253rd). |
| DB-049 | **OPEN** | Drawing-surface a11y/disclosure cluster — the **CURRENT M5-T078 lane** addresses it. Governs DR-05/DR-08. |
| DB-050 | **OPEN** | (a) geometry threading **LIVE as M5-T076** (accepted 256th); spun off DB-051; (b)-(m) riders remain; **split-district disclosure required PRE-MOUNT** (DCV finding 5). Governs ME/DR mount. |
| DB-051 (head-new) | **OPEN** | Geometry-threading test/consumer cluster (M5-T076 wave) — the **CURRENT M5-T077 lane**. |
| DB-052 (head-new) | **OPEN** | Local directive-harness slowness; control-plane tooling packet. Not a UI item. |

**Reconciliation delta beyond the assessment's frozen §10.4 view:** head adds only `DB-051`, `DB-052`,
and the T073/T074/T075/T076 accepts (seams 256th–259th). Net UI effect: DB-045(a) is now *delivered
but bounded* (3/8), DB-045(c) closed, and the geometry-threading mount work is live-but-not-closed
(DB-050(a)→M5-T076 accepted, DB-051 open). The mount is **not** proven complete; split-district
disclosure and authoritative-geometry threading remain pre-mount preconditions.

---

## 4. D-040 / D-076 / D-082 / D-087 boundary check

Verified against `.claude/rules/expansion-agent-dispatch-hold.md` (§2 + §2.1–§2.3 at head) and the
directive records under `project-control/directives/`.

| Boundary | Hold-notice section (head) | Released scope | P0 compliance |
|---|---|---|---|
| **§2 base hold** | §2 (owner 2026-07-17) | 19-task pack, 9 contracts, GDS P1–P8, master-plan changes on the pack's instruction **all SUSPENDED** | P0 contracts none of these, authors no pack contract, applies no GDS proposal, changes no master plan. ✓ |
| **D-040** | §2.1 (2026-09-12) | ONE increment: address-flow lot-outline (MapPLUTO connector + confirm-card outline, MapLibre GL JS) | Released + implemented (`LotOutlineMap`, `AddressConfirmCard`). Ledger M*/AC* describe this existing surface — within boundary. ✓ |
| **D-076** | §2.2 (2026-09-19) | proposal-editor phased plan + phase-B flat outline/walls/floors/heights increments; work beyond phase B waits for the plan's owner-review checkpoint | Phase B0–B3 accepted (through 244th); **D-076-R003 post-B3 owner checkpoint REACHED, owner review QUEUED**. Ledger PE/DR/PC/PV describe the existing flat editor — no work beyond phase B. ✓ |
| **D-082** | named inline in §2.3 (2026-09-20) + `project-control/directives/D-082-max-envelope-first-and-map-drawing/` | max-envelope-first + map drawing | Released; T064/T065/T066/T070 accepted. Ledger ME/DR describe these surfaces. **The assessment's flagged documentary gap ("hold has no D-082 subsection", §11) is RECONCILED at head** — §2.3 references D-082 and its directive record exists. ✓ |
| **D-087** | §2.3 (2026-09-24) + `project-control/directives/D-087-parallel-build-3d-cad-pdf/` | 3D massing, CAD/DXF export (native DWG = owner licensing), phase-C PDF blueprints, CAD write/edit/export — as orchestrator-designed `M<x>-T<n>` packets | Post-dates the assessment; the assessment audits only current 2D surfaces and starts none of the pack. **The ledger contains no 3D/CAD/PDF rows** — P0 stays clear of D-087 families. ✓ |

**Boundary conclusion:** P0 is docs-only reconciliation and no-loss inventory; it neither contracts nor
starts any held expansion work, authors no pack contract, applies no GDS proposal, and changes no
master plan. It stays entirely within §2 and the scoped releases §2.1–§2.3. Phase D beyond D-087's
families remains held (§2.3).

---

## 5. Section-13 verification matrix (finding → fixture/steps → owning later slice)

Assessment §13 lists source-grounded risks to verify **before or alongside** layout work — not claimed
live reproductions. Each must be reproduced from existing fixtures (do not label as live findings).

| §13 finding (source) | Priority | Fixture / steps | Owning later slice / ledger rows |
|---|---|---|---|
| Report freshness — edits leave `outcome` intact; save pairs current draft with existing report (`ProposalEditor.tsx:73-79,105-137,195-403`) | High | Run a check → edit geometry/levels/attestations → inspect current result → save/select a variation → edit during an in-flight check. Bind displayed/saved results to the checked input revision; current-vs-stale must be visible. Verify **before** repair. | **P4** proposal behavior task (before visual polish); DB-043(b). Ledger PE-08/PE-10/PV-02. |
| Sample attribution — `rectangleSampleDraft()` seeds R5/wide/8,000 sq ft as "your input" (`ProposalEditor.tsx:73,183-185`; `proposal-draft.ts:421-449`) | High | Open two different BBLs, inspect the seed; label/gate the example or seed only provenance-supported inputs; no silent inference. | **P4** proposal behavior task. Ledger PE-10 (open_question), PE-01. |
| Generated-option mount — DB-050 authoritative-geometry / split-district disclosure / adoption feedback | High before mount | Orchestrator reconciles accepted backend/mount state; show ALL split districts + truthful candidate availability; preserve edits on re-adoption via an explicit reviewed interaction. | **Geometry-threading MOUNT packet** (DB-050(a) LIVE as M5-T076; DB-051 = M5-T077; DB-045 bounded). Ledger ME-04/ME-03/DR-08. |
| Null-end "in effect…to present" vs "simultaneously in effect" (`RuleEvaluationResult.tsx:279-280`; `NoScenarioBlock` intro) | Medium | Scope a semantic correction with rule/domain (G6-aware) review; retain recorded dates/unknowns, not merely hide the claim. | **P3/P5** rule-eval + compare, G6 legal review. PART-B LS-E10, LS-C10. |
| Manual fallback "Street name only" copies full query into Street (`AddressResolutionScreen.tsx:220-229`) | Medium | Exercise manual fallback; visibly preserve the original query and clearly label needed fields. Parsing = separate contract. | **P2** address slice. Ledger AD04, AD01 note. |
| DB-049 drawing issues — incomplete rows omitted; missing markers; disabled Convert/focus; competing live regions | Medium | Validate mixed complete/incomplete rows, map loading/fallback/selection, keyboard-only conversion; keep an explicit omitted-row state until resolved. | **P4** drawing slice / **current M5-T078 lane**. Ledger DR-05, DR-08. |
| Survey "All material facts are resolved" fallback for no-fact docs; `DocumentOverlay` null `imageRef` (`surveyReview/model.ts:130-145`; `DocumentOverlay.tsx:126-138`) | Medium | Reproduce uploaded/processing/zero-fact/null-preview states; display true lifecycle/preview availability locally. | **P6** survey. PART-B SR11, SR27. |
| Static "Every value … official-source fact" + shared coverage glosses span record/result contexts | Medium | Test fact / rule / scenario / human-confirmation fixtures; preserve backend statuses with object-specific explanation. | **P3/P5** coverage vocabulary review. PART-B LS-P13, `lib/coverage.ts`. |
| Print opens non-raw disclosures; mobile hides env/nav-footnote; map attribution ~10px (`ReportView.tsx:53-65`; CSS :138, :74-77) | Medium | Separate print, narrow-width and assistive-technology gates; verify actual disclaimer/environment visibility and readable source/accuracy text. | **P5** report + **P7** integrated. Cross-cut (SH-01, M01, M11). |
| Duplicated ZoLa links, source-location narration, empty success cards, internal route/schema strings, legacy future-Evidence | Low / consolidation | Map each removal to one surviving affordance/state; verify the relevant route variant. No disclosure deleted without a destination. | Cross-cut P2–P6 consolidation. Ledger AC05/ZC-01 shared-copy; PART-B LS-C28. |

---

## 6. Ledger summary + completeness proof

**Exact enumeration command** (run from the worktree root; sections 4–9 = lines 57–923 of the spec,
per `grep -nE '^## [0-9]+\.' docs/UI_DEEP_DIVE_ASSESSMENT.md`; every table row whose first cell starts
with an inventory id):

```
sed -n '57,923p' docs/UI_DEEP_DIVE_ASSESSMENT.md \
  | grep -oE '^\|[[:space:]]*(SH-|PE-|DR-|PC-|PV-|ME-|SW-|ZC-|LS-P|LS-C|LS-E|LS-F|LS-T|AD|AC|LC|SR|DB|M|A|C|F|E|R)[0-9]+' \
  | sed -E 's/^\|[[:space:]]*//' | sort
```

**Total enumerated inventory rows: 381** (`… | wc -l` = 381; POSIX leftmost-longest keeps `AD/AC/ME/LS-*`
from being swallowed by `A`/`M`; `DB-0xx` discovery rows are protected by the hyphen). **Zero
duplicates** (`… | sort | uniq -d` empty). **Zero intra-family gaps** (independently re-verified;
note **SR spans SR01–SR62 with SR51 present at line 829** and DB dashboard rows are DB01–DB22).

Expected per-family counts for ALL sections 4–9 families:

| Part | Family (section) | Count | | Part | Family (section) | Count |
|---|---|---|---|---|---|---|
| **A** | SH (§4) | 15 | | **B** | A (§7.2) | 15 |
| A | PE (§5.2) | 10 | | B | C (§7.3) | 11 |
| A | DR (§5.3) | 23 | | B | F (§7.4) | 8 |
| A | PC (§5.4) | 6 | | B | E (§7.5) | 16 |
| A | PV (§5.5) | 3 | | B | R (§7.5) | 5 |
| A | ME (§5.6) | 17 | | B | LS-P (§8.1) | 16 |
| A | SW (§5.7) | 3 | | B | LS-C (§8.2) | 28 |
| A | ZC (§5.8) | 4 | | B | LS-E (§8.3) | 11 |
| A | AD (§6.1) | 28 | | B | LS-F (§8.4) | 17 |
| A | AC (§6.2) | 11 | | B | LS-T (§8.6) | 15 |
| A | M (§6.3) | 13 | | B | SR (§9.2–9.6) | 62 |
| A | LC (§6.4) | 22 | | B | DB (§9.8) | 22 |
| | **PART A total** | **155** | | | **PART B total** | **226** |

**Grand total 155 + 226 = 381.**

**Part-A completeness check (this producer):** `disclosure-ledger-a.json` contains exactly **155** rows;
its id set is a verified **bijection** with the enumerated PART-A ids (SH/PE/DR/PC/PV/ME/SW/ZC/AD/AC/M/LC)
— `in ledger not enum: []`, `in enum not ledger: []`. Every row carries all 18 packet keys; every
L-marked row has non-empty `primary_state`, `progressive_destination`, `accessibility`,
`print_destination`, `proof_owner`; **zero rows are `consolidate`/`retire`** (dispositions: 16 `keep`,
139 `convert`), so there are **zero orphaned `replacement_ref`s** (vacuously satisfied). `drift` =
`unchanged` on all 155 (apps/web byte-identical, §1). Validated with
`python -m json.tool docs/design/ui-cleanup/disclosure-ledger-a.json` (exit 0).

**Cross-file completeness (both ledgers) is completed AT HARVEST.** PART B writes `disclosure-ledger-b.json`
(the 226 §7–9 rows) concurrently in `wt-m5t080b`; the orchestrator's harvest verifies that all 381
enumerated ids appear **exactly once across `disclosure-ledger-a.json` + `disclosure-ledger-b.json`**
and that every `consolidate`/`retire` row in either file resolves its `replacement_ref`. This producer
cannot perform the cross-file check because `disclosure-ledger-b.json` is out of scope (a separate
producer owns it); the two-file union check is recorded here as a harvest obligation.

### In-flight rows (concurrent lanes at this pinned head)

Per the packet's CONCURRENT WORK note, lanes **M5-T078** (drawing surface) and **M5-T079** (limits
panel) edit `ProposalOutlineDraw/Map` and `MaxEnvelopePanel/max-envelope-api` during P0. Drift is
recorded at **this pinned head only** (`unchanged`); the affected ledger rows carry an
`in-flight (M5-T078/T079)` marker in `open_question`: **DR-01…DR-09** (M5-T078) and **ME-01…ME-17**
(M5-T079). These spans must be re-verified after those lanes land.

---

*P0 does not redesign, and changes no source/test/copy/rule/assessment file — only the four
`allowed_paths`. This reconciliation is the current baseline and the ledger is the no-loss contract
for the later slices P1–P7 (assessment §14). Phase labels are the assessment's report-local names; the
orchestrator assigns canonical ledger task IDs.*
