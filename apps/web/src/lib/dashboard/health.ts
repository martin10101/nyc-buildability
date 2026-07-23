// Health computation (owner directive #3): HEALTH is independent of completion.
// A system is not "healthy" merely because its tasks are accepted; live signals
// (blocked tasks, open blockers, failed CI, stale GitHub, control-plane
// inconsistencies) degrade health WITHOUT changing historical completion.
// PURE.

import type {
  Task, Blocker, Health, GitHubStatus, Issue, SystemModel, OverallHealth,
} from './types';

const RANK: Record<Health, number> = { GREEN: 0, YELLOW: 1, RED: 2, UNKNOWN: 3 };

function worse(a: Health, b: Health): Health {
  // UNKNOWN is surfaced but should not mask a RED; RED is the most urgent.
  if (a === 'RED' || b === 'RED') return 'RED';
  return RANK[a] >= RANK[b] ? a : b;
}

export interface SystemHealthInput {
  id: string;
  criticalForBeta: boolean;
  dataQuality: SystemModel['dataQuality'];
  tasks: Task[];
  hasActive: boolean;
}

export function systemHealth(
  s: SystemHealthInput,
  openBlockers: Blocker[],
  github: GitHubStatus,
  ciFailingAffectsActive: boolean,
): { health: Health; reasons: string[] } {
  const reasons: string[] = [];
  let health: Health = 'GREEN';

  if (s.dataQuality === 'unknown') {
    reasons.push('Some control-plane data for this system could not be verified.');
    health = worse(health, 'UNKNOWN');
  }

  // control-plane inconsistency on a member task (e.g. roster contradiction)
  const inconsistent = s.tasks.some((t) => t.issues.some((i) => i.severity === 'error'));
  if (inconsistent) {
    reasons.push('A control-plane inconsistency was detected in this system.');
    health = worse(health, 'RED');
  }

  // blocked member task
  if (s.tasks.some((t) => t.status === 'blocked')) {
    reasons.push('A task in this system is blocked.');
    health = worse(health, 'RED');
  }

  // open blocker referencing this system
  const relatedBlockers = openBlockers.filter((b) => b.affectedSystemIds.includes(s.id));
  if (relatedBlockers.length) {
    reasons.push(`Open blocker(s): ${relatedBlockers.map((b) => b.id).join(', ')}.`);
    health = worse(health, 'RED');
  }

  // failed CI, while this system has active work
  if (ciFailingAffectsActive && s.hasActive) {
    reasons.push('CI is failing while this system has active work.');
    health = worse(health, 'RED');
  }

  // in-review work => YELLOW (waiting, not failing)
  if (health === 'GREEN' && s.tasks.some((t) => t.status === 'awaiting_gate')) {
    reasons.push('Work in this system is awaiting independent review.');
    health = 'YELLOW';
  }

  // stale GitHub is a live-ops caveat, not a project-state failure
  if (health === 'GREEN' && github.stale && s.hasActive) {
    reasons.push('Live GitHub status is stale.');
    health = 'YELLOW';
  }

  if (health === 'GREEN') reasons.push('No problems detected.');
  return { health, reasons };
}

export function overallHealth(
  systems: SystemModel[],
  github: GitHubStatus,
  issues: Issue[],
): OverallHealth {
  const reasons: string[] = [];
  let overall: Health = 'GREEN';

  for (const s of systems) {
    overall = worse(overall, s.health);
  }

  if (github.ci?.conclusion === 'failure') {
    overall = worse(overall, 'RED');
    reasons.push('CI is failing on main.');
  }
  const errorIssues = issues.filter((i) => i.severity === 'error');
  if (errorIssues.length) {
    overall = worse(overall, 'RED');
    reasons.push(`${errorIssues.length} control-plane inconsistency/inconsistencies detected.`);
  }
  if (github.stale) {
    if (overall === 'GREEN') overall = 'YELLOW';
    reasons.push('Live GitHub data is stale (project state is unaffected; only live CI/PR view).');
  }
  if (!github.available && !github.stale) {
    if (overall === 'GREEN') overall = 'YELLOW';
    reasons.push('Live GitHub status is unavailable.');
  }

  const redCount = systems.filter((s) => s.health === 'RED').length;
  if (redCount) reasons.push(`${redCount} system(s) need attention.`);
  if (overall === 'GREEN') reasons.push('All systems healthy; CI green.');

  return { overall, reasons };
}
