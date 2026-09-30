#!/usr/bin/env bash
# Create the five lane worktrees ../nyc-lane-a .. ../nyc-lane-e (task M0-T164, D-090).
#
# Local only: fetches the integration branch and adds detached worktrees at its tip. It never
# pushes, never deletes, and leaves an existing worktree directory untouched. Each worktree gets
# a git-ignored .env.local with the lane's ports (docs/lanes/OWNERSHIP.yaml: API 8101-8105,
# web 3101-3105). Lanes then work on lane-<x>/<task-id> branches (docs/lanes/PARALLEL_BUILD_PLAN.md).
#
# Usage: scripts/lanes/setup_worktrees.sh [integration-branch]
set -euo pipefail

base_branch="${1:-candidate/D-024-mrl-option-b}"
root="$(git rev-parse --show-toplevel)"
parent="$(dirname "$root")"

git -C "$root" fetch --no-tags origin "$base_branch"
start="$(git -C "$root" rev-parse FETCH_HEAD)"

n=1
for lane in a b c d e; do
  upper="$(printf '%s' "$lane" | tr 'a-e' 'A-E')"
  dir="$parent/nyc-lane-$lane"
  if [ -e "$dir" ]; then
    echo "lane $upper: $dir exists - left untouched"
  else
    git -C "$root" worktree add --quiet --detach "$dir" "$start"
    echo "lane $upper: created $dir at ${start:0:12} (detached; branch lane-$lane/<task-id>)"
  fi
  if [ ! -e "$dir/.env.local" ]; then
    cat > "$dir/.env.local" <<ENV
# Lane $upper - written by scripts/lanes/setup_worktrees.sh (git-ignored).
LANE=$upper
LANE_${upper}_ENABLED=true
API_PORT=810$n
WEB_PORT=310$n
ENV
    mkdir -p "$dir/apps/web"
    if [ ! -e "$dir/apps/web/.env.local" ]; then
      printf 'NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:810%s\n' "$n" > "$dir/apps/web/.env.local"
    fi
    echo "lane $upper: wrote .env.local (API 810$n, web 310$n)"
  fi
  n=$((n + 1))
done
