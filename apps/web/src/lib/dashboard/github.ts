// GitHub read-only parsers (owner directive #9): GitHub is SUPPLEMENTAL live
// operational state (CI / PR / head / freshness). It NEVER feeds the canonical
// project-state numbers. These functions are PURE (parse recorded/live JSON ->
// typed summaries); the actual network fetch + caching lives in githubClient.ts.

import type { CiSummary, PrSummary, CiCheck } from './types';
import { isRecord, asString, asFiniteNumber } from './parse';

export function parseHeadSha(commitJson: unknown): string | undefined {
  if (!isRecord(commitJson)) return undefined;
  return asString(commitJson.sha);
}

export function parsePrs(pullsJson: unknown, opts: { mergedOnly?: boolean } = {}): PrSummary[] {
  if (!Array.isArray(pullsJson)) return [];
  const out: PrSummary[] = [];
  for (const p of pullsJson) {
    if (!isRecord(p)) continue;
    const number = asFiniteNumber(p.number);
    if (number === undefined) continue;
    const mergedAt = asString(p.merged_at) ?? undefined;
    if (opts.mergedOnly && !mergedAt) continue;
    out.push({
      number,
      title: asString(p.title) ?? `PR #${number}`,
      mergedAt,
      url: asString(p.html_url),
    });
  }
  return out;
}

/**
 * Summarize CI from GET /actions/runs?branch=main (optionally restricted to the
 * head SHA). Latest run per workflow name; overall conclusion = failure if any
 * failed, else pending if any still running, else success if any succeeded.
 */
export function parseCiRuns(runsJson: unknown, headSha?: string): CiSummary {
  const empty: CiSummary = { conclusion: 'unknown', checks: [] };
  if (!isRecord(runsJson)) return empty;
  const runs = Array.isArray(runsJson.workflow_runs) ? runsJson.workflow_runs : [];
  if (!runs.length) return empty;

  // latest run per workflow name (runs are returned newest-first; keep first seen)
  const latestByName = new Map<string, Record<string, unknown>>();
  for (const r of runs) {
    if (!isRecord(r)) continue;
    if (headSha && asString(r.head_sha) && asString(r.head_sha) !== headSha) continue;
    const name = asString(r.name) ?? asString(r.display_title) ?? 'workflow';
    if (!latestByName.has(name)) latestByName.set(name, r);
  }
  const source = latestByName.size ? latestByName : (() => {
    // headSha filtered everything out (e.g. very fresh push): fall back to newest overall
    const m = new Map<string, Record<string, unknown>>();
    for (const r of runs) {
      if (!isRecord(r)) continue;
      const name = asString(r.name) ?? 'workflow';
      if (!m.has(name)) m.set(name, r);
    }
    return m;
  })();

  const checks: CiCheck[] = [];
  let anyFailure = false;
  let anyPending = false;
  let anySuccess = false;
  for (const [name, r] of source) {
    const status = asString(r.status); // queued|in_progress|completed
    const conclusion = asString(r.conclusion); // success|failure|cancelled|...|null
    let c: string;
    if (status !== 'completed') { c = 'pending'; anyPending = true; }
    else if (conclusion === 'success') { c = 'success'; anySuccess = true; }
    else if (conclusion === 'failure' || conclusion === 'timed_out' || conclusion === 'startup_failure') {
      c = 'failure'; anyFailure = true;
    } else { c = conclusion ?? 'unknown'; }
    checks.push({ name, conclusion: c });
  }
  checks.sort((a, b) => a.name.localeCompare(b.name));

  const conclusion: CiSummary['conclusion'] =
    anyFailure ? 'failure' : anyPending ? 'pending' : anySuccess ? 'success' : 'unknown';
  return { conclusion, checks };
}
