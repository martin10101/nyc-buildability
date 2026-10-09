# D-024 Amendment 45 — Settlement-identity + permission corrective package with Fable switch (owner directives, 2026-09-02)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-044-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-02, two messages: a mid-turn stop-order
  requiring a read-only causal trace of the preserved `canary-b5-02r1` run, then — after the
  trace was returned ending `LIVE_FAILURE_CAUSAL_TRACE_READY` — the corrective-package
  authorization below)
- **Context:** The owner-typed corrected canary (successor run `canary-b5-02r1`,
  2026-09-02 20:12–20:15Z) proved the M0-T141 Draft-7 hotfix live (child launched, real
  provider contact, schema accepted) but settlement REFUSED the checkpoint:
  `contract_violation: runtime reported no model` — `observed_model_from_result` requires
  exactly one `modelUsage` key while Claude Code 2.1.252 reports a session-wide aggregate
  (`claude-opus-4-8` + internal-helper `claude-haiku-4-5-20251001` + the decorated
  1M-context key `claude-opus-4-8[1m]`), although every assistant turn (main 15/15 +
  sidechains 34/34 and 19/19) ran exactly the pinned `claude-opus-4-8`. Separately, Bash
  EXECUTED twice under `dontAsk` despite being absent from `allowedTools` (read-only
  commands), and the external script's rows 3/8 misread durable evidence. Full causal
  trace preserved at `project-control/reports/M0-T140-canary-b502r1-causal-trace.md`
  (three clusters: A settlement-identity misread PRIMARY; B Bash enforcement drift REAL;
  C script evidence-interpretation only).
- **Base identity at capture:** worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`,
  branch `candidate/D-024-mrl-option-b` (local only), HEAD `6da0658f`, tree clean. Frozen
  M0-T141 candidate `2245de74…` INSTALLED live (update/verify/doctor evidence 20:12Z).
  Next unused task ID: M0-T142. Model pin at capture: `model_selection.toml [claude]
  model = "claude-opus-4-8"` (unchanged during analysis).

## Verbatim owner directive 1 (mid-turn stop-order — DISCHARGED by the preserved causal trace)

> Stop. Do not create another amendment, task, commit, hotfix, or provider launch yet.
>
> Analyze only the preserved `canary-b5-02r1` artifacts. The current five FAIL rows must not be treated as five independent defects.
>
> Adjudicate them correctly:
>
> * Claude authentication/provider contact is PASS if the recorded nonempty session ID came from the live provider.
> * Codex authentication is NOT_RUN unless Codex was actually invoked.
> * Subagent fan-out is NOT_RUN unless execution reached the fan-out request.
> * Item 7 is the actual no-valid-result failure.
> * Item 6 is an actual failure only if the raw event stream proves Bash was attempted and the expected denial was not recorded.
> * Item 4 requires separating the selected primary model from internal/subagent/system model activity and stripping ANSI/display decoration before comparison.
> * Confirm that the controller is still pinned to `claude-opus-4-8`; the owner wants Fable, but do not change it yet.
>
> From durable artifacts, extract and report together:
>
> 1. The exact child argv, selected model, exit code, timeout value, termination reason, stdout tail, and stderr tail.
> 2. Every provider/CLI event in timestamp order between launch and settlement.
> 3. The exact permission request: actual tool name, input, classification, controller response, and what the CLI did afterward.
> 4. Why execution ended at exactly 180.0 seconds: controller timeout, CLI timeout, max-turn limit, or natural completion.
> 5. Why `observed_models` contains Haiku, Opus, and the decorated `claude-opus-4-8[1m]`.
> 6. Whether the accepted canary is logically capable of both provoking a denied tool and continuing to a valid WorkerResult under Claude CLI 2.1.252.
> 7. Which failures are primary, cascading, not reached, or merely faulty evidence interpretation.
>
> Return no more than three proven root-cause clusters and one minimal repair boundary. Do not recommend reopening accepted tasks or creating several follow-up tasks. Do not implement anything.
>
> End with exactly `LIVE_FAILURE_CAUSAL_TRACE_READY`.

## Verbatim owner directive 2 (the corrective-package authorization)

> Proceed with exactly one bounded corrective package based on `LIVE_FAILURE_CAUSAL_TRACE_READY`. Do not reopen accepted tasks, create multiple follow-ups, perform another repo-wide audit, or make another live provider call. If project control requires a new task, create exactly one.
>
> Before implementing, incorporate these official-document corrections:
>
> 1. `modelUsage` is a session-wide aggregate covering the main loop, subagents, and internal calls. It must not be required to contain exactly one key.
> 2. `[1m]` is a real 1-million-context model variant/suffix, not ANSI decoration.
> 3. In Claude Code `dontAsk`, read-only Bash commands may execute even when Bash is absent from `allowedTools`.
> 4. A bare `disallowedTools Bash` removes Bash from Claude's context, so it cannot create a Bash-denial event. If an observable denial is required, use a scoped deny rule or a `PreToolUse` hook for one exact harmless canary command. If the production contract requires no Bash whatsoever, use the bare deny and change the evidence criterion to prove Bash was absent and never executed.
> 5. Do not base production settlement on forensic-only transcript files unless the normal controller can securely correlate and consume them. Use a correlation-bound source already available during normal settlement, or explicitly add and test that binding.
>
> Implement one change set containing only:
>
> * Settlement identity correction: accept a valid WorkerResult when the requested/pinned model is proven by a normal, correlation-bound runtime source. Treat auxiliary `modelUsage` entries separately. Recognize `<pinned-model>[1m]` as the same model family with a distinct context tier—not as a different primary model. Continue refusing when the pinned model is absent or the actual top-level model differs.
> * Permission correction: enforce the intended Bash restriction explicitly using the correct Claude Code 2.1.252 semantics. Make the canary's evidence criterion match the chosen enforcement mechanism.
> * Evidence-reader correction: Claude authentication passes from the real session ID; Codex authentication is NOT_RUN until Codex is invoked; item 8 reads the actual subagent ledger and recognizes issued=2, denied=1, processes=3.
> * Preserve the already-proven schema hotfix, one-shot transport, updater disablement, process containment, manifest binding, and all stored evidence.
>
> Add exact regression fixtures derived from `canary-b5-02r1`:
>
> * Valid WorkerResult plus multiple `modelUsage` keys settles successfully.
> * The pinned model's `[1m]` context variant is handled explicitly.
> * Missing or genuinely different primary model refuses.
> * Auxiliary/internal model usage does not masquerade as primary identity.
> * The chosen Bash restriction is load-bearing and its evidence is measured correctly.
> * Rows 3 and 8 read the correct artifacts.
> * Codex review proceeds after successful settlement.
>
> Run focused tests while editing, then one affected-suite verification at the frozen candidate. Do not repeatedly run the complete repository suite after each individual edit.
>
> Finally, prepare one owner-run PowerShell script that performs the transactional update, manifest verification, canonical switch from Opus 4.8 to the exact CLI-recognized Fable 5.1 selection, recovery preparation, and the corrected canary. Do not execute it. Do not give the owner separate commands.
>
> Return the frozen candidate identity, independent-review result, and exactly one PowerShell command. End with `SETTLEMENT_PERMISSION_REPAIR_READY`.

## Verbatim owner directive 3 (model-identifier correction, same session, mid-turn)

> OWNER CORRECTION: The required worker model is the original Fable 5 only.
>
> Use the exact model identifier `claude-fable-5`.
>
> Do not use the `fable` alias because it can resolve to Fable 5.1. Do not use `claude-fable-5-1`. Do not upgrade Claude Code for Fable 5.1. Keep the Claude fallback list empty.
>
> Replace the previous instruction mentioning "Fable 5.1" with: prepare the canonical owner-controlled switch from `claude-opus-4-8` to the exact pinned model `claude-fable-5`, and prove that the generated launch argv contains exactly `--model claude-fable-5`.
>
> No live launch yet.

## Decomposition

Requirements D-024-R684 through D-024-R699 (see `requirements.json`), amendment_sequence 45.
Forward trace: directive-1 whole text → R684 (discharged read-only analysis; trace preserved
as a committed report); directive-2 opening paragraph → R685; official corrections 1–5 →
R686–R690 in order; change-set bullets 1–4 → R691–R694 in order; the fixtures list → R695;
the test-discipline paragraph → R696; the owner-script paragraph (transactional update,
manifest verification, canonical owner-controlled model switch, recovery preparation,
corrected canary, never executed, no separate commands) → R697; the return/token paragraph
→ R698; directive-3 (model-identifier correction: exact `claude-fable-5`, never the `fable`
alias, never `claude-fable-5-1`, no Claude Code upgrade, empty fallback list, argv must
contain exactly `--model claude-fable-5`, no live launch yet) → R699, which SUPERSEDES the
"Fable 5.1" wording inside directive-2's script paragraph. Bindings: R684, R697, R699 →
M0-T140 (canary-continuation vehicle; R699 also to M0-T142 for the argv proof fixture);
R685 → both M0-T140 and M0-T142; R686–R696, R698 → M0-T142 (the single authorized
corrective task). Model-selection note: the canonical switch is the OWNER's own model
decision (directive 3), typed by the owner running the script; `claude-fable-5` is in the
immutable config allowlist, so `model_selection_allowlists` validates it. R603–R605 are
thereby exercised BY THE OWNER, not interpreted by the agent.
