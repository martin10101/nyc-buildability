# D-093 source-001: the owner's directive to install permanent research and verification rules (attached brief dated 2026-10-10) and the resume prompt it came with

Captured 2026-10-11 by the orchestrator (Claude Code session 01TpXJN7hC1avVgaNN9B4fCz, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `33a4b56e-2b0e-47dd-9b18-d09cf4097f56.jsonl` | 10 | none | 2026-10-11T01:26:01.398Z | queue entry holding the typed text | `3c78f7ecbcf886f8b98332c9588e42b08471c949edd9e63f2aca0c8db0f59ef1` |
| the message | `33a4b56e-2b0e-47dd-9b18-d09cf4097f56.jsonl` | 14 | `f54b6183-6b00-4a1f-8b84-a63606a82356` | 2026-10-11T01:26:01.575Z | user line holding the message as delivered | `3c78f7ecbcf886f8b98332c9588e42b08471c949edd9e63f2aca0c8db0f59ef1` |

Context. The owner's first message of session 33a4b56e (2026-10-11 01:26 UTC), after /clear: the standard resume prompt followed by the instruction to implement the attached brief. The resume part's wave-22 seam had already been completed by the previous session (PR 486 merged into main c8f06029; 380 accepted).

## Owner message (verbatim)

Transcript timestamp 2026-10-11T01:26:01.398Z. 1954 characters; the digest is of the raw text.

> @"/root/.claude/uploads/33a4b56e-2b0e-47dd-9b18-d09cf4097f56/b0ad1ba0-CLAUDE-PERMANENT-RESEARCH-AND-SESSION-RULES.md" Resume as the NYC Buildability orchestrator. Start: tmux, then `cd /root/project/nyc-buildability && claude` (no MCP servers; `/mcp` must show none before any write).
> Read-only checks first; change nothing until they pass: `git rev-parse --show-toplevel`, `git status`, `git rev-parse HEAD`, `git -C /root/project/w-wave20 rev-parse HEAD` (expect 7adc476e or a later commit of the wave-22 accept seam), `gh pr view 486 --json state,headRefOid`, `git worktree list`, `tmux ls`, ListAgents, `python tools/project_control.py status` (377 accepted plus any of M5-T154..156 the old session accepted).
> Read CLAUDE.md, docs/SESSION_HANDOFF.md (seq 155) in full, then the last STATE lines of /root/project/lanes-runtime/owner-docs/session-2026-10-10a/SESSION_NOTES.md. Reconcile them with git, CI and the ledger; those win.
> Next action: handoff section 4 (rule-check returns -> seam_w22_accept.sh -> PR 486 body, CI, pre-merge audit, fail-closed merge -> owner PDF as images), then the next wave of section 4 item 6. Do not repeat completed work.
> Standing restrictions: handoff section 5. Updates to the owner: four short bullets, plain words.
> Report READY TO RESUME or BLOCKED.Read the attached MD and implement it as a permanent project workflow.
>
> Update the existing project instructions, research procedure, session handoff and verification checks. Preserve our existing approval boundaries and unresolved property numbers.
>
> The next session must recover these requirements without me repeating them. Verify this using a fresh session and a context-recovery check.
>
> Show me the actual files changed, which checks passed, and any remaining limitations. Record genuine questions in our existing owner questionnaire and continue everything that is already authorized.
>
> Complete the installation and verification—not just a promise to remember.

## Attached brief (verbatim)

The owner attached this file to the message (Claude Code upload `b0ad1ba0-CLAUDE-PERMANENT-RESEARCH-AND-SESSION-RULES.md`). The file's raw-text SHA-256 is `29d774661da026e12893a5b1e797ffbc28617757cf8e3433e1456dbfbeddfad5` (15712 characters).

- Upload path: `/root/.claude/uploads/33a4b56e-2b0e-47dd-9b18-d09cf4097f56/b0ad1ba0-CLAUDE-PERMANENT-RESEARCH-AND-SESSION-RULES.md` (15,716 bytes).
- Recorded in the transcript as a file attachment of the same user turn.

> # Install permanent research and verification rules
>
> **Project: NYC Buildability · Owner directive · October 10, 2026**
>
> Implement this workflow in the project. I should not have to carry the same research corrections into every new session or ask another AI to perform ordinary source checks that belong in this project.
>
> Complete the authorized documentation, configuration and verification work. Return concrete changed files and evidence that the next session can load them. Preserve existing merge, activation and professional-review requirements. This instruction does not authorize changing unresolved property numbers or enabling hidden features.
>
> ## 1. Find the existing structure before adding anything
>
> Identify the actual repository root, branch/worktree, installed Claude Code version, instruction files, session handoff, research records, design requirements and existing owner questionnaire. Inspect applicable parent and nested instructions and project settings for conflicts or disabled loading.
>
> Extend the canonical files already used. The paths below are **fallback locations**, not assertions that these files currently exist:
>
> | Purpose | Location if no equivalent exists | Content |
> |---|---|---|
> | Session entry point | Root `CLAUDE.md` | A short mandatory pointer to the research rule, relevant protocol and current handoff. |
> | Always-loaded project rule | `.claude/rules/research-and-verification.md` | The compact standing rule in section 2. No path-scoped frontmatter. |
> | Detailed procedure | `docs/governance/RESEARCH_AND_VERIFICATION.md` | Evidence requirements, search procedure, review and completion checks. Read when relevant. |
> | Research decisions | Existing research index and topic/case records | Sources, conclusions, conflicts, review status and affected implementation. |
> | Current work state | Existing session handoff | Branch/commit, next work, unresolved items, approvals and links. |
> | Owner questions | Existing `OWNER_QUESTIONS.md` | Consolidated document requests and genuine owner decisions. |
>
> Record the actual path mapping once in the canonical handoff. Use repository-relative links for shared instructions. Keep private owner material in its established private location, with a clear access requirement; do not publish it merely to make a fresh clone self-contained.
>
> Keep permanent instructions short. Do not paste the full property report, all source documents or the entire session history into startup context. If the project uses `AGENTS.md` as its canonical instructions, preserve that arrangement and verify how the installed Claude Code loads it. Avoid conflicting copies of the same policy.
>
> ## 2. Install this compact standing rule
>
> Adapt only the references to the actual paths discovered above:
>
> ```markdown
> # Research and verification — required project workflow
>
> - At session start or after context recovery, read the current handoff and identify the repository/worktree, current task and unresolved decisions.
> - Before changing feasibility facts, rule applicability, calculations or verification labels, read the research protocol and the affected evidence records.
> - Establish the applicable rule, definitions, exceptions, overlays, source-field meaning, measurement basis and zoning-lot scope before promoting a calculation to a supported result.
> - Open primary sources. Distinguish retrieved evidence, interpretation, software testing and professional verification. None automatically implies the others.
> - Investigate relevant missing facts through permitted official sources. An unknown requires a recorded search, the exact missing item and a next step.
> - Preserve conflicts and conditional assumptions. Do not invent values, double-count quantities, equate a tax lot with a zoning lot, or treat an index entry as the instrument itself.
> - Reuse valid evidence; recheck it when law, source data, scenario, document revision or affected logic changes. Do not repeat completed research without a reason.
> - Independently check the reasoning and a worked example before changing a result's verification status. Passing implementation tests is insufficient.
> - Keep unresolved inputs unresolved in every dependent output. Continue unaffected authorized work.
> - Update the canonical research record and handoff when a decision changes; checkpoint during long work. Put genuine owner questions in the existing questionnaire.
> - Follow the existing design specification. Show architects the answer, decisive conditions and action; keep detailed evidence available without filling the main screen or PDF summary with research logs.
> - Preserve existing approval and activation boundaries. Report completion with changed files, evidence, checks and remaining limits.
> ```
>
> ## 3. Make the rule survive real session changes
>
> Use the installed version's supported project-instruction mechanism. Track shared rules and any shared configuration in version control through the existing authorized workflow. A file saved only in one account's personal memory or an uncommitted worktree does not establish availability in other clones.
>
> Check the following:
>
> - The normal launch directory loads the intended project instructions and settings.
> - New, resumed and compacted sessions recover the policy and current task state.
> - Another worktree or remote session must receive the relevant commit before relying on the policy. List any active worktrees still on an older version; do not reset or overwrite their work.
> - Changing accounts does not become a dependency on the previous account's personal memory. Do not log the owner out or switch accounts just to test this.
> - Existing reviewer/worker launch instructions pass the applicable policy and evidence references. Do not assume every delegated task receives the parent conversation. Use the project's existing review arrangement; no new agent framework is needed.
>
> For static rules, use project instruction files. **If a context-restoration hook is needed**, first inspect the existing hook and checkpoint setup; extend it instead of adding a duplicate. Verify the installed `SessionStart` event behavior for startup, resume, compaction and other supported reset/fork events. Keep it fast and limited to policy identity, handoff location and relevant state. Preserve all unrelated settings and access restrictions.
>
> A startup hook supplies context; it is not proof that research happened and does not enforce legal correctness. If hooks are unavailable or disabled, record that limitation and verify the supported instruction-file route. Do not bypass configuration restrictions or claim coverage for a session type that was not tested.
>
> Checkpoint decisions as they occur, not just at a graceful session exit. Abrupt disconnection or an exhausted context window must not lose the latest finding or open blocker. Use the existing checkpoint mechanism where present; do not dump whole transcripts into the handoff.
>
> ## 4. Apply a proportionate evidence check before implementation
>
> Trigger this procedure when a change affects an official property fact, legal interpretation, calculation input, result, or certainty label. Routine styling and unrelated maintenance do not require a new zoning investigation.
>
> For each affected question, create or update one concise record with:
>
> 1. **Question and scope:** property/scenario, tax lot or zoning lot, building or whole site, current-law scenario or historical approval.
> 2. **Primary evidence:** issuing authority, title, direct URL, document/job/section ID, page, document/effective date, retrieval date and relevant excerpt or source field. Save permitted source material in the established evidence location.
> 3. **Meaning and applicability:** definitions, parent provisions, relevant exceptions, overlays/special districts, exclusions and field instructions. Explain which apply and why. Do not stop at the first matching paragraph.
> 4. **Measurement/accounting basis:** units and whether a quantity is deed, survey, printed tax map, approved plan, filing attribute, administrative record or GIS; existing/proposed and building/site scope; any inclusion that could cause double counting.
> 5. **Conclusion and status:** separate observed fact from interpretation. Record unresolved conflicts, conditional assumptions and what would settle them. Distinguish AI review from professional verification.
> 6. **Implementation link:** affected functions/output fields, worked example, regression cases and reviewer findings. Record the reviewed revision so a later change cannot inherit review status automatically.
>
> Reuse existing fields and status terms where possible. Do not build a second evidence platform or expand every record into an essay.
>
> Before describing a new assessment as current, check the applicable official rule/data version under the project's freshness policy. If live verification is unavailable, state the snapshot date and limitation; do not silently relabel old evidence as checked today.
>
> ### When a fact is missing
>
> Search the relevant permitted official sources, following references to supporting documents. Examples include form instructions and data dictionaries, tax-map history, recorded-document indexes, approved plans and applicable legal definitions. These are routes to consider according to the question, not a requirement to query every agency every time.
>
> Distinguish **not researched**, **searched but not found**, **access blocked**, **conflicting evidence**, and **interpretation awaiting review**. A missing field in one dataset is not proof that the fact is unavailable elsewhere. An index entry does not establish document contents; a filing status does not establish what an approved plan shows.
>
> Record the source/query attempted, result, exact missing document, affected outputs and next retrieval step. Respect access controls. Use a reasonable permitted alternative, then consolidate a genuine blocker rather than repeatedly retrying a denial.
>
> Ask the owner for documents, access or a real project preference. Do not ask the owner to choose which legal area or interpretation is correct merely to unblock the calculation. Continue work that does not depend on the missing item.
>
> ## 5. Review evidence independently and check result promotion
>
> Use the existing review workflow to evaluate the source interpretation independently of the implementation. The reviewer must open the decisive sources, consider the relevant exception and counterexample, and work the expected result separately before checking the code. Repeating the builder's explanation is not independent verification. If independent review is unavailable, report it as pending.
>
> For changed logic, test meaningful boundaries: an applicable versus inapplicable exception, conflicting measurement bases, a shared internal line versus an external boundary, or building-only versus whole-site totals. Avoid tests that merely copy the implementation's formula. A synthetic fixture must never be relabeled as a professionally verified real-site result.
>
> Add the smallest appropriate check to the existing validation/review process so an affected result cannot be marked verified when its required evidence record is absent, stale relative to the changed inputs/rule, or unresolved. Automated checks can validate references, required fields, dependency status and test coverage. They cannot certify that a zoning interpretation is legally correct. Do not invent a `verified: true` field and treat its presence as proof.
>
> If the existing workflow supports enforced checks, integrate this there and document the scope. Otherwise implement the available checks and state exactly what remains procedural. Keep draft or conditional work possible under the project's existing labels and activation rules. Do not create a project-wide stop for one unresolved property.
>
> Keep this internal evidence structure out of the architect's main reading flow. Reuse the established clean PDF and website design; evidence should be accessible without overwhelming the answer.
>
> ## 6. Apply the process to Northern Boulevard first
>
> Locate the supplied `215-16-Northern-research-handoff.md` and evidence ZIP. Treat that research as an input to verify against its cited sources, not an unquestionable replacement for earlier work. If these attachments are absent, request them once in the existing questionnaire and continue installing the general workflow.
>
> Review these specific issues:
>
> - Which recorded instruments establish the current zoning lot, and what remains known only from index entries?
> - Does the proposed zoning floor-area total already include retained lot 1 area?
> - Is the short-block rear-yard provision applicable, and how do the neighboring line classifications affect the alternative analysis?
> - Which dimensions come from printed tax-map labels versus GIS, and what does the identified survey need to settle?
> - Can the special-density geography be resolved while the independent inputs to the dwelling-unit count remain conditional?
>
> Preserve the existing report numbers until the required official-document review supports changing them. Once a general reasoning defect is established, identify the other rules, scenarios and outputs that use the same logic and assess those dependencies. Do not assume every similar result is wrong or hard-code an address-specific exception.
>
> ## 7. Prove that this was installed
>
> Perform these checks using disposable/read-only sessions where possible. Never clear or terminate the owner's active working session to run a demonstration.
>
> | Check | Evidence to return |
> |---|---|
> | Persistence | Actual file paths, diff/commit or prepared PR, and confirmation that shared files are tracked and available on the intended branch. |
> | Instruction loading | Installed version and observed loaded instruction files using its supported inspection method; identify exclusions or overrides. |
> | Fresh session | A session without this conversation can find the policy, handoff and evidence record; explain why missing plans remain unresolved. Record the actual prompt/result. |
> | Context recovery | A disposable compaction/resume test recovers the policy and task state. Mark untested session types honestly. |
> | Evidence check | A deliberately incomplete test record prevents promotion to verified; a properly complete record passes the structural check without being called professionally verified. |
> | Practical review | One Northern Boulevard question traced from source to interpretation, relevant code and expected behavior, or a precise documented missing-document blocker. |
> | Handoff | The next action, remaining dependencies and required owner documents are recorded in the canonical handoff/questionnaire. |
>
> Return one concise completion report: **what changed, where it lives, which checks actually ran, which session types are covered, and what remains unresolved.** Do not respond only with a promise to remember. If one check cannot run, finish the available work and identify that specific limit.
>
> ## Installation references
>
> Official Anthropic documentation checked October 10, 2026. Confirm compatibility with the version actually installed:
>
> - [Project memory and instructions](https://code.claude.com/docs/en/memory): persistent instruction files, imports, project rules, loading inspection and compaction behavior. These are model context, not a guarantee of compliance.
> - [Hooks reference](https://code.claude.com/docs/en/hooks): supported lifecycle events and their capabilities; startup context is distinct from action-blocking mechanisms.
> - [Settings scope](https://code.claude.com/docs/en/settings): shared project configuration, local overrides, working-directory and cloud-session differences.

## Reading

| Words of the message | Requirement |
|---|---|
| "@"/root/.claude/uploads/33a4b56e-2b0e-47dd-9b18-d09cf4097f56/b0ad1ba0-CLAUDE-PERMANENT-RESEARCH-AND-SESSION-RULES.md" Resume as the NYC Buildability orchestrator." "Start: tmux, then `cd /root/project/nyc-buildability && claude` (no MCP servers; `/mcp` must show none before any write)." "Read-only checks first; change nothing until they pass: `git rev-parse --show-toplevel`, `git status`, `git rev-parse HEAD`, `git -C /root/project/w-wave20 rev-parse HEAD` (expect 7adc476e or a later commit of the wave-22 accept seam), `gh pr view 486 --json state,headRefOid`, `git worktree list`, `tmux ls`, ListAgents, `python tools/project_control.py status` (377 accepted plus any of M5-T154..156 the old session accepted)." "Read CLAUDE.md, docs/SESSION_HANDOFF.md (seq 155) in full, then the last STATE lines of /root/project/lanes-runtime/owner-docs/session-2026-10-10a/SESSION_NOTES.md." "Reconcile them with git, CI and the ledger; those win." | R001 (obligation) |
| "Next action: handoff section 4 (rule-check returns -> seam_w22_accept.sh -> PR 486 body, CI, pre-merge audit, fail-closed merge -> owner PDF as images), then the next wave of section 4 item 6." "Do not repeat completed work." | R002 (sequencing) |
| "Standing restrictions: handoff section 5." | R003 (prohibition) |
| "Updates to the owner: four short bullets, plain words." | R004 (obligation) |
| "Report READY TO RESUME or BLOCKED.Read the attached MD and implement it as a permanent project workflow." | R005 (obligation) |
| "Update the existing project instructions, research procedure, session handoff and verification checks." | R006 (obligation) |
| "Preserve our existing approval boundaries and unresolved property numbers." | R007 (prohibition) |
| "The next session must recover these requirements without me repeating them." "Verify this using a fresh session and a context-recovery check." | R008 (harness) |
| "Show me the actual files changed, which checks passed, and any remaining limitations." | R009 (return) |
| "Record genuine questions in our existing owner questionnaire and continue everything that is already authorized." | R010 (obligation) |
| "Complete the installation and verification—not just a promise to remember." | R011 (evidence) |
| "Implement this workflow in the project." "I should not have to carry the same research corrections into every new session or ask another AI to perform ordinary source checks that belong in this project." "Complete the authorized documentation, configuration and verification work." | R012 (obligation) |
| "Return concrete changed files and evidence that the next session can load them." | R013 (return) |
| "Preserve existing merge, activation and professional-review requirements." "This instruction does not authorize changing unresolved property numbers or enabling hidden features." | R014 (prohibition) |
| "Identify the actual repository root, branch/worktree, installed Claude Code version, instruction files, session handoff, research records, design requirements and existing owner questionnaire." "Inspect applicable parent and nested instructions and project settings for conflicts or disabled loading." | R015 (obligation) |
| "Extend the canonical files already used." "The paths below are **fallback locations**, not assertions that these files currently exist:" | R016 (obligation) |
| "| Session entry point | Root `CLAUDE.md` | A short mandatory pointer to the research rule, relevant protocol and current handoff. |" | R017 (obligation) |
| "| Always-loaded project rule | `.claude/rules/research-and-verification.md` | The compact standing rule in section 2." "No path-scoped frontmatter. |" | R018 (obligation) |
| "| Detailed procedure | `docs/governance/RESEARCH_AND_VERIFICATION.md` | Evidence requirements, search procedure, review and completion checks." "Read when relevant. |" | R019 (obligation) |
| "| Research decisions | Existing research index and topic/case records | Sources, conclusions, conflicts, review status and affected implementation. |" | R020 (obligation) |
| "| Current work state | Existing session handoff | Branch/commit, next work, unresolved items, approvals and links. |" "Record the actual path mapping once in the canonical handoff." | R021 (obligation) |
| "| Owner questions | Existing `OWNER_QUESTIONS.md` | Consolidated document requests and genuine owner decisions. |" | R022 (obligation) |
| "Use repository-relative links for shared instructions." "Keep private owner material in its established private location, with a clear access requirement; do not publish it merely to make a fresh clone self-contained." | R023 (prohibition) |
| "Keep permanent instructions short." "Do not paste the full property report, all source documents or the entire session history into startup context." | R024 (prohibition) |
| "If the project uses `AGENTS.md` as its canonical instructions, preserve that arrangement and verify how the installed Claude Code loads it." "Avoid conflicting copies of the same policy." | R025 (obligation) |
| "Install this compact standing rule" "Adapt only the references to the actual paths discovered above:" | R026 (obligation) |
| "Use the installed version's supported project-instruction mechanism." "Track shared rules and any shared configuration in version control through the existing authorized workflow." "A file saved only in one account's personal memory or an uncommitted worktree does not establish availability in other clones." | R027 (obligation) |
| "The normal launch directory loads the intended project instructions and settings." | R028 (harness) |
| "New, resumed and compacted sessions recover the policy and current task state." | R029 (harness) |
| "Another worktree or remote session must receive the relevant commit before relying on the policy." "List any active worktrees still on an older version; do not reset or overwrite their work." | R030 (obligation) |
| "Changing accounts does not become a dependency on the previous account's personal memory." "Do not log the owner out or switch accounts just to test this." | R031 (prohibition) |
| "Existing reviewer/worker launch instructions pass the applicable policy and evidence references." "Do not assume every delegated task receives the parent conversation." "Use the project's existing review arrangement; no new agent framework is needed." | R032 (obligation) |
| "For static rules, use project instruction files. **If a context-restoration hook is needed**, first inspect the existing hook and checkpoint setup; extend it instead of adding a duplicate." "Verify the installed `SessionStart` event behavior for startup, resume, compaction and other supported reset/fork events." "Keep it fast and limited to policy identity, handoff location and relevant state." | R033 (obligation) |
| "Preserve all unrelated settings and access restrictions." "Do not bypass configuration restrictions or claim coverage for a session type that was not tested." | R034 (prohibition) |
| "A startup hook supplies context; it is not proof that research happened and does not enforce legal correctness." "If hooks are unavailable or disabled, record that limitation and verify the supported instruction-file route." | R035 (obligation) |
| "Checkpoint decisions as they occur, not just at a graceful session exit." "Abrupt disconnection or an exhausted context window must not lose the latest finding or open blocker." "Use the existing checkpoint mechanism where present; do not dump whole transcripts into the handoff." | R036 (obligation) |
| "Trigger this procedure when a change affects an official property fact, legal interpretation, calculation input, result, or certainty label." "Routine styling and unrelated maintenance do not require a new zoning investigation." | R037 (obligation) |
| "For each affected question, create or update one concise record with:" "1. **Question and scope:** property/scenario, tax lot or zoning lot, building or whole site, current-law scenario or historical approval." "2. **Primary evidence:** issuing authority, title, direct URL, document/job/section ID, page, document/effective date, retrieval date and relevant excerpt or source field." "Save permitted source material in the established evidence location." | R038 (obligation) |
| "3. **Meaning and applicability:** definitions, parent provisions, relevant exceptions, overlays/special districts, exclusions and field instructions." "Explain which apply and why." "Do not stop at the first matching paragraph." | R039 (obligation) |
| "4. **Measurement/accounting basis:** units and whether a quantity is deed, survey, printed tax map, approved plan, filing attribute, administrative record or GIS; existing/proposed and building/site scope; any inclusion that could cause double counting." | R040 (obligation) |
| "5. **Conclusion and status:** separate observed fact from interpretation." "Record unresolved conflicts, conditional assumptions and what would settle them." "Distinguish AI review from professional verification." | R041 (obligation) |
| "6. **Implementation link:** affected functions/output fields, worked example, regression cases and reviewer findings." "Record the reviewed revision so a later change cannot inherit review status automatically." | R042 (obligation) |
| "Reuse existing fields and status terms where possible." "Do not build a second evidence platform or expand every record into an essay." | R043 (prohibition) |
| "Before describing a new assessment as current, check the applicable official rule/data version under the project's freshness policy." "If live verification is unavailable, state the snapshot date and limitation; do not silently relabel old evidence as checked today." | R044 (external_fact) |
| "Search the relevant permitted official sources, following references to supporting documents." "Examples include form instructions and data dictionaries, tax-map history, recorded-document indexes, approved plans and applicable legal definitions." "These are routes to consider according to the question, not a requirement to query every agency every time." | R045 (obligation) |
| "Distinguish **not researched**, **searched but not found**, **access blocked**, **conflicting evidence**, and **interpretation awaiting review**." "A missing field in one dataset is not proof that the fact is unavailable elsewhere." "An index entry does not establish document contents; a filing status does not establish what an approved plan shows." | R046 (obligation) |
| "Record the source/query attempted, result, exact missing document, affected outputs and next retrieval step." "Respect access controls." "Use a reasonable permitted alternative, then consolidate a genuine blocker rather than repeatedly retrying a denial." | R047 (obligation) |
| "Ask the owner for documents, access or a real project preference." "Do not ask the owner to choose which legal area or interpretation is correct merely to unblock the calculation." | R048 (prohibition) |
| "Continue work that does not depend on the missing item." | R049 (obligation) |
| "Use the existing review workflow to evaluate the source interpretation independently of the implementation." "The reviewer must open the decisive sources, consider the relevant exception and counterexample, and work the expected result separately before checking the code." "Repeating the builder's explanation is not independent verification." "If independent review is unavailable, report it as pending." | R050 (obligation) |
| "For changed logic, test meaningful boundaries: an applicable versus inapplicable exception, conflicting measurement bases, a shared internal line versus an external boundary, or building-only versus whole-site totals." "Avoid tests that merely copy the implementation's formula." "A synthetic fixture must never be relabeled as a professionally verified real-site result." | R051 (harness) |
| "Add the smallest appropriate check to the existing validation/review process so an affected result cannot be marked verified when its required evidence record is absent, stale relative to the changed inputs/rule, or unresolved." "Automated checks can validate references, required fields, dependency status and test coverage." "They cannot certify that a zoning interpretation is legally correct." "Do not invent a `verified: true` field and treat its presence as proof." | R052 (harness) |
| "If the existing workflow supports enforced checks, integrate this there and document the scope." "Otherwise implement the available checks and state exactly what remains procedural." | R053 (obligation) |
| "Keep draft or conditional work possible under the project's existing labels and activation rules." "Do not create a project-wide stop for one unresolved property." | R054 (prohibition) |
| "Keep this internal evidence structure out of the architect's main reading flow." "Reuse the established clean PDF and website design; evidence should be accessible without overwhelming the answer." | R055 (prohibition) |
| "Locate the supplied `215-16-Northern-research-handoff.md` and evidence ZIP." "Treat that research as an input to verify against its cited sources, not an unquestionable replacement for earlier work." "If these attachments are absent, request them once in the existing questionnaire and continue installing the general workflow." | R056 (obligation) |
| "Which recorded instruments establish the current zoning lot, and what remains known only from index entries?" | R057 (obligation) |
| "Does the proposed zoning floor-area total already include retained lot 1 area?" | R058 (obligation) |
| "Is the short-block rear-yard provision applicable, and how do the neighboring line classifications affect the alternative analysis?" | R059 (obligation) |
| "Which dimensions come from printed tax-map labels versus GIS, and what does the identified survey need to settle?" | R060 (obligation) |
| "Can the special-density geography be resolved while the independent inputs to the dwelling-unit count remain conditional?" | R061 (obligation) |
| "Preserve the existing report numbers until the required official-document review supports changing them." | R062 (prohibition) |
| "Once a general reasoning defect is established, identify the other rules, scenarios and outputs that use the same logic and assess those dependencies." "Do not assume every similar result is wrong or hard-code an address-specific exception." | R063 (obligation) |
| "Perform these checks using disposable/read-only sessions where possible." "Never clear or terminate the owner's active working session to run a demonstration." | R064 (prohibition) |
| "| Persistence | Actual file paths, diff/commit or prepared PR, and confirmation that shared files are tracked and available on the intended branch. |" | R065 (evidence) |
| "| Instruction loading | Installed version and observed loaded instruction files using its supported inspection method; identify exclusions or overrides. |" | R066 (evidence) |
| "| Fresh session | A session without this conversation can find the policy, handoff and evidence record; explain why missing plans remain unresolved." "Record the actual prompt/result. |" | R067 (evidence) |
| "| Context recovery | A disposable compaction/resume test recovers the policy and task state." "Mark untested session types honestly. |" | R068 (evidence) |
| "| Evidence check | A deliberately incomplete test record prevents promotion to verified; a properly complete record passes the structural check without being called professionally verified. |" | R069 (evidence) |
| "| Practical review | One Northern Boulevard question traced from source to interpretation, relevant code and expected behavior, or a precise documented missing-document blocker. |" | R070 (evidence) |
| "| Handoff | The next action, remaining dependencies and required owner documents are recorded in the canonical handoff/questionnaire. |" | R071 (evidence) |
| "Return one concise completion report: **what changed, where it lives, which checks actually ran, which session types are covered, and what remains unresolved.** Do not respond only with a promise to remember." "If one check cannot run, finish the available work and identify that specific limit." | R072 (return) |
| "Official Anthropic documentation checked October 10, 2026." "Confirm compatibility with the version actually installed:" | R073 (external_fact) |

- **Not decided by this capture:** where each fallback path maps to; that is discovery work recorded in the procedure and the handoff.
- **The resume part (rows R001 to R005)** is the standard session-start prompt; it is captured because it arrived in the same message.
- **Sentences of the message quoted by no row:** none.
- **Lines of the attached brief quoted by no row:** 53 of 176; the unquoted lines are headings, table frames, the twelve bullets of the compact rule (installed word for word under row R026 and checked there) and the documentation references (row R073).
- **Not claimed by this capture:** no row is verified; all 73 are pending. This capture changes no product file, no test and no instruction file.
