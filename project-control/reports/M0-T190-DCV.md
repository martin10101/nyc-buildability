# M0-T190 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `762ec5ebb790a4f3eeac565aaeae1f898a5db0a9` (branch `task/research-verification-rules`, review copy `/root/project/w-rv`). Directive D-093. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R003, R006, R007, R008, R010, R011, R012, R013, R014, R015, R016, R017, R018, R019, R020, R021, R022, R023, R024, R025, R026, R027, R029, R030, R031, R032, R033, R034, R035, R036, R037, R038, R039, R040, R041, R042, R043, R044, R045, R046, R047, R048, R049, R050, R051, R052, R053, R054, R055, R056, R057, R058, R059, R060, R061, R062, R064, R065, R066, R067, R068, R069, R070, R071, R073, R074.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No bound requirement is VIOLATED or UNVERIFIABLE; all 66 are SATISFIED (PASS). - Two non-blocking advisories recorded by the gates, confirmed here and NOT affecting any row: (a) the installed rule adds one top-level provenance line beyond pure path references (R026 — I judge it acceptable); (b) the builder commit 93b8e693 used a "Co-Authored-By: Claude Opus 5.5" trailer while the environment attribution is Opus 4.8 (a commit-message cosmetic for the orchestrator to reconcile on integration; not a content/behaviour defect). Neither blocks acceptance.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one message in four parts (PART 1 of 4 to PART 4 of 4) inside one code fence, as the final hand-back, received 2026-10-11T02:41Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T190 (directive D-093, 66 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, read-only
reproduction of primary evidence; it is NOT a human or professional review and certifies
no legal reading. I produced none of this work or its records; I treated every report,
map, gate record and the brief as an unverified claim and opened the source evidence
myself at the frozen head.

PART 1 of 4

(1) HEAD VERIFIED
 - I read the frozen head directly in /root/project/w-rv: `git rev-parse HEAD` =
   762ec5ebb790a4f3eeac565aaeae1f898a5db0a9 on branch task/research-verification-rules,
   and `git status --porcelain` is empty (clean working tree).
 - Working-tree blobs equal the committed blobs (e.g. source-001.md hashes to
   34ea620fec93 and requirements.json to cda2af63fbd0 both on disk and at
   762ec5ebb790:<path>), so reading files in place equals reading the commit.
 - The task's rule file blob is identical at the submit head 7a57fb61, the candidate head
   7ec7c5ec, the G4 head 6f6d3a90 and the frozen head (LF-sha256 12-hex = f5d71c755fdb on
   all four), so gate/session evidence recorded at those heads applies unchanged here.
 - Forbidden heavy harnesses (tools/test_directive_compliance.py, full api suite) were not
   run; I ran only the permitted focused commands plus one validator --check.

(2) ROWS

ROW D-093-R003 — PASS
 - Prohibition "Standing restrictions: handoff section 5." The task honoured every standing
   restriction: no services/apps/packages change, no settings/agents change, PR 241 not
   merged, no unattended merge, ports 3000/3001/8000 untouched.
 - docs/SESSION_HANDOFF.md seq 156 section 5 re-states the standing restrictions
   (Tier D stops, expansion hold, production switches off, no model: on dispatch, at most
   3 builders/4 reviewers, builders never touch the preview ports).
 - Diff c8f06029..762ec5eb touches only governance/docs/tools/hook/data paths, consistent
   with those restrictions. Nothing stays open.

ROW D-093-R006 — PASS
 - Obligation to "Update the existing project instructions, research procedure, session
   handoff and verification checks." All four updated: CLAUDE.md principle 21 + the
   always-loaded rule .claude/rules/research-and-verification.md (instructions); the
   procedure docs/RESEARCH_AND_VERIFICATION.md.
 - Session handoff updated to seq 156; the verification check is tools/research_record_check.py
   wired into .github/workflows/ci.yml (two new control-plane steps) with tests.
 - Each is an edit to a file already used, not a parallel copy. Nothing stays open.

ROW D-093-R007 — PASS
 - Prohibition "Preserve our existing approval boundaries and unresolved property numbers."
   `git diff --name-only c8f06029..762ec5eb` under services/apps/packages = 0 files;
   labels.py / engine_conditions.py / coverage.py untouched.
 - No report number changed: the five NB records keep every figure conditional
   (NB-01 zoning_lot_unconfirmed, NB-02 "Not confirmed", NB-04 recorded area with basis
   named) and none requests a Verified label (promotion.requested_label = null in all five).
 - ADR-007 approval/activation path is unchanged; the C1 gate keeps Verified unreachable.
   Nothing stays open.

ROW D-093-R008 — PASS
 - Harness "The next session must recover these requirements ... Verify this using a fresh
   session and a context-recovery check." project-control/reports/M0-T190-verification-sessions.md
   records a disposable fresh (startup) session that found the rule, handoff seq 156 and the
   NB records without the conversation.
 - A compaction + after-compaction disposable session recovered the rule's first bullet
   verbatim, the rule/procedure files, handoff seq 156 and the records folder from context
   only (section 2).
 - Transcripts exist under ~/.claude/projects/-root-project-w-rv/ and were independently
   opened by G4. Open: hook-line delivery on resume/fork is unproven in print mode and is
   honestly marked (section 6).

ROW D-093-R010 — PASS
 - Obligation "Record genuine questions in our existing owner questionnaire and continue
   everything that is already authorized." /root/project/lanes-runtime/owner-docs/OWNER_QUESTIONS.md
   carries A1,A2,C1,C2,D1,F1,B1-B3; F1's 2026-10-11 update consolidates the still-missing
   Northern Boulevard documents into one list.
 - Every question has a "Meanwhile" line so authorized work continues (e.g. F1 "nothing waits
   for this"; the next-wave DB-231/230/232 proceed per handoff section 4).
 - Questions are both in chat and in the file per the owner's rule. Nothing stays open.

ROW D-093-R011 — PASS
 - Evidence "Complete the installation and verification—not just a promise to remember."
   The installation is physically present (rule, procedure, records, check, hook line, CI,
   handoff) and the verification ran: research_record_check.py --check exits 0 over 5 records.
 - project-control/reports/M0-T190-producer-report.md gives concrete commits (51f50cec..
   6f6d3a90), a file list, and self-check command outputs, not a promise.
 - Five gate records (G1 delta, G3, G5, G4) PASS with reproduced commands. Nothing stays open.

ROW D-093-R012 — PASS
 - Obligation to implement the workflow so ordinary source checks "belong in this project."
   docs/RESEARCH_REQUESTS.md line 34 (D-093 note) states ordinary source checks are done by
   the project's own researchers as evidence records, and a law-meaning question is never sent
   to the owner.
 - The always-loaded rule + procedure + record format + CI check institutionalise this.
   Nothing stays open.

ROW D-093-R013 — PASS
 - Return "Return concrete changed files and evidence that the next session can load them."
   The producer report lists each changed file with line counts and commit SHAs; all outputs
   are tracked in git on task/research-verification-rules.
 - The next session loads them via CLAUDE.md principle 21 + the always-loaded rule (confirmed
   loaded in the fresh-session transcript, section 1 of verification-sessions). Nothing stays open.

ROW D-093-R014 — PASS
 - Prohibition "Preserve existing merge, activation and professional-review requirements...
   does not authorize changing unresolved property numbers or enabling hidden features."
   No product/settings/agents file changed; no feature flag or production switch added
   (none appear in the diff).
 - ADR-007 professional-review-advisory posture is preserved in the procedure (section 1 and
   section 8: the check "certifies nothing"); no record is called professionally verified.
 - Unresolved property numbers stay unresolved (NB records conditional). Nothing stays open.

ROW D-093-R015 — PASS
 - Obligation to identify repo root, branch/worktree, installed version, instruction files,
   handoff, research records, design requirements and questionnaire. docs/RESEARCH_AND_VERIFICATION.md
   section 1 records repo /root/project/nyc-buildability, origin martin10101/nyc-buildability,
   Claude Code 2.1.288, and a full path-mapping table.
 - It records the observed instruction-loading set and states "no claudeMdExcludes setting
   exists in project, local or user settings" (conflicts/disabled-loading inspected).
   Nothing stays open.

ROW D-093-R016 — PASS
 - Obligation "Extend the canonical files already used." Every output edits a pre-existing
   file (CLAUDE.md, .claude/rules/, .claude/hooks/directive_reminder.py, docs/, the existing
   RESEARCH_REQUESTS.md, the existing SESSION_HANDOFF.md, the existing OWNER_QUESTIONS.md).
 - The procedure (section 1) maps each brief "fallback" path to the canonical file actually
   in use. Nothing stays open.

ROW D-093-R017 — PASS
 - Obligation: a short mandatory CLAUDE.md pointer to the rule, protocol and handoff.
   CLAUDE.md line 37 principle 21 points to .claude/rules/research-and-verification.md
   (always loaded), docs/RESEARCH_AND_VERIFICATION.md, docs/research/evidence-records/ and
   docs/SESSION_HANDOFF.md.
 - It is one concise mandatory principle, consistent with keeping instructions short.
   Nothing stays open.

ROW D-093-R018 — PASS
 - Obligation: always-loaded rule at .claude/rules/research-and-verification.md with no
   path-scoped frontmatter. The file begins "# Research and verification — required project
   workflow" with no `---` frontmatter block.
 - tools/context_budget_check.py lists it in the eager (auto-loaded) set (~614 tok), and the
   fresh-session transcript's "instructions loaded" entry includes it — confirming it loads
   unconditionally. Nothing stays open.

ROW D-093-R019 — PASS
 - Obligation: a detailed procedure with evidence requirements, search procedure, review and
   completion checks. docs/RESEARCH_AND_VERIFICATION.md has sections 1-11 covering trigger
   (2), record parts (3), missing-fact search (4), freshness (5), independent review (6),
   tests (7), the enforced/procedural split (8), continuity (9), presentation (10) and the
   completion report (11).
 - The brief's fallback docs/governance/ path is explicitly remapped to docs/ (section 1,
   "the brief's fallback docs/governance/ does not exist"). Nothing stays open.

ROW D-093-R020 — PASS
 - Obligation: research index and topic/case records with sources, conclusions, conflicts,
   review status and affected implementation. docs/research/evidence-records/ holds NB-01..05
   (JSON records) and a README.md format spec; the index docs/RESEARCH_REQUESTS.md RQ-009
   (line 492) links all five records with status labels.
 - docs/DISCOVERY_BACKLOG.md DB-230/231/232 each name their evidence record (NB-03/NB-05/NB-01,
   "read it before building"). Each record carries evidence, conclusion, conflicts, review and
   implementation links. Nothing stays open.

ROW D-093-R021 — PASS
 - Obligation: current work state in the handoff (branch/commit, next work, unresolved items,
   approvals, links) and the path mapping recorded once. docs/SESSION_HANDOFF.md seq 156
   section 1 lists branches/worktrees/commits; section 4 the exact next action; section 5
   blockers/holds/decisions.
 - The "Path mapping (once; detail in the procedure, section 1)" line records the mapping once
   in the handoff with repo-relative references. Nothing stays open.

ROW D-093-R022 — PASS
 - Obligation: owner questions in the existing OWNER_QUESTIONS.md as consolidated document
   requests and genuine decisions. The file holds F1 (a consolidated list of the three
   document groups still missing) and genuine preference questions (A1/A2/C1/C2/D1/B1-B3).
 - It never asks the owner which legal interpretation is correct; F1 asks only to send
   documents or grant permission for a records request. Nothing stays open.

ROW D-093-R023 — PASS
 - Prohibition: use repo-relative links for shared instructions; keep private owner material
   private and do not publish it. docs/RESEARCH_AND_VERIFICATION.md section 1 "Access
   requirement" states the questionnaire and session notes live only on the build server and
   "are never published to make a clone self-contained."
 - CLAUDE.md principle 21, the rule and the README use repository-relative links. Nothing stays open.

ROW D-093-R024 — PASS
 - Prohibition: keep permanent instructions short; do not paste the full report, all sources
   or the entire history into startup context. The rule is 17 lines; CLAUDE.md principle 21 is
   one entry; no property report, source dump or transcript is in the eager set.
 - tools/context_budget_check.py enforces the handoff 8,000-tok budget and bans duplicate/
   retired boards; the eager list contains only the five compact instruction files. Nothing
   stays open.

ROW D-093-R025 — PASS
 - Obligation: if AGENTS.md is canonical, preserve it and avoid conflicting policy copies.
   AGENTS.md now carries a "Research and verification (D-093)" section that is "a pointer, not
   a copy" to the rule and procedure.
 - The procedure (section 1) records that Claude Code does not load AGENTS.md (it is the Codex
   brief; CLAUDE.md is canonical), so no conflicting duplicate policy is created. Nothing stays open.

ROW D-093-R026 — PASS (one provenance line added at the top — judged acceptable)
 - Obligation to install the section-2 compact rule adapting only path references. A
   programmatic bullet-by-bullet comparison shows all 12 bullets byte-identical to the brief
   except added parenthetical references; the "diffs" after stripping parentheticals are
   whitespace artifacts only.
 - The added parentheticals are path/location references (SESSION_HANDOFF.md,
   RESEARCH_AND_VERIFICATION.md, evidence-records/, RESEARCH_REQUESTS.md, OWNER_QUESTIONS.md,
   ARCHITECT_PRESENTATION_CONTRACT.md, and "the session notes the handoff names").
 - One extra line was added at the top (line 3: "Owner directive D-093 (2026-10-11). Always
   loaded: no `paths:` frontmatter. Only the path references are adapted from the owner's
   text."). I judge this an acceptable provenance/authority note (CLAUDE.md principle 2); it
   does not alter the 12 substantive bullets or weaken any obligation. Nothing stays open.

ROW D-093-R027 — PASS
 - Obligation: use the installed version's supported project-instruction mechanism and track
   shared rules in version control; personal memory or an uncommitted worktree does not
   establish availability. All policy files are committed (procedure section 1 marks each "in
   git: yes").
 - The procedure section 9 "Accounts" and verification-sessions section 6 state nothing lives
   in account memory and other worktrees get the policy only after they contain the commit.
   Nothing stays open.

PART 2 of 4

ROW D-093-R029 — PASS
 - Harness: new, resumed and compacted sessions recover the policy and task state. The rule is
   an always-loaded instruction file; the fresh (startup) transcript loads it (section 1), and
   the after-compaction session recovered it from context (section 2).
 - verification-sessions section 3 shows the SessionStart source probe log firing startup,
   resume, fork and clear; resume and fork answered correctly from the retained rule.
 - Open: hook-line DELIVERY on resume/fork is "not proven" in print mode (honestly recorded);
   the instruction file still loads regardless of the hook.

ROW D-093-R030 — PASS
 - Obligation: list active worktrees still on an older version; do not reset/overwrite their
   work. docs/SESSION_HANDOFF.md section 1 lists worktree /root/project/w-wave20 "detached at
   main c8f06029 ... It gets the D-093 files only when moved to a main that contains them."
 - No reset/overwrite of that worktree is implied; the move is left to the orchestrator.
   Nothing stays open.

ROW D-093-R031 — PASS
 - Prohibition: changing accounts must not depend on the previous account's memory; do not log
   the owner out or switch accounts to test. docs/RESEARCH_AND_VERIFICATION.md section 9
   "Accounts" states the policy lives in git, not memory.
 - verification-sessions section 6 records that another account was "not tried, by the owner's
   instruction." Nothing stays open.

ROW D-093-R032 — PASS
 - Obligation: reviewer/worker launch instructions pass the policy and evidence references; no
   new agent framework. docs/RESEARCH_AND_VERIFICATION.md section 6 "Dispatch clause" gives the
   verbatim brief line carrying the rule, procedure and affected record paths.
 - AGENTS.md now carries the pointer; verification-sessions section 4 shows subagent transcripts
   load the main checkout's CLAUDE.md and rules. No new framework was added. Nothing stays open.

ROW D-093-R033 — PASS
 - Obligation: extend the existing SessionStart hook rather than duplicate it; keep it fast and
   limited to policy identity, handoff location and relevant state. The diff to
   .claude/hooks/directive_reminder.py adds a bounded _research_line() to the existing hook.
 - The research line names the rule by sha256 digest, the procedure, the records folder and the
   sanitized handoff first line (all bounded by RESEARCH_CAP=600 / HANDOFF_CAP=140); 22 hook
   tests pass. No duplicate hook was created. Nothing stays open.

ROW D-093-R034 — PASS
 - Prohibition: preserve unrelated settings; do not claim coverage for an untested session type.
   `git diff c8f06029..762ec5eb -- .claude/settings.json .claude/agents/` is empty.
 - verification-sessions section 6 names the untested types (interactive terminal, cloud/remote,
   another machine/Windows, another account) and marks resume/fork hook delivery "not proven."
   Nothing stays open.

ROW D-093-R035 — PASS
 - Obligation: a startup hook supplies context, is not proof research happened, and if hooks are
   disabled the instruction-file route must be verified. The hook docstring and
   docs/RESEARCH_AND_VERIFICATION.md section 9 both state "a hook supplies context; it is not
   proof ... If hooks are disabled the instruction files still load; that is the route to rely on."
 - A missing rule file yields a visible WARNING (still exit 0), confirmed by the hook test.
   Nothing stays open.

ROW D-093-R036 — PASS
 - Obligation: checkpoint decisions as they occur, using the existing mechanism; do not dump
   transcripts. docs/RESEARCH_AND_VERIFICATION.md section 9 "Checkpoint as decisions happen"
   directs dated CHECKPOINT/STATE lines to the session notes "not only at the end."
 - The rule's bullet 10 points to "checkpoint during long work (the session notes the handoff
   names)." Nothing stays open.

ROW D-093-R037 — PASS
 - Obligation: trigger the procedure when a change affects an official fact, legal
   interpretation, calculation input, result or label; routine styling is exempt.
   docs/RESEARCH_AND_VERIFICATION.md section 2 states exactly this trigger and exemption.
 - The rule bullet 2 mirrors it ("Before changing feasibility facts, rule applicability,
   calculations or verification labels ..."). Nothing stays open.

ROW D-093-R038 — PASS
 - Obligation: a record with question/scope and primary evidence (authority, title, URL,
   id, page, dates, excerpt, source field), source material saved. README format table requires
   question.{text,property,lot_scope,site_scope,time_scope} and a non-empty evidence[] with
   authority/title/url/reference/page/document_date/retrieved/excerpt/saved_copy/sha256.
 - NB-05 shows four evidence entries with live ZR 12-10 / 23-52 excerpts, URLs, dates and
   MapPLUTO source fields; research_record_check.py --check validates all five and exits 0.
   Nothing stays open.

ROW D-093-R039 — PASS
 - Obligation: meaning and applicability (definitions, parent provisions, exceptions, overlays,
   exclusions), explaining which apply and why, not stopping at the first paragraph. README
   requires meaning_and_applicability.{provisions_read,exceptions_considered,reading,applies}.
 - NB-05 lists provisions_read (ZR 12-10 both definitions, 23-52 opening + (a)(1)-(3) + (b),
   11-25) and four exceptions_considered with a reasoned "reading." Nothing stays open.

ROW D-093-R040 — PASS
 - Obligation: measurement/accounting basis with units and whether each quantity is deed,
   survey, tax map, approved plan, filing attribute, administrative record or GIS, existing/
   proposed and building/site, with double-count risk. README enumerates the basis vocabulary
   and requires double_count_risk.
 - NB-04 records the recorded area (10,075 sq ft, printed_tax_map/filing_attribute) vs GIS
   (10,387.99 sq ft) with the conflict named; NB-05 records the 680 factor basis "law" and the
   dividend double-count risk. Nothing stays open.

ROW D-093-R041 — PASS
 - Obligation: conclusion and status separating observed fact from interpretation, recording
   conflicts/conditions and what settles them, distinguishing AI review from professional.
   README requires conclusion.{research_status,observed_facts,interpretation,conflicts,
   conditions,settled_by}.
 - NB-05 separates observed_facts from a one-line interpretation, lists conditions and settled_by,
   and professional_review is null; the check prints "not a professional verification" on every
   line. Nothing stays open.

ROW D-093-R042 — PASS
 - Obligation: implementation link with affected functions/fields, worked example, regression
   cases, reviewer findings and the reviewed revision so review status cannot be inherited.
   README requires implementation.{affected_outputs,code_paths,code_identity,worked_example,
   regression_cases,dependency_assessment} and review with reviewed_revision/reviewed_code_identity.
 - NB-05 records affected_outputs (dwelling_units.legal_limit, engine_condition.special_density_area),
   code_identity hashes equal to the current files, a worked example (20,150/680=29.63→29) and a
   G1 review stamped reviewed_revision 1 with the reviewed code identity. Nothing stays open.

ROW D-093-R043 — PASS
 - Prohibition: reuse existing fields/terms; do not build a second evidence platform or expand
   records into essays. docs/RESEARCH_AND_VERIFICATION.md section 3 reuses the six report labels,
   the screen's settled/conditional/not-known, the register verdicts and D-052 terms, and says
   "Keep records short; link the long material."
 - The records are single JSON files under the existing docs/research tree; no new platform was
   built. Nothing stays open.

ROW D-093-R044 — PASS
 - External fact / obligation: check the applicable rule/data version under the freshness policy;
   if live verification is unavailable, state the snapshot date and limitation, never silently
   relabel. docs/RESEARCH_AND_VERIFICATION.md section 5 requires method "snapshot" with the
   snapshot date and limitation.
 - NB-05 freshness records method "snapshot", snapshot_date 2026-10-07 and a limitation naming
   the 12-10/23-52 capture dates and the PLUTO 26v2 retrieval. Nothing stays open.

ROW D-093-R045 — PASS
 - Obligation: search relevant permitted official sources, following references; these are routes
   to consider, not a duty to query every agency. docs/RESEARCH_AND_VERIFICATION.md section 4.1
   lists form instructions, data dictionaries, tax-map history, recorded-document indexes,
   approved plans and legal definitions as routes chosen by the question.
 - NB-01/NB-02 searches name the specific ACRIS index/DOB routes attempted. Nothing stays open.

ROW D-093-R046 — PASS
 - Obligation: distinguish not-researched / searched-but-not-found / access-blocked /
   conflicting-evidence / interpretation-awaiting-review; an index entry does not establish a
   document's contents. README conclusion.research_status enumerates exactly these six values.
 - The five records actually use five distinct statuses (NB-01 access_blocked, NB-02
   searched_not_found, NB-03 interpretation_awaiting_review, NB-04 conflicting_evidence, NB-05
   answered_from_primary_source); NB-01 states an index entry does not establish the instrument.
   Nothing stays open.

ROW D-093-R047 — PASS
 - Obligation: record the source/query, result, exact missing document, affected outputs and
   next retrieval step; respect access controls; consolidate a blocker rather than retry a denial.
   README requires searches[].{source,query,result,missing_item,affected_outputs,next_step}.
 - NB-01 (access_blocked) names the blocked instrument and next step; OWNER_QUESTIONS.md F1
   consolidates the blocked documents into one request instead of retrying. Nothing stays open.

ROW D-093-R048 — PASS
 - Prohibition: ask the owner only for documents, access or a real project preference; never ask
   the owner to choose which legal area/interpretation is correct to unblock a calculation.
   OWNER_QUESTIONS.md F1 asks only to send documents or permit a records request; A1/A2/C1/C2/D1
   are presentation/label preferences.
 - docs/RESEARCH_REQUESTS.md line 34 states a law-meaning question "is never sent to the owner to
   decide: it is recorded as a labelled draft reading with its law link (ADR-007)." Nothing stays open.

ROW D-093-R049 — PASS
 - Obligation: continue work that does not depend on the missing item. OWNER_QUESTIONS.md gives
   every open question a "Meanwhile" line, and docs/SESSION_HANDOFF.md section 4 lists the next
   authorized wave (DB-231/230/232) proceeding now.
 - The rule bullet 9 states "Continue unaffected authorized work." Nothing stays open.

ROW D-093-R050 — PASS
 - Obligation: evaluate the source interpretation independently of the implementation; the
   reviewer opens the decisive sources, considers exception and counterexample, and works the
   result before reading the code; repeating the builder's explanation is not independent.
   docs/RESEARCH_AND_VERIFICATION.md section 6 states this and the "pending if unavailable" rule.
 - The G1 record (M0-T190-reviews.md, data-contract-verifier) shows the reviewer fetched ZR
   23-52/12-10 and PLUTO live and wrote its own 29-unit answer, boundary arithmetic and a
   Manhattan-CD9 counterexample "before reading NB-05 or code." Open: future reviews must carry
   their own current reviewed_revision (the format enforces this).

ROW D-093-R051 — PASS
 - Harness: test meaningful boundaries, not a copy of the formula; a synthetic fixture is never
   relabelled as a verified real-site result. docs/RESEARCH_AND_VERIFICATION.md section 7 lists
   the boundary classes and the no-formula-copy / no-synthetic-relabel rules.
 - tools/test_research_record_check.py (29 tests, all pass) exercises applicable-vs-inapplicable
   status, stale review, reviewer==producer and the Verified-while-C1-open refusal; NB-05's
   worked example states expected values from the law text, not a program run. Nothing stays open.

ROW D-093-R052 — PASS
 - Harness: add the smallest check so a result cannot be marked verified when its evidence record
   is absent, stale or unresolved; no invented verified:true treated as proof. tools/research_record_check.py
   implements promotion_refusals with a hard-coded OWNER_C1_ANSWERED=False gate and derived
   staleness; no verified boolean field exists.
 - I ran `python3 tools/research_record_check.py --check` (exit 0) and `python3 tools/test_research_record_check.py`
   (29 tests OK); the check refuses a Verified request for dwelling_units.legal_limit with named
   reasons (access_blocked, open conditions, stale/absent review, C1 open). Nothing stays open.

PART 3 of 4

ROW D-093-R053 — PASS
 - Obligation: if the workflow supports enforced checks, integrate there and document the scope;
   otherwise implement available checks and state what remains procedural.
   .github/workflows/ci.yml adds two steps in the existing control-plane job
   (research_record_check.py --check and test_research_record_check.py).
 - docs/RESEARCH_AND_VERIFICATION.md section 8 documents the enforced-vs-procedural split
   explicitly ("Enforced by the check" / "Not enforced; still procedural"). Nothing stays open.

ROW D-093-R054 — PASS
 - Prohibition: keep draft/conditional work possible; no project-wide stop for one unresolved
   property. docs/RESEARCH_AND_VERIFICATION.md section 8 states "Every other label stays
   available, so draft and conditional work continues" and code drift "does not fail the build."
 - I confirmed research_record_check.py --check exits 0 with a stale/unresolved record present
   (the drift prints a NOTE, never an error). Nothing stays open.

ROW D-093-R055 — PASS
 - Prohibition: keep the internal evidence structure out of the architect's main flow; reuse the
   clean PDF/website design. docs/research/evidence-records/README.md states "These records are
   internal working evidence. They never appear in the architect's main screen or the PDF summary."
 - docs/RESEARCH_AND_VERIFICATION.md section 10 defers to the presentation contract and keeps
   records/searches in the evidence pages only. Nothing stays open.

ROW D-093-R056 — PASS
 - Obligation: locate the Northern Boulevard handoff and evidence ZIP, treat it as input to verify
   against its sources, not a replacement; if absent, request once and continue. The task inputs
   include docs/research/owner-research/2026-10-10-215-16-northern-research-handoff.md and the
   evidence pack.
 - docs/RESEARCH_REQUESTS.md RQ-009 marks the owner research "ANSWERED 2026-10-10 (owner's
   research AI); key facts re-checked by the orchestrator," and G1 re-verified every decisive
   source live. Nothing stays open.

ROW D-093-R057 — PASS
 - Obligation: which recorded instruments establish the current zoning lot, and what is known only
   from index entries. NB-01-zoning-lot-instruments.json (status access_blocked) reads the 2022/
   2016 ACRIS index entries and DOB job text, and concludes the zoning lot is unconfirmed because
   "an index entry and a filing description do not establish what the instruments say."
 - G1 confirmed the index facts live and required F1 (moving type/date/CRFN from the Legals to the
   Master evidence), applied as NB-01 revision 2. Open: the recorded instruments themselves are
   access-blocked and listed for the owner in OWNER_QUESTIONS.md F1.

ROW D-093-R058 — PASS
 - Obligation: does the proposed zoning floor area already include retained lot 1 area.
   NB-02-proposed-zfa-scope.json (searched_not_found) records the permitted 39,934 sq ft of DOB
   job 440608941 and finds the question not established because the filled PW1/ZD1 has not been read.
 - The double-count risk (subtracting lot 1's 9,100 sq ft twice) is stated, not asserted; remaining
   capacity stays "Not confirmed." Open: the approved ZD1/PW1 schedule is access-blocked (F1).

ROW D-093-R059 — PASS
 - Obligation: short-block rear-yard applicability and how neighbouring line classifications affect
   the alternative. NB-03-rear-yard-short-block.json (interpretation_awaiting_review) reads ZR
   23-344(b) and (c)(3) and 12-10, finds the Northern Blvd blockfront (200.01 ft tax / 203.13 ft
   GIS, both < 230) a short dimension, so no rear yard within 100 ft under (b) for a ~100-ft lot.
 - The ~0.03 ft depth margin is flagged survey-dependent; the (c)(3) side-lot-line path is
   conditioned on the neighbours' tax lines being their zoning-lot lines. Open: the operative
   street line/depth await a survey or the approved ZD1.

ROW D-093-R060 — PASS
 - Obligation: which dimensions come from printed tax-map labels vs GIS and what the survey must
   settle. NB-04-lot-dimensions-basis.json (conflicting_evidence) records printed/PLUTO/DOB 100.76
   ft frontage and 10,075 sq ft against the wider GIS outline (103.88 ft / 10,387.99 sq ft, 3.11%).
 - It keeps the GIS outline for display only and the recorded area for zoning, and names the 2017
   Buckley survey as the settling evidence. Open: no deed/survey area has been read (F1).

ROW D-093-R061 — PASS
 - Obligation: can the special-density geography be resolved while the dwelling-unit inputs stay
   conditional. NB-05-special-density-area.json (answered_from_primary_source) resolves "not in a
   special density area" from ZR 12-10 (Manhattan Core = CDs 1-8; Special Downtown Brooklyn
   District) and MapPLUTO (Queens, SPDist1 null), while the unit limit stays conditional on the
   zoning lot (NB-01) and lot area (NB-04).
 - The dependency_assessment records DB-231 (derive the flag for every lot, no address-specific
   exception). Open: the dwelling-unit count stays conditional until the zoning lot and area settle.

ROW D-093-R062 — PASS
 - Prohibition: preserve the existing report numbers until official-document review supports a
   change. No services/apps/packages file changed; the five records keep every figure conditional
   and change no shown number.
 - docs/SESSION_HANDOFF.md section 5 restates "The report's numbers stay until the official
   documents support a change (D-093)." Nothing stays open.

ROW D-093-R064 — PASS
 - Prohibition: use disposable/read-only sessions; never clear or terminate the owner's active
   session. verification-sessions section 3 states every session "was disposable, in print mode
   (claude -p), limited to the tools Read, Grep and Glob ... none wrote a file. The owner's
   running session was not touched, and no account was changed."
 - Nothing stays open.

ROW D-093-R065 — PASS
 - Evidence (Persistence): actual file paths, diff/commit or PR, and confirmation shared files are
   tracked on the intended branch. All outputs are committed on task/research-verification-rules
   (frozen head 762ec5eb), and PR 487 exists.
 - I independently re-hashed the 33 restored data/ files against source-manifest.json: 33 match,
   0 mismatch (the only two non-present manifest entries are law HTML captures kept in the snapshot
   folder, not the data pack). Nothing stays open.

ROW D-093-R066 — PASS
 - Evidence (Instruction loading): installed version and observed loaded files, with exclusions/
   overrides identified. verification-sessions section 1 quotes Claude Code 2.1.288's "instructions
   loaded" entry listing CLAUDE.md and the four unconditional rules incl. research-and-verification.md.
 - It records that AGENTS.md is not loaded by Claude Code and no claudeMdExcludes/override exists.
   Nothing stays open.

ROW D-093-R067 — PASS
 - Evidence (Fresh session): a session without this conversation finds the policy, handoff and
   evidence record, with the actual prompt/result recorded. verification-sessions section 2 records
   the fresh-session prompt and result (it quoted the rule's first bullet, handoff seq 156, NB-01
   and NB-02 statuses and the Verified conditions).
 - G4 spot-read p1-fresh.json and confirmed it is byte-for-byte the quoted result. Nothing stays open.

ROW D-093-R068 — PASS
 - Evidence (Context recovery): a disposable compaction/resume test recovers the policy and task
   state; untested session types are marked honestly. verification-sessions section 2 shows the
   after-compaction session recovering the rule's first bullet, the rule/procedure files, handoff
   seq 156 and the records folder from context only.
 - Section 6 names the untested types (interactive terminal, cloud/remote, another machine/Windows,
   another account). Open: resume/fork hook-line delivery is honestly marked "not proven" in print mode.

ROW D-093-R069 — PASS
 - Evidence (Evidence check): a deliberately incomplete record is refused promotion; a complete one
   passes the structural check without being called professionally verified. verification-sessions
   section 5 shows the Verified refusal with named reasons and a Conditional request not refused.
 - The G4 R069 proof (reproduced in a scratch copy) shows an incomplete record exiting 1 with named
   reasons and a complete record passing --check (exit 0) while a Verified request is refused only by
   the C1 gate, with "not a professional verification" in the output. I re-ran the 29 unit tests (OK).
   Nothing stays open.

ROW D-093-R070 — PASS
 - Evidence (Practical review): one Northern Boulevard question traced source → interpretation →
   code → expected behaviour. NB-05 traces ZR 12-10/23-52 + MapPLUTO → "not a special density area"
   → engine_conditions.py/r6b_dwelling_units.rule.json (with code_identity) → worked example
   20,150/680 = 29 units with boundary cases.
 - The G1 review independently reproduced the trace and the DB-231 dependency assessment. Nothing
   stays open.

ROW D-093-R071 — PASS
 - Evidence (Handoff): the next action, remaining dependencies and required owner documents are in
   the canonical handoff/questionnaire. docs/SESSION_HANDOFF.md section 4 gives the exact next
   action and the DB-231/230/232 dependency order; section 5 the blockers.
 - OWNER_QUESTIONS.md F1 lists the required owner documents (the 2022/2016 ACRIS documents, the
   DOB 440608941 approved plans, the 2017 survey and 2018 deed). Nothing stays open.

ROW D-093-R073 — PASS
 - External fact: Anthropic documentation checked 2026-10-10; confirm compatibility with the
   installed version. docs/RESEARCH_AND_VERIFICATION.md section 1 and verification-sessions record
   the installed Claude Code 2.1.288 and its observed SessionStart/instruction-loading behaviour.
 - Compatibility was confirmed against the installed version, not assumed from the docs. Nothing
   stays open.

ROW D-093-R074 — PASS (cap removed, nothing moved)
 - Authorization ("No dont move just take of the tkoen restrictions"). tools/context_budget.json
   changes eager_token_budget 10000 → null with a _comment_eager citing D-093-R074 and the owner's
   exact words; the live `context_budget_check.py` prints the eager total ~10652 tok with "(no cap:
   owner D-093-R074)" and still enforces the 8,000-tok handoff budget and the duplicate/retired/
   historical checks (20 tests OK).
 - Nothing was moved: PROGRAM_KNOWLEDGE.md and docs/WORKING_KNOWLEDGE.md update the cap note in place
   ("nothing was moved, question B1 stays open"); no instruction text was relocated. Nothing stays open.

PART 4 of 4

(3) BINDING B1–B5
 - B1 PASS. The requirements.json diff from the capture commit ef647a279 to the frozen head changes
   only top-level updated_at (01:35:37 → 01:38:58) and appends "M0-T190" to exactly 66 rows'
   applicability.task_ids. A structured compare confirms: 66 rows changed, the changed set equals the
   named 66 ids exactly (no extras, none missing), each change adds only M0-T190 and removes nothing,
   and no requirement body or any other field changed.
 - B2 PASS. directive_registry.sha256_text_artifact(requirements.json) = b1cb2879...84a2bb3, equal to
   the manifest's requirements_content_digest_sha256; the id digest (newline-joined) = 796fbc27...,
   equal to requirements_id_digest_sha256; and both source digests (source-001.md f0cb7376...,
   source-002-amendment.md d5cd38ee...) equal the manifest.
 - B3 PASS. verification.json has exactly one M0-T190 task_verifications row listing the 66 applicable
   ids, producer "orchestrator", verifier "" (empty), reviewed_sha null, and every requirement entry
   state "pending" with empty evidence.
 - B4 PASS. load_registry().evaluate_task_refs(packet) returns ok=True, applicable == cited (66 == 66),
   missing_ids [], invalid_refs [], unresolved []; the packet directive_refs list the same 66 ids.
 - B5 PASS. derive_applicable(packet) over all 91 active directives yields 66 applicable ids, all from
   D-093, and applicable-but-not-cited is empty — no other active directive applies to this task
   uncited. The excluded rows (R001,R002,R004,R005,R009,R028,R063,R072) carry only D-093-BOOTSTRAP,
   not M0-T190, matching the brief.
 - Gates: G0 PASS at 934f7845 (contract head); G1, G2 (orchestrator self-check), G3, G4, G5 each
   PASS with reviewed_sha 7a57fb61 (the submit head). The diff submit→frozen touches only
   project-control/ ledger and gate records, so the required gates stand at one content identity.
   `python3 tools/validate_directive_compliance.py --check` exits 0 (direct exit code).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided the blob-level predicate
   holds: the blob ids of CLAUDE.md, AGENTS.md, everything under .claude/rules, .claude/hooks,
   .claude/session-handoff-profile.md, tools, .github, docs/RESEARCH_AND_VERIFICATION.md, docs/research,
   docs/RESEARCH_REQUESTS.md, services, apps, packages, and the task's project-control/reports for
   M0-T190 are unchanged, AND the rows' text and the binding (requirements.json digests,
   verification.json ids) are unchanged.
 - Tolerated later commits: those touching only project-control/ (acceptance records, this DCV report,
   the verification row, ledger state), docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, and a merge
   of the main line that changes none of the predicate's files. (I confirmed submit 7a57fb61 → frozen
   762ec5eb already fits this: only project-control/ changed.)

(5) REQUIRED CORRECTIONS
 - None. No bound requirement is VIOLATED or UNVERIFIABLE; all 66 are SATISFIED (PASS).
 - Two non-blocking advisories recorded by the gates, confirmed here and NOT affecting any row:
   (a) the installed rule adds one top-level provenance line beyond pure path references (R026 — I
   judge it acceptable); (b) the builder commit 93b8e693 used a "Co-Authored-By: Claude Opus 5.5"
   trailer while the environment attribution is Opus 4.8 (a commit-message cosmetic for the orchestrator
   to reconcile on integration; not a content/behaviour defect). Neither blocks acceptance.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - CI result on PR 487 / run 38104484095 (46 of 46 success): I am read-only and did not run gh or
   rerun CI; the orchestrator must confirm the live rollup at the accepted head. The two new CI steps
   are present in .github/workflows/ci.yml and both commands pass locally, so a green run is expected.
 - Live delivery of the SessionStart hook line on resume and fork: honestly marked "not proven" in the
   verification-sessions file (print mode records no hook text there); I confirmed the event fires and
   the rule stays loaded as an instruction file regardless.
 - A dedicated secret scanner (gitleaks/trufflehog) was unavailable to G5 and to me; the 33 data files'
   cleanliness rests on manual pattern greps (G5) plus my SHA-256 match to the manifest (33/33).
 - The disposable verification sessions ran at candidate head 7ec7c5ec, not the frozen head; I confirmed
   the rule blob is byte-identical across 7ec7c5ec, 7a57fb61, 6f6d3a90 and 762ec5eb (LF-sha256
   f5d71c755fdb), so the session evidence applies to the frozen head unchanged.
 - Whether the zoning readings in the five NB records are legally correct: out of scope and uncertifiable
   by any automated check (ADR-007); I verified structure, provenance, source-match and the independent
   G1 review, not legal correctness.

Summary: 66 of 66 bound requirements SATISFIED; 0 VIOLATED; 0 UNVERIFIABLE; 0 BLOCKED. Binding B1–B5
all PASS; all required gates PASS at one content identity; validator --check exits 0. VERDICT: PASS.
END-OF-REPORT
```