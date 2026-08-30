# M0-T121 — producer model identity + durable Opus-4.8 authority (D-024-R323, Amendment 18)

Recorded by the orchestrator 2026-08-30, while the producer was RUNNING (not interrupted —
R324; every step below is read-only with respect to the producer). Determination at the
bottom. This record is re-verified at accept time per R323 (the transcript grows until the
producer finishes; the final re-read happens before acceptance).

## 1. Observed model identity (actual evidence, not configuration)

The producer's live session transcript (Claude Code subagent JSONL under the orchestrator
session's `subagents/` directory) was grepped read-only for per-request model ids at
~03:35 UTC, mid-run:

```
$ grep -o '"model":"[^"]*"' <producer-subagent transcript>.jsonl | sort | uniq -c
    105 "model":"claude-opus-4-8"
```

**Every one of the 105 assistant events so far carries `claude-opus-4-8`.** No second
model id appears anywhere in the transcript: no Fable 5, no Opus 5, no Sonnet — i.e. no
mid-run substitution, no fallback event, no mixed identity.

## 2. Dispatch facts (what the orchestrator actually launched)

- Agent type: `backend-engineer`; **no `model` override was passed** on the Agent dispatch
  — the checked-in agent definition governs the model.
- The dispatch was an explicitly chosen bounded producer assignment for ledger task
  M0-T121 (claimed by `supervisor-restart-producer`, isolated worktree), not a fallback
  from any unavailable model: no quota/availability event preceded or accompanied the
  dispatch, and the orchestrator session itself continued on Fable 5 throughout.

## 3. Durable authority chain

1. **Agent definition (checked in):** `.claude/agents/backend-engineer.md` frontmatter
   `model: claude-opus-4-8`, `effort: high`. Last commit touching the file:
   `8b1b386` (2026-08-04) — "Model governance: orchestrator+reviewers Fable 5, other
   subagents Opus 4.8 + effort high (D-004 am.22-23, R734-R742)". The frontmatter is
   byte-stable since that owner-resolved decision.
2. **Owner directive of record:** D-004 (agent-teams runtime adoption), amendment 22/23 —
   **D-004-R735**: "SUBAGENT MODELS: every project agent EXCEPT the five gate reviewers
   carries model: claude-opus-4-8 and effort: high in its frontmatter." `backend-engineer`
   is one of the 19 non-reviewer agents inside that assignment. **D-004-R759** adds the
   exact-model-id discipline (keep `claude-opus-4-8` exact; never resolve to opus-5).
3. **Boundary respected:** the Fable-5-pinned set (the five gate reviewers + the
   orchestrator agent) is not involved here — the producer is not a reviewer, and the
   M0-T121 gate wave will run on the reviewer roster under its own pinned identities.

## 4. What this is NOT (R325/R326 assessment)

- **Not a substitution or fallback:** the reviewer-fallback rule (Fable→Opus 4.8 when
  Fable is unavailable) and the D-004 orchestrator quota-substitution chain were not
  exercised; no unavailability event exists in this window. The model used is the one the
  owner assigned to this agent class in advance.
- **Not allowlist-inferred:** authorization is claimed ONLY from the explicit D-004-R735
  assignment + the checked-in frontmatter it mandates (§3), never from any allowlist
  membership (R326). No allowlist was consulted or cited as authority.

## 5. Determination

**AUTHORIZED — explicitly permitted bounded subagent assignment.** Observed identity
(`claude-opus-4-8`, uniform across all 105 events at observation time) matches the durable
owner-resolved assignment (D-004-R735, commit `8b1b386`) for exactly this agent class. The
R325 fail-closed condition is NOT met. Final transcript re-read to be recorded at accept
time; if ANY non-`claude-opus-4-8` id appears in the final re-read, acceptance fails
closed per R325 and goes to the owner for disposition.
