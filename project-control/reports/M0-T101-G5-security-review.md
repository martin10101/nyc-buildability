# M0-T101 — G5 Independent Security Review

> Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
> (transport entity-decoding only). Verdict: PASS. Reviewer preamble: "All dimensions
> verified. CI wires both the validator (ci.yml:456) and the test suite (ci.yml:458), so the
> pin is machine-enforced. Ruff clean."

# G5 Security Review — M0-T101 (MCP-policy validator: strict `statusLine` shape)

**Task:** M0-T101 — extend the D-020 MCP default-deny validator to accept the D-027-authorized `statusLine` key with a strict, fail-closed, exact-command shape.
**Reviewer:** independent G5 security reviewer (read-only)
**Date:** 2026-08-26 UTC · branch `control/D-024-fable-codex-loop`
**Frozen content SHA:** `4e894af779679a61cc34d96e9dd1a0f5f88396af` (short `4e894af`).
> Note on the packet SHA: the task prompt cites `4e894afe`, which does not resolve. The correct short SHA is `4e894af7` (`4e894af` is unambiguous). The last hex digit in the packet is a transcription error; content identity is otherwise exact and confirmed below.
**Parent (pre-content):** `718b53d` · **Current HEAD:** `dac4bb3` (submit commit; control-plane only).
**Files reviewed (frozen):** `tools/validate_mcp_policy.py`, `tools/test_mcp_policy.py`, `project-control/reports/M0-T101-mcp-policy-statusline-shape.md`.

## Verdict: PASS

No blocking, major, or minor defects. One nit (documentation completeness), non-blocking.

---

## Evidence and reproduction

All commands run read-only from the repo root. Working-tree tool files are byte-identical to frozen `4e894af` (`git diff 4e894af -- tools/validate_mcp_policy.py tools/test_mcp_policy.py` → empty), so the runs below test the frozen content.

- **Test suite:** `python -m pytest tools/test_mcp_policy.py -q` → **42 passed / 0 failed** in 0.48s.
- **Live validator:** `python tools/validate_mcp_policy.py --check` → **EXIT=0** (includes the p10 CI-wiring self-check).
- **Ruff:** `ruff check tools/validate_mcp_policy.py tools/test_mcp_policy.py` → `All checks passed!`
- **Content diff surface** (`git diff --stat 718b53d 4e894af`): exactly 3 files — `tools/validate_mcp_policy.py` (+24), `tools/test_mcp_policy.py` (+37), `project-control/reports/M0-T101-mcp-policy-statusline-shape.md` (new, +72). No deletions.
- **Full task range** (`git diff --name-only 718b53d dac4bb3`): the two tool files + M0-T101 report + M0-T101 control-plane records (task/gate/reports/evidence-map/state) only.

---

## Findings by review dimension

### 1. No weakening of pre-existing checks — CONFIRMED (from the diff, not the report)
The full patch of both tool files is **purely additive**. In `validate_mcp_policy.py` the only new content is: the `EXPECTED_STATUSLINE_COMMAND` constant, the `_is_statusline_shape` helper, and one `KNOWN_KEY_SHAPES` entry (`"statusLine": (_is_statusline_shape, …)`). Every hunk is `+`-only against unchanged context; no p1–p10 line (deny lists, empty allowlist `p3`, disabled mcpjson `p5`, hooks/preservation `p7`, `mcp__*` deny `p8`, unknown-key fail-closed `p9`, CI twin-check `p10`) is modified or deleted. The 5 tests are appended in a new `statusLine shape` section; no existing test is altered. This satisfies the packet's "touches ONLY the two tool files + the new report; every pre-existing p1–p10 check unchanged" requirement.

### 2. The pin and the every-tick execution-vector mitigation — CONFIRMED
`EXPECTED_STATUSLINE_COMMAND` (concatenation of the two source literals) equals the committed `.claude/settings.json` `statusLine.command` **byte-for-byte**: both are `python -m tools.agent_supervisor.telemetry_statusline --journal .claude/telemetry/statusline_journal.jsonl` (len 106 == 106, programmatic `==` → True). The same string is corroborated by the M0-T100 activation report (`M0-T100-statusline-activation.md:19`), its evidence-map, and the M0-T100 G5 review (`M0-T100-G5-security-review.md:25`).

The exact-command pin **adequately mitigates** the M0-T100 G5 "every-tick execution vector" concern: any swap or mistype of the committed `statusLine.command` now yields a `p9` error, and CI runs both the validator (`.github/workflows/ci.yml:456`, `python3 tools/validate_mcp_policy.py --check`) and its test suite (`ci.yml:458`). A changed command therefore fails CI; passing it requires a reviewed change to `EXPECTED_STATUSLINE_COMMAND` in the same PR — the intended-visibility discipline already applied to `DENIED_SERVER_NAMES` and the hook commands. This is a least-privilege posture (exactly one command permitted).

### 3. Fail-closed completeness — CONFIRMED (each variant closed)
`_is_statusline_shape` = `isinstance(v, dict) and set(v) == {"type","command"} and v.get("type") == "command" and v.get("command") == EXPECTED_STATUSLINE_COMMAND`. Enumerated bypass attempts:
- **Trailing/leading whitespace on command** → `!= EXPECTED` (exact string equality) → fails closed.
- **Unicode homoglyphs / different bytes** → `!= EXPECTED` → fails closed.
- **`type` case variation (`"Command"`, `"COMMAND"`)** → `v.get("type") == "command"` false → fails closed.
- **Nested object / non-string command (dict, list, number)** → never `==` the str pin → fails closed.
- **Extra keys (`refreshInterval`, `padding`, even alongside the correct command)** → closed-set `set(v) == {"type","command"}` false → fails closed.
- **Missing a sub-key (only `type`, or only `command`)** → set mismatch → fails closed.
- **Whole-key absence** → the `p9` loop only inspects keys `present` in the file, so an absent `statusLine` is simply not checked → remains valid (owner-optional activation, as intended).
The closed-set check plus two exact `==` comparisons form a complete closed shape; I found no permissive slip-through.

### 4. Tests genuinely mutation-detecting — CONFIRMED
Of the 5 new tests, three are permissive-mutation teeth: `test_statusline_wrong_type_fails_closed` (string body), `test_statusline_different_command_fails_closed` (`powershell -c calc`), and `test_statusline_extra_key_fails_closed` (`refreshInterval` added) each assert `any(e.startswith("p9") and "statusLine" in e …)`; against a mutant where `_is_statusline_shape` returned `True` permissively, all three would fail — genuine teeth. `test_statusline_absent_still_passes` guards the opposite regression (over-strictness/false positive on absence). `test_statusline_command_pinned_to_committed_settings` binds `self.intact["statusLine"]["command"]` to `vmp.EXPECTED_STATUSLINE_COMMAND`; `self.intact` is loaded from `vmp.DEFAULT_SETTINGS` (= the real `.claude/settings.json`), so the pin and the committed file cannot drift apart silently — it does bind to the committed file. Additionally, the red half of the red/green proof is real: before this fix the committed `statusLine` was an unknown p9 key, so the intact-fixture tests (`test_committed_settings_pass`, `test_intact_fixture_passes_in_temp_dir`, `test_main_check_exit_zero`, `test_valid_default_mode_passes`, `test_extra_deny_rules_alongside_wildcard_pass`) failed until the shape was registered.

### 5. Scope — CONFIRMED
Forbidden-path probe over the full range `718b53d..dac4bb3` for `.claude/settings.json`, `.claude/hooks`, `tools/project_control.py`, `apps`, `services`, `supabase` → no hits. No `M0-T099*` or `M0-T100*` artifact changed in the range. `.claude/settings.json` was last modified by `a0b945e` (M0-T100), **not** by this task. Accepted M0-T099/M0-T100 work is untouched.

---

## Cross-cutting security checks (mandate)
- **Cross-tenant isolation, service-role secrecy, private storage, SSRF, upload controls, log redaction:** not implicated — this is a stdlib-only, read-only config validator with no data plane, network, secret, or storage surface.
- **Injection defenses:** the change adds no execution surface; the `statusLine` command is a fixed literal in tracked settings (its own execution surface was reviewed under M0-T100 and is unchanged here). This task **tightens** defense-in-depth by pinning that literal.
- **Prompt-injection:** not applicable; no model-facing input path added.
- **Least privilege:** the exact-command pin is a least-privilege tightening — the settings file may carry only the one authorized command.

## Modularity
Additive change of +24 SLOC to `validate_mcp_policy.py` (350 SLOC total, well under the 600 warn threshold), single responsibility preserved (settings-shape validation), no dumping-ground growth, focused tests added. No modularity concern.

## Nit (non-blocking)
- The module-level p-section docstring (lines 10–45) enumerates p1–p10 but does not name `statusLine` explicitly; the new key is covered generically by the p9 prose ("EVERY key present must be a known key matching its expected shape") and by the constant/helper docstrings. Purely cosmetic; no action required for acceptance.

## Directive posture note (for the orchestrator, not a review finding)
The producer report cites `D-020:ALL;D-027:ALL` with an empty applicable set (rows bind their original tasks; empty-set rows recorded at DCV). The independent `directive-compliance-verifier` pass and `verification.json` are the authority for in-regime acceptance; this G5 security verdict does not substitute for that DCV.

**Final verdict: PASS** — no weakening, byte-exact pin bound to the committed file, complete fail-closed shape, mutation-detecting tests (42/42 green, live validator EXIT=0, ruff clean), scope respected, accepted artifacts untouched.
