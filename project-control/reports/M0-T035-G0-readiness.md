# M0-T035 — G0 readiness (administrative, orchestrator)

**Task:** D-006 Section 3/5.2 edits — ORCHESTRATION_POLICY model-tiering amendment + code-graph
awareness lines in eight agent definitions.
**Recorded at:** 2026-08-03, head `62a247e` (merge of PR #145, the D-006 capture that contracted
this task).

## Readiness checks

1. **Authority.** D-004-R681 (amendment 17 Step 5, resumed by amendment 18 R714) orders this task
   contracted and dispatched through its normal gates on D-006 issuance; D-006-R030 carries the
   same obligation from the captured directive. The `.claude/` hold lifts exactly to D-006-R027's
   scope (Section 5.2 one-line additions + Section 3 policy amendment; no new definition —
   progress-auditor is compatible).
2. **Packet completeness.** Exact allowed_paths (9 target files + report + packet), forbidden
   paths, 5 acceptance scenarios, 4 reviewers (roster covers required G3 + G5), in-regime
   D-006:ALL (9 applicable rows resolved, zero unresolved).
3. **Inputs exist at head:** `D-006 source-001.md` Sections 3/5.2/7; all eight
   `.claude/agents/*.md` targets; `.claude/ORCHESTRATION_POLICY.md`; `tools/code_graph/README.md`.
4. **No conflicts:** no open blocker references this scope; no other active task claims these
   paths; validator exit 0 at head.
5. **Dependency:** M0-T027 accepted (2026-08-03).

**G0: PASS (administrative readiness; not independent review).**
