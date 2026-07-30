# M0-T028 — Live teammate PreToolUse payload evidence (H1 vs H2)

**Task:** M0-T028 (D-004 Step 3; blocker B-015 diagnosis).
**Captured by:** orchestrator (evidence-capture division of labor, `.claude/rules/project-control.md`
2026-07-15: reviewers/producers verify stored evidence they cannot capture themselves; recorded
explicitly here, not silently).
**Captured at:** frozen main `4a4bf2d572edce963a355d9d997a2e05833c1dbf` (post PR #120), 2026-07-29/30 session.
**Sanitization:** per D-004 evidence hygiene, all machine-specific values (usernames, absolute
paths, session/prompt/tool-use IDs, runtime hex IDs) are redacted to `<...>` placeholders. The raw
capture file lives OUTSIDE the repository (orchestrator-local temp) and is deliberately not
committed; this document is the committed record of what it contains.

## 1. Method (primary, not synthetic)

Temporary task-scoped instrumentation was added to `.claude/hooks/readonly_agent_guard.py` in the
live checkout: at the top of `main()`, the raw stdin payload was appended verbatim (newlines
flattened) to a capture file in the machine temp directory — outside the repository, so no repo
artifact was created. The hook command is re-executed per PreToolUse event, so the instrumentation
was live immediately, without any settings change. After the probes, the instrumentation was
reverted byte-exact (`git checkout -- .claude/hooks/readonly_agent_guard.py`; post-revert
`git status` shows zero entries under `.claude/hooks/`). Dirt sweeps were run and recorded before
and after the probes across the primary checkout and the M0-T028 worktree: no unexpected file
appeared anywhere at any point (the probes were read-only by instruction and by tool roster).

This is the ACTUAL PreToolUse payload as delivered by the harness to the hook process — a primary
runtime artifact, not a synthetic reconstruction (AS-1 satisfied on primary evidence).

## 2. Captured payloads

### 2.1 Baseline — main session (orchestrator) Bash call

```
keys = [cwd, effort, hook_event_name, permission_mode, prompt_id, session_id,
        tool_input, tool_name, tool_use_id, transcript_path]
```

- **No agent identity key of any kind** (`agent_type`, `agentType`, and `agent_id` all absent).
- The lead's pass-through therefore rests on identity ABSENCE, not on a recognized identity.

### 2.2 Probe A — NAMED spawn of a governed read-only role

Spawn: role `ci-evidence-verifier` (one of the seven `READ_ONLY_AGENTS`), spawn name
`m0t028-diag-probe`, explicit model Fable 5 (D-004-R161), read-only instructions
(`pwd`, `git rev-parse HEAD` only). Both captured payload entries:

```
keys = [agent_id, agent_type, cwd, effort, hook_event_name, permission_mode,
        prompt_id, session_id, tool_input, tool_name, tool_use_id, transcript_path]
agent_type = "m0t028-diag-probe"            <- the SPAWN NAME, not the role
agent_id   = "am0t028-diag-probe-<hex>"     <- name-derived runtime id
cwd        = <primary-checkout-root>        <- NOT a worktree (matches Step-2 finding)
effort     = {"level": "xhigh"}             <- session-global effort, present per-payload
tool_input.command = "pwd" / "git rev-parse HEAD"
```

- A whole-payload search for the role string `ci-evidence-verifier` across every field:
  **NOT PRESENT in any field.** For a named spawn the role is unrecoverable from the payload.

### 2.3 Probe B — UNNAMED spawn of the same governed role

Spawn: role `ci-evidence-verifier`, NO name, explicit model Fable 5, identical read-only
instructions. Both captured payload entries:

```
agent_type = "ci-evidence-verifier"         <- the ROLE (roster identity)
agent_id   = "<runtime-hex-id>"
```

- Probe B self-reported its exact model ID as `claude-fable-5`, proving the explicit per-spawn
  model selection mechanism works (relevant to D-004-R160/R161 and the Step-1 R090 deviation).
- Both probes' read-only commands were correctly ALLOWED (they are not mutations; no over-denial).

## 3. Verdict: H1 REFUTED, H2 CONFIRMED — with the exact mechanism

- **H1 (PreToolUse does not invoke the hook for spawned teammates): REFUTED.** The hook fired and
  received a payload for every spawned-agent Bash call observed (entries for both probes).
- **H2 (the payload lacks a recognizable `agent_type`/`agentType` identity or uses a different
  identity shape): CONFIRMED — identity substitution.** The payload's `agent_type` carries the
  runtime SPAWN NAME whenever a name is provided; the `.claude/agents/` role appears in no payload
  field. Only unnamed spawns carry the role in `agent_type`.

**Why B-015 happened:** the D-004 Step-1 pilot spawned its reviewer teammates WITH names (names +
agent types recorded from team configuration). Each teammate's PreToolUse `agent_type` was
therefore its name, which is not in `READ_ONLY_AGENTS`, so `main()` fell through
`if agent not in READ_ONLY_AGENTS: return 0` and ALLOWED the sentinel redirection. The guard's
command-classification logic never ran; nothing about the mutation-matching was wrong.

## 4. Required reconciliation (AS-2)

1. **Direct Write/Edit tool-unavailability WAS enforced** (Step 1: `No such tool available: Write`).
   That enforcement lives in the per-spawn tool roster (the agent definition's `tools:` omits the
   writers; `disallowedTools` reinforces) — applied by the harness at spawn time, independent of
   payload identity. That is why it held even while the guard was blind.
2. **The Bash redirection escaped** because the PreToolUse layer is identity-gated and the named
   teammate's payload identity (`agent_type` = name) resolved to "ungoverned".
3. **The hook logic worked on the synthetic payload** because the synthetic payload used
   `agent_type: "code-reviewer"` — the role shape the hook was written against. Live named-teammate
   payloads use the name shape. Both Step-1 observations are therefore consistent.
4. **Step 2 proved teammate Bash starts in the primary checkout before every call** — re-confirmed
   live here (probe A `cwd` = primary checkout root). Worktree-location assumptions can never
   provide confinement; an uncompensated write lands in the MAIN checkout.
5. **Conclusion — where enforcement actually lives:** (a) per-spawn tool roster (positive,
   holds); (b) PreToolUse identity resolution (was broken for named spawns; repairable in the
   hook, inside M0-T028's allowed paths); (c) never cwd. Detection (containment diff) remains the
   guaranteed backstop per D-004 Step 3's guarantee model.

## 5. Fix constraint derived from this evidence (H2 branch)

Because the role is unrecoverable from a named spawn's payload, positive role lookup alone can
never govern named spawns. The narrowest enforceable correction is fail-closed identity
resolution in the hook:

- Payload carries NO agent identity (`agent_type`/`agentType`/`agent_id` all absent) -> lead/main
  session -> pass through (unchanged).
- Resolved identity in `READ_ONLY_AGENTS` -> enforce read-only rules (unchanged).
- Resolved identity is another KNOWN `.claude/agents/` roster definition (write-authorized
  producer/specialist) -> pass through (unchanged for unnamed producer spawns).
- Identity present but NOT a known roster definition (e.g. any arbitrary spawn name) -> treat as
  read-only: **fail closed.** An unidentifiable spawned agent must never mutate; writing producers
  are spawned with their roster identity resolvable (unnamed), which only the lead controls.
- Malformed/unparseable payloads keep failing closed (existing behavior, unchanged).

This denies strictly more than before for spawned agents (no existing denial weakened), keeps all
read-only git/gh/test commands allowed for everyone, and leaves the lead and roster producers
untouched.
