// Server composition edge: read files + fetch supplemental GitHub, then assemble.
// The ONLY function the /dashboard server component calls. Read-only.

import { loadControlPlane } from './loader.server';
import { fetchGitHubStatus } from './githubClient';
import { assembleDashboard } from './assemble';
import type { DashboardModel, GitHubStatus } from './types';

export async function getDashboardModel(): Promise<DashboardModel> {
  const nowIso = new Date().toISOString();
  const rawPromise = loadControlPlane();
  const githubPromise: Promise<GitHubStatus> = fetchGitHubStatus({ nowIso }).catch(
    (e): GitHubStatus => ({ available: false, stale: false, error: (e as Error).message }),
  );
  const [raw, github] = await Promise.all([rawPromise, githubPromise]);
  return assembleDashboard(raw, github, nowIso);
}
