<!-- Saved VERBATIM by the orchestrator from the G4 qa-engineer agent-return channel
     (transport entity-decoding only). Review head a0c48b0, material identity 7d8195b. -->

All verification complete. Here is my complete G4 QA report.

---

# G4 QA GATE REPORT — M0-T120 (D-024 Amendment 14: shell-routing compatibility)

**Reviewer:** qa-engineer (independent, read-only)
**Reviewed identity:** control head `a0c48b0`, material identity `7d8195b`
**Method:** direct file reads + independent pytest at `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`. The worktree-isolation guard blocked git against the shared checkout (`git rev-parse` / `status` refused — expected), so SHA was not re-derived via git; I verified content by direct reads of the packet, both reports, and the touched source, plus full re-run of the suite. This is the established fallback method for this repo.

## 1. Commands run (exact) and results

| # | Command | Result |
|---|---------|--------|
| A | `python -m pytest ctl24/tools/test_agent_supervisor_routing_probe.py test_...recovery_probes.py test_...command_authority.py test_...golden_run.py test_...bounded_mode.py -q` | **301 passed in 36.76s** |
| B | per-module (5 separate runs) | routing_probe **35**, recovery_probes **88**, command_authority **45**, golden_run **42**, bounded_mode **91** |
| C | `python -m pytest ctl24/tools/test_agent_supervisor_*.py -q` (full suite) | **2780 passed, 2 skipped in 205.43s (2782 collected, 0 failed)** |
| D | `... test_...golden_run.py -q -k routing_tooth_bites` | **1 passed, 41 deselected** (`test_the_routing_tooth_bites_a_certified_start_without_evidence` exists & passes) |
| E | `executable_identity(r'C:\Users\MLFLL\.local\bin\claude.exe', name='claude').digest` (read-only hash) | `d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8` = fixture `cli_identity` exactly |

Python is 3.11.9 (repo targets 3.12); the supervisor suite collects and passes under 3.11 and no touched code uses PEP-695 generics.

**Full-suite reconciliation (item 3):** Collected **2782 = 2726 baseline + 56**, passed 2780, skipped 2 (pre-existing platform skips), 0 failed — matches the expected line exactly. The **+56 arithmetic** closes as: routing_probe **35** (new module) + recovery_probes **+2** + command_authority **+13** + bounded_mode **+5** + golden_run **+1** = 56. golden_run = **42** confirmed (was 41; +1 tooth-bites).

## 2. Acceptance-scenario → test/evidence mapping (all backed)

| AS | Requirement | Concrete test(s) / evidence | Verdict |
|----|-------------|------------------------------|---------|
| **AS-1** | live probe bounded, recorded+denied stream, ≤3 calls, honest fixture | `RoutingFixtureShapeTests` (routing_probe.py:48) — asserts `measured` True, `provider_calls_made ≤ ceiling (3)`, `no_worker_file_write_observed` True, real-claude-digest pass; committed fixture stream = Grep(native), Read(native), Edit(native, **brokered+DENIED `no_broker`**); `provider_calls_made=3`; `files_written:false` per assignment; live console output in routing-evidence §1. Fixture `cli_identity` = installed binary digest (independently confirmed, cmd E). | **BACKED** |
| **AS-2** | native-tool prompt guidance + worker-text-clean | `NativeToolsGuidanceTests` (routing_probe.py:318): `test_the_guidance_is_appended_exactly_once`, `test_the_guidance_is_worker_text_clean` (calls `assert_worker_text_clean`), documented_test_commands + native tools referenced, sentinel-in-source-file. `NATIVE_TOOLS_GUIDANCE` folded into `build_checkpoint_contract` (claude_runner.py:913) so it rides the single append seam onto every worker prompt; `claude_native_tools.md` names Read/Grep/Glob/Edit/Write and routes validation through `documented_test_commands`, no quotas/countdowns. | **BACKED** |
| **AS-3** | tooth three states + GATE-level tooth-bite | Probe-level: `DriftToothTests` (routing_probe.py:145) — absent→`routing_evidence_absent`, different-identity→`routing_evidence_stale`, undetermined→`cli_version_undetermined`; `JournalEvidenceTests` (journal three states). Gate-level: `ShellRoutingGateFoldTests` (bounded_mode.py:1349, 5 tests: pass / no-evidence→UNSAFE / stale→UNSAFE / current→safe / identity-by-file-hash-not-spawn) + **golden `test_the_routing_tooth_bites_a_certified_start_without_evidence`** (end-to-end `cli.main` limited-auto refuse). | **BACKED** |
| **AS-4** | broker preservation; shapes ASK/HARD_DENY; classifier byte-untouched | `WindowsShapeCoverageTests` (command_authority.py:560) — **13 assertions**: here-string/pipeline/redirection/compound/`cmd /c &`/scratch-copy/ambiguous-env = ASK; iex+`-EncodedCommand`/credential-path/recursive-delete/control-disabling = HARD_DENY; + `test_finding_f1/f2`. `policy.py`, `broker.py`, `cli.py` are NOT in allowed_paths (untouched); the R295 fold lives in `start_gate.live_revalidation` (allowed), reusing the existing `cmd_start`→`live_revalidation` wiring so cli.py needed no edit. | **BACKED** |
| **AS-5** | red/green captured | routing-evidence §3 RED: tooth stubbed → 3 fails whose names match `DriftToothTests` methods exactly; guidance no-op → 1 fail = `test_the_guidance_is_appended_exactly_once`. Gate-level RED §6a: cleared evidence → `UNSAFE_OR_DRIFTED`, dispatched False, 0 provider calls. GREEN independently re-run (cmds A–D). | **BACKED** |

## 3. Red/green integrity (item 4)

- The tooth compares a **recorded** digest (shipped fixture + durable journal `SHELL_ROUTING_EVIDENCE_KEY`) against the **file-hashed pinned identity** (`_claude_identity_digest` / `installed_cli_identity`) — **not live-to-live**. `probe_shell_routing_evidence` matches on exact `fx_identity == identity`; version is only a fallback when no digest is supplied. Confirmed non-tautological: the shipped fixture digest = the real installed binary (cmd E), while the golden tooth-bite uses a **different fake** digest.
- Gate-level RED is consistent with the design: clearing the seed yields `routing_evidence_stale`/`routing_evidence_absent` → folds `cli_capability_manifest` to False → `recovery.classify` → `UNSAFE_OR_DRIFTED`, `dispatched: false`, `provider_calls_made: 0`. Removing the fold line would make the golden tooth-bite test fail (dispatched would flip True), so the fold is removal-sensitive.

## 4. Fixture / evidence integrity (item 5)

Fixture `shell_routing_2026-08-29_m0t120_2_1_251.json`: `schema shell_routing/v1`, `measured:true`, `provider_calls_made:3` (ceiling 3), `no_worker_file_write_observed:true`, `claude_version "2.1.251"`, `routing_summary` = 3 native / 0 shell / verdict `native_preferred`, tool stream Grep→Read→Edit with Edit `brokered:true`. `cli_identity d6f6c29a…` = the installed binary (independently re-hashed). Cross-report agreement: producer-report AS-1 mapping, routing-evidence §1 table, and the fixture all state provider_calls=3, 0 shell, Edit brokered+DENIED — mutually consistent and consistent with my runs. (Suite-count numbers do NOT fully agree across the two reports — see Finding MINOR-2.)

## 5. Negative-space analysis (item 6)

- **Any limited-auto dispatch path bypassing `live_revalidation`?** No. `cmd_start` (cli.py:2895-2905): dispatchable → `live_revalidation` (fold applied when `mode==MODE_LIMITED_AUTO`); non-dispatchable/packet-error → `unprobed_revalidation` sets **all** STEP_PROBES False (incl. `cli_capability_manifest`) → refuse. There is no limited-auto path to dispatch that skips the routing check.
- **Over-seeding that could mask a failing tooth?** No. Only `golden_run.seed_routing_evidence` seeds, and it records **only its own fake exe's digest** (`executable_identity(claude_executable).digest`). `record_routing_evidence` requires a non-empty identity and dedups **per identity**; `probe_shell_routing_evidence` matches on exact digest equality with no wildcard. All other `record_routing_evidence` calls are unit tests using specific fake identities (incl. an idempotent-per-identity test and an empty-identity-rejection test).
- **Mode-scoping (orchestrator ruling under scrutiny):** the fold gates only limited-auto. Shadow forwards nothing; supervised holds every prompt for a human — neither is the unattended "silent entry" R295 targets. **Is the evidence check still hit at the limited-auto start after a supervised run carried stale routing?** **YES.** Each `start` runs its own `live_revalidation` reading fixtures+journal fresh and re-applies the fold at every limited-auto start; the tooth is not cached across runs. Proven both by the code path and end-to-end by the golden test (seeded limited-auto dispatches green; cleared limited-auto refuses).

## 6. Findings

- **MINOR-1 (report hygiene):** producer-report file-list states `routing_probe.py (NEW, 27 tests)`; the actual module has **35** tests. The +56 total only closes with 35 (35+2+13+5+1). Recommend correcting the sub-count.
- **MINOR-2 (report hygiene):** routing-evidence **§3** (`routing_probe 27`) and **§4** (`2773 passed, 2 skipped, 2775 collected; +49`) are stale intermediate snapshots that contradict **§6b** and the producer-report self-check (`2780 / 2 / 2782; +56`). The authoritative final numbers (§6b) match my run exactly; §4/§3 should be reconciled to the final. Non-blocking because the correct numbers are present and independently reproduced.
- **MINOR-3 (forward-looking maintenance):** the gating fold hardcodes `mode == MODE_LIMITED_AUTO` rather than membership in `OWNER_GATED_MODES`. Correct today (test asserts `OWNER_GATED_MODES == (MODE_LIMITED_AUTO,)`), but any future certified/unattended mode added to `OWNER_GATED_MODES` would silently escape the routing gate. Worth a comment or a set-membership check.
- **MINOR-4 (stale comment):** `test_agent_supervisor_bounded_mode.py:1346-1348` still describes the LIVE fold line as "staged"; the fold is now live (L1 CLOSED). Doc-only.
- **INFO:** F1 (`… | sh`) and F2 (`powershell -Command "Remove-Item -Recurse …"`) classify **ASK not HARD_DENY** — recorded-not-fixed per R293 (classifier frozen), captured as `test_finding_f1/f2_*` asserting current ASK behavior so future tightening surfaces as a test update. Both remain gated (never AUTO). F-LIVE-1: 2.1.251 reports `permissionMode=default` despite `--permission-mode manual`; mutating tools are still brokered+DENIED (fixture: Edit denied, no write). Both explicitly out of R293 scope and appropriately flagged.
- **INFO:** the routing tooth is evaluated once per `start` (pre-dispatch), not per cycle — consistent with every other S11.5 probe, and safe because the binary identity is pinned and `DISABLE_AUTOUPDATER=1` is forced for the run.

No BLOCKER or MAJOR findings. All five acceptance scenarios are backed by tests I independently re-ran and passed; the full suite reconciles to 2782/2780/2 exactly; the fixture pins the real installed binary; the tooth genuinely bites; and no dispatch bypass or over-seeding exists. The MINOR items are report-hygiene / forward-looking and do not affect delivered behavior; I recommend the orchestrator have the producer reconcile the stale counts (MINOR-1/2) as a doc-only touch-up (non-blocking for G4).

**G4 VERDICT: PASS**
