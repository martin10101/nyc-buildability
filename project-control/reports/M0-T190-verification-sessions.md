# M0-T190 verification sessions (D-093 rows R008, R027 to R030, R066 to R068, R073)

Run by the orchestrator on 2026-10-11 from 2026-10-11T02:06:22Z to 2026-10-11T02:08:28Z (UTC), with `2.1.288 (Claude Code)`, in the checkout `/root/project/w-rv` of the candidate head `7ec7c5ec2cee7de6a21b755f004e9a763642b8ab` (branch `task/research-verification-rules`). Every session was disposable, in print mode (`claude -p`), limited to the tools Read, Grep and Glob, with a spending cap; none wrote a file. The owner's running session was not touched, and no account was changed. Script: `/root/project/lanes-runtime/owner-docs/session-2026-10-11a/verify_sessions.sh`; raw outputs in that folder's `verify-candidate/` (private, build server). The after-merge check from the normal launch directory is recorded separately (section 7).

## 1. Instruction loading (observed in the transcript, not assumed)

Session `9cbe059a-e809-4489-81e7-386ecd877599` transcript `~/.claude/projects/-root-project-w-rv/9cbe059a-e809-4489-81e7-386ecd877599.jsonl`. Claude Code records the instruction files it loaded as an `instructions` entry:

```
## transcript /root/.claude/projects/-root-project-w-rv/9cbe059a-e809-4489-81e7-386ecd877599.jsonl
- line 3 2026-10-11T02:06:23.446Z: hook_success SessionStart:startup: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Research and verification (D-093): rule .claude/rules/research-and-verification.md [sha256 f5d71c755fdb], proce
- line 4 2026-10-11T02:06:23.451Z: hook_additional_context SessionStart: Research and verification (D-093): rule .claude/rules/research-and-verification.md [sha256 f5d71c755fdb], procedure docs/RESEARCH_AND_VERIFICATION.md, evidence records docs/research/evide
Active owner directives (91): D-001 (Durable Owner Directive Compliance System), D-002 (Activate the control system, consolidate the plan, and prepa), D-003 (Integrate first wave (D-002 sequential integration) and prep), D-004 (Agent-teams runtime a
- line 12 2026-10-11T02:06:23.949Z: instructions loaded:
    Project: /root/project/w-rv/CLAUDE.md (14561 chars)
    Project: /root/project/w-rv/.claude/rules/expansion-agent-dispatch-hold.md (4027 chars)
    Project: /root/project/w-rv/.claude/rules/CODING_RULES.md (4537 chars)
    Project: /root/project/w-rv/.claude/rules/research-and-verification.md (2452 chars)
    Project: /root/project/w-rv/.claude/rules/PROGRAM_KNOWLEDGE.md (17019 chars)
    AutoMem: /root/.claude/projects/-root-project-nyc-buildability/memory/MEMORY.md (8289 chars)
- line 63 2026-10-11T02:08:12.652Z: system compact_boundary: Conversation compacted
- line 64 2026-10-11T02:08:12.649Z: compaction summary present (11563 bytes)
- line 73 2026-10-11T02:08:12.869Z: hook_success SessionStart:compact: AFTER A COMPACTION: NO CHECKPOINT IS SHOWN. No notes file is registered for this session (session id 9cbe059a-e809-4489-81e7-386ecd877599; looked in /root/project/lanes-runtime/hooks/sessio
- line 74 2026-10-11T02:08:12.886Z: hook_success SessionStart:compact: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Research and verification (D-093): rule .claude/rules/research-and-verification.md [sha256 f5d71c755fdb], proc
- line 75 2026-10-11T02:08:12.889Z: hook_additional_context SessionStart: Research and verification (D-093): rule .claude/rules/research-and-verification.md [sha256 f5d71c755fdb], procedure docs/RESEARCH_AND_VERIFICATION.md, evidence records docs/research/evid
Active owner directives (91): D-001 (Durable Owner Directive Compliance System), D-002 (Activate the control system, consolidate the plan, and prepa), D-003 (Integrate first wave (D-002 sequential integration) and prep), D-004 (Agent-teams runtime a
- line 86 2026-10-11T02:08:15.214Z: instructions loaded:
    Project: /root/project/w-rv/CLAUDE.md (14561 chars)
    Project: /root/project/w-rv/.claude/rules/expansion-agent-dispatch-hold.md (4027 chars)
    Project: /root/project/w-rv/.claude/rules/CODING_RULES.md (4537 chars)
    Project: /root/project/w-rv/.claude/rules/research-and-verification.md (2452 chars)
    Project: /root/project/w-rv/.claude/rules/PROGRAM_KNOWLEDGE.md (17019 chars)
    AutoMem: /root/.claude/projects/-root-project-nyc-buildability/memory/MEMORY.md (8289 chars)
## transcript /root/.claude/projects/-root-project-w-rv/cc254542-1b9e-44b8-b317-6ddce8f79704.jsonl
- line 5 2026-10-11T02:08:12.652Z: system compact_boundary: Conversation compacted
- line 6 2026-10-11T02:08:12.649Z: compaction summary present (11533 bytes)
- line 17 2026-10-11T02:08:12.869Z: hook_success SessionStart:compact: AFTER A COMPACTION: NO CHECKPOINT IS SHOWN. No notes file is registered for this session (session id 9cbe059a-e809-4489-81e7-386ecd877599; looked in /root/project/lanes-runtime/hooks/sessio
- line 18 2026-10-11T02:08:12.886Z: hook_success SessionStart:compact: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Research and verification (D-093): rule .claude/rules/research-and-verification.md [sha256 f5d71c755fdb], proc
- line 19 2026-10-11T02:08:12.889Z: hook_additional_context SessionStart: Research and verification (D-093): rule .claude/rules/research-and-verification.md [sha256 f5d71c755fdb], procedure docs/RESEARCH_AND_VERIFICATION.md, evidence records docs/research/evid
Active owner directives (91): D-001 (Durable Owner Directive Compliance System), D-002 (Activate the control system, consolidate the plan, and prepa), D-003 (Integrate first wave (D-002 sequential integration) and prep), D-004 (Agent-teams runtime a
- line 24 2026-10-11T02:08:15.214Z: instructions loaded:
    Project: /root/project/w-rv/CLAUDE.md (14561 chars)
    Project: /root/project/w-rv/.claude/rules/expansion-agent-dispatch-hold.md (4027 chars)
    Project: /root/project/w-rv/.claude/rules/CODING_RULES.md (4537 chars)
    Project: /root/project/w-rv/.claude/rules/research-and-verification.md (2452 chars)
    Project: /root/project/w-rv/.claude/rules/PROGRAM_KNOWLEDGE.md (17019 chars)
    AutoMem: /root/.claude/projects/-root-project-nyc-buildability/memory/MEMORY.md (8289 chars)
```

Read: at start (line 12) and again after the compaction (line 86) the session loaded `CLAUDE.md`, the four unconditional rules including `.claude/rules/research-and-verification.md`, and the account's auto-memory index. `AGENTS.md` is not loaded by Claude Code (it is the Codex brief and now carries a pointer). Path-scoped rules were not loaded because no matching file was opened. No exclusion or override setting exists (procedure section 1).

## 2. The sessions: prompts and results, unchanged

### Fresh session (startup)

Session id `9cbe059a-e809-4489-81e7-386ecd877599`; result subtype `success`; is_error `False`; turns 6.

Prompt:

```
You are a fresh session in this repository; you have no earlier conversation. Answer from the repository only, using Read, Grep and Glob, in at most 14 short lines with file paths:
1. Which file holds the project's research-and-verification rule, and is it already in your instructions now (quote its first bullet word for word)?
2. Where is the current session handoff, and what exact next action does it give?
3. Which evidence record covers whether tax lots 1 and 70 of 215-16 Northern Boulevard are one zoning lot? Give its research status and the exact documents that would settle it.
4. Which record covers whether the permitted 39,934 sq ft already includes the lot 1 building, and why does the missing approved plan keep it unresolved?
5. What must be true before any result may be labelled Verified?
```

Result:

```
1. `.claude/rules/research-and-verification.md` — yes, it's auto-loaded in my instructions now. First bullet: "At session start or after context recovery, read the current handoff (`docs/SESSION_HANDOFF.md`) and identify the repository/worktree, current task and unresolved decisions."
2. `docs/SESSION_HANDOFF.md` (seq 156). Next action §4: finish M0-T190 if the ledger doesn't show it accepted and merged (reviews G1, G3, G4, G5, DCV; CI; pre-merge audit; fail-closed merge), then move the `w-wave20` worktree to the new main; after that, the next wave starts with DB-231, DB-230, DB-232.
3. `docs/research/evidence-records/NB-01-zoning-lot-instruments.json`. Research status: `access_blocked`. Settled by: the recorded 2022 CERT 2022020201551001, ZONE 2022020201551002 and DECL 2022031600431001 with their exhibits; the 2016 CERT 2016081000837001 and ZONE 2016081000837002; and a current title and zoning-lot review.
4. `docs/research/evidence-records/NB-02-proposed-zfa-scope.json` (status `searched_not_found`). The filed 39,934 sq ft could be either the whole zoning lot's zoning floor area (per the PW1 guide, including the retained lot 1 building) or building-only; only the approved ZD1 and PW1 section 12 zoning schedule of NB job 440608941 shows which, and that plan is access-blocked — so subtracting lot 1's 9,100 sq ft may double count, and remaining capacity stays "Not confirmed".
5. Per `docs/RESEARCH_AND_VERIFICATION.md:172-176`: every covering record must be valid and resolved (no not-researched / not-found / blocked / conflicting status, no open conflicts or conditions), have a current independent review and a named professional review for its current revision, **and** the owner must have answered question C1 — until C1 is answered nothing can be Verified (enforced by `tools/research_record_check.py`).
```

### Resumed session (`--resume`)

Session id `9cbe059a-e809-4489-81e7-386ecd877599`; result subtype `success`; is_error `False`; turns 1.

Prompt:

```
This session was resumed. Without reading any file again, answer in at most 6 lines: what does the research rule require before a result's verification status changes, which command enforces part of it, and what can that command not certify?
```

Result:

```
Before changing a result's verification status, the rule (`.claude/rules/research-and-verification.md`, D-093) requires independently checking the reasoning and a worked example first — passing implementation tests is insufficient. The record and handoff must also be updated as part of the same change.
The enforcing command is `python tools/research_record_check.py --check` (run in CI; it refuses promotion on invalid/unresolved records, stale reviews, or the Verified label before owner question C1 is answered).
What it cannot certify (`docs/RESEARCH_AND_VERIFICATION.md` §"Not enforced"): whether a reading of the law is actually right, that a reviewer truly opened the sources and worked the example, or the link from a shown result to its record — it validates references, fields, status and staleness; it certifies nothing substantive.
```

### Compaction (`/compact` in the resumed session)

Session id `9cbe059a-e809-4489-81e7-386ecd877599`; result subtype `success`; is_error `False`; turns 0.

Prompt:

```
/compact
```

Result:

```
(no text: the command only compacted the conversation)
```

### After the compaction (no file reads allowed)

Session id `9cbe059a-e809-4489-81e7-386ecd877599`; result subtype `success`; is_error `False`; turns 1.

Prompt:

```
The conversation was just compacted. Do not read or search any file for this answer. From your instructions and session context only, in at most 6 lines: quote the first bullet of the research-and-verification rule word for word; name the rule file and the procedure file; give the handoff file and the sequence number of the handoff named in your session context; say which evidence-records folder holds the Northern Boulevard records. If something is not in your context, say "not in context".
```

Result:

```
First bullet, word for word: "At session start or after context recovery, read the current handoff (`docs/SESSION_HANDOFF.md`) and identify the repository/worktree, current task and unresolved decisions."
Rule file: `.claude/rules/research-and-verification.md` (always loaded in my instructions).
Procedure file: `docs/RESEARCH_AND_VERIFICATION.md`.
Handoff: `docs/SESSION_HANDOFF.md`, sequence 156 (2026-10-11, written during M0-T190).
Northern Boulevard records (NB-01 to NB-05): `docs/research/evidence-records/`.
```

### Forked session (`--resume --fork-session`)

Session id `cc254542-1b9e-44b8-b317-6ddce8f79704`; result subtype `success`; is_error `False`; turns 1.

Prompt:

```
This is a forked copy of an earlier session. Without reading files, in at most 3 lines: name the research rule file and the handoff file you were given at the start of this fork.
```

Result:

```
Research rule file: `.claude/rules/research-and-verification.md` (always loaded, D-093).
Handoff file: `docs/SESSION_HANDOFF.md` (seq 156, 2026-10-11, written during M0-T190).
```

## 3. Which SessionStart events fire (hook probe)

A temporary settings file given only to these probe sessions (`--settings`, not saved anywhere) added one SessionStart hook that wrote the event's `source` to a log. The project's own hooks ran as usual. Log:

```
{"at": "2026-10-11T02:09:10", "event": "SessionStart", "source": "startup", "session_id": "657284f1-27e0-4c02-9fde-aefbf0a8025d"}
{"at": "2026-10-11T02:09:18", "event": "SessionStart", "source": "resume", "session_id": "657284f1-27e0-4c02-9fde-aefbf0a8025d"}
{"at": "2026-10-11T02:09:26", "event": "SessionStart", "source": "fork", "session_id": "2b336d52-ce1f-4185-9474-8702fa0388e7"}
{"at": "2026-10-11T02:09:46", "event": "SessionStart", "source": "resume", "session_id": "657284f1-27e0-4c02-9fde-aefbf0a8025d"}
{"at": "2026-10-11T02:09:46", "event": "SessionStart", "source": "clear", "session_id": "c96a1d1d-91df-4f95-8191-6a06eaeb0935"}
```

The project hook's research line was recorded in the transcripts for `startup`, `compact` and `clear` (session `c96a1d1d-91df-4f95-8191-6a06eaeb0935`, lines 3 and 4). For `resume` and `fork` the event fires (log above), but print mode records no hook text in the transcript, so delivery of the hook line on those two is not proven; the rule itself stayed in the resumed and forked context and both answered correctly.

## 4. Delegated agents

The transcripts of this session's own subagents (builder and reviewers, 2026-10-11) each hold an `instructions` entry listing the main checkout's `CLAUDE.md`, its unconditional rules and the account memory index. So once the main checkout holds the D-093 files, every delegated agent loads the rule. A delegated agent does not see the parent conversation; the affected record paths travel in its brief (the procedure's dispatch clause, section 6; the M0-T190 review briefs carried it).

## 5. The evidence check on the real records

`--promotion dwelling_units.legal_limit` (asks for Verified):

```
REFUSED to label 'dwelling_units.legal_limit' as Verified (structural check only; not a professional verification):
  record NB-01: research status 'access_blocked' cannot support a Verified label for 'dwelling_units.legal_limit'.
  record NB-01: open conditions prevent a Verified label for 'dwelling_units.legal_limit'.
  record NB-01: the agent review is 'stale', not a current independent review, for 'dwelling_units.legal_limit'.
  record NB-01: no named professional review for the current revision for 'dwelling_units.legal_limit'.
  record NB-05: open conditions prevent a Verified label for 'dwelling_units.legal_limit'.
  record NB-05: no named professional review for the current revision for 'dwelling_units.legal_limit'.
  owner question C1 (what must be true before a result is labelled Verified) is open; nothing is labelled Verified
```

an output no record covers:

```
REFUSED to label 'report.nonexistent_output' as Verified (structural check only; not a professional verification):
  no evidence record covers the output 'report.nonexistent_output'.
  owner question C1 (what must be true before a result is labelled Verified) is open; nothing is labelled Verified
```

the same output asking for Conditional:

```
No evidence-state refusal for labelling 'dwelling_units.legal_limit' as Conditional (structural check only; not a professional verification).
```

The first output above was taken at head `882ffd43`: NB-01's review shows `stale` because its agent review covered revision 1 while the record was already at revision 2 after the G1 correction; the check derived this on its own (the G1 delta review confirmed it). After the same reviewer confirmed revision 2 and that review was recorded, the same command gives:

```
REFUSED to label 'dwelling_units.legal_limit' as Verified (structural check only; not a professional verification):
  record NB-01: research status 'access_blocked' cannot support a Verified label for 'dwelling_units.legal_limit'.
  record NB-01: open conditions prevent a Verified label for 'dwelling_units.legal_limit'.
  record NB-01: no named professional review for the current revision for 'dwelling_units.legal_limit'.
  record NB-05: open conditions prevent a Verified label for 'dwelling_units.legal_limit'.
  record NB-05: no named professional review for the current revision for 'dwelling_units.legal_limit'.
  owner question C1 (what must be true before a result is labelled Verified) is open; nothing is labelled Verified
```

The staleness refusal is gone; every other refusal stays, and the owner's question C1 still refuses Verified on its own. Deliberately incomplete and complete test records are exercised by `tools/test_research_record_check.py` (29 tests) and by the G4 review.

## 6. Coverage, and what was not tested

- **Tested (print mode, candidate checkout):** fresh start; resume; compaction; `/clear`; fork. Instruction files loaded at start and re-loaded after compaction; the hook line injected at start, after compaction and after `/clear`.
- **Not tested:** an interactive (terminal) session; a cloud or remote session; another machine or a Windows PC; another account (not tried, by the owner's instruction). A cloud or remote session or another worktree has the policy only after it contains the merge commit.
- **Accounts:** nothing in the policy depends on the account's personal memory; the memory index loads, but the rule, the procedure, the records and the hook are in git.

## 7. After the merge (normal launch directory)

Recorded in the session handoff and the session notes after the merge, not here (this file is frozen with the task).
