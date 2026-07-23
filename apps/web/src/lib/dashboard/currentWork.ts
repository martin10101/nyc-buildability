// Current Work + Next (owner directive #5): derived from AUTHORITATIVE lifecycle
// state, never from latest-commit heuristics. Shows all active tasks and picks a
// deterministic critical-path/primary. PURE.

import type { Task, CurrentWork } from './types';
import { ACTIVE_STATUSES } from './parse';

// How close a status is to done (higher = further along). Deterministic.
const LIFECYCLE_ADVANCEMENT: Record<string, number> = {
  awaiting_gate: 5,
  self_check: 4,
  in_progress: 3,
  rework: 2,
  claimed: 1,
};

export function computeCurrentWork(
  tasks: Task[],
  taskById: Map<string, Task>,
  currentMilestone: string,
): CurrentWork {
  const activeTasks = tasks
    .filter((t) => ACTIVE_STATUSES.has(t.status))
    .sort((a, b) => a.id.localeCompare(b.id));

  // Primary = the active task nearest to completion within the current milestone;
  // fall back across milestones. Fully deterministic tie-breaking.
  const primary = [...activeTasks].sort((a, b) => {
    const am = a.milestoneId === currentMilestone ? 1 : 0;
    const bm = b.milestoneId === currentMilestone ? 1 : 0;
    if (am !== bm) return bm - am;
    const aa = LIFECYCLE_ADVANCEMENT[a.status] ?? 0;
    const ba = LIFECYCLE_ADVANCEMENT[b.status] ?? 0;
    if (aa !== ba) return ba - aa;
    if (a.progressPercent !== b.progressPercent) return b.progressPercent - a.progressPercent;
    return a.id.localeCompare(b.id);
  })[0];

  // Next = tasks not started (ready/backlog) whose dependencies are all accepted.
  const next = tasks
    .filter((t) => (t.status === 'ready' || t.status === 'backlog'))
    .filter((t) => t.dependencies.every((d) => taskById.get(d)?.accepted))
    .sort((a, b) => {
      const am = a.milestoneId === currentMilestone ? 1 : 0;
      const bm = b.milestoneId === currentMilestone ? 1 : 0;
      if (am !== bm) return bm - am;
      return a.id.localeCompare(b.id);
    })
    .slice(0, 5);

  return { activeTasks, primary, next };
}
