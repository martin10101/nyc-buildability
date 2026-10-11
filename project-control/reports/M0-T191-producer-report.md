# M0-T191 producer report (orchestrator)

- Found after the M0-T190 merge: a delegated agent of a session started before the merge did not have the research rule (evidence and reading: `project-control/reports/M0-T191-delegated-agents.md`; three transcripts compared).
- Changed: `docs/RESEARCH_AND_VERIFICATION.md` section 6 (the dispatch clause now says why it is needed: helpers inherit the parent session's start-time instructions) and section 9 (compaction re-attaches the instruction files; picking up a mid-session change at that point was not tested; helpers get the start-time set); `.claude/rules/PROGRAM_KNOWLEDGE.md` one pointer; the evidence record.
- Not changed: the accepted M0-T190 report (the correction is recorded beside it).
- Self-checks: `python3 tools/context_budget_check.py` PASS; `python3 tools/research_record_check.py --check` PASS.
