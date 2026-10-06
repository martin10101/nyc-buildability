# SESSION HANDOFF — seq 143 (2026-10-06 ~05:05 UTC; owner-invoked `/session-handoff`, no reason given; session nyc-buildability-5c / 013RaGmCmULdpmjCy58qBeMY, transcript 50db7f46, claude-opus-5-5; directive D-090 sources 032–036)

Orientation only. The ledger (`python tools/project_control.py status`) and `project-control/` WIN over this prose. Seq 142 is the previous commit of this file on this branch.

**Turnover reason (owner's words):** none given.

## READ FIRST — nothing can merge (blocker B-029); nothing was built this session
- Advisory GHSA-68fv-2mgg-jv7q (high) on `source-map-js` 1.2.1 fails `web-dependency-security` on every new run. The fix, 1.2.2, was published 2026-09-30T14:08:09.382Z. **Owner's safe check time: 2026-10-07 14:09 UTC or later (R219).** Reaching it approves nothing (R220).
- No owner decision is needed: the written policy (`docs/DEPENDENCY_SECURITY_POLICY.md` section 6) says the machine gate has no exception path, so an age exception cannot turn a check green.
- The one-line pin is prepared on the server only: branch `task/deps-source-map-js-1-2-2`, worktree `/root/project/w-deps-smj`, commit `6c8fd257` (adds `"source-map-js": "1.2.2"` to `overrides` in `apps/web/package.json`). NOT pushed, on purpose. Not verified.
- No timer, watcher or scheduled job exists or may be created (R232). The 14:09 step is started by hand.

## Identity (live at generation)
- Repo `/root/project/nyc-buildability` = origin `candidate/D-024-mrl-option-b`, HEAD == origin == `e97bf405`, clean. This file is written in `/root/project/w-handoff10`, branch `task/session-handoff-2026-10-06` (PR #444).
- Ledger unchanged: 325 accepted, 11 awaiting_gate, 7 claimed, 2 in_progress, 1 rework, 2 blocked, 17 backlog. `campaign_continuity --status` prints restrictions only. One Claude process (tmux `buildability`); no helper, test or watcher running.
- Server: `/root/project/lanes-runtime/venv/bin/python`; api tests from `services/api`; web checks per `.claude/rules/CODING_RULES.md`. Fail-closed merge step: `python3 /root/project/lanes-runtime/merge/merge_failclosed.py <pr> <40-char head> --expected /root/project/lanes-runtime/merge/expected-checks.tsv`.

## The goal and the rules (owner, 2026-10-06; rows R248–R273 on PR #445)
- **Goal:** the FULL feasibility report comparable to the owner's 88-page sample, with reliable numbers; not a zoning summary. Nine contents: property facts, applicable zoning, development options, estimated floors, simple building shapes, legal unit limits, realistic apartment-count estimates, option comparisons, the downloadable report. One piece at a time; a finished piece is a milestone, never completion. Outside: detailed apartment layouts, permit-ready plans.
- **Six rules (R255–R260):** facts and legal eligibility from evidence, a user's assumption only as a labelled conditional result; design choices with visible, editable starting values, no hidden defaults; conflicting areas never chosen automatically; missing information is not unfinished work, and "unsupported" never finishes a promised feature; reference cases in files apart from program output, AI agreement alone is not proof; no "best" without the criterion.
- **A result appears three ways only:** settled, conditional ("If …"), or withheld ("not known" + reason + what would resolve it).
- **"Not checked" is never "confirmed" (R267–R269):** a district limit is not the property's confirmed maximum. For unchecked conditions: unaffected answers stay visible, defensible assumptions are conditional, only unsupportable answers are withheld.
- **Nothing is dropped (R272):** every sample section inside the line and all eleven options stay unless the owner agrees.
- Earlier, unchanged: R142 (never copy the sample's numbers), R160 plain words, R164/R165 no professional-review ask, R167/R168 one at a time, done only when all twelve zones are, R211 one heavy run and one helper at a time, R223 no building on the unmerged queue.

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

## Done this session (documents and reviews only; nothing merged, nothing built)
- **#443** (timing-test fix): independent review PASS at `41d5086b`, no correction; full api suite run alone 7,920 passed, 8 skipped. Record on the PR.
- **#445** (`task/D-090-source-032-review-hold-and-results-work-order`, head `83a993f4`, stacked on #442): the records of owner messages 72–80 (sources 032–036, R214–R273, all pending); `docs/plans/FEASIBILITY_REPORT_SECTION_MAP_2026-10-06.md` (the sample's sections against the intended report; existing property screens apart from the unconnected results and PDF; the open scope choices); `docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md` (first milestone: results on the screen; gaps K1–K20; steps R0, P1, P2, Part 0, A, B; tests marked LAW / WIRING / UNCHANGED).
- Review trail on #445: work order audited four times by one progress-auditor (the owner's reviewer found two defects the audits had passed: tests requiring uncertain answers; a district height shown as the property's settled maximum). Final state: PASS at `83a993f4` (the fourth audit required four corrections; they were applied and the same auditor attested them). Registry records 032–036 all verified PASS by one directive-compliance-verifier (the last at `83a993f4`). Every record is a comment on the PR.
- Independent reference values (a blind helper, law text and recorded facts only): the newer engine equals them wherever it gives a number (floor area 20,150 / 24,180; heights 30/45/55, 65; unit limit 29; made-up lots). It also gives numbers the reading does not support for a whole lot (corner coverage, rear-yard waiver, full-lot floor plate); two lot areas differ 3.1 percent (10,075 recorded, 10,388 outline).
- What a user can see today (read from code): property and zoning facts for any lot on the property and confirm pages, no switch. A workspace with an older draft floor-area cap and a print view sits behind switches that are all off. The newer R6B results, option comparison, the report builder and any file are on no screen. No evidence the site is deployed.

## Waiting PRs — merge order after the fix; each needs a fresh green run on its then-current head
#432 `14cd44f5` → #433 `af8d820c` → #439 `28047183` (then close #369, #377, #382) → #440 `b41dd369` (then close #405, #417, #421) → #442 `8a5a4733` (has 23 checks; needs an empty base merge + identity check) → #445 (stacked on #442) → #441 `26df5a72` → #431 `224add5c` → #443 `41d5086b` → #444 (this handoff). All reviewed at those heads except as noted above. A base merge needs the reviewer to confirm an empty remerge-diff.

## Owner decisions open (the section map, section 4; nothing is dropped meanwhile)
1. The ORDER of the sample's eleven options (all stay). 2. Sections beyond the nine named contents: comparable sales, block description, parking/loading counts, photographs (imagery licence), tax abatement (large, last), financial inputs (under the owner's hold). 3. The realistic estimate: one average apartment size and one shared-space allowance first, a mix later. 4. Starting values for floor height, apartment size, shared space: the owner approves; bring proposed values with their basis. 5. PDF converter, saved-report storage (B-001), imagery licence. **The owner asked for these in plain English with a recommendation and what each adds (R271); the reply of this session gave them — confirm the owner's answers before contracting.**

## Attempted, not completed
Steps R0/P1/P2 not started · no ledger task contracted · discoveries DB-134, DB-136, DB-137, DB-140–DB-149 open in `docs/DISCOVERY_BACKLOG.md`.

## Helpers and local state
No helper is running. Not in the repo, on the server: `/root/project/lanes-runtime/owner-docs/` (the owner's testing-plan PDF, proposed and not adopted; `session-2026-10-06/` with the sealed law packet, the hand-calculation scripts and every helper's return). Worktrees added: `rv-443`, `w-deps-smj`, `w-dir-1014`. Unpushed by design: the pin branch only.

## Standing restrictions
Tier D (production approval, payments, secrets, paid accounts); never merge #241; expansion §2 hold (financial analysis); all production switches off; settled capacity wording never changes; never pass `model:`; no waiver of an advisory, no bypass of the 7-day check, older green runs are not approval (R217, R218); no timer, watcher or automatic rerun or merge (R232); never rerun a job without reading its state; merge fails closed on any non-success, missing, queued or pending check; no building on the unmerged queue (R223); FULL `services/api` pytest before any api PR; never ask for a secret in chat; never ask the owner for professional review; plain words to the owner; never reset, clean, stash or discard work to pass a check; one heavy run and one helper at a time; never report a milestone, R6B or the program as complete (R251).

## Authoritative files (smallest set)
`project-control/state.json`; `project-control/blockers/B-029-*.json` (this branch); on #445's branch: `project-control/directives/D-090-*/{requirements,manifest}.json`, `source-032…036-amendment.md`, the two documents under `docs/plans/` named above; `docs/plans/CITYWIDE_ONE_AT_A_TIME_PLAN_2026-10-05.md` (#431); `docs/plans/district-checklists/R6B.md` (#441); `docs/DISCOVERY_BACKLOG.md`.

## EXACT NEXT ACTION (successor)
1. Read-only checks first: `ListAgents`, `tmux ls`, `git status`, `git worktree list`. Another live session or unexplained files: BLOCKED, write nothing.
2. `git pull --ff-only`; `gh pr list`; read this file from branch `task/session-handoff-2026-10-06` while #444 is open; read the two documents on #445.
3. Before 2026-10-07T14:09Z: no dependency step. Allowed: take the owner's answers to the scope choices and record them (owner message 81, the `/session-handoff` command, is not in a source file yet; number it with the next record).
4. At or after 14:09Z, when the owner says go, attended: read the registry publish time of `source-map-js` 1.2.2 again; push the prepared pin branch (or recreate it); dispatch `.github/workflows/generate-lockfile.yml` on it (never generate the lock locally; a bot push starts no CI run, so open the PR or push after it); independent G5 dependency review at the exact head; every expected check a completed success; merge with the fail-closed step.
5. Then the queue above, one at a time, each on a fresh green run; wait for the integration branch's own run before the next.
6. Then milestone 1 from the work order, as ledger tasks citing R166, R167, R213, R221–R273: R0, P1, P2, Part 0, Part A, Part B. Each written, then reviewed by a different agent at the exact commit, then merged.
7. Owner update in plain words: milestone, what is owed, what they must decide.

## COPY INTO THE NEW SESSION
Owner, before starting: run `tmux ls`; if a session is listed, attach to it instead of starting another. Start ONE session: `cd /root/project/nyc-buildability && claude` (not `claude --continue`). `/mcp` must list none.

Resume as the NYC Buildability orchestrator (verify the model with /model). Work only from repository evidence; this prompt is orientation.

START (Bootstrap Gate 0). Read-only checks first; change nothing until they pass: cwd must BE /root/project/nyc-buildability (repo root), branch candidate/D-024-mrl-option-b; run ListAgents and `tmux ls`; run `git status` (uncommitted and untracked files) and `git worktree list`; /mcp empty; memory under 70 %. If another nyc-buildability session is alive, or there are files you cannot explain: report BLOCKED, write nothing and explain. Never reset, clean, stash or discard work to pass a check. Only after that: `git pull --ff-only` (HEAD must equal origin). Read ONLY docs/SESSION_HANDOFF.md (seq 143; if the PR from branch task/session-handoff-2026-10-06 is still open, read it from that branch), run `python tools/project_control.py status` (the ledger wins) and `gh pr list`. Report READY TO RESUME or BLOCKED.

WHERE WE ARE: the owner wants the FULL feasibility report comparable to their sample PDF, with reliable numbers, for all of R1–R12, built one piece at a time; a finished piece is a milestone, not completion; no detailed apartment layouts or permit-ready plans. Nothing is built yet beyond what existed: a user can see property and zoning facts; the new R6B results, the option comparison and the PDF are on no screen. This session produced documents only, on pull request 445: the record of the owner's instructions, a map of the sample against the intended report, and the work order for the first milestone (results on the screen). The owner's rules: facts from evidence; a result is settled, conditional ("If …") or "not known"; "not checked" is never "confirmed"; nothing from the sample is dropped without the owner's agreement. NOTHING can merge until blocker B-029 clears: the fixed version of source-map-js may be checked on 2026-10-07 at 14:09 UTC or later, by hand, with a normal review and fresh passing checks.

NEXT ACTION, in order: (1) before that time only read-only work and records: take the owner's answers to the open scope choices; (2) at or after 14:09 UTC on 7 October, when the owner says go: the dependency fix through /dependency-security; (3) the waiting PRs one at a time, each on a fresh green run, merged with the fail-closed step in /root/project/lanes-runtime/merge/; (4) then build milestone 1 from the work order, one step at a time, each reviewed by a different agent; (5) owner update in plain words.

STOPS: Tier D (production approval, payments, secrets, paid accounts); PR #241 never; the expansion §2 hold; all production switches off; settled capacity wording never changes; never pass `model:`; no waiver of a security advisory and no bypass of the 7-day check; no timers, watchers or automatic reruns or merges; never ask for a secret in chat; never ask the owner for professional review; merge fails closed on any non-success, missing, queued or pending check; never rerun a job without reading its state; one heavy run and one helper at a time; no building on unmerged work; never report a milestone, R6B or the program as complete; never drop a sample section or an option without the owner's agreement; plain, simple words to the owner.
