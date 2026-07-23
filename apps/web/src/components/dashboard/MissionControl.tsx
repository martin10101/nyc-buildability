'use client';

import type { DashboardModel } from '@/lib/dashboard/types';
import { HealthDot, PercentStat, StatusBadge, Freshness, UnavailableNote } from './ui';

const CI_META: Record<string, { sym: string; label: string; cls: string }> = {
  success: { sym: '✓', label: 'Passing', cls: 'dash-ci-ok' },
  failure: { sym: '✗', label: 'Failing', cls: 'dash-ci-bad' },
  pending: { sym: '◐', label: 'Running', cls: 'dash-ci-pending' },
  unknown: { sym: '?', label: 'Unknown', cls: 'dash-ci-unknown' },
};

export function MissionControl({
  model, onSelectSystem, onGoto,
}: {
  model: DashboardModel;
  onSelectSystem: (id: string) => void;
  onGoto: (view: string) => void;
}) {
  const { github, health } = model;
  const ci = CI_META[github.ci?.conclusion ?? 'unknown'] ?? CI_META.unknown;
  const blocked = model.ledgerCounts.blocked ?? 0;
  const primary = model.currentWork.primary;

  return (
    <div>
      {model.dataQuality === 'unknown' && (
        <UnavailableNote>
          Progress unavailable — project state could not be verified. The dashboard
          could not read the control-plane files. Showing no fabricated numbers.
        </UnavailableNote>
      )}

      <section className="dash-progress-row" aria-label="Overall progress">
        <PercentStat label="Engineering completion" result={model.engineering} />
        <PercentStat label="Launch readiness (architect beta)" result={model.launch} />
      </section>

      <section className="dash-tiles" aria-label="System status">
        <button className="dash-tile" onClick={() => onGoto('map')} type="button">
          <div className="dash-tile-label">System health</div>
          <div className="dash-tile-value"><HealthDot health={health.overall} showLabel /></div>
          <div className="dash-tile-note">{health.reasons[0] ?? ''}</div>
        </button>

        <button className="dash-tile" onClick={() => onGoto('work')} type="button">
          <div className="dash-tile-label">Current work</div>
          <div className="dash-tile-value dash-tile-mono">{primary ? primary.id : '—'}</div>
          <div className="dash-tile-note">
            {primary ? (primary.ownerTitle ?? primary.title) : 'No active task'}
          </div>
        </button>

        <div className={`dash-tile ${blocked > 0 ? 'dash-tile-alert' : ''}`}>
          <div className="dash-tile-label">Blocked tasks</div>
          <div className="dash-tile-value">{blocked}</div>
          <div className="dash-tile-note">{blocked > 0 ? 'Needs attention' : 'None'}</div>
        </div>

        <div className="dash-tile">
          <div className="dash-tile-label">CI on main</div>
          <div className={`dash-tile-value ${ci.cls}`}>
            <span aria-hidden="true">{ci.sym}</span> {ci.label}
          </div>
          <div className="dash-tile-note">
            {github.stale ? 'stale' : github.available === false ? 'live data unavailable' : `${github.ci?.checks.length ?? 0} checks`}
          </div>
        </div>

        <div className="dash-tile">
          <div className="dash-tile-label">Open PRs</div>
          <div className="dash-tile-value">{github.openPrCount ?? '—'}</div>
          <div className="dash-tile-note">
            {github.headShaShort ? `main @ ${github.headShaShort}` : 'main head unknown'}
          </div>
        </div>

        <div className="dash-tile">
          <div className="dash-tile-label">Milestone</div>
          <div className="dash-tile-value dash-tile-mono">{model.project.currentMilestone}</div>
          <div className="dash-tile-note">{model.project.latestCheckpoint ?? ''}</div>
        </div>
      </section>

      <section className="dash-card" aria-labelledby="dash-blockers-h">
        <h2 id="dash-blockers-h" className="dash-card-title">Biggest things preventing an architect beta</h2>
        {model.launchBlockers.length === 0 ? (
          <p className="dash-muted">Nothing outstanding on the launch-critical path.</p>
        ) : (
          <ol className="dash-blockers">
            {model.launchBlockers.map((b) => (
              <li key={`${b.kind}-${b.systemId ?? b.label}`}>
                <button
                  type="button"
                  className="dash-blocker-row"
                  onClick={() => b.systemId && onSelectSystem(b.systemId)}
                  disabled={!b.systemId}
                >
                  <span className="dash-blocker-rank">{b.rank}</span>
                  <span className="dash-blocker-main">
                    <span className="dash-blocker-label">{b.label}</span>
                    <span className="dash-blocker-detail">{b.detail}</span>
                  </span>
                  <span className={`dash-kind dash-kind-${b.kind}`}>{b.kind.replace(/_/g, ' ')}</span>
                </button>
              </li>
            ))}
          </ol>
        )}
      </section>

      <p className="dash-honesty" role="note">
        This is a read-only observatory over the project-control ledger. Progress is derived
        deterministically from recorded state, not from commit volume. Rules shown in later
        systems are engineering drafts and are <strong>not legally verified</strong> until a
        qualified human approves them (gate G6).
      </p>

      <div className="dash-freshness-bar">
        <Freshness iso={github.fetchedAtIso} stale={github.stale} available={github.available} />
        <span className="dash-generated">Ledger read {model.generatedAtIso.replace('T', ' ').replace(/\..*$/, ' UTC')}</span>
      </div>
    </div>
  );
}
