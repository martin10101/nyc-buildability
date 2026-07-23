// GitHub client edge (owner directive #9): SUPPLEMENTAL live ops only. Public
// repo, UNAUTHENTICATED reads — no token, no secret ever. Caches briefly and
// falls back to last-known-marked-STALE on failure; it NEVER blocks or corrupts
// the canonical file-derived project state. Injectable fetch for tests.

import type { GitHubStatus } from './types';
import { parseHeadSha, parsePrs, parseCiRuns } from './github';

const API = 'https://api.github.com';
const DEFAULT_REPO = 'martin10101/nyc-buildability';
const TTL_MS = 45_000;
const TIMEOUT_MS = 6_000;

export type FetchImpl = (url: string, init?: RequestInit) => Promise<Response>;

interface CacheEntry { status: GitHubStatus; at: number }
let cache: CacheEntry | null = null;
let lastGood: GitHubStatus | null = null;

async function getJson(fetchImpl: FetchImpl, url: string): Promise<unknown> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const res = await fetchImpl(url, {
      headers: { Accept: 'application/vnd.github+json', 'User-Agent': 'nycdf-owner-dashboard' },
      signal: ctrl.signal,
    });
    if (!res.ok) throw new Error(`GitHub ${res.status} for ${url}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

export interface FetchOptions {
  repo?: string;
  fetchImpl?: FetchImpl;
  nowMs?: number;
  nowIso?: string;
  /** bypass the in-process cache (tests). */
  noCache?: boolean;
}

export async function fetchGitHubStatus(opts: FetchOptions = {}): Promise<GitHubStatus> {
  const repo = opts.repo ?? DEFAULT_REPO;
  const fetchImpl: FetchImpl | undefined =
    opts.fetchImpl ??
    (typeof globalThis.fetch === 'function'
      ? (globalThis.fetch.bind(globalThis) as FetchImpl)
      : undefined);
  const nowMs = opts.nowMs ?? Date.now();
  const nowIso = opts.nowIso ?? new Date(nowMs).toISOString();

  if (!opts.noCache && cache && nowMs - cache.at < TTL_MS) return cache.status;
  if (!fetchImpl) {
    return { available: false, stale: false, error: 'fetch unavailable in this runtime' };
  }

  const base = `${API}/repos/${repo}`;
  try {
    const [commit, openPulls, closedPulls, runs] = await Promise.all([
      getJson(fetchImpl, `${base}/commits/main`),
      getJson(fetchImpl, `${base}/pulls?state=open&per_page=20`),
      getJson(fetchImpl, `${base}/pulls?state=closed&per_page=20`),
      getJson(fetchImpl, `${base}/actions/runs?branch=main&per_page=30`),
    ]);

    const headSha = parseHeadSha(commit);
    const openPrs = parsePrs(openPulls);
    const recentMergedPrs = parsePrs(closedPulls, { mergedOnly: true }).slice(0, 8);
    const ci = parseCiRuns(runs, headSha);

    const status: GitHubStatus = {
      available: true,
      stale: false,
      fetchedAtIso: nowIso,
      headSha,
      headShaShort: headSha ? headSha.slice(0, 7) : undefined,
      openPrCount: openPrs.length,
      openPrs,
      recentMergedPrs,
      ci,
    };
    cache = { status, at: nowMs };
    lastGood = status;
    return status;
  } catch (e) {
    const error = (e as Error).message || 'GitHub fetch failed';
    if (lastGood) {
      const stale: GitHubStatus = { ...lastGood, stale: true, available: false, error };
      return stale;
    }
    return { available: false, stale: false, error };
  }
}

/** test-only: clear module cache */
export function __resetGitHubCache(): void {
  cache = null;
  lastGood = null;
}
