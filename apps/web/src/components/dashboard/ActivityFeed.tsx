'use client';

import type { DashboardModel, ActivityEvent } from '@/lib/dashboard/types';

const KIND_META: Record<ActivityEvent['kind'], { sym: string; label: string }> = {
  task_accepted: { sym: '✓', label: 'Accepted' },
  task_started: { sym: '▸', label: 'Started' },
  gate_pass: { sym: '✓', label: 'Gate passed' },
  gate_fail: { sym: '✗', label: 'Gate failed' },
  pr_merged: { sym: '»', label: 'PR merged' },
  blocker_opened: { sym: '▲', label: 'Blocker opened' },
  blocker_resolved: { sym: '●', label: 'Blocker resolved' },
  checkpoint: { sym: '◆', label: 'Checkpoint' },
};

function fmtTime(iso: string): string {
  return iso.replace('T', ' ').replace(/\..*$/, '').replace(/\+00:00$/, '') + ' UTC';
}

function EventRow({ e }: { e: ActivityEvent }) {
  const m = KIND_META[e.kind] ?? { sym: '·', label: e.kind };
  return (
    <li className={`dash-event dash-event-${e.kind}`}>
      <span className="dash-event-sym" aria-hidden="true">{m.sym}</span>
      <span className="dash-event-body">
        <span className="dash-event-title">{e.title}</span>
        <span className="dash-event-meta">
          <span className="dash-event-kind">{m.label}</span>
          <span className="dash-event-time">{fmtTime(e.at)}</span>
        </span>
      </span>
    </li>
  );
}

export function ActivityFeed({ model }: { model: DashboardModel }) {
  const today = model.activity.filter((e) => e.today);
  const earlier = model.activity.filter((e) => !e.today);

  return (
    <section className="dash-card" aria-labelledby="dash-activity-h">
      <h2 id="dash-activity-h" className="dash-card-title">What changed</h2>
      <p className="dash-muted dash-small">
        Meaningful control-plane events (acceptances, gate reviews, merges, blockers,
        checkpoints) — not a raw commit log.
      </p>

      <h3 className="dash-subhead">Today ({today.length})</h3>
      {today.length === 0 ? (
        <p className="dash-muted">No control-plane changes recorded today.</p>
      ) : (
        <ul className="dash-events">{today.map((e, i) => <EventRow key={`t${i}`} e={e} />)}</ul>
      )}

      {earlier.length > 0 && (
        <>
          <h3 className="dash-subhead">Earlier</h3>
          <ul className="dash-events">{earlier.map((e, i) => <EventRow key={`e${i}`} e={e} />)}</ul>
        </>
      )}
    </section>
  );
}
