# GATE REPORT — G3 Independent Code Review — M0-T132 (verbatim reviewer return)

- **Task:** M0-T132 — D-024 Amendment 34/35: Claude Code 2.1.252 admission + combined R247 recertification
- **Reviewed SHA:** `d743ad24446455f01ff859304ae838c6b7792c6c` (HEAD == frozen SHA confirmed; branch `control/D-024-fable-codex-loop`)
- **Code identity reviewed:** producer commit `259833de` (the only commit carrying the fixture/test/module changes); `d743ad24` is the control-plane submit on top.
- **Reviewer role:** read-only. No project-control CLI, git-write, or gh invoked.
- **Verdict:** **PASS** (four LOW/INFO advisories below; none blocking)

## Reproduction environment
- Installed CLI on PATH: `/c/Users/MLFLL/.local/bin/claude`, `claude --version` = **`2.1.252 (Claude Code)`** — matches the admitted fixtures, so the live drift teeth executed (not skipped).
- Four affected packs: `PYTHONPATH=. python -m pytest tools/test_agent_supervisor_{event_bus,capability_probe,native_adapter,routing_probe}.py -q` → **150 passed, 0 skipped** (live `@requires_claude` teeth ran green).
- `ruff check` on `event_drift.py` + the 4 tests → **All checks passed**. `python tools/modularity_check.py --check` → **exit 0** (`event_drift.py` not flagged; warns are pre-existing on untouched modules).

## Focus-area findings

### 1. Re-pointing correctness — PASS
- `tools/agent_supervisor/event_drift.py:45` `CATALOG_FIXTURE_PATH` → `hook_event_catalog_2_1_252.json`; the comment (`:37-44`) accurately explains the benign patch bump. This is the only manifest-tracked change.
- All four consumers re-pointed with updated version/task assertions: `event_bus.py:28` + `:302-303` (task M0-T132, version 2.1.252, 33 events); `capability_probe.py:36` + `:236-243` (2.1.252, filename `m0t132`); `native_adapter.py:25` + `:670-671` (task M0-T132, 2.1.252); `routing_probe.py:40` + `:53-61,245-246` (2.1.252, task M0-T132, digest identity).
- **INFO-1 (non-blocking, out of scope):** two other 2_1_251 references remain and are *correct to leave*: `guardrail_refusal.py:164` (functional pointer to `guardrail_refusal_shapes_2_1_251.json`) and `loop_interception_detection_2_1_251.json` (read by `operator_channel` test `:690` asserting `"2.1.251"`), plus a comment at `claude_runner.py:900`. These are documentation-confidence, C1-canary-gated surfaces that were **not** in Amendment 34's "three affected fixtures" scope and are **not** in the packet `allowed_paths` — re-pointing them would be a scope violation. I confirmed they carry no live-installed version tooth (grep + whole-suite 0-failed), so no hidden RED. Advisory: after admission these two surfaces label the base CLI as 2.1.251, lagging the installed 2.1.252 by one patch (pre-existing from M0-T118).

### 2. Fixture provenance/shape — PASS
- `shell_routing_..._2_1_252.json`: `cli_identity == e713c5a6c8bc71afbc149988c0d7ac4e313bf371316ed2b34e261e34c785a883`, `measured: true`, `routing_summary.verdict == native_preferred`, `capture_model == "claude-opus-4-8"` with an explicit `capture_note` on the Fable cap. Paths masked as `<executable>` / `<tmp>\routing_probe_<id>`.
- `hook_event_catalog_2_1_252.json`: **33 events, byte-identical event set to 2.1.251** (verified set-symmetric-difference empty), `claude_version == "2.1.252 (Claude Code)"`, `confidence == official-docs`.
- `capability_probe_..._2_1_252.json`: `claude --help` `output_sha256` **unchanged** (`83af8a9a7edc…` in both 251/252); only the `claude_version` line and its hash moved (`075f89d9…`); flags + codex identical — an honest patch-bump capture.
- `native_runtime_detection_..._m0t132.json`: flags/verbs/`background_gaps` identical to 2.1.251, version 2.1.252.
- **No home/user-path leak** in any of the four fixtures (repo-wide scan clean; `probe_meta` binary paths all `[HOME]`-masked).

### 3. Honesty of disclosures (recert §4) — PASS (within code-review scope)
- §4.1 (routing on opus, Fable capped) is consistent with the fixture's `capture_model`/`capture_note` and with `admission-evidence.md` §3, which honestly documents the cap, the `rate_limit_event rejected` signal, and the **deletion** of the capped `no_tool_observed` artifact (it would have false-greened the digest-keyed gate). Nothing overstated.
- §4.2/§4.3 (doctor `--live` control-response FAILED as a cap artifact; journal control_response probe refreshed while `transitions=35`/`audit=85` unchanged) are **runtime/journal state claims not verifiable from the static diff** — the journal is a forbidden path and is absent from the commit (preserved). They are internally consistent (the routing fixture does record a live brokered `can_use_tool` on Edit, corroborating "protocol works"). **Defer to DCV/G4/orchestrator journal verification.**

### 4. Removal-sensitivity — PASS (strong, empirically reproduced)
- Three live teeth are `@requires_claude` and **ran green against the live 2.1.252 binary**: `event_bus::test_s8_live_version_matches_catalog_fixture` (confirmed executed, not skipped), `capability_probe::test_live_reprobe_claude_version_matches_fixture` (`:186-191`), `native_adapter::test_live_detection_matches_committed_fixture` (`:722-731`). Each asserts `installed == fixture version`, so any drift goes RED.
- Routing tooth bites forward drift: `probe_shell_routing_evidence(installed_version="2.1.253")` → `routing_evidence_stale`; wrong digest → `routing_evidence_stale` (reproduced directly). Red-proof teeth (`test_a_mismatched_digest_identity_refuses`, stale-by-version) present and passing.
- Note: `installed_version="2.1.251"` still passes only because the old fixture is retained (append-only history) and production keys on the executable **digest** — by design, not a defect.

### 5. Regression / scope — PASS
- Full base→HEAD change set: the 10 code/script files are **exactly within** `allowed_paths`; no `apps/packages/services/supabase`, no `tools/agent_supervisor/journal*`, no `project_control.py`/`directive_registry.py`/`validate_directive_compliance.py` touched.
- The additional control-plane files (directives, state.json, tasks/M0-T132.json, gates, blockers, campaigns, SESSION_HANDOFF, and the G2/G0/recert/evidence-map reports) are orchestrator-authored lifecycle/registry writes, legitimate for this orchestrator-run governance task under ADR-005.
- `event_drift.py` is 113 lines; the change is a one-line fixture path + comment — no responsibility mixing, public interface (`CATALOG_FIXTURE_PATH`) name-stable.

## LOW advisories (non-blocking; suggest orchestrator note, not rework)
- **LOW-1:** `project-control/reports/M0-T132-routing-capture.py:23` hardcodes `C:/Users/MLFLL/.local/bin/claude.exe`, exposing the username in a committed file the project otherwise scrubs. It is a reproducibility harness (not a fixture, not a secret), but consider resolving the exe via PATH or a parameter.
- **LOW-2:** `tools/test_agent_supervisor_routing_probe.py:57` loosened `assertEqual(requirement, "R292")` → `assertIn("R292", requirement)` (the field is now the descriptive string `"R292/R295 recaptured at the 2.1.252 admission"`). Still meaningful; noted for the record.
- **LOW-3:** Packet output/`allowed_paths` name `M0-T132-producer-report.md`, which is **absent**; its producer-self-check role is fulfilled by `M0-T132-G2-self-check.md` (present, labeled a G2 self-check). Bookkeeping mismatch between the packet and the tree — recommend the orchestrator record the equivalence.

## Notes for downstream gates
- Whole-suite reconciliation (3,040+3 = 3,043 passed / 2 skipped / 0 failed) is a **G4** claim; I deliberately did not run the whole suite. I independently confirmed the mechanism: the three M0-T131 CLI-drift failures are exactly the three live version teeth, all of which now pass at 2.1.252.
- The doctor/journal/manifest/verify-controller/repin claims (recert §3/§4/§5) are orchestrator/operator-executed and outside the reviewable code diff — for DCV + G4 + the orchestrator to verify against live control-plane state.

**VERDICT: PASS.**
