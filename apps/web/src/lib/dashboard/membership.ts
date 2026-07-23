// Resolve which product system each ledger task belongs to.
// MUST mirror tools/validate_product_map.py resolve_membership() exactly so the
// dashboard and the CI integrity gate agree:
//
//   membership(system) = ({tasks whose milestone_id is in system.milestones}
//                         - system.tasks_exclude) | system.tasks_include
//
// The CI product-map job guarantees every ledger task maps to exactly one system.
// At runtime we still defend: a task mapping to 0 or >1 systems yields an Issue
// and a deterministic assignment (none / first-by-declaration), never a silent drop.

import type { Issue } from './types';
import type { ParsedProductMapSystem } from './parse';

export interface MembershipResult {
  /** taskId -> systemId (undefined when unmapped). */
  systemByTask: Map<string, string | undefined>;
  /** systemId -> ordered task ids. */
  tasksBySystem: Map<string, string[]>;
  issues: Issue[];
}

export function resolveMembership(
  systems: ParsedProductMapSystem[],
  taskMilestones: Map<string, string>,
): MembershipResult {
  const issues: Issue[] = [];
  const allTasks = [...taskMilestones.keys()];

  // Compute each system's raw membership set.
  const membership = new Map<string, Set<string>>();
  for (const s of systems) {
    const ms = new Set(s.milestones);
    const include = new Set(s.tasksInclude);
    const exclude = new Set(s.tasksExclude);
    const set = new Set<string>();
    for (const [tid, mid] of taskMilestones) {
      if (ms.has(mid) && !exclude.has(tid)) set.add(tid);
    }
    for (const tid of include) set.add(tid);
    membership.set(s.id, set);
  }

  // Assign each task to exactly one system; flag anomalies deterministically.
  const systemByTask = new Map<string, string | undefined>();
  for (const tid of allTasks) {
    const owners = systems.filter((s) => membership.get(s.id)!.has(tid)).map((s) => s.id);
    if (owners.length === 1) {
      systemByTask.set(tid, owners[0]);
    } else if (owners.length === 0) {
      systemByTask.set(tid, undefined);
      issues.push({
        code: 'membership.orphan',
        message: `Task ${tid} maps to no product system.`,
        severity: 'error',
        ref: tid,
      });
    } else {
      // >1: assign to the first by declaration order (deterministic), flag it.
      systemByTask.set(tid, owners[0]);
      issues.push({
        code: 'membership.duplicate',
        message: `Task ${tid} maps to multiple systems (${owners.join(', ')}); using ${owners[0]}.`,
        severity: 'error',
        ref: tid,
      });
    }
  }

  const tasksBySystem = new Map<string, string[]>();
  for (const s of systems) tasksBySystem.set(s.id, []);
  for (const tid of allTasks.slice().sort()) {
    const sid = systemByTask.get(tid);
    if (sid) tasksBySystem.get(sid)!.push(tid);
  }

  return { systemByTask, tasksBySystem, issues };
}
