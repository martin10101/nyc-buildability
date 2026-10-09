# M0-T120 producer report — D-024 Amendment 14: shell-routing compatibility

Producer: backend-engineer. Worktree `wt-m0t120`, branch
`task/M0-T120-shell-routing-compat` (base `47f9037`). Qualifying evidence
(supervisor-freeze §2): **D-024-R291** — the first live limited-auto run's
shell-first ASK stops (`M0-T113-activation-evidence.md` item 4) that no ledger
task addressed; also AD-093 "inability to complete an authorized product task
without owner touches". Requested status: **awaiting_gate**.

Detailed live transcripts, denial records, red/green verbatim, version stamps, and
the classifier coverage map are in `M0-T120-routing-evidence.md`.

## Files created / changed (all inside allowed_paths)

Production:
- `tools/agent_supervisor/routing_probe.py` (NEW) — R292 bounded non-forwarding
  live routing probe (`build_argv` + `claude_child_env` + `deny_everything`),
  classify/gather/build helpers, CLI entry. ~470 lines.
- `tools/agent_supervisor/recovery_probes.py` — R295 `probe_shell_routing_evidence`
  (matches by DIGEST `installed_identity` or version; reads dir fixtures + journal),
  `record_routing_evidence` + `SHELL_ROUTING_EVIDENCE_KEY` (durable seeding) +
  `default_claude_version_runner`; registered in `run_live_probes`/`FOLDED_PROBES`;
  `ProbeInputs` gains `installed_cli_identity`, `installed_cli_version`,
  `routing_evidence_dir`, `routing_version_runner`.
- `tools/agent_supervisor/start_gate.py` (L1) — `_claude_identity_digest` (no-spawn
  digest source); `live_revalidation` threads `installed_cli_identity` + journal and
  APPLIES the gating fold (scoped to `limited-auto`, the certified run).
- `tools/agent_supervisor/golden_run.py` (L1, admitted) — `seed_routing_evidence` /
  `clear_routing_evidence` durable-journal helpers for the golden fake identity.
- `tools/agent_supervisor/claude_runner.py` — R294 native-tool preference block
  (`NATIVE_TOOLS_GUIDANCE`, `with_native_tools_guidance`) FOLDED into
  `build_checkpoint_contract` so it rides the same single append seam; `run_unit`
  records `native_tools_guidance_appended`; `import pathlib` added.
- `tools/agent_supervisor/prompts/claude_native_tools.md` (NEW) — R294 source-of-truth guidance.
- `tools/agent_supervisor/fixtures/shell_routing_2026-08-29_m0t120_2_1_251.json`
  (NEW) — the MEASURED-LIVE routing fixture (ran the probe myself; redacted paths).

Tests:
- `tools/test_agent_supervisor_routing_probe.py` (NEW, 27 tests).
- `tools/test_agent_supervisor_recovery_probes.py` — +2 registration/stale tests;
  updated the healthy-checkout `inputs()` helper and 2 end-to-end assertions to
  account for the folded `shell_routing` tooth (see Limitations).
- `tools/test_agent_supervisor_command_authority.py` — +13 Windows-shape coverage
  assertions (`WindowsShapeCoverageTests`) + the existing-coverage map.
- `tools/test_agent_supervisor_bounded_mode.py` (L1) — +5
  `ShellRoutingGateFoldTests` proving the gate-level fold semantics
  (probe three-states at the pinned digest + AND-into-`cli_capability_manifest` →
  `recovery.classify` UNSAFE) and that the identity source is a file hash.
- `tools/test_agent_supervisor_golden_run.py` (L1, admitted) — `GoldenRunBase`
  seeds routing evidence for its fake identity in setUp; +1 tooth-bites test
  (`clear_routing_evidence` → certified start REFUSES).
- `tools/test_agent_supervisor_routing_probe.py` — +`JournalEvidenceTests` (5) and
  the real-claude-digest pass test.

Reports: `M0-T120-producer-report.md`, `M0-T120-routing-evidence.md`.

## Acceptance-scenario mapping

- **AS-1 (live routing proof):** `routing_probe.py`, run from the worktree,
  produced the committed fixture — every tool request recorded; the one mutating
  tool (Edit) brokered+DENIED; zero file writes; provider_calls=3 (≤3). Result:
  2.1.251 routed discovery (Grep) and edit (Read→Edit) to NATIVE tools, 0 shell.
- **AS-2 (native-tool preference):** `NATIVE_TOOLS_GUIDANCE` appended to every
  worker prompt via `build_checkpoint_contract`; names native Read/Grep/Glob/
  Edit/Write and routes validation through `documented_test_commands`;
  `assert_worker_text_clean` passes (test `test_the_guidance_is_worker_text_clean`).
- **AS-3 (pre-dispatch tooth, three states):** `probe_shell_routing_evidence` —
  absent→`routing_evidence_absent`; current (matching pinned DIGEST identity or
  version)→pass; identity/version-mismatch→`routing_evidence_stale`; undetermined→
  `cli_version_undetermined` (fail-closed). Removal-sensitive tests in
  `DriftToothTests` (+ journal-evidence three states in `JournalEvidenceTests`).
  At the START-GATE level the fold is LIVE (limited-auto): the end-to-end
  `golden_run` tooth-bites test proves a certified start REFUSES
  (`UNSAFE_OR_DRIFTED`, `dispatched: false`) with routing evidence cleared, and the
  seeded golden pack dispatches green; `bounded_mode.ShellRoutingGateFoldTests`
  proves the fold semantics deterministically. See L1 — CLOSED.
- **AS-4 (broker preservation):** classifier/policy/broker BYTE-UNTOUCHED (no edit
  to `policy.py`/`broker.py`/`cli.py`); Windows shapes classify ASK/HARD_DENY as
  mapped; only missing assertions added.
- **AS-5 (red/green):** captured verbatim (routing-evidence report §3): tooth
  stub → 3 fails; guidance no-op → 1 fail; green = 160 passed.

## Self-check results (after L1 CLOSED — the fold is live)

- Full supervisor suite: `python -m pytest tools/test_agent_supervisor_*.py -q` →
  **2780 passed, 2 skipped** (2782 collected; +56 tests over the 2726 baseline; 0
  failures). Notable: `golden_run` **42** (was 41; +1 tooth-bites test), and all
  shadow/supervised cmd_start packs (recovery_probes, manifest_binding, model_chain,
  start_reentry, loop) green with the fold live thanks to the limited-auto scoping.
- `python tools/modularity_check.py --check` → `failures 0` (pre-existing warnings
  only; EXIT 0).
- Gate-level tooth-bites captured verbatim in routing-evidence report §6 (certified
  start with evidence cleared → refuse `UNSAFE_OR_DRIFTED`; seeded → dispatch green).

## Design decisions worth the reviewer's attention

1. **R294 folded into the checkpoint contract.** The task's "same append seam"
   naturally reads as a second `run_unit` append, but a standalone append to every
   dispatched prompt broke an out-of-scope exact-prompt-equality test
   (`runner.py::...contract_is_not_duplicated`). Folding the guidance into
   `build_checkpoint_contract` keeps ONE append seam, makes that test's
   `authored = "..." + cr.CHECKPOINT_CONTRACT` automatically include the block, and
   preserves 0 suite failures. `with_native_tools_guidance` is retained as a
   standalone, tested seam (belt-and-suspenders for prompts carrying only an older
   contract).
2. **R295 tooth does NOT auto-launch the CLI in the probe sweep.** An earlier draft
   read the installed version by spawning `claude --version` inside
   `run_live_probes`; that launched the golden tests' launch-counted FAKE
   executables an extra time and desynced their state machines (6 golden + 3
   manifest failures). The tooth now takes the version via injection
   (`installed_cli_version` / an explicit `routing_version_runner`); the sweep does
   not spawn anything. This keeps the hot path non-invasive AND fixed all 9 of
   those failures.

## L1 — CLOSED (orchestrator Option 1: the fold is LIVE and gates dispatch)

Scope was extended twice (start_gate.py + bounded_mode.py, then golden_run.py +
test_agent_supervisor_golden_run.py + test_agent_supervisor_loop.py). The routing
tooth now GATES the certified run.

**The applied fold** (`start_gate.live_revalidation`):
```
if getattr(args, "mode", "") == MODE_LIMITED_AUTO:
    revalidation["cli_capability_manifest"] = bool(
        revalidation.get("cli_capability_manifest")
        and answers["shell_routing"].passes)
```
A failing/undetermined routing tooth drifts `cli_capability_manifest`, which
`recovery.classify` turns into `UNSAFE_OR_DRIFTED` before any provider contact.

**Pinned-identity source (no spawn):** `_claude_identity_digest(executable)` = the
executable DIGEST (the same identity `cli._claude_cli_identity`/the capability
manifest use), computed by hashing the binary. In production the installed claude
digest `d6f6c29a…` matches the committed fixture's `cli_identity`, so the certified
start PASSES (no-op for the good case).

**SCOPE decision — gate the CERTIFIED (limited-auto) run, verbatim to R295.**
R295 says "changed shell-routing behavior cannot silently enter a **certified**
run"; the certified/unattended loop is `limited-auto`. Applying the fold
UNCONDITIONALLY additionally refused **shadow/supervised** cmd_start starts across
SIX test files (golden 7, loop 2, recovery_probes 5, manifest_binding 1,
model_chain 5, start_reentry 5 = 25 failures) — and THREE of those files
(`manifest_binding`, `model_chain`, `start_reentry`) are OUTSIDE even the twice-
extended allowed_paths. Scoping the gate to `limited-auto` (a) is faithful to
R295's "certified run" language, (b) is not weakening/special-casing (the tooth
still RUNS in every mode and its verdict is in the report; only its gating EFFECT
is scoped to the unattended run it protects; a shadow/supervised run is
human-observed), and (c) is the only way to satisfy every standing constraint at
once (gate the tooth, don't edit unadmitted files, no cli.py/broker change, suite
green). After scoping, only the golden (admitted) limited-auto starts needed
seeding. **If unconditional gating in every mode is wanted instead, admit
`manifest_binding.py`, `model_chain.py`, `start_reentry.py` and I will seed them
and drop the mode guard.**

**Seeding design (M0-T072 bound-manifest precedent; NOT a bypass):**
`recovery_probes.record_routing_evidence(journal, cli_identity=…)` records a
routing-evidence record in the DURABLE JOURNAL keyed on the pinned identity, and
`probe_shell_routing_evidence` reads it (dir fixtures + journal, either may match).
The golden harness records ITS OWN fake executable's digest in its temp runtime
journal during setUp (`golden_run.seed_routing_evidence`) — exactly the way it
records a bound manifest. This is NOT a bypass: it never writes the shipped
`fixtures/` dir, never special-cases a fake digest in production policy, and never
weakens the tooth — it records the harness's own measured-analogue evidence in the
same durable state a certified run records its manifest binding. The shipped
package fixture still covers the REAL installed claude.

**Golden-blob-moves consequence (R296):** the supervisor tree hash changes with
these edits; the single M0-T119 recertification certifies the new final identity.

**Removal-sensitivity (the tooth BITES) —** `golden_run.clear_routing_evidence`
removes the seed and
`TwoUnitGoldenRunTests::test_the_routing_tooth_bites_a_certified_start_without_evidence`
asserts the certified start then REFUSES: `dispatched: false`,
`provider_calls_made: 0`, `shell_routing` fails
(`routing_evidence_absent`/`routing_evidence_stale`) →
`failed_steps: ['cli_capability_manifest']` → `UNSAFE_OR_DRIFTED` (verbatim in
routing-evidence §6). Seeded → the whole golden pack dispatches green.

**Not needed:** `test_agent_supervisor_loop.py` was admitted but its failures were
`shadow` starts, resolved by the scoping — left untouched.
- **L2 — live permission-mode finding (F-LIVE-1).** 2.1.251 reports
  `permissionMode=default` despite `--permission-mode manual`; mutating tools are
  still brokered+deniable (verified: Edit denied, no write) but read-only tools are
  auto-allowed and never reach the broker. The broker/runner permission-mode
  contract is out of R293 scope; flagged for the gate.
- **F1/F2 — classifier permissiveness (recorded, NOT fixed per R293):** pipe-to-
  interpreter and `powershell -Command "Remove-Item -Recurse ..."` classify ASK
  (still gated, never AUTO), not HARD_DENY. Captured as explicit tests.
- **Pre-existing `F401`** (`AuditLog` unused import) in
  `test_agent_supervisor_recovery_probes.py` is from M0-T115, not this diff; left
  untouched (CI ruff only lints `services/api/`, so it is not CI-enforced).
- **Sandbox note:** Python is 3.11.9 (repo targets 3.12); the supervisor suite
  collects and passes under 3.11 here, and no touched code uses PEP-695 generics.
  The live probe launched the real 2.1.251 executable successfully.
