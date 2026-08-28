<!-- Saved VERBATIM by the orchestrator from the qa-engineer agent-return channel
     (delta re-attestation after correction round C1-C3; report-preservation rule). -->

Delta verification complete. All claims independently reproduced read-only.

# G4 Delta Re-Attestation — M0-T094 (content identity db689c83e12376384934c67be5debecfd4c7b7b9)

**Reviewed delta:** `git diff f6edf11..db689c8` (db689c8 parent = my reviewed 3c4b888). Full file set: hook (+13, C3), `cli.py` (+8, C1), test file (+41), `M0-T094-operator-channel.md` (C2), 3 saved verbatim gate reports, control-plane `M0-T094.json`. No other production files; guard hooks untouched; all within allowed_paths.

**Commands run (read-only, from a fresh `git archive db689c8` extraction):**
| Command | Result |
|---|---|
| `pytest tools/test_agent_supervisor_operator_channel.py -q` | **54 passed** |
| matrix + command_authority + controller_succession + start_reentry + reviewer + phase1 | **335 passed** |
| Revert C1 (drop `redact_structure` on `--json`), run C1 test | **FAILED** (raw `ghp_…` token present in JSON) |
| Revert C3 (drop `--` separator), run C3 test | **FAILED** (`ValueError: '--' is not in list`) |
| Restore both, re-run | back to green |

**Findings against the four asks:**

**(a) My MINOR-1 resolved — CONFIRMED.** `operator-channel.md` now reads "52/52 PASS" in both places I cited (intro line and §4.3); diff shows exactly `51/51 → 52/52`, no other content change.

**(b) The two NEW tests are real failing-mode tests — CONFIRMED.** I reverted each fix in the scratch copy and observed the corresponding test fail:
- `S2::test_status_json_is_redacted_like_every_transmission` (test L300-312) fails without the fix because a runtime-built token in the durable graceful-stop reason flows unredacted into `status --json` (compose_status reads records verbatim). Genuine guard for the C1 redaction fix. `redact_structure` is already imported at `cli.py:236` (the concise path used it); C1 only closes the `--json` transmission gap — a real, latent secret-leak MINOR now closed, with the section-14 labeling/unknown-never-zero invariants intact (full S2 class still green).
- `S12::test_loop_ask_question_rides_behind_an_end_of_options_separator` (test L834-861) fails without the `--` separator (`echoed.index("--")` raises). Proves a dash-leading `/loop-ask` question rides verbatim after `--` as data, argv[0]=="ask". The fake-root `bound_answer` stub is a disclosed, sound isolation of argv-construction from redaction (redaction covered by S6).

**(c) Nothing else material changed — CONFIRMED.** Only C1 (`cmd_status --json` → `redact_structure(payload).value`, single branch) and C3 (hook `/loop-ask` argv gains `--`) touch production logic; both are strictly behavior-improving (secret-leak closure; option-injection hardening). The test file delta is exactly the two new methods. `M0-T094-G4-qa.md` is my G4 report saved verbatim (only transport entity-decoding noted). `M0-T094.json` is control-plane bookkeeping (status/progress/gate records). No regressions in the 335-test slice.

**(d) G4 PASS stands at db689c8 — CONFIRMED.** Matrix reproduces 54/54; regression slice green; my original MINOR-1 is resolved and no new findings arise. My prior ADVISORY-5 is discharged: the orchestrator reports the CI workflow on pushed SHA 3c4b888 (which carries the full deliverable) completed SUCCESS including the supervisor-bridge whole-suite job — the independent single-run confirmation I requested. My earlier ADVISORY-2 (source-proxy tests) and ADVISORY-3 (zero-context proof honestly deferred to owner-gated C1) are unchanged and remain non-blocking.

DELTA VERDICT: PASS
