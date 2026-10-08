# D-090 source-062 (amendment): owner messages 121 and 122, 2026-10-08 - the start prompt at once; a workflow audit of one session; a lighter routine handoff and shorter chat updates

Captured 2026-10-08 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5). A script copied the raw text from the saved session transcripts under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped. Every fragment quoted in a requirement row was checked to be an exact substring of its message.

| Message | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| 121 | `63113ab3-654f-4726-b052-febc1c3b4433.jsonl` | 1246 | none (a queue entry carries no uuid) | 2026-10-08T06:42:56.867Z | queue entry holding the typed text | `163e148b09b271bb7a09c7a031a636e7af5d579a70c93851292bb30276d71c35` |
| 121 | `63113ab3-654f-4726-b052-febc1c3b4433.jsonl` | 1248 | `127503b0-a385-4f6d-9cd8-198cfcbc1ae9` | 2026-10-08T06:42:57.009Z | user line (the same text) | `163e148b09b271bb7a09c7a031a636e7af5d579a70c93851292bb30276d71c35` |
| 122 | `5b29ad99-7c30-4e36-8c3f-cf862905fe8f.jsonl` | 66 | none (a queue entry carries no uuid) | 2026-10-08T06:45:57.357Z | queue entry holding the typed text | `80a3be5e4ec9b56023a594af575c61a9a9a4ca09bd87ab3cb9a526133f31a2d6` |
| 122 | `5b29ad99-7c30-4e36-8c3f-cf862905fe8f.jsonl` | 76 | `264fdc40-d26b-4456-ad3b-a79732c3e9b6` | 2026-10-08T06:45:57.357Z | attachment line holding the message as delivered to the running turn (the same text) | `80a3be5e4ec9b56023a594af575c61a9a9a4ca09bd87ab3cb9a526133f31a2d6` |

The blocks below hold the raw texts unchanged (60 and 18779 characters; the digests are of the raw texts).

Context. Message 121 arrived during the handover of seq 151, about 31 minutes after the handoff command: the session had first completed the merge of wave 8 and was then waiting for the handoff pull request's checks and its independent check. The start prompt was printed at once. Message 122 is the first message after the owner cleared the session; it arrived while the session was finishing the landing of the handoff's pull request (the independent check had just returned PASS). It has four parts with no break between them: (a) the start prompt the previous session printed, pasted back; (b) from "For this next session only", an audit of how this one session works; (c) from "I want routine session continuation to be lighter.", a lighter routine handoff and a shorter form for chat updates; (d) from "For this session only, audit how the work is performed", the audit stated a second time, shorter, with further limits.

A note on source-061: its two rows (R589 and R590) are the orchestrator's readings of a command that carried no text. Each row says so in its own text; the source file has no separate line saying it (a note of the independent check of the handoff of seq 151). A recorded source is not edited, so the statement is made here.

## Owner message 121 (verbatim)

Transcript timestamp 2026-10-08T06:42:56.867Z.

> Just give me the handoff prompt already enough with the test

## Owner message 122 (verbatim)

Transcript timestamp 2026-10-08T06:45:57.357Z.

> Resume as the NYC Buildability orchestrator (verify the model with /model). Work only from repository evidence; this prompt is orientation.
>
> START (Bootstrap Gate 0). Read-only checks first; change nothing until they pass: cwd must BE /root/project/nyc-buildability (repo root), branch candidate/D-024-mrl-option-b; run ListAgents and `tmux ls`; run `git status` (uncommitted and untracked files) and `git worktree list`; /mcp empty; memory under 70 %. If another nyc-buildability session is alive, or there are files you cannot explain: report BLOCKED, write nothing and explain. Never reset, clean, stash or discard work to pass a check. Only after that: `git pull --ff-only` (HEAD must equal origin; it was 20e83480, the merge of wave 8, when this prompt was printed).
>
> THE HANDOFF FILE (seq 151) is on pull request 471 (branch task/session-handoff-2026-10-08b, head f264db7a4c4552f16e2c42bcbc6b8f17f8aa9b29, worktree /root/project/w-handoff17). The owner asked for this prompt before that pull request's checks and its independent audit had finished. Run `gh pr view 471 --json state`. If MERGED: read docs/SESSION_HANDOFF.md in the main checkout. If still OPEN: read /root/project/w-handoff17/docs/SESSION_HANDOFF.md, then finish its landing before any other work: read its 46 checks by hand; look in /root/project/lanes-runtime/owner-docs/session-2026-10-08b/SESSION_NOTES.md for the audit's result (if no PASS is recorded there, run one independent read-only audit with a progress-auditor, from prompt-audit-handoff-151.tmpl.md in that folder with the head and the number filled in); merge only with `python3 /root/project/lanes-runtime/merge/merge_failclosed.py 471 f264db7a4c4552f16e2c42bcbc6b8f17f8aa9b29 --expected /root/project/lanes-runtime/merge/expected-checks.tsv`; then `git pull --ff-only`. Read CLAUDE.md. Run `python tools/project_control.py status` (the ledger wins) and `gh pr list`. Report READY TO RESUME or BLOCKED.
>
> WHERE WE ARE: the owner wants the FULL feasibility report comparable to their sample PDF, with reliable numbers, for all of R1–R12, built one piece at a time; a finished piece is a milestone, not completion. Merged and tested: everything through wave 8 (the decision module and its wiring beside the engine, the reference rows, the measurement-basis record with the owner's decisions, 185 law-text captures); the main line's own run on the wave-8 merge completed with every job a success. Nothing emits the three-way results document, nothing calls the decision module from a route, and nothing of the report is visible on a screen beyond what existed. THE OWNER DECIDED on 2026-10-08 where five results are carried (as recommended: rear yard and setback with the envelope results; the three legal unit limits with the floor-area results; the apartment-estimate section reserved for the preliminary capacity estimate) and approved four handoff changes (three not built yet); fewer checks are NOT approved; the instruction-file list was pasted to the owner and is NOT answered: move nothing.
>
> NEXT ACTION, in order: (1) the handoff's "Waiting work" item 1: read the draft of the piece that first emits the three-way results document (/root/project/lanes-runtime/owner-docs/session-2026-10-08b/drafts/spec-emit.json and return-draft-emit.txt beside it; one helper's unchecked draft; it leaves three questions), check it against the code, contract it and build it; (2) then the results display; (3) beside them, by read-only helpers: the exact fewer-checks proposal the owner asked for; (4) record, with the next ledger change, the owner's message of about 06:38 UTC on 2026-10-08 ("Just give me the handoff prompt already enough with the test"): from now on print the start prompt as soon as the handoff file is pushed, and never make the owner wait for the handoff's checks; (5) owner update in plain words and without tables, short, saying what became usable toward the report, what remains before the results screen works and the next concrete deliverable. Do not end a turn while waiting on GitHub checks: read them by hand and carry on (the owner allows waiting for existing checks inside an active session: no automatic rerun, no unattended merge).
>
> STOPS: Tier D (production approval, payments, secrets, paid accounts); PR #241 never; the expansion §2 hold; all production switches off and no hidden feature activated; settled capacity wording never changes; never pass `model:`; no waiver of a security advisory, no age exception without a new owner approval, and nothing merged on a run that predates an advisory; no timers, watchers, automatic reruns or unattended merges (one exception: waiting for existing checks inside an active session); fewer checks are not approved; never ask for a secret in chat; never ask the owner for professional review; merge fails closed on any non-success, missing, queued or pending check; never rerun a job without reading its state; at most five helpers at once (at most three building, four reviewing), never two on the same file, a concurrency record before each wave, heavy test runs one at a time, merges one at a time; one ledger-touching branch at a time; every allowed path of a packet a plain literal path; no new spending, access changes or added agents beyond those limits; no building on unmerged work; report completion only when the agreed requirements and tests pass; never drop a sample section or an option without the owner's agreement; no apartment estimator before the corrections are complete and independently reviewed; no option presented as feasible before parking, loading and bicycle requirements are addressed; a withheld result never shows a number, an older or a substitute value; a legal limit and an estimate never share a label; never offer the early simple PDF; never enter a human verdict in the review register; move or remove nothing in the instruction files before the owner approves the list; change the handoff procedure only by the task that builds the four approved changes; a recommendation is not a decision; a question of law is never put to the owner as a preference; when a helper's report says "part 1 of 2", ask for the rest at once; a new session cannot resume this session's helpers, so a correction needs a new builder; a capture's recorded time is the real time of its fetch; for a Windows defect, state nothing about Windows that a run on a Windows test machine has not shown; research is never a blocker; plain, simple words and no tables to the owner; keep updates short.For this next session only, conduct a workflow audit while continuing the work assigned in the handoff.
>
> The purpose is to understand where time and effort go, identify avoidable overhead, and improve future delivery. This is an observation exercise, not an instruction to rush, skip safeguards, or change the normal workflow.
>
> 1. Scope and boundaries
>
> Cover the session from startup and reading the incoming handoff through producing the next normal handoff. Include the main agent and every helper involved.
>
> Continue the agreed work in its existing order, with the existing review requirements, permissions and concurrency limits. This audit does not approve any outstanding product or process decisions.
>
> Do not optimize the workflow during the trial. Record proposed improvements for later. Do not create an audit team, install a monitoring system, or change standing instructions for this exercise.
>
> 2. Capture actions without creating a running essay
>
> Use existing session transcripts, tool records, helper transcripts and ordinary task/CI records as the primary evidence.
>
> Preserve every observable action, including:
>
> - File and directory searches, file reads, edits and writes.
> - Web lookups and documents consulted.
> - Commands, tests, reviews, retries and failed attempts.
> - Helper assignments, results and follow-up instructions.
> - Git operations, task records, approval checks and CI checks.
> - Waiting, interruptions, context compaction and handoff preparation.
>
> Do not repeatedly reread the growing log or rewrite the full report after every action.
>
> Where the ordinary record does not explain an action’s purpose, add a short note at the next natural work boundary. Several related actions may share one purpose note, but every action must remain individually traceable.
>
> Record brief operational explanations, not private internal reasoning.
>
> 3. Account for files and starting context
>
> Inventory the incoming handoff and the instruction files, memory, skills, summaries and task documents supplied or consulted.
>
> Distinguish:
>
> - Confirmed automatically loaded into context.
> - Explicitly read during the session.
> - Configured or available, but not confirmed loaded.
> - Merely listed or returned by a search.
>
> For each file actually consulted, record its path, the question you were trying to answer, why that file was relevant, and whether it provided useful information. Record repeated reads separately and explain them when possible.
>
> Include loading that occurs later, such as nested instructions or context restored after compaction.
>
> Verify what the installed environment can expose. Do not claim visibility into hidden context or every internal file opened by a program. Mark missing evidence clearly.
>
> 4. Make the action record independently checkable
>
> For each observable action, include:
>
> - Event ID and available timestamp.
> - Main agent or helper identity.
> - Action and target: file, command, URL, task or check.
> - Purpose or linked purpose-note ID.
> - Outcome and connection to the assigned deliverable.
> - Source reference in the underlying record.
>
> Include unsuccessful and abandoned work. Label explanations reconstructed afterward as retrospective; label uncertain explanations as unknown.
>
> Distinguish a search across files from actually reading those files.
>
> 5. Measure effort honestly
>
> Classify activity into product implementation, necessary research, verification/security, administration/handoffs, rework, waiting and audit overhead. Allow a primary category plus a rework flag.
>
> Report elapsed session time separately from summed helper time. Account for parallel work so overlapping durations are not added into an inflated total.
>
> Use measured timing and token information where available. Identify estimates and unknowns. Distinguish input, output and cache usage where the records support it. Do not invent per-file costs or treat gaps between timestamps as measured work.
>
> Tag this audit’s setup, notes, extraction and report writing separately. Show directly measurable audit overhead, while acknowledging that extra context and interruptions cannot be cleanly subtracted.
>
> 6. Produce one complete Markdown report at handoff
>
> Save "SESSION_WORKFLOW_AUDIT_<date>_<session-id>.md" in the normal owner-document location.
>
> Include:
>
> 1. Starting objective, repository revision and relevant unfinished work.
> 2. What was actually accomplished, distinguishing drafted, tested, committed, merged and visible to a user.
> 3. Starting-context inventory and later instruction loads.
> 4. Complete chronological action appendix.
> 5. File-access inventory, including repeat reads and their purposes.
> 6. Helper work, tests, reviews, failures and resulting corrections.
> 7. Time/token breakdown, audit overhead and measurement limits.
> 8. Avoidable repetition, blockers and recommendations.
>
> For each recommendation, identify the supporting events, what caused the work, any instruction requiring it, what could change, and what risk that change would introduce. Distinguish useful checks that caught defects from duplicate checks that added no new evidence.
>
> Do not implement these recommendations during the trial.
>
> 7. Check the report’s completeness
>
> Reconcile the action appendix against the available main-agent and helper records. Report missing intervals, inaccessible records and unexplained actions.
>
> Keep original evidence local. Provide sanitized supporting records where useful; exclude credentials, secrets and private reasoning. Do not automatically commit or publish audit artifacts.
>
> Return the Markdown file and its location with the normal handoff. Record a final audit cutoff so producing the report does not create an endless requirement to report on reporting.
>
> If evidence is incomplete, call this a best-effort audit. Do not present one session as proof of the project’s average productivity.I want routine session continuation to be lighter.
>
> When I ask for a session handoff:
>
> - Stop at the nearest safe point. Do not start another batch or make the handoff depend on completing the whole current milestone.
> - A handoff alone does not require a commit, push, pull request, merge, clean working tree or fresh full test run. Preserve unfinished local work. Normal checks still apply when the development milestone reaches them.
> - Safely checkpoint active writers. Do not assume helpers or commands survive closing the session. Record any continuing work and how the next session can check it.
> - Record pending CI or reviews as pending. Do not wait solely to make the handoff look finished.
> - Reuse existing evidence. Do only the small current-state checks needed for accurate continuation. Do not build new handoff tooling or reorganize instructions during the handoff.
>
> Use the existing handoff location. Include:
>
> 1. Exact working directory, branch and revision.
> 2. Completed work and unfinished files.
> 3. Active helpers, commands and checks, with their identifiers or log locations.
> 4. The exact next action.
> 5. Relevant blockers and existing holds.
>
> Reference existing detailed records rather than copying them into the handoff.
>
> For ordinary chat updates, use three to five short bullets: what changed, what I can now use, what comes next, and any decision genuinely needed. Put detailed evidence in the relevant file; give its path and affected lines or section.
>
> If something prevents a quick handoff, explain the specific reason briefly.
>
> This changes routine handoff and communication expectations only. It does not approve the proposed instruction-file moves or remove development checks.For this session only, audit how the work is performed, from reading the incoming handoff through producing the next handoff.
>
> The purpose is to identify where effort goes and what can safely be simplified so more effort reaches the actual product.
>
> Continue the currently agreed workflow, including the lighter handoff procedure. Do not make further workflow changes during this trial.
>
> Recording method
>
> Use existing session transcripts, tool records, helper records and task/check logs as the primary evidence. Preserve them through the audit.
>
> Do not write a running essay or repeatedly rewrite the report. Add only brief purpose notes where the normal record does not explain an action. Related actions may share a purpose note, but each action must remain individually traceable.
>
> Do not install monitoring tools, change logging settings, create an audit team or build an audit framework. If evidence is unavailable, record that limitation and continue the assigned work.
>
> Capture every observable action
>
> Include the main agent and all helpers:
>
> - Searches, directory listings, file reads, edits and writes.
> - Web lookups and documents consulted.
> - Commands, tests, reviews, failures, retries and abandoned attempts.
> - Helper assignments, messages, results and follow-ups.
> - Task administration, Git operations, pushes, pull requests and CI checks.
> - Waiting, interruptions, context compaction and handoff preparation.
> - Work performed solely for this audit.
>
> For each action, record its event ID, available timestamp, actor, target, purpose, outcome and evidence reference.
>
> For every file consulted, record its exact path, what information was sought, why that file was relevant, and what useful information was obtained. Keep repeated reads visible and explain their purpose where known.
>
> Distinguish searching across files, seeing filenames in results, actually reading content, and loading instructions. Do not claim to capture every internal file read performed by a command.
>
> Give brief operational explanations, not private internal reasoning. Label retrospective explanations and uncertain inferences.
>
> Inventory the context
>
> Record the incoming handoff and instruction files, memory, skills, summaries and task records supplied or consulted.
>
> Distinguish confirmed automatic loading, explicit reading, and files merely configured or available. Include later instruction loading and context restored after compaction.
>
> Use the environment’s available evidence. Do not infer that an instruction file was loaded merely because it exists. State what cannot be observed.
>
> Attribute effort fairly
>
> Classify activity as:
>
> - Product implementation.
> - Necessary research.
> - Verification or security.
> - Administration and handoffs.
> - Rework.
> - Waiting.
> - Audit overhead.
>
> Identify which work was required by an owner instruction or standing rule, with its source, and which was your implementation choice.
>
> Separate elapsed time from summed helper time; account for overlapping work. Use measured timing and token usage where available, distinguishing cache usage. Mark estimates and unknowns. Do not invent per-file costs or treat timestamp gaps as measured work.
>
> Record audit overhead separately. Explain that subtracting its direct effort does not completely remove its effects on context and workflow.
>
> Deliver one complete Markdown report
>
> At the next normal handoff, save:
>
> "SESSION_WORKFLOW_AUDIT_<date>_<session-id>.md"
>
> Use the normal owner-document location. Include:
>
> 1. Starting objective and repository state.
> 2. What was accomplished: drafted, tested, committed, merged and usable on screen.
> 3. Starting-context inventory and later loads.
> 4. Complete chronological action appendix.
> 5. File-access inventory, including repeated reads.
> 6. Helper activity, verification results and corrections.
> 7. Effort breakdown and measurement limitations.
> 8. Specific opportunities to simplify future work.
>
> For each proposed improvement, cite the relevant events, explain why the work happened, identify any instruction requiring it, and state what could change and what risk that introduces. Do not automatically treat research or testing as waste. Do not implement these recommendations during the trial.
>
> Reconcile the appendix against available main-agent and helper records. State missing intervals or records explicitly; do not describe an incomplete audit as exhaustive.
>
> Keep raw records private and exclude secrets from the report. Do not create a commit, push or pull request solely for this audit.
>
> Return a maximum of five chat bullets, the exact report path, and the Markdown file as an attachment if supported. Establish a final reporting cutoff so the audit does not endlessly audit its own report writing.

## Reading

| Message | Words of the message | Requirement |
|---|---|---|
| 121 | "Just give me the handoff prompt already" | R591 (obligation) |
| 121 | "enough with the test" | R592 (prohibition) |
| 122 | "Resume as the NYC Buildability orchestrator" "Read-only checks first; change nothing until they pass" "finish its landing before any other work" "Report READY TO RESUME or BLOCKED." | R593 (harness) |
| 122 | "read the draft of the piece that first emits the three-way results document" "(2) then the results display" "(3) beside them, by read-only helpers: the exact fewer-checks proposal the owner asked for" | R594 (sequencing) |
| 122 | "(4) record, with the next ledger change" "from now on print the start prompt as soon as the handoff file is pushed" | R595 (obligation) |
| 122 | "WHERE WE ARE: the owner wants the FULL feasibility report comparable to their sample PDF" "STOPS: Tier D (production approval, payments, secrets, paid accounts)" "keep updates short." | R596 (hold) |
| 122 | "For this next session only, conduct a workflow audit while continuing the work assigned in the handoff." "The purpose is to understand where time and effort go, identify avoidable overhead, and improve future delivery." "Cover the session from startup and reading the incoming handoff through producing the next normal handoff." "Include the main agent and every helper involved." "For this session only, audit how the work is performed, from reading the incoming handoff through producing the next handoff." "The purpose is to identify where effort goes and what can safely be simplified so more effort reaches the actual product." | R597 (obligation) |
| 122 | "This is an observation exercise, not an instruction to rush, skip safeguards, or change the normal workflow." "Continue the agreed work in its existing order, with the existing review requirements, permissions and concurrency limits." "This audit does not approve any outstanding product or process decisions." "Continue the currently agreed workflow, including the lighter handoff procedure." | R598 (hold) |
| 122 | "Do not optimize the workflow during the trial." "Record proposed improvements for later." "Do not implement these recommendations during the trial." "Do not make further workflow changes during this trial." | R599 (prohibition) |
| 122 | "Do not create an audit team, install a monitoring system, or change standing instructions for this exercise." "Do not install monitoring tools, change logging settings, create an audit team or build an audit framework." | R600 (prohibition) |
| 122 | "Use existing session transcripts, tool records, helper transcripts and ordinary task/CI records as the primary evidence." "Use existing session transcripts, tool records, helper records and task/check logs as the primary evidence." "Preserve them through the audit." "If evidence is unavailable, record that limitation and continue the assigned work." | R601 (evidence) |
| 122 | "Do not repeatedly reread the growing log or rewrite the full report after every action." "Do not write a running essay or repeatedly rewrite the report." | R602 (prohibition) |
| 122 | "add a short note at the next natural work boundary" "Several related actions may share one purpose note, but every action must remain individually traceable." "Record brief operational explanations, not private internal reasoning." "Label explanations reconstructed afterward as retrospective; label uncertain explanations as unknown." "Add only brief purpose notes where the normal record does not explain an action." "Give brief operational explanations, not private internal reasoning." "Label retrospective explanations and uncertain inferences." | R603 (obligation) |
| 122 | "Preserve every observable action, including:" "File and directory searches, file reads, edits and writes." "Commands, tests, reviews, retries and failed attempts." "Waiting, interruptions, context compaction and handoff preparation." "Include unsuccessful and abandoned work." "Capture every observable action" "Work performed solely for this audit." "Web lookups and documents consulted." "Helper assignments, results and follow-up instructions." "Git operations, task records, approval checks and CI checks." "Searches, directory listings, file reads, edits and writes." "Commands, tests, reviews, failures, retries and abandoned attempts." "Helper assignments, messages, results and follow-ups." "Task administration, Git operations, pushes, pull requests and CI checks." | R604 (obligation) |
| 122 | "Event ID and available timestamp." "Main agent or helper identity." "Action and target: file, command, URL, task or check." "Purpose or linked purpose-note ID." "Outcome and connection to the assigned deliverable." "Source reference in the underlying record." "For each action, record its event ID, available timestamp, actor, target, purpose, outcome and evidence reference." | R605 (evidence) |
| 122 | "Inventory the incoming handoff and the instruction files, memory, skills, summaries and task documents supplied or consulted." "Confirmed automatically loaded into context." "Explicitly read during the session." "Configured or available, but not confirmed loaded." "Merely listed or returned by a search." "Include loading that occurs later, such as nested instructions or context restored after compaction." "Record the incoming handoff and instruction files, memory, skills, summaries and task records supplied or consulted." "Do not infer that an instruction file was loaded merely because it exists." "Distinguish confirmed automatic loading, explicit reading, and files merely configured or available." "Include later instruction loading and context restored after compaction." | R606 (obligation) |
| 122 | "Verify what the installed environment can expose." "Do not claim visibility into hidden context or every internal file opened by a program." "Mark missing evidence clearly." "Do not claim to capture every internal file read performed by a command." "State what cannot be observed." | R607 (evidence) |
| 122 | "For each file actually consulted, record its path, the question you were trying to answer, why that file was relevant, and whether it provided useful information." "Record repeated reads separately and explain them when possible." "Distinguish a search across files from actually reading those files." "For every file consulted, record its exact path, what information was sought, why that file was relevant, and what useful information was obtained." "Distinguish searching across files, seeing filenames in results, actually reading content, and loading instructions." | R608 (obligation) |
| 122 | "Classify activity into product implementation, necessary research, verification/security, administration/handoffs, rework, waiting and audit overhead." "Allow a primary category plus a rework flag." "Identify which work was required by an owner instruction or standing rule, with its source, and which was your implementation choice." "Product implementation." "Necessary research." "Verification or security." "Administration and handoffs." "Rework." "Waiting." "Audit overhead." | R609 (obligation) |
| 122 | "Report elapsed session time separately from summed helper time." "Account for parallel work so overlapping durations are not added into an inflated total." "Use measured timing and token information where available." "Identify estimates and unknowns." "Distinguish input, output and cache usage where the records support it." "Do not invent per-file costs or treat gaps between timestamps as measured work." "Separate elapsed time from summed helper time; account for overlapping work." "Mark estimates and unknowns." | R610 (evidence) |
| 122 | "setup, notes, extraction and report writing separately." "Show directly measurable audit overhead, while acknowledging that extra context and interruptions cannot be cleanly subtracted." "Record audit overhead separately." "Explain that subtracting its direct effort does not completely remove its effects on context and workflow." | R611 (obligation) |
| 122 | "Produce one complete Markdown report at handoff" "SESSION_WORKFLOW_AUDIT_<date>_<session-id>.md" "in the normal owner-document location." "Starting objective, repository revision and relevant unfinished work." "Complete chronological action appendix." "File-access inventory, including repeat reads and their purposes." "Avoidable repetition, blockers and recommendations." "Deliver one complete Markdown report" "Specific opportunities to simplify future work." "What was actually accomplished, distinguishing drafted, tested, committed, merged and visible to a user." "Starting-context inventory and later instruction loads." "Helper work, tests, reviews, failures and resulting corrections." "Time/token breakdown, audit overhead and measurement limits." "Use the normal owner-document location." "Starting objective and repository state." "What was accomplished: drafted, tested, committed, merged and usable on screen." "Starting-context inventory and later loads." "File-access inventory, including repeated reads." "Helper activity, verification results and corrections." "Effort breakdown and measurement limitations." | R612 (return) |
| 122 | "For each recommendation, identify the supporting events, what caused the work, any instruction requiring it, what could change, and what risk that change would introduce." "Distinguish useful checks that caught defects from duplicate checks that added no new evidence." "For each proposed improvement, cite the relevant events, explain why the work happened, identify any instruction requiring it, and state what could change and what risk that introduces." "Do not automatically treat research or testing as waste." | R613 (obligation) |
| 122 | "Reconcile the action appendix against the available main-agent and helper records." "Report missing intervals, inaccessible records and unexplained actions." "If evidence is incomplete, call this a best-effort audit." "Do not present one session as proof of the project" "Reconcile the appendix against available main-agent and helper records." "do not describe an incomplete audit as exhaustive." | R614 (harness) |
| 122 | "Keep original evidence local." "exclude credentials, secrets and private reasoning." "Do not automatically commit or publish audit artifacts." "Keep raw records private and exclude secrets from the report." "Do not create a commit, push or pull request solely for this audit." | R615 (prohibition) |
| 122 | "Return the Markdown file and its location with the normal handoff." "Record a final audit cutoff so producing the report does not create an endless requirement to report on reporting." "Return a maximum of five chat bullets, the exact report path, and the Markdown file as an attachment if supported." "Establish a final reporting cutoff so the audit does not endlessly audit its own report writing." | R616 (return) |
| 122 | "I want routine session continuation to be lighter." "Stop at the nearest safe point." "Do not start another batch or make the handoff depend on completing the whole current milestone." | R617 (obligation) |
| 122 | "A handoff alone does not require a commit, push, pull request, merge, clean working tree or fresh full test run." "Preserve unfinished local work." "Normal checks still apply when the development milestone reaches them." | R618 (authorization) |
| 122 | "Safely checkpoint active writers." "Do not assume helpers or commands survive closing the session." "Record any continuing work and how the next session can check it." | R619 (obligation) |
| 122 | "Record pending CI or reviews as pending." "Do not wait solely to make the handoff look finished." | R620 (obligation) |
| 122 | "Reuse existing evidence." "Do only the small current-state checks needed for accurate continuation." "Do not build new handoff tooling or reorganize instructions during the handoff." | R621 (prohibition) |
| 122 | "Use the existing handoff location." "Exact working directory, branch and revision." "Completed work and unfinished files." "Active helpers, commands and checks, with their identifiers or log locations." "The exact next action." "Relevant blockers and existing holds." "Reference existing detailed records rather than copying them into the handoff." | R622 (obligation) |
| 122 | "For ordinary chat updates, use three to five short bullets: what changed, what I can now use, what comes next, and any decision genuinely needed." "Put detailed evidence in the relevant file; give its path and affected lines or section." | R623 (obligation) |
| 122 | "If something prevents a quick handoff, explain the specific reason briefly." | R624 (obligation) |
| 122 | "This changes routine handoff and communication expectations only." "It does not approve the proposed instruction-file moves or remove development checks." | R625 (hold) |

- **Message 121 (R591, R592):** the start prompt comes first at a handover; no check counts in the chat. Not an approval to merge on unfinished checks or to leave a check out.
- **The start prompt pasted back (R593 to R596):** the session's own text; it adds one thing, the record of message 121, which this capture is. Its lists of where the work stands, of the next actions and of the stops restate rows already recorded.
- **The audit (R597 to R616):** for this one session, from its start to its handoff; the work goes on unchanged; evidence is the records that exist anyway; short purpose notes only; one report at the handoff, named `SESSION_WORKFLOW_AUDIT_<date>_<session-id>.md`, in the owner-document folder; nothing is improved during the trial; no helper, tool, setting or instruction is added for it; nothing of it is committed or published by itself.
- **The lighter handoff (R617 to R622, R624, R625):** stop at the nearest safe point; no commit, push, pull request, merge, clean tree or full test run for the handoff's own sake; checkpoint writers; pending things recorded as pending; five things in the handoff, with references instead of copies. It does not approve the instruction-file moves and removes no development check.
- **Chat updates (R623):** three to five short bullets; the detail in the file it belongs to.
- **Readings that are the orchestrator's, not the owner's words:** each is marked in its row. The chief ones: the two texts of the audit are read together (R597); the lighter handoff changes what the procedure's files ask, and those files are not edited during the audited session (R618); the long lists a handoff carried are referred to, not copied (R622); this capture is not a commit made only for the audit (R615).
- **Lines of message 122 quoted by no row** (kept in the verbatim block; each is a heading, a lead-in to a list, or part of the pasted start prompt that restates recorded rows):
- none
- **Not claimed by this capture:** no row is verified. All thirty-five rows are pending. No instruction file, no procedure file and no check is changed by this capture.
