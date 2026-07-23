'use client';

import { useEffect, useRef } from 'react';
import type { SystemModel } from '@/lib/dashboard/types';
import { HealthDot, StatusBadge, ProgressMeter } from './ui';

function relianceVerdict(s: SystemModel): { can: boolean; text: string } {
  if (s.launchReadiness === null) return { can: false, text: 'Unknown — readiness could not be verified.' };
  if (s.launchReadiness >= 0.999 && s.health !== 'RED') return { can: true, text: 'Yes — this system is accepted and healthy.' };
  if (s.contractedCount === 0) return { can: false, text: 'No — this system has not been started yet.' };
  if (s.health === 'RED') return { can: false, text: 'No — this system currently needs attention (see health below).' };
  return { can: false, text: 'Not yet — it is built or partially accepted but not fully launch-ready.' };
}

function whatsMissing(s: SystemModel): string[] {
  const out: string[] = [];
  if (s.contractedCount === 0) out.push('No tasks contracted yet.');
  const unmet = [...new Set(s.tasks.flatMap((t) => t.unmetGates))].sort();
  if (unmet.length) out.push(`Pending gate(s): ${unmet.join(', ')}.`);
  const notAccepted = s.tasks.filter((t) => !t.accepted).length;
  if (s.contractedCount > 0 && notAccepted > 0) out.push(`${notAccepted} task(s) not yet accepted.`);
  if (s.launchReadiness !== null && s.launchReadiness < 1 && s.expectedCount > s.contractedCount) {
    out.push(`${s.expectedCount - s.contractedCount} more planned task(s) not yet contracted.`);
  }
  return out.length ? out : ['Nothing outstanding.'];
}

export function SystemDrawer({
  system, viewMode, onClose, onSelectSystem,
}: {
  system: SystemModel; viewMode: 'owner' | 'technical'; onClose: () => void; onSelectSystem: (id: string) => void;
}) {
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  const eng = system.engCompletion === null ? null : Math.round(system.engCompletion * 100);
  const launch = system.launchReadiness === null ? null : Math.round(system.launchReadiness * 100);
  const verdict = relianceVerdict(system);

  return (
    <div className="dash-drawer-scrim" onClick={onClose}>
      <aside
        className="dash-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dash-drawer-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="dash-drawer-head">
          <h2 id="dash-drawer-title" className="dash-drawer-title">{system.name}</h2>
          <button ref={closeRef} type="button" className="dash-drawer-close" onClick={onClose} aria-label="Close detail">×</button>
        </div>

        <div className="dash-drawer-badges">
          <HealthDot health={system.health} showLabel />
          <StatusBadge status={system.ownerStatusSummary} />
          {system.criticalForBeta && <span className="dash-crit-tag">critical for beta</span>}
        </div>

        {/* Owner view (default) */}
        <section className="dash-drawer-section">
          <h3 className="dash-drawer-h">What it does</h3>
          <p>{system.ownerPurpose}</p>
          <h3 className="dash-drawer-h">Why it matters</h3>
          <p>{system.ownerWhy}</p>

          <h3 className="dash-drawer-h">Can an architect rely on this today?</h3>
          <p className={verdict.can ? 'dash-verdict-yes' : 'dash-verdict-no'}>
            <span aria-hidden="true">{verdict.can ? '✓ ' : '✗ '}</span>{verdict.text}
          </p>

          <div className="dash-drawer-bars">
            <div className="dash-bar-row">
              <span className="dash-bar-label">Built</span><ProgressMeter value={eng} small />
              <span className="dash-bar-pct">{eng === null ? '—' : `${eng}%`}</span>
            </div>
            <div className="dash-bar-row">
              <span className="dash-bar-label">Launch-ready</span><ProgressMeter value={launch} small />
              <span className="dash-bar-pct">{launch === null ? '—' : `${launch}%`}</span>
            </div>
          </div>

          <h3 className="dash-drawer-h">What is still missing?</h3>
          <ul className="dash-missing">{whatsMissing(system).map((m, i) => <li key={i}>{m}</li>)}</ul>

          {system.healthReasons.length > 0 && (
            <>
              <h3 className="dash-drawer-h">Health</h3>
              <ul className="dash-missing">{system.healthReasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
            </>
          )}
        </section>

        {/* Technical view */}
        <details className="dash-drawer-tech" open={viewMode === 'technical'}>
          <summary>Technical detail</summary>
          <dl className="dash-tech">
            <dt>Engineering weight</dt><dd>{system.engWeight}</dd>
            <dt>Launch weight</dt><dd>{system.launchWeight}</dd>
            <dt>Tasks</dt><dd>{system.acceptedCount} accepted / {system.contractedCount} contracted / {system.expectedCount} expected</dd>
            {system.dependsOn.length > 0 && (
              <><dt>Depends on</dt><dd>
                {system.dependsOn.map((d, i) => (
                  <span key={d}>
                    {i > 0 && ', '}
                    <button type="button" className="dash-link" onClick={() => onSelectSystem(d)}>{d}</button>
                  </span>
                ))}
              </dd></>
            )}
          </dl>
          {system.tasks.length > 0 && (
            <table className="dash-tech-table">
              <thead><tr><th scope="col">Task</th><th scope="col">Status</th><th scope="col">Gates</th></tr></thead>
              <tbody>
                {system.tasks.map((t) => (
                  <tr key={t.id}>
                    <td className="dash-mono">{t.id}{t.prNumber ? ` · PR #${t.prNumber}` : ''}</td>
                    <td><StatusBadge status={t.ownerStatus} /></td>
                    <td className="dash-small">{t.passedGates.join(',') || '—'}{t.unmetGates.length ? ` (pending ${t.unmetGates.join(',')})` : ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </details>
      </aside>
    </div>
  );
}
