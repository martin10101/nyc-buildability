# M0-T191 reviews (every return kept unchanged)

- G3 round 1: code-reviewer at 67a4b844, PASS with one advisory (characters vs bytes), returned 2026-10-11 03:12 UTC; saved by script as session-2026-10-11a/return-T191-code.md.
- G3 round 2: a fresh code-reviewer at c703a571 (delta 1: the D-090-R941 pointer and the advisory applied), PASS with one cosmetic advisory (the correction tag sits after 'principle 21'); not applied, so the reviewed files stay byte-identical. Saved as session-2026-10-11b/return-T191-code-r2.md.
- Identity note: the gates are recorded at a later head of the same branch. The commits after c703a571 (5b81aeee, 41c6778f and this record) touch only M5-T158's packet, placeholders and control records; the four M0-T191 files are byte-identical to c703a571 (git diff c703a571..HEAD on the packet's allowed paths is empty; this reviews file and the evidence map are control records outside them).

## G3 round 2 return

<!-- saved unchanged by save_return.py from agent-a84a731b1543a2559.jsonl, entry 2026-10-11T05:01:46.589Z, sha256 8c3533d22940191da63401b167b6becc5dd237229d3a38e353565482cf7e8b40 -->
# G3 Gate Report — M0-T191 (code-reviewer, independent, read-only, round 2)

**Task:** M0-T191 — "D-093 correction: a delegated agent inherits its parent session's start-time instructions."
**Gate:** G3 (code review). In-regime: D-093 (R029,R032,R034,R068) + D-090-R941. Modularity: N/A (no services/apps/packages; docs + control-plane records only).
**Frozen head reviewed:** `c703a571037c9073b6c0bbbd35a9406a0ea5615d` on `task/wave23-density-zoning-lot` in `/root/project/w-wave20` (worktree HEAD == frozen SHA, `git status --porcelain` empty). Delta over the previously-passed `67a4b844`: one new D-090-R941 PROGRAM_KNOWLEDGE pointer + the earlier G3 bytes/characters advisory applied.

**VERDICT: PASS** (one ADVISORY, non-blocking; no REQUIRED corrections).

## Brief item 1 — record claims re-derived from the three transcripts — VERIFIED
Extracted the first `instructions` attachment of each transcript directly (per-file `content` lengths) and the first user message.
- `2f0aa039` (fresh print-mode, `entrypoint=sdk-cli`, cwd `/root/project/nyc-buildability`, attachment ts 02:58:38.199Z, session start 02:58:37.999Z): CLAUDE.md **14561**, expansion-hold **4027**, CODING_RULES **4537**, **research-and-verification 2452 (present)**, PROGRAM_KNOWLEDGE **17019**, memory **8289** — all EXACT. First user msg asks it to quote the research rule (it had it loaded).
- `agent-a1200433925ba8efc` (code-reviewer), ts **02:58:48.241Z**: CLAUDE.md **14177**, expansion-hold 4027, CODING_RULES 4537, PROGRAM_KNOWLEDGE **17012**, memory 8289, **no research rule** — all EXACT. Its final answer (02:59:01) reads verbatim: "No — there is no rule titled 'Research and verification — required project workflow' in my loaded instructions… (2) and (3): not in my instructions." — matches the record's claim.
- `agent-a7180378d084bf28b`, ts **03:05:24.679Z**: same pre-merge set, no research rule — EXACT. First user msg confirms it is the **M5-T157 builder (DB-231, special density)** and its brief carried the D-093 dispatch clause ("Research and verification (owner directive D-093) applies…"). Read nothing further for this transcript (per brief).
- Pre-merge/merged anchors re-derived from git: `9e107bf3^1` CLAUDE.md = 14178 chars, no principle 21; merged `9e107bf3` = 14562 chars, principle 21 present (line 37). Loaded = git-chars minus one stripped trailing newline (14177/14561, 17012/17019), consistent. Merge committer time 2026-10-11T02:58:22Z; orchestrator session `33a4b56e` first timestamp 2026-10-11T01:25:28Z — confirms "started 01:25 UTC, before the research rule existed." Both pre-merge subagents loaded at/after the ~02:58:28 fast-forward while disk already held the merged files (proven by the 02:58:37 fresh session). **Inheritance reading is evidence-supported.** Untested point stated in both the record ("Not tested: whether a compaction… refreshes the set its later subagents inherit") and §9 ("whether a file changed during the session is picked up at that point was not tested").
- **Corrected line 7 checked:** record says "`CLAUDE.md` 14,562 characters (14,609 bytes)". `git show 9e107bf3:CLAUDE.md | wc -m` = **14562**; `| wc -c` = **14609**; `context_budget_check` independently reports 14609B. Both figures correct; the earlier bytes-mislabel is fixed and tagged `[ORCH-CORRECTED per G3 advisory 2026-10-11 03:12]`.

## Brief item 2 — docs say only what the evidence supports; new pointer matches D-090-R941 — VERIFIED
- Procedure §6 and §9 (`docs/RESEARCH_AND_VERIFICATION.md`) assert only the inheritance fact plus the explicit not-tested caveat; §9 *narrows* the prior "re-read from disk after a compaction" to "attached again… not tested," a conservative correction. §9's "attached again after a compaction (observed 2026-10-11)" is grounded in the accepted M0-T190 report (its resumed session loaded the four unconditional rules "at start … and again after the compaction," §lines 50/97-162). No overstatement.
- First PROGRAM_KNOWLEDGE pointer (D-093) states only the supported fact (subagent inherits parent start-time snapshot; a mid-session merge reaches helpers only through the brief).
- Second PROGRAM_KNOWLEDGE pointer (D-090-R941) checked against `source-084-amendment.md` and the `requirements.json` R941 row: "Owner handoff = NOTHING keeps running" = "when the owner asks for a handoff, nothing the session started keeps running"; "save each helper's unfinished work into the session folder (`git diff --binary`)" = "unfinished work is saved in the session folder (for example a binary diff of its worktree)"; "stop it, record where it is" = "the helper is stopped, and the handoff says where the work is"; "overrides the skill's let-helpers-finish line" = "replaces… the session-handoff skill's advice to let healthy helpers finish." Owner's verbatim words ("I told u to do a handoff why is 2 thinks still running") plus the orchestrator's separately-labelled reading fully support the pointer; it adds nothing the owner did not say beyond that recorded reading. The pointer wraps to two physical lines but is one bullet, satisfying the "one-line PROGRAM_KNOWLEDGE pointer" harness. Applicability: R941 `task_ids` include `M0-T191`; `scope_corrections` documents the binding.

## Brief item 3 — scope — VERIFIED
- `git diff 9e107bf3..c703a571 -- project-control/reports/M0-T190-verification-sessions.md` is **empty** — accepted report untouched; the over-broad sentence it names ("So once the main checkout holds the D-093 files, every delegated agent loads the rule.") exists verbatim at its §4 line 166, and is genuinely over-broad (this very session's pre-merge subagents lacked the rule).
- `git diff --name-only d4636970..c703a571`: the only material (non-control-plane) files are the 4 packet outputs (`.claude/rules/PROGRAM_KNOWLEDGE.md`, `docs/RESEARCH_AND_VERIFICATION.md`, `project-control/reports/M0-T191-delegated-agents.md`, `project-control/reports/M0-T191-producer-report.md`), all in `allowed_paths`, none in `forbidden_paths`. Everything else is control-plane records within the brief's allowance (D-090/D-094 directives + index.json, M5-T157/M0-T191 tasks, state.json, M5-T157-G0 gate, M0-T191-G0/M5-T157-G0 reports) produced by peer wave-23 commits. `docs/SESSION_HANDOFF.md` is **unchanged** in the range.

## Required checks (direct exit codes, run in w-wave20 @ c703a571)
- `python3 tools/context_budget_check.py` → **PASS, EXIT=0** (eager ~10756 tok, no cap per D-093-R074; CLAUDE.md 14609B).
- `python3 tools/research_record_check.py --check` → **PASS, EXIT=0** (5 records structurally valid; none claims Verified).

## Findings
1. **ADVISORY** — `project-control/reports/M0-T191-delegated-agents.md:7`: the inline tag `[ORCH-CORRECTED per G3 advisory 2026-10-11 03:12]` is placed immediately after "with principle 21" rather than adjacent to the corrected "14,562 characters (14,609 bytes)" figure it refers to; a reader could momentarily read it as correcting "principle 21". The figures themselves are correct and the tag text names the right advisory. Cosmetic placement only; non-blocking.

## What I could not check / out of scope
- Full per-requirement directive compliance (D-093 R029/R032/R034/R068 and D-090-R941 end-to-end) and directive-registry integrity (c14) are the packet's separate `directive-compliance-verifier` pass + control-plane CI; I verified only that the R941 pointer faithfully reflects its source and that directive files sit in the brief's control-plane exception set. I did not run `validate_directive_compliance.py --check` (brief directed `context_budget_check` + `research_record_check` for this G3).
- Per the brief I read only the first `instructions` attachment and first user message of each transcript (plus the code-reviewer subagent's final answer to test the record's quote); nothing more from the builder transcript.
- No temporary worktree was created: the w-wave20 checkout already is c703a571 and clean, so checks ran there (no git write command used).

Every quoted file list, size and timestamp reproduces exactly; the reading is supported with both untested points stated; line 7's characters/bytes are both correct; the D-090-R941 pointer matches its source; the accepted M0-T190 report is untouched; scope is clean; both checks PASS. Recommend **PASS**.

END-OF-REPORT


## G3 round 1 return

# G3 Gate Report — M0-T191 (code-reviewer, independent, read-only)

**Task:** M0-T191 — "D-093 correction: a delegated agent inherits its parent session's start-time instructions"
**Gate:** G3 (code review) | **Directive regime:** in-regime, D-093 (R029, R032, R034, R068)
**Frozen head reviewed:** `67a4b8447c7e7111c87cf83e5af27ee84e7de822` on `task/wave23-density-zoning-lot` in `/root/project/w-wave20` (worktree HEAD == frozen SHA, tree clean). Parent = `d46369705...` (single commit).
**Change:** docs/report-only correction; no production source. Modularity policy N/A (no services/apps/packages touched).

**VERDICT: PASS** (one ADVISORY note; no REQUIRED corrections).

## Scope / allowed paths (brief item 3) — VERIFIED
`git diff --name-only d4636970..67a4b844` lists exactly 4 files, all in `allowed_paths`, none in `forbidden_paths`:
`.claude/rules/PROGRAM_KNOWLEDGE.md`, `docs/RESEARCH_AND_VERIFICATION.md`, `project-control/reports/M0-T191-delegated-agents.md`, `project-control/reports/M0-T191-producer-report.md`. No stray files.

## Brief item 1 — transcript claims re-derived from primary evidence — VERIFIED
Read the `instructions` attachment of each transcript directly (char lengths of each file's `content`).
- Fresh print-mode session `2f0aa039` (entrypoint `sdk-cli`, cwd `/root/project/nyc-buildability`, started 02:58:37Z): CLAUDE.md **14561**, expansion-hold **4027**, CODING_RULES **4537**, **research-and-verification 2452 (present)**, PROGRAM_KNOWLEDGE **17019**, memory **8289** — all EXACT.
- Subagent `agent-a1200433925ba8efc` (code-reviewer), ts **02:58:48**Z: CLAUDE.md **14177**, expansion-hold 4027, CODING_RULES 4537, PROGRAM_KNOWLEDGE **17012**, memory 8289, **no research rule** — all EXACT.
- Subagent `agent-a7180378d084bf28b`, ts **03:05:24**Z: same pre-merge set, no research rule; first user message confirms it is the **M5-T157 builder** (DB-231) whose brief carried the D-093 dispatch clause — EXACT.
- "Pre-merge" labels verified against git: `9e107bf3^1` CLAUDE.md = 14178 chars (no principle 21), PROGRAM_KNOWLEDGE = 17013; merged `9e107bf3` = 14562 chars (has principle 21), 17020. Loaded values are git-chars minus one stripped trailing newline, consistently (14177/14561, 17012/17019). The inheritance point is proven: both subagents loaded at/after the 02:58:28 fast-forward yet got the pre-merge snapshot while disk already held the merged files.
- **02:58:48 subagent final answer** (read directly): "No — there is no rule titled 'Research and verification — required project workflow' in my loaded instructions… (2) and (3): not in my instructions." Matches the record exactly.
- **Reading supported:** evidence (post-merge disk, pre-merge inherited set) supports "inherits the parent session's start-time set, does not re-read from disk." **Untested point stated:** the record's Reading says "(Not tested: whether a compaction of the parent session refreshes the set its later subagents inherit.)" and section 9 says "(…whether a file changed during the session is picked up at that point was not tested)." Both present.

## Brief item 2 — docs say only what evidence supports; M0-T190 not edited — VERIFIED
- Procedure §6 (dispatch clause) and §9 (session continuity) additions assert only the inheritance fact plus the explicit not-tested caveat; §9 actually *narrows* the prior "re-read from disk after a compaction" to "attached again… not tested," a conservative correction aligned with D-093. §9's "attached again after a compaction (observed 2026-10-11)" is grounded in the M0-T190 report (its compaction/`/clear`/fork test section, lines 97–213). PROGRAM_KNOWLEDGE pointer states only the supported fact. No overstatement.
- `git diff 9e107bf3..67a4b844 -- project-control/reports/M0-T190-verification-sessions.md` is **empty** — the accepted report is not edited.
- The over-broad sentence the correction names exists **verbatim** in M0-T190 §4 (line 166: "So once the main checkout holds the D-093 files, every delegated agent loads the rule."), and the evidence shows it is indeed over-broad (that session's own pre-merge subagents did not load the rule). Correction is accurate and recorded beside, not inside, the accepted report.

## Required checks (direct exit codes)
- `python3 tools/context_budget_check.py` → **PASS, EXIT=0** (eager ~10702 tok; "no cap: owner D-093-R074").
- `python3 tools/research_record_check.py --check` → **PASS, EXIT=0** (5 records structurally valid; none claims Verified).

## Findings
1. **ADVISORY** — `project-control/reports/M0-T191-delegated-agents.md:7`: "`CLAUDE.md` 14,562 **bytes** with principle 21." 14,562 is the merged file's **character** count; the byte count is **14,609** (confirmed by `context_budget_check` reporting "14609B" and `git show 9e107bf3:CLAUDE.md | wc -c`). The rest of the record correctly labels its figures "characters as the transcript records them." A units mislabel in a provenance record under D-093's measurement-basis discipline; does not affect the correction's substance. Non-blocking.

(Context, not a finding: merge committer date is 02:58:22Z while the record says files reached the checkout at 02:58:28Z — the ~6s gap is the local fast-forward vs the GitHub merge-commit timestamp; internally consistent.)

## Conclusion
Every quoted file list, size, and timestamp reproduces exactly from the three transcripts; the 02:58:48 subagent's final answer matches; the reading is evidence-supported with both untested points stated; the docs changes are conservative and faithful; the accepted M0-T190 report is untouched; scope is clean; both required checks PASS. Recommend **PASS**; the single ADVISORY (bytes vs characters) may be corrected opportunistically but does not block acceptance.

END-OF-REPORT