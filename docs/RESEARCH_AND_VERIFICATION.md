# Research and verification procedure

Owner directive D-093 (2026-10-11; the owner's brief "Install permanent research and verification
rules", dated 2026-10-10). The short standing rule is `.claude/rules/research-and-verification.md`
(always loaded); `CLAUDE.md` principle 21 points to it and to this file. Read this file when a change
meets the trigger in section 2. It extends the policies already in force and replaces none of them:
`docs/SOURCE_AUTHORITY_POLICY.md` (which source wins), `docs/DOCUMENT_EVIDENCE_POLICY.md`
(documents), the zoning-rule review register (`docs/zoning-rule-review/GUIDE.md`, one record per
rule or calculation), ADR-007 (results ship as labelled, unreviewed drafts with a law link;
professional review is advisory) and D-050 (owner-supplied research is a discovery aid, checked
against the official sources before use).

## 1. Where things live

Discovered on 2026-10-11 (repository `/root/project/nyc-buildability`, origin
`github.com/martin10101/nyc-buildability`, Claude Code 2.1.288 on the Linux build server). The
brief's fallback paths are mapped to the files already in use:

| Purpose | Location | In git |
|---|---|---|
| Session entry point | `CLAUDE.md`, principle 21 | yes |
| Always-loaded rule | `.claude/rules/research-and-verification.md` (no frontmatter) | yes |
| Detailed procedure | this file (the brief's fallback `docs/governance/` does not exist; the other policies live in `docs/`) | yes |
| Research request queue (the index) | `docs/RESEARCH_REQUESTS.md` (RQ-nnn entries link their records) | yes |
| Question records | `docs/research/evidence-records/` (format and index in its `README.md`) | yes |
| Rule and calculation records | `docs/zoning-rule-review/` (register; `GUIDE.md`) | yes |
| Captured law text | `docs/research/zr-snapshots/v1/` (the engine's copy: `services/api/app/_zr_snapshots/v1/`) | yes |
| Property evidence packs | `docs/research/owner-research/<date>-<property>-evidence/` (large official files left out; each listed with URL and SHA-256 in `source-manifest.json`) | yes |
| Independent worked examples | `docs/reference-cases/` | yes |
| Measurement-basis records | `docs/measurement-basis/` | yes |
| Discoveries and queued fixes | `docs/DISCOVERY_BACKLOG.md` (DB-nnn) | yes |
| Design specification | `docs/design/ARCHITECT_PRESENTATION_CONTRACT.md` | yes |
| Current work state | `docs/SESSION_HANDOFF.md` (orientation; the ledger wins) | yes |
| Ledger, gates, reports | `project-control/` | yes |
| Codex-facing brief | `AGENTS.md` (a pointer only; `CLAUDE.md` is canonical; Claude Code does not load `AGENTS.md`) | yes |
| Session notes and checkpoints | `/root/project/lanes-runtime/owner-docs/<session>/SESSION_NOTES.md`; the after-compaction hook prints the latest CHECKPOINT line of the notes registered in `/root/project/lanes-runtime/hooks/session-notes/<session id>` | no (private) |
| Owner questionnaire | `/root/project/lanes-runtime/owner-docs/OWNER_QUESTIONS.md` | no (private) |

**Access requirement.** The two private items exist only on the build server under the root
account. A clone elsewhere has the rule, this procedure and the records, but not the questionnaire
or the session notes; it asks the owner or the build-server session for them. They are never
published to make a clone self-contained.

**Instruction loading (observed, not assumed).** A session started in the repository root loads
`CLAUDE.md`, every `.claude/rules/*.md` without `paths:` frontmatter (today
`CODING_RULES.md`, `PROGRAM_KNOWLEDGE.md`, `expansion-agent-dispatch-hold.md`,
`research-and-verification.md`) and the account's own auto-memory index. Path-scoped rules load
when matching files are opened. No parent-directory `CLAUDE.md` exists; no `claudeMdExcludes`
setting exists in project, local or user settings. The account memory is personal and is never the
home of a policy. The observed load list of a fresh session is recorded in
`project-control/reports/M0-T190-verification-sessions.md`.

## 2. When this procedure applies

It applies when a change affects an official property fact, a legal interpretation, a calculation
input, a result, or a certainty label (the six report labels, the screen's settled / conditional /
not known, a rule's coverage status). Routine styling, wording that does not change a meaning,
tooling and unrelated maintenance do not need a new zoning investigation.

## 3. The evidence record

For each affected question, create or update one concise record in `docs/research/evidence-records/`
(format: its `README.md`). The six parts the owner named map to the record's keys:

1. **Question and scope** (`question`): the property or scenario; tax lot, zoning lot, or zoning lot
   not yet confirmed; building or whole site; current-law scenario or historical approval.
2. **Primary evidence** (`evidence`): issuing authority, title, direct URL, document/job/section id,
   page, document or effective date, retrieval date, and the relevant excerpt or source field.
   Save permitted source material where the project already keeps it (law text in the snapshot
   folder; property sources in the property's evidence pack) and record its path and SHA-256.
3. **Meaning and applicability** (`meaning_and_applicability`): definitions, parent provisions,
   exceptions, overlays and special districts, exclusions and field instructions actually opened;
   which apply and why. Do not stop at the first matching paragraph.
4. **Measurement and accounting basis** (`measurement_basis`): units; whether each quantity is law,
   deed, survey, printed tax map, approved plan, filing attribute, administrative record, GIS or
   derived; existing or proposed; building or site; any inclusion that could double count.
5. **Conclusion and status** (`conclusion`): observed facts apart from interpretation; conflicts,
   conditional assumptions and what would settle them. An agent review is never a professional
   verification.
6. **Implementation link** (`implementation`, `review`): affected outputs and code, a worked example,
   regression cases, reviewer findings, and the revision and code identity each review covered,
   so a later change cannot inherit a review.

Reuse the project's terms: the six report labels, the screen's settled / conditional / not known,
the register's verdict words, the D-052 street-width policy terms, the measurement-basis names.
Keep records short; link the long material (handoffs, evidence packs, register pages) instead of
copying it.

**A rule or calculation change** also updates the review register in the same change (principle
20); the register's entry links the question records it relies on.

## 4. When a fact is missing

1. Search the relevant permitted official sources and follow their references: form instructions
   and data dictionaries, tax-map history, recorded-document indexes, approved plans, the legal
   definitions. Choose the routes by the question; there is no duty to query every agency.
2. Say which of these it is: **not researched**, **searched but not found**, **access blocked**,
   **conflicting evidence**, or **interpretation awaiting review** (the record's
   `research_status`). A field missing from one dataset does not show the fact is unavailable
   elsewhere. An index entry does not establish a document's contents; a filing status does not
   establish what an approved plan shows.
3. Record each search (`searches`): the source or query, the result, the exact missing document or
   field, the affected outputs and the next retrieval step.
4. Respect access controls. Use one reasonable permitted alternative (for example the official
   open-data copy of an index whose website refuses automated access), then consolidate a genuine
   blocker; never retry a denial in a loop.
5. Ask the owner only for documents, access, or a real project preference, in
   `OWNER_QUESTIONS.md` and in chat in the same step. Never ask the owner to choose which legal
   area or reading is correct in order to unblock a calculation: record the reading as an
   unreviewed draft with its law link (ADR-007) and say "not sure" where the program is not sure.
6. Keep the unknown unknown in every dependent output, and continue the work that does not depend
   on it.

## 5. Freshness

Before describing an assessment as current, check the applicable official rule or data version
under the project's existing freshness rules (the law snapshots' last-amended dates and the
connectors' data-version checks). If live checking is not possible, the record says
`"method": "snapshot"`, the snapshot date and the limitation; old evidence is never relabelled as
checked today. Recheck a record when the law, the source data, the scenario, a document revision
or the linked code changes; the check reports linked-code drift on its own (section 8).

## 6. Independent review

The existing gates do the review (`docs/GATES_AND_CHECKPOINTS.md`): G1 for sources and data, G3/G4
for code and tests. For a record or a changed reading, the reviewer must:

- open the decisive sources themselves (not the builder's summary);
- consider the relevant exception and a counterexample;
- work the expected result separately, before reading the code or the program's output;
- then compare, and record findings in the record's `review.agent_reviews` with the revision and
  code identity reviewed.

Repeating the builder's explanation is not an independent review. If no independent reviewer is
available, the review is reported as pending.

**Dispatch clause.** A delegated agent does not see this conversation. Every builder or reviewer
brief whose work meets section 2 carries, in its own words or verbatim:

> Research and verification (D-093) applies. Follow `.claude/rules/research-and-verification.md`
> and `docs/RESEARCH_AND_VERIFICATION.md`. The affected evidence records are: <record paths>. Open
> the primary sources they cite; do not rely on this brief's summary of them. Keep every unresolved
> input unresolved in every output. Report what you checked, what you could not check, and why.

## 7. Tests for changed logic

Test the boundaries that decide the reading, not a copy of the formula: an applicable versus an
inapplicable exception; conflicting measurement bases; a shared internal line versus an external
boundary; building-only versus whole-site totals; the rounding threshold. Expected values come from
the law text or an independent reference case, never from a program run. A synthetic fixture is
never relabelled as a verified real-site result.

## 8. The promotion check: what is enforced, what remains procedural

`tools/research_record_check.py --check` runs in the CI control-plane job on every push and pull
request (with its tests, `tools/test_research_record_check.py`).

**Enforced by the check.**

- Every record has the six parts, the required fields and the fixed vocabulary; saved copies match
  their SHA-256; code paths exist; a reviewer is never the producer; a professional review names a
  human.
- Status rules: a not-found or blocked status names its search, missing item and next step; a
  conflict status lists the conflicts; an interpretation awaiting review states it.
- Linked-code drift and review staleness are derived on every run and printed. Drift does not fail
  the build (ordinary work is never stopped by a record); it makes the review stale and refuses
  promotion.
- A record that asks for the **Verified** label fails the build unless every covering record is
  valid, resolved (no not-researched, not-found, blocked or conflicting status; no open conflicts or
  conditions), has a current independent review and a named professional review for its current
  revision, **and** the owner has answered question C1. Until C1 is answered nothing can be
  Verified. Every other label stays available, so draft and conditional work continues.

**Not enforced; still procedural.**

- Whether a reading of the law is right. The check validates references, fields, status and
  staleness; it certifies nothing.
- That a reviewer really opened the sources and worked the example first. The review return and
  the gate record are the evidence.
- The link from a shown result to its record. Today no result can be labelled Verified in the
  product at all (`services/api/app/drawings/report/labels.py` gives Verified a definition only,
  tested by `services/api/tests/drawings/report/test_report_pages.py`; the rule engine reaches
  `verified` only for a published rule with recorded approval, `services/api/app/rules/coverage.py`).
  The task that first lets a shown result carry Verified (after C1) must call
  `promotion_refusals(<output name>, ...)` from the check for that output and must not ship
  without it.

## 9. Session continuity

- **Start, resume, clear, compaction.** Instruction files load on every start and are re-read from
  disk after a compaction. The existing SessionStart hook `.claude/hooks/directive_reminder.py`
  (project settings, every source) adds one bounded line naming the rule with its digest, this
  procedure, the records folder and the handoff's first line. The private after-compaction hook
  (local settings) prints the latest CHECKPOINT of the session's notes. A hook supplies context; it
  is not proof that research happened and enforces no legal correctness. If hooks are disabled the
  instruction files still load; that is the route to rely on.
- **Checkpoint as decisions happen.** Write a dated CHECKPOINT or STATE line to the session notes
  at each decision, finding or blocker, not only at the end, so an abrupt stop or a full context
  window loses nothing. Do not copy transcripts into the handoff.
- **Other worktrees and remote sessions** have the policy only after they contain the commit that
  added it. Check with `git merge-base --is-ancestor <commit> HEAD` before relying on it there;
  never reset or overwrite another worktree's work to bring it in.
- **Accounts.** Nothing in this policy lives in an account's personal memory; a change of account
  needs no memory transfer. Never log the owner out or switch accounts to test it.

## 10. Presentation

Follow the presentation contract. The architect sees the answer, the decisive conditions and the
next action; the label and the law link stay with each figure. The records, searches and review
notes stay in the evidence pages and the repository, never in the main screen or the PDF summary.

## 11. Completion report

Report what changed, where it lives, which checks actually ran (command and result), which session
types were tested, and what remains unresolved, with the record ids. A promise to remember is not a
completion.
