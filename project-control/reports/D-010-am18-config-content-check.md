# D-010 source-018 — pre-hardening config-content correctness determination (READ-ONLY)

Orchestrator-executed 2026-08-08 under owner amendment source-018 (R168–R172). Nothing was
changed: config untouched (R170), nothing moved, no ACLs applied, nothing activated, M2-T015/T016
untouched (R172). All citations are to merged main (`bbd176a` era; supervisor code byte-identical
since `0a7cc4c`).

## VERDICT (R171 branch: "already exactly correct")

**The existing config contents are already exactly correct for the supervised-auto activation.
The set of immutable fields that must change before supervised-auto can operate correctly is
EMPTY.** No STOP; no diff to present. Proof below, per question.

The complete live file (712 bytes, SHA-256 `29eb765e…da1cb`) contains exactly three sections:
`[controller] default_mode="shadow"`; `[codex] allowed_models=["gpt-5.6-sol","gpt-5.6-terra"]`;
`[claude] allowed_models=[]`. `[limits]`, `[rotation]`, and every other section are deliberately
omitted → fail-closed code defaults apply.

## Q1 — default_mode: supervised-auto is represented SOMEWHERE ELSE ENTIRELY

`controller.default_mode` has exactly two consumers in the entire package (grep-proof):
config validation (config.py:334–343 — must be one of the four MODES and must be BOOTABLE:
`shadow` or `supervised`; `limited-auto` may NEVER come from a configuration file) and the doctor
display line (cli.py:478–479). **Zero consumers in loop.py.** The RUN mode is chosen per launch
by the operator: `start --mode {shadow|supervised|limited-auto}` (cli.py argdef, CLI default
"shadow"; `--mode limited-auto` refuses by name with NotImplementedError), and the loop receives
`mode=args.mode` — never `config.default_mode`. Supervised-auto activation is represented by the
owner's explicit act (the R131 typed decision, the R595 path) plus activation gating that reads
`controller_config_acl.protected` from doctor (cli.py payload comment: "Activation gating (a
separate explicit owner act) reads `protected`"). **`default_mode = "shadow"` is therefore
correct AND the desired fail-safe:** a flagless launch stays observation-only; supervised
sessions are started with an explicit `--mode supervised`. Changing it to "supervised" is
permitted by validation but would only change what an ACCIDENTAL flagless launch does — a strict
safety downgrade with zero functional gain. Keep "shadow".

## Q2 — Yes: the product-task pipeline launches Claude through this controller

`_run_loop` builds `RunnerConfig(model=launch_model, expected_model=…)` and constructs
`ClaudeRunner` (cli.py, D-004-R739 block) for every dispatched unit; M2-T015/T016 supervised
product tasks run as supervisor-dispatched units through exactly this path.

## Q3 — Yes: `claude.allowed_models = []` is VALID (and is a working, live-proven posture)

The chain, from code: `pinned_model = selection.selection("claude").primary` → model_selection.toml
has claude model `""` → `launch_model = ""` → `ClaudeRunner`: `if config.model: argv += ["--model",
config.model]` (claude_runner.py:337–338) — empty model adds NO `--model` flag → the worker runs
on the **account/CLI default** (exactly what "no explicit selection permitted" means; the
account default is owner-controlled, currently claude-fable-5 per D-004). `expected_model = ""` →
the per-event identity check observes without a pin (claude_runner.py:608: enforcement only `if
expected_model`). Validation agrees: `validate_selection` passes (doctor
`model_selection_allowlists = True` — "every selected and fallback model is in its OWN provider's
allowlist"). And this exact combination is **live-proven**: the Phase-5 pilot ran full cycles —
worker units dispatched and completed, live Codex decision, run 6 FULL CYCLE COMPLETE — on this
very file. Note the enforced consistency: with the allowlist empty, a NON-empty claude selection
in model_selection.toml would be **refused** (empty allowlist = no explicit selection permitted),
so the current pair (`[]` + `""`) is the only valid claude configuration — and it holds.

## Q4 — Config vs model_selection.toml vs the M2-T015/T016 supervised path

- **Codex:** selection `review_model = "gpt-5.6-sol"` ∈ frozen allowlist {gpt-5.6-sol,
  gpt-5.6-terra} ✓. The review model remains changeable on the MUTABLE side (model_selection.toml
  stays outside the hardened parent AND outside the manifest) within the frozen allowlist —
  hardening does not freeze model choice, only the permitted set.
- **Claude:** selection `""` + allowlist `[]` ✓ (Q3). Worker model = account default.
- **Limits / rotation:** `[limits]` omitted → every fail-closed default applies; `[rotation]`
  omitted → threshold 400000 default — matching the owner's R113 rotation ceiling.
- **M2-T015/T016 execution:** `start --mode supervised` + task packet + worktree + explicit
  executables; every forward held for operator approval (WAIT_FOR_OWNER; the M0-T048-hardened
  sealed-approval path); no step in that path reads any config field the file lacks.

## Q5 — Immutable fields requiring change before supervised-auto: NONE

Empty list. Every axis is either per-launch (mode), mutable-side (model selection within the
frozen allowlists), defaulted fail-closed ([limits]/[rotation]), or already correct (codex
allowlist).

**One deliberate trade-off to acknowledge (not a blocker):** freezing `claude.allowed_models=[]`
under UAC means a FUTURE decision to pin an explicit worker model would require the elevated
unlock → edit → re-harden cycle (the config change itself is validated through the model-change
endpoint against the frozen allowlist). Under the current design the worker model is steered by
the owner-controlled account default, so no such pin is needed for M2-T015/T016. If the owner
prefers pre-authorizing named worker models before freezing, that would be an owner-reviewed
diff to `[claude] allowed_models` — optional policy, NOT required for correct operation.

## Prohibitions honored (R170/R172)
Config unmodified (SHA re-verified `29eb765e…da1cb`); nothing moved; no ACLs; nothing activated;
M2-T015/T016 untouched. The relocation remains ready per source-017's approved-in-principle
design pending the owner's go after this determination.
