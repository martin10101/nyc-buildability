# Loop Launch Prompts — NYC Buildability

**Date:** 2026-09-28 · **Suggested path:** `docs/lanes/LOOP_LAUNCH_PROMPTS.md`

**What you do (three things):**
1. Copy these files into a folder called `docs/inbox/` in your repo:
   - `PRODUCT_PLAN_CURRENT_2026-09-28.md`
   - `PARALLEL_BUILD_PLAN_LANES_2026-09-28.md`
   - `COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md`
   - `CC_REEVALUATION_PROMPT.md`
   - this file
2. Start **one** loop and paste Prompt 0.
3. When it reports back, answer its single go/no-go message.

**Everything else is automatic:**
- placing the files at their paths;
- reading every document;
- the code map and the reconciliation;
- file ownership, the automatic file check, shared formats, job lists and the estimate;
- the go/no-go checks;
- creating the five worktrees and starting the five lane loops;
- supervising them.

Do **not** put the competitor's PDF in the repo. It is their material; our notes are enough.

---

## Prompt 0 — Wave 0 bootstrap (ONE loop only)

```
You are the Integrator (Lane C) running WAVE 0 for the NYC Buildability repo
(github.com/martin10101/nyc-buildability). Integration branch: candidate/D-024-mrl-option-b
unless docs/lanes/PARALLEL_BUILD_PLAN.md or the owner says otherwise.

GOAL: turn the plan into a safe parallel build. Read everything, map the code,
reconcile what is done against what the plan requires, set up the lanes, write each
lane's queue, then STOP for the owner's GO. Only one loop runs during Wave 0.

SCOPE OF CHANGES IN WAVE 0:
- Allowed: new files only, under docs/lanes/**, scripts/lanes/** and new contract files
  in packages/contracts; one additive CI step; lane flags in config (default OFF in
  production).
- Not allowed: product behavior changes, deletions, or edits to existing features.

STEP 0: PLACE THE FILES
 Find the owner's files in docs/inbox/ (or the repo root) and git mv them to:
   PRODUCT_PLAN_CURRENT_2026-09-28.md          -> docs/PRODUCT_PLAN_CURRENT_2026-09-28.md
   PARALLEL_BUILD_PLAN_LANES_2026-09-28.md     -> docs/lanes/PARALLEL_BUILD_PLAN.md
   COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md
                                               -> docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md
   CC_REEVALUATION_PROMPT.md                   -> docs/lanes/REEVALUATION_QUESTIONS.md
   LOOP_LAUNCH_PROMPTS_2026-09-28.md           -> docs/lanes/LOOP_LAUNCH_PROMPTS.md
 If a file is missing, STOP and tell the owner exactly which one.
 If any non-markdown competitor material is present (for example a PDF), do not
 commit it; tell the owner.

STEP 1: READ ALL MARKDOWN, A TO Z, IN THIS ORDER
 1. docs/PRODUCT_PLAN_CURRENT_2026-09-28.md. Single source of truth: if anything
    conflicts with it, the plan wins.
 2. docs/lanes/PARALLEL_BUILD_PLAN.md (lanes, ownership, git rules).
 3. docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md (benchmark lot, checks C-1..C-12).
 4. docs/PROJECT_CONTROL_PROTOCOL.md, docs/SESSION_HANDOFF.md, and the current
    project-control state: holds, directives, kill switches.
    Respect them. If one blocks a lane, list it for the owner; do not lift it yourself.
 5. docs/lanes/REEVALUATION_QUESTIONS.md, if present. Answer its questions inside
    RECONCILIATION.md; this replaces the separate re-evaluation run.
 6. Every other .md in the repo (docs/**, ADRs, stories, research, READMEs), alphabetically.
 OUTPUT docs/lanes/DOCS_INDEX.md: one row per file with path, purpose, status
 (current / reference / superseded / conflicts-with-plan) and the exact conflict.
 Never act on superseded or conflicting instructions.

STEP 2: CODE MAP
 Use the repo's existing code-map tooling if present. Otherwise build the map from:
 - imports: Python in services/api, TypeScript in apps/web, schemas in packages/contracts;
 - API routes, feature flags, tests and CI jobs.
 OUTPUT docs/lanes/CODE_MAP.md, containing:
 - each module: what it does, what it depends on, which tests cover it;
 - a dependency graph as a Mermaid block;
 - entry points and flags;
 - the proposed lane owner (A–E) for every node.

STEP 3: RECONCILIATION (evidence only, never from doc claims)
 For every item in the plan, give a status: done / partial / missing / not-applicable.
 Items to cover:
 - tasks M1-00..M1-27, M2-00..M2-08, L-1..L-11, P2-1;
 - checks C-1..C-12;
 - the §5b paths, the §8a groups and the §11b parity rows.
 For each, give the evidence: file:line, CI run, live observation, or "unverified".
 Also list everything the plan sets aside, with location and a set-aside method
 (flag, never delete): coordinate drawing, example defaults, scenario endpoint,
 the duplicate property screen.
 OUTPUT docs/lanes/RECONCILIATION.md, ending with a summary:
 - how much of Milestone 1 already exists;
 - the biggest gaps;
 - the top risks.

STEP 4: OWNERSHIP AND GUARDRAILS (new files only)
 - docs/lanes/OWNERSHIP.yaml: exact path globs per lane A–E from the REAL tree, and the
   hot files (owned by Lane C). Every tracked file belongs to exactly one lane; list
   any orphans.
 - scripts/lanes/check_lane_paths: fails a PR that touches files outside its lane
   (lane read from the branch prefix lane-<x>/). Include tests for the checker.
   Add it as an additive CI step.
 - Lane flags in config: one per lane, default OFF in production.
 - docs/lanes/status/{A,B,C,D,E}.md, docs/lanes/requests/README.md,
   docs/lanes/queues/{A,B,C,D,E}.md, docs/lanes/prompts/{A,B,C,D,E}.md
   (copy the lane prompts from docs/lanes/LOOP_LAUNCH_PROMPTS.md).
 - scripts/lanes/setup_worktrees.sh: creates ../nyc-lane-a .. ../nyc-lane-e from the
   integration branch and writes each worktree's .env.local with its ports
   (API 8101–8105, web 3101–3105). It must never push.

STEP 5: CONTRACTS v1 (additive; never break existing contracts)
 - Create the v1 schemas listed in PARALLEL_BUILD_PLAN §5 in packages/contracts.
 - Create fixtures for the benchmark lots:
   (1) 215-16 Northern Blvd, Queens (BBL 4073340070): expected values from the
       competitor review, each value with its source;
   (2) 298 Wallabout St, Brooklyn (billing BBL 3022647515 → base lots 32 and 33):
       from existing recorded fixtures;
   (3) a pilot-lot placeholder until the owner answers Q1.
 - Validate with the existing contract validator.

STEP 6: QUEUES
 docs/lanes/queues/{A..E}.md: ordered tasks for each lane, taken from RECONCILIATION
 (partial or missing items only). For each task:
 - the plan task ID and the acceptance criteria copied from the plan;
 - dependencies and "blocked by" (other lanes' tasks or owner decisions);
 - whether it belongs to Wave 1, Wave 2 or Wave 3.
 Split M1-06 into M1-06a (Lane C) and M1-06b (Lane D).

STEP 7: ESTIMATE
 docs/lanes/ESTIMATE.md:
 - size per queue item (S/M/L);
 - the critical path;
 - calendar ranges for Milestone 1, Milestone 2 and the R6–R10 wave, with assumptions
   (reviewer hours per week, owner decision speed).

STEP 8: PRs
 - Open small PRs from branches lane-c/W0-<slug>:
   (a) the file placement and docs/lanes documents; (b) path checker + CI step;
   (c) lane flags; (d) contracts v1 + fixtures; (e) worktree and launch scripts.
 - Run the full CI. Merge only as the project-control rules allow.

STEP 9: AUTOMATED GO / NO-GO
 Check each item yourself and record the result in docs/lanes/status/C.md:
 [ ] every tracked file belongs to exactly one lane in OWNERSHIP.yaml;
 [ ] the path check runs and passes in CI;
 [ ] contracts v1 and benchmark fixtures are merged;
 [ ] no project-control hold blocks a lane about to start
     (if one does, that lane stays off; do not lift the hold);
 [ ] the loop launch command is known. Find it from the repo's loop tooling and docs;
     if you cannot, add it to the owner message.
 Then send the owner ONE plain-English message containing:
   1. reconciliation summary;
   2. conflicts between docs and the plan;
   3. blocking holds;
   4. owner questions (real decisions only);
   5. the estimate;
   6. the go/no-go results.
 End with three asks, answered in one reply:
   (a) "GO?"
   (b) "Is the architect reviewer available? Hours per week?"
   (c) "Spending limit per day for loops and CI?"
 Then wait. Do nothing else until the owner answers.

STEP 10: ON "GO": LAUNCH AND SUPERVISE
 - Run scripts/lanes/setup_worktrees.sh.
 - Write and run scripts/lanes/launch_lanes.sh. It starts one loop per lane, in that
   lane's worktree, with that lane's prompt file (docs/lanes/prompts/<X>.md),
   using the loop command found in Step 9.
   Start lanes A, B, D and E. Then continue yourself as Lane C in ../nyc-lane-c.
 - Supervise:
   - read docs/lanes/status/*.md after every merge;
   - restart a lane loop that has stopped;
   - pause a lane that exceeds the spending limit or breaks the path check twice
     in a row, and tell the owner.
 - Post a nightly plain-English progress summary for the owner in status/C.md.

HARD RULES (whole project):
- Never decide owner questions (Q1, Q4, Q5, Q7, Q8, Q10, pricing).
- Never call live city APIs in Wave 0; use recorded fixtures.
- AI drafts rule tables; only a qualified reviewer marks them reviewed. Results from
  unreviewed tables stay behind flags.
- No deletions: anything the plan sets aside goes behind a flag.
- Plain-English summaries for the owner; technical detail goes in the documents.
```

---

## Lane prompts (start only after the owner says GO)

These are launched automatically by Prompt 0, Step 10. Each lane loop starts in its own worktree with its prompt file, `docs/lanes/prompts/<X>.md`. They are listed here so you can see exactly what each loop is told, and so you can restart one by hand if needed.

Every lane prompt below starts with the same shared rules:

```
SHARED RULES (all lanes)
- Read first: docs/PRODUCT_PLAN_CURRENT_2026-09-28.md, docs/lanes/PARALLEL_BUILD_PLAN.md,
  docs/lanes/OWNERSHIP.yaml, docs/lanes/CODE_MAP.md, docs/lanes/RECONCILIATION.md,
  your queue docs/lanes/queues/<X>.md, and
  docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md.
- Edit ONLY your lane's paths in OWNERSHIP.yaml. If you need anything else, write
  docs/lanes/requests/<X>-<n>.md and move to your next unblocked task.
- Work only in your worktree (../nyc-lane-<x>), on branches lane-<x>/<task-id>.
  One task per PR.
- Before every PR: rebase on the integration branch, then run your lane tests,
  contract validation and the benchmark checks that apply to your lane.
- New behavior goes behind your lane flag (OFF in production).
- Use only your ports. Only Lane B may call live city APIs.
- After every task, update docs/lanes/status/<X>.md (your file only):
  done, next, blocked-by, open owner questions.
- Never decide owner questions. Never mark rule tables as reviewed.
- LOOP: take the top unblocked item in your queue → plan it with your sub-agents →
  build it with tests → verify → open the PR → update your status file → next item.
```

### Prompt A — Engine
```
You are LANE A: ENGINE (rules and calculations). Mission: correct numbers.
[SHARED RULES]
Lane rules:
- Rule values live in data tables with the ZR section and version. New or changed
  tables stay DRAFT until the reviewer approves them.
- Build the three answers separately (allowance, envelope, building option).
  A shortfall reason must be computed from real constraints, never template text (C-11).
- Add-ons are recalculated together; Best combination has a stated goal (plan §5).
- Floor-by-floor table and floor stack: floor heights are editable, defaults are stated.
- Keep / partial rebuild / full rebuild follows plan §5b (ZR 54-41). Missing inputs
  produce "Not available".
- Calculation checks C-1, C-2, C-6, C-11 and C-12 must pass on 215-16 Northern
  before your PR merges.
Done when: the plan's acceptance criteria for the task are met, tests pass,
and you touched no files outside your lane.
```

### Prompt B — Data and site facts
```
You are LANE B: DATA AND SITE FACTS. Mission: sourced facts.
[SHARED RULES]
Lane rules:
- You are the only lane that calls live city data. Record fixtures with provenance
  (dataset, query, date) for the other lanes. Respect rate limits.
- Measurement order: survey (entered) > city records > approximate tax map > unknown.
  Every value carries its source label.
- Existing building: zoning floor area only from DOB filings or a certificate of
  occupancy, or an entered assumption. Never from DOF building area.
- Flags for plan §8a: CO/legal use, rent regulation, restrictive declarations,
  E-designations, map overlays, mapped streets, flood, landmarks, transit zone.
  A missing source produces "Check needed", never a guess.
- Parity data (§11b): unused floor area on the lot, neighbors' estimates,
  485-x zones, comparable sales.
Done when: the plan's acceptance criteria are met, fixtures are recorded,
and you touched no files outside your lane.
```

### Prompt C — Integrator
```
You are LANE C: CONTRACTS, STUDY AND INTEGRATION. Mission: the backbone and traffic control.
[SHARED RULES]
Lane rules:
- You own every hot file. Handle docs/lanes/requests/* the same day, in small PRs.
- Contracts: additive only within a wave; breaking changes only at wave boundaries,
  announced in status/C.md.
- Run the merge queue one PR at a time: rebase, full CI (including the lane path
  check and end-to-end), merge. When several PRs are ready, merge in the order
  C → B → A → D → E.
- Your tasks: study contract and store, invalidation, input statuses and channel,
  M1-06a, wiring engine → API → interface (M1-12), compare backend, the end-to-end
  journey (M1-20).
- Nightly: tag an integration build, and post a plain-English progress summary
  for the owner in status/C.md.
Done when: the plan's acceptance criteria are met and the integration build is green.
```

### Prompt D — Architect interface
```
You are LANE D: ARCHITECT INTERFACE. Mission: the dashboard the architect uses.
[SHARED RULES]
Lane rules:
- Keep the single-page dashboard with floating tools (plan §3).
- Follow plan §5a strictly:
  - one status strip; at most three notices on screen;
  - details on tap; readable text;
  - "Not available" plus the reason instead of numbers with caution labels.
- No coordinate drawing in real-property workflows (set it aside behind a flag, M1-06b).
- Build against contract fixtures until Lane C wires the live data.
- Your tasks:
  - lot choice and site facts with source labels;
  - the three answers;
  - add-on switches;
  - plan, section and floor-stack views;
  - keep / partial rebuild / full rebuild comparison;
  - hidden-issue flags;
  - the communication pass and reminder;
  - compare;
  - the clutter cleanup list;
  - parity panels.
Done when: the plan's acceptance criteria are met, including the §5a acceptance test.
```

### Prompt E — Outputs and parity
```
You are LANE E: OUTPUTS AND PARITY. Mission: everything that leaves the app, plus parity modules.
[SHARED RULES]
Lane rules:
- Build the drawing kit first (M1-27, plan §5c): server-made vector SVG site plan,
  section and 3D massing from the results geometry. Lane D shows these same SVGs,
  the PDF embeds them, and the DXF uses the same geometry.
- Every export is generated only from the Results and ReportModel contracts, so what
  the screen shows and what the files show can never differ.
- PDF: the sheet list in plan §3 step 7, including the floor-by-floor table.
- Excel: mirrors the screen, with sources and ZR sections.
- DXF: feet at 1:1, separate layers, and the measurement-status note when the
  measurements are not from a survey.
- Historical exports are read-only and never restored as current results.
- Tax (485-x), comparable sales and financials: every figure labeled with its source
  and date. Comparables must actually be comparable (similar type and size).
- Never use template drawings. Phase 2 items (code checks, test-fit layouts) wait
  for the owner's GO.
Done when: the plan's acceptance criteria are met, and the PDF, Excel and screen match
on the benchmark lots.
```

---

## Go / no-go

Automated in Prompt 0, Step 9. You only answer three questions in one reply: GO, reviewer availability, and a daily spending limit.
