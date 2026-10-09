<!-- Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
     (delta re-attestation after correction round C1-C3; report-preservation rule). -->

Delta verified read-only at content identity db689c8. Attestation below.

---

# G5 Delta Re-Attestation — M0-T094 (D-024 unit G)

- Reviewer: security-reviewer (independent, read-only)
- Reviewed-from: f6edf11 (original G5 PASS) → **content identity db689c83e12376384934c67be5debecfd4c7b7b9** (confirmed current HEAD; working tree carries only control-plane files — state.json, M0-T094.json, untracked M0-T094.json report — production code is committed).
- Delta surface (`git diff --stat f6edf11..db689c8`): hook + cli.py (the two corrections), the matrix test file (two new tests), three saved gate reports (G3/G4/G5), operator-channel.md (count fix), task file. **settings.json and both guard packs are absent from the delta** — verified untouched.

## (a) MINOR-1 and ADVISORY-2 faithfully resolved — CONFIRM

- **C1 (my MINOR-1):** `tools/agent_supervisor/cli.py:1537-1543` now emits `print(json.dumps(redact_structure(payload).value, indent=2, default=str))` — precisely the one-line fix I recommended. The whole `status --json` payload (including the newly-added `section14` and the verbatim graceful-stop reason sink I flagged) now obeys the same redaction as `emit_payload` and the concise path. The unredacted-transmission gap is closed.
- **C3 (my ADVISORY-2):** the `/loop-ask` argv is now `[…, "ask", "--codex-executable", exe, "--config", cfg, "--model-selection", sel, "--", argument]` — the three provider options are parsed first, then an explicit `--` end-of-options separator, then the question as the final single element. A dash-leading question is now unambiguously the positional question, never an option. No regression to the single-element/`shell=False` guarantee.

## (b) The new tests are real — CONFIRM

- `S2StatusSection14::test_status_json_is_redacted_like_every_transmission`: builds a runtime token `"ghp_" + "z9Y8"*5`, stores it as a graceful-stop `--reason`, runs `status --json`, and asserts the token is absent and `REDACTED` present — a faithful reproduction of my exact MINOR-1 attack scenario. It is genuinely coupled to the fix (it would fail against the old `json.dumps(payload)`). Token is runtime-built; no committed literal matches gitleaks/redaction patterns.
- `S12HookFailClosed::test_loop_ask_question_rides_behind_an_end_of_options_separator`: echoes the argv the hook actually builds through a fake supervisor root and asserts `--show is this an option?` arrives verbatim as the element after `--`, with `argv[0]=="ask"`. The pass-through `bound_answer` stub is written into the **fake** root only (verified — no real-tree write). Non-vacuous and behavioral.
- Re-ran at db689c8: matrix **54/54 PASS**; the two named tests pass individually; regression slice (command_authority + reviewer + controller_succession) **185 PASS**; `modularity_check --check` **0 failures**.

## (c) Nothing else material changed; no new attack surface — CONFIRM

Both production edits are strictly risk-reducing: C1 adds redaction (reduces disclosure); C3 tightens the option/positional boundary (removes an argparse ambiguity). Neither adds external I/O, new commands, new env trust, or new literal secrets. Settings wiring and the guard packs are untouched in the delta. My non-blocking ADVISORY-3 (POSIX process-group kill for the hook child) and ADVISORY-4 ([HOME] masking) are appropriately carried to the M0-T109 guard-hardening backlog with attribution — consistent with the unit-F residual pattern; neither is a blocker.

## (d) G5 verdict at content identity db689c8

My original G5 PASS stands, and the single MINOR I raised is now closed with a proving test, ADVISORY-2 is closed with a proving test, and the two remaining ADVISORYs are tracked non-blocking. G5 PASS holds at db689c8.

DELTA VERDICT: PASS
