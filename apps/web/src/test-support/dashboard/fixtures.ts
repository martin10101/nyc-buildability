// Deterministic synthetic fixtures for the dashboard engine tests.
// Small enough to hand-compute; exercises accepted / awaiting_gate / blocked /
// backlog / unknown statuses, independent-gate rules, a readiness cap, blockers,
// dependencies, and GitHub CI. Hand-computed expectations live in the tests.

import type { RawControlPlane } from '@/lib/dashboard/types';

export const NOW_ISO = '2026-07-23T12:00:00+00:00';

export const synthProductMapRaw = {
  version: 1,
  progress_model: { engineering_completion: 'x', launch_readiness: 'y' },
  owner_status_vocabulary: {
    backlog: 'PLANNED', ready: 'READY', claimed: 'ACTIVE', in_progress: 'ACTIVE',
    self_check: 'TESTING', awaiting_gate: 'REVIEW', rework: 'ACTIVE',
    accepted: 'ACCEPTED', blocked: 'BLOCKED', canceled: 'CANCELED',
  },
  repo: { github: 'acme/demo', default_branch: 'main', public: true },
  systems: [
    {
      id: 'sys_a', name: 'System A', owner_purpose: 'p', owner_why: 'w',
      eng_weight: 50, launch_weight: 50, planned_count: 2, milestones: ['M0'],
      critical_for_beta: true, journey_steps: [1],
    },
    {
      id: 'sys_b', name: 'System B', owner_purpose: 'p', owner_why: 'w',
      eng_weight: 50, launch_weight: 50, planned_count: 2, milestones: ['M1'],
      critical_for_beta: true, journey_steps: [2],
      readiness_cap: { until_gate_passes: 'G6', on_task: 'M1-T001', max_readiness_fraction: 0.15, reason: 'legal sign-off' },
    },
  ],
  architect_journey: [
    { step: 1, label: 'Step one', systems: ['sys_a'] },
    { step: 2, label: 'Step two', systems: ['sys_b'] },
  ],
  task_overrides: {
    'M0-T001': { owner_title: 'Foundation piece', owner_description: 'Plain-English.' },
  },
  blocker_labels: { 'B-900': 'Owner must supply a demo credential.' },
};

export const synthMasterPlan = {
  project: 'Demo',
  current_milestone: 'M0',
  milestones: [
    { id: 'M0', name: 'Milestone 0', status: 'active', depends_on: [] },
    { id: 'M1', name: 'Milestone 1', status: 'active', depends_on: ['M0'] },
  ],
};

export const synthState = {
  project_status: 'active',
  current_milestone: 'M0',
  last_checkpoint: 'CP-0001',
  accepted_tasks: ['M0-T001', 'M1-T001'],
};

export const synthTasks = [
  {
    task_id: 'M0-T001', milestone_id: 'M0', title: 'A1', status: 'accepted',
    progress_percent: 100, required_gates: ['G3'], dependencies: [],
    producer_agent: 'backend-engineer', accepted_at: '2026-07-23T10:00:00+00:00',
    business_reason: 'because',
  },
  {
    task_id: 'M0-T002', milestone_id: 'M0', title: 'A2', status: 'awaiting_gate',
    progress_percent: 90, required_gates: ['G3'], dependencies: [],
    producer_agent: 'backend-engineer',
    progress_log: [{ at: '2026-07-23T09:00:00+00:00', agent: 'x', percent: 10, status: 'claimed', message: 'start' }],
  },
  {
    task_id: 'M1-T001', milestone_id: 'M1', title: 'B1', status: 'accepted',
    progress_percent: 100, required_gates: ['G6'], dependencies: [],
    producer_agent: 'rules-engineer', accepted_at: '2026-07-20T10:00:00+00:00',
    reconciliation: { merged_pr: 42, reconciled_at: '2026-07-20T09:00:00+00:00', acceptance_status: 'draft only' },
  },
  {
    task_id: 'M1-T002', milestone_id: 'M1', title: 'B2', status: 'blocked',
    progress_percent: 0, required_gates: ['G3'], dependencies: ['M1-T001'],
    producer_agent: 'rules-engineer',
  },
];

export const synthGates = [
  { task_id: 'M0-T001', gate_id: 'G3', reviewer: 'code-reviewer', role: 'independent_review', result: 'PASS', reviewed_at: '2026-07-22T10:00:00+00:00' },
  // M0-T002 G3 PASS, independent
  { task_id: 'M0-T002', gate_id: 'G3', reviewer: 'code-reviewer', role: 'independent_review', result: 'PASS', reviewed_at: '2026-07-23T11:00:00+00:00' },
];

export const synthBlockers = [
  { blocker_id: 'B-900', status: 'open', affects: ['M1-T002'], detail: 'blocks M1-T002', created_at: '2026-07-21T10:00:00+00:00' },
  { blocker_id: 'B-901', status: 'resolved', affects: ['M0-T001'], detail: 'was blocking', created_at: '2026-07-10T10:00:00+00:00', audit_log: [{ at: '2026-07-12T10:00:00+00:00', by: 'owner', note: 'resolved: credential supplied' }] },
];

export const synthCheckpoints = [
  { checkpoint_id: 'CP-0001', timestamp: '2026-07-19T10:00:00+00:00', commit: 'abc1234', branch: 'main', active_milestone: 'M0', summary: 'first checkpoint' },
];

export function synthRaw(overrides: Partial<RawControlPlane> = {}): RawControlPlane {
  return {
    tasks: synthTasks,
    masterPlan: synthMasterPlan,
    state: synthState,
    config: {},
    gates: synthGates,
    blockers: synthBlockers,
    checkpoints: synthCheckpoints,
    productMap: synthProductMapRaw,
    ...overrides,
  };
}

// ---- GitHub API fixtures ----
export const ghCommitMain = { sha: 'deadbeefcafef00d1234567890abcdef12345678' };
export const ghPullsOpen = [
  { number: 84, title: 'Open PR', merged_at: null, html_url: 'https://x/84' },
];
export const ghPullsClosed = [
  { number: 82, title: 'Merged PR', merged_at: '2026-07-22T10:00:00Z', html_url: 'https://x/82' },
  { number: 80, title: 'Closed unmerged', merged_at: null, html_url: 'https://x/80' },
];
export const ghRunsSuccess = {
  workflow_runs: [
    { name: 'CI', head_sha: 'deadbeefcafef00d1234567890abcdef12345678', status: 'completed', conclusion: 'success' },
    { name: 'secret-scan', head_sha: 'deadbeefcafef00d1234567890abcdef12345678', status: 'completed', conclusion: 'success' },
  ],
};
export const ghRunsFailure = {
  workflow_runs: [
    { name: 'CI', head_sha: 'deadbeefcafef00d1234567890abcdef12345678', status: 'completed', conclusion: 'failure' },
    { name: 'secret-scan', head_sha: 'deadbeefcafef00d1234567890abcdef12345678', status: 'completed', conclusion: 'success' },
  ],
};
