# Dependency Security Policy (permanent, machine-enforced, no agent waiver)

Status: PERMANENT. Owner directive 2026-07-20 (frontend P0), reconciled 2026-07-23,
activated for fresh build under governance directive D-009 (2026-08-04). This document is the
full, authoritative statement of the rule. The concise pointer lives in `CLAUDE.md`; the
short canonical wording lives in `.claude/ORCHESTRATION_POLICY.md` §G. Where any of these
disagree, the STRICTER reading governs. This policy is enforcement policy, not advisory.

It applies to **every** dependency the platform admits, across **both** ecosystems and
**every** layer: production runtime, development, build, lock generation, audit tooling, and
the package-manager CLIs themselves.

---

## 1. The rule (what every admitted package must satisfy)

An agent may admit a dependency version into a committed lockfile only if ALL of the following
hold, proven by machine checks in CI:

1. **Advisory-free at every severity.** No known advisory — info, low, moderate, high, or
   critical — affects the admitted version, anywhere in the tree (runtime, dev, build, and the
   audit/package-manager tooling included). A single finding fails the build.
2. **At least seven complete days old.** Measured against the official registry publication
   timestamp in UTC: **exactly 604800 seconds PASSES; 604799 seconds FAILS.** Full-second
   arithmetic — no day rounding, no timezone fudging. The current instant is taken from the
   registry's own clock (npm/PyPI `Date` response header), never the local/CI clock.
3. **Exact pins + lockfile integrity.** Every direct dependency and devDependency is pinned to
   an EXACT version (no `^`, `~`, or range). The committed lockfile carries an integrity hash
   for every tarball, and that hash must MATCH the official registry `dist.integrity`. Installs
   are deterministic (`npm ci` / `pip install --require-hashes`); a lockfile that does not match
   the manifest, or a tarball whose integrity does not match, fails the build.
4. **Registry origin.** Every package resolves to the official registry
   (`registry.npmjs.org` for npm, `pypi.org` for Python). An unexpected resolved host fails
   closed.
5. **Audited on every change AND on a schedule.** A blocking advisory audit runs on every push
   and pull request that can affect the tree, and again on a daily schedule so an advisory
   disclosed AFTER a lock lands turns the run red without any code change.

**Fail closed, always.** On an unavailable/timed-out registry, missing or malformed metadata,
a missing/mismatched integrity hash, an unexpected host, or any ambiguous or unverifiable
condition, the check FAILS (non-zero exit, package marked FAIL). A network failure is **never**
interpreted as "advisory-free" or "old enough". No check is ever warning-only.

**No agent waiver. No unlocked bootstrap tool. No dynamic download outside a reviewed lock.**
No agent may add an allowlist, suppression, `--ignore`, exception file, or "warning-only"
downgrade to any gate. The age/advisory gates contain no exception path whatsoever.

---

## 2. The four enforcement layers (npm) — how they differ and why all four exist

A single mechanism is not enough; each layer closes a gap the others leave open.

**(a) `.npmrc` resolver-time filtering — defence in depth, NOT a gate.**
`apps/web/.npmrc` sets `min-release-age=7` and `save-exact=true`. This filters versions **when a
lockfile is (re)generated**. It does *not* inspect an already-committed lockfile, so on its own a
hand-edited lock could smuggle a too-new package past `npm ci`. Treat `.npmrc` as help during
regeneration only.

**(b) Independent committed-lockfile age verification in CI — the real age gate (FE-S9).**
`apps/web/scripts/dependency_age_gate.mjs` parses the **entire committed
`package-lock.json`**, enumerates every unique registry package (direct, transitive, dev, test,
build, optional, scoped, platform-specific), and independently proves each one: it resolves to
`registry.npmjs.org`, its lock integrity matches the official registry `dist.integrity`, and its
official publication timestamp is `>= 604800 s` before the registry's own UTC clock. It runs in
the required push/PR CI and in the scheduled re-audit, fails closed on every ambiguous/outage
condition (with a distinct `infrastructure_unavailable` outcome after bounded retries + backoff,
so a transient outage is visibly different from a genuine too-new finding), and has **no**
allowlist/suppression/exception. This is what stops a hand-edited lock.

**(c) Application-lock advisory auditing — `npm audit` (FE-S2).**
`npm audit --audit-level=low` plus an explicit `npm audit --json` check requiring
`metadata.vulnerabilities` total `== 0` across every severity, on the installed tree (dev deps
included). Blocking on any finding. This is the advisory dimension for the application tree.

**(d) npm CLI tooling advisory verification (FE-S11).**
The dependency-management tool itself must be trustworthy. The exact pinned npm CLI (currently
`npm@11.18.0`) is checked against the official advisory source on every relevant CI run and in
the scheduled re-audit; any advisory affecting that version fails the run. No suppression. This
gives the tooling the same continuous advisory coverage the application tree has (parallel to
the Python tooling-lock `pip-audit` in M0-T020).

Layers (a)+(b) are the **age** dimension; (c)+(d) are the **advisory** dimension. The committed
lock needs all four because resolver-time filtering, committed-lock verification, application
auditing, and tooling auditing each defend a different attack surface.

### Python parallel (M0-T018 / M0-T020)
The same rule is enforced for `services/api` by `services/api/scripts/dependency_age_gate.py`
(committed hash-pinned lock age gate over both the runtime and tooling locks) and blocking
`pip-audit --strict` over both locks, on push/PR and on the daily `scheduled-audit` workflow,
with the resolver pinned to an exact `uv` bootstrapped from the hash-pinned tooling lock.

---

## 3. Exact pins and zero-resolution-change conversion

Every direct dependency and devDependency in `apps/web/package.json` is an exact version equal
to the version already resolved at the lockfile root. Converting an existing range to an exact
pin must introduce **zero** package-resolution change: the regenerated lock's resolved versions
and integrity hashes must be the same set. If regenerating the lock (via the reviewed npm CLI on
CI) would change any resolved version that was not the deliberate subject of the change, **STOP
and report** — do not silently accept the drift. `save-exact=true` keeps future `npm i <pkg>`
adds pinned.

---

## 4. Post-merge advisories reopen security work and block deploy

An advisory disclosed against an already-merged lockfile is a security regression, not a
backlog item:

- The scheduled re-audit (npm and Python) turns red; that red run is the actionable signal.
- Public deployment is blocked until the tree is advisory-free again.
- The fix is a normal tracked task through the gates (a patched, re-verified, re-audited lock)
  — never a suppression or an ignore entry.

---

## 5. Admitting a NEW package — provenance review

Prefer an already-admitted dependency or the standard library over a new package. Before adding
any new dependency, a human reviewer (G5 security review) records and checks:

- **Name** — guard against typosquats / confusable names; confirm it is the intended package.
- **Maintainers / ownership** — who publishes it; any recent ownership or maintainer change
  (a common supply-chain compromise vector).
- **Lifecycle scripts** — does it run `preinstall`/`install`/`postinstall` scripts? Justify and
  scrutinise any that do. (`ignore-scripts` posture is preferred where feasible.)
- **Registry origin** — published from the official registry, not a mirror or a git/URL source.
- **Publication date** — satisfies the 7-day age rule; not a brand-new release.
- **Necessity** — why an existing dependency or stdlib cannot do the job.

A new dependency is a G5-reviewed change like any other; it inherits every rule in §1.

---

## 6. Emergency exception — AGE REQUIREMENT ONLY, owner-authorized

There is exactly one narrow exception, and it applies to the **7-day age requirement ONLY**. It
can **never** waive an advisory affecting the installed version, an integrity mismatch, an
unexpected host, or any other fail-closed condition.

- **Authority:** owner only. No agent may create, approve, or apply an age exception. The
  machine gates (`dependency_age_gate.mjs` / `.py`) contain no exception path, so a "paper"
  exception cannot make a gate pass — the owner action happens outside the tool and the gate is
  only satisfied once real registry time proves the age.
- **Scope:** a single, named `package==version`. No wildcard, no org-wide, no
  category-wide, no permanent, and no undocumented exception.
- **Record fields (all required):** package name + exact version; the exact age at the moment of
  the request; the specific business reason the wait cannot be met; the owner authorization; the
  issue/PR link; and an explicit auto-expiry.
- **Auto-expiry:** the exception expires automatically once the package reaches 7 complete days
  old (i.e., it can only ever shorten a wait that is about to end anyway), and never persists
  beyond that.
- **Still fully gated otherwise:** the package must still be advisory-free, integrity-matched,
  from the official registry, and pass every other check. An advisory or integrity/host/unverifiable
  condition is **never** exceptionable.

---

## 7. Enforcement map (files)

| Concern | npm (web) | Python (api) |
|---|---|---|
| Resolver-time age filter | `apps/web/.npmrc` (`min-release-age=7`, `save-exact=true`) | pinned `uv` + `--generate-hashes` locks |
| Committed-lock age gate (fail-closed) | `apps/web/scripts/dependency_age_gate.mjs` + `scripts/tests/**` | `services/api/scripts/dependency_age_gate.py` + `scripts/tests/**` |
| Application advisory audit (blocking) | `npm audit --audit-level=low` + JSON total==0 | `pip-audit -r requirements.txt --strict` |
| Tooling advisory audit (blocking) | `... --npm-cli-advisory 11.18.0` | `pip-audit -r requirements-tools.lock --strict` |
| Runs on every push/PR | `web-dependency-security` job (`.github/workflows/ci.yml`) | `exact-production-install` / lock-verify jobs |
| Scheduled re-audit | `.github/workflows/scheduled-web-audit.yml` | `.github/workflows/scheduled-audit.yml` |
| Lock (re)generation (no local install) | `.github/workflows/generate-lockfile.yml` (pinned npm 11.18.0, validates before commit) | pinned-`uv` lock scripts |

Do not modify a gate's behaviour (weaken a check, add a suppression, make it warning-only)
without an explicit G5 security review. SHA-pin every third-party GitHub Action.
