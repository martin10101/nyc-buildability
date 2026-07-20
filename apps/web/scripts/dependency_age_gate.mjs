#!/usr/bin/env node
// Machine-enforced npm dependency release-age gate (task M0-T019, FE-S9/FE-S11).
//
// Enforces the owner's permanent dependency-admission rule for the npm tree: every
// registry package version admitted by the COMMITTED apps/web/package-lock.json --
// direct, transitive, dev, test, build, optional, scoped, and platform-specific --
// must have been published to the official npm registry at least MIN_AGE_SECONDS
// (604800 s = 7 days) ago, and the lock's committed integrity for each version must
// match the registry's own dist.integrity for that version.
//
// WHY THIS EXISTS (the gap it closes): apps/web/.npmrc `min-release-age=7` only
// filters versions while npm RESOLVES/regenerates the lock. CI installs the
// committed lock with `npm ci`, which does NOT resolve -- so a hand-edited lock
// could smuggle a <7-day (or forged-integrity) package past `npm ci` + `npm audit`.
// This gate independently validates the committed lock, fail-closed, and is the
// authoritative age enforcement. It is the npm parallel of the accepted Python
// services/api/scripts/dependency_age_gate.py.
//
// DESIGN (mirrors the Python reference):
//   * The live gate uses the CURRENT UTC instant taken from the npm registry's own
//     HTTP `Date` response header (not the local clock, not a cached table), and
//     official LIVE registry packument metadata queried per package.
//   * Age is read from the packument `time[version]` publication timestamp.
//   * The lock's committed integrity MUST equal the registry
//     versions[version].dist.integrity (anti-forgery: a hand-edited lock cannot
//     claim an old version while shipping a different artifact).
//   * The comparison is full-instant integer-second arithmetic; exactly 604800 s
//     PASSES, 604799 s FAILS. No date-only or truncated-day math.
//   * The gate FAILS CLOSED (exit 1, package marked FAIL, never skipped/passed) on:
//     registry outage / network error, a missing/malformed publication timestamp,
//     a malformed lock entry, a missing integrity, an integrity mismatch, a
//     `resolved` host that is not exactly registry.npmjs.org, or any otherwise
//     ambiguous result.
//   * FE-S11: the pinned npm CLI tooling version is independently checked for
//     advisories (OSV) and for age (>= 7 days) and fails the run on any advisory or
//     if it is too new / unverifiable.
//   * There is NO agent-created exception path anywhere -- no allowlist, no
//     suppression, no --ignore. Any emergency age-only exception is an owner action
//     taken OUTSIDE this tool; this module never reads an allowlist or suppression
//     file.
//
// Network access is confined to `RegistryClient`; the pure logic (`parseLock`,
// `decide`, `evaluateLock`, `checkNpmTooling`) takes an injectable `now` and
// injectable providers so the unit tests are deterministic and offline.
//
// Usage:
//   node dependency_age_gate.mjs <package-lock.json path> --npm-tooling-version <ver>
//
// Exit code 0 iff every registry package in the lock is at least seven days old
// (with matching integrity) AND the npm tooling passes; 1 otherwise (including any
// fail-closed condition). Node built-ins only -- no npm dependencies, zero install.

import { readFileSync } from 'node:fs';
import process from 'node:process';

export const MIN_AGE_SECONDS = 604800; // 7 days; exactly this PASSES, one second less FAILS.
const REGISTRY_HOST = 'registry.npmjs.org';
const REGISTRY_ROOT = 'https://registry.npmjs.org/';
const OSV_QUERY_URL = 'https://api.osv.dev/v1/query';
const HTTP_TIMEOUT_MS = 30000;
const LIVE_CONCURRENCY = 10;

// A fail-closed condition (outage, missing/malformed metadata, integrity mismatch,
// unexpected host, ambiguous result). Distinct class so evaluateLock can convert a
// per-package failure into a FAIL result while a programming error would surface.
export class AgeGateError extends Error {
  constructor(message) {
    super(message);
    this.name = 'AgeGateError';
  }
}

// --------------------------------------------------------------------------- //
// Lock parsing (pure)
// --------------------------------------------------------------------------- //

// Derive the package name from a lockfileVersion-3 `packages` key such as
// "node_modules/@next/swc-linux-x64-gnu" or
// "node_modules/foo/node_modules/lru-cache": take the segment after the LAST
// "node_modules/", preserving a leading "@scope/".
function _nameFromPath(pkgPath) {
  const marker = 'node_modules/';
  const idx = pkgPath.lastIndexOf(marker);
  if (idx === -1) {
    throw new AgeGateError(`lock entry key is not a node_modules path: ${pkgPath}`);
  }
  const tail = pkgPath.slice(idx + marker.length);
  if (!tail) {
    throw new AgeGateError(`lock entry key has empty package name: ${pkgPath}`);
  }
  if (tail.startsWith('@')) {
    // Scoped: "@scope/name" -- keep exactly the scope + first path segment.
    const parts = tail.split('/');
    if (parts.length < 2 || !parts[0] || !parts[1]) {
      throw new AgeGateError(`malformed scoped package name in lock key: ${pkgPath}`);
    }
    return `${parts[0]}/${parts[1]}`;
  }
  // Unscoped: the first segment is the name (guards against any stray subpath).
  return tail.split('/')[0];
}

// Validate that a `resolved` URL is exactly the official registry host. Fail-closed
// on any other host (mirror registry, tarball URL, git/file/link ref).
function _requireRegistryHost(resolved, pkgKey) {
  let host;
  try {
    host = new URL(resolved).host;
  } catch (err) {
    throw new AgeGateError(`lock entry ${pkgKey} has an unparseable resolved URL: ${resolved}`);
  }
  if (host !== REGISTRY_HOST) {
    throw new AgeGateError(
      `lock entry ${pkgKey} resolves to unexpected host ${host} (must be ${REGISTRY_HOST})`,
    );
  }
}

/**
 * Parse a lockfileVersion-3 package-lock object into the unique registry packages.
 *
 * Enumerates EVERY entry in `packages` whose key starts with "node_modules/" and
 * carries a `resolved` URL (these are registry packages of every class). Skips the
 * root entry "" and any link/workspace entry that has no `resolved`. FAILS CLOSED
 * if a registry entry (one that has `resolved`) is missing `integrity` or
 * `version`, or if its `resolved` host is not exactly registry.npmjs.org. Dedupes
 * by `name@version` (a version pinned at multiple tree positions is one wait).
 *
 * @param {object} lockObject parsed package-lock.json
 * @returns {{name:string, version:string, resolved:string, integrity:string}[]}
 */
export function parseLock(lockObject) {
  if (!lockObject || typeof lockObject !== 'object') {
    throw new AgeGateError('package-lock.json did not parse to an object');
  }
  const packages = lockObject.packages;
  if (!packages || typeof packages !== 'object') {
    throw new AgeGateError('package-lock.json has no "packages" object (lockfileVersion >= 2/3 required)');
  }
  const byKey = new Map(); // name@version -> record
  for (const [pkgKey, entry] of Object.entries(packages)) {
    if (pkgKey === '') {
      continue; // the workspace root is not a registry package
    }
    if (!pkgKey.startsWith('node_modules/')) {
      continue; // defensive: only node_modules entries are dependency packages
    }
    if (!entry || typeof entry !== 'object') {
      throw new AgeGateError(`lock entry ${pkgKey} is not an object`);
    }
    const resolved = entry.resolved;
    if (resolved === undefined || resolved === null || resolved === '') {
      // link:/file:/workspace entry -- not a registry download; skip (no age to gate).
      continue;
    }
    if (typeof resolved !== 'string') {
      throw new AgeGateError(`lock entry ${pkgKey} has a non-string resolved`);
    }
    _requireRegistryHost(resolved, pkgKey);
    const version = entry.version;
    if (typeof version !== 'string' || version === '') {
      throw new AgeGateError(`registry lock entry ${pkgKey} is missing a version`);
    }
    const integrity = entry.integrity;
    if (typeof integrity !== 'string' || integrity === '') {
      throw new AgeGateError(`registry lock entry ${pkgKey} is missing integrity`);
    }
    const name = _nameFromPath(pkgKey);
    const dedupeKey = `${name}@${version}`;
    if (!byKey.has(dedupeKey)) {
      byKey.set(dedupeKey, { name, version, resolved, integrity });
    } else {
      // Same name@version at another tree position must carry the SAME committed
      // integrity; a divergence is a tampered/inconsistent lock -> fail closed.
      const prior = byKey.get(dedupeKey);
      if (prior.integrity !== integrity) {
        throw new AgeGateError(
          `lock has conflicting integrity for ${dedupeKey}: ${prior.integrity} vs ${integrity}`,
        );
      }
    }
  }
  return [...byKey.values()];
}

// --------------------------------------------------------------------------- //
// Live registry / OSV access (the only networked surface)
// --------------------------------------------------------------------------- //
export class RegistryClient {
  // `fetchImpl` is injectable purely so a networked integration test could stub it;
  // the deterministic unit tests never construct a RegistryClient -- they inject the
  // pure providers below. Defaults to the global fetch (Node >= 18).
  constructor(fetchImpl = fetch) {
    this._fetch = fetchImpl;
  }

  async _get(url, init) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), HTTP_TIMEOUT_MS);
    try {
      return await this._fetch(url, { ...init, signal: controller.signal });
    } catch (err) {
      throw new AgeGateError(`network error fetching ${url}: ${err.message}`);
    } finally {
      clearTimeout(timer);
    }
  }

  // Authoritative current UTC in ms from the registry's own Date header (mirror of
  // the Python utc_now). Fail-closed if the header is missing or unparseable.
  async utcNow() {
    const resp = await this._get(REGISTRY_ROOT, { method: 'HEAD' });
    if (!resp || !resp.ok) {
      throw new AgeGateError(
        `registry HEAD for the UTC clock failed with status ${resp && resp.status}`,
      );
    }
    const dateHdr = resp.headers && resp.headers.get('date');
    if (!dateHdr) {
      throw new AgeGateError('registry response carried no Date header for the UTC clock');
    }
    const ms = Date.parse(dateHdr);
    if (Number.isNaN(ms)) {
      throw new AgeGateError(`malformed registry Date header: ${dateHdr}`);
    }
    return ms;
  }

  // GET the packument for a package (URL-encoding a scoped name's "/" as %2f).
  // Returns the parsed JSON (with `time` and `versions`). Fail-closed on any error.
  async packument(name) {
    const encoded = name.startsWith('@') ? name.replace('/', '%2f') : name;
    const url = `${REGISTRY_ROOT}${encoded}`;
    const resp = await this._get(url);
    if (!resp || !resp.ok) {
      throw new AgeGateError(`packument fetch for ${name} failed with status ${resp && resp.status}`);
    }
    let json;
    try {
      json = await resp.json();
    } catch (err) {
      throw new AgeGateError(`packument for ${name} did not parse as JSON: ${err.message}`);
    }
    if (!json || typeof json !== 'object') {
      throw new AgeGateError(`packument for ${name} was not a JSON object`);
    }
    return json;
  }

  // POST an OSV query for one npm package version. Returns the vulns array (empty
  // when OSV reports no advisories -- OSV omits `vulns` entirely in that case).
  // Fail-closed on network error, non-OK status, or unparseable body.
  async advisories(name, version) {
    const resp = await this._get(OSV_QUERY_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ package: { ecosystem: 'npm', name }, version }),
    });
    if (!resp || !resp.ok) {
      throw new AgeGateError(`OSV query for ${name}@${version} failed with status ${resp && resp.status}`);
    }
    let json;
    try {
      json = await resp.json();
    } catch (err) {
      throw new AgeGateError(`OSV response for ${name}@${version} did not parse as JSON: ${err.message}`);
    }
    if (json && json.vulns !== undefined && !Array.isArray(json.vulns)) {
      throw new AgeGateError(`OSV response for ${name}@${version} had a non-array vulns field`);
    }
    return json && Array.isArray(json.vulns) ? json.vulns : [];
  }
}

// --------------------------------------------------------------------------- //
// Core decision logic (pure; deterministic under injected now + providers)
// --------------------------------------------------------------------------- //

function _publishedMsFromPackument(packument, version) {
  const time = packument && packument.time;
  if (!time || typeof time !== 'object') {
    throw new AgeGateError('packument has no "time" object');
  }
  const raw = time[version];
  if (!raw || typeof raw !== 'string') {
    throw new AgeGateError(`packument time has no publication timestamp for version ${version}`);
  }
  const ms = Date.parse(raw);
  if (Number.isNaN(ms)) {
    throw new AgeGateError(`malformed publication timestamp ${raw} for version ${version}`);
  }
  return ms;
}

function _registryIntegrityFromPackument(packument, version) {
  const versions = packument && packument.versions;
  if (!versions || typeof versions !== 'object') {
    throw new AgeGateError('packument has no "versions" object');
  }
  const entry = versions[version];
  if (!entry || typeof entry !== 'object') {
    throw new AgeGateError(`packument has no version entry for ${version}`);
  }
  const integrity = entry.dist && entry.dist.integrity;
  if (typeof integrity !== 'string' || integrity === '') {
    throw new AgeGateError(`packument version ${version} has no dist.integrity`);
  }
  return integrity;
}

/**
 * Decide PASS/FAIL for one committed lock package against its registry packument.
 *
 * Reads the publication timestamp from `packument.time[version]` (fail-closed if
 * missing/malformed); requires the registry `dist.integrity` for that version to
 * EQUAL the lock's committed integrity (anti-forgery -- fail-closed if missing or
 * mismatched); computes `ageSeconds = floor((nowMs - publishedMs)/1000)`; passes
 * iff `ageSeconds >= MIN_AGE_SECONDS`. Any thrown condition is caller-converted to
 * a FAIL (never a skip/pass).
 *
 * @param {{name:string,version:string,integrity:string}} pkg
 * @param {object} packument
 * @param {number} nowMs
 * @returns {{name,version,publishedMs,ageSeconds,passed,reason}}
 */
export function decide(pkg, packument, nowMs) {
  const publishedMs = _publishedMsFromPackument(packument, pkg.version);
  const registryIntegrity = _registryIntegrityFromPackument(packument, pkg.version);
  if (registryIntegrity !== pkg.integrity) {
    throw new AgeGateError(
      `integrity mismatch for ${pkg.name}@${pkg.version}: lock=${pkg.integrity} registry=${registryIntegrity}`,
    );
  }
  const ageSeconds = Math.floor((nowMs - publishedMs) / 1000);
  const passed = ageSeconds >= MIN_AGE_SECONDS;
  const reason = passed ? '' : `published ${ageSeconds}s ago; requires >= ${MIN_AGE_SECONDS}s`;
  return { name: pkg.name, version: pkg.version, publishedMs, ageSeconds, passed, reason };
}

// Run an async worker over items with bounded concurrency, preserving input order
// in the returned results array. Used only for the live provider over ~500
// packages; the deterministic tests pass small inputs.
async function _mapWithConcurrency(items, limit, worker) {
  const results = new Array(items.length);
  let next = 0;
  const runners = new Array(Math.min(limit, items.length)).fill(0).map(async () => {
    while (true) {
      const i = next++;
      if (i >= items.length) return;
      results[i] = await worker(items[i], i);
    }
  });
  await Promise.all(runners);
  return results;
}

/**
 * Evaluate every unique registry package from a parsed lock.
 *
 * Fetches each packument once via `packumentProvider(name)` (cached by name so a
 * name pinned at several versions still fetches one packument). A fail-closed
 * error for a single package is captured as a FAIL result for that package (the run
 * still fails) rather than aborting the report, so every problem is listed. Uses
 * bounded concurrency so the live run over ~500 packages stays fast.
 *
 * @param {{name,version,integrity}[]} packages
 * @param {(name:string)=>Promise<object>|object} packumentProvider
 * @param {number} nowMs
 * @returns {Promise<{name,version,publishedMs,ageSeconds,passed,reason}[]>}
 */
export async function evaluateLock(packages, packumentProvider, nowMs) {
  const packumentCache = new Map(); // name -> Promise<packument>
  const getPackument = (name) => {
    if (!packumentCache.has(name)) {
      packumentCache.set(name, Promise.resolve().then(() => packumentProvider(name)));
    }
    return packumentCache.get(name);
  };
  return _mapWithConcurrency(packages, LIVE_CONCURRENCY, async (pkg) => {
    try {
      const packument = await getPackument(pkg.name);
      return decide(pkg, packument, nowMs);
    } catch (err) {
      const message = err instanceof AgeGateError ? err.message : `unexpected error: ${err.message}`;
      return {
        name: pkg.name,
        version: pkg.version,
        publishedMs: null,
        ageSeconds: null,
        passed: false,
        reason: message,
      };
    }
  });
}

/**
 * FE-S11: verify the pinned npm CLI tooling version has ZERO advisories AND is at
 * least MIN_AGE_SECONDS old. Fail-closed on any error (advisory-source outage,
 * missing/malformed timestamp). No suppression / allowlist.
 *
 * @param {string} npmVersion e.g. "11.18.0"
 * @param {(name:string)=>Promise<object>|object} packumentProvider provides the npm packument
 * @param {(name:string,version:string)=>Promise<any[]>|any[]} advisoryProvider OSV vulns for npm@version
 * @param {number} nowMs
 * @returns {Promise<{passed:boolean, reason:string}>}
 */
export async function checkNpmTooling(npmVersion, packumentProvider, advisoryProvider, nowMs) {
  if (typeof npmVersion !== 'string' || npmVersion === '') {
    return { passed: false, reason: 'no npm tooling version supplied' };
  }
  try {
    const vulns = await advisoryProvider('npm', npmVersion);
    if (!Array.isArray(vulns)) {
      throw new AgeGateError('advisory provider returned a non-array for npm');
    }
    if (vulns.length > 0) {
      const ids = vulns.map((v) => (v && v.id) || '?').join(', ');
      return { passed: false, reason: `npm@${npmVersion} has ${vulns.length} advisory(ies): ${ids}` };
    }
    const packument = await packumentProvider('npm');
    const publishedMs = _publishedMsFromPackument(packument, npmVersion);
    const ageSeconds = Math.floor((nowMs - publishedMs) / 1000);
    if (ageSeconds < MIN_AGE_SECONDS) {
      return {
        passed: false,
        reason: `npm@${npmVersion} published ${ageSeconds}s ago; requires >= ${MIN_AGE_SECONDS}s`,
      };
    }
    return { passed: true, reason: `npm@${npmVersion} advisory-free, age ${ageSeconds}s` };
  } catch (err) {
    const message = err instanceof AgeGateError ? err.message : `unexpected error: ${err.message}`;
    return { passed: false, reason: `fail-closed checking npm@${npmVersion}: ${message}` };
  }
}

// --------------------------------------------------------------------------- //
// Reporting / CLI
// --------------------------------------------------------------------------- //
function _formatResult(r) {
  const uploaded = r.publishedMs !== null && r.publishedMs !== undefined
    ? new Date(r.publishedMs).toISOString()
    : '-';
  const age = r.ageSeconds !== null && r.ageSeconds !== undefined
    ? `${r.ageSeconds}s (${(r.ageSeconds / 86400).toFixed(2)}d)`
    : '-';
  const verdict = r.passed ? 'PASS' : 'FAIL';
  const tail = r.passed ? '' : `  [${r.reason}]`;
  return `${verdict}  ${r.name}@${r.version}  uploaded=${uploaded}  age=${age}${tail}`;
}

function _parseArgs(argv) {
  const args = { lockPath: undefined, npmToolingVersion: undefined };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === '--npm-tooling-version') {
      args.npmToolingVersion = argv[i + 1];
      i += 1;
    } else if (a.startsWith('--npm-tooling-version=')) {
      args.npmToolingVersion = a.slice('--npm-tooling-version='.length);
    } else if (!a.startsWith('--') && args.lockPath === undefined) {
      args.lockPath = a;
    }
  }
  return args;
}

/**
 * CLI entry: read the committed lock, take `now` from the registry Date header
 * (fail-closed), evaluate every registry package, and check the npm tooling.
 * Returns the intended process exit code (0 iff every package AND the tooling
 * pass). No allowlist / suppression / exception path.
 */
export async function main(argv, client) {
  const args = _parseArgs(argv);
  if (!args.lockPath) {
    process.stderr.write('usage: node dependency_age_gate.mjs <package-lock.json> --npm-tooling-version <ver>\n');
    return 1;
  }
  const registry = client || new RegistryClient();

  let nowMs;
  try {
    nowMs = await registry.utcNow();
  } catch (err) {
    process.stderr.write(`FAIL-CLOSED: ${err.message}\n`);
    return 1;
  }

  let packages;
  try {
    const lockObject = JSON.parse(readFileSync(args.lockPath, 'utf8'));
    packages = parseLock(lockObject);
  } catch (err) {
    process.stderr.write(`FAIL-CLOSED: cannot read/parse lock ${args.lockPath}: ${err.message}\n`);
    return 1;
  }

  process.stdout.write(
    `npm committed-lockfile release-age gate  (now=${new Date(nowMs).toISOString()}, min_age=${MIN_AGE_SECONDS}s)\n`,
  );
  process.stdout.write(`== ${args.lockPath}  (${packages.length} registry packages) ==\n`);

  const results = await evaluateLock(packages, (name) => registry.packument(name), nowMs);
  let overallOk = true;
  for (const r of [...results].sort((a, b) => (a.name === b.name ? a.version.localeCompare(b.version) : a.name.localeCompare(b.name)))) {
    process.stdout.write('  ' + _formatResult(r) + '\n');
    overallOk = overallOk && r.passed;
  }

  const tooling = await checkNpmTooling(
    args.npmToolingVersion,
    (name) => registry.packument(name),
    (name, version) => registry.advisories(name, version),
    nowMs,
  );
  process.stdout.write(`\nnpm CLI tooling: ${tooling.passed ? 'PASS' : 'FAIL'}  ${tooling.reason}\n`);
  overallOk = overallOk && tooling.passed;

  process.stdout.write(
    '\nRESULT: ' +
    (overallOk
      ? 'PASS — every committed lock package is >= 7 days old with matching integrity, and npm tooling is advisory-free and >= 7 days old\n'
      : 'FAIL — at least one package is too new, has mismatched integrity, could not be verified, or the npm tooling failed\n'),
  );
  return overallOk ? 0 : 1;
}

// Only run the CLI when executed directly (not when imported by the tests).
const _invokedPath = process.argv[1] ? process.argv[1].replace(/\\/g, '/') : '';
if (_invokedPath.endsWith('dependency_age_gate.mjs')) {
  main(process.argv.slice(2))
    .then((code) => process.exit(code))
    .catch((err) => {
      process.stderr.write(`FAIL-CLOSED (unexpected): ${err && err.message}\n`);
      process.exit(1);
    });
}
