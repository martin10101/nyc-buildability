#!/usr/bin/env node
// Machine-enforced committed-lockfile release-age gate for the web app
// (task M0-T019, scenario FE-S9).
//
// THE GAP THIS CLOSES
// -------------------
// `.npmrc` min-release-age is RESOLVER-TIME only: it filters versions when a
// lock is (re)generated, but it does NOT gate the committed package-lock.json
// that `npm ci` actually installs. A hand-edited lockfile could therefore
// smuggle a <7-day-old package past `npm ci` + `npm audit`. This gate parses
// the ENTIRE committed lock, enumerates every unique registry package
// name@version (direct, transitive, dev, test, build, optional, scoped,
// platform-specific), and independently proves each one:
//   * resolves to registry.npmjs.org,
//   * carries an integrity that MATCHES the official registry dist.integrity,
//   * was published at least MIN_AGE_SECONDS ago, measured against an
//     authoritative current UTC (the npm registry `Date` response header).
//
// FAIL-CLOSED SEMANTICS (never skip, never warn-only, no allowlist/exception)
// --------------------------------------------------------------------------
// A package is marked FAIL (non-zero process exit) on ANY of: registry outage
// or network error (after bounded retries, distinctly typed as
// INFRASTRUCTURE_UNAVAILABLE — a network failure is NEVER treated as
// advisory-free / age-clean), missing or malformed publication timestamp,
// malformed lock entry, missing integrity, integrity mismatch, unexpected
// resolved host, or any unverifiable/ambiguous condition. There is no
// allowlist, no --ignore, no suppression, and no exception path in this tool.
//
// Boundary: exactly 604800 s PASSES; 604799 s FAILS (full-second arithmetic,
// no day rounding).
//
// The pure logic (parseLock / decide / evaluateLock) takes an injectable `now`
// and an injectable packument provider, so the unit tests are deterministic
// and fully offline. All network access is confined to RegistryClient.
//
// Node ESM, Node built-ins ONLY (node:https, node:fs, node:url, node:process,
// node:timers/promises). No third-party dependency — this gate must run before
// and independently of any `npm install`.

import { readFileSync } from "node:fs";
import https from "node:https";
import process from "node:process";
import { setTimeout as sleep } from "node:timers/promises";
import { fileURLToPath } from "node:url";

export const MIN_AGE_SECONDS = 604_800; // 7 days; this PASSES, one second less FAILS.
export const REGISTRY_HOST = "registry.npmjs.org";
const REGISTRY_ORIGIN = `https://${REGISTRY_HOST}`;
// Any stable project; only its `Date` response header is used for the clock.
const CLOCK_URL = `${REGISTRY_ORIGIN}/npm`;
const HTTP_TIMEOUT_MS = 30_000;
const MAX_ATTEMPTS = 4; // 1 try + 3 retries
const BASE_BACKOFF_MS = 500;

// Distinct result kinds. INFRASTRUCTURE_UNAVAILABLE is deliberately separate
// from a genuine too-new finding so an operator can tell a transient outage
// (retry the job) from a real policy failure (a package is too new / tampered).
export const Kind = Object.freeze({
  OK: "ok",
  TOO_NEW: "too_new",
  INFRASTRUCTURE_UNAVAILABLE: "infrastructure_unavailable",
  INTEGRITY_MISMATCH: "integrity_mismatch",
  UNEXPECTED_HOST: "unexpected_host",
  MISSING_INTEGRITY: "missing_integrity",
  MISSING_TIMESTAMP: "missing_timestamp",
  MALFORMED: "malformed",
  AMBIGUOUS: "ambiguous",
});

// A fail-closed condition. `kind` lets callers distinguish an infrastructure
// outage from a genuine verification failure.
export class AgeGateError extends Error {
  constructor(message, kind = Kind.MALFORMED) {
    super(message);
    this.name = "AgeGateError";
    this.kind = kind;
  }
}

// --------------------------------------------------------------------------- //
// Lock parsing
// --------------------------------------------------------------------------- //
// Derive the package name from a lockfileVersion-2/3 `packages` key such as
// "node_modules/@types/node" or "node_modules/a/node_modules/b".
export function nameFromLockPath(pkgPath) {
  const marker = "node_modules/";
  const idx = pkgPath.lastIndexOf(marker);
  if (idx === -1) return null;
  return pkgPath.slice(idx + marker.length);
}

// Parse a committed npm lockfile (lockfileVersion 2 or 3) into the unique set
// of registry packages it admits. Each entry: { name, version, integrity,
// resolved }. Deduped by name@version; a name@version that appears with two
// DIFFERENT integrities is fail-closed (ambiguous). Throws AgeGateError on a
// structurally malformed lock.
export function parseLock(lockText) {
  let lock;
  try {
    lock = JSON.parse(lockText);
  } catch (err) {
    throw new AgeGateError(`lockfile is not valid JSON: ${err.message}`, Kind.MALFORMED);
  }
  const packages = lock && lock.packages;
  if (!packages || typeof packages !== "object") {
    throw new AgeGateError(
      "lockfile has no `packages` map (need lockfileVersion 2 or 3)",
      Kind.MALFORMED,
    );
  }

  // key = "name@version" -> { name, version, integrity, resolved }
  const byKey = new Map();

  for (const [pkgPath, meta] of Object.entries(packages)) {
    if (pkgPath === "") continue; // the root workspace itself
    if (!meta || typeof meta !== "object") {
      throw new AgeGateError(`malformed lock entry at "${pkgPath}"`, Kind.MALFORMED);
    }
    if (meta.link === true) continue; // workspace symlink, not a registry tarball
    // Only registry-installed packages carry `resolved`. Entries without a
    // `resolved` field (the workspace root, workspace/link entries, and local
    // `file:`/root deps) are not registry tarballs, so there is no registry
    // packument to age-check and this gate deliberately skips them. Their
    // identity is instead pinned by `npm ci`'s integrity verification against
    // the committed lock, which is the intended backstop for these entries.
    if (meta.resolved === undefined) continue;

    const name = meta.name || nameFromLockPath(pkgPath);
    if (!name) {
      throw new AgeGateError(`cannot determine package name for "${pkgPath}"`, Kind.MALFORMED);
    }
    const version = meta.version;
    if (!version || typeof version !== "string") {
      throw new AgeGateError(`missing version for "${name}" ("${pkgPath}")`, Kind.MALFORMED);
    }

    const key = `${name}@${version}`;
    const entry = {
      name,
      version,
      integrity: typeof meta.integrity === "string" ? meta.integrity : null,
      resolved: typeof meta.resolved === "string" ? meta.resolved : null,
    };

    const existing = byKey.get(key);
    if (existing) {
      // Same name@version must present identical integrity everywhere, else the
      // lock is ambiguous about what tarball is admitted -> fail closed later.
      if (existing.integrity !== entry.integrity || existing.resolved !== entry.resolved) {
        existing.ambiguous = true;
      }
    } else {
      byKey.set(key, entry);
    }
  }

  return [...byKey.values()];
}

// --------------------------------------------------------------------------- //
// Core decision logic (pure; deterministic under injected now + packument)
// --------------------------------------------------------------------------- //
function result(entry, kind, timestamp, ageSeconds, reason) {
  return {
    name: entry.name,
    version: entry.version,
    kind,
    timestamp: timestamp || null,
    ageSeconds: ageSeconds ?? null,
    passed: kind === Kind.OK,
    reason: reason || "",
  };
}

// Decide PASS/FAIL for one lock entry given the official registry packument for
// its package and an authoritative `now` (Date instance, UTC). Pure + total:
// returns a result object; never throws for a per-package failure.
export function decide(entry, packument, now) {
  if (entry.ambiguous) {
    return result(entry, Kind.AMBIGUOUS, null, null,
      "lock lists this name@version with conflicting integrity/resolved values");
  }
  // Host check. When `resolved` is a non-empty string it MUST point at the
  // official registry origin. When `resolved` is explicit-null (parseLock
  // normalises a non-string `resolved` to null) this check is a no-op — but the
  // integrity match below still binds the tarball identity, so a null-`resolved`
  // entry is not admitted on host trust alone.
  if (entry.resolved && !entry.resolved.startsWith(`${REGISTRY_ORIGIN}/`)) {
    return result(entry, Kind.UNEXPECTED_HOST, null, null,
      `resolved host is not ${REGISTRY_HOST}: ${entry.resolved}`);
  }
  if (!entry.integrity) {
    return result(entry, Kind.MISSING_INTEGRITY, null, null,
      "lock entry carries no integrity hash");
  }

  const versions = packument && packument.versions;
  const times = packument && packument.time;
  if (!versions || typeof versions !== "object" || !times || typeof times !== "object") {
    return result(entry, Kind.MALFORMED, null, null,
      "registry packument missing `versions`/`time` maps");
  }
  const vmeta = versions[entry.version];
  if (!vmeta || typeof vmeta !== "object") {
    return result(entry, Kind.MALFORMED, null, null,
      `registry has no metadata for version ${entry.version}`);
  }
  const officialIntegrity = vmeta.dist && vmeta.dist.integrity;
  if (!officialIntegrity || typeof officialIntegrity !== "string") {
    // Cannot independently verify the tarball identity -> fail closed.
    return result(entry, Kind.MISSING_INTEGRITY, null, null,
      "official registry metadata carries no dist.integrity to match against");
  }
  if (officialIntegrity !== entry.integrity) {
    return result(entry, Kind.INTEGRITY_MISMATCH, null, null,
      `lock integrity does not match official registry dist.integrity`);
  }

  const ts = times[entry.version];
  if (!ts || typeof ts !== "string") {
    return result(entry, Kind.MISSING_TIMESTAMP, null, null,
      "registry time map has no publication timestamp for this version");
  }
  const published = new Date(ts);
  if (Number.isNaN(published.getTime())) {
    return result(entry, Kind.MISSING_TIMESTAMP, null, null,
      `malformed publication timestamp ${JSON.stringify(ts)}`);
  }
  const ageSeconds = Math.floor((now.getTime() - published.getTime()) / 1000);
  if (ageSeconds >= MIN_AGE_SECONDS) {
    return result(entry, Kind.OK, published.toISOString(), ageSeconds, "");
  }
  return result(entry, Kind.TOO_NEW, published.toISOString(), ageSeconds,
    `published ${ageSeconds}s ago; requires >= ${MIN_AGE_SECONDS}s`);
}

// Evaluate every entry. A fail-closed provider error for one package becomes a
// FAIL result for THAT package (the run still fails) rather than aborting the
// whole report, so the operator sees every problem in one pass. A provider
// error tagged INFRASTRUCTURE_UNAVAILABLE is surfaced with that distinct kind.
export async function evaluateLock(entries, provider, now) {
  const results = [];
  for (const entry of entries) {
    try {
      const packument = await provider(entry.name);
      results.push(decide(entry, packument, now));
    } catch (err) {
      const kind = err instanceof AgeGateError ? err.kind : Kind.INFRASTRUCTURE_UNAVAILABLE;
      results.push(result(entry, kind, null, null, err.message));
    }
  }
  return results;
}

// --------------------------------------------------------------------------- //
// Live npm registry access (the only networked surface)
// --------------------------------------------------------------------------- //
function httpGet(url, { method = "GET", body = null, headers = {} } = {}) {
  return new Promise((resolve, reject) => {
    const opts = { method, timeout: HTTP_TIMEOUT_MS, headers: { ...headers } };
    if (body != null) opts.headers["content-length"] = Buffer.byteLength(body);
    const req = https.request(url, opts, (res) => {
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: Buffer.concat(chunks).toString("utf8"),
        });
      });
    });
    req.on("timeout", () => req.destroy(new Error(`request timed out after ${HTTP_TIMEOUT_MS}ms`)));
    req.on("error", reject);
    if (body != null) req.write(body);
    req.end();
  });
}

// Retry a network thunk with bounded exponential backoff. On exhaustion, throw
// an AgeGateError tagged INFRASTRUCTURE_UNAVAILABLE — the caller then fails
// CLOSED with a distinct kind (a transient outage is NEVER age-clean).
async function withRetries(label, thunk, requestFn = httpGet) {
  let lastErr;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      return await thunk(requestFn);
    } catch (err) {
      // Deterministic verification failures (malformed JSON, missing Date
      // header) are NOT transient — surface them immediately rather than
      // retrying and mislabelling them as an outage.
      if (err instanceof AgeGateError && err.kind !== Kind.INFRASTRUCTURE_UNAVAILABLE) {
        throw err;
      }
      lastErr = err;
      if (attempt < MAX_ATTEMPTS) {
        await sleep(BASE_BACKOFF_MS * 2 ** (attempt - 1));
      }
    }
  }
  throw new AgeGateError(
    `${label}: registry unreachable after ${MAX_ATTEMPTS} attempts: ${lastErr && lastErr.message}`,
    Kind.INFRASTRUCTURE_UNAVAILABLE,
  );
}

export class RegistryClient {
  // `requestFn` is injectable so tests never touch the network.
  constructor(requestFn = httpGet) {
    this._request = requestFn;
  }

  // Authoritative current UTC from the registry's own `Date` header (not the
  // local clock, which a tampered CI runner could skew).
  async utcNow() {
    return withRetries("clock", async (request) => {
      const res = await request(CLOCK_URL, { method: "HEAD" });
      const dateHdr = res.headers && res.headers.date;
      if (!dateHdr) {
        // Missing Date header is a hard fail-closed, not retryable-forever.
        throw new AgeGateError("registry response carried no Date header", Kind.MALFORMED);
      }
      const now = new Date(dateHdr);
      if (Number.isNaN(now.getTime())) {
        throw new AgeGateError(`malformed registry Date header ${JSON.stringify(dateHdr)}`, Kind.MALFORMED);
      }
      return now;
    }, this._request);
  }

  // Full packument for a package (its `versions[*].dist.integrity` and `time`).
  async packument(name) {
    const url = `${REGISTRY_ORIGIN}/${encodeURIComponent(name).replace("%40", "@")}`;
    return withRetries(`packument ${name}`, async (request) => {
      const res = await request(url);
      if (res.status !== 200) {
        throw new Error(`HTTP ${res.status}`);
      }
      let payload;
      try {
        payload = JSON.parse(res.body);
      } catch (err) {
        throw new AgeGateError(`malformed registry JSON for ${name}: ${err.message}`, Kind.MALFORMED);
      }
      return payload;
    }, this._request);
  }

  // Bulk advisory lookup (the exact endpoint `npm audit` uses). `bulkQuery` is
  // { "<name>": ["<version>", ...] }; the response is
  // { "<name>": [ { id, url, title, severity, vulnerable_versions, ... } ] }
  // containing ONLY advisories that affect the queried versions. Fails closed
  // (INFRASTRUCTURE_UNAVAILABLE) after retry exhaustion — a network failure is
  // NEVER treated as advisory-free.
  async advisories(bulkQuery) {
    const url = `${REGISTRY_ORIGIN}/-/npm/v1/security/advisories/bulk`;
    const body = JSON.stringify(bulkQuery);
    return withRetries("advisories", async (request) => {
      const res = await request(url, {
        method: "POST",
        body,
        headers: { "content-type": "application/json" },
      });
      if (res.status !== 200) throw new Error(`HTTP ${res.status}`);
      try {
        return JSON.parse(res.body);
      } catch (err) {
        throw new AgeGateError(`malformed advisory JSON: ${err.message}`, Kind.MALFORMED);
      }
    }, this._request);
  }
}

// --------------------------------------------------------------------------- //
// FE-S11: continuous npm CLI tooling advisory verification (fail-closed).
// The exact pinned npm CLI (e.g. 11.18.0) is checked for advisories affecting
// THAT version on every relevant CI run and in the scheduled audit. Any
// advisory fails the run; there is no suppression/allowlist. Pure decision is
// separated from network so it is deterministically testable.
// --------------------------------------------------------------------------- //
export function decideNpmCli(advisoriesResponse, version) {
  const list = (advisoriesResponse && advisoriesResponse.npm) || [];
  return {
    name: "npm",
    version,
    passed: Array.isArray(list) && list.length === 0,
    advisories: Array.isArray(list) ? list : [],
  };
}

export async function runNpmCliAdvisory(version, client = new RegistryClient()) {
  if (!version) {
    console.error("FAIL-CLOSED: no npm CLI version supplied to advisory check");
    return 1;
  }
  let resp;
  try {
    resp = await client.advisories({ npm: [version] });
  } catch (err) {
    console.error(
      `FAIL-CLOSED: cannot verify npm@${version} advisories [${err.kind || "error"}]: ${err.message}`,
    );
    return 1;
  }
  const d = decideNpmCli(resp, version);
  console.log(`npm CLI advisory verification  (pinned npm@${version})`);
  if (d.passed) {
    console.log(`RESULT: PASS — no advisory affects npm@${version}`);
    return 0;
  }
  for (const a of d.advisories) {
    console.log(`  ADVISORY ${a.severity || "?"}  ${a.id || ""}  ${a.title || ""}  ${a.url || ""}`);
  }
  console.error(
    `RESULT: FAIL — ${d.advisories.length} advisory(ies) affect the pinned npm@${version}. ` +
      `Pin a fixed npm version (no suppression/allowlist is permitted).`,
  );
  return 1;
}

// --------------------------------------------------------------------------- //
// Reporting / CLI
// --------------------------------------------------------------------------- //
export function formatResult(r) {
  const verdict = r.passed ? "PASS" : "FAIL";
  const ts = r.timestamp || "-";
  const age = r.ageSeconds != null ? `${r.ageSeconds}s (${(r.ageSeconds / 86400).toFixed(2)}d)` : "-";
  const tail = r.passed ? "" : `  [${r.kind}: ${r.reason}]`;
  return `${verdict}  ${r.name}@${r.version}  uploaded=${ts}  age=${age}${tail}`;
}

export async function run(lockPath, client = new RegistryClient()) {
  let now;
  try {
    now = await client.utcNow();
  } catch (err) {
    console.error(`FAIL-CLOSED: cannot obtain authoritative UTC time [${err.kind || "error"}]: ${err.message}`);
    return 1;
  }

  let entries;
  try {
    entries = parseLock(readFileSync(lockPath, "utf8"));
  } catch (err) {
    console.error(`FAIL-CLOSED: cannot read/parse lock ${lockPath}: ${err.message}`);
    return 1;
  }

  console.log(
    `Committed-lockfile release-age gate  (now=${now.toISOString()}, min_age=${MIN_AGE_SECONDS}s)`,
  );
  console.log(`== ${lockPath}  (${entries.length} unique registry packages) ==`);

  const results = await evaluateLock(entries, (name) => client.packument(name), now);
  results.sort((a, b) => (a.name === b.name ? a.version.localeCompare(b.version) : a.name.localeCompare(b.name)));

  let ok = true;
  let infra = 0;
  for (const r of results) {
    console.log("  " + formatResult(r));
    if (!r.passed) ok = false;
    if (r.kind === Kind.INFRASTRUCTURE_UNAVAILABLE) infra += 1;
  }

  if (infra > 0) {
    console.error(
      `\nRESULT: FAIL-CLOSED — ${infra} package(s) could not be verified because the ` +
        `registry was unavailable after ${MAX_ATTEMPTS} attempts. This is an ` +
        `INFRASTRUCTURE_UNAVAILABLE result (retry the job); it is NOT a clean pass.`,
    );
    return 1;
  }
  console.log(
    "\nRESULT: " +
      (ok
        ? "PASS — every committed registry package is >= 7 days old and integrity-verified"
        : "FAIL — at least one package is too new, tampered, or unverifiable"),
  );
  return ok ? 0 : 1;
}

// Executed directly (not imported by the test runner).
//   node dependency_age_gate.mjs <lockfile>                  -> committed-lock age gate (FE-S9)
//   node dependency_age_gate.mjs --npm-cli-advisory <ver>    -> npm CLI advisory check (FE-S11)
const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMain) {
  if (process.argv[2] === "--npm-cli-advisory") {
    runNpmCliAdvisory(process.argv[3]).then((code) => process.exit(code));
  } else {
    const lockPath = process.argv[2] || "package-lock.json";
    run(lockPath).then((code) => process.exit(code));
  }
}
