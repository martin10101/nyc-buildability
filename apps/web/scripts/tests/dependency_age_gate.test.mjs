// Deterministic, offline unit tests for the npm committed-lockfile release-age
// gate (task M0-T019, FE-S9 boundary + fail-closed + enumeration, FE-S11 tooling).
//
// Every test injects a fixed UTC `now` (ms) and synthetic packument / advisory
// providers, so nothing here touches the network. The live behaviour (real
// registry Date header + real packuments + OSV) is exercised by the CI gate job
// over the real committed lock; these tests pin the LOGIC: the 604800/604799
// boundary, the integrity-match anti-forgery check, the enumeration/dedupe of the
// `packages` map, that every fail-closed branch FAILS (never skips or passes), and
// the npm tooling advisory + age check.
//
// Built-in runner only (no npm deps): run with `node --test`.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  MIN_AGE_SECONDS,
  AgeGateError,
  parseLock,
  decide,
  evaluateLock,
  checkNpmTooling,
} from '../dependency_age_gate.mjs';

// A fixed "now": 2026-07-20T12:00:00.000Z.
const NOW_MS = Date.parse('2026-07-20T12:00:00.000Z');
const INTEGRITY_A = 'sha512-' + 'A'.repeat(80) + '==';
const INTEGRITY_B = 'sha512-' + 'B'.repeat(80) + '==';

function uploadedSecondsAgoIso(seconds) {
  return new Date(NOW_MS - seconds * 1000).toISOString();
}

// Build a minimal packument with one version's time + dist.integrity.
function packumentFor(version, uploadedIso, integrity) {
  return {
    time: { [version]: uploadedIso },
    versions: { [version]: { dist: { integrity } } },
  };
}

function lockPkg(name, version, integrity, resolved) {
  return {
    name,
    version,
    integrity,
    resolved: resolved || `https://registry.npmjs.org/${name}/-/${name}-${version}.tgz`,
  };
}

// --------------------------------------------------------------------------- //
// Boundary: exactly 604800 s PASSES; 604799 s FAILS (the critical proof, FE-S9)
// --------------------------------------------------------------------------- //
test('age exactly 604800 s passes (boundary)', () => {
  const pkg = lockPkg('demo', '1.0.0', INTEGRITY_A);
  const pack = packumentFor('1.0.0', uploadedSecondsAgoIso(MIN_AGE_SECONDS), INTEGRITY_A);
  const r = decide(pkg, pack, NOW_MS);
  assert.equal(r.passed, true);
  assert.equal(r.ageSeconds, MIN_AGE_SECONDS);
  assert.equal(r.reason, '');
});

test('age exactly 604799 s fails (boundary)', () => {
  const pkg = lockPkg('demo', '1.0.0', INTEGRITY_A);
  const pack = packumentFor('1.0.0', uploadedSecondsAgoIso(MIN_AGE_SECONDS - 1), INTEGRITY_A);
  const r = decide(pkg, pack, NOW_MS);
  assert.equal(r.passed, false);
  assert.equal(r.ageSeconds, MIN_AGE_SECONDS - 1);
  assert.match(r.reason, /requires >= 604800s/);
});

test('sub-second-fractional age uses integer-second floor (no day rounding)', () => {
  // now - published = 604800 s minus 500 ms => floor gives 604799 => FAIL.
  const pkg = lockPkg('demo', '1.0.0', INTEGRITY_A);
  const uploadedIso = new Date(NOW_MS - (MIN_AGE_SECONDS * 1000 - 500)).toISOString();
  const pack = packumentFor('1.0.0', uploadedIso, INTEGRITY_A);
  const r = decide(pkg, pack, NOW_MS);
  assert.equal(r.ageSeconds, MIN_AGE_SECONDS - 1);
  assert.equal(r.passed, false);
});

// --------------------------------------------------------------------------- //
// Positive
// --------------------------------------------------------------------------- //
test('a several-days-older package passes', () => {
  const pkg = lockPkg('demo', '2.5.0', INTEGRITY_A);
  const pack = packumentFor('2.5.0', uploadedSecondsAgoIso(30 * 86400), INTEGRITY_A);
  assert.equal(decide(pkg, pack, NOW_MS).passed, true);
});

test('a full multi-package lock that is all-old passes overall', async () => {
  const packages = [
    lockPkg('alpha', '1.0.0', INTEGRITY_A),
    lockPkg('@scope/beta', '2.0.0', INTEGRITY_B),
    lockPkg('gamma', '3.1.4', INTEGRITY_A),
  ];
  const provider = (name) => {
    if (name === 'alpha') return packumentFor('1.0.0', uploadedSecondsAgoIso(20 * 86400), INTEGRITY_A);
    if (name === '@scope/beta') return packumentFor('2.0.0', uploadedSecondsAgoIso(15 * 86400), INTEGRITY_B);
    if (name === 'gamma') return packumentFor('3.1.4', uploadedSecondsAgoIso(10 * 86400), INTEGRITY_A);
    throw new AgeGateError(`unexpected ${name}`);
  };
  const results = await evaluateLock(packages, provider, NOW_MS);
  assert.equal(results.length, 3);
  assert.ok(results.every((r) => r.passed === true));
});

// --------------------------------------------------------------------------- //
// Fail-closed branches (FE-S9): none may skip or pass
// --------------------------------------------------------------------------- //
test('missing time[version] fails closed (decide throws)', () => {
  const pkg = lockPkg('demo', '1.0.0', INTEGRITY_A);
  const pack = { time: {}, versions: { '1.0.0': { dist: { integrity: INTEGRITY_A } } } };
  assert.throws(() => decide(pkg, pack, NOW_MS), AgeGateError);
});

test('malformed publication timestamp fails closed (decide throws)', () => {
  const pkg = lockPkg('demo', '1.0.0', INTEGRITY_A);
  const pack = {
    time: { '1.0.0': 'not-a-date' },
    versions: { '1.0.0': { dist: { integrity: INTEGRITY_A } } },
  };
  assert.throws(() => decide(pkg, pack, NOW_MS), AgeGateError);
});

test('missing dist.integrity in the registry packument fails closed (decide throws)', () => {
  const pkg = lockPkg('demo', '1.0.0', INTEGRITY_A);
  const pack = {
    time: { '1.0.0': uploadedSecondsAgoIso(30 * 86400) },
    versions: { '1.0.0': { dist: {} } },
  };
  assert.throws(() => decide(pkg, pack, NOW_MS), AgeGateError);
});

test('integrity mismatch (committed != registry) fails closed (decide throws)', () => {
  const pkg = lockPkg('demo', '1.0.0', INTEGRITY_A);
  // Old enough on time, but the registry integrity differs from the lock's.
  const pack = packumentFor('1.0.0', uploadedSecondsAgoIso(30 * 86400), INTEGRITY_B);
  assert.throws(() => decide(pkg, pack, NOW_MS), AgeGateError);
});

test('lock entry missing integrity fails closed (parseLock throws)', () => {
  const lock = {
    packages: {
      '': { name: 'root' },
      'node_modules/demo': {
        version: '1.0.0',
        resolved: 'https://registry.npmjs.org/demo/-/demo-1.0.0.tgz',
        // no integrity
      },
    },
  };
  assert.throws(() => parseLock(lock), AgeGateError);
});

test('lock entry with unexpected resolved host fails closed (parseLock throws)', () => {
  const lock = {
    packages: {
      '': { name: 'root' },
      'node_modules/demo': {
        version: '1.0.0',
        resolved: 'https://evil.example.com/demo/-/demo-1.0.0.tgz',
        integrity: INTEGRITY_A,
      },
    },
  };
  assert.throws(() => parseLock(lock), AgeGateError);
});

test('packument provider throwing (registry outage) yields a FAIL result, not a skip', async () => {
  const packages = [lockPkg('demo', '1.0.0', INTEGRITY_A)];
  const provider = () => {
    throw new AgeGateError('simulated registry outage');
  };
  const results = await evaluateLock(packages, provider, NOW_MS);
  assert.equal(results.length, 1);
  assert.equal(results[0].passed, false);
  assert.match(results[0].reason, /outage/);
});

test('a too-new package inside an otherwise-old lock makes the whole run FAIL', async () => {
  const packages = [
    lockPkg('old', '1.0.0', INTEGRITY_A),
    lockPkg('fresh', '2.0.0', INTEGRITY_B),
  ];
  const provider = (name) => {
    if (name === 'old') return packumentFor('1.0.0', uploadedSecondsAgoIso(30 * 86400), INTEGRITY_A);
    // 604799 s old -> one second too new.
    return packumentFor('2.0.0', uploadedSecondsAgoIso(MIN_AGE_SECONDS - 1), INTEGRITY_B);
  };
  const results = await evaluateLock(packages, provider, NOW_MS);
  const byName = Object.fromEntries(results.map((r) => [r.name, r]));
  assert.equal(byName.old.passed, true);
  assert.equal(byName.fresh.passed, false);
  assert.ok(results.some((r) => r.passed === false), 'the run must contain a FAIL');
});

// --------------------------------------------------------------------------- //
// Enumeration: parseLock over a realistic lockfileVersion-3 fixture
// --------------------------------------------------------------------------- //
test('parseLock enumerates direct + transitive + scoped + platform entries and dedupes name@version; skips root + resolved-less', () => {
  const lock = {
    name: '@nyc-buildability/web',
    lockfileVersion: 3,
    packages: {
      // root: skipped
      '': { name: '@nyc-buildability/web', version: '0.1.0', dependencies: { next: '15.5.20' } },
      // direct
      'node_modules/next': {
        version: '15.5.20',
        resolved: 'https://registry.npmjs.org/next/-/next-15.5.20.tgz',
        integrity: INTEGRITY_A,
      },
      // scoped platform-specific (optional)
      'node_modules/@next/swc-linux-x64-gnu': {
        version: '15.5.20',
        resolved: 'https://registry.npmjs.org/@next/swc-linux-x64-gnu/-/swc-linux-x64-gnu-15.5.20.tgz',
        integrity: INTEGRITY_B,
      },
      // transitive
      'node_modules/picocolors': {
        version: '1.1.1',
        resolved: 'https://registry.npmjs.org/picocolors/-/picocolors-1.1.1.tgz',
        integrity: INTEGRITY_A,
      },
      // nested transitive (name is the LAST node_modules segment) -- SAME name@version
      // as the top-level lru-cache below, so it must dedupe to one entry.
      'node_modules/@asamuzakjp/css-color/node_modules/lru-cache': {
        version: '10.4.3',
        resolved: 'https://registry.npmjs.org/lru-cache/-/lru-cache-10.4.3.tgz',
        integrity: INTEGRITY_A,
      },
      'node_modules/lru-cache': {
        version: '10.4.3',
        resolved: 'https://registry.npmjs.org/lru-cache/-/lru-cache-10.4.3.tgz',
        integrity: INTEGRITY_A,
      },
      // a workspace/link entry with no resolved: skipped (no age to gate)
      'node_modules/@nyc-buildability/some-workspace': { version: '0.0.0', link: true },
    },
  };
  const pkgs = parseLock(lock);
  const names = pkgs.map((p) => `${p.name}@${p.version}`).sort();
  assert.deepEqual(names, [
    '@next/swc-linux-x64-gnu@15.5.20',
    'lru-cache@10.4.3', // deduped from two positions
    'next@15.5.20',
    'picocolors@1.1.1',
  ]);
  // scoped name preserved exactly
  assert.ok(pkgs.some((p) => p.name === '@next/swc-linux-x64-gnu'));
  // nested transitive derived to the bare package name
  assert.ok(pkgs.some((p) => p.name === 'lru-cache'));
});

test('parseLock fails closed when a registry entry is missing its version', () => {
  const lock = {
    packages: {
      '': { name: 'root' },
      'node_modules/demo': {
        resolved: 'https://registry.npmjs.org/demo/-/demo-1.0.0.tgz',
        integrity: INTEGRITY_A,
        // no version
      },
    },
  };
  assert.throws(() => parseLock(lock), AgeGateError);
});

test('parseLock fails closed when duplicate name@version carry different committed integrity', () => {
  const lock = {
    packages: {
      '': { name: 'root' },
      'node_modules/demo': {
        version: '1.0.0',
        resolved: 'https://registry.npmjs.org/demo/-/demo-1.0.0.tgz',
        integrity: INTEGRITY_A,
      },
      'node_modules/other/node_modules/demo': {
        version: '1.0.0',
        resolved: 'https://registry.npmjs.org/demo/-/demo-1.0.0.tgz',
        integrity: INTEGRITY_B, // conflicting -> tampered/inconsistent lock
      },
    },
  };
  assert.throws(() => parseLock(lock), AgeGateError);
});

// --------------------------------------------------------------------------- //
// Tooling (FE-S11)
// --------------------------------------------------------------------------- //
test('npm tooling with an injected advisory FAILS', async () => {
  const advisoryProvider = () => [{ id: 'GHSA-xxxx-yyyy-zzzz' }];
  const packumentProvider = () => packumentFor('11.18.0', uploadedSecondsAgoIso(30 * 86400), INTEGRITY_A);
  const r = await checkNpmTooling('11.18.0', packumentProvider, advisoryProvider, NOW_MS);
  assert.equal(r.passed, false);
  assert.match(r.reason, /advisory/);
});

test('npm tooling that is advisory-free and old PASSES', async () => {
  const advisoryProvider = () => [];
  const packumentProvider = () => packumentFor('11.18.0', uploadedSecondsAgoIso(21 * 86400), INTEGRITY_A);
  const r = await checkNpmTooling('11.18.0', packumentProvider, advisoryProvider, NOW_MS);
  assert.equal(r.passed, true);
});

test('npm tooling that is advisory-free but too new FAILS (age)', async () => {
  const advisoryProvider = () => [];
  const packumentProvider = () => packumentFor('11.18.0', uploadedSecondsAgoIso(MIN_AGE_SECONDS - 1), INTEGRITY_A);
  const r = await checkNpmTooling('11.18.0', packumentProvider, advisoryProvider, NOW_MS);
  assert.equal(r.passed, false);
  assert.match(r.reason, /requires >= 604800s/);
});

test('npm tooling advisory provider throwing fails closed (FAIL, not skip)', async () => {
  const advisoryProvider = () => {
    throw new AgeGateError('OSV outage');
  };
  const packumentProvider = () => packumentFor('11.18.0', uploadedSecondsAgoIso(30 * 86400), INTEGRITY_A);
  const r = await checkNpmTooling('11.18.0', packumentProvider, advisoryProvider, NOW_MS);
  assert.equal(r.passed, false);
  assert.match(r.reason, /fail-closed/);
});
