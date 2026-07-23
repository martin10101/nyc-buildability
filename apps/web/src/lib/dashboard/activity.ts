// "What changed" (owner directive #6): a CONTROL-PLANE event model, not a raw
// git log. Events come from ledger timestamps: task accepted/started, gate
// PASS/FAIL, PR merged, blocker opened/resolved, checkpoint. Raw commits are
// deliberately excluded (they are secondary evidence, surfaced only via PR/CI).
// PURE. `todayIso` is injected so "today" is deterministic and testable.

import type { ActivityEvent, Task } from './types';
import { isRecord, asString, asFiniteNumber } from './parse';

function dayOf(iso: string | undefined): string | undefined {
  if (!iso || typeof iso !== 'string') return undefined;
  const m = iso.match(/^(\d{4}-\d{2}-\d{2})/);
  return m ? m[1] : undefined;
}

export function computeActivity(
  rawTasks: unknown[],
  rawGates: unknown[],
  rawBlockers: unknown[],
  rawCheckpoints: unknown[],
  taskById: Map<string, Task>,
  todayIso: string,
  limit = 50,
): ActivityEvent[] {
  const today = dayOf(todayIso);
  const events: ActivityEvent[] = [];
  const push = (e: Omit<ActivityEvent, 'today'>) => {
    if (!e.at) return;
    events.push({ ...e, today: dayOf(e.at) === today });
  };
  const sysOf = (tid: string) => taskById.get(tid)?.systemId;
  const nameOf = (tid: string) => taskById.get(tid)?.ownerTitle ?? taskById.get(tid)?.title ?? tid;

  for (const t of rawTasks) {
    if (!isRecord(t)) continue;
    const id = asString(t.task_id);
    if (!id) continue;

    const acceptedAt = asString(t.accepted_at);
    if (acceptedAt) {
      push({ at: acceptedAt, kind: 'task_accepted', taskId: id, systemId: sysOf(id),
        title: `Accepted: ${nameOf(id)}`, detail: id });
    }

    // task started = first progress_log entry that reaches 'claimed'
    if (Array.isArray(t.progress_log)) {
      const started = t.progress_log.find((e) => isRecord(e) && e.status === 'claimed');
      if (isRecord(started)) {
        const at = asString(started.at);
        if (at) push({ at, kind: 'task_started', taskId: id, systemId: sysOf(id),
          title: `Started: ${nameOf(id)}`, detail: id });
      }
    }

    // PR merged (reconciliation carries the reliable merged_pr + a timestamp)
    if (isRecord(t.reconciliation)) {
      const pr = asFiniteNumber(t.reconciliation.merged_pr);
      const at = asString(t.reconciliation.reconciled_at);
      if (pr && at) {
        push({ at, kind: 'pr_merged', taskId: id, systemId: sysOf(id),
          title: `Merged PR #${pr}: ${nameOf(id)}`, detail: id, refType: 'pr', refId: String(pr) });
      }
    }
  }

  for (const g of rawGates) {
    if (!isRecord(g)) continue;
    const tid = asString(g.task_id);
    const gid = asString(g.gate_id);
    const result = asString(g.result);
    const at = asString(g.reviewed_at);
    if (!tid || !gid || !at) continue;
    if (result === 'PASS' || result === 'FAIL') {
      push({
        at, kind: result === 'PASS' ? 'gate_pass' : 'gate_fail',
        taskId: tid, systemId: sysOf(tid),
        title: `${gid} ${result}: ${nameOf(tid)}`,
        detail: `${tid} - ${gid} reviewed by ${asString(g.reviewer) ?? 'reviewer'}`,
      });
    }
  }

  for (const b of rawBlockers) {
    if (!isRecord(b)) continue;
    const id = asString(b.blocker_id);
    if (!id) continue;
    const created = asString(b.created_at);
    if (created) push({ at: created, kind: 'blocker_opened', refType: 'blocker', refId: id,
      title: `Blocker opened: ${asString(b.title) ?? id}`, detail: id });
    if (Array.isArray(b.audit_log)) {
      for (const entry of b.audit_log) {
        if (!isRecord(entry)) continue;
        const at = asString(entry.at);
        const note = asString(entry.note) ?? '';
        if (at && /resolv|close/i.test(`${note} ${asString(b.status) ?? ''}`)) {
          push({ at, kind: 'blocker_resolved', refType: 'blocker', refId: id,
            title: `Blocker resolved: ${asString(b.title) ?? id}`, detail: note });
        }
      }
    }
  }

  for (const c of rawCheckpoints) {
    if (!isRecord(c)) continue;
    const at = asString(c.timestamp);
    const cid = asString(c.checkpoint_id);
    if (at && cid) push({ at, kind: 'checkpoint', refType: 'checkpoint', refId: cid,
      title: `Checkpoint ${cid}`, detail: asString(c.summary) });
  }

  events.sort((a, b) => (a.at < b.at ? 1 : a.at > b.at ? -1 : 0));
  return events.slice(0, limit);
}
