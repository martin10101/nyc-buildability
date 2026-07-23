// Shared presentational primitives for the owner dashboard.
// Status/health are ALWAYS conveyed by label + symbol, never color alone
// (design-system rule + owner directive). Percentages are whole-number in the
// headline; the exact value + full breakdown live behind "How is this
// calculated?" (owner directives #1, #2). All text is rendered via JSX, which
// React escapes — untrusted ledger/GitHub strings cannot inject markup.

import type { ReactNode } from 'react';
import type { Health, OwnerStatus, ProgressResult } from '@/lib/dashboard/types';

export function healthMeta(h: Health): { symbol: string; label: string; cls: string } {
  switch (h) {
    case 'GREEN': return { symbol: '●', label: 'Healthy', cls: 'dash-h-green' };
    case 'YELLOW': return { symbol: '◑', label: 'Attention', cls: 'dash-h-yellow' };
    case 'RED': return { symbol: '▲', label: 'Problem', cls: 'dash-h-red' };
    default: return { symbol: '?', label: 'Unknown', cls: 'dash-h-unknown' };
  }
}

export function HealthDot({ health, showLabel = false }: { health: Health; showLabel?: boolean }) {
  const m = healthMeta(health);
  return (
    <span className={`dash-health ${m.cls}`}>
      <span aria-hidden="true" className="dash-health-sym">{m.symbol}</span>
      {showLabel ? <span>{m.label}</span> : <span className="visually-hidden">{m.label}</span>}
    </span>
  );
}

const OWNER_STATUS_META: Record<OwnerStatus, { label: string; sym: string }> = {
  PLANNED: { label: 'Planned', sym: '○' },
  READY: { label: 'Ready', sym: '◔' },
  ACTIVE: { label: 'Active', sym: '◐' },
  TESTING: { label: 'Testing', sym: '◑' },
  REVIEW: { label: 'In review', sym: '◕' },
  ACCEPTED: { label: 'Accepted', sym: '●' },
  BLOCKED: { label: 'Blocked', sym: '▲' },
  CANCELED: { label: 'Canceled', sym: '×' },
  UNKNOWN: { label: 'Unknown', sym: '?' },
};

export function StatusBadge({ status }: { status: OwnerStatus }) {
  const m = OWNER_STATUS_META[status] ?? OWNER_STATUS_META.UNKNOWN;
  return (
    <span className={`dash-badge dash-badge-${status.toLowerCase()}`}>
      <span aria-hidden="true">{m.sym}</span> {m.label}
    </span>
  );
}

export function ProgressMeter({ value, small = false }: { value: number | null; small?: boolean }) {
  const pct = value === null ? 0 : Math.max(0, Math.min(100, value));
  return (
    <div className={`dash-meter ${small ? 'dash-meter-sm' : ''}`} role="img"
      aria-label={value === null ? 'Progress unavailable' : `${Math.round(pct)} percent`}>
      <div className="dash-meter-fill" style={{ width: `${value === null ? 0 : pct}%` }} />
      {value === null && <span className="dash-meter-unknown" aria-hidden="true">unavailable</span>}
    </div>
  );
}

function fmtWhole(n: number | null): string {
  return n === null ? '—' : `${n}%`;
}

/** Big headline percentage + a reproducible "How is this calculated?" panel. */
export function PercentStat({ label, result }: { label: string; result: ProgressResult }) {
  const unavailable = result.percentWhole === null;
  return (
    <div className="dash-stat">
      <div className="dash-stat-label">{label}</div>
      <div className={`dash-stat-value ${unavailable ? 'dash-stat-unavailable' : ''}`}>
        {unavailable
          ? (result.dataQuality === 'unknown' ? 'Unavailable' : 'Partial')
          : fmtWhole(result.percentWhole)}
      </div>
      <ProgressMeter value={result.percentWhole} />
      {unavailable && (
        <p className="dash-stat-note">
          {result.dataQuality === 'unknown'
            ? 'Progress unavailable — project state could not be verified.'
            : `Partial — ${result.unverifiedWeight}% of the model could not be verified.`}
        </p>
      )}
      <details className="dash-how">
        <summary>How is this calculated?</summary>
        <div className="dash-how-body">
          <p className="dash-how-method">{result.method}</p>
          {result.exactPercent !== null && (
            <p className="dash-how-exact">Exact: {result.exactPercent.toFixed(1)}%</p>
          )}
          <div className="table-scroll">
            <table className="dash-how-table">
              <thead>
                <tr>
                  <th scope="col">System</th>
                  <th scope="col">Weight</th>
                  <th scope="col">Done</th>
                  <th scope="col">Contribution</th>
                </tr>
              </thead>
              <tbody>
                {result.breakdown.map((r) => (
                  <tr key={r.systemId}>
                    <td>{r.systemName}{r.capApplied ? ` (capped until ${r.capApplied.gate})` : ''}</td>
                    <td>{r.weight}</td>
                    <td>{r.fraction === null ? 'unknown' : `${Math.round(r.fraction * 100)}%`}</td>
                    <td>{r.contribution === null ? '—' : `${r.contribution.toFixed(1)}`}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </details>
    </div>
  );
}

export function Freshness({ iso, stale, available }: { iso?: string; stale?: boolean; available?: boolean }) {
  const time = iso ? iso.replace('T', ' ').replace(/\..*$/, ' UTC') : 'never';
  return (
    <span className="dash-fresh">
      <span aria-hidden="true">{stale ? '⚠' : available === false ? '⋯' : '↻'}</span>{' '}
      {stale ? 'Live data STALE — last synced ' : available === false ? 'Live data unavailable' : 'Synced '}
      {available === false && !stale ? '' : time}
    </span>
  );
}

export function UnavailableNote({ children }: { children: ReactNode }) {
  return <p className="dash-unavailable" role="status">{children}</p>;
}
