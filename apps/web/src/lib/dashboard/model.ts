// Build the canonical project model from parsed control-plane data.
// PURE. project-control files are the ONLY authority for project state
// (owner directive #9). Reproduces the control CLI's status/gate/acceptance
// semantics read-only; it never mutates anything.

import type {
  Task, Blocker, MilestoneModel, Issue, GateStateEntry,
} from './types';
import {
  isRecord, asString, asFiniteNumber, asStringArray,
  coerceStatus, ownerStatusFor, parseGateRecord, INDEPENDENT_GATES,
  type ParsedProductMap,
} from './parse';
import { resolveMembership } from './membership';

export interface ProjectModel {
  tasks: Task[];
  taskById: Map<string, Task>;
  milestones: MilestoneModel[];
  blockers: Blocker[];
  openBlockers: Blocker[];
  ledgerCounts: Record<string, number>;
  project: { name: string; currentMilestone: string; latestCheckpoint?: string; repo?: string };
  tasksBySystem: Map<string, string[]>;
  issues: Issue[];
}

/** Mirror of project_control.py _blocker_references: word-bounded id match in affects/detail. */
export function blockerReferencesTask(taskId: string, affects: string[], detail: string): boolean {
  const hay = [...affects, detail].join('\n');
  // (?<![A-Za-z0-9])ID(?!\d)  — base id also matches its -R# rework mentions.
  const re = new RegExp(`(?<![A-Za-z0-9])${taskId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?!\\d)`);
  return re.test(hay);
}

function parseBlocker(raw: unknown): Blocker | null {
  if (!isRecord(raw)) return null;
  const id = asString(raw.blocker_id);
  if (!id) return null;
  const status = (asString(raw.status) ?? '').toLowerCase();
  const affects = asStringArray(raw.affects);
  const sinceIso = asString(raw.created_at);
  return {
    id,
    title: asString(raw.title) ?? id,
    status,
    open: status === 'open' || status === '',
    affects,
    detail: asString(raw.detail),
    sinceIso,
    affectedTaskIds: [],
    affectedSystemIds: [],
  };
}

export function buildProjectModel(
  rawTasks: unknown[],
  rawGates: unknown[],
  rawBlockers: unknown[],
  rawCheckpoints: unknown[],
  rawMasterPlan: unknown,
  rawState: unknown,
  productMap: ParsedProductMap,
): ProjectModel {
  const issues: Issue[] = [];

  // ---- gates grouped by task ----
  const gatesByTask = new Map<string, GateStateEntry[]>();
  for (const g of rawGates) {
    const rec = parseGateRecord(g);
    if (!rec) continue;
    const tid = isRecord(g) ? asString(g.task_id) : undefined;
    if (!tid) continue;
    const arr = gatesByTask.get(tid) ?? [];
    arr.push(rec);
    gatesByTask.set(tid, arr);
  }

  // ---- task -> milestone map (for membership) ----
  const taskMilestones = new Map<string, string>();
  const rawTaskById = new Map<string, Record<string, unknown>>();
  for (const t of rawTasks) {
    if (!isRecord(t)) continue;
    const id = asString(t.task_id);
    if (!id) continue;
    const mid = asString(t.milestone_id) ?? (id.includes('-') ? id.split('-')[0] : '');
    taskMilestones.set(id, mid);
    rawTaskById.set(id, t);
  }

  const membership = resolveMembership(productMap.systems, taskMilestones);
  issues.push(...membership.issues);

  // ---- blockers ----
  const blockers: Blocker[] = [];
  for (const b of rawBlockers) {
    const parsed = parseBlocker(b);
    if (parsed) blockers.push(parsed);
  }
  const openBlockers = blockers.filter((b) => b.open);

  // ---- state.json accepted roster (for contradiction detection) ----
  const acceptedRoster = new Set<string>(
    isRecord(rawState) ? asStringArray(rawState.accepted_tasks) : [],
  );

  // ---- build tasks ----
  const tasks: Task[] = [];
  for (const [id, raw] of rawTaskById) {
    const { status, issue: statusIssue } = coerceStatus(raw.status);
    const taskIssues: Issue[] = [];
    if (statusIssue) { taskIssues.push({ ...statusIssue, ref: id }); }

    const milestoneId = taskMilestones.get(id) ?? '';
    const progressPercent = Math.max(0, Math.min(100, asFiniteNumber(raw.progress_percent) ?? 0));
    const dependencies = asStringArray(raw.dependencies);
    const requiredGates = asStringArray(raw.required_gates);
    const producer = asString(raw.producer_agent) ?? undefined;
    const gates = gatesByTask.get(id) ?? [];

    // per-task gate state: a required gate counts as PASS only if a record exists
    // with result PASS AND (for independent gates) an independent role + reviewer!=producer.
    const passedGates: string[] = [];
    for (const gid of requiredGates) {
      const rec = gates.find((g) => g.gateId === gid && g.result === 'PASS');
      if (!rec) continue;
      if (INDEPENDENT_GATES.has(gid)) {
        const independent = rec.role !== 'self_check' && rec.reviewer !== 'orchestrator'
          && (!producer || rec.reviewer !== producer);
        if (independent) passedGates.push(gid);
      } else {
        passedGates.push(gid);
      }
    }
    const unmetGates = requiredGates.filter((g) => !passedGates.includes(g));

    const accepted = status === 'accepted';

    // acceptance-eligibility (reproduces accept(); does NOT itself accept).
    const acceptanceBlockers: string[] = [];
    if (status !== 'awaiting_gate' && !accepted) {
      acceptanceBlockers.push(`status is ${status}, not awaiting_gate`);
    }
    for (const g of unmetGates) acceptanceBlockers.push(`gate ${g} not PASS`);
    for (const dep of dependencies) {
      const depRaw = rawTaskById.get(dep);
      const depStatus = depRaw ? asString(depRaw.status) : undefined;
      if (depStatus !== 'accepted') acceptanceBlockers.push(`dependency ${dep} not accepted`);
    }
    for (const b of openBlockers) {
      if (blockerReferencesTask(id, b.affects, b.detail ?? '')) {
        acceptanceBlockers.push(`open blocker ${b.id}`);
      }
    }
    const acceptanceEligible = acceptanceBlockers.length === 0 && !accepted;

    // control-plane contradiction (owner directive #8): roster says accepted but
    // the task file disagrees (or vice versa). Surface, never silently trust.
    if (acceptedRoster.has(id) && status !== 'accepted') {
      taskIssues.push({
        code: 'roster.contradiction',
        message: `state.json lists ${id} as accepted but its task file status is '${status}'.`,
        severity: 'error',
        ref: id,
      });
    }
    if (!acceptedRoster.has(id) && status === 'accepted') {
      taskIssues.push({
        code: 'roster.contradiction',
        message: `${id} status is 'accepted' but it is absent from state.json accepted_tasks.`,
        severity: 'warn',
        ref: id,
      });
    }

    // reconciliation honesty note
    let reconciliationNote: string | undefined;
    if (isRecord(raw.reconciliation)) {
      reconciliationNote = asString(raw.reconciliation.acceptance_status)
        ?? asString(raw.reconciliation.note);
    }

    // PR number: reconciliation.merged_pr is the reliable structured source.
    let prNumber: number | undefined;
    if (isRecord(raw.reconciliation)) prNumber = asFiniteNumber(raw.reconciliation.merged_pr);

    const override = productMap.taskOverrides[id];
    const systemId = membership.systemByTask.get(id);

    tasks.push({
      id,
      milestoneId,
      title: asString(raw.title) ?? id,
      ownerTitle: override?.ownerTitle,
      ownerDescription: override?.ownerDescription,
      businessReason: asString(raw.business_reason),
      status,
      ownerStatus: ownerStatusFor(status, productMap.ownerStatusVocabulary),
      progressPercent,
      dependencies,
      requiredGates,
      gates,
      passedGates,
      unmetGates,
      acceptanceEligible,
      acceptanceBlockers,
      accepted,
      branch: asString(raw.branch) && raw.branch !== '-' ? asString(raw.branch) : undefined,
      prNumber,
      systemId,
      reconciliationNote,
      issues: taskIssues,
    });
  }
  tasks.sort((a, b) => a.id.localeCompare(b.id));
  const taskById = new Map(tasks.map((t) => [t.id, t]));
  for (const t of tasks) issues.push(...t.issues);

  // ---- link blockers to tasks/systems ----
  for (const b of blockers) {
    const affectedTaskIds = tasks
      .filter((t) => blockerReferencesTask(t.id, b.affects, b.detail ?? ''))
      .map((t) => t.id);
    b.affectedTaskIds = affectedTaskIds;
    b.affectedSystemIds = [
      ...new Set(affectedTaskIds.map((tid) => taskById.get(tid)?.systemId).filter((x): x is string => !!x)),
    ];
    b.ownerLabel = productMap.blockerLabels[b.id];
  }

  // ---- milestones from master_plan + counts ----
  const milestones: MilestoneModel[] = [];
  const mpMilestones = isRecord(rawMasterPlan) && Array.isArray(rawMasterPlan.milestones)
    ? rawMasterPlan.milestones : [];
  for (const m of mpMilestones) {
    if (!isRecord(m)) continue;
    const id = asString(m.id);
    if (!id) continue;
    const inMs = tasks.filter((t) => t.milestoneId === id);
    milestones.push({
      id,
      name: asString(m.name) ?? id,
      status: asString(m.status) ?? 'unknown',
      dependsOn: asStringArray(m.depends_on),
      acceptedCount: inMs.filter((t) => t.accepted).length,
      contractedCount: inMs.length,
      summary: asString(m.summary),
    });
  }

  // ---- ledger counts ----
  const ledgerCounts: Record<string, number> = {};
  for (const t of tasks) ledgerCounts[t.status] = (ledgerCounts[t.status] ?? 0) + 1;

  // ---- project meta ----
  const currentMilestone =
    (isRecord(rawState) ? asString(rawState.current_milestone) : undefined)
    ?? (isRecord(rawMasterPlan) ? asString(rawMasterPlan.current_milestone) : undefined)
    ?? 'unknown';
  const projectName = isRecord(rawMasterPlan) ? (asString(rawMasterPlan.project) ?? 'Project') : 'Project';

  // latest checkpoint by id sort
  let latestCheckpoint: string | undefined;
  const cps = rawCheckpoints
    .map((c) => (isRecord(c) ? asString(c.checkpoint_id) : undefined))
    .filter((x): x is string => !!x)
    .sort();
  if (cps.length) latestCheckpoint = cps[cps.length - 1];
  else if (isRecord(rawState)) latestCheckpoint = asString(rawState.last_checkpoint);

  const repo = productMap.repo?.github;

  return {
    tasks,
    taskById,
    milestones,
    blockers,
    openBlockers,
    ledgerCounts,
    project: { name: projectName, currentMilestone, latestCheckpoint, repo },
    tasksBySystem: membership.tasksBySystem,
    issues,
  };
}
