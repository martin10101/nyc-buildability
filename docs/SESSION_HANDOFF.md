# SESSION HANDOFF — seq 139 (2026-10-04 ~05:15 UTC; owner-invoked /session-handoff; Claude Code session 0ba6d6a3 / 01AjePR92H83Yc5jH81uya6d, claude-fable-5-1; directive D-090 sources 015–021)

Orientation only. The ledger (`python tools/project_control.py status`) and `project-control/` WIN over this prose. Seq 138 is in git (#365).

**Turnover reason (owner, verbatim):**
> find a seam and do the handoff make sure the handoff has enough information that the next session has easy job to get restarted, and everything also 4000 tokens can be removed. If you need more tokens for the season handoff, that's okay, but don't start right now making a big deal out of it.

## Identity (live at generation)
- **Repo:** `/root/project/nyc-buildability` = origin `candidate/D-024-mrl-option-b`; integration head at generation `14447e17` (#403 merge). This file is written in worktree `/root/project/w-handoff7`, branch `task/session-handoff-2026-10-04`. Primary checkout clean. Orchestrator worktree still present: `/root/project/nyc-scopeall` (detached at 136580d7 = the rebuilt 12-assumption scope branch, pushed as `task/R108-scope-all-assumed-inputs`). ~250 stale `rv-*`/`w-*`/lane worktrees from earlier sessions remain (housekeeping, not urgent).
- **Running at generation:** no loop, no supervisor, no live subagent; `campaign_continuity --status` prints restrictions only (no active campaign) → use the ledger + git.
- **Server venv:** `/root/project/lanes-runtime/venv/bin/{python,ruff}`; api tests from `services/api` cwd; web proves only in CI.

## Owner decisions in force (this session; D-090 R099–R131)
- **R106–R115** (message 45): accurate wording; height discrepancy first; scope beside the numbers; one journey; approvals explained not granted; CI proposal tightened; switches off; one consolidated update. **R116** reviewer prompt (delivered in chat).
- **R117–R123** (the owner's independent reviewer's audit, forwarded): corrections to the walkthrough, height note, scope, journey plan, #382 body, CI record; decisions carried. **R124–R127** (second check): the envelope street fetch and the map renderers EXIST — connect, don't rebuild; **HOLD #388 and the CI change** until corrections are verified; status language must not overstate; passing tests never close a named gap. **R128–R131** (third check): #383 title/body; every Lane A step needs the owner's yes; a PR run is NOT re-run when the base advances; special-district/special-density assumptions disclosed.
- Standing: Option B merges (a different agent's PASS at the exact head + all CI green + `--match-head-commit` full sha); Lane A merges need the owner's yes **per PR**; `LANE_*_ENABLED` and `INTERNAL_STUDY_READ_ENABLED` off; capacity wording settled (R038: "Remaining development capacity: Not confirmed" no period / "Needs verified zoning-lot boundaries and existing zoning floor area." with period); never PR #241; expansion §2 hold; never pass `model:`; no local npm/node; dependency security no waiver; ≤ 10 robots.

## Done this session (merged after an independent PASS at the exact head + green CI)
#381 CI duplicate-runs inspection · #383 walkthrough + evidence (title/body later corrected: components on test inputs, NOT a complete request) · #384/#393/#396/#399/#401 directive captures (sources 017–021) · #385 CI proposal tightened · #386 journey plan + accurate framing · #402 docs corrections per the audit (walkthrough, journey plan incl. Lane A owner-yes rows, CI record incl. both losses, scheduled audits only, policy narrowing, no auto re-run on base advance) · #387 results 1.1.0 `scope` slot · #389 its test snapshots · #390 B-03 geometry → study read (fixture path; lot_type corner) · #391 evaluator_inputs 1.1.0 inert existing_building slot · #394 docs seam (DB-118/119/120) · #395 cards show the scope with assumptions OPEN by default · #397 B-05 evidence → study read (honest unknown; 39,934 sq ft set aside because DOB job 421803891 says one zoning lot of tax lots 1 & 70) · #398 scope printed on the site plan + DXF notes · #400 study_setup → study bridge (corner lot: two frontages → `build_evaluator_inputs` fails closed; open rule question) · #403 Lane B `street_data_for_lot` connects the B-03 wrapper to the EXISTING envelope street fetch (URL byte-identical to the recorded query; same corner SiteGeometry; no new connector).

## Open PRs (state at generation)
- **HELD by the owner (R125):** #388 R107 height finding + computed note + 30/45/65; corrected at 2ff2dada (draft register; §23-432 fingerprint recheck recorded; note-dropped-before-document test); both delta attestations PASS; 46/46 green. **The CI proposal** (no workflow change exists; the record is corrected in #402).
- **Owner's yes needed (Lane A), all reviewed PASS + 46/46 green:** #369 A-05 (no duplicate options), #377 A-06 (add-on model), #382 A-07 step 1 (ZR 54-41/54-40/11-23 source text; body corrected to 36 provisions), **#405** (supersedes #392, which is CLOSED): engine emits the scope with all 12 assumed inputs + Northern fixture + Lane E drawing vocabulary and snapshots (head 3bc82a07, task/ branch) — needs the FULL api pytest at head, an independent review, THEN the owner's yes.
- **Needs an independent review before merge:** #404 Lane D plain-word labels + value words for the 7 new scope keys (92393ae0; producer self-checks only; web proves in CI).
- Never: #241. Old: #64.

## Sub-agents at generation
None running. One stop recorded: the Lane E vocabulary producer (agent aef913d6e7eb9079e) finished its edits, targeted suites (1633 passed) and modularity check, then its FULL pytest hung for ~50 min; the orchestrator harvested its 7 uncommitted files byte-for-byte into `/root/project/nyc-scopeall`, re-ran ruff + the targeted suites (1632 passed, 1 known DXF timing flake), committed as `[ORCH-HARVEST]` 3bc82a07 on #405, and stopped the agent (its final message, received after the stop: full regression 7749 passed / 4 skipped on the identical tree). Never resume it.

## What is still NOT done (say so plainly in every owner update)
- Live geometry binding: Lane C must bind the study read's `geometry_provider` (#390 seam) to `street_data_for_lot` (#403) behind `LIVE_SPATIAL_PROVIDER_ENABLED` and refresh the stale comment in `app/api/v1/study_inputs.py` (~lines 333–345). Until then production study reads show lot_type unknown.
- Maps: `app/drawings/maps` renderers exist (E-07) but are not connected to this lot's results/study document (no `map_context`). Lane E/C task; not started.
- R107 note is dropped before the results document (DB-119): needs a Lane C additive results slot, Lane A emitter, Lane D display.
- Corner-lot frontage governing rule (two frontages; G6 question) — Lane A+C; DB-121 to record at the next docs seam.
- DOB connector (B-05 live) — Lane B, not started. Address step: Geoclient connector + flag-gated route exist; record a fixture and exercise them on the recorded path (no owner decision).
- Next docs seam: DB-121 (corner frontage), DB-122 (reviewer prompts must `git grep` any "does not exist" claim); `docs/WORKING_KNOWLEDGE.md` session section; lane status files.
- Owner-facing: a corrected consolidated update (R115/R126) built only from the PR record, listing decisions: yes/no per Lane A PR (#369, #377, #382, #388 after the hold, the 12-assumption scope PR); accept/reject the CI policy change after the corrected record; M1-05 Q1/Q12; E-02; Q4; B-001.

## Standing restrictions
Tier D / Section 20; never merge #241; expansion §2 hold; Lane A merges need the owner's yes per PR; #388 + CI change HELD; `LANE_*` off; settled capacity wording never changes; Codex/loop commissioning deferred (R084); never pass `model:`; dependency security no waiver; no local npm/node; cross-lane orchestrator corrections go on a `task/` PR (the lane-path check fails them on lane-* branches); run the FULL `services/api` pytest before any api PR (shared fixture dirs feed snapshot suites); a PR's checks are NOT re-run when the base moves — merge the base in, prove the merge empty.

## Authoritative files (smallest set)
`project-control/state.json`; `project-control/directives/D-090-*/{requirements,manifest}.json` (R099–R131); `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md` (corrected in #402); `docs/walkthroughs/2026-10-04-215-16-northern-blvd.md`; `docs/ci/DUPLICATE_RUNS_INSPECTION_2026-10-04.md`; `docs/DISCOVERY_BACKLOG.md` (DB-118–DB-120); `docs/lanes/status/*.md`.

## EXACT NEXT ACTION (successor)
1. Gate 0 → READY TO RESUME or BLOCKED. `gh pr list`. Merge the handoff PR (branch `task/session-handoff-2026-10-04`) when its reviewer PASS is on it and CI is green.
2. Dispatch a read-only reviewer for #404 (Lane D labels); merge when PASS + green.
3. #405: run the FULL api pytest at 3bc82a07 (a worktree; the known DXF timing guard may redden under load — rerun alone), dispatch an independent G3/G4 review (incl. the C-4 guard extensions and the two snapshot diffs), then ask the owner's yes for #405 (not #392). Then merge #404 after its review.
4. Lane C: bind the live geometry provider behind the flag, fixture-tested; then wave-1 item 2 (B-04 street width → study read).
5. Send the corrected consolidated owner update (R115/R126) only from the PR record; mark #388 and the CI change HELD; list the decisions.
6. Each build: lane branch off the integration head → ROSTER producer in an isolated worktree (reset to head; show-toplevel guard; FULL pytest) → a DIFFERENT read-only reviewer PASS at the exact head + body check → `gh pr merge --merge --match-head-commit <full sha>` on all-green.

## COPY INTO THE NEW SESSION
Owner, before starting: `cd /root/project/nyc-buildability && git pull --ff-only && claude`. `/mcp` must list none.

Resume as the NYC Buildability orchestrator (Fable 5.1; verify with /model). Work only from repository evidence; this prompt is orientation so you can start cheaply.

START (Bootstrap Gate 0, about 5 tool calls): cwd must BE /root/project/nyc-buildability (repo root), branch candidate/D-024-mrl-option-b, HEAD == origin, /mcp empty, memory under 70 %. Read ONLY docs/SESSION_HANDOFF.md (seq 139; if the PR from branch task/session-handoff-2026-10-04 is still open, read it from that branch and merge it when green with a reviewer PASS on it), run `python tools/project_control.py status` (the ledger wins) and `gh pr list`. Report READY TO RESUME or BLOCKED.

WHERE WE ARE: the owner's independent reviewer audited the 2026-10-04 wave three times; every finding is captured (D-090 R117–R131) and corrected or in flight. #388 and the CI proposal are HELD by the owner. Lane A PRs #369/#377/#382 wait for the owner's yes; #392 will be superseded by the 12-assumption scope PR. Nothing claims a complete address-to-screen journey: the pieces work on recorded fixtures; live geometry, maps, the DOB connector, the corner-frontage rule and the visible height note are still open and listed above.
