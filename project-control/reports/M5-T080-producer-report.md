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
