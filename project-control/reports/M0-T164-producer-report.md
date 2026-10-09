# M0-T164 producer report — lane guardrails (orchestrator producer)

## Files
| Path | Change |
|---|---|
| `docs/lanes/OWNERSHIP.yaml` | Replaces the contract-seam placeholder: lanes A–E (name, flag, ports), informational hot-file list, 12 ordered first-match rules covering the whole tree |
| `scripts/lanes/check_lane_paths.py` | New, stdlib: YAML-subset reader, glob matcher (`*` one segment, `**` any), `--coverage`, lane-branch check (merge-base diff locally; `--base-sha` tree diff vs GitHub's merge commit in CI) |
| `scripts/lanes/test_check_lane_paths.py` | New, 24 stdlib unittest cases (parser, globs, 31 representative owners, real-tree coverage, hot files -> C, fail-closed on malformed map, branch pass/fail cases, merge-base and base-sha diffs in throwaway repos, worktree script) |
| `scripts/lanes/setup_worktrees.sh` | New: five detached worktrees + git-ignored `.env.local` ports; no push (tested) |
| `scripts/lanes/README.md` | Replaces the placeholder |
| `services/api/app/config.py` | Additive: `LANE_FLAG_ENV_VARS` (LANE_A..E_ENABLED) + `lane_enabled(lane, env=None)`, same fail-safe reader as the existing flags; read nowhere yet |
| `services/api/tests/test_lane_flags.py` | New pytest: names, absent/false/unknown -> off, true tokens -> on, independence, unknown lane raises, process env default off |
| `.github/workflows/ci.yml` | ONE additive step at the end of `control-plane`; existing steps untouched |

## Self-checks (run here)
- `python3 scripts/lanes/test_check_lane_paths.py` -> `Ran 24 tests … OK`
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> `LANE COVERAGE PASS: 7601 file(s), each owned by exactly one lane.`
- Lane-flag logic exercised directly with python3 (absent/unknown off, " yes " on, unknown lane raises).
- Line lengths <= 100 in every new/changed Python file (ruff E501).
- NOT run here: `ruff` and `pytest` for services/api (this sandbox has no pip/ensurepip); CI's `api` job is the proof.

## Deviation noted
- Subagents in this session run on the session model; the repo's named agent roster is not loaded in
  this cloud session, so no `model:` was passed and no named agent was dispatched.
