// Deterministic progress calculators (owner directives #1,#2,#4).
// PURE. Two distinct numbers, each reproducible from repo state + product-map
// weights, each returning a full breakdown for "How is this calculated?".
//
//   Engineering % = sum over systems of eng_weight * eng_fraction
//     eng_fraction = clamp( sum(progress_percent of contracted tasks)
//                           / (100 * max(contracted, planned)), 0, 1 )
//     -> credits built-but-unaccepted code; planned-but-uncontracted = incomplete.
//
//   Launch % = sum over systems of launch_weight * launch_fraction
//     launch_fraction = clamp( accepted_count / max(contracted, planned), 0, 1 )
//                       then reduced by any readiness cap that still applies
//     -> only ACCEPTED capability counts; rules capped until G6.
//
// A system whose inputs are unverifiable contributes null (UNKNOWN), never 0.

import type { Task, ProgressResult, ProgressBreakdownRow, DataQuality } from './types';
import type { ParsedProductMapSystem } from './parse';

export interface PerSystemProgress {
  engCompletion: number | null;
  launchReadiness: number | null;
  contractedCount: number;
  acceptedCount: number;
  expectedCount: number;
  sumProgress: number;
  dataQuality: DataQuality;
  capApplied?: { gate: string; maxFraction: number; reason: string };
}

function clamp01(n: number): number {
  return Math.max(0, Math.min(1, n));
}

/** A cap applies while its gate has NOT passed on its target task. */
function capStillApplies(
  cap: ParsedProductMapSystem['readinessCap'],
  taskById: Map<string, Task>,
): boolean {
  if (!cap) return false;
  if (!cap.onTask) return true; // conservative: unknown target => cap applies
  const t = taskById.get(cap.onTask);
  if (!t) return true;
  return !t.passedGates.includes(cap.untilGatePasses);
}

export function computePerSystem(
  system: ParsedProductMapSystem,
  memberTaskIds: string[],
  taskById: Map<string, Task>,
): PerSystemProgress {
  const members = memberTaskIds.map((id) => taskById.get(id)).filter((t): t is Task => !!t);
  const contractedCount = members.length;
  const expectedCount = Math.max(contractedCount, system.plannedCount);
  const acceptedCount = members.filter((t) => t.accepted).length;
  const sumProgress = members.reduce((acc, t) => acc + t.progressPercent, 0);

  // UNKNOWN inputs (a member task with unrecognized status) => the whole system
  // is UNKNOWN, never silently computed from partial data.
  const hasUnknown = members.some((t) => t.status === 'unknown');
  if (hasUnknown || expectedCount === 0) {
    return {
      engCompletion: null, launchReadiness: null,
      contractedCount, acceptedCount, expectedCount, sumProgress,
      dataQuality: 'unknown',
    };
  }

  const engCompletion = clamp01(sumProgress / (100 * expectedCount));
  let launchReadiness = clamp01(acceptedCount / expectedCount);
  let capApplied: PerSystemProgress['capApplied'];
  if (system.readinessCap && capStillApplies(system.readinessCap, taskById)) {
    const capped = Math.min(launchReadiness, system.readinessCap.maxReadinessFraction);
    if (capped !== launchReadiness || launchReadiness <= system.readinessCap.maxReadinessFraction) {
      capApplied = {
        gate: system.readinessCap.untilGatePasses,
        maxFraction: system.readinessCap.maxReadinessFraction,
        reason: system.readinessCap.reason ?? '',
      };
    }
    launchReadiness = capped;
  }

  return {
    engCompletion, launchReadiness,
    contractedCount, acceptedCount, expectedCount, sumProgress,
    dataQuality: 'ok', capApplied,
  };
}

function aggregate(
  systems: ParsedProductMapSystem[],
  perSystem: Map<string, PerSystemProgress>,
  memberTasks: Map<string, Task[]>,
  metric: 'eng' | 'launch',
): ProgressResult {
  const breakdown: ProgressBreakdownRow[] = [];
  let weightedSum = 0;
  let unverifiedWeight = 0;
  let anyKnown = false;

  for (const s of systems) {
    const ps = perSystem.get(s.id);
    const weight = metric === 'eng' ? s.engWeight : s.launchWeight;
    const fraction = ps ? (metric === 'eng' ? ps.engCompletion : ps.launchReadiness) : null;
    const contribution = fraction === null ? null : weight * fraction;
    if (fraction === null) {
      unverifiedWeight += weight;
    } else {
      weightedSum += contribution as number;
      anyKnown = true;
    }
    breakdown.push({
      systemId: s.id,
      systemName: s.name,
      weight,
      fraction,
      contribution,
      contractedCount: ps?.contractedCount ?? 0,
      acceptedCount: ps?.acceptedCount ?? 0,
      expectedCount: ps?.expectedCount ?? 0,
      sumProgress: ps?.sumProgress ?? 0,
      capApplied: metric === 'launch' ? ps?.capApplied : undefined,
      contributingTasks: (memberTasks.get(s.id) ?? []).map((t) => ({
        id: t.id, status: t.status, progressPercent: t.progressPercent, accepted: t.accepted,
      })),
      dataQuality: ps?.dataQuality ?? 'unknown',
    });
  }

  const dataQuality: DataQuality =
    !anyKnown ? 'unknown' : unverifiedWeight > 0 ? 'partial' : 'ok';

  // Owner directive #1/#4: only show a headline number when fully verifiable.
  const exactPercent = anyKnown ? weightedSum : null;
  const percentWhole = dataQuality === 'ok' ? Math.round(weightedSum) : null;

  const method = metric === 'eng'
    ? 'Sum over systems of eng_weight x (sum of task progress_percent) / (100 x max(contracted, planned)). Credits built code; planned-but-uncontracted scope counts as incomplete.'
    : 'Sum over systems of launch_weight x (accepted_count / max(contracted, planned)), reduced by readiness caps (e.g. rules capped until the G6 legal gate passes). Only accepted capability counts.';

  return { percentWhole, exactPercent, breakdown, unverifiedWeight, dataQuality, method };
}

export interface ProgressComputation {
  engineering: ProgressResult;
  launch: ProgressResult;
  perSystem: Map<string, PerSystemProgress>;
}

export function computeProgress(
  systems: ParsedProductMapSystem[],
  tasksBySystem: Map<string, string[]>,
  taskById: Map<string, Task>,
): ProgressComputation {
  const perSystem = new Map<string, PerSystemProgress>();
  const memberTasks = new Map<string, Task[]>();
  for (const s of systems) {
    const ids = tasksBySystem.get(s.id) ?? [];
    perSystem.set(s.id, computePerSystem(s, ids, taskById));
    memberTasks.set(s.id, ids.map((id) => taskById.get(id)).filter((t): t is Task => !!t));
  }
  return {
    engineering: aggregate(systems, perSystem, memberTasks, 'eng'),
    launch: aggregate(systems, perSystem, memberTasks, 'launch'),
    perSystem,
  };
}
