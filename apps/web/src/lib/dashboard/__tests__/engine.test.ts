import { describe, it, expect, beforeEach } from 'vitest';
import { assembleDashboard } from '@/lib/dashboard/assemble';
import { parseCiRuns, parsePrs, parseHeadSha } from '@/lib/dashboard/github';
import { fetchGitHubStatus, __resetGitHubCache, type FetchImpl } from '@/lib/dashboard/githubClient';
import { dashboardEnabled } from '@/lib/dashboard/config';
import type { RawControlPlane, GitHubStatus } from '@/lib/dashboard/types';
import {
  synthRaw, NOW_ISO, ghCommitMain, ghPullsClosed, ghRunsSuccess, ghRunsFailure,
} from '@/test-support/dashboard/fixtures';

const GH_OK: GitHubStatus = { available: true, stale: false, ci: { conclusion: 'success', checks: [] } };

describe('progress calculators (deterministic, hand-computed)', () => {
  it('engineering credits built code: 50*0.95 + 50*0.5 = 72.5 -> 73%', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    expect(m.engineering.exactPercent).toBeCloseTo(72.5, 6);
    expect(m.engineering.percentWhole).toBe(73);
    expect(m.engineering.dataQuality).toBe('ok');
  });

  it('launch counts only accepted, capped by G6: 50*0.5 + 50*0.15 = 32.5 -> 33%', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    expect(m.launch.exactPercent).toBeCloseTo(32.5, 6);
    expect(m.launch.percentWhole).toBe(33);
  });

  it('the two numbers diverge and launch < engineering', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    expect(m.launch.percentWhole!).toBeLessThan(m.engineering.percentWhole!);
  });

  it('exposes a reproducible breakdown for "How is this calculated?"', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    const rowB = m.engineering.breakdown.find((r) => r.systemId === 'sys_b')!;
    expect(rowB.weight).toBe(50);
    expect(rowB.fraction).toBeCloseTo(0.5, 6);
    expect(rowB.contribution).toBeCloseTo(25, 6);
    expect(rowB.contributingTasks.map((t) => t.id).sort()).toEqual(['M1-T001', 'M1-T002']);
    const launchB = m.launch.breakdown.find((r) => r.systemId === 'sys_b')!;
    expect(launchB.capApplied?.gate).toBe('G6');
  });
});

describe('owner status + acceptance eligibility', () => {
  it('maps control statuses to owner vocabulary', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    const byId = Object.fromEntries(m.tasks.map((t) => [t.id, t.ownerStatus]));
    expect(byId['M0-T001']).toBe('ACCEPTED');
    expect(byId['M0-T002']).toBe('REVIEW');
    expect(byId['M1-T002']).toBe('BLOCKED');
  });

  it('reproduces accept(): awaiting_gate + gates PASS + deps + no blocker = eligible', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    const t2 = m.tasks.find((t) => t.id === 'M0-T002')!;
    expect(t2.acceptanceEligible).toBe(true);
    const b2 = m.tasks.find((t) => t.id === 'M1-T002')!;
    expect(b2.acceptanceEligible).toBe(false);
    expect(b2.acceptanceBlockers.length).toBeGreaterThan(0);
  });

  it('ignores a gate PASS recorded by the producer (independence rule)', () => {
    const raw: RawControlPlane = synthRaw({
      tasks: [{
        task_id: 'M0-T009', milestone_id: 'M0', title: 'x', status: 'awaiting_gate',
        progress_percent: 85, required_gates: ['G3'], dependencies: [], producer_agent: 'backend-engineer',
      }],
      gates: [{ task_id: 'M0-T009', gate_id: 'G3', reviewer: 'backend-engineer', role: 'independent_review', result: 'PASS', reviewed_at: '2026-07-23T10:00:00Z' }],
    });
    const m = assembleDashboard(raw, GH_OK, NOW_ISO);
    const t = m.tasks.find((x) => x.id === 'M0-T009')!;
    expect(t.passedGates).not.toContain('G3');
    expect(t.unmetGates).toContain('G3');
  });

  it('an accepted task never shows pending gates, even with legacy records (owner directive #8)', () => {
    // Mirrors accept()'s tolerance of legacy pre-hardening gate records: an
    // ACCEPTED task with a G3 recorded by the orchestrator and no G4 record must
    // still read as fully gated — never "pending" — so its canonical ACCEPTED
    // status is not contradicted in any drill-down.
    const raw: RawControlPlane = synthRaw({
      tasks: [{
        task_id: 'M0-T050', milestone_id: 'M0', title: 'legacy accepted', status: 'accepted',
        progress_percent: 100, required_gates: ['G3', 'G4'], dependencies: [],
        producer_agent: 'backend-engineer', accepted_at: '2026-07-01T00:00:00+00:00',
      }],
      gates: [{ task_id: 'M0-T050', gate_id: 'G3', reviewer: 'orchestrator', result: 'PASS', reviewed_at: '2026-07-01T00:00:00+00:00' }],
      state: { project_status: 'active', current_milestone: 'M0', accepted_tasks: ['M0-T050'] },
    });
    const m = assembleDashboard(raw, GH_OK, NOW_ISO);
    const t = m.tasks.find((x) => x.id === 'M0-T050')!;
    expect(t.accepted).toBe(true);
    expect(t.unmetGates).toEqual([]);
    expect(t.passedGates).toEqual(['G3', 'G4']);
    expect(m.issues.some((i) => i.code === 'roster.contradiction')).toBe(false);
  });
});

describe('health is independent of completion (owner directive #3)', () => {
  it('a system with an accepted task can still be RED (blocked + open blocker)', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    const sysB = m.systems.find((s) => s.id === 'sys_b')!;
    expect(sysB.acceptedCount).toBe(1);
    expect(sysB.health).toBe('RED');
    // completion is unchanged by health
    expect(sysB.engCompletion).toBeCloseTo(0.5, 6);
  });

  it('failed CI degrades health without changing completion', () => {
    const ok = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    const failing: GitHubStatus = { available: true, stale: false, ci: parseCiRuns(ghRunsFailure) };
    const bad = assembleDashboard(synthRaw(), failing, NOW_ISO);
    expect(bad.health.overall).toBe('RED');
    expect(bad.engineering.exactPercent).toBe(ok.engineering.exactPercent);
    expect(bad.launch.exactPercent).toBe(ok.launch.exactPercent);
  });
});

describe('UNKNOWN / DEGRADED is never coerced (owner directive #4)', () => {
  it('an unrecognized task status makes its system UNKNOWN and the headline null', () => {
    const tasks = JSON.parse(JSON.stringify(synthRaw().tasks));
    tasks[0].status = 'weird_status';
    const m = assembleDashboard(synthRaw({ tasks }), GH_OK, NOW_ISO);
    const sysA = m.systems.find((s) => s.id === 'sys_a')!;
    expect(sysA.engCompletion).toBeNull();
    expect(sysA.dataQuality).toBe('unknown');
    expect(m.engineering.dataQuality).toBe('partial');
    expect(m.engineering.percentWhole).toBeNull();
    expect(m.engineering.unverifiedWeight).toBe(50);
    expect(m.issues.some((i) => i.code === 'task.status.unknown')).toBe(true);
  });

  it('missing product-map + empty ledger => UNKNOWN, no fabricated number, no throw', () => {
    const empty: RawControlPlane = {
      tasks: [], masterPlan: null, state: null, config: null,
      gates: [], blockers: [], checkpoints: [], productMap: null,
    };
    const m = assembleDashboard(empty, undefined, NOW_ISO);
    expect(m.dataQuality).toBe('unknown');
    expect(m.engineering.percentWhole).toBeNull();
    expect(m.launch.percentWhole).toBeNull();
    expect(m.issues.length).toBeGreaterThan(0);
  });

  it('flags a roster vs task-file contradiction (owner directive #8)', () => {
    const state = { ...synthRaw().state as object, accepted_tasks: ['M0-T001', 'M1-T001', 'M0-T002'] };
    const m = assembleDashboard(synthRaw({ state }), GH_OK, NOW_ISO);
    expect(m.issues.some((i) => i.code === 'roster.contradiction' && i.ref === 'M0-T002')).toBe(true);
  });
});

describe('blockers, current work, activity, launch blockers', () => {
  it('surfaces only open blockers with owner labels', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    expect(m.openBlockers.map((b) => b.id)).toEqual(['B-900']);
    expect(m.openBlockers[0].ownerLabel).toContain('demo credential');
    expect(m.openBlockers[0].affectedSystemIds).toContain('sys_b');
  });

  it('derives current work from lifecycle, not commits; picks a deterministic primary', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    expect(m.currentWork.activeTasks.map((t) => t.id)).toEqual(['M0-T002']);
    expect(m.currentWork.primary?.id).toBe('M0-T002');
  });

  it('activity is a control-plane event model with a deterministic "today"', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    const today = m.activity.filter((e) => e.today).map((e) => e.kind).sort();
    expect(today).toEqual(['gate_pass', 'task_accepted', 'task_started']);
    expect(m.activity.some((e) => e.kind === 'pr_merged')).toBe(true);
    // activity is a control-plane event model (no raw-commit kinds)
    const allowedKinds = ['task_accepted', 'task_started', 'gate_pass', 'gate_fail', 'pr_merged', 'blocker_opened', 'blocker_resolved', 'checkpoint'];
    expect(m.activity.every((e) => allowedKinds.includes(e.kind))).toBe(true);
  });

  it('biggest-things-preventing-beta is deterministic and derived, not invented', () => {
    const m = assembleDashboard(synthRaw(), GH_OK, NOW_ISO);
    const kinds = Object.fromEntries(m.launchBlockers.map((x) => [x.systemId ?? x.label, x.kind]));
    expect(kinds['sys_b']).toBe('unmet_gate');
    expect(kinds['sys_a']).toBe('system_incomplete');
    expect(m.launchBlockers.some((x) => x.kind === 'open_blocker')).toBe(true);
    // ranks are 1..n unique and ascending
    expect(m.launchBlockers.map((x) => x.rank)).toEqual(m.launchBlockers.map((_, i) => i + 1));
  });
});

describe('GitHub parsers + client (supplemental only)', () => {
  it('parses head SHA, merged PRs, and CI conclusion', () => {
    expect(parseHeadSha(ghCommitMain)).toBe('deadbeefcafef00d1234567890abcdef12345678');
    expect(parsePrs(ghPullsClosed, { mergedOnly: true }).map((p) => p.number)).toEqual([82]);
    expect(parseCiRuns(ghRunsSuccess).conclusion).toBe('success');
    expect(parseCiRuns(ghRunsFailure).conclusion).toBe('failure');
  });

  beforeEach(() => __resetGitHubCache());

  it('falls back to last-known marked STALE on fetch failure', async () => {
    const ok: FetchImpl = async (url) => ({
      ok: true, status: 200,
      json: async () => (url.includes('/commits/') ? ghCommitMain
        : url.includes('/actions/runs') ? ghRunsSuccess
        : url.includes('state=closed') ? ghPullsClosed : []),
    }) as unknown as Response;
    const first = await fetchGitHubStatus({ fetchImpl: ok, noCache: true, nowMs: 1000 });
    expect(first.available).toBe(true);
    expect(first.stale).toBe(false);

    const fail: FetchImpl = async () => { throw new Error('network down'); };
    const second = await fetchGitHubStatus({ fetchImpl: fail, noCache: true, nowMs: 2000 });
    expect(second.stale).toBe(true);
    expect(second.available).toBe(false);
    expect(second.headSha).toBe(first.headSha); // last-known retained, never fabricated
  });
});

describe('internal flag (fail-safe off)', () => {
  it('is disabled unless an explicit true token is set', () => {
    expect(dashboardEnabled({})).toBe(false);
    expect(dashboardEnabled({ INTERNAL_OWNER_DASHBOARD_ENABLED: '0' })).toBe(false);
    expect(dashboardEnabled({ INTERNAL_OWNER_DASHBOARD_ENABLED: 'nope' })).toBe(false);
    expect(dashboardEnabled({ INTERNAL_OWNER_DASHBOARD_ENABLED: '1' })).toBe(true);
    expect(dashboardEnabled({ INTERNAL_OWNER_DASHBOARD_ENABLED: 'true' })).toBe(true);
  });
});

describe('real ledger smoke (runs against committed project-control)', () => {
  it('assembles the real control plane without throwing', async () => {
    const { loadControlPlane } = await import('@/lib/dashboard/loader.server');
    const raw = await loadControlPlane();
    const m = assembleDashboard(raw, undefined, NOW_ISO);
    expect(m.systems.length).toBe(10);
    expect(m.engineering.breakdown.length).toBe(10);
    expect(['ok', 'partial']).toContain(m.dataQuality);
    if (m.dataQuality === 'ok') {
      expect(typeof m.engineering.percentWhole).toBe('number');
      expect(typeof m.launch.percentWhole).toBe('number');
    }
  });
});
