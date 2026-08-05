// Deterministic, offline unit tests for the committed-lockfile release-age gate
// (task M0-T019, scenario FE-S9). Node's built-in test runner + node:assert;
// no third-party dependency, so these run before any `npm install`.
//
// Every test injects a fixed `now` and a synthetic packument provider (or a
// fake request function), so nothing here touches the network. The live
// behaviour (real registry Date header + real per-version metadata) is
// exercised by the CI age-gate step over the real committed lock; these tests
// pin the LOGIC: the 604800/604799 boundary, integrity matching, host
// checking, every fail-closed branch, and the distinct
// INFRASTRUCTURE_UNAVAILABLE outcome after retry exhaustion.

import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import {
  MIN_AGE_SECONDS,
  Kind,
  AgeGateError,
  parseLock,
  nameFromLockPath,
  decide,
  evaluateLock,
  RegistryClient,
  decideNpmCli,
  runNpmCliAdvisory,
  run,
} from "../dependency_age_gate.mjs";

const NOW = new Date("2026-08-05T00:00:00.000Z");
const INTEG_A = "sha512-" + "A".repeat(80) + "==";
const INTEG_B = "sha512-" + "B".repeat(80) + "==";
const REG = "https://registry.npmjs.org";

function uploadedSecondsAgo(seconds) {
  return new Date(NOW.getTime() - seconds * 1000).toISOString();
}

// A minimal packument for one version.
function packument(version, { integrity = INTEG_A, time = uploadedSecondsAgo(30 * 86400) } = {}) {
  return {
    versions: { [version]: { dist: { integrity } } },
    time: { [version]: time },
  };
}

function entry(over = {}) {
  return {
    name: "demo",
    version: "1.0.0",
    integrity: INTEG_A,
    resolved: `${REG}/demo/-/demo-1.0.0.tgz`,
    ...over,
  };
}

// --------------------------------------------------------------------------- //
// Boundary: exactly 604800 s PASSES; 604799 s FAILS (FE-S9)
// --------------------------------------------------------------------------- //
test("exactly seven days (604800s) passes", () => {
  const p = packument("1.0.0", { time: uploadedSecondsAgo(MIN_AGE_SECONDS) });
  const r = decide(entry(), p, NOW);
  assert.equal(r.passed, true);
  assert.equal(r.kind, Kind.OK);
  assert.equal(r.ageSeconds, MIN_AGE_SECONDS);
});

test("one second under seven days (604799s) fails", () => {
  const p = packument("1.0.0", { time: uploadedSecondsAgo(MIN_AGE_SECONDS - 1) });
  const r = decide(entry(), p, NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.TOO_NEW);
  assert.equal(r.ageSeconds, MIN_AGE_SECONDS - 1);
  assert.match(r.reason, /requires >= 604800s/);
});

test("comfortably old passes", () => {
  const r = decide(entry(), packument("1.0.0"), NOW);
  assert.equal(r.passed, true);
});

// --------------------------------------------------------------------------- //
// Fail-closed branches — none may skip or pass
// --------------------------------------------------------------------------- //
test("integrity mismatch fails closed", () => {
  const p = packument("1.0.0", { integrity: INTEG_B }); // registry differs from lock
  const r = decide(entry({ integrity: INTEG_A }), p, NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.INTEGRITY_MISMATCH);
});

test("missing integrity in lock fails closed", () => {
  const r = decide(entry({ integrity: null }), packument("1.0.0"), NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.MISSING_INTEGRITY);
});

test("registry lacking dist.integrity fails closed", () => {
  const p = { versions: { "1.0.0": { dist: {} } }, time: { "1.0.0": uploadedSecondsAgo(30 * 86400) } };
  const r = decide(entry(), p, NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.MISSING_INTEGRITY);
});

test("unexpected resolved host fails closed", () => {
  const r = decide(entry({ resolved: "https://evil.example.com/demo/-/demo-1.0.0.tgz" }), packument("1.0.0"), NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.UNEXPECTED_HOST);
});

test("missing publication timestamp fails closed", () => {
  const p = { versions: { "1.0.0": { dist: { integrity: INTEG_A } } }, time: {} };
  const r = decide(entry(), p, NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.MISSING_TIMESTAMP);
});

test("malformed publication timestamp fails closed", () => {
  const p = { versions: { "1.0.0": { dist: { integrity: INTEG_A } } }, time: { "1.0.0": "not-a-date" } };
  const r = decide(entry(), p, NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.MISSING_TIMESTAMP);
});

test("registry missing the version fails closed", () => {
  const p = { versions: {}, time: {} };
  const r = decide(entry(), p, NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.MALFORMED);
});

test("ambiguous lock entry (conflicting integrity) fails closed", () => {
  const r = decide(entry({ ambiguous: true }), packument("1.0.0"), NOW);
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.AMBIGUOUS);
});

// --------------------------------------------------------------------------- //
// evaluateLock: a provider outage becomes a distinct INFRASTRUCTURE_UNAVAILABLE
// FAIL for that package (never a skip / pass).
// --------------------------------------------------------------------------- //
test("provider outage yields INFRASTRUCTURE_UNAVAILABLE fail, not a skip", async () => {
  const provider = async () => {
    throw new AgeGateError("simulated registry outage", Kind.INFRASTRUCTURE_UNAVAILABLE);
  };
  const results = await evaluateLock([entry()], provider, NOW);
  assert.equal(results.length, 1);
  assert.equal(results[0].passed, false);
  assert.equal(results[0].kind, Kind.INFRASTRUCTURE_UNAVAILABLE);
});

test("plain (non-AgeGateError) provider throw is treated as infrastructure fail", async () => {
  const provider = async () => {
    throw new Error("ECONNRESET");
  };
  const results = await evaluateLock([entry()], provider, NOW);
  assert.equal(results[0].passed, false);
  assert.equal(results[0].kind, Kind.INFRASTRUCTURE_UNAVAILABLE);
});

test("evaluateLock reports every package", async () => {
  const entries = [entry({ name: "old", version: "1.0.0" }), entry({ name: "new", version: "2.0.0" })];
  const provider = async (name) =>
    name === "old"
      ? packument("1.0.0", { time: uploadedSecondsAgo(30 * 86400) })
      : packument("2.0.0", { time: uploadedSecondsAgo(MIN_AGE_SECONDS - 1) });
  const byName = Object.fromEntries((await evaluateLock(entries, provider, NOW)).map((r) => [r.name, r]));
  assert.equal(byName.old.passed, true);
  assert.equal(byName.new.passed, false);
  assert.equal(byName.new.kind, Kind.TOO_NEW);
});

// --------------------------------------------------------------------------- //
// Lock parsing
// --------------------------------------------------------------------------- //
test("nameFromLockPath handles scoped and nested paths", () => {
  assert.equal(nameFromLockPath("node_modules/next"), "next");
  assert.equal(nameFromLockPath("node_modules/@types/node"), "@types/node");
  assert.equal(nameFromLockPath("node_modules/a/node_modules/@scope/b"), "@scope/b");
});

test("parseLock collects unique registry packages and skips root/link/file entries", () => {
  const lock = JSON.stringify({
    lockfileVersion: 3,
    packages: {
      "": { name: "root" },
      "node_modules/next": {
        version: "15.5.21",
        resolved: `${REG}/next/-/next-15.5.21.tgz`,
        integrity: INTEG_A,
      },
      "node_modules/@types/node": {
        version: "22.20.1",
        resolved: `${REG}/@types/node/-/node-22.20.1.tgz`,
        integrity: INTEG_B,
      },
      "node_modules/local-link": { link: true, resolved: "../pkg" },
      "some/workspace": { version: "0.0.0" }, // no resolved -> skipped
    },
  });
  const entries = parseLock(lock).sort((a, b) => a.name.localeCompare(b.name));
  assert.equal(entries.length, 2);
  assert.equal(entries[0].name, "@types/node");
  assert.equal(entries[1].name, "next");
  assert.equal(entries[1].version, "15.5.21");
});

test("parseLock flags a name@version with conflicting integrity as ambiguous", () => {
  const lock = JSON.stringify({
    lockfileVersion: 3,
    packages: {
      "": { name: "root" },
      "node_modules/dup": { version: "1.0.0", resolved: `${REG}/dup/-/dup-1.0.0.tgz`, integrity: INTEG_A },
      "node_modules/a/node_modules/dup": {
        version: "1.0.0",
        resolved: `${REG}/dup/-/dup-1.0.0.tgz`,
        integrity: INTEG_B,
      },
    },
  });
  const entries = parseLock(lock);
  assert.equal(entries.length, 1);
  assert.equal(entries[0].ambiguous, true);
  assert.equal(decide(entries[0], packument("1.0.0"), NOW).kind, Kind.AMBIGUOUS);
});

test("parseLock rejects a lock with no packages map", () => {
  assert.throws(() => parseLock(JSON.stringify({ lockfileVersion: 1, dependencies: {} })), AgeGateError);
});

test("parseLock rejects non-JSON", () => {
  assert.throws(() => parseLock("{not json"), AgeGateError);
});

test("parseLock fails closed on a resolved entry missing its version", () => {
  const lock = JSON.stringify({
    lockfileVersion: 3,
    packages: {
      "": { name: "root" },
      "node_modules/broken": { resolved: `${REG}/broken/-/broken-1.0.0.tgz`, integrity: INTEG_A },
    },
  });
  assert.throws(() => parseLock(lock), AgeGateError);
});

// --------------------------------------------------------------------------- //
// RegistryClient.utcNow: uses the server Date header, fails closed without it,
// and after retry exhaustion yields INFRASTRUCTURE_UNAVAILABLE.
// --------------------------------------------------------------------------- //
test("utcNow reads the registry Date header", async () => {
  const request = async () => ({ status: 200, headers: { date: "Wed, 05 Aug 2026 00:00:00 GMT" }, body: "" });
  const client = new RegistryClient(request);
  const now = await client.utcNow();
  assert.equal(now.getTime(), NOW.getTime());
});

test("utcNow fails closed (no retry loop) when Date header is missing", async () => {
  let calls = 0;
  const request = async () => {
    calls += 1;
    return { status: 200, headers: {}, body: "" };
  };
  const client = new RegistryClient(request);
  await assert.rejects(() => client.utcNow(), (err) => err instanceof AgeGateError && err.kind === Kind.MALFORMED);
  assert.equal(calls, 1, "a missing Date header is deterministic and must not be retried");
});

test("utcNow retries a network error and then fails closed as INFRASTRUCTURE_UNAVAILABLE", async () => {
  let calls = 0;
  const request = async () => {
    calls += 1;
    throw new Error("ECONNRESET");
  };
  const client = new RegistryClient(request);
  await assert.rejects(
    () => client.utcNow(),
    (err) => err instanceof AgeGateError && err.kind === Kind.INFRASTRUCTURE_UNAVAILABLE,
  );
  assert.equal(calls, 4, "should attempt 1 + 3 retries before failing closed");
});

test("packument retries then fails closed on persistent network error", async () => {
  let calls = 0;
  const request = async () => {
    calls += 1;
    throw new Error("ETIMEDOUT");
  };
  const client = new RegistryClient(request);
  await assert.rejects(
    () => client.packument("demo"),
    (err) => err instanceof AgeGateError && err.kind === Kind.INFRASTRUCTURE_UNAVAILABLE,
  );
  assert.equal(calls, 4);
});

test("packument fails closed (no retry) on malformed JSON", async () => {
  let calls = 0;
  const request = async () => {
    calls += 1;
    return { status: 200, headers: {}, body: "{not json" };
  };
  const client = new RegistryClient(request);
  await assert.rejects(
    () => client.packument("demo"),
    (err) => err instanceof AgeGateError && err.kind === Kind.MALFORMED,
  );
  assert.equal(calls, 1);
});

test("packument treats a non-200 as retryable then infrastructure-unavailable", async () => {
  let calls = 0;
  const request = async () => {
    calls += 1;
    return { status: 503, headers: {}, body: "" };
  };
  const client = new RegistryClient(request);
  await assert.rejects(
    () => client.packument("demo"),
    (err) => err instanceof AgeGateError && err.kind === Kind.INFRASTRUCTURE_UNAVAILABLE,
  );
  assert.equal(calls, 4);
});

// --------------------------------------------------------------------------- //
// FE-S11: npm CLI tooling advisory verification (fail-closed, no suppression).
// --------------------------------------------------------------------------- //
test("decideNpmCli passes when the bulk response lists no advisory for npm", () => {
  assert.equal(decideNpmCli({}, "11.18.0").passed, true);
  assert.equal(decideNpmCli({ npm: [] }, "11.18.0").passed, true);
});

test("decideNpmCli fails when any advisory affects the pinned npm", () => {
  const resp = { npm: [{ id: 1, severity: "high", title: "x", url: "u" }] };
  const d = decideNpmCli(resp, "11.18.0");
  assert.equal(d.passed, false);
  assert.equal(d.advisories.length, 1);
});

test("runNpmCliAdvisory returns 0 for a clean npm version", async () => {
  const request = async () => ({ status: 200, headers: {}, body: JSON.stringify({}) });
  const code = await runNpmCliAdvisory("11.18.0", new RegistryClient(request));
  assert.equal(code, 0);
});

test("runNpmCliAdvisory returns 1 when an advisory affects npm", async () => {
  const request = async () => ({
    status: 200,
    headers: {},
    body: JSON.stringify({ npm: [{ id: 9, severity: "critical", title: "boom", url: "u" }] }),
  });
  const code = await runNpmCliAdvisory("11.18.0", new RegistryClient(request));
  assert.equal(code, 1);
});

test("runNpmCliAdvisory fails closed (returns 1) when the advisory endpoint is unreachable", async () => {
  const request = async () => {
    throw new Error("ECONNRESET");
  };
  const code = await runNpmCliAdvisory("11.18.0", new RegistryClient(request));
  assert.equal(code, 1);
});

test("runNpmCliAdvisory fails closed when no version is supplied", async () => {
  const code = await runNpmCliAdvisory(undefined, new RegistryClient(async () => ({ status: 200, headers: {}, body: "{}" })));
  assert.equal(code, 1);
});

// --------------------------------------------------------------------------- //
// Host-slash boundary (nit 5a): the registry-origin prefix check must admit the
// exact `https://registry.npmjs.org/…` origin and reject a look-alike host whose
// authority merely begins with those characters (…npmjs.org.evil.com/…).
// --------------------------------------------------------------------------- //
test("resolved host exactly registry.npmjs.org passes the host check", () => {
  const r = decide(entry({ resolved: `${REG}/demo/-/demo-1.0.0.tgz` }), packument("1.0.0"), NOW);
  assert.equal(r.passed, true);
  assert.equal(r.kind, Kind.OK);
});

test("look-alike registry host (registry.npmjs.org.evil.com) fails UNEXPECTED_HOST", () => {
  const r = decide(
    entry({ resolved: "https://registry.npmjs.org.evil.com/demo/-/demo-1.0.0.tgz" }),
    packument("1.0.0"),
    NOW,
  );
  assert.equal(r.passed, false);
  assert.equal(r.kind, Kind.UNEXPECTED_HOST);
});

// --------------------------------------------------------------------------- //
// run() end-to-end aggregation (nit 5b): drives the full CLI path with an
// injected RegistryClient (registry Date header for the clock + per-package
// packuments) over a lock written to a temp dir. No network, no real npm.
// --------------------------------------------------------------------------- //
const CLOCK_DATE_HEADER = "Wed, 05 Aug 2026 00:00:00 GMT"; // == NOW

// One request function that serves both surfaces run() touches:
//   * HEAD  -> the registry `Date` header (RegistryClient.utcNow)
//   * GET   -> a per-package packument keyed by the name in the URL tail
// `pkgTimes[name]` is that package's published-at ISO string.
function fakeRegistryRequest(pkgTimes) {
  return async (url, opts = {}) => {
    if ((opts.method || "GET") === "HEAD") {
      return { status: 200, headers: { date: CLOCK_DATE_HEADER }, body: "" };
    }
    const name = decodeURIComponent(url.slice(REG.length + 1));
    const time = pkgTimes[name];
    return {
      status: 200,
      headers: {},
      body: JSON.stringify({
        versions: { "1.0.0": { dist: { integrity: INTEG_A } } },
        time: { "1.0.0": time },
      }),
    };
  };
}

function lockWith(names) {
  const packages = { "": { name: "root" } };
  for (const name of names) {
    packages[`node_modules/${name}`] = {
      version: "1.0.0",
      resolved: `${REG}/${name}/-/${name}-1.0.0.tgz`,
      integrity: INTEG_A,
    };
  }
  return JSON.stringify({ lockfileVersion: 3, packages });
}

async function runOnLock(lockText, client) {
  const dir = mkdtempSync(join(tmpdir(), "agegate-run-"));
  const lockPath = join(dir, "package-lock.json");
  writeFileSync(lockPath, lockText);
  const out = [];
  const origLog = console.log;
  const origErr = console.error;
  console.log = (...a) => out.push(a.join(" "));
  console.error = (...a) => out.push(a.join(" "));
  try {
    const code = await run(lockPath, client);
    return { code, output: out.join("\n") };
  } finally {
    console.log = origLog;
    console.error = origErr;
    rmSync(dir, { recursive: true, force: true });
  }
}

test("run() fails (exit 1) and names the too-new package when one entry is under age", async () => {
  const client = new RegistryClient(
    fakeRegistryRequest({
      oldpkg: uploadedSecondsAgo(30 * 86400),
      newpkg: uploadedSecondsAgo(MIN_AGE_SECONDS - 1),
    }),
  );
  const { code, output } = await runOnLock(lockWith(["oldpkg", "newpkg"]), client);
  assert.equal(code, 1);
  assert.match(output, /FAIL/);
  assert.match(output, /newpkg@1\.0\.0/);
  assert.match(output, /PASS  oldpkg@1\.0\.0/);
});

test("run() passes (exit 0) for an all-valid multi-entry lock", async () => {
  const client = new RegistryClient(
    fakeRegistryRequest({
      alpha: uploadedSecondsAgo(30 * 86400),
      beta: uploadedSecondsAgo(MIN_AGE_SECONDS),
    }),
  );
  const { code, output } = await runOnLock(lockWith(["alpha", "beta"]), client);
  assert.equal(code, 0);
  assert.match(output, /RESULT: PASS/);
});

// --------------------------------------------------------------------------- //
// Success paths not otherwise covered (nit 5c): a null-`resolved` entry still
// binds identity through the integrity match and passes the host check as a
// no-op (it is not rejected merely for lacking a registry host string).
// --------------------------------------------------------------------------- //
test("null-resolved entry with matching integrity passes (host check is a no-op)", () => {
  const r = decide(entry({ resolved: null }), packument("1.0.0"), NOW);
  assert.equal(r.passed, true);
  assert.equal(r.kind, Kind.OK);
});

// --------------------------------------------------------------------------- //
// parseLock robustness (nit 5d): malformed structural input fails closed; a
// name@version listed with conflicting `resolved` values is flagged ambiguous
// (fail-closed downstream in decide).
// --------------------------------------------------------------------------- //
test("parseLock throws on a malformed (non-object) lock entry", () => {
  const lock = JSON.stringify({
    lockfileVersion: 3,
    packages: {
      "": { name: "root" },
      "node_modules/broken": "not-an-object",
    },
  });
  assert.throws(() => parseLock(lock), (err) => err instanceof AgeGateError && err.kind === Kind.MALFORMED);
});

test("parseLock throws when a resolved entry's version is not a string", () => {
  const lock = JSON.stringify({
    lockfileVersion: 3,
    packages: {
      "": { name: "root" },
      "node_modules/badver": { version: 5, resolved: `${REG}/badver/-/badver-5.tgz`, integrity: INTEG_A },
    },
  });
  assert.throws(() => parseLock(lock), (err) => err instanceof AgeGateError && err.kind === Kind.MALFORMED);
});

test("parseLock flags a name@version with conflicting resolved as ambiguous (fails closed)", () => {
  const lock = JSON.stringify({
    lockfileVersion: 3,
    packages: {
      "": { name: "root" },
      "node_modules/dup": { version: "1.0.0", resolved: `${REG}/dup/-/dup-1.0.0.tgz`, integrity: INTEG_A },
      "node_modules/a/node_modules/dup": {
        version: "1.0.0",
        resolved: `${REG}/dup/-/dup-1.0.0-mirror.tgz`,
        integrity: INTEG_A,
      },
    },
  });
  const entries = parseLock(lock);
  assert.equal(entries.length, 1);
  assert.equal(entries[0].ambiguous, true);
  assert.equal(decide(entries[0], packument("1.0.0"), NOW).kind, Kind.AMBIGUOUS);
});
