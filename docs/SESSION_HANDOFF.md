# SESSION HANDOFF — seq 152 (2026-10-09 ~04:50 UTC; owner-invoked `/session-handoff`, no reason given; session 013RaGmCmULdpmjCy58qBeMY, transcript `5b29ad99-7c30-4e36-8c3f-cf862905fe8f`)

Orientation only. The ledger (`project-control/`), git and CI win over this prose. A routine handoff in the owner's lighter form (D-090 rows R617 to R625): five things, references in place of copies; no pull request, merge or test run of its own.

## READ FIRST
- **This file lives on the branch `task/wave16-server-corrections` (worktree `/root/project/w-wave16`). Until that branch merges, the copy in the main checkout is the OLD one (seq 151): do not act on its waiting list.**
- Session folder with every script, brief and helper return: `C=/root/project/lanes-runtime/owner-docs/session-2026-10-08c` (`SESSION_NOTES.md`: notes PN-01 to PN-70 and the STATE lines).
- Before saying anything is "not done", open the place where it would be (`docs/reference-cases/`, the task's status, `git log`). On 2026-10-09 the orchestrator called a merged reading "not done" from the old waiting list; the owner had to correct it.

## 1. Where
- Main checkout `/root/project/nyc-buildability`: `candidate/D-024-mrl-option-b` at `7f0e131f96d6104924c13a296f9da52a286e8236` (clean; its own CI run 37880806221: success). Origin `https://github.com/martin10101/nyc-buildability`.
- Active work `/root/project/w-wave16`: `task/wave16-server-corrections`. Code head under review `582dcccb49964fcb5ee2b0dfb7f1fd01863e4c5b` (pushed; CI 37884285350, secret-scan 37884285480, context-budget 37884285511: success, read 04:39 UTC). On top: one commit that holds only this file.
- Ledger: 364 tasks accepted. One ledger-touching branch at a time: this one.

## 2. Done and unfinished
- **Merged this session:** pull requests 472 to 479 (tasks M5-T136 to M5-T143 and two reworded lines of `.claude/rules/CODING_RULES.md`). `gh pr list --state merged --limit 10` shows them.
- **What the owner can use:** the test preview of the results screen (recorded inputs, one lot; how to open it and what remains before any switch-on: `C/RESULTS_SCREEN_TEST_PREVIEW.md`). It shows the layout change (M5-T142). Everything else of this session is maintenance or sits behind switches that are off.
- **In progress: M5-T144** (three corrections of the server: the withheld rear yard's reason, the owner's label `Preliminary zoning results`, the geometry block follows every withheld result). Built in one commit (`582dcccb`), read by the orchestrator, pushed, CI green. Its two independent reviews were RUNNING at handoff time. Not submitted, no gate beyond G0, not accepted.
- **Unfinished files:** none uncommitted in a worktree of this session. Prepared and not yet used, all in `C`: `prompt-g3-M5-T144.md`, `prompt-g4-M5-T144.md`, `prompt-dcv-M5-T144.tmpl.md`, `seam_reviews_T144.py`, `runs-M5-T144.json`, `wave16_dcv_accept.py`; models for what is still to write: `evidence_map_M5_T143.py`, `backlog_wave15_seam.py`, `pr-body-wave15.tmpl.md`, `prompt-premerge-wave15.tmpl.md`.

## 3. Helpers, commands, checks
- **Reviewers of M5-T144 (cannot be resumed by a new session):** G3 `abc83a74d999e6010` (data-contract-verifier, copy `/root/project/rv-w6-a`), G4 `a422074e9131a95c8` (qa-engineer, copy `/root/project/rv-w6-c`). If `C/return-g3-M5-T144.txt` and `C/return-g4-M5-T144.txt` exist, the returns were saved unchanged and are the review evidence. If not, start fresh reviewers with the two prepared briefs (never pass `model:`).
- **The owner's test preview** runs from `/root/project/w-wave14` on 127.0.0.1 ports 3001 and 8000: `bash C/preview_results_screen.sh status|stop|start <checkout>`. Stop it before any local build or browser run that needs those ports.
- tmux session `buildability` (one window). No background command of this session is running. The push of this file starts one CI run on the branch: records and this file only.
- Review copies `/root/project/rv-w6-a|b|c` are detached at `582dcccb`. Old worktrees `w-wave13`, `w-wave15`, `w-lean` hold merged branches.

## 4. Exact next action
1. Start checks (read only), then `git -C /root/project/w-wave16 status` and `log -3`.
2. **Finish M5-T144** in `/root/project/w-wave16` by the wave-15 routine (`C/SESSION_NOTES.md`, STATE lines of 03:15 and 03:51): review record (`seam_reviews_T144.py`), evidence map, progress 90, commit; submit; G2, G3, G4 at that head; commit; `verified-M5-T144.txt`; rule check (ten rows); `wave16_dcv_accept.py record|accept` (the arrival time from `save_return.py`'s output, never guessed); ledger accept; backlog sweep; validator; final push; pull request; read both runs; description; pre-merge check; fail-closed merge (`/root/project/lanes-runtime/merge/merge_failclosed.py`); pull. A review finding goes to a NEW `rules-engineer` builder. The tolerated later paths now include `docs/SESSION_HANDOFF.md` (this file rides on the branch).
3. After the merge: restart the preview from the merged head, take pictures, and tell the owner in four bullets (the new label and the corrected rear-yard reason are visible).
4. Then section 6, item 2.

## 5. Blockers, holds, decisions
- **Waiting for the owner (none blocks the work):** may the coding rule say that local browser tests are started the way CI starts them (backlog DB-207 d); the fewer-checks picture (orchestrator's recommendation: no change); the instruction-file list (nothing moves before the answer); keep or remove one memory note and one superseded file (status report of 2026-10-08); an upper limit for the entered floor height (before any switch-on); the converter and storage at the PDF step.
- **Decided by the owner on 2026-10-09 (never ask again):** the overall label `Preliminary zoning results` (R641); M5-T143, then the bounded fixes, then the first building shape, the floor schedule and the apartment estimate (R643, R663); the height-data defect is repaired and tested before drawings or estimates use those values (R661, R662); completed research is reused, blockers are named as missing property fact, unresolved law or code not built, no new reading before a list says which are necessary (R645, R650, R651); updates are four bullets (completed product work; current work; blocker or decision; next visible deliverable) that tell maintenance from new capability, with links (R655, R666, R667). Records: D-090 `source-065-amendment.md`, `source-066-amendment.md`.
- **Changed this session with the owner's approval:** two lines of `.claude/rules/CODING_RULES.md` (R637 to R640): focused checks on the build machine; every full suite and security check green in CI on the exact head before any gate, acceptance or merge. The simplification (R633 to R635, R657): evidence written once; only reviewed heads and the final head are pushed.
- **Standing restrictions and the owner's text on what "finished" means: unchanged.** Read them in `git show 7f0e131f:docs/SESSION_HANDOFF.md` (sections "Standing restrictions" and "What finished means") and in D-090 `source-030` and `source-062`. Among them: Tier D stops; never merge pull request 241; the expansion hold; every production switch off; never pass `model:`; no security waiver; no timer, watcher or unattended merge; a withheld result never shows a number; never ask the owner for professional review.

## 6. Remaining work (replaces the old waiting list; each item checked against the repository on 2026-10-09)
**Completed research, not to be repeated:** the nine R6B reference cases in `docs/reference-cases/R6B/cases/` (steps P1 to P5; `step-p5-worked.json` is task M4-T035, merged 2026-10-08); the 185 law captures in `docs/research/zr-snapshots/v1/`; the measurement-basis record (M5-T135). Which case row settles which question for a building shape: `C/drafts/necessary-readings-first-shape.md` (checked row by row). A helper's wider study, to be checked before use: `C/drafts/shape-estimate-dependencies.md`.

In order:
1. **M5-T144** (section 4).
2. **Step P6: one independent hand-worked example of a first building option** (two readers working alone from a sealed folder of the EXISTING captures, then a `rules-engineer` writes the case; models `session-2026-10-07a/build_sealed_packet.py` and `session-2026-10-08a/prompt-blind-reading-P5.tmpl.md`, `prompt-builder-M4-T035.md`). It is the only new reading that is necessary. It holds the one point of law not yet read independently: whether a building may stay below the minimum base height (ZR 35-631(b), 23-431(b), 23-436(e): captured). Not started.
3. **Lot coverage by portion of a corner lot** (code not built; the law is read: `corner-reach#real-lot-coverage`, `interior-lots#interior-coverage`).
4. **The building option's generator and the floor schedule** (code: `building_option.py` gives a 2-floor sample that the decision module withholds). After items 2 and 3 and after M5-T144 has merged (R662). Three property facts are missing (how the adjoining lots' lot lines meet this lot; the neighbouring buildings' street walls; ground elevations): show a clearly conditional scenario on stated assumptions, never a confirmed shape.
5. **The preliminary apartment estimate** (code not built; the owner's values R540 to R544; the reserved block R568). Check the task statuses behind row R546 before contracting it.
6. **The screen change that shows them:** useful results first, fewer repeated explanations, every condition tied to its result (R652 to R654); backlog DB-208 a to c; the dashboard's own text "Zoning maximum not available".

Later, unchanged and open: a wording task for the frontage line and two route messages (DB-206 c); a lot with no outline (DB-203); sign-in and the height limit (DB-204); the open question of DB-199 c; the setback above the base and the rear yard beyond the corner area (code); the four approved handoff changes as one governance task (R574 to R578: not built); twelve older packets (DB-191); steps 6 to 8 of the owner's order (the other options, the report, the PDF).

Removed from the old list because done: the piece that emits the results document (M5-T136), the results display (M5-T140, M5-T142), the reading of the captured law texts (M4-T035).

## 7. The one-time workflow audit of this session
Report (not committed, raw records stay on the server): `C/SESSION_WORKFLOW_AUDIT_2026-10-08_5b29ad99-7c30-4e36-8c3f-cf862905fe8f.md`. Its cutoff is in `C/audit-final-cutoff.txt`. The audit ends with this handoff; the next session does not continue it.

## Authoritative files (smallest set)
`CLAUDE.md`; `python tools/project_control.py status`; `project-control/tasks/M5-T144.json`; `docs/DISCOVERY_BACKLOG.md` (rows DB-196 to DB-209 and the last sweep lines); D-090 `requirements.json` rows R617 to R668.

## COPY INTO THE NEW SESSION
```
Resume as the NYC Buildability orchestrator. Start: tmux, then `cd /root/project/nyc-buildability && claude` (no MCP servers).
Read-only checks first; change nothing until they pass: `git status`, `git worktree list`, `tmux ls`, ListAgents, `python tools/project_control.py status`.
The current handoff is NOT in this folder yet: read `/root/project/w-wave16/docs/SESSION_HANDOFF.md` (branch task/wave16-server-corrections) in full; the copy here is the old one. Then `C/SESSION_NOTES.md`, last two STATE lines (C=/root/project/lanes-runtime/owner-docs/session-2026-10-08c).
Next action: finish task M5-T144 in /root/project/w-wave16 (its two reviews were running at handoff: use the saved returns if C/return-g3-M5-T144.txt and C/return-g4-M5-T144.txt exist, else start fresh reviewers with the prepared briefs), then section 6 of the handoff in order. Do not repeat completed research (handoff section 6).
Standing restrictions are unchanged: read them where section 5 of the handoff points. Updates to the owner: four short bullets with links, telling maintenance from new capability.
Report READY TO RESUME or BLOCKED.
```
