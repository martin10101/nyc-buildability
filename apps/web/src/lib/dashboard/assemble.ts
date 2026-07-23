// Pure assembler: RawControlPlane (+ supplemental GitHubStatus) -> DashboardModel.
// This is the single entry the server loader and the tests call. PURE and
// framework-independent (owner directive #10): no React/Next/fs/network here.

import type {
  RawControlPlane, DashboardModel, GitHubStatus, SystemModel, Task,
  OwnerStatus, DataQuality, Issue,
} from './types';
import { parseProductMap } from './parse';
import { buildProjectModel } from './model';
import { computeProgress } from './progress';
import { systemHealth, overallHealth } from './health';
import { computeCurrentWork } from './currentWork';
import { computeActivity } from './activity';
import { computeLaunchBlockers } from './launch';

const NO_GITHUB: GitHubStatus = { available: false, stale: false };

function ownerStatusSummary(tasks: Task[]): OwnerStatus {
  if (tasks.length === 0) return 'PLANNED';
  const has = (s: string) => tasks.some((t) => t.status === s);
  if (has('blocked')) return 'BLOCKED';
  if (tasks.every((t) => t.accepted)) return 'ACCEPTED';
  if (has('awaiting_gate')) return 'REVIEW';
  if (has('claimed') || has('in_progress') || has('rework')) return 'ACTIVE';
  if (has('self_check')) return 'TESTING';
  if (has('ready')) return 'READY';
  if (tasks.some((t) => t.accepted)) return 'ACTIVE'; // partial acceptance, more to do
  return 'PLANNED';
}

export function assembleDashboard(
  raw: RawControlPlane,
  github: GitHubStatus = NO_GITHUB,
  nowIso: string,
): DashboardModel {
  const issues: Issue[] = [...(raw.fileIssues ?? [])];
  const pm = parseProductMap(raw.productMap);
  issues.push(...pm.issues);

  const model = buildProjectModel(
    raw.tasks, raw.gates, raw.blockers, raw.checkpoints, raw.masterPlan, raw.state, pm,
  );
  issues.push(...model.issues);

  const progress = computeProgress(pm.systems, model.tasksBySystem, model.taskById);

  const ciFailingAffectsActive = github.ci?.conclusion === 'failure';

  // ---- systems (completion from files; health from live signals, separately) ----
  const systems: SystemModel[] = pm.systems.map((s) => {
    const memberIds = model.tasksBySystem.get(s.id) ?? [];
    const memberTasks = memberIds
      .map((id) => model.taskById.get(id))
      .filter((t): t is Task => !!t);
    const ps = progress.perSystem.get(s.id)!;
    const hasActive = memberTasks.some((t) =>
      ['claimed', 'in_progress', 'self_check', 'awaiting_gate', 'rework'].includes(t.status));

    const sys: SystemModel = {
      id: s.id,
      name: s.name,
      ownerPurpose: s.ownerPurpose,
      ownerWhy: s.ownerWhy,
      engWeight: s.engWeight,
      launchWeight: s.launchWeight,
      plannedCount: s.plannedCount,
      criticalForBeta: s.criticalForBeta,
      journeySteps: s.journeySteps,
      dependsOn: s.dependsOn,
      tasks: memberTasks,
      contractedCount: ps.contractedCount,
      acceptedCount: ps.acceptedCount,
      expectedCount: ps.expectedCount,
      engCompletion: ps.engCompletion,
      launchReadiness: ps.launchReadiness,
      ownerStatusSummary: ownerStatusSummary(memberTasks),
      health: 'GREEN',
      healthReasons: [],
      dataQuality: ps.dataQuality,
    };
    const h = systemHealth(
      { id: s.id, criticalForBeta: s.criticalForBeta, dataQuality: ps.dataQuality,
        tasks: memberTasks, hasActive },
      model.openBlockers, github, ciFailingAffectsActive,
    );
    sys.health = h.health;
    sys.healthReasons = h.reasons;
    return sys;
  });

  const health = overallHealth(systems, github, issues);
  const currentWork = computeCurrentWork(model.tasks, model.taskById, model.project.currentMilestone);
  const activity = computeActivity(
    raw.tasks, raw.gates, raw.blockers, raw.checkpoints, model.taskById, nowIso,
  );
  const launchBlockers = computeLaunchBlockers(systems, model.openBlockers);

  // ---- overall data quality (never coerce unknown to ok) ----
  let dataQuality: DataQuality;
  if (pm.systems.length === 0 || model.tasks.length === 0) {
    dataQuality = 'unknown';
  } else if (progress.engineering.dataQuality === 'unknown' && progress.launch.dataQuality === 'unknown') {
    dataQuality = 'unknown';
  } else if (
    issues.some((i) => i.severity === 'error') ||
    progress.engineering.dataQuality !== 'ok' ||
    progress.launch.dataQuality !== 'ok'
  ) {
    dataQuality = 'partial';
  } else {
    dataQuality = 'ok';
  }

  return {
    generatedAtIso: nowIso,
    dataQuality,
    issues,
    project: model.project,
    engineering: progress.engineering,
    launch: progress.launch,
    systems,
    milestones: model.milestones,
    tasks: model.tasks,
    currentWork,
    activity,
    openBlockers: model.openBlockers,
    launchBlockers,
    health,
    github,
    ledgerCounts: model.ledgerCounts,
  };
}
