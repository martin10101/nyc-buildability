# D-024 Amendment 50 — Continue M0-T107 from journey-m0t107-01: consolidated Codex adjudication, one bounded correction pass, then G3/G4/DCV acceptance wave (owner directive, 2026-09-03)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-049-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-03, one message after the owner-typed
  `run_first_supervised_journey.ps1` run completed)
- **Context:** journey-m0t107-01 ran to a settled close. Durable run evidence
  (`%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075…\mrl\journey-m0t107-01\`):
  `one_shot_unit.json` — ok true, returncode 0, worker outcome COMPLETED via
  structured_output, primary model `claude-fable-5` (model_mismatch false, session
  5bd21dae-714f-4250-bcbd-541183faf915, 39 assistant turns), tool census
  Edit 5 / Glob 8 / Grep 2 / Read 7 / StructuredOutput 1 (no Bash), 0/2 subagents used,
  descendant cleanup proven (windows_toolhelp32, remaining []); `codex_decision.json` —
  schema-valid `mrl_codex_decision_record/v1`, decision REVISE (gpt-5.6-sol @ 0.146.0),
  git-bound to task head `ffc77bab` / observed base `d8b3899f`. The worker left its
  revisions UNCOMMITTED in wt-m0t107 on exactly the two allowed paths
  (`M docs/D024_PORTABILITY_PLAN.md`, `M project-control/reports/M0-T107-portability-plan.md`).
  The Codex rationale requests a re-issued review packet with complete file contents, the
  task contract, applicable directive text, and real acceptance-command output — the owner
  now routes that adjudication through the normal independent acceptance wave instead of
  another supervised cycle.
- **Base identity at capture:** control plane `ctl24` branch `candidate/D-024-mrl-option-b`
  HEAD `99165bc2b51a9d432bc06b34f40d8a82e5fe57e7`, tree clean. Worker `wt-m0t107` branch
  `task/M0-T107-plugin-portability` HEAD `ffc77bab80907fac1fde4e3bd81f1fdf1aa5dd81` with the
  two uncommitted worker revisions above. M0-T107 claimed at 55%.

## Verbatim owner directive

> Continue M0-T107 from the completed journey-m0t107-01 evidence.
>
> Treat this as a successful first supervised journey: Fable returned COMPLETED, Codex produced a valid REVISE decision, process cleanup passed, and exit code was 0. The operator_declined stop is the expected end of the one-cycle supervised script, not a defect. Do not open another incident, stabilization task, or controller repair.
>
> Read codex_decision.json and both modified allowed-path files. Consolidate every Codex revision request first, adjudicate them together, and make all valid corrections in one bounded pass limited to:
>
> * docs/D024_PORTABILITY_PLAN.md
> * project-control/reports/M0-T107-portability-plan.md
>
> Then run one normal targeted verification and independent G3/G4/DCV acceptance wave. Do not rerun the live journey or canaries unless a specific requirement proves it unavoidable. Do not modify the controller, model selection, infrastructure, task scope, or cwd guard. No push, PR, merge, or deployment.
>
> Return the Codex findings in plain English, the corrections made, gate results, and final task status. End with exactly either M0_T107_ACCEPTED or M0_T107_ONE_CONSOLIDATED_BLOCKER.
