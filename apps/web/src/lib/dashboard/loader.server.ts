// Server-only edge: read project-control/*.json off disk into RawControlPlane.
// Uses Node built-ins only (fs/path) -> importing this from a client component
// fails at build, which is the guard we want. NEVER imported by the pure engine
// tests. Read-only: it only reads files; it never writes or runs the CLI.

import { promises as fs } from 'node:fs';
import path from 'node:path';
import type { RawControlPlane, Issue } from './types';

/** Walk up from a starting dir to find the repo root (the dir with project-control/). */
export async function findControlPlaneDir(startDir: string = process.cwd()): Promise<string | null> {
  let dir = path.resolve(startDir);
  for (let i = 0; i < 8; i++) {
    const candidate = path.join(dir, 'project-control');
    try {
      const stat = await fs.stat(path.join(candidate, 'master_plan.json'));
      if (stat.isFile()) return candidate;
    } catch {
      // keep walking up
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

async function readJson(file: string): Promise<unknown> {
  const text = await fs.readFile(file, 'utf-8');
  // strip a possible UTF-8 BOM
  return JSON.parse(text.replace(/^﻿/, ''));
}

async function readJsonDir(dir: string, filter: (name: string) => boolean): Promise<{ items: unknown[]; issues: Issue[] }> {
  const items: unknown[] = [];
  const issues: Issue[] = [];
  let names: string[] = [];
  try {
    names = (await fs.readdir(dir)).filter(filter).sort();
  } catch {
    return { items, issues };
  }
  for (const name of names) {
    try {
      items.push(await readJson(path.join(dir, name)));
    } catch (e) {
      issues.push({
        code: 'file.unparseable',
        message: `Could not parse ${name}: ${(e as Error).message}`,
        severity: 'error',
        ref: name,
      });
    }
  }
  return { items, issues };
}

/** Load the full control plane, never throwing. Missing/corrupt files -> fileIssues. */
export async function loadControlPlane(startDir?: string): Promise<RawControlPlane> {
  const fileIssues: Issue[] = [];
  const pcDir = await findControlPlaneDir(startDir);
  if (!pcDir) {
    return {
      tasks: [], masterPlan: null, state: null, config: null,
      gates: [], blockers: [], checkpoints: [], productMap: null,
      fileIssues: [{
        code: 'control_plane.not_found',
        message: 'Could not locate project-control/ from the current working directory.',
        severity: 'error',
      }],
    };
  }

  const single = async (rel: string): Promise<unknown> => {
    try {
      return await readJson(path.join(pcDir, rel));
    } catch (e) {
      fileIssues.push({
        code: 'file.missing_or_unparseable',
        message: `Could not read ${rel}: ${(e as Error).message}`,
        severity: rel === 'product-map.json' || rel === 'master_plan.json' ? 'error' : 'warn',
        ref: rel,
      });
      return null;
    }
  };

  const isJson = (n: string) => n.endsWith('.json');
  const tasks = await readJsonDir(path.join(pcDir, 'tasks'), isJson);
  const gates = await readJsonDir(path.join(pcDir, 'gates'), isJson);
  const blockers = await readJsonDir(path.join(pcDir, 'blockers'), isJson);
  const checkpoints = await readJsonDir(path.join(pcDir, 'checkpoints'), (n) => /^CP-.*\.json$/.test(n));

  fileIssues.push(...tasks.issues, ...gates.issues, ...blockers.issues, ...checkpoints.issues);

  const [masterPlan, state, config, productMap] = await Promise.all([
    single('master_plan.json'),
    single('state.json'),
    single('config.json'),
    single('product-map.json'),
  ]);

  return {
    tasks: tasks.items,
    masterPlan, state, config, productMap,
    gates: gates.items,
    blockers: blockers.items,
    checkpoints: checkpoints.items,
    fileIssues,
  };
}
