# SESSION HANDOFF — seq 142 (2026-10-06 ~01:55 UTC; owner-invoked `/session-handoff first handoff`; session nyc-buildability-5c / 013RaGmCmULdpmjCy58qBeMY, transcript e43b0faf, claude-opus-5-5; directive D-090 sources 030–031)

Orientation only. The ledger (`python tools/project_control.py status`) and `project-control/` WIN over this prose. Seq 141 is in git (#434, #437, #438).

**Turnover reason (owner's words):** `first handoff`.

## READ FIRST — nothing more can merge until blocker B-029 clears
- A security advisory (GHSA-68fv-2mgg-jv7q, high) against `source-map-js` 1.2.1 (pulled in by `postcss` in `apps/web/package-lock.json`) reached `npm audit` on 2026-10-05 ~23:31 UTC. The `web-dependency-security` check now fails on EVERY new run (first seen on #443).
- The fixed version 1.2.2 was published 2026-09-30T14:08:09Z. It passes the 7-day age rule at **2026-10-07T14:08:09Z**, not before.
- The seven waiting PRs below show 46/46 green, but those runs predate the advisory. Do not merge on them: a merge needs a fresh green run after the fix.
- **Owner decision:** wait until 2026-10-07 14:08 UTC (no action needed), or authorize a one-package, auto-expiring exception to the 7-day rule for `source-map-js` 1.2.2 so the fix can go in now. There is no exception to the advisory itself. Record: `project-control/blockers/B-029-source-map-js-advisory-web-dependency-gate.json`.

## Identity (live at generation)
- Repo `/root/project/nyc-buildability` = origin `candidate/D-024-mrl-option-b`, HEAD == origin == `e97bf405` (#438 merge), clean. This file is written in worktree `/root/project/w-handoff10`, branch `task/session-handoff-2026-10-06`.
- Ledger unchanged: 325 accepted, 11 awaiting_gate, 7 claimed, 2 in_progress, 1 rework, 2 blocked, 17 backlog. This work is tracked by PRs + the D-090 registry (209 requirements merged; 213 with #442). `campaign_continuity --status` prints restrictions only.
- One Claude process (tmux session `buildability`); no helper and no test process running. Helpers (pinned `claude-opus-4-8`) ran all session with no limit error.
- Server: `/root/project/lanes-runtime/venv/bin/python`; api tests from `services/api`; web checks per `.claude/rules/CODING_RULES.md`. GitHub Actions had an outage 2026-10-05 19:11 to ~21:40 UTC; operational at generation.

## Owner decisions in force (D-090)
- **R172–R209 (source-030, merged as #438):** the owner's completion requirements (next section) and two start-up fixes: read-only checks come before `git pull` or any change, and work is never reset, cleaned, stashed or discarded to pass a check (R174, R177–R179); a job is never rerun without first reading its state, and never while queued or running (R175, R176); a missing, cancelled, queued or pending check is not a success (R181); implementation, then review (R182).
- **R210–R213 (source-031, #442 open):** the checklist and "done" EXCLUDE detailed apartment design and permit-ready plans; the goal is simplified feasibility: numbers and diagram drawings labelled not for construction (R210). One heavy local run and one helper at a time (R211). A run with a failed test is not green until a clean full run or a reviewed fix (R212). Next build: connected R6B results, then the report, then the PDF (R213).
- From seq 141, unchanged: R142 (the competitor sample is the KIND of report; never copy its numbers); R160 plain words to the owner; R163 the orchestrator decides Lane A merges; R164/R165 no professional-review ask (one standing label, a law link per stat, "not known" when unsure); R167/R168 build one, go to the next; done only when all twelve zones R1–R12 are fully done; R170/R171 this server runs the web checks.

## What "finished" means — the owner's text, unchanged (2026-10-05; D-090 source-030, R173 and R177–R209). Keep this section in every later handoff.

REPORT ACCURACY AND COMPLETION REQUIREMENTS

1. Preserve existing work. Check active sessions and uncommitted/untracked files before changing anything. If blocked, stop and explain. Never reset, clean, stash or discard work to make startup checks pass.

2. Verify current evidence. Saved commit hashes, handoff versions and review results are snapshots. Before merging, confirm the current head has independent PASS review and all expected checks succeeded. Missing, cancelled, queued or pending checks do not count as success. Implementation and independent review happen sequentially.

3. Use one shared, versioned analysis result. The website, floor schedules, drawings and PDF must use the same property, scenario, inputs and calculated results. Changing an input must update every affected output.

4. Automatically check the numbers. Apartment counts must agree with the floor schedules and plans. Floor areas must reconcile with totals. FAR calculations must use the correct lot area and zoning-floor-area definitions. Keep gross, net and zoning floor area distinct. State the denominator for every efficiency percentage. Keep individual-building figures separate from combined-site figures. Define rounding tolerances; never hide discrepancies inside them.

5. Make the drawings honest. Use actual parcel geometry for parcel-specific conclusions. Label simplified geometry clearly. Show the applicable yards, setbacks, floor shapes and cores. Drawings and schedules must agree on uses, floors, units and elevators. Treat detailed layout feasibility as unconfirmed until checked.

6. Make every important number traceable. Include the relevant source or zoning-law link, assumptions and applicable date. Distinguish sourced facts, calculations, estimates and unknowns. Missing information must never silently become zero. Carry the standing disclosure and uncertainty labels into every export.

7. Prove the complete workflow. A real R6B property must go from address input through calculations and website results to a downloadable PDF. Test changed inputs, missing evidence and conflicting evidence. Inspect the actual PDF, including its drawings, numbers, citations and page layout. Turn the confirmed competitor-report discrepancies into regression tests with justified expected results.

8. Define district completion. Maintain a checklist of rules, overlays, exceptions and scenarios supported and tested. One successful R6B example does not establish complete R6B coverage. List unsupported cases clearly. Complete and review the agreed district coverage before moving to the next; do not declare the whole program finished until the full R1–R12 scope is complete.

## Done this session (merged after a different agent's PASS at the exact head + 46/46 expected checks)
#436 the browser-decision record (`78eee04c`) · #437 the rule that this server runs the web checks (`37dafb4f`) · #438 the record of the owner's completion requirements + the handoff carrying them (`e97bf405`). Their cancelled or failed jobs were each read first and restarted once.

## Waiting PRs — all reviewed PASS at these heads (records are comments on each PR); merge order; BLOCKED by B-029
1. #432 `14cd44f5` ADR-007 + CLAUDE.md: the professional sign-off gate becomes a label + law link (three review rounds; seven Markdown files).
2. #433 `af8d820c` the standing label, exactly once per screen (after #432, which it cites).
3. #439 `28047183` Lane A wave 1 (then close #369, #377, #382 as carried).
4. #440 `b41dd369` wave 2 (then close #405, #417, #421 as carried).
5. #442 `8a5a4733` the source-031 record. It has 23 checks, not 46: GitHub showed a conflict while #438 was open, so no pull-request run was made. Merge the integration branch into it (an empty merge), have the same verifier confirm the tree is identical and the remerge-diff empty, then wait for 46 checks (the pattern used on #438).
6. #441 `26df5a72` the R6B checklist (cites wave 2's code and R210).
7. #431 `224add5c` the one-district-at-a-time plan (last).
- **NOT reviewed:** #443 `41d5086b` the fix for the timing test that failed two combined runs (DB-135). It needs a different agent's review and a full api run.

## Evidence on the development server
- All eight changes merged in order on a local branch (`scratch/integration-dryrun-2026-10-05` in `/root/project/w-integ`, never pushed): no conflict; registry validator exit 0; ruff clean; FULL api suite run alone 8,000 passed, 8 skipped, 0 failed; web lint 0 errors, typecheck clean, 2,423 unit tests, build, 153 browser journeys. Two earlier api runs made beside other heavy runs each failed one timing test.
- The stricter merge step: `python3 /root/project/lanes-runtime/merge/merge_failclosed.py <pr> <40-char reviewed head> --expected /root/project/lanes-runtime/merge/expected-checks.tsv`. It refuses a moved head and any missing, cancelled, queued, pending, skipped or failed check (`selftest.py` beside it: PASS). Not in the repo yet (DB-142).

## Journey state — honest (nothing professionally verified)
R6B is not finished. The R6B checklist (#441) counts 46 rows: 13 supported and tested, 4 built but reaching no output, 7 flags only, 20 not built, 2 not applicable. No mounted results route, no report builder, no report PDF, no spreadsheet.

## Attempted, not completed
The seven-PR merge queue (stopped by B-029) · #443 unreviewed · the source-map-js fix not started · discoveries DB-134, DB-136, DB-137, DB-140 to DB-143 open in `docs/DISCOVERY_BACKLOG.md`.

## Helpers and local state
No helper is running; every return is recorded on its PR. Unpushed by design: the scratch dry-run branch only. Untracked: two generated files in the #433 worktree (`apps/web/next-env.d.ts`, `apps/web/tsconfig.tsbuildinfo`); never commit them. Worktrees added this session: `/root/project/rv-wave1`, `w-dir-1012`, `w-dir-1013`, `w-r6b-checklist`, `w-integ`, `w-timing`, `w-handoff10`.

## Standing restrictions
Tier D (production approval, payments, secrets, paid accounts); never merge #241; expansion §2 hold (financial analysis); all production switches off; settled capacity wording never changes; never pass `model:`; dependency security: no waiver of an advisory, ever; no npm/node on the owner's PC; no package outside the lockfile; FULL `services/api` pytest before any api PR; merge fails closed on any non-success, missing, queued or pending check (R181); never ask for a secret in chat; never ask the owner for professional review (R164); plain words to the owner (R160); never reset, clean, stash or discard work to pass a start-up check (R179); never rerun a job without reading its state, and never a queued or running one (R175); one heavy run and one helper at a time (R211).

## Authoritative files (smallest set)
`project-control/state.json`; `project-control/blockers/B-029-*.json`; `project-control/directives/D-090-*/{requirements,manifest}.json` and `source-030…031-amendment.md`; `docs/plans/CITYWIDE_ONE_AT_A_TIME_PLAN_2026-10-05.md` (#431) and `docs/plans/district-checklists/R6B.md` (#441), each on its PR branch; `docs/DISCOVERY_BACKLOG.md` (DB-130..DB-143).

## EXACT NEXT ACTION (successor)
1. Read-only checks first, before `git pull` or any change: `ListAgents`, `tmux ls`, `git status` (uncommitted and untracked files), `git worktree list`. If another nyc-buildability session is alive or there are files you cannot explain: report BLOCKED, write nothing, explain.
2. Then `git pull --ff-only`; `gh pr list`; read this file (from branch `task/session-handoff-2026-10-06` while its PR is open).
3. B-029 first. If the owner granted the age exception, or it is past 2026-10-07T14:08:09Z: invoke `/dependency-security`, move `source-map-js` to 1.2.2 through `.github/workflows/generate-lockfile.yml` (never locally), get the G5 provenance review, prove `web-dependency-security` green, merge that PR.
4. Then the waiting PRs in the order above, one at a time. Each needs a fresh green run after the fix (bring the branch up to date with an empty merge and have the same reviewer confirm the tree is identical; a real change needs a new review). Re-read the live head and checks, merge with the fail-closed step, wait for the integration branch's own run before the next.
5. #443: review by a different agent, then merge.
6. Then build, one piece at a time, as contracted ledger tasks: the R6B results connected to the website, then the report builder, then the PDF (R213). Never report R6B or the program finished before its checklist says so (R206, R209).
7. Owner update in plain words.

## COPY INTO THE NEW SESSION
Owner, before starting: run `tmux ls`; if a session is listed, attach to it instead of starting another (closing a window does not stop a session). Start ONE session: `cd /root/project/nyc-buildability && claude` (not `claude --continue`). `/mcp` must list none.

Resume as the NYC Buildability orchestrator (verify the model with /model). Work only from repository evidence; this prompt is orientation.

START (Bootstrap Gate 0). Read-only checks first; change nothing until they pass: cwd must BE /root/project/nyc-buildability (repo root), branch candidate/D-024-mrl-option-b; run ListAgents and `tmux ls`; run `git status` (uncommitted and untracked files) and `git worktree list`; /mcp empty; memory under 70 %. If another nyc-buildability session is alive, or there are files you cannot explain: report BLOCKED, write nothing and explain. Never reset, clean, stash or discard work to pass a check. Only after that: `git pull --ff-only` (HEAD must equal origin). Read ONLY docs/SESSION_HANDOFF.md (seq 142; if the PR from branch task/session-handoff-2026-10-06 is still open, read it from that branch), run `python tools/project_control.py status` (the ledger wins) and `gh pr list`. Report READY TO RESUME or BLOCKED.

WHERE WE ARE: the owner wants an accurate PDF feasibility report of the kind in their competitor sample: simplified feasibility, not detailed apartment design or permit-ready plans, for all of R1–R12 and all zoning, built ONE AT A TIME, done only when all twelve zones are fully done. What "finished" means is the handoff section of that name (the owner's own text). Three records merged on 2026-10-05/06. Seven more changes are reviewed PASS and waiting (the rule change ending the professional sign-off gate, the standing label, two combined Lane A branches, the record of the owner's latest message, the R6B checklist, the one-at-a-time plan); one test fix (#443) is not reviewed. NOTHING can merge until blocker B-029 clears: a new security advisory on source-map-js fails the dependency check on every new run; the fixed version passes the 7-day age rule at 2026-10-07 14:08 UTC unless the owner authorizes a one-package age exception sooner. R6B is not finished: no connected results page, no report builder, no PDF.

NEXT ACTION, in order: (1) B-029 through /dependency-security; (2) the waiting PRs one at a time, each on a fresh green run after the fix, merged with the fail-closed step in /root/project/lanes-runtime/merge/; (3) review and merge #443; (4) build the R6B results connection, then the report, then the PDF, one piece at a time; (5) owner update in plain words.

STOPS: Tier D (production approval, payments, secrets, paid accounts); PR #241 never; the expansion §2 hold; all production switches off; settled capacity wording never changes; never pass `model:`; no waiver of a security advisory; never ask for a secret in chat; never ask the owner for professional review; merge fails closed on any non-success, missing, queued or pending check; never rerun a job without reading its state; one heavy run and one helper at a time; never report the program done before all twelve zones are; plain, simple words to the owner.
