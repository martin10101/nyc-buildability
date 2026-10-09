# D-055 source-001 (original, verbatim) — owner directive, interactive chat (orchestrator session, mid-turn), 2026-09-14

Capture head: `218dd2728c55755e93e71af5d42ab19a4f4417d3` (branch `candidate/D-024-mrl-option-b`).
Frozen origin/main baseline: `d8b3899f61efa6620e18a26541ced96020f5bef9`.
Captured by the orchestrator (build) session mid-turn, immediately after it reported the D-053
launch hand-off (M4-T020 staged; launch classifier-blocked; D-036 model revert
classifier-blocked and listed as an owner item; five gate-reviewer agent files still on the
2026-08-09 opus-4-8 fallback flip).

## owner-message-verbatim

> Please fix the fable issue so it selects fable while it last for main and reviewers

## capture-context

- "the fable issue" = the two Fable-deselection states just reported to the owner at this seam:
  (a) the loop worker ("main") pinned to claude-opus-4-8 by the D-036-R002 exhaustion-era manual
  actuation in `C:/SupervisorController/model_selection.toml`, whose recorded Thursday revert
  (D-036-R001) was still unexecuted; (b) the five gate-reviewer agent files flipped
  claude-fable-5 -> claude-opus-4-8 + effort: xhigh on 2026-08-09 (commit 89c4e304, the standing
  reviewer-model-fallback rule) and never reverted.
- "selects fable while it last" = Fable 5 is the selection while quota lasts; on exhaustion the
  standing fallback chains take over WITHOUT waiting or blocking (model_selection
  fallback_models=["claude-opus-4-8"] on reason_code quota_exhausted; the reviewer-model-fallback
  standing rule for the agent files). This message is the owner's "Fable is back" trigger that
  the reviewer-model-fallback rule (owner 2026-08-05) named as the revert condition.
- "for main and reviewers" = the loop worker pin ("main") and the five gate-reviewer agent files.
  NOT producers: D-047 (sonnet-5 producers) and the untouched opus-4-8 specialist agents are
  unchanged; the orchestrator agent file already pins claude-fable-5.
- Fable availability evidence at capture: the orchestrator session itself is running
  claude-fable-5 on this account at this seam (post the 2026-09-10 Thursday weekly reset);
  controller-side Fable launch capability was proven by the R263 probe
  (project-control/reports/M0-T113-fable-probe.md).
- Execution caveat disclosed to the owner at this seam: both surfaces were
  permission-classifier-blocked for this session earlier this turn; this directive is the
  owner's explicit authorization to retry, and any surface that remains blocked returns to the
  owner as an exact manual step (R005), never bypassed.
