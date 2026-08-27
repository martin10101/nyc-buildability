# M0-T108 directive-compliance verification (DCV) — VERBATIM save

Verifier: independent read-only `directive-compliance-verifier` (unnamed spawn) ≠ producer
(`orchestrator`). Verified M0-T108's D-024 applicable set at HEAD `2d3c645f` (identity `90376158`);
mid-review HEAD advanced to `4014ee7a` (docs-only handoff note), directive registry + M0-T108
allowed_paths byte-identical, identity re-stamps to the same `90376158`. Returned through the
agent-return channel 2026-08-27 UTC and saved verbatim below (transport entity-decoding only; the
harness neutralized `<`/`>`/`&` and flagged the output as instruction-shaped — control tags were
neutralized and the content is preserved here as verifier findings, not instructions).

---

I have complete, independently-reproduced evidence. The `test_directive_compliance` suite is genuinely slow (>20 min, no flush; each attempt exceeded the sandbox budget) and is a general regression suite, not load-bearing for the empty-set determination, which is proven three independent ways. Here is my report.

---

# DCV Report — M0-T108 (Control-plane security fix: readonly_agent_guard PowerShell/scripting write gap)

## Verdict: `DCV: PASS`

**M0-T108 D-024 applicable set = EMPTY; verified independently at HEAD 2d3c645f / identity 90376158; no selective citation across active directives.**

Task M0-T108 is in-regime (`directive_refs: [{"directive_id": "D-024", "requirement_ids": "ALL"}]`, `directive_regime_version` 1.0, status `awaiting_gate`). Its D-024 applicable requirement set is genuinely empty, so there are zero in-scope requirement IDs to individually satisfy, and the selective-citation guard across all 28 active directives is clean. The single mid-review commit is a docs-only handoff note that leaves the reviewed identity and the directive registry byte-identical.

## Frozen-identity verification

| Check | Command | Observed |
|---|---|---|
| HEAD at review start | `git rev-parse HEAD` | `2d3c645f14aaa77b2fcf7da7cade3e1808c74d11` (matches frozen SHA) |
| Branch | `git branch --show-current` | `control/D-024-fable-codex-loop` (matches) |
| Content-manifest identity | `_task_git_identity(reg_mod, M0-T108 packet)` | `90376158…`, resolved SHA = HEAD, ERR = None (in-scope files tracked & clean) |

**Mid-review HEAD advance (disclosed, benign).** HEAD advanced to `4014ee7a`. `git diff --name-status 2d3c645f..HEAD` = sole changed file `docs/SESSION_HANDOFF.md`. `git diff --stat 2d3c645f..HEAD -- project-control/directives project-control/tasks/M0-T108.json .claude/hooks .claude/settings.json` is **empty** — M0-T108's allowed_paths, its packet, and the entire directive registry are byte-identical across the two SHAs. The content identity re-stamps to the same `90376158` at HEAD `4014ee7a`. Not a mid-review supersession; the empty-set determination is unaffected.

## Step 1 — Resolver (`evaluate_task_refs`)

Returned (identical at both SHAs): `{'ok': True, 'applicable_ids': [], 'cited_ids': [], 'missing_ids': [], 'invalid_refs': [], 'unresolved': [], 'reasons': []}`. Meets every required condition.

## Step 2 — Independent inspection of D-024 `requirements.json` (not trusting the resolver)

Re-implemented the registry's conjunction semantics against M0-T108's dimensions (`task_id=M0-T108`, `task_type=governance`, `milestone_id=M0`, allowed_paths):
- 219 requirements, all binding, 0 malformed applicability, 0 wildcard rows.
- All 219 scoped ONLY by `task_ids`; `task_types` used by 0, `milestones` by 0, `paths` by 0.
- Requirements with `task_types` incl `governance`: 0. With `milestones` incl `M0`: 0. With `paths` intersecting M0-T108's allowed_paths: 0. Naming `M0-T108` in `task_ids`: 0.
- **Independent match count against M0-T108: 0.**
- Corroboration: `grep "M0-T108"` across the D-024 registry hits only `manifest.json` audit-log line 407, documenting M0-T108 as "created as a standalone governance task citing D-024:ALL (not amendment scope)" and explicitly not among the restamped rows. Empty set is intentional design.

## Step 3 — Cross-directive selective-citation check (all 28 active directives)

`active_directives()` = 28 (D-001…D-020, D-023…D-030). Ran the same independent matcher over all 3021 requirements:
- 0 full matches to M0-T108; 0 wildcard; 0 malformed.
- **28 requirements have `paths` intersecting M0-T108's files** (`.claude/settings.json`, `.claude/hooks/readonly_agent_guard.py`) — the exact selective-citation risk. Every one is excluded by a non-empty `task_ids` naming other tasks, never M0-T108:
  - D-004 ×26 (R080, R081, R089, R094, R096, R100, R124, R142, R159, R165, R175, R199, R200, R214, R222, R240, R242, R243, R244, R245, R249, R254, R255, R277, R754, R759) → task_ids ∈ {M0-T027, M0-T028, M0-T029, M0-T034, D-004-PHASE0, D-004-PROCESS} — all `EXCLUDED_BY ['task_ids-excludes']`.
  - D-007 ×2 (R608, R610) → task_ids {D-007-BUILD, M0-T036} — `EXCLUDED_BY ['task_ids-excludes']`.
  These bound the guard/settings obligations to the tasks that originally built them, not to every future task touching those files. Nothing for M0-T108 to cite beyond D-024; `D-024:ALL` covers the (empty) applicable set with no missing_ids.

## Supporting integrity/harness runs

| Check | Result |
|---|---|
| `python tools/validate_directive_compliance.py --check` (both SHAs) | **EXIT=0** |
| `python tools/test_project_control.py` | **EXIT=0** — all 23 groups passed |
| `python tools/test_directive_reminder.py` | **EXIT=0** — 12 tests OK |
| `python tools/test_directive_compliance.py` | Not completed in sandbox time budget (>20 min, un-flushed); no failure observed; not load-bearing for the empty-set verdict. |

## Requirement-level disposition

The D-024 applicable requirement set for M0-T108 is **∅** (empty), proven three ways. No in-scope requirement IDs to mark SATISFIED/VIOLATED/BLOCKED/UNVERIFIABLE. Selective-citation obligation clean. No VIOLATED and no UNVERIFIABLE findings. Nothing merged/accepted/dispatched observed (M0-T108 remains `awaiting_gate`; no writes; git/gh/control-plane untouched).

## `DCV: PASS`
