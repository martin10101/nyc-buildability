# D-090 source-030 (amendment): owner messages 69-70, 2026-10-05 - the resume prompt with its "FIRST, BEFORE ANYTHING ELSE" merge step; then two instruction fixes and the REPORT ACCURACY AND COMPLETION REQUIREMENTS (eight numbered items) to add to the handoff

Captured 2026-10-05 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/e43b0faf-e7e2-4b40-8795-1be41c8cad50.jsonl` (the conversation that began after `/clear` in the same running session): message 69 (line 13, uuid `49eff0af-2e37-4923-be56-fd57f2bd007d`, 2026-10-05T20:34:03.112Z; a user turn) and message 70 (line 180, uuid `b0a2a204-dccf-43be-a17c-a29a9eda1f56`, 2026-10-05T20:38:48.947Z; sent while the session was working; stored as a queued_command attachment). A script copied the raw text; nothing was retyped; each is complete and byte-identical to the transcript except for the blockquote prefix. Raw-text SHA-256: 69 `98f034bfff97dcdd9274f004cdacf787a3dcf191f2659840974856f6ed0f07ed`; 70 `879d531003250fe6f1cfe6fe2558f51c959d44ed29e0f25b853e02cd6f5ed1a6`; the part of message 70 from the heading "REPORT ACCURACY AND COMPLETION REQUIREMENTS" to its end (the text to add to the handoff) `6cfc3c555a5056a20f5669819f640cbb2ed2519d58a909a8c91c9ad3ad9f7e4f`. Every owner fragment quoted in a requirement row was checked by the script to be an exact substring of its message.

Message numbers continue from source-029 (message 66). Messages 67 and 68 were sent in the earlier conversation (transcript `4d3637bc-346a-4b44-a0e7-b9688bc4f91a.jsonl`, line 3103 at 2026-10-05T20:20:18.784Z and line 3125 at 2026-10-05T20:24:06.585Z); script-copied, they read "Its taking too long something is not write" and "Yes, i'm going to exit out of here. Please give me the final prompt. One more time for the handoff". They add no requirement (a remark on the wait during the GitHub outage, and the request for the final hand-off prompt) and are recorded here only so the numbering has no gap.

This branch is stacked on the source-029 capture (PR #436, head `686f6bd7`) and on the web-checks rule branch (PR #437, head `e27a3dda`); both are open, reviewed, and waiting for checks.

Context: message 69 is the hand-off prompt the earlier conversation wrote when the owner asked for it (message 68); the owner pasted it to start this conversation. It is the committed handoff's copy-into-the-new-session text plus one new paragraph, "FIRST, BEFORE ANYTHING ELSE", which is in no committed handoff. Message 70 arrived about five minutes later, while the start-up checks and the first reviews were running.

## Owner message 69 (verbatim)

Transcript timestamp 2026-10-05T20:34:03.112Z.

> Resume as the NYC Buildability orchestrator (verify the model with /model). Work only from repository evidence; this prompt is orientation.
>
> START (Bootstrap Gate 0): cwd must BE /root/project/nyc-buildability (repo root), branch candidate/D-024-mrl-option-b, HEAD == origin after `git pull --ff-only`, /mcp empty, memory under 70 %. Run ListAgents and `tmux ls`: if another nyc-buildability session is alive, report BLOCKED and write nothing. Read ONLY docs/SESSION_HANDOFF.md (seq 141; if the PR from branch task/web-tests-run-on-dev-server is still open, read it from that branch), run `python tools/project_control.py status` (the ledger wins), `gh pr list` and `git worktree list`. Report READY TO RESUME or BLOCKED.
>
> WHERE WE ARE: the owner wants an accurate PDF feasibility report of the kind in their competitor sample, for the whole program: all of R1–R12 and all zoning, built ONE AT A TIME (finish one, go to the next; no swarm of helpers), and the program is done only when all twelve zones are fully done (D-090 R142, R166–R168). The owner ended the professional-review gate: one standing "not professionally reviewed" label, a zoning-law link per stat, and "not known" when unsure replace it (R164/R165; ADR-007 is open as #432). The orchestrator decides Lane A merges (R163). Thirteen PRs merged on 2026-10-04. Six reviewed-PASS PRs (#369, #377, #382, #405, #417, #421) are combined in two wave branches that are pushed but have no PR and no review yet. #431 (the plan; its parallel waves must be rewritten to one-at-a-time), #432 (ADR-007) and #433 (standing label) are unreviewed. The owner's one-at-a-time correction is recorded and merged (D-090 R167/R168). Helper agents failed with a weekly-limit error on 2026-10-04 but ran on 2026-10-05; if they fail again, reviews wait. This server can now run the website checks itself (lint, typecheck, unit tests, build, browser journeys; commands in .claude/rules/CODING_RULES.md): run them before pushing any web change.
>
> FIRST, BEFORE ANYTHING ELSE: PRs #436 (the record of the owner's browser decision, head 686f6bd7) and #437 (the rule that this server runs the website checks, plus the newest handoff, head e27a3dda) are both reviewed PASS at those exact heads with the records posted on each PR. They wait only for green checks: GitHub Actions had an outage on 2026-10-05 from 19:11 UTC (hosted runners not assigned; jobs cancelled with zero steps). Check https://www.githubstatus.com first. When Actions is operational, re-run the cancelled or queued runs ONCE (`gh run rerun <run id> --failed`), then merge #436 first and #437 second, each only when the live rollup shows zero non-success. Do not hammer reruns.
>
> NEXT ACTION, in order: (1) reconcile git against the handoff; (2) reviews, each merged only on a different agent's PASS at the exact head with every check green: #432 → #433 → wave 1 → wave 2, and #431 only after its rewrite; (3) finish R6B end to end: results route, report builder, PDF, standing label on exports, per-stat law links; (4) then the next zone, one at a time, never more helpers than the policy cap; (5) owner update in plain words.
>
> STOPS: Tier D (production approval, payments, secrets, paid accounts); PR #241 never; the expansion §2 hold; all production switches off; settled capacity wording never changes; never pass `model:`; dependency security no waiver; never ask for a secret in chat; never ask the owner for professional review; merge fails closed on any non-success check; never report the program done before all twelve zones are; plain, simple words to the owner.

## Owner message 70 (verbatim)

Transcript timestamp 2026-10-05T20:38:48.947Z.

> Yes. Add the text below to your handoff. It makes “finished” measurable and targets the mistakes we found in the competitor’s report.
>
> First, fix two instructions already there:
> - Put the read-only startup checks before git pull or any other change. “FIRST, BEFORE ANYTHING ELSE” currently conflicts with your earlier startup gate.
> - Don’t automatically rerun queued jobs. Check their actual state first; --failed specifically reruns failed jobs. [GitHub’s command reference](https://cli.github.com/manual/gh_run_rerun)
>
> Text to add:
>
> REPORT ACCURACY AND COMPLETION REQUIREMENTS
>
> 1. Preserve existing work. Check active sessions and uncommitted/untracked files before changing anything. If blocked, stop and explain. Never reset, clean, stash or discard work to make startup checks pass.
>
> 2. Verify current evidence. Saved commit hashes, handoff versions and review results are snapshots. Before merging, confirm the current head has independent PASS review and all expected checks succeeded. Missing, cancelled, queued or pending checks do not count as success. Implementation and independent review happen sequentially.
>
> 3. Use one shared, versioned analysis result. The website, floor schedules, drawings and PDF must use the same property, scenario, inputs and calculated results. Changing an input must update every affected output.
>
> 4. Automatically check the numbers. Apartment counts must agree with the floor schedules and plans. Floor areas must reconcile with totals. FAR calculations must use the correct lot area and zoning-floor-area definitions. Keep gross, net and zoning floor area distinct. State the denominator for every efficiency percentage. Keep individual-building figures separate from combined-site figures. Define rounding tolerances; never hide discrepancies inside them.
>
> 5. Make the drawings honest. Use actual parcel geometry for parcel-specific conclusions. Label simplified geometry clearly. Show the applicable yards, setbacks, floor shapes and cores. Drawings and schedules must agree on uses, floors, units and elevators. Treat detailed layout feasibility as unconfirmed until checked.
>
> 6. Make every important number traceable. Include the relevant source or zoning-law link, assumptions and applicable date. Distinguish sourced facts, calculations, estimates and unknowns. Missing information must never silently become zero. Carry the standing disclosure and uncertainty labels into every export.
>
> 7. Prove the complete workflow. A real R6B property must go from address input through calculations and website results to a downloadable PDF. Test changed inputs, missing evidence and conflicting evidence. Inspect the actual PDF, including its drawings, numbers, citations and page layout. Turn the confirmed competitor-report discrepancies into regression tests with justified expected results.
>
> 8. Define district completion. Maintain a checklist of rules, overlays, exceptions and scenarios supported and tested. One successful R6B example does not establish complete R6B coverage. List unsupported cases clearly. Complete and review the agreed district coverage before moving to the next; do not declare the whole program finished until the full R1–R12 scope is complete.

## Reading

Message 69:

| Owner words | Requirement |
|---|---|
| "FIRST, BEFORE ANYTHING ELSE: PRs #436 ... and #437 ... merge #436 first and #437 second, each only when the live rollup shows zero non-success." | R172 (sequencing) |
| "Check https://www.githubstatus.com first. When Actions is operational, re-run the cancelled or queued runs ONCE ... Do not hammer reruns." | corrected by message 70: R175, R176 (no separate row) |
| START, WHERE WE ARE, NEXT ACTION and STOPS paragraphs | the committed handoff's own text; already bound by R142, R160-R168, R170-R171 (no new row); the START order is corrected by R174 |

Message 70:

| Owner words | Requirement |
|---|---|
| "Yes." and the sentence that the text makes finished measurable and targets the competitor-report mistakes | purpose of the items below (no row) |
| "First, fix two instructions already there:" | R174, R175 |
| "Add the text below to your handoff." "Text to add:" | R173 (obligation) |
| "Put the read-only startup checks before git pull or any other change." "currently conflicts with your earlier startup gate." | R174 (sequencing) |
| "automatically rerun queued jobs." "Check their actual state first;" | R175 (prohibition) |
| "--failed specifically reruns failed jobs." "https://cli.github.com/manual/gh_run_rerun" | R176 (external_fact) |
| "Preserve existing work." "Check active sessions and uncommitted/untracked files before changing anything." | R177 (sequencing) |
| "If blocked, stop and explain." | R178 (obligation) |
| "Never reset, clean, stash or discard work to make startup checks pass." | R179 (prohibition) |
| "Verify current evidence." "Saved commit hashes, handoff versions and review results are snapshots." "Before merging, confirm the current head has independent PASS review and all expected checks succeeded." | R180 (evidence) |
| "Missing, cancelled, queued or pending checks do not count as success." | R181 (prohibition) |
| "Implementation and independent review happen sequentially." | R182 (sequencing) |
| "Use one shared, versioned analysis result." "The website, floor schedules, drawings and PDF must use the same property, scenario, inputs and calculated results." | R183 (obligation) |
| "Changing an input must update every affected output." | R184 (obligation) |
| "Automatically check the numbers." "Apartment counts must agree with the floor schedules and plans." | R185 (obligation) |
| "Floor areas must reconcile with totals." | R186 (obligation) |
| "FAR calculations must use the correct lot area and zoning-floor-area definitions." | R187 (obligation) |
| "Keep gross, net and zoning floor area distinct." | R188 (obligation) |
| "State the denominator for every efficiency percentage." | R189 (obligation) |
| "Keep individual-building figures separate from combined-site figures." | R190 (obligation) |
| "Define rounding tolerances; never hide discrepancies inside them." | R191 (obligation) |
| "Make the drawings honest." "Use actual parcel geometry for parcel-specific conclusions." | R192 (obligation) |
| "Label simplified geometry clearly." | R193 (obligation) |
| "Show the applicable yards, setbacks, floor shapes and cores." | R194 (obligation) |
| "Drawings and schedules must agree on uses, floors, units and elevators." | R195 (obligation) |
| "Treat detailed layout feasibility as unconfirmed until checked." | R196 (obligation) |
| "Make every important number traceable." "Include the relevant source or zoning-law link, assumptions and applicable date." | R197 (obligation) |
| "Distinguish sourced facts, calculations, estimates and unknowns." | R198 (obligation) |
| "Missing information must never silently become zero." | R199 (prohibition) |
| "Carry the standing disclosure and uncertainty labels into every export." | R200 (obligation) |
| "Prove the complete workflow." "A real R6B property must go from address input through calculations and website results to a downloadable PDF." | R201 (harness) |
| "Test changed inputs, missing evidence and conflicting evidence." | R202 (harness) |
| "Inspect the actual PDF, including its drawings, numbers, citations and page layout." | R203 (evidence) |
| "Turn the confirmed competitor-report discrepancies into regression tests with justified expected results." | R204 (harness) |
| "Define district completion." "Maintain a checklist of rules, overlays, exceptions and scenarios supported and tested." | R205 (obligation) |
| "One successful R6B example does not establish complete R6B coverage." | R206 (decision) |
| "List unsupported cases clearly." | R207 (obligation) |
| "Complete and review the agreed district coverage before moving to the next" | R208 (sequencing) |
| "do not declare the whole program finished until the full R1" | R209 (prohibition) |

- **Orchestrator's readings (not owner wording):** (1) "your handoff" is `docs/SESSION_HANDOFF.md`; the section stays in each later handoff so every successor reads it. (2) The "FIRST, BEFORE ANYTHING ELSE" paragraph exists only in message 69, not in a committed handoff; the fix is applied to the committed handoff's start-up text so the next prompt cannot repeat it: read-only checks, then the pull, then the waiting merges as step one after the gate. (3) On reruns: read each run's jobs first; never rerun a queued or running job; rerun only finished, unsuccessful jobs, once; nothing unattended. The manual the owner linked and the installed `gh` help agree on the flag text; neither covers queued or cancelled jobs, so results are read back, not assumed. (4) "Implementation and independent review happen sequentially" is read per change: finish and freeze, then a different agent reviews; a later commit means a new review. It does not shorten the policy cap of reviewers. (5) "Never reset, clean, stash or discard work" covers any checkout or worktree holding uncommitted, untracked or unpushed work; setting a brand-new empty helper worktree to its starting commit discards nothing. (6) "Expected checks" are the check names this repository's workflows produce for a PR; the merge step refuses when one is absent. (7) "Agreed district coverage" is the district's checklist as recorded in the repository and independently reviewed; the owner sees it in plain words and can change it; no professional-review ask (R164). (8) Items 3 to 7 are requirements on the product still to be built and proven by tests; the benchmark R6B lot is 215-16 Northern Boulevard (R137, R142); the competitor guard list E1-E20 (R146-R151) is the starting point for the regression tests.
- **Not claimed by this capture:** none of R172-R209 is done. All 38 rows are pending until built and independently verified.
