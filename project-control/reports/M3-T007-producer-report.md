# M3-T007 producer report — zoning-law library, second pass (documents only)

Producer: legal-corpus-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ad76f4537916bbd49`.
Contract base: `680cbe779618ad20c3f895c11c1dfb603c5096c1` (`git reset --hard` confirmed at setup).
Unreviewed draft throughout (ADR-007): no result is labelled Verified; no option is called
compliant, buildable, feasible, optimal or preferred; no eligibility is decided; no floor area,
height, unit count or parking count is computed for the benchmark lot. All ten research returns
(HA, HB, HC, HD, HE, HF, HG, HS, HX1, HX2) were in the folder before commit and are folded in; the
folder was re-listed before writing and before commit.

## What each file holds

- `options/README.md` — what the folder is; the unreviewed-draft label (ADR-007, first-pass
  wording); the limits; one line per option family with its still-open questions; the benchmark
  transit-zone recorded value; a six-item "Questions for the owner" list in plain sentences.
- `options/option-02-03-affordable-and-senior-housing.md` — options 2/3; the 23-22/23-432/23-52
  changes; the correction that the UAP/affordable rules moved to Article II Chapter 7 (27-111ff)
  and 23-154 is only the Offsite-Option rate (still access-blocked).
- `options/option-05-shops-with-residences.md` — option 5; the use correction (32-161, not 32-131);
  32-421 floors; 33-121 overlay FAR 2.00; 35-31 greatest-single-use cap; 35-32 does not reach R6B;
  overlay-depth location (76-131/76-141) with the actual line unread.
- `options/option-06-07-community-facility.md` — options 6/7; 24-11 CF FAR 2.00 / coverage 80-60;
  24-111 defers to 24-11 for R6B; the corrections that 24-162 and 35-33 exclude R6B; the 24-04 →
  23-43 height routing; CF yards.
- `options/option-08-split-lot.md` — option 8; the two readings kept apart (A.1 subdivide / A.2 two
  buildings on one lot / B district-boundary split); the 36-64 loading-pointer correction; the
  sample by page pointer; the overlay-edge question left open.
- `options/option-09-shared-housing.md` — option 9; "shared housing" = rooming units; the 23-51
  density-exclusion correction; use permission 22-12/22-121/32-121; the outside-ZR occupancy gate.
- `options/option-10-parking-and-transit-zone.md` — option 10; the transit-zone recorded value
  (Outer); the 66-11 correction; the parking/loading/bicycle chain; a one-line applicability
  statement per option 1-11 (DB-180).
- `options/option-11-combinations.md` — option 11; the greatest-single-use FAR ceiling; the
  compatibility table; the capture-state correction; the note that option 11 currently reduces to
  the single best qualifying-housing program.
- `options/research-log.md` — every search (producer's and the ten helpers'), with results,
  missing items and next steps; the 23-154 and HMC access blocks recorded.
- `options-sections.md` — a pointer + second-pass-state block appended to §2, §3, §5, §6, §7, §8,
  §9, §10, §11; nothing else in the file changed.

## Acceptance scenarios S1-S8

- **S1 (section rows):** every cited section carries id, title, official URL, last-amended date,
  capture state (snapshot file from the folder listing, or NOT CAPTURED) and handled state (rule
  file, or NOT HANDLED). Capture states were taken from a listing of `docs/research/zr-snapshots/v1/`
  (not an index); handled states from `services/api/app/rules/rulesets/`. MET.
- **S2 (reading):** each file states the applicable rule, definitions, exceptions, overlay/special-
  district effects, measurement basis, zoning-lot scope and the lot facts needed with a possible
  source; each unsure point says "not sure" with a next step. MET.
- **S3 (options-sections.md items):** each NOT-CAPTURED / not-sure item for options 2-11 is
  restated as resolved (with the official page/snapshot checked this pass) or still open with the
  exact missing item and next step; none dropped. MET.
- **S4 (option 8):** the two readings are kept apart, each with its sections; the sample is given
  by page pointer only (pp. 2, 5, 82-87; no copied text, no figures); the "which reading" question
  stays open. MET.
- **S5 (option 10):** one parking/loading/bicycle applicability line for every option 1-11, naming
  the deciding sections; transit-zone membership stated as a recorded value (Outer Transit Zone)
  with its source (reference `step-p5-worked#transit-zone-value`; dataset `6ztr-wgff` 2025-12-16).
  MET.
- **S6 (research-log):** every search has source, query/URL, found/not found/access blocked, the
  missing item and next step; the 23-154 (HTTP 403) and HMC §27-2004 (HTTP 403) blocks are recorded,
  never evaded. MET.
- **S7 (diff):** `git status --porcelain` and `git diff --stat HEAD` touch only the 11 allowed
  paths; at most one short quote per cited item; no third-party text copied; no code/rule/capture/
  evidence/review-register file changed. MET.
- **S8 (status words):** every file carries the unreviewed-draft label; the only
  Verified/compliant/buildable/feasible/optimal/preferred hits are inside the denial/label block,
  plus README's "Captured ≠ handled ≠ verified" and "professional verification" (both denial/
  definitional). No eligibility decided; no benchmark figure computed. MET (see the check output).

## Corrections carried, and how each was checked by the producer

1. **Option 5 use: 32-161 (UG VI) is the shops use; 32-131 is UG III community facilities.**
   Checked against the captured snapshots `zr-32-161` (title "Use Group VI – general use
   allowances"; C2 column permits UG VI retail) and `zr-32-131` (title "Use Group III – general use
   allowances").
2. **36-64 is a loading-berth pointer, not a general rule.** Checked against `zr-36-64` body:
   applies Article VII Chapter 7 only "whenever a #zoning lot# is divided by a boundary between
   districts having different requirements for #accessory# off-street loading berths".
3. **66-11 is not the transit-zone definition (the 12-10 terms are).** Checked against `zr-66-11`:
   title "Definitions", Article VI Chapter 6 (TOD), last amended 8/14/2025.
4. **23-51 takes rooming units out of the density rules.** Checked on the official page (WebFetch,
   HTTP 200, 12/5/2024): "the provisions of this Section shall not apply to #rooming units#".
5. **35-33 and 24-162 exclude R6B.** 35-33 checked against `zr-35-33` ("In C1 and C2 Districts
   mapped within R6 Districts without a letter suffix, and in R7-1 Districts"). 24-162 checked on
   the official page (WebFetch, HTTP 200, 12/5/2024): "In the districts indicated, except R4-1,
   R4A, R4B, R5D, R6A, R6B and R6D Districts…".

Additional producer checks: R6B FAR 2.00/2.40 (`zr-23-22`); R6B heights 30/45/55 std and 45/65
qualifying (`zr-23-432`); 33-121 R5D/R6B row A/B/C = 2.00 (`zr-33-121`); 35-31 greatest-single-use
cap (`zr-35-31`); 35-32 and the "qualifying residential site" term list R1-R5 only (`zr-35-32`,
`zr-12-10-qualifying-residential-site`); 27-111 defines UAP/MIH/regulatory-agreement and cites
23-154/23-22/23-432 (official page); 24-11 R6B CF FAR 2.00 / coverage 80-60 (official page). The
settled R6B reference cases (`docs/reference-cases/R6B/cases/`) were cited for the points they
settle (transit-zone value; the mixed-use greatest-FAR cap and shared-area rule; 34-111 exceptions
do not reach R6B; qualifying-residential-site not R6B; dwelling-unit factors; suffix inheritance).

## Helper statements the producer could not independently confirm (kept marked)

- §23-154 verbatim text/title — access blocked (HTTP 403 on WebFetch and the documented
  browser-UA GET fallback); kept NOT CAPTURED / access-blocked.
- HMC §27-2004 rooming-unit text and NYC Intro 1475-2025 committee status (HE) — HE's amlegal fetch
  was HTTP 403 and the legistar id guess failed; kept as pointers, wording not confirmed.
- The "select commercial overlays" membership of C2-2 (32-421) — HX1 could not read the 12-10 term
  verbatim; kept not sure.
- The single ZR rule governing a mixed-building rear yard (33-26 vs a residence-district
  rear-yard-equivalent for the whole building) — HX1 could not verbatim-confirm one governing
  cross-reference; kept not sure.
- The actual mapped C2-2 overlay line at the lot — HX2 recorded the 76-131(b) 150-ft default but
  could not read the zoning-map sheet / ZoLa / NYCO geometry; kept NOT KNOWN, nothing assumed about
  coverage.
- Whether a C1/C2 overlay triggers the same commercial parking numbers as a stand-alone district
  (HF) — no overlay-applicability clause read; kept not sure.
- The 24-xx community-facility section bodies, the 77-xx bodies, 22-1xx use sections, 23-371/23-35
  court group, 25-30+ CF parking and the 12-10 "Transit Zone, Inner" term are all NOT CAPTURED (read
  live by helpers but no snapshot); each carries a capture next-step.

## Findings outside my files (non-editable; NOT changed)

1. `docs/zoning-law-library/benchmark-r6b-sections.json` — the 32-131 entry's `scope_status` reads
   "followed: option 5/11 (C2-2 retail use permission)" (≈ lines 1458, 1482). 32-131 is Use Group
   III (community facilities); the C2-2 retail/shops use is 32-161 (Use Group VI). Mislabel.
2. `docs/zoning-law-library/benchmark-r6b-sections.json` — the 36-64 notes (≈ line 2078) call it
   "the C-district counterpart". 36-64 is only a loading-berth pointer into Article VII Chapter 7,
   not a general C-district apportionment counterpart.
3. `docs/zoning-law-library/benchmark-r6b-sections.json` — capture flags mark 23-20, 33-12, 33-121,
   35-30, 35-31, 35-32, 35-33 as `not_evaluated`/`missing`, but the snapshot folder shows all seven
   captured (the folder is authoritative; confirmed by HX1). Stale capture flags.
4. `docs/zoning-law-library/coverage.md` — line 53 lists "66-11 (transit-zone definitions)". 66-11
   is Article VI Chapter 6 "Definitions" (TOD; "mass transit station"); the transit-zone definition
   is the 12-10 terms. Line 64 calls 36-64 "the C-district counterpart" (same as finding 2). Line 44
   lists "32-131 / 32-161 (commercial use permission)" — 32-131 is community-facility use, not
   commercial.
5. `services/api/app/rules/rulesets/r6b_dwelling_units.rule.json` — does not encode the 23-51
   rooming-unit density exclusion (HE); applying the 680 factor to a rooming-unit scenario would
   impose a unit cap the law does not. Rule-behavior note for the rule owner; that file is outside
   this task's scope and was not changed.

## Checks (direct exit codes)

- `python3 scripts/lanes/check_lane_paths.py --coverage` → `LANE COVERAGE PASS: 10318 file(s)…`
  exit **0**.
- `git status --porcelain` / `git diff --stat HEAD` → only the 11 allowed paths; exit **0** each.
- Snapshot-existence: every section cited as CAPTURED resolves to a file in
  `docs/research/zr-snapshots/v1/`; the only "MISS" tokens were sections cited as NOT CAPTURED
  (23-154, 23-51, 24-xx, 77-xx), a reference-case row id (`zr-34-111-exceptions`) and a path
  fragment (`zr-snapshots`).
- Rule-file-existence: r6_r12_residential_far, r6b_dwelling_units, r6b_height, r6b_lot_coverage,
  r6b_qualifying_housing_far (and r6b_rear_yard_corner_waiver) all exist under
  `services/api/app/rules/rulesets/`.
- Status-word search: all Verified/compliant/buildable/feasible/optimal/preferred hits are in the
  per-file denial/label block (lines 5-8); README lines 33-34 hold "Captured ≠ handled ≠ verified"
  and "professional verification" (denial/definitional). None is a claim.
- No server started; ports 3000/3001/8000 untouched; no test suite run.

## What I could not check (and why)
- §23-154 and HMC §27-2004 verbatim text — durable HTTP 403 (recorded, not evaded).
- The actual mapped overlay line at the lot — requires reading the DCP Zoning Map sheet / ZoLa /
  NYCO GIS, outside this read-only documents pass.
- The 24-xx, 77-xx, 22-1xx, 23-371/23-35, 25-30+ and 12-10 "Transit Zone, Inner" bodies beyond the
  helpers' live reads — not captured in the snapshot set; capture is owed before any rule cites them.
