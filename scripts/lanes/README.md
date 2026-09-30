# scripts/lanes — parallel-build lane tooling (task M0-T164, D-090)

| File | What it does |
|---|---|
| `check_lane_paths.py` | `--coverage`: every tracked file has exactly one owning lane in `docs/lanes/OWNERSHIP.yaml` (first matching rule wins; no match = orphan = fail). Default: on a `lane-<x>/…` branch, every changed file must be owned by lane x; other branches are skipped. Exit 0 pass, 1 violation, 2 error (fail closed). |
| `test_check_lane_paths.py` | Stdlib unittest suite for both scripts (`python3 scripts/lanes/test_check_lane_paths.py`). |
| `setup_worktrees.sh` | Creates `../nyc-lane-a` … `../nyc-lane-e` detached at the integration branch tip and writes each one's git-ignored `.env.local` (API 8101–8105, web 3101–3105). Never pushes; leaves existing worktrees untouched. |

Local use before a PR (from a lane worktree):

```
python3 scripts/lanes/check_lane_paths.py              # diff vs merge-base with origin/<integration branch>
python3 scripts/lanes/check_lane_paths.py --coverage
```

CI runs both in the `control-plane` job; on pull requests it diffs the PR's base SHA against
GitHub's merge commit.
