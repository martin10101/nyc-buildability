// "Biggest things preventing an architect beta" (owner directive #7).
// Deterministic, derived from launch-readiness critical dependencies + unmet
// gates/capabilities + open blockers. NOT a subjective AI list. PURE.

import type { SystemModel, Blocker, LaunchBlockerItem } from './types';

export function computeLaunchBlockers(
  systems: SystemModel[],
  openBlockers: Blocker[],
  limit = 7,
): LaunchBlockerItem[] {
  const items: Array<LaunchBlockerItem & { score: number; sortKey: string }> = [];

  for (const s of systems) {
    if (!s.criticalForBeta) continue;
    const readiness = s.launchReadiness; // may be null (UNKNOWN)
    const effReadiness = readiness ?? 0;
    if (readiness !== null && effReadiness >= 1) continue; // fully launch-ready
    const gap = s.launchWeight * (1 - effReadiness);
    if (gap <= 0 && readiness !== null) continue;

    let kind: LaunchBlockerItem['kind'];
    let detail: string;
    if (readiness === null) {
      kind = 'system_incomplete';
      detail = 'Launch readiness could not be verified for this system.';
    } else if (s.contractedCount === 0) {
      kind = 'not_started';
      detail = 'Not started yet — no tasks contracted.';
    } else if (s.tasks.some((t) => t.unmetGates.length > 0) &&
               s.tasks.some((t) => t.status === 'awaiting_gate' || t.accepted)) {
      kind = 'unmet_gate';
      const gates = [...new Set(s.tasks.flatMap((t) => t.unmetGates))].sort();
      detail = `Built but not verified — awaiting gate(s) ${gates.join(', ') || 'review'}.`;
    } else {
      kind = 'system_incomplete';
      detail = `${s.acceptedCount} of ${s.expectedCount} needed pieces accepted.`;
    }

    items.push({
      rank: 0, kind, systemId: s.id, label: s.name, detail,
      launchWeight: s.launchWeight, score: gap, sortKey: s.id,
    });
  }

  for (const b of openBlockers) {
    // urgency = highest launch weight among the critical systems it affects
    const affectedCritical = systems.filter(
      (s) => s.criticalForBeta && b.affectedSystemIds.includes(s.id),
    );
    const score = affectedCritical.length
      ? Math.max(...affectedCritical.map((s) => s.launchWeight))
      : 4;
    items.push({
      rank: 0, kind: 'open_blocker', label: b.ownerLabel ?? b.title,
      detail: `Owner action needed (${b.id})${affectedCritical.length ? ` — affects ${affectedCritical.map((s) => s.name).join(', ')}` : ''}.`,
      score, sortKey: b.id,
    });
  }

  items.sort((a, b) => (b.score - a.score) || a.sortKey.localeCompare(b.sortKey));
  return items.slice(0, limit).map((it, i) => ({
    rank: i + 1, kind: it.kind, label: it.label, detail: it.detail,
    systemId: it.systemId, launchWeight: it.launchWeight,
  }));
}
