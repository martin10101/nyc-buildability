# MVP Agenda — owner working list

**What this is:** the running to-do list from owner conversations. Plain bullets, no narrative.
Orientation only — `project-control/` + git + CI remain authoritative. Nothing here is a task until
it has a packet under `project-control/tasks/`.

**Opened:** 2026-09-10 (owner session, client zoning PDFs 23-21 / 23-22)
**Last updated:** 2026-09-10

---

## A. Decisions made (standing, from owner conversation)

- MVP target = **impress the client**. A lookup that duplicates free ZoLa/PLUTO is not a deliverable.
- Program answers **as-of-right** only. Variances, special permits, rezonings are out of scope and must
  be labeled as out of scope on screen.
- Program outputs an **envelope + constraints**, not a design. It is not AutoCAD. The architect designs.
- Practitioner "tricks" may be encoded, but only labeled as *flags to investigate*, never as cited rules.
- Owner's separate **AMI / tax-abatement program** is a downstream consumer, not an MVP integration.
- Render MCP to be added later, when the owner asks. MCP stays excluded until then.

---

## A1. IMMEDIATE — finished loop output awaiting a gate

**M5-T004 (Compare UI) is BUILT and has never been reviewed.** Found 2026-09-10.

- Producer output complete at `a0bec4eb` on `task/M5-T004-compare-ui`, worktree
  `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t004`, working tree clean.
- **2,353 insertions / 13 files:** compare route + `CompareScreen`, `ScenarioCard`, `ScenarioResult`,
  `CoverageMatrixSection`, `ScenarioFailureStates`, `scenario-api.ts`, `scenario-contract.ts`,
  `scenario-display.ts`, a 279-line test file + fixtures, and the producer report.
- Every path is inside the packet's declared `allowed_paths`. No scope violation.
- **Only G0 is recorded.** No G1/G3/G4/G5, no DCV. It was never gated.
- **No contract drift:** `packages/contracts/` is byte-identical between the packet's branch point
  (`1c8945be`) and current HEAD, so the UI is built against the live scenario contract.
- Branch point is behind current HEAD (M5-T005…T013 landed after), so it needs rebasing onto HEAD
  before the gate wave.
- Cannot be verified locally — no `node_modules` installed anywhere (thin-client policy). Verification
  runs through CI, where `web` and `web-e2e` are both green.

**Action: gate + accept M5-T004 (5 reviewers) BEFORE relaunching the loop.** Would be the 177th accepted.

---

## A2. Build order (current — work top to bottom)

| # | Work | Reuses | Est | Blocked on |
|---|---|---|---|---|
| 1 | R1–R12 flat-district FAR rules | `r5_residential_far.rule.json` shape; engine unchanged | ~1 day | nothing |
| 2 | Overbuilt-lot check (BuiltFAR vs allowed) | PLUTO connector + property profile, both live | ~0.5 day | nothing |
| 3 | Confirm screen + ZoLa deep link + lot outline | `PropertyLookup.tsx` state machine; MapPLUTO geometry connector | ~1 day | nothing |
| 4 | Geoclient connector + address entry | the 5 existing connector patterns | ~1–2 days | one live call to record the fixture |
| 5 | Wide-street determination | ZR 12-10 snapshot (already captured) + lot geometry | unscoped | street-width source not chosen |
| 6 | Dwelling-unit density (max units) | rules engine | ~1–2 days | nothing |
| 7 | ZR corpus text extraction | existing PDF reader + new text profile | unscoped | none technically |

Runs alongside, not in this queue: Next.js RCE fix (owner authorization), `exact-production-install`
diagnosis (deployment correctness), the other three CI failures.

---

## B. Do before any client demo

1. **R1–R12 floor-area rules — flat districts first.**
   - Copy the `r5_residential_far.rule.json` pattern for every district whose FAR is a plain lookup.
   - Covers: all of R1–R4, plus R6A, R6B, R6D, R6-2, R7A, R7B, R7D, R7X, R7-3, R8A, R8X, R8B,
     R9A, R9, R9D, R9X, R9-1, R10A, R10X, R10, R11, R12.
   - Source: ZR 23-21 (R1–R5) and ZR 23-22 (R6–R12), both Last Amended 2024-12-05.
   - Include the second column (qualifying affordable / qualifying senior housing) as a surfaced
     conditional alternative, same as the R5 qualifying-residential-site exception.
   - Est: 1–2 days including tests + independent review.

2. **Wide-street conditional districts — separate task, do NOT fold into item 1.**
   - Affects **R6, R7-1, R7-2, R8**. Their higher FAR applies only within 100 ft of a wide street,
     and applies to *portions* of a lot — a geometry computation, not a lookup.
   - Blocked on a wide-street determination (street width + lot geometry) that does not exist yet.
   - Until it exists these districts must return the lower value with an explicit conditional flag.
     Never the higher value.
   - Est: separate feature; size unknown until the street-width source is chosen.

3. **Address entry (Geoclient).** Owner action: register at api-portal.nyc.gov, subscribe "Geoclient User"
   v2, provide `GEOCLIENT_SUBSCRIPTION_KEY` (blocker B-004). Free. Biggest single demo improvement.

4. **Property confirmation screen** before anything computes:
   - BBL, large.
   - Address **as the city normalizes it**, not as typed.
   - Live link to the city's own ZoLa page for that lot (buildable today, no key needed).
   - Map with the **real lot outline** from DCP geometry — not a Google pin. Pins mislead on corner
     lots and large parcels.
   - Lot area, zoning district(s), borough — the facts every downstream number depends on.
   - Data release date stamps. A recently subdivided lot may not have propagated.
   - Explicit Confirm button. Nothing computes before it. Plus a "not my property" path back to search.

5. **Next.js critical RCE upgrade** (GHSA-p293-qw3h-jr36). Needs owner authorization — the fix version is
   outside the current pinned range, so it is a dependency-policy change. **No hosted demo before this.**

6. **Overbuilt-lot check.** PLUTO already gives `BuiltFAR` and `ResidFAR`. If BuiltFAR is at or above the
   allowed FAR, the lot has no as-of-right development potential. Nearly free from data already read,
   and an extremely common real-world answer. Highest value per hour on this list.

7. **Hand-check batch.** Pick ~15 lots across all five boroughs, compare program output against the
   city's own pages by hand, record results. Cheapest real validation available.

---

## C. Do next (post-demo, pre-production)

- **Height / setback / yards for R6–R12.** Not a number swap. Two different regimes:
  - Non-lettered districts (R6, R7, R8, R9, R10) use height factor / sky exposure plane / open space ratio.
  - Lettered contextual districts (R6A, R6B, R7A, R8A…) use Quality Housing contextual envelopes with
    hard maximum heights and base heights.
  - Different math, not different constants. Weeks, not days.
- **Dwelling-unit density.** ZR sets minimum lot area per dwelling unit, which yields a maximum unit count.
  First real step toward anything unit-based, and toward the owner's AMI program.
- **Split-zone lots.** `SplitZone` is already a PLUTO field we read. A lot in two districts breaks naive math.
- **Zoning lot vs tax lot.** A zoning lot can be several merged tax lots. The program works on tax lots.
  Known limitation; will bite on real assemblage deals. Needs an explicit on-screen statement.
- **Commercial overlays + mixed use.** The `nyco` overlay layer is already connected. Residential,
  commercial and community-facility floor area are separate allowances under a combined cap, and
  community-facility allowance is often the largest. Rules not yet written.
- **Special purpose districts.** `nysp` / `nysp_sd` layers already connected, so the program can already
  detect one. The rules for what they *do* are not written. Current behavior (flag, do not compute)
  is correct and must stay until those rules exist.
- **Mandatory Inclusionary Housing areas.** Needed both for the R8 footnote-2 condition and for any
  "how much affordable is required" answer.

---

## C1. Live defect on an ALREADY-ACCEPTED screen — authored legal claim

Found during the M5-T004 rework (2026-09-11) by fixing the same defect in new code.

- `apps/web/src/components/rule-evaluation/RuleEvaluationResult.tsx:251` renders
  `{rule.effective_from ?? "unknown start"} to {rule.effective_to ?? "present"}`.
- **"present" is an authored temporal claim.** It asserts the rule is in effect *now* when the
  document said nothing. Same class as `minor_portion` defaulting to `false` (already fixed to
  tri-state) and the `"The value above…"` clause (fixed in M5-T004).
- `??` also catches only `null`, not `""`, so a value that cleans to empty renders blank.
- Compare (M5-T004) is now **stricter than rule-evaluation on the same field** — the inconsistency
  is the tell.
- This is on an accepted screen, not a draft one. `RuleEvaluationResult.tsx` was outside M5-T004's
  `allowed_paths`, so the producer correctly did not touch it.

Action: small packet. Apply the `stated()` helper pattern from
`apps/web/src/components/compare/NoScenarioBlock.tsx:22-40` and replace `"present"` with
`"end not stated"`. Check the file for the same `??`-on-provenance pattern elsewhere while there.

---

## C2. Dormant landmine — fires on whatever packet turns scenario assumptions ON

Found by G1 during the M5-T004 re-review (2026-09-11). **Not a defect today. It becomes a
full-screen outage the moment the feature it guards is used.**

- `assumptions[].key` is **caller-supplied and passed through verbatim**. `_normalize_assumptions`
  (`services/api/app/scenario/builder.py:199-202`) accepts any non-empty string as a key with no
  charset normalization.
- The reworked client validator now enforces token-representability on that field
  (`apps/web/src/lib/scenario-contract.ts:367`). A key like `utilization factor` or `far:bonus` is a
  **schema-valid document the client rejects outright** — the whole screen goes to a
  validation-failure card.
- It is dormant only because `services/api/app/api/v1/scenario.py:289` calls `build_scenario(profile,
  rule_evaluation)` without the keyword-only `assumptions` argument, so the list is always empty.
- **The parameter exists precisely to be used** — the contract states "Preliminary scenarios vary ONLY
  via explicit typed assumptions (no hidden utilization/optimization defaults)." So the first feature
  that varies a scenario by assumption trips this.
- **Fix belongs server-side: normalize assumption keys at the source.** Do NOT relax the client check
  — the representability guarantee is what stops a silently-rewritten identifier reaching the screen.

Action: attach this to the packet that first passes `assumptions`, before it is written.

---

## C3. Snapshot digest-convention divergence — blocks M4-T009's test path and one CI test

Found 2026-09-11 while syncing the runtime ZR snapshot bundle (the sync itself was CI-required:
the bundle was missing `zr-23-22` and carried a stale pre-recapture `zr-23-21`).

- The two September captures (`zr-23-21` recapture at `17e8eb78`, `zr-23-22` at `23ca629d`) wrote
  `content_digest_sha256` = sha256 over the **whole canonical-JSON record** (compact, sorted, minus
  the digest field). Verified by recomputation: both match that convention exactly.
- The runtime loader (`services/api/app/rules/snapshots.py::load_snapshot_file`) and **all five
  older snapshots** define the same field as sha256 over `verbatim_excerpt` alone. Every file
  declares the same `zr_section_snapshot/v1` schema — the semantics changed without a version bump.
- Consequence: `SnapshotStore` fail-closes (`SnapshotError: content_digest_sha256 mismatch`) on
  both September snapshots. `tests/rules/test_zr_snapshot_bundle.py::test_default_store_resolves_to_packaged_location`
  is red in CI once the bundle is synced, and **M4-T009's own test suite uses the validating
  loader**, so the in-flight loop's acceptance path is blocked until this is resolved.
- **The captures themselves are sound**: the archived raw HTML (session scratchpad) authenticates
  byte-for-byte against the recorded `raw_html_sha256` for both sections, and every FAR value in
  both structured tables (4 + 25) appears verbatim in that authenticated HTML. Nothing legal is in
  question — this is a checksum-convention defect, not a fidelity defect.
- Note the whole-record convention is *stronger* (it covers `table` and `footnotes`, where the
  legal values live; the v1 excerpt-only digest covers neither) — arguably what v2 *should* be.

Decision needed (owner or a directed packet): either (a) conform the two snapshots to their
declared v1 schema — recompute `content_digest_sha256` = sha256(excerpt), preserving the original
whole-record digest in `notes[]` so nothing is silently lost — or (b) version the schema: bump the
new captures to `zr_section_snapshot/v2` and teach the loader both conventions. (a) is a two-line
evidence correction; (b) is an engine change with its own review. Either way, M4-T009's rule
citations (authored against the current stored digests) must be reconciled at integration.

**RESOLUTION — (a) executed 2026-09-11 by the orchestrator.** CI at `48cd58a5` revealed the true
blast radius once the bundle was synced: ~245 tests red (89 failed + 156 errors) across the entire
rules-engine surface, with the scenario API turning `SnapshotError` into typed 500s — far beyond
the one predicted test, and blocking M4-T009's acceptance path. Both digests recomputed to the v1
convention; the original whole-record values preserved verbatim in each snapshot's `notes[]`.
The same repair exposed a SECOND v1-shape drift in the recapture: `source.section_last_amended`
(read by the loader into citation provenance) had been renamed to `last_amended_machine_readable`/
`_display`, so provenance carried `None`; restored additively, new fields kept. After both fixes:
`tests/rules` + `tests/scenario` 716 passed locally, full 3.11-runnable suite 1692 passed (the
`tests/documents` subset needs CI's 3.12 for PEP 695 syntax). **(b) remains open** as a deliberate
`zr_section_snapshot/v2` upgrade — the whole-record digest covers `table`/`footnotes` where the
legal values live, and excerpt-only does not. M4-T009 citation reconciliation at integration
still stands.

---

## D. Flags the program should surface but currently cannot

Each is a separate mapped data source. None currently connected.

- **Landmarks / historic districts (LPC).** Does not change FAR — changes the *approval path*. Certificate
  of Appropriateness before DOB permits. Can add a year or kill a project. Highest-value flag here.
- **E-designations** (environmental). `EDesigNum` is already in the PLUTO field list we read. Nearly free.
- **Flood zones** (FEMA). Affects ground-floor design and cost.
- **Transit zones.** Affect parking requirements.
- **Waterfront lots.** Separate ZR article entirely.
- **Limited height districts.** `nylh` layer already connected; rules not written.

---

## E. Legal corpus ingestion (owner raised: "why can't it just be parsed?")

- Confirmed: **there is no API for the Zoning Resolution text.** Probed and verified 2026-07-16 — no
  JSON:API, no Open Data dataset. Only server-rendered HTML pages, a ~98 MB complete PDF, and 10 dated
  archive snapshots back to March 2024.
- Owner proposal — a one-time full extraction plus a recurring re-check — is **the right approach and
  matches the existing research recommendation** (portal HTML as ingestion primary, dated PDFs as the
  reproducibility archive). Formalize it as M3 work.
- Value beyond convenience: a parsed corpus makes coverage **computed instead of asserted**. The program
  can state which sections it has rules for and which it does not, instead of relying on a hand-maintained
  matrix. Strongest argument for doing it.
- **A full PDF reader already exists and is accepted** — `services/api/app/documents/extraction/`,
  ~3,500 lines, written from scratch with **zero third-party dependencies** (which is why a
  dependency-list search does not find it). Built under M2-T015; M2-T014 / T015 / T016 are all accepted.
  - Layers: `pdf_lexer` (tokens) → `pdf_objects` (composite objects) → `pdf_xref` (xref/trailer/object
    table) → `pdf_container` (page tree + stream decode) → `pdf_content` (content-stream interpreter,
    paths **and** text) → `vector_pdf_decoder`, plus `routing` and `survey_pipeline`.
  - `pdf_content` already emits **positioned text runs with font size**, which is exactly what is needed
    to reconstruct a table (group runs by y for rows, x for columns).
  - 14 adversarial test fixtures (SVY01–SVY14) including an executable renamed as a PDF and an
    oversize sentinel.
- **Reuse plan for the corpus:** keep the container stack unchanged — it is the hard, done, tested part.
  Add a second **profile** to the content interpreter for document text that *skips* unsupported drawing
  constructs instead of refusing the file. The current doctrine is correctly strict for surveys (an
  XObject, curve, inline image or rotated matrix rejects the whole document); ZR PDFs contain a seal
  image on the cover page and would be refused outright under that doctrine. Bounded change to one
  module, not a rebuild. **No new dependency required.**
- Storage note: the complete ZR PDF is ~98 MB. Thin-client policy (~7 GB free) means work per-article,
  not whole-file.
- Hard limit: parsing produces a **searchable library**, not executable rules. The step from text to
  computable rule stays human-reviewed. Parsing does not remove the G6 gate.

---

## F. Owner's AMI program — real prerequisite chain

The owner's program handles the last step. Everything before it is missing. In order:

1. Envelope / total floor area — **exists for R5 only**
2. Height + setback (the shape) — **R5 only, draft**
3. Floor count and floor plates — **does not exist**
4. Gross-to-net efficiency factor — **does not exist**, and is an assumption, not a law
5. Dwelling-unit count (density rule) — **does not exist**
6. Unit mix (studio / 1BR / 2BR) — **a design and market decision, not a legal one**
7. Which units are designated affordable — **human negotiation, not computable**
8. AMI levels + rent roll — **owner's existing program**

The AMI program is roughly five steps downstream, not one. Do not scope it into MVP. When it does connect,
its output inherits the draft / not-verified label of whatever fed it.

---

## G. Testing — source-of-truth hierarchy

Ranked. Nothing lower may override anything higher.

1. **Zoning Resolution text** on the city's portal, with its Last Amended date. Top authority.
2. **City GIS / ZoLa** for which district a lot is in.
3. **PLUTO** — convenient but derived and lagging. Its `ResidFAR` / `CommFAR` / `FacilFAR` are explicitly
   *exclusive of bonuses* and based on `ZoneDist1` only. A **cross-check**, never the answer.
4. **DOB filings / approved projects** — evidence of practice, not law. One-directional: proves we are not
   too strict, cannot prove we are not too generous.
5. **Our own test suite** — proves the code does what we told it. **Cannot** prove we read the law right.

Open item: automate a PLUTO-vs-rules-engine divergence report. Where our number and PLUTO's differ, either
we caught a bonus or condition PLUTO ignores, or we have a bug. Both are worth knowing.

---

## H. UI / presentation risks (architect's-eye view)

- An architect wants, in this order: (1) is this the right lot, (2) how much can I build, (3) how tall,
  (4) how many units, (5) what stops me, (6) what needs a human. Evidence behind a click, not on the page.
- Current screens are organized around provenance and honesty labels. Correct for defensibility, but they
  read like a compliance document. Risk: the headline number is hard to find at a glance.
- **Never present a maximum as achievable in isolation.** Max FAR, max height and max unit count are
  almost never simultaneously attainable. Present them as constraints the real building must fit inside.
- Open decision: primary user — developer, architect, or broker? Same numbers, three different layouts.
- Open decision: how visually heavy the draft / not-verified labels should be. Too heavy reads unfinished;
  too light is a promise we cannot back.
- Missing and likely to be asked for in a demo: PDF export, saved project, share link. None exist.

---

## I. Owner actions outstanding

- **`GEOCLIENT_SUBSCRIPTION_KEY` — owner HAS the key (2026-09-10).** Setup steps in §J.
- Supabase token — unblocks all persistence and auth (B-001). Note: **the API currently has no
  authentication at all**, which is why every route is flag-gated internal-only.
- Authorize the Next.js RCE upgrade.
- Decide: local demo or hosted link. Hosted requires the RCE fix, auth, and the database first.
- Provide the client's list of practitioner "tricks" — each with its triggering condition and a confidence
  level. To be stored as investigate-flags, never as cited rules.

---

## J. Geoclient key — setup

Two separate needs. Render covers runtime; it does NOT unblock building the connector.

### J1. To build the connector (needed first)

The codebase never invents a city service's response shape — it records a real one and builds against
the recorded bytes. That requires **one live call from a machine holding the key**.

- Windows Settings → search "environment variables" → *Edit environment variables for your account* →
  **New** under **User variables**: name `GEOCLIENT_SUBSCRIPTION_KEY`, value = the key. Reopen the terminal.
- Alternative: a local `services/api/.env` (already gitignored; `services/api/.env.example` documents the
  name with an empty value at line 37).
- The recorded fixture stores the response shape, never the key. Key is never printed or logged.
- **Never paste the key into chat, a commit, or `render.yaml`.**

### J2. To run the deployed API (later, at deploy time)

`render.yaml` already declares it:

```
- key: GEOCLIENT_SUBSCRIPTION_KEY
  sync: false
```

`sync: false` makes Render prompt in the dashboard instead of storing a value in the file.

- **Services already exist:** Dashboard → `nycdf-api` → Environment → Add Environment Variable →
  `GEOCLIENT_SUBSCRIPTION_KEY` = key → Save. Render restarts the service.
  Put it on `nycdf-api` only — never `nycdf-web` (frontend vars can reach the browser bundle).
- **Services do not exist yet** (current state per `render.yaml`'s own notes — nothing provisioned,
  B-002 owner-gated): Dashboard → New → Blueprint → connect `nyc-buildability` → **point at branch
  `candidate/D-024-mrl-option-b`, not `main`** (main is ~900 commits behind). Render reads `render.yaml`
  from the repo root and prompts for every `sync: false` variable.

**Recommendation: do not create the Blueprint yet.** It provisions `nycdf-web`, which still carries the
critical Next.js RCE, and `render.yaml` itself notes the API has no auth and must not be publicly
reachable. Hold until the RCE fix lands and a deploy is actually wanted.

---

## K. Ledger inconsistencies to fix

- `project-control/master_plan.json` M2 summary says M2-T014 / T015 / T016 "remain HELD (owner
  survey-dispatch hold), not accepted." **They are accepted** — present in `state.json.accepted_tasks`,
  their task files say `accepted`, and they are inside the 176 count. Stale prose beside correct data in
  the same file. Fix in the next control pass.
