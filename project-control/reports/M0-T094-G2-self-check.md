# M0-T094 — G2 producer self-check (orchestrator-recorded; never an independent gate)

Producer: fable-orchestrator-session. Supervisor-freeze qualifying evidence: D-024-R104.
G2 is the producer's own check (ADR-005 gate classes); the independent verdicts are G3/G4/G5 +
the directive-compliance verification.

## Self-check results

1. **Section-16.5 matrix** — `tools/test_agent_supervisor_operator_channel.py`:
   **52/52 PASS** (14 scenario classes S1–S14; stdlib unittest + one mock patch; fake
   process runners; real hook subprocess runs with env-accelerated timeout; temp-dir
   journals and scratch runtimes only; no network, no providers).
2. **Mutation testing** — **10/10 non-equivalent targeted mutants KILLED**, baseline
   re-established PASS after every restore, `__pycache__` cleared around each run:
   M1 question-size bound, M2 control-sequence strip, M3 question redaction,
   M4 durable queue on timeout, M5 resubmit same-row identity, M6b exact-command token
   boundary, M7 hook identity validation, M8 unknown-coerced-to-zero, M9 owner-command
   clear authority, M10 hook ask-no-env fail-open. (M6 `.match`→`.search` SURVIVED and is
   documented EQUIVALENT: the pattern's own `^` anchor makes the two identical; the
   boundary property is the pattern's, killed via M6b.)
3. **Modularity** — `python tools/modularity_check.py --check`: **0 failures** (a mid-unit
   `baseline_growth` FAIL on grandfathered cli.py was resolved by the
   `operator_channel_cli.py` split, not an exception record; cli.py net diff +34 lines).
4. **Lint** — ruff (local 0.9.9): **no findings in any touched file**; the 9 cli.py F401s
   predate this unit at the accepted HEAD (verified against `git show HEAD:...`) and are
   recorded, not hidden.
5. **Full supervisor-freeze suite baseline** — full `tools/` pytest run recorded below at
   completion (M0-T039 baseline duty); the CI supervisor-bridge job on the pushed SHA is
   the confirming whole-suite run.
6. **Regression over touched surfaces** — operator_channel + command_authority +
   controller_succession + phase1 + reviewer + start_reentry: **332 PASS** (before the
   matrix grew to 52; the moved `_open_runtime`/`_emit` helpers are proven
   behavior-neutral by this run).
7. **Scope** — diff strictly inside allowed_paths: 3 new supervisor modules + 1 schema +
   1 fixture + 1 additive `durable_state.ask_by_id` + thin cli.py wiring; NEW hook file +
   additive settings registration (guard packs untouched); 8 new skills; the matrix test
   file; this report set. Nothing deleted; forbidden paths untouched.
8. **Prohibitions honored** — no PR merged (PR #241 untouched); no activation; no MCP
   servers/channels; no new dependencies (stdlib only); no worker-facing token pressure
   (S13); no unproven native contract adopted (UserPromptExpansion carried unproven).
9. **Owner-gated residual** — C1 live interception canary NOT executed (R192/R197
   exact-command): zero-context proof + idle/active queueing measurement carried as
   pending-owner-C1 with the documented second-terminal fallback (R088), enforced honest
   by tests S9/S11.

## Full-suite baseline (item 5)

- Command: `python -m pytest tools/ -q -p no:cacheprovider`, full log committed:
  `project-control/reports/M0-T094-full-suite-T1.txt`.
- Honesty note: a FIRST whole-suite background run was deliberately STOPPED by the
  producer and discarded — the targeted mutation pass (item 2) briefly mutated
  production files on disk while it was in flight, and the hook tests read files at
  subprocess runtime, so that run could not serve as a clean baseline. The recorded
  run started only after every mutant site was verified restored (matrix 52/52 PASS
  on the restored tree). No result from the discarded run is cited anywhere.
- Method note: single-process whole-suite runs were repeatedly killed/timed out in this
  environment (two background kills + a 25m/29m tool-timeout pair, all recorded in the
  log), so the baseline is COMPOSED from sequential same-tree chunks per the carried
  seq-18 lesson — every chunk at the identical frozen working tree, no edits between
  chunks, summaries appended verbatim to the committed log. `test_directive_compliance.py`
  is the measured >29-minute outlier and got its own dedicated run (concurrent only with
  temp-dir-isolated suites).
- Result: composed totals in the committed log; the CI supervisor-bridge job on the
  pushed SHA is the confirming single-run whole-suite evidence.

## Live smoke (read-only / scratch-runtime, this workstation)

- `status` renders the section-14 concise block against the real checkout (read-only).
- `graceful-stop --reason` → `status` shows `graceful_stop [status-live]` → `--clear`
  round-trip on a scratch runtime base.
- Hook end-to-end: `/loop-status` and `/loop-tasks` intercept → run → block-with-output;
  similar-text prompts pass through emitting nothing; `/loop-pause` outside the repo
  root refuses; `/loop-ask` without provider env prints the exact second-terminal command.
