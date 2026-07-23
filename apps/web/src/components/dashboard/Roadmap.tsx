'use client';

import type { DashboardModel, SystemModel } from '@/lib/dashboard/types';
import { HealthDot, StatusBadge, ProgressMeter } from './ui';

function orderKey(s: SystemModel): number {
  return s.journeySteps.length ? Math.min(...s.journeySteps) : 99;
}

export function Roadmap({
  model, viewMode, onSelectSystem,
}: {
  model: DashboardModel; viewMode: 'owner' | 'technical'; onSelectSystem: (id: string) => void;
}) {
  const systems = [...model.systems].sort((a, b) => orderKey(a) - orderKey(b) || a.name.localeCompare(b.name));

  return (
    <section className="dash-card" aria-labelledby="dash-roadmap-h">
      <h2 id="dash-roadmap-h" className="dash-card-title">Roadmap — by product system</h2>
      <p className="dash-muted dash-small">
        Two bars per system: <strong>built</strong> (engineering) and <strong>launch-ready</strong>
        {' '}(accepted &amp; verified). They differ on purpose.
      </p>
      <ul className="dash-roadmap">
        {systems.map((s) => {
          const eng = s.engCompletion === null ? null : Math.round(s.engCompletion * 100);
          const launch = s.launchReadiness === null ? null : Math.round(s.launchReadiness * 100);
          return (
            <li key={s.id} className="dash-roadmap-item">
              <div className="dash-roadmap-head">
                <button type="button" className="dash-link dash-roadmap-name" onClick={() => onSelectSystem(s.id)}>
                  {s.name}
                </button>
                {s.criticalForBeta && <span className="dash-crit-tag">critical</span>}
                <HealthDot health={s.health} showLabel />
                <StatusBadge status={s.ownerStatusSummary} />
              </div>
              <div className="dash-roadmap-bars">
                <div className="dash-bar-row">
                  <span className="dash-bar-label">Built</span>
                  <ProgressMeter value={eng} small />
                  <span className="dash-bar-pct">{eng === null ? '—' : `${eng}%`}</span>
                </div>
                <div className="dash-bar-row">
                  <span className="dash-bar-label">Launch-ready</span>
                  <ProgressMeter value={launch} small />
                  <span className="dash-bar-pct">{launch === null ? '—' : `${launch}%`}</span>
                </div>
              </div>
              <details className="dash-roadmap-tasks">
                <summary>{s.contractedCount} task(s) · {s.acceptedCount} accepted</summary>
                {s.tasks.length === 0 ? (
                  <p className="dash-muted dash-small">Not started — no tasks contracted yet.</p>
                ) : (
                  <ul className="dash-tasklist">
                    {s.tasks.map((t) => (
                      <li key={t.id}>
                        <span className="dash-mono">{t.id}</span>
                        <span className="dash-tasklist-title">{t.ownerTitle ?? t.title}</span>
                        <StatusBadge status={t.ownerStatus} />
                        {viewMode === 'technical' && t.prNumber && <span className="dash-small dash-muted">PR #{t.prNumber}</span>}
                      </li>
                    ))}
                  </ul>
                )}
              </details>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
