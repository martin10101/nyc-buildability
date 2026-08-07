# Session handoff template (D-007 S11.3)

Produced by the OUTGOING session at a safe checkpoint, verified by a fresh
read-only reviewer using `review_model` (never `advisory_model`), stored durably
with its digest, and given to a BRAND-NEW session id. The new session must return
a structured `READY` checkpoint after re-orientation, before it changes anything.

A rotation is never an interactive `/clear`: it is always a new, explicitly
identified session.

---

## Handoff

- **Task and stage:** {task_id} / {task_stage}
- **Authoritative SHAs:** HEAD `{current_sha}`, started at `{starting_sha}`,
  origin/main `{origin_main_sha}`
- **Branch and worktree:** `{branch}` / `{worktree}`
- **Completed work:** {completed_work}
- **Changed files:** {changed_files}
- **Tests and CI:** {tests_and_ci}
- **PR state:** {pull_request}
- **Reviews and findings:** {reviews_and_findings}
- **Open blockers:** {open_blockers}
- **Owner gates outstanding:** {owner_gates}
- **Forbidden scope (do not touch):** {forbidden_scope}
- **Exact next authorized action:** {next_action}
- **Evidence digests:** {evidence_digests}

## Rules for the incoming session

1. You are a NEW session. You remember nothing. This document plus the task
   packet and the supervisor's evidence are your entire context.
2. Re-orient and return a `READY` checkpoint BEFORE making any change.
3. Do not re-do completed work, and do not assume any listed result is still
   true without the supervisor's current evidence.
4. Your authority is the task packet's, unchanged by this rotation.
