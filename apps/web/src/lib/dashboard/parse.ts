// Defensive parsers: raw (untrusted, already-JSON) -> typed engine values.
// PURE. Never throws. Anything unrecognized becomes UNKNOWN and records an Issue
// (owner directive #4: never silently coerce unknown/corrupt data to 0/complete).

import type {
  Issue, TaskStatus, OwnerStatus, GateStateEntry, GateResult,
} from './types';

export const KNOWN_STATUSES: readonly TaskStatus[] = [
  'backlog', 'ready', 'claimed', 'in_progress', 'self_check',
  'awaiting_gate', 'rework', 'accepted', 'blocked', 'canceled',
];

/** Built-in fallback vocabulary; product-map.owner_status_vocabulary overrides it. */
export const DEFAULT_OWNER_STATUS: Record<TaskStatus, OwnerStatus> = {
  backlog: 'PLANNED',
  ready: 'READY',
  claimed: 'ACTIVE',
  in_progress: 'ACTIVE',
  self_check: 'TESTING',
  awaiting_gate: 'REVIEW',
  rework: 'ACTIVE',
  accepted: 'ACCEPTED',
  blocked: 'BLOCKED',
  canceled: 'CANCELED',
  unknown: 'UNKNOWN',
};

export const ACTIVE_STATUSES: ReadonlySet<TaskStatus> = new Set<TaskStatus>([
  'claimed', 'in_progress', 'self_check', 'awaiting_gate', 'rework',
]);

export const INDEPENDENT_GATES: ReadonlySet<string> = new Set(['G1', 'G3', 'G4', 'G5', 'G6']);

export function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}

export function asString(v: unknown): string | undefined {
  return typeof v === 'string' ? v : undefined;
}

export function asFiniteNumber(v: unknown): number | undefined {
  return typeof v === 'number' && Number.isFinite(v) ? v : undefined;
}

export function asStringArray(v: unknown): string[] {
  if (!Array.isArray(v)) return [];
  return v.filter((x): x is string => typeof x === 'string');
}

export function coerceStatus(v: unknown): { status: TaskStatus; issue?: Issue } {
  const s = asString(v);
  if (s && (KNOWN_STATUSES as readonly string[]).includes(s)) {
    return { status: s as TaskStatus };
  }
  return {
    status: 'unknown',
    issue: {
      code: 'task.status.unknown',
      message: `Unrecognized task status ${JSON.stringify(v)}; treated as UNKNOWN.`,
      severity: 'warn',
    },
  };
}

export function ownerStatusFor(
  status: TaskStatus,
  vocab: Record<string, string> | undefined,
): OwnerStatus {
  const fromVocab = vocab && typeof vocab[status] === 'string' ? vocab[status] : undefined;
  const candidate = (fromVocab ?? DEFAULT_OWNER_STATUS[status]) as OwnerStatus;
  return candidate ?? 'UNKNOWN';
}

/** Parse a gates/*.json record into a normalized gate-state entry (or null). */
export function parseGateRecord(raw: unknown): GateStateEntry | null {
  if (!isRecord(raw)) return null;
  const gateId = asString(raw.gate_id);
  const taskId = asString(raw.task_id);
  if (!gateId || !taskId) return null;
  const result = asString(raw.result);
  const normalized: GateResult =
    result === 'PASS' || result === 'FAIL' || result === 'BLOCKED' ? result : 'none';
  return {
    gateId,
    result: normalized,
    reviewer: asString(raw.reviewer),
    role: asString(raw.role),
    reviewedAt: asString(raw.reviewed_at),
  };
}

export interface ParsedProductMapSystem {
  id: string;
  name: string;
  ownerPurpose: string;
  ownerWhy: string;
  engWeight: number;
  launchWeight: number;
  plannedCount: number;
  milestones: string[];
  tasksInclude: string[];
  tasksExclude: string[];
  dependsOn: string[];
  criticalForBeta: boolean;
  journeySteps: number[];
  readinessCap?: { untilGatePasses: string; onTask?: string; maxReadinessFraction: number; reason?: string };
}

export interface ParsedProductMap {
  systems: ParsedProductMapSystem[];
  ownerStatusVocabulary: Record<string, string>;
  journey: Array<{ step: number; label: string; systems: string[] }>;
  taskOverrides: Record<string, { ownerTitle: string; ownerDescription: string }>;
  blockerLabels: Record<string, string>;
  repo?: { github?: string; defaultBranch?: string; public?: boolean };
  issues: Issue[];
}

export function parseProductMap(raw: unknown): ParsedProductMap {
  const issues: Issue[] = [];
  const empty: ParsedProductMap = {
    systems: [], ownerStatusVocabulary: {}, journey: [],
    taskOverrides: {}, blockerLabels: {}, issues,
  };
  if (!isRecord(raw)) {
    issues.push({ code: 'product_map.missing', message: 'product-map.json missing or not an object.', severity: 'error' });
    return empty;
  }
  const systemsRaw = Array.isArray(raw.systems) ? raw.systems : [];
  const systems: ParsedProductMapSystem[] = [];
  for (const s of systemsRaw) {
    if (!isRecord(s)) continue;
    const id = asString(s.id);
    if (!id) continue;
    const cap = isRecord(s.readiness_cap) ? s.readiness_cap : undefined;
    systems.push({
      id,
      name: asString(s.name) ?? id,
      ownerPurpose: asString(s.owner_purpose) ?? '',
      ownerWhy: asString(s.owner_why) ?? '',
      engWeight: asFiniteNumber(s.eng_weight) ?? 0,
      launchWeight: asFiniteNumber(s.launch_weight) ?? 0,
      plannedCount: asFiniteNumber(s.planned_count) ?? 0,
      milestones: asStringArray(s.milestones),
      tasksInclude: asStringArray(s.tasks_include),
      tasksExclude: asStringArray(s.tasks_exclude),
      dependsOn: asStringArray(s.depends_on),
      criticalForBeta: s.critical_for_beta === true,
      journeySteps: Array.isArray(s.journey_steps)
        ? s.journey_steps.filter((n): n is number => typeof n === 'number')
        : [],
      readinessCap: cap
        ? {
            untilGatePasses: asString(cap.until_gate_passes) ?? '',
            onTask: asString(cap.on_task),
            maxReadinessFraction: asFiniteNumber(cap.max_readiness_fraction) ?? 1,
            reason: asString(cap.reason),
          }
        : undefined,
    });
  }
  if (systems.length === 0) {
    issues.push({ code: 'product_map.no_systems', message: 'product-map.json defines no systems.', severity: 'error' });
  }

  const vocab: Record<string, string> = {};
  if (isRecord(raw.owner_status_vocabulary)) {
    for (const [k, v] of Object.entries(raw.owner_status_vocabulary)) {
      if (typeof v === 'string') vocab[k] = v;
    }
  }

  const journey: ParsedProductMap['journey'] = [];
  if (Array.isArray(raw.architect_journey)) {
    for (const j of raw.architect_journey) {
      if (!isRecord(j)) continue;
      const step = asFiniteNumber(j.step);
      const label = asString(j.label);
      if (step === undefined || !label) continue;
      journey.push({ step, label, systems: asStringArray(j.systems) });
    }
  }

  const taskOverrides: ParsedProductMap['taskOverrides'] = {};
  if (isRecord(raw.task_overrides)) {
    for (const [k, v] of Object.entries(raw.task_overrides)) {
      if (!isRecord(v)) continue;
      const ownerTitle = asString(v.owner_title);
      const ownerDescription = asString(v.owner_description);
      if (ownerTitle && ownerDescription) taskOverrides[k] = { ownerTitle, ownerDescription };
    }
  }

  const blockerLabels: Record<string, string> = {};
  if (isRecord(raw.blocker_labels)) {
    for (const [k, v] of Object.entries(raw.blocker_labels)) {
      if (typeof v === 'string') blockerLabels[k] = v;
    }
  }

  const repoRaw = isRecord(raw.repo) ? raw.repo : undefined;
  const repo = repoRaw
    ? {
        github: asString(repoRaw.github),
        defaultBranch: asString(repoRaw.default_branch),
        public: repoRaw.public === true,
      }
    : undefined;

  return { systems, ownerStatusVocabulary: vocab, journey, taskOverrides, blockerLabels, repo, issues };
}
