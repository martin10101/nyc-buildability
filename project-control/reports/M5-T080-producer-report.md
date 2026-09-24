# M5-T080 producer report — PART A (D-086 P0 reconciliation + ledger sections 3–6)

**Task:** M5-T080 (D-086 phase P0; docs only). **Producer:** frontend-engineer.
**Worktree:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t080` — branch `task/M5-T080-p0-reconcile`.
**Pinned head:** `b56f3d5b40171bcb6b760f97eb0eef574995f8ae` (verified FIRST; matched the packet's
required head on `task/M5-T080-p0-reconcile`).

**Files changed (exactly the allowed_paths this producer owns):**
- `docs/design/ui-cleanup/disclosure-ledger-a.json` — 155 PART-A inventory rows (§3–6 families).
- `docs/design/ui-cleanup/P0-RECONCILIATION.md` — global reconciliation items.
- `project-control/reports/M5-T080-producer-report.md` — this file.

`docs/design/ui-cleanup/disclosure-ledger-b.json` (PART B) is untouched — a separate producer owns it
in `wt-m5t080b`. No source, test, copy, rule, or `docs/UI_DEEP_DIVE_ASSESSMENT.md` edit anywhere. Never
ran npm/npx/node.

Evidence-status form: `[OBSERVED]` = I ran the command in this worktree and read the output; anything
not observed is routed to harvest with a recipe.

---

## Commands run (explicit cwd = `wt-m5t080`; outputs verbatim)

**Spec identity (`[OBSERVED]`):**
`tr -d '\r' < docs/UI_DEEP_DIVE_ASSESSMENT.md | sha256sum` →
`c6d1b25779c2dd3fb4699d6a99ca50d9695d82f7afc05986fe58de5cf8504b84` — matches the capture-commit
`1cb14c4e` cited `c6d1b257…`. (On-disk CRLF sha `ed94df52…` differs — Windows checkout, not drift.)

**Drift (`[OBSERVED]`):** `git diff --stat dc5a763e b56f3d5b -- apps/web` → **0 changed files**;
`git diff --name-only dc5a763e b56f3d5b -- apps/web | wc -l` → **0**. apps/web is byte-identical between
the frozen assessment SHA and the pinned head ⇒ every inventory span + cited test = `drift: unchanged`.
Non-apps changes (`git diff --name-only dc5a763e b56f3d5b`): `docs/DISCOVERY_BACKLOG.md` (+8),
`.claude/rules/expansion-agent-dispatch-hold.md` (+§2.3), directive records (D-086/D-087) — reconciled
in P0-RECONCILIATION §1/§3/§4.

**Enumeration (`[OBSERVED]`)** — sections 4–9 = lines 57–923 (`grep -nE '^## [0-9]+\.'`):
```
sed -n '57,923p' docs/UI_DEEP_DIVE_ASSESSMENT.md \
  | grep -oE '^\|[[:space:]]*(SH-|PE-|DR-|PC-|PV-|ME-|SW-|ZC-|LS-P|LS-C|LS-E|LS-F|LS-T|AD|AC|LC|SR|DB|M|A|C|F|E|R)[0-9]+' \
  | sed -E 's/^\|[[:space:]]*//' | sort
```
→ total **381** rows; `| sort | uniq -d` → **empty (no duplicates)**. Per-family tally (`| sed -E 's/[0-9]+$//' | sort | uniq -c`):
PART A — SH 15, PE 10, DR 23, PC 6, PV 3, ME 17, SW 3, ZC 4, AD 28, AC 11, M 13, LC 22 = **155**.
PART B — A 15, AC(see AC)…: A 15, C 11, F 8, E 16, R 5, LS-P 16, LS-C 28, LS-E 11, LS-F 17, LS-T 15,
SR 62, DB 22 = **226**. Grand total **381**. No intra-family gaps (independently re-checked with a
Python range scan); **SR spans SR01–SR62 with SR51 present at line 829**; dashboard rows are DB01–DB22
(distinct from the discovery-backlog `DB-0xx` namespace).

**JSON validity (documented test command, `[OBSERVED]`):**
`python -m json.tool docs/design/ui-cleanup/disclosure-ledger-a.json` → exit 0 (valid).

**Bijection check (`[OBSERVED]`):** ledger-a ids vs enumerated PART-A ids →
`in ledger not enum: []`, `in enum not ledger: []`, `MATCH: True` (155 = 155).

**Authority spot-checks (`[OBSERVED]`):** cited test/source files exist on disk at head (20/20 OK);
content of `apps/web/e2e/honesty.spec.ts:11-23` (internal banner + PRD 29 disclaimer),
`max-envelope-panel.test.tsx:274-291` (bans "maximum allowed building"/"demonstrated maximum"), and
`e2e/proposal-editor.spec.ts:430-444` (verbatim `ENVELOPE_DISCLOSURE`) confirmed present.

**Routes (`[OBSERVED]`):** `find apps/web/src/app -name page.tsx` + reads of `app/property/page.tsx:38-46`
and `lib/architect/navigation.ts:1-11` confirm the assessment §3 route set and `WORKSPACE_VIEWS` at head
(no route drift).

---

## Per-AS evidence

**AS-1 (completeness) — MET (PART A).** Every ID'd inventory row in §§4–9 enumerated (command +
per-family counts above); the total 381 splits 155 (PART A) + 226 (PART B). ledger-a.json holds exactly
the 155 PART-A ids, each once, bijection verified; every row has all 18 keys. Independent re-enumeration
(grep + a separate Python matcher) agreed at 381. The **cross-file** check that all 381 appear exactly
once across both ledgers is a recorded **harvest** obligation (ledger-b is out of scope).

**AS-2 (no-loss) — MET (PART A).** Every L-marked row has non-empty `primary_state`,
`progressive_destination`, `accessibility`, `print_destination`, `proof_owner` (builder asserts this;
0 violations). No mark is weakened relative to the assessment (marks transcribed verbatim, incl.
`L`/`L→V`/`L+V`/combinations). **Zero `consolidate`/`retire` rows** — every PART-A row carries surviving
on-surface meaning, so all dispositions are `keep` (16, pure-L retained as-is) or `convert` (139, L→V
progressive); `replacement_ref` is empty throughout ⇒ zero orphaned removals (AS-2 requirement
vacuously satisfied). Rationale recorded in P0-RECONCILIATION §6.

**AS-3 (current truth) — MET.** Every `current_source` span checked at the pinned head: apps/web
byte-identical (`git diff --stat … -- apps/web` = 0), so `drift: unchanged` on all 155. Authority cells
cite real, spot-checkable anchors: PRD sections drawn from the assessment §11 authority table
(§§2,4,9,10,12,19,20,23,27,29,32.2); `exact-copy test <file:line>` and `returned contract <name>` cite
files verified to exist at head (20/20) with three line-spans content-checked; `reviewer finding <DB/HJ>`
cite discovery-backlog ids present at head.

**AS-4 (reconciliation) — MET.** `P0-RECONCILIATION.md` carries: (§1) per-file drift table with the
authoritative `git diff` evidence; (§2) the reachable route + state map verified in source; (§3) the
latest head disposition for every DB item the assessment cites (rows + later sweeps, later overrides);
(§4) the D-040/D-076/D-082/D-087 boundary check against hold §2.1–§2.3 + the directive records; (§5) the
Section-13 verification matrix (fixture/steps + owning later slice per finding).

**AS-5 (scope) — MET.** Exactly the allowed_paths changed (three files this producer owns); no source,
test, copy, rule, or assessment edit. `python -m json.tool` passes on ledger-a.json (exit 0). ledger-b.json
untouched.

---

## Family counts (PART A, this ledger)

SH 15 · PE 10 · DR 23 · PC 6 · PV 3 · ME 17 · SW 3 · ZC 4 · AD 28 · AC 11 · M 13 · LC 22 = **155**.
Dispositions: `keep` 16, `convert` 139. In-flight markers: DR-01…DR-09 (M5-T078), ME-01…ME-17 (M5-T079).

---

## Assumptions / deviations

1. **Authority classification.** For rows the assessment does not pin to a specific test/DB/contract, I
   assigned the governing PRD section from the assessment's own §11 authority table (never invented), or
   `implementation-only prose` for pure structural/removable narration. This is faithful to the
   migration-row Authority definition (§14) which explicitly lists "implementation-only prose" as a class.
2. **Disposition = keep/convert only (no consolidate/retire).** The assessment marks *portions* of mixed
   rows `R`, but no whole PART-A inventory row loses all meaning, so `convert` (keep meaning, compact
   form) is the faithful, no-loss choice and `keep` for pure-L accessibility rows. This trivially
   satisfies "every consolidate/retire names a resolving replacement_ref" and guarantees zero orphans.
3. **`section` field** uses the assessment subsection (e.g., `5.6`, `6.3`). **`phase`** is a best-effort
   P2–P6 mapping to the later slice that owns each surface (address/confirm→P2, overview/zoning/scenario→P3,
   proposal/drawing/limits→P4). Cross-cutting rows (e.g., SH-01 disclaimer) noted in the reconciliation.
4. **`accessibility`/`print_destination`** are usually `P0-proposed:` (the assessment rarely states them
   per-row); they draw on §6.5/§12 rules. Announcement/aria rows carry their own content as `accessibility`.
5. **`current_source` = `assessed_source`** (same span) because apps/web is byte-identical; recorded as
   full repo-relative `path:line` so a reviewer can `git show b56f3d5b:<path>` to spot-check.
6. **Cross-file (both-ledger) completeness** is deferred to harvest by design (ledger-b is a separate
   producer's scope) — recorded as an explicit harvest obligation, not skipped.

## Discoveries (D-069; route to the orchestrator, not fixed in-packet)

- **DISC-1 (documentary, resolved-at-head):** the assessment §11 flags "the hold file names D-040/D-076
  but has no D-082 subsection." At the pinned head this is **already reconciled** — hold §2.3 (D-087,
  2026-09-24) names D-082 inline and a `D-082-…` directive record exists. No action needed; recorded so
  the orchestrator can close the assessment's open reconciliation item.
- **DISC-2 (spec numbering):** the survey family skips no id — SR runs SR01–SR62 with **SR51 present**
  (line 829, `StateHistory.tsx`); I flag it only because a quick read of §9.5→§9.6 (which jumps 50→52 on
  the page) can look like a gap. Not a defect.
- **DISC-3 (mount readiness, from the head backlog):** DB-045(a) real-parcel bridge validation is
  **delivered but bounded** (M5-T073, 3/8 pass — refusals = capacity + ambiguity classes), DB-050(a)
  geometry threading is **live-but-not-closed** (M5-T076 accepted; spun off DB-051, open), and split-district
  disclosure is a recorded **pre-mount** precondition. The later proposal/drawing/limits slices (P4) must
  not treat intercepted-candidate fixtures as proof of deployed generated-option capability.

## Limitations

- Docs-only, thin-client: no tests/build/browser were run; all claims are source/ledger inspection at the
  pinned head. "Test pins" mean assertions exist, not that they passed this session.
- The reachable route/state map is source-grounded (routes + `WORKSPACE_VIEWS` read in actual source);
  it does not establish deployed flag state or live endpoint mounts.

## Requested status

**awaiting_gate** — PART A complete: valid ledger-a.json (155 rows, bijection-verified), the global
reconciliation, and this evidence pass. The cross-file (both-ledger) completeness check is the one
recorded harvest obligation.

*(The orchestrator appends the PART B producer return verbatim below at harvest.)*

END-OF-REPORT

---

## [ORCH-HARVEST] PART B return (verbatim) + cross-file completeness check

Per the packet's SPLIT input, PART B (worktree wt-m5t080b, commit b51cba02, cherry-picked with blob MATCH) returned its evidence as its final message; the orchestrator appends it here byte-for-byte (extracted from the producer's own transcript), followed by the cross-file check the packet assigned to harvest.

### PART B return (verbatim)

M5-T080 PART B — producer report (DOCS ONLY; ledger sections 7-9)

PRECONDITION CHECK
- Worktree HEAD at start: b56f3d5b40171bcb6b760f97eb0eef574995f8ae on task/M5-T080-p0-reconcile-b — MATCHES the required pin. Proceeded.
- Spec drift: `git diff --stat dc5a763e b56f3d5b -- apps/web` = EMPTY (apps/web byte-identical). The assessment file itself did not exist at dc5a763e under that path (added later); its content at my head equals the packet's cited sha256 c6d1b257 (via `git show b56f3d5b:...`; the working-tree sha ed94df52 is only the CRLF smudge). Because apps/web — the tree every source anchor points into — is byte-identical dc5a763e..b56f3d5b, every anchor remains valid at my head.

FILE PRODUCED (only one, in scope): docs/design/ui-cleanup/disclosure-ledger-b.json — 226 objects, each with EXACTLY the packet's 18 keys. PART A files (P0-RECONCILIATION.md, disclosure-ledger-a.json, producer report) untouched.

ENUMERATION COMMAND (run from C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t080b):
  sed -n '417,923p' docs/UI_DEEP_DIVE_ASSESSMENT.md | grep -oE '^\| (LS-[PCEFT][0-9]{2}|[ACEFR][0-9]{2}|SR[0-9]{2}|DB[0-9]{2})' | sed 's/^| //'
  -> 226 ids, 0 duplicates.

PER-FAMILY COUNTS (spec enumeration == ledger, both 226):
  Section 7: A=15, C=11, F=8, E=16, R=5  (55)
  Section 8: LS-P=16, LS-C=28, LS-E=11, LS-F=17, LS-T=15  (87)
  Section 9 (survey SR + 9.8 dashboard DB): SR=62, DB=22  (84)

AS-1 (completeness) — independent re-enumeration: LF-normalized `diff spec_ids ledger_ids` = EXACT MATCH (every enumerated id appears exactly once); `uniq -d` empty. (The raw diff first showed a false 1,226c1,226 purely from CRLF `\r` on the checkout-sed output vs LF from Python — resolved by `tr -d '\r'`.)

AS-2 (no-loss) — L-ROW COVERAGE CHECK: an in-script validator asserted, over all 226 rows: (a) unique ids; (b) every row has the full 18-key set; (c) every row whose mark contains "L" (all L / L->V / L+V / L; ... rows) has non-empty primary_state, progressive_destination, accessibility, print_destination, proof_owner; (d) every consolidate/retire row has a replacement_ref that resolves to an existing ledger id. Result: PASS, 0 failures. Consolidate rows and refs: LS-C08->LS-C24, LS-C23->LS-C22, LS-C27->LS-C06, SR27->SR12 (all resolve). No mark was weakened vs the assessment; where the assessment is silent on a migration field the value is prefixed "P0-proposed:" and no authority was invented.

AS-3 (current truth): drift="unchanged" and current_source==assessed_source for all 226 rows, justified by tree-level byte-identity PLUS 14 spans spot-checked in actual source at the head across every family (A05, C04, E11, R01, LS-P01, LS-C04, LS-E10, SR22, DB07, and 5 more) — all matched the assessment's cited text exactly. authority cells cite only head-verified anchors: 15 test files + lib/coverage.ts/disclaimer.ts/format.ts/surveyReview/* were all confirmed present (existence-checked). authority vocabulary is restricted to the packet's allowed set (PRD <section> only where section 11 maps one; returned contract <name>; reviewer finding <B-001/DB-025/DB-030>; exact-copy test <file:line>; implementation-only prose).

AS-5 (scope): `python -m json.tool docs/design/ui-cleanup/disclosure-ledger-b.json` -> VALID JSON. `git status --short` shows ONLY docs/design/ui-cleanup/disclosure-ledger-b.json. No source/test/copy/rule/assessment edit. Nothing under ctl24 touched. Working tree clean after commit.

PHASE MAPPING (from assessment section 14): A/C/F->P3, E/R->P5, LS-P/LS-C/LS-E/LS-F/LS-T->P3, SR/DB->P6.

CONCURRENT-LANE NOTE (M5-T078 drawing / M5-T079 limits): none of my sections 7-9 source anchors reference ProposalOutlineDraw/Map/MaxEnvelopePanel/max-envelope-api, so no rows needed an "in-flight" flag; recorded drift at my pinned head only.

COMMIT: b51cba02c436d3d19c12c371e3f6f500d3768718 on task/M5-T080-p0-reconcile-b — "M5-T080 part B (ledger sections 7-9)"; 1 file changed (+4522/-1); gitleaks scanned, no leaks; working tree clean. (Git warned "LF will be replaced by CRLF" on checkout — cosmetic autocrlf, committed content is LF.)

OPEN QUESTIONS (carried in per-row open_question fields, not fixed in-packet):
- Section 8 legacy routes have no dedicated phase in section 14. I assigned LS-P/LS-C/LS-E/LS-F/LS-T -> P3 by closest fit (P3's named guards — numeric-promotion, fingerprint, condo, source-link — ARE the section-8 property/compare guards). Orchestrator may want an explicit phase/scope decision for the flag-off property/compare/rule-evaluation routes.
- LS-E10 (RuleEvaluationResult.tsx:279-280): null end-date rendered "in effect ... to present" — confirmed at head; compare sibling rejects this. Corrective = reviewed semantic task (assessment 13, Medium).
- LS-C10 (NoScenarioBlock intro): "simultaneously in effect" unsupported legal-effect assertion — correct transparently under a reviewed task, do not preserve as old copy.
- SR11/SR27 (assessment 9.1/13): verify the "All material facts are resolved" fallback cannot imply completion for an unprocessed/zero-fact document, and add an explicit preview-unavailable cue beside a null-imageRef DocumentOverlay canvas; verify actual upload availability.
- LS-P13: check the absolute "Every value ... official-source fact" wording against mixed-status fixtures before carrying it forward.
- Cross-row method duplication SR19<->SR31 and SR12<->SR27 (SR27 consolidated to SR12) — collapse to one shared Source without dropping unique content.

DEVIATIONS (judgment calls for the reviewer):
- LS-T (test copy-wall) rows are test invariants, not user-visible states. To honor "never weaken a mark" I marked them "L (test invariant / copy-wall)" and filled the five migration fields with "P0-proposed:" content framed for a test row (invariant remains provable; locked strings survive in the related row's named tier; assertion targets accessible/visible text; print parity where the related row prints), proof_owner = the test file itself. If the reviewer prefers these carried as V/reference rows, that is a one-line mark change.
- Line spans written with ASCII hyphen "-" rather than the assessment's en-dash; span numbers preserved verbatim and spot-checkable.

DISCOVERIES (D-069, for the reconciliation/backlog — I did not edit DISCOVERY_BACKLOG.md):
- No section-14 phase exists for the legacy flag-off property/compare/rule-evaluation routes as distinct from the architect surface (see open questions).
- Confirmed at head (not merely from the assessment): RuleEvaluationResult.tsx:279-280 "to present" / "in effect" for null end dates; this is real source drift a reviewed P3/P4 semantic-correction task should own.

END-OF-REPORT

### Cross-file completeness check (orchestrator, at the harvested head)

- Enumeration over docs/UI_DEEP_DIVE_ASSESSMENT.md lines 57-923 (every table row whose first cell starts with an inventory id): 381 ids, 381 unique.
- disclosure-ledger-a.json (155) + disclosure-ledger-b.json (226) = 381 rows, 381 unique; missing from the ledgers: none; extra in the ledgers: none (exact bijection).
- Every row carries exactly the packet's 18 keys; both files pass `python -m json.tool`.
- 344 L-marked rows: none missing primary_state / progressive_destination / accessibility / print_destination / proof_owner.
- consolidate/retire rows with an unresolved replacement_ref: none (PART B's four consolidations resolve).

---

## Rework A (2026-09-24) — G3 cr-p0 F1–F3 + HJ hj-p0, PART A ledger + reconciliation

Producer: frontend-engineer (rework producer A). Scope: exactly `docs/design/ui-cleanup/P0-RECONCILIATION.md`,
`docs/design/ui-cleanup/disclosure-ledger-a.json` and this report. `disclosure-ledger-b.json` untouched
(producer B). Inputs read: `project-control/tasks/M5-T080.json`, `project-control/reports/M5-T080-G3.md`,
`project-control/reports/M5-T080-HJ.md`, `project-control/directives/D-086-ui-design-cleanup/`, D-082 and
D-083 requirements, assessment §§1–6, 7.8, 11–14.

### IMPLEMENTATION

1. **Ledger A (155 rows)** — rewrote every `accessibility` and `print_destination` cell from source, one
   true statement per row (no shared boilerplate: 150 distinct accessibility cells, max repeat 4; print cells
   repeat only where rows share one surface, e.g. the 28 AD rows + SH-03 on the no-BBL search state).
   Targeted fixes to `assessed_source`/`current_source` (SH-02, ZC-04, M08), `authority` (PE-07, AD15, M07,
   SH-07), `primary_state` (PE-02, PC-04, PC-05, PV-01, ME-05), `protected_meaning` (D-083 citations on 10
   rows), `proof_owner` (139 rows: re-anchors + a phase visibility/announcement proof clause on every L row)
   and `open_question` (51 rows: in-flight flags, P5 decisions, cross-refs, one defect pointer). No mark,
   section, disposition or replacement_ref changed; key set and order unchanged.
2. **Reconciliation** — rewrote §1 (two-step drift + pin-of-record rule + method limit), §2 (route/state
   map: 23 rows, one per route + flag + view, ★ report), §3 (DB-038/043/046/049/050/051 + head-new
   DB-053…056, read at `a57bb8de`), §4 (D-076 checkpoint PASSED), §5 (named fixtures, freshness → PC-04/
   PC-05/PV-01), §6 (counts + anchor list); added §7 (print/accessibility legend, P5-D1…P5-D6, speaking
   regions, kept `role=alert` sites, P5 print-gate recipe) and §8 (in-flight re-pin register).

### Identity / setup (cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t080`)

```
$ git rev-parse --show-toplevel && git rev-parse HEAD && git status --short && git branch --show-current
C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t080
a57bb8dec34129a86e5c9bfe6ea2d2be1f5dfc1d
task/M5-T080-p0-reconcile
```
(status empty = clean tree at start.)

### Per-finding closure (PART A + reconciliation)

| Finding | Status | Rows / sections |
|---|---|---|
| G3-F1 (SH-02 line) | CLOSED | SH-02 `current_source` = `page.tsx:5`; `assessed_source` annotated (assessment cites :6, line 6 is `}` at dc5a763e too). The 10 SR path rows are PART B. |
| G3-F2 PE-07 | CLOSED | authority `exact-copy test …/proposal-editor.test.tsx:83-88`; proof owner the same span. |
| G3-F2 AD15 | CLOSED | authority `PRD 5 (Primary user flow, step 5 …, PRD.md:96)`. |
| G3-F2 M07 | CLOSED | DB-002/DB-032 dropped; authority `exact-copy test …/lot-outline-map.test.tsx:349-360 (asserts 'condominium unit lot') @b56f3d5b`; proof owner same; in-flight anchor note (`:362-373` at a57bb8de). R01/R03/C01/C10/E08/E13/LS-C03 are PART B. |
| G3-F3 D-076 | CLOSED | §4: checkpoint PASSED per D-082-R001. |
| G3-F3 DB-046 | CLOSED | §3: OPEN row; (a)-(f) resolved 251st; (g)/(h) WATCH; (i) public-exposure packet. |
| G3-F3 route map | CLOSED | §2 rows 4, 7, 11, 18: AC\*/M\* on the `/property` search state (`ArchitectEntry.tsx:65-67`, `AddressResolutionScreen.tsx:247`, `AddressConfirmCard.tsx:305`); Continue only links to `/property/confirm` (`:380`). |
| HJ-2 (print, PART A) | CLOSED for PART A | All 155 print cells: 3 printed (SH-01 via root-layout footer — not the appendix; SH-09 when present; LC22 via format.ts), 3 split/partly (SW-01, SW-02, SW-03), 11 not applicable, 1 not a designed print element (SH-15), 137 not printed today. Real gaps recorded as P5-D1 (A01/LS-P01 env banner + SH-02), P5-D2 (A03 footnote, print and ≤700px), P5-D3 (SH-08 alias/draft/borough), P5-D4 (no proposal print), P5-D5 (SW-01 scope), P5-D6 (SW-02 association label). PART B rows (HJ-1) are producer B's. |
| HJ-5 (a11y, PART A) | CLOSED for PART A | All 155 cells name role/name, keyboard/touch path, speaking region, alert vs status, focus rule. Kept alerts: SH-05/SH-09 (AnalysisIdentityNotice), SH-10, SH-14, PE-07, PC-06, ME-06, ME-09…ME-16, DR-07, DR-11…DR-22. SH-01 = contentinfo landmark, not a control. Same-event duplicates recorded (PE-07, PC-06, ME-03, ME-04/ME-07, ME-06, DR-06/DR-07). Region table in §7. |
| HJ-6 | CLOSED | ME-05 primary state pins the heading and the qualifier; proof owner records that the qualifier is pinned by no test. D-083 cited (protected_meaning) on ME-01…ME-05, ME-07, ME-08, DR-01, DR-06, DR-10; D-083-R004 on ME-03, ME-08, PC-05, PV-01. PC-05/PV-01 default to failed/unchecked with "Incomplete - N could not be checked". |
| HJ-7 | CLOSED | §2 rebuilt; AD\* and the no-BBL search state included; ★ view=report. |
| HJ-8 | CLOSED | §5 freshness → PC-04/PC-05/PV-01 (+ "Changed since check" in their primary states); PE-02 cross-references PE-10. |
| G3-A1 / HJ-10 | CLOSED as instructed | Flags kept on DR-01…09 and ME-01…17 (pinned b56f3d5b, observed a57bb8de locations recorded); flags extended to DR-10…23 (rendering component + proof file) and M01/M02/M05/M07/M11 (proof anchors). §8 lists copy that will need rows at re-pin; no rows added now. |
| G3-A5 | CLOSED | DB-038 remaining = (a)/(d)/(e); DB-043 note (checkpoint passed, packet not contracted, (a) closed); false "byte-identical" claim removed; fixtures named in §5; ZC\*/ME\* placement corrected. |
| G3-A3 (SH-07) | CLOSED | authority `implementation-only prose`; proof owner says no test pins the card (architect-workspace.spec.ts:126 covers only the survey-enabled inbox). |
| G3-A4 (ZC-04, M08) | CLOSED | ZC-04 `current_source` 30-47 (file has 49 lines); M08 `694-702` (text on 699). |
| HJ-11 | PARTIAL | PV-01…PV-03 re-anchored to `proposal-editor.test.tsx:91-103` / `:40-42` (no variations spec exists); M05 to `:418`; SH-01 print corrected; every L row now names a phase visibility / announcement / name / silence proof (D-086-R003). Rows still citing a whole test file keep that; exact lines are the owning slice's G0 job. |

### Commands run (cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t080` unless stated; outputs verbatim, trimmed where noted)

```
$ git diff --stat b56f3d5b a57bb8de -- apps/web
 11 files changed, 866 insertions(+), 107 deletions(-)     [list in P0-RECONCILIATION §1]
$ git log --format='%h %s' b56f3d5b..a57bb8de -- apps/web/e2e/proposal-editor.spec.ts
006f3589 M5-T079 unit (DB-050 max-surface hardening)
$ git log --format='%h %s' b56f3d5b..a57bb8de -- apps/web/src/components/address/__tests__/lot-outline-map.test.tsx
5879cdfa M5-T078 unit (DB-049 drawing-surface disclosure + a11y)
$ git diff -U0 b56f3d5b a57bb8de -- apps/web/src/components/address/__tests__/lot-outline-map.test.tsx | grep '^@@'
@@ -212,0 +213,10 @@ / @@ -247,2 +257,5 @@ / @@ -530 +543,8 @@ / @@ -713,0 +734,6 @@ / @@ -741 +767,5 @@ / @@ -785 +815,7 @@
$ git show HEAD:apps/web/src/app/page.tsx | sed -n 5,6p           (dc5a763e identical)
  return <div className="architect-shell"><header className="architect-topbar"><span class…
}
$ git show HEAD:apps/web/src/components/architect/__tests__/proposal-editor.test.tsx | sed -n 83,88p
  it("blocks a bad-charset draft client-side, naming the route constant, without sending", () => {
  …
    expect(screen.getByTestId("draft-problems")).toHaveTextContent("_LABEL_CHARSET");
    expect(screen.queryByTestId("proposal-check-summary")).toBeNull();
$ git show HEAD:PRD.md | sed -n 96p
5. System displays possible matches if ambiguous.
$ git show b56f3d5b:apps/web/src/components/address/__tests__/lot-outline-map.test.tsx | sed -n '349p;357p'
  it("condo unit lot: honest-empty state names the reason; no map is constructed", async () => {
    expect(empty.textContent).toContain("condominium unit lot");
$ git show HEAD:apps/web/src/components/address/__tests__/lot-outline-map.test.tsx | sed -n '362p;370p'
  (same two lines)
$ git show b56f3d5b:…/lot-outline-map.test.tsx | sed -n 418p      and   git show HEAD:… | sed -n 431p
  it("single_lot without WebGL: honest fallback, +/-20 ft copy kept, maplibre-gl NEVER imported/constructed", …
$ git show HEAD:apps/web/src/components/address/LotOutlineMap.tsx | sed -n '694p;699p'
          {view.outcome === "no_outline" ? (
                  : "No parcel outline is drawn: the official source returned no lot for this BBL. …
$ git show HEAD:apps/web/src/components/architect/ZoningContextControl.tsx | wc -l
49
$ git show b56f3d5b:apps/web/src/components/architect/__tests__/max-envelope-panel.test.tsx | sed -n '18p;122p;275p'
  "These are rules-derived preliminary development limits for this lot — not a maximum permitted building.";
    expect(await screen.findByRole("heading", { name: "Preliminary development limits" })).toBeInTheDocument();
  it("no changed panel/lib source asserts an unqualified 'maximum allowed building' or 'demonstrated maximum'", () => {
$ git grep -n "not a maximum permitted building" b56f3d5b -- apps/web
  MaxEnvelopePanel.tsx:264 (lead) · max-envelope-panel.test.tsx:18 (server-disclosure fixture) ·
  max-envelope-api.test.ts:47 (fixture) · max-envelope-api.ts:587 (announcement)   → the lead is unpinned
$ git show HEAD:apps/web/src/components/compare/__tests__/property-error-boundary.test.tsx | sed -n 96p
    expect(card.closest('[role="alert"]')).not.toBeNull();
$ git show HEAD:apps/web/src/components/architect/__tests__/proposal-editor.test.tsx | sed -n 42p
    expect(screen.getByTestId("variations-ephemeral")).toHaveTextContent("this browser session only");
$ git show HEAD:apps/web/e2e/architect-workspace.spec.ts | sed -n 126p
    if (view === "documents") await expect(page.getByTestId("inbox-empty")).toBeVisible();
$ grep -rn 'id="bbl-input"\|bbl-input\b' apps/web/src apps/web/e2e --include=*.ts* | grep -v __tests__
  AddressOutcomeCards.tsx:100 (href="#bbl-input") · PropertyLookup.tsx:286,290 (the only id) · e2e keyboard/a11y specs (legacy)
$ grep -rn "@media print" --include=*.css apps/web/src
  app/property/architect.css:140, :187, :188   (no other print rules)
[summary, not verbatim] source reads with sed/grep/git show for every accessibility/print cell: ArchitectEntry, ArchitectShell,
  ReportView, architect.css, layout.tsx, page.tsx, ProposalEditor, ProposalCheckReport, ProposalVariations,
  MaxEnvelopePanel/max-envelope-api/ProposalOutlineDraw/ProposalOutlineMap @b56f3d5b (extracted with git show
  to the session scratchpad), LotOutlineMap, AddressResolutionScreen, AddressAutocomplete, AddressForm,
  AddressOutcomeCards, SuggestionChooser, AddressConfirmCard, ConfirmScreen, PropertyLookup, ScenarioWorkspace,
  DevelopmentLimits, ZoningContextPanel/Control, ZoningSection, AdditionalZoningFlags, OutcomeAnnouncer,
  error.tsx, ScenarioFailureStates)
```

Self-check (the required completeness enumeration + json.tool):

```
$ sed -n '57,923p' docs/UI_DEEP_DIVE_ASSESSMENT.md \
  | grep -oE '^\|[[:space:]]*(SH-|PE-|DR-|PC-|PV-|ME-|SW-|ZC-|LS-P|LS-C|LS-E|LS-F|LS-T|AD|AC|LC|SR|DB|M|A|C|F|E|R)[0-9]+' \
  | sed -E 's/^\|[[:space:]]*//' | sort > <scratchpad>/enum.txt
$ wc -l < enum.txt ; uniq -d enum.txt | wc -l
381
0
$ python <scratchpad>/check_a.py
enumerated total 381 | enumerated PART A 155 | ledger-a rows 155
ids appearing more than once in ledger-a: []
in enum not ledger: [] | in ledger not enum: []
per family: {'AC': 11, 'AD': 28, 'DR': 23, 'LC': 22, 'M': 13, 'ME': 17, 'PC': 6, 'PE': 10, 'PV': 3, 'SH': 15, 'SW': 3, 'ZC': 4}
rows with exact 18-key set/order: 155
L rows 138 | empty required cells: []
dispositions: {'keep': 16, 'convert': 139} | consolidate/retire without replacement_ref: []
marks changed vs HEAD: []
$ python -m json.tool docs/design/ui-cleanup/disclosure-ledger-a.json > /dev/null; echo "exit=$?"
json.tool disclosure-ledger-a.json exit=0
$ python -m json.tool docs/design/ui-cleanup/disclosure-ledger-b.json > /dev/null; echo "exit=$?"
json.tool disclosure-ledger-b.json (untouched) exit=0
```

Apply-script summary (the script asserts the key order, unchanged marks/sections/dispositions/refs, the five
L cells non-empty, and that neither old boilerplate sentence survives):
`rows 155 distinct accessibility 150 max repeat 4 | distinct print 69 max repeat 29 | changed cells per key
{accessibility 155, print_destination 155, proof_owner 139, open_question 51, protected_meaning 10,
primary_state 5, authority 4, current_source 3, assessed_source 1}`.

### Evidence status

- [OBSERVED] every cited span, anchor, role, live region and print rule named in the cells, read at
  `a57bb8de` (or at `b56f3d5b` for the in-flight files) with `git show` / `grep` / `sed`.
- [BLOCKED] browser, print and screen-reader behaviour (thin client: no npm/npx/node). The print and
  accessibility cells are source-grounded, not observed in a browser. Harvest recipe for P5: extend
  `apps/web/e2e/architect-workspace.spec.ts:185-214` (already emulates print on view=report) with one
  visibility assertion per "printed today" row and one per P5-D decision; for accessibility, a Playwright
  journey per surface asserting the named live-region text changes once per state change.
- [PREDICTED] none claimed.

### Meaning preservation

Docs only: no user-visible string changed (no before → after pairs). No mark weakened (script check:
`marks changed vs HEAD: []`). No disclosure, gap or review meaning removed from any row; the edits add
destinations, obligations and gaps.

### DISCOVERIES (D-069; route to the orchestrator, not fixed here)

1. **Unreachable legacy branches.** `PropertyLookup.tsx:165` (RuleEvaluationPanel) and `:265`
   (AddressResolutionScreen, legacy "Address lookup" copy) render only when `ruleEvalEnabled` is true, but
   the only mount passes `false` (`app/property/page.tsx:41` returns ArchitectEntry when the flag is on;
   `:45` renders PropertyLookup only when it is off). They render in tests only. Route: P2 / legacy-route
   retirement decision.
2. **Dead "Look up by BBL instead" link on the architect route (source-grounded defect).**
   `AddressOutcomeCards.tsx:100` links to `#bbl-input`, which exists only in PropertyLookup
   (`PropertyLookup.tsx:290`). On the reachable architect search state the BBL field is `#architect-bbl`
   inside a closed `<details>` (`ArchitectEntry.tsx:68-73`), so the link should move neither scroll nor focus
   and leaves the BBL form closed. `address-resolution.test.tsx:459` pins only the href. Needs a browser
   check and a P2 fix (AD14 open_question).
3. **Tab title does not follow the architect view.** Flag-on navigation always uses `/property?view=…`
   (`navigation.ts:13-17`), so the Report and Proposal views are titled "Property lookup — NYC Buildability
   (internal)". Route: P2/P3 (SH-15).
4. **ME-05 qualifier unpinned.** "…not a maximum permitted building" in the limits lead
   (`MaxEnvelopePanel.tsx:262-264` @b56f3d5b) is asserted by no test; the copy wall only forbids "maximum
   allowed building". Route: M5-T079 rework or P4.
5. **Landing environment badge hidden at ≤700px** (`architect.css:138` applies on `/`). Folded into P5-D1.
6. **Map container name may not be exposed.** `aria-label` sits on a role-less `<div>`
   (`LotOutlineMap.tsx:643-646`); ARIA 1.2 does not name generic elements. Route: next lot-outline-map touch
   (DB-049 (g)/(h) class).
7. **Same-event double announcements** (alert card + polite announcer: PE-07, PC-06, ME-06, DR-07/DR-11…22;
   two announcers for one adopt click: ME-04/ME-07 + PE-08). DB-049/DB-044 class; route P4 after M5-T078.

### Not closed (with reason)

- PART B items (G3-F1 SR paths; G3-F2 R01, R03, C01, C10, E08/E13, LS-C03; HJ-1, HJ-3, HJ-4, HJ-9; PART B
  halves of HJ-2/HJ-5; G3-A3/A4 PART B rows): producer B's file, out of my scope.
- HJ-10 rows for new in-flight copy: deliberately not added (orchestrator instruction; copy still changing);
  listed in reconciliation §8 for the re-pin.
- HJ-11 exact test lines for rows that cite a whole test file: left to each owning slice's G0; every L row
  now carries a phase proof obligation.
- Browser/print/AT observation: [BLOCKED] by the thin-client rule (recipe above).

### Assumptions

- Pin of record: in-flight rows stay at `b56f3d5b` (the orchestrator said to keep the flags and re-pin after
  the lanes land); all other rows are byte-identical at `a57bb8de`.
- D-083 is an owner directive, not one of the packet's authority classes, so it is cited in
  `protected_meaning` / `primary_state`, and each `authority` cell keeps one packet class.
- "Printed today" means inside the brief print tree or outside every print-hiding rule on view=report.

### Requested status

`awaiting_gate` — delta check of the rows and sections in the closure table (G3 cr-p0; HJ hj-p0 for the
PART A print/accessibility cells), once producer B's PART B rework is harvested.

---

## [ORCH-HARVEST] Rework round: PART B return (verbatim) + cross-file completeness check

Rework producer A (wt-m5t080, commit 8a9a9f38) wrote its rework section above; its commit is cherry-picked as 6644f93f. Rework producer B (wt-m5t080b, commit 6190e69c, one file) is cherry-picked as d5209b4e. Every file is a MATCH by git blob identity. PART B returned its evidence as its final message; the orchestrator appends it here byte-for-byte, extracted from the producer's own transcript. The cross-file check the packet assigns to harvest follows it.

### Rework PART B return (verbatim)

M5-T080 rework, producer B (Part B ledger). Requested status: awaiting_gate.

COMMIT
- The commit is 6190e69c70ff6f89e9d8112d785b913938406bc2. Its parent is a57bb8dec34129a86e5c9bfe6ea2d2be1f5dfc1d.
- Branch task/M5-T080-p0-reconcile-b, in worktree C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t080b. Not pushed.
- The commit changes one file: docs/design/ui-cleanup/disclosure-ledger-b.json (1016 lines added, 1016 removed). The committed blob is 077754438f479327c53f05fad10fdd0bdfb1bf14.
- The gitleaks pre-commit hook reported no leaks. After the commit the worktree is clean.
- Start checks: the toplevel was wt-m5t080b, HEAD was a57bb8de and the tree was clean.
- Pin: every Part B source file has zero diff between dc5a763e and a57bb8de. The only apps/web changes in that range are the M5-T078/T079 files, which Part B does not cite.

CLOSURE LIST
- G3-F1: fixed the paths in SR11, SR52, SR53, SR54, SR55, SR56, SR58, SR59, SR60 and SR61, in both assessed_source and current_source, to apps/web/src/lib/surveyReview/{model,labels,errorCopy}.ts. SR11's second path is now a full path too. I read every span at HEAD and each one shows the stated text.
- G3-F2: I checked every anchor at HEAD before writing it.
  - R01: workspace.test.tsx:56-85 and e2e architect-workspace.spec.ts:185-213. Gap recorded: no test pins the BBL/generated line or "not saved automatically".
  - R03: source-links.test.tsx:35, used for the report appendix through :60-68.
  - C01: condo-resolution-display.test.tsx:410-419, 548-563 and 781-792.
  - C10: condo-resolution-display.test.tsx:435-455.
  - E08: now "implementation-only prose" plus a named gap. No test covers the evidence index.
  - E13: now carries the workspace.test.tsx:36-50 pin.
  - LS-C03: compare-entry.test.tsx:42-76 and e2e compare-journey.spec.ts:147-150.
- HJ-1: the 16 rows (LS-P03 to LS-P15, LS-C17, LS-C18, LS-C19) now say "Prints in the property brief today; must stay in default print. Shared primitive (architect + legacy)". Each names its ReportView mount line and is routed to the P5 print gate.
  - LS-P10: the grouped fields sit behind a button that print hides, so paper shows neither the fields nor the "Show n more" cue.
  - LS-P15: the nested JSON disclosures are not raw, so the full JSON prints by default.
  - The false "legacy route, no print" line is corrected on all 72 LS rows:
    - LS-P01 is in the architect shell but hidden in print.
    - LS-C09 to C14 and C20 to C23 are shared with the architect scenarios view but not printed.
    - LS-E03 to E11 are shared with the architect zoning view.
    - LS-F cards print above the brief on the report view.
    - Legacy-only rows keep an accurate legacy-only line.
- HJ-2 (touches Part B): A01 and A03 now say "not printed today" and each opens a P5 decision. E10 is linked to the SH-08 identity-alias decision.
- HJ-3 (E12): the reason (CalculationEvidence.tsx:43) and fallback_direction_note (:45) stay in the readable tier, which prints by default. Only internal IDs and the CapturedRecord go to raw. The proof owner is report-view.test.tsx:146-187 and :214-276, both CalculationEvidence tests. A gap is recorded: no test proves the note stays in the default printout.
- HJ-4:
  - LS-C06 keeps both flags beside the value.
  - LS-C27's replacement_ref is now "LS-C06 + LS-C05", with professional_review_required mapped to a visible state.
  - A06's primary state names the readable per-cap status (DevelopmentLimits.tsx:15-21, :39).
- HJ-5: every Part B row now has an accessibility cell describing that row. For each L row whose state changes, it names the speaking region, alert or status, and the focus rule. Static rows say plainly that nothing speaks and focus does not move. Existing alerts are kept and named:
  - AnalysisIdentityNotice:72 (A15)
  - CorrectionForm:90, :146, :151
  - ReasonForm:67, :72
  - FocusedItem:166
  - ConfirmDocumentPanel:180
  - app/property/error.tsx:37 (LS-T15)
  - app/dashboard/error.tsx:19 (DB21)
- HJ-9: survivors are named.
  - A03: SH-01 footer plus the per-result status. The nav footnote is ruled out.
  - A15: first paragraph as the alert, with the second paragraph's clauses moving into the Why detail.
  - E03: A04 for staleness; E11 and SH-01 for the review line.
  - LS-C22 now keeps the "missing (n)" count, the named blockers and the empty state from LS-C23.
- HJ-11: every proof_owner has line anchors, or a named gap with its later phase. All 206 L rows carry a visibility obligation. SH-01 is left to Part A.
- G3-A3:
  - Every authority cell now uses exactly one class: 145 exact-copy test, 47 returned contract, 28 implementation-only prose, 6 PRD.
  - Every returned contract names a real schema or type.
  - B-001 is no longer called a reviewer finding (A01, LS-P01, DB01).
  - The UI-only copy rows DB09, DB21, SR21, SR47 and SR57 were reclassified.
  - A05 now uses :457-466 and LS-C05 uses :125-133.
  - SR24 is now a named gap.
- G3-A4: all spans use full paths. The disjoint spans for LS-T02, LS-T04 and LS-T06 are restored. The LS-F rows, LS-T11, DB05 and DB08 are normalized.

COUNTS AND SELF-CHECK OUTPUT
- Enumeration: python selfcheck.py (scratchpad) takes every table row in assessment lines 417-923 whose first cell starts with an id.
  - enumerated 226 unique 226
  - per family: A 15, C 11, DB 22, E 16, F 8, LS-C 28, LS-E 11, LS-F 17, LS-P 16, LS-T 15, R 5, SR 62
  - ledger-b rows 226 unique 226; missing from b []; extra in b []; dup in b []; overlap with a []
  - all rows exact key list True
  - L rows 206; empty L fields []
  - consolidate/retire: LS-C08->LS-C24, LS-C23->LS-C22, LS-C27->"LS-C06 + LS-C05" (both ids resolve), SR27->SR12
  - replacement_ref on other rows []
  - mark, disposition, phase, section and drift changed: [] for each
  - non-ascii chars 0
  - fields changed: authority 225; accessibility, print_destination and proof_owner 226 each; assessed_source and current_source 33 each; trigger 16; progressive_destination 10; open_question 10; primary_state 7; protected_meaning 3; replacement_ref 1
- json.tool: `python -m json.tool docs/design/ui-cleanup/disclosure-ledger-b.json` exited 0, run before and after the commit (cwd wt-m5t080b).
- Reference checker (merge.py): 2003 path:line references across all cells, 0 bad. It checks that each path resolves to one file at HEAD and each line is inside the file. It does not check content.
- Span content check (spancheck.py): 213 of 226 current_source spans matched an assessment text probe automatically. I read the other 13 by hand and they are correct: C05, C06, C09, C10, C11, LS-P03, LS-P16, LS-F16, LS-F17, LS-T07, SR52, SR53, SR57.

NOT CLOSED, OR JUDGEMENT CALLS
- The HJ-1 rows keep phase P3 for the screen work. The print duty is routed to P5 in print_destination and proof_owner. Change phase to P5 if you prefer.
- replacement_ref "LS-C06 + LS-C05" uses a " + " separator. Any checker has to split on "+".
- Short ":NN" references inside prose were checked by reading, not by script.
- The 62 SR rows share one print sentence, and the 14 LS-F rows share one accessibility description per surface. In both cases the fact is the same for every row.
- Web tests were not run (thin client). Every claim comes from reading source at a57bb8de.
- Out of my scope and left to producer A: SH-02, PE-07, AD15, M07, SH-01's print note, and P0-RECONCILIATION.md.

DISCOVERIES (for DISCOVERY_BACKLOG; none fixed)
1. In the architect workspace a scenario failure is never announced. Only the rule-eval announcer (ArchitectEntry.tsx:168) and the property announcer (:220) exist, and scenario failures render at :190.
2. When a property fails in the architect workspace, focus does not move to the failure heading (ArchitectEntry.tsx:239-242).
3. On the report view, analysis failure cards and their Retry buttons print above the brief. They sit outside .architect-report (:190-191), and architect.css:140 only hides buttons inside it.
4. Full JSON prints by default for every fact in the brief (ProvenanceDisclosure.tsx:101-110).
5. The grouped missing fields and their cue disappear on paper (MissingInputsSection.tsx:76-90).
6. The spatial evidence (F04) and the exact rule-evaluation server disclaimer (LS-E05) are not in the default printout.
7. An identity mismatch is spoken twice: once by the alert and once by the rule-eval announcer (ArchitectEntry.tsx:95-96).
8. An incomplete evaluation uses two status regions (DevelopmentLimits.tsx:25 and ArchitectEntry.tsx:97).
9. The dashboard drawer does not return focus to its opener on close (DashboardApp.tsx:101).
10. The survey inbox never focuses its failure heading (ReviewInbox.tsx:89).
11. The "not authoritative" meaning of the AI-drafted label is in a tooltip only (FactRow.tsx:43).
12. The legacy compare announcement leaves out an identity mismatch (scenario-api.ts:438-445).
13. Several L rows have no pinning test. Each is marked "gap" in its proof_owner, for example A04, A12, E08, LS-P12, LS-P13, SR05 and DB21.

MEMORY
I added one project-memory note, project_architect-print-and-a11y-facts.md, with a MEMORY.md pointer in the frontend-engineer agent-memory directory of my harness worktree. It holds stable print and accessibility facts only, no task status.

END-OF-REPORT

### Cross-file completeness check (orchestrator, at the harvested head)

- Enumeration over docs/UI_DEEP_DIVE_ASSESSMENT.md lines 57-923 (every table row whose first cell starts with an inventory id): 381 ids, 381 unique.
- disclosure-ledger-a.json (155) + disclosure-ledger-b.json (226) = 381 rows, 381 unique; missing from the ledgers: none; extra in the ledgers: none; duplicates: none.
- Every row carries exactly the same 18 keys: True.
- 344 L-marked rows; missing primary_state / progressive_destination / accessibility / print_destination / proof_owner: none.
- consolidate/retire rows with an unresolved replacement_ref (split on '+'): none.
