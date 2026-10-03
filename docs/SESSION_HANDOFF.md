# SESSION HANDOFF — seq 137 (2026-10-03 ~14:45–18:00 UTC; Claude Code session 966ea9e4 / 01AjePR92H83Yc5jH81uya6d, claude-fable-5-1; directive D-090 source-013)

Orientation only. The ledger (`python tools/project_control.py status`) and `project-control/` WIN over this prose. Seq 136 is in git (#354).

## Identity (live at generation)
- **Machine:** the DigitalOcean droplet, not the owner's PC. Peak memory ~17 %; up to 4 robots at once; ~20 robot runs.
- **Repo:** `/root/project/nyc-buildability` = origin `candidate/D-024-mrl-option-b` @ `ec68fb71` (integration head after #364; this handoff PR is written in a worktree off it). Primary checkout clean.
- **CLIs:** claude (Fable 5.1); codex installed, not signed in — the Codex/loop track is DEFERRED by the owner (D-090-R084).
- **Running:** nothing — no loop, no supervisor, no live subagent. Use the ledger + git for state.
- **Server venv:** `/root/project/lanes-runtime/venv/bin/{python,ruff}`; run api tests from `services/api` cwd.

## Owner decisions in force
- New this session: #355 captured D-090 source-013 (the seq-136 resume prompt) — R090 resume harness, R091 next-action order. No other new owner directive landed.
- Standing: Option B merges (a different agent's PASS at the exact head, all CI green, `--match-head-commit` full sha); `LANE_A_ENABLED` off; capacity wording settled (R038); never PR #241; expansion §2 hold; never pass `model:`; no local npm/node; dependency security no waiver; up to 10 robots, memory under 70 %.

## Done this session (all merged after an independent PASS at the exact head + green CI)
- **#355** D-090 source-013 capture (R090 resume harness, R091 next-action order).
- **#356** Lane C: the :3001 e2e server gets `INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED` + `INTERNAL_PARITY_UI_ENABLED`; `.gitignore` un-ignores `services/api/app/rules/coverage/` (the Lane C path for #349's red lane check).
- **#357** lane status refresh A–E from the PR record.
- **#358** D-12 slice 2: flag-on e2e for the Hidden issues window over the real W2 route + flag-off spec.
- **#359** D-15 slice 2: transit/parking zone section in the parity window (round-1 FAIL on a hanging vitest test → fixed → delta PASS).
- **#360** D-06 slice 2: "Existing building — keep or remove" step with the existing zoning floor area and its source.
- **#363** Lane C request D-3: `enterSiteFactAssumption` store op.
- **#361** Lane B request D-2 part 1: recorded transit `detail` names the dataset without its id, byte-identical to the fixture.
- **#362** docs seam: requests D-2/D-3, D-1 done, DB-111/DB-112, status D/C/B, PROGRAM_KNOWLEDGE ×3, WORKING_KNOWLEDGE "2026-10-03c".
- **#364** Lane D adopts the D-3 op; D-3 State done. Integration head after #364: `ec68fb71`.

## Open PRs
- **#349 A-01** rule-coverage matrix — reviewed PASS; base merged in at 2e2d9312 (remerge-diff empty, net-diff patch-id unchanged vs the reviewed content); all checks green; **waits for the owner's yes**.
- **#353 A-04 slice 1** three answers on the 215-16 Northern benchmark — reviewed PASS at f47cf233; all checks green; **waits for the owner's yes** (merge the base in and prove it empty before merging).
- #268 E-03 draft (rebase after #353). #241 never. #64 old.

## Owner questions (plain words; none decided)
1. **Yes to merge #349 and #353?** Both reviewed PASS, both behind the off switch; merging them turns nothing on.
2. **The Windows `supervisor-bridge` CI job flaked 3× today** in two timing-sensitive real-process tests (DB-111; paired runs of the same commit passed; no PR touched supervisor code). Spend a contracted test-side hardening packet now, or keep rerun-to-green with the record while the Codex/loop track stays deferred (R084)? Default = rerun.
3. **D-2 remainder:** the check-needed transit/parking prose and `missing_source` still name the DCP dataset ids as the source to check (DB-112). Leave as the only place that id lives in the payload, or move it to Source?
4. Carried from seq 136: the tax-lot-only warning tag; B-11 Q-B11-1..3; Q1/Q12 pilot lot + licensed checker; Q4; Q8; Q10; E-02 WeasyPrint runtime; OD-B / B-027 PIN deferred with Codex.

## Standing restrictions
Tier D / Section 20 stops; never merge #241; expansion §2 hold; zoning-math (Lane A) merges need the owner's explicit yes per PR; `LANE_A_ENABLED` off; the settled capacity wording never changes; Codex/loop commissioning and the B-027 PIN text are DEFERRED (R084); never pass `model:`; dependency security: no waiver; no local npm/node.

## Authoritative files (smallest set)
`project-control/state.json`; `project-control/directives/D-090-*/{requirements,manifest,verification}.json`; `docs/lanes/queues/*.md` + `docs/lanes/status/*.md` (status files follow the PR record); `docs/lanes/requests/*.md`; `docs/DISCOVERY_BACKLOG.md`; `docs/WORKING_KNOWLEDGE.md`.

## EXACT NEXT ACTION (successor)
1. Gate 0 → READY TO RESUME or BLOCKED. `gh pr list`.
2. If the owner said yes: merge **#349** (`--match-head-commit` full sha of 2e2d9312 after confirming CI is still green), then **#353** (merge the base in, prove empty with `git show --remerge-diff` + patch-id, CI green, merge). Then Lane C **C-07** (after #349); Lane A **A-05** and the **E-03** rebase (#268) (after #353).
3. If no yes: nothing in the lane queues is unblocked; do not start Codex/loop work (R084); answer the owner's questions only when asked.
4. Lane D remaining items are all blocked (D-07 A-06, D-08 Q8, D-10, D-11 A-07, D-13 Q10, D-14 A-04 + E-04, D-02 Q4). Lane B has nothing without answers (plus the D-2 remainder decision).
5. Each build: lane branch off the integration head → producer in an isolated worktree → a DIFFERENT read-only reviewer posts PASS at the exact head and verifies the PR body → merge base in if CI is stale → `gh pr merge --merge --match-head-commit <full-sha>`. Zoning-math PRs: the owner's yes first.

## COPY INTO THE NEW SESSION
Owner, before starting: `cd /root/project/nyc-buildability && git pull --ff-only && claude`. `/mcp` must list none.

Resume as the NYC Buildability orchestrator (Fable 5.1; verify with /model). Work only from repository evidence; this prompt is orientation so you can start cheaply — do NOT re-read the product plan, the lane status files or the directive registry to re-derive it.

START (Bootstrap Gate 0, about 5 tool calls): cwd must BE /root/project/nyc-buildability (repo root), branch candidate/D-024-mrl-option-b, HEAD == origin, /mcp empty, memory under 70 %. Then read ONLY docs/SESSION_HANDOFF.md (seq 137) and run `python tools/project_control.py status` (the ledger wins over prose) and `gh pr list`. Report READY TO RESUME or BLOCKED.

WHERE WE ARE: the green baseline holds. Ten PRs merged this session (#355–#360, #361, #362, #363, #364); integration head `ec68fb71`. Two engine PRs are reviewed PASS and WAIT FOR THE OWNER'S YES: #349 A-01 (rule-coverage matrix) and #353 A-04 slice 1 (LANE_A_ENABLED off). Nothing in the lane queues is unblocked until that yes.

HOW WE WORK (do not re-derive): lane items run as lane-branch PRs under the lean process — producer subagent in an isolated worktree (reset to the integration head first; show-toplevel guard; exact lane paths per docs/lanes/OWNERSHIP.yaml; `python3 scripts/lanes/check_lane_paths.py` and `python tools/modularity_check.py --check` with DIRECT exit codes; never npm/npx/node locally — web tests prove only in CI) → you push and open the PR → a DIFFERENT read-only reviewer subagent posts PASS at the exact head and verifies the PR body → merge base in if CI is stale → `gh pr merge --merge --match-head-commit <full-sha>` once all checks are green (Option B). Up to 10 subagents at once; memory under 70 %. Never pass `model:` on a dispatch. Capture every new owner instruction with /directive-compliance before acting (mid-turn owner messages live in `queued_command` attachments in the transcript).

NEXT ACTION, in order: (1) ask the owner in one short plain message for the yes on #349 and #353, and the flake-hardening question (spend a packet now vs rerun-to-green, loop track deferred); (2) if yes: merge #349 then #353, then Lane C C-07, Lane A A-05 and the E-03 rebase (#268); (3) if no yes: nothing is unblocked — do not start Codex/loop work; answer owner questions only when asked.

STOPS: Tier D / Section 20; PR #241 never; the expansion §2 hold; zoning-math (Lane A) merges need the owner's explicit yes per PR; LANE_A_ENABLED stays off; the settled capacity wording never changes; Codex/loop commissioning and the B-027 PIN text are DEFERRED by the owner (R084); dependency security has no waiver; explain things to the owner in plain, simple words.
