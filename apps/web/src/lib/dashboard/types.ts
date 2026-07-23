// Owner Mission-Control dashboard (M0-T022) — engine types.
//
// This module is PURE and framework-independent: no React, Next, fs, or network
// imports anywhere in the engine core. File reading and GitHub fetching are
// injected at the edges (loader.server.ts, githubClient.ts). See docs/DASHBOARD.md.
//
// Owner invariants encoded here (owner directive 2026-07-23):
//  - completion is computed from project-control files ONLY (authoritative);
//  - HEALTH is a separate concept, degraded by live signals (CI, stale GitHub,
//    blocked deps, control-plane inconsistencies) WITHOUT rewriting completion;
//  - unknown/corrupt/contradictory data is surfaced as UNKNOWN/DEGRADED, never
//    silently coerced to 0% / complete / healthy.

/** The 10 canonical control-plane task statuses, plus a safe fallback. */
export type TaskStatus =
  | 'backlog' | 'ready' | 'claimed' | 'in_progress' | 'self_check'
  | 'awaiting_gate' | 'rework' | 'accepted' | 'blocked' | 'canceled'
  | 'unknown';

/** Owner-facing status vocabulary (small, understandable). */
export type OwnerStatus =
  | 'PLANNED' | 'READY' | 'ACTIVE' | 'TESTING' | 'REVIEW'
  | 'BLOCKED' | 'ACCEPTED' | 'CANCELED' | 'UNKNOWN';

/** Health is independent of completion. */
export type Health = 'GREEN' | 'YELLOW' | 'RED' | 'UNKNOWN';

/** Whether a computed value is trustworthy. Never coerce UNKNOWN to a number. */
export type DataQuality = 'ok' | 'partial' | 'unknown';

export type GateResult = 'PASS' | 'FAIL' | 'BLOCKED' | 'none';

export interface Issue {
  /** Machine code, e.g. 'task.status.unknown', 'roster.contradiction'. */
  code: string;
  /** Human-readable explanation. */
  message: string;
  severity: 'info' | 'warn' | 'error';
  /** Optional reference (task id, file, blocker id). */
  ref?: string;
}

export interface GateStateEntry {
  gateId: string;
  result: GateResult;
  reviewer?: string;
  role?: string;
  reviewedAt?: string;
}

export interface Task {
  id: string;
  milestoneId: string;
  title: string;
  ownerTitle?: string;
  ownerDescription?: string;
  businessReason?: string;
  status: TaskStatus;
  ownerStatus: OwnerStatus;
  progressPercent: number;
  dependencies: string[];
  requiredGates: string[];
  gates: GateStateEntry[];
  passedGates: string[];
  /** required_gates that are not yet PASS. */
  unmetGates: string[];
  /** Reproduces accept(): all required gates PASS (independent role, reviewer!=producer),
   *  all deps accepted, no open blocker referencing the task. */
  acceptanceEligible: boolean;
  acceptanceBlockers: string[];
  accepted: boolean;
  branch?: string;
  prNumber?: number;
  systemId?: string;
  /** Canonical-honesty note (e.g. reconciliation.acceptance_status). */
  reconciliationNote?: string;
  issues: Issue[];
}

export interface Blocker {
  id: string;
  title: string;
  status: string;
  open: boolean;
  affects: string[];
  detail?: string;
  ownerLabel?: string;
  sinceIso?: string;
  affectedTaskIds: string[];
  affectedSystemIds: string[];
}

export interface ProgressBreakdownRow {
  systemId: string;
  systemName: string;
  weight: number;
  /** null => UNKNOWN (do not treat as 0). */
  fraction: number | null;
  /** weight * fraction, or null when UNKNOWN. */
  contribution: number | null;
  contractedCount: number;
  acceptedCount: number;
  expectedCount: number;
  sumProgress: number;
  capApplied?: { gate: string; maxFraction: number; reason: string };
  contributingTasks: Array<{ id: string; status: TaskStatus; progressPercent: number; accepted: boolean }>;
  dataQuality: DataQuality;
}

export interface ProgressResult {
  /** Whole-number percentage for main UI; null when the model can't support a number. */
  percentWhole: number | null;
  /** Precise percentage for detail/debug views only. */
  exactPercent: number | null;
  breakdown: ProgressBreakdownRow[];
  /** Sum of weights whose fraction is UNKNOWN (not counted as 0). */
  unverifiedWeight: number;
  dataQuality: DataQuality;
  /** Human-readable formula, for "How is this calculated?". */
  method: string;
}

export interface SystemModel {
  id: string;
  name: string;
  ownerPurpose: string;
  ownerWhy: string;
  engWeight: number;
  launchWeight: number;
  plannedCount: number;
  criticalForBeta: boolean;
  journeySteps: number[];
  dependsOn: string[];
  tasks: Task[];
  contractedCount: number;
  acceptedCount: number;
  expectedCount: number;
  /** Completion fraction 0..1 (built code) or null=UNKNOWN. */
  engCompletion: number | null;
  /** Launch-readiness fraction 0..1 (accepted+caps) or null=UNKNOWN. */
  launchReadiness: number | null;
  ownerStatusSummary: OwnerStatus;
  health: Health;
  healthReasons: string[];
  dataQuality: DataQuality;
}

export interface MilestoneModel {
  id: string;
  name: string;
  status: string;
  dependsOn: string[];
  acceptedCount: number;
  contractedCount: number;
  summary?: string;
}

export interface ActivityEvent {
  at: string;
  /** Control-plane event kind (never a raw commit). */
  kind:
    | 'task_accepted' | 'task_started' | 'gate_pass' | 'gate_fail'
    | 'pr_merged' | 'blocker_opened' | 'blocker_resolved' | 'checkpoint';
  title: string;
  detail?: string;
  taskId?: string;
  systemId?: string;
  refType?: string;
  refId?: string;
  /** True when the event falls on the reference "today". */
  today: boolean;
}

export interface CurrentWork {
  activeTasks: Task[];
  primary?: Task;
  next: Task[];
}

export interface LaunchBlockerItem {
  rank: number;
  kind: 'not_started' | 'system_incomplete' | 'unmet_gate' | 'open_blocker';
  label: string;
  detail: string;
  systemId?: string;
  launchWeight?: number;
}

export interface CiCheck { name: string; conclusion: string }

export interface CiSummary {
  conclusion: 'success' | 'failure' | 'pending' | 'unknown';
  checks: CiCheck[];
  runUrl?: string;
}

export interface PrSummary {
  number: number;
  title: string;
  mergedAt?: string;
  url?: string;
}

export interface GitHubStatus {
  /** True when a live fetch succeeded this cycle. */
  available: boolean;
  /** True when displaying last-known data because the latest fetch failed. */
  stale: boolean;
  fetchedAtIso?: string;
  headSha?: string;
  headShaShort?: string;
  openPrCount?: number;
  openPrs?: PrSummary[];
  recentMergedPrs?: PrSummary[];
  ci?: CiSummary;
  error?: string;
}

export interface OverallHealth {
  overall: Health;
  reasons: string[];
}

export interface DashboardModel {
  generatedAtIso: string;
  dataQuality: DataQuality;
  issues: Issue[];
  project: {
    name: string;
    currentMilestone: string;
    latestCheckpoint?: string;
    repo?: string;
  };
  engineering: ProgressResult;
  launch: ProgressResult;
  systems: SystemModel[];
  milestones: MilestoneModel[];
  tasks: Task[];
  currentWork: CurrentWork;
  activity: ActivityEvent[];
  openBlockers: Blocker[];
  launchBlockers: LaunchBlockerItem[];
  health: OverallHealth;
  github: GitHubStatus;
  ledgerCounts: Record<string, number>;
}

/** Raw inputs handed to the pure assembler (already JSON-parsed, still untrusted). */
export interface RawControlPlane {
  /** From project-control/tasks/*.json (any parse failures listed in fileIssues). */
  tasks: unknown[];
  masterPlan: unknown;
  state: unknown;
  config: unknown;
  gates: unknown[];
  blockers: unknown[];
  checkpoints: unknown[];
  productMap: unknown;
  /** Populated when a file was missing or unparseable (fail-safe, never silent). */
  fileIssues?: Issue[];
}
