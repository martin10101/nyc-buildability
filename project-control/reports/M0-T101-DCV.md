# M0-T101 — Directive-Compliance Verification (DCV)

> Saved VERBATIM by the orchestrator from the directive-compliance-verifier agent-return
> channel (transport entity-decoding only). Verdict: PASS. Reviewer preamble: "All evidence
> reproduced. The M0-T101 deliverable blobs are byte-identical at frozen 4e894af and HEAD."

# DCV Report — M0-T101 (D-020:ALL; D-027:ALL)

**Task:** M0-T101 "D-027 follow-up: admit the statusLine key into the MCP-policy validator shape table (post-acceptance discovery)"
**Frozen content:** commit `4e894af` · **Verdict basis:** every point below reproduced independently, read-only.
**Reviewer:** directive-compliance-verifier (producer ≠ verifier; producer_agent = orchestrator).

## (a) Reproduced empty-applicable-set evidence

In-process resolver over the packet (`tools/directive_registry.py evaluate_task_refs`):
```
OK: True   APPLICABLE_COUNT: 0   APPLICABLE_IDS: []   MISSING: []   REASONS_HEAD: []
```
Structural confirmation of *why* it is empty (conjunction semantics):
- `grep -c "M0-T101"` in `project-control/directives/D-020-program-wide-mcp-default-deny/requirements.json` → **0**; in `.../D-027-statusline-activation/requirements.json` → **0**. M0-T101 is named in no requirement row.
- Every D-027 row binds `task_ids` `["M0-T100"]` or `["D-027-BOOTSTRAP","M0-T100"]` with `task_types: []`. Every D-020 row binds sentinels like `["D-020-BOOTSTRAP"]`/original M0-T077-era ids with `task_types: []`, `milestones: []`, `paths: []`. None intersect M0-T101.

The empty applicable set is confirmed. Per registry rules the empty-set task rows are still recorded at acceptance; the substance was verified anyway below.

## (b) Per-directive substance rows

### D-020 (program-wide MCP default-deny) — **PASS**
- **Diff is additive-only.** `git show 4e894af --numstat` for `tools/validate_mcp_policy.py` = **24 insertions, 0 deletions** (deletion-line count = 0). The change adds exactly: `EXPECTED_STATUSLINE_COMMAND` constant, `_is_statusline_shape` helper, one `KNOWN_KEY_SHAPES["statusLine"]` entry. No deny list, allowlist-emptiness, hooks, permissions, or any p1–p10 check is edited.
- **Fail-closed on unknown keys intact.** The unchanged p9 logic (`tools/validate_mcp_policy.py` lines 288–300: `spec = KNOWN_KEY_SHAPES.get(key)` → `None` yields `"p9 unknown settings key … (fail closed…)"`) is outside the diff. Mutation tests exercise it (wrong-type / different-command / extra-key → p9).
- **Live check green.** `python tools/validate_mcp_policy.py --check` → **EXIT=0** at the committed settings.

### D-027 (statusLine activation linkage) — **PASS**
- **Command pin matches three independent sources.** `EXPECTED_STATUSLINE_COMMAND` (concatenated) = `python -m tools.agent_supervisor.telemetry_statusline --journal .claude/telemetry/statusline_journal.jsonl`, byte-equal to `.claude/settings.json` `statusLine.command` (at `4e894af` and HEAD) and to the block quoted in `project-control/reports/M0-T100-statusline-activation.md` §1.
- **Absence-of-key stays valid.** Validator iterates only present keys; `test_statusline_absent_still_passes` asserts `errors == []` after popping the key — consistent with D-027's owner-optional/passive posture.
- **Accepted M0-T100/M0-T099 untouched.** `.claude/settings.json` (M0-T100's deliverable, in this packet's `forbidden_paths`) is absent from `git diff --name-only 8749fae HEAD -- .claude/settings.json` (empty) and last changed by `a0b945e` (M0-T100 content). The frozen commit `4e894af` touched only 3 files, none under M0-T100/M0-T099.

## Additional required checks (points 3–5)

- **Repair discipline (new bounded task, not an edit to accepted work) — PASS.** M0-T101 control records all present: `gates/M0-T101-G0.json` (PASS), `reports/M0-T101-G0-readiness.md`, claim + `gates/M0-T101-G2.json`, `reports/M0-T101-G2-self-check.md`, `reports/M0-T101-evidence-map.json`, and the repair report. Frozen diff surface = exactly `{tools/validate_mcp_policy.py, tools/test_mcp_policy.py, project-control/reports/M0-T101-mcp-policy-statusline-shape.md}` = the packet's `allowed_paths` exactly; no `forbidden_paths` entry touched.
- **Tests — PASS.** `python -m pytest tools/test_mcp_policy.py -q` → **42 passed** (EXIT 0). The 5 new statusLine tests exist and assert: `test_statusline_wrong_type_fails_closed` (string → p9), `test_statusline_different_command_fails_closed` (`powershell -c calc` → p9), `test_statusline_extra_key_fails_closed` (`refreshInterval` → p9, closed shape), `test_statusline_absent_still_passes` (removal valid), `test_statusline_command_pinned_to_committed_settings` (pin vs committed file). The pin-drift test is genuine: fixture `self.intact` loads from `vmp.DEFAULT_SETTINGS = ROOT/".claude"/"settings.json"` (the real committed file, read-only).
- **Report accuracy — PASS.** Every claim in `M0-T101-mcp-policy-statusline-shape.md` (5-test-then-fix RED/GREEN, "one shape helper + one table entry", "no MCP rule weakened", 42 passed, live validator EXIT=0, diff = allowed_paths, accepted artifacts untouched, empty applicable set recorded at DCV) reproduces against observed evidence.

## (c) Overall verdict: **PASS**

Every point reproduces from primary evidence (source files, deterministic tests, git objects, in-process resolver). No VIOLATED or UNVERIFIABLE requirement. Since the resolver's applicable set is empty, the recorded acceptance rows are the two empty-set directive task rows (D-020, D-027); their substance is nonetheless independently confirmed non-weakening.

## (d) Content identity observed

- **Frozen M0-T101 content: `4e894af`.** The three deliverable blobs are byte-identical at `4e894af` and current HEAD (`tools/validate_mcp_policy.py` blob `d4548db…`, `tools/test_mcp_policy.py` blob `e5d1296…`, report unchanged). M0-T101 content identity is stable.
- **Later commits:** `dac4bb3` (immediate next) is **control-plane only** — M0-T101 G2 self-check + submit (`gates/`, `reports/`, `state.json`, `tasks/M0-T101.json`). Current HEAD is `e8b21d1`, which is **M0-T090's** frozen content (`tools/agent_supervisor/*.py` + `tools/test_agent_supervisor_bounded_contracts.py`, D-024-R101) — a **separate task**, touching **no** M0-T101 deliverable file. So relative to M0-T101, later commits are either control-plane (dac4bb3) or unrelated-task content that does not modify any M0-T101 path.

**Recommendation to orchestrator: record this gate as PASS.** (Reviewer is read-only; the orchestrator records `verification.json` and the gate result after validating this report.)
