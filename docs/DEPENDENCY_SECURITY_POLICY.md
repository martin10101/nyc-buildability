# Dependency Security Policy

**Status:** Permanent operating policy (owner directive 2026-07-20, P0).
**Scope:** Every dependency in every ecosystem in this repository — currently the
npm tree under `apps/web/` and the Python trees under `services/api/`. Any
ecosystem added later is bound by this policy from its first dependency.
**Authority:** This policy is owner-authorized and machine-enforced. No agent may
waive, relax, or grant an exception to any part of it. Only the owner may
authorize the single narrow exception defined in the "Emergency exception"
section, and even that never covers an advisory.

This policy exists so that a future lockfile change — by an agent, a bot, or a
person — cannot silently reintroduce a vulnerable, too-new, or unvetted package.

---

## 1. Advisory-free dependency tree (all classes, all transitives)

The complete dependency tree must be free of known security advisories against
the installed versions. This applies to **every class of dependency**, not only
runtime:

- runtime / production dependencies,
- development and test tooling,
- build tooling,
- lockfile-generation tooling,
- audit tooling itself,
- and **every transitive dependency** of all of the above.

A "known advisory" means any advisory at any severity (including `info`/`low`)
that affects the installed version, as reported by the ecosystem's audit tool
(npm audit's advisory database for npm; PyPI Advisory Database / OSV via
pip-audit for Python).

There is **no allowlist, no ignore list, no `--ignore-vuln`, no `--ignore`, no
warning-only downgrade, and no severity threshold below which a finding is
tolerated.** A finding fails the build.

## 2. Minimum publication age — 7 complete days

Every package that is admitted through the ordinary process must have been
published to its registry at least **7 complete days (604800 seconds)** before it
is admitted. This blunts the window in which a freshly published (possibly
compromised or hijacked) version can enter the tree before the community and
scanners have had time to react.

The age requirement is enforced **fail-closed** in CI in both ecosystems:

- **npm:** `apps/web/.npmrc` sets `min-release-age=7`. `min-release-age` was
  introduced in **npm 11.10.0**, so CI pins **npm 11.18.0** everywhere a lock is
  generated or installed (see Section 6). When npm resolves or regenerates the
  lock it refuses to select any version younger than 7 days. No
  `min-release-age-exclude` entry exists, and none may be added — an exclusion
  would carve a hole in this rule.
- **Python:** `services/api/scripts/dependency_age_gate.py` reads live PyPI
  metadata and PyPI's own UTC clock and fails the build if any admitted artifact
  in `services/api/requirements.txt` or `services/api/requirements-tools.lock`
  (direct **or** transitive) is younger than 604800 seconds or cannot be
  verified.

The producer of any dependency change must record, in the task report, the exact
publication date/time (UTC) and the official registry/advisory source URL for
every directly changed or overridden package, and must confirm each ordinarily
admitted package is at least 7 days old before the change is committed. If the
registry or advisory state has changed since the task was contracted, the
producer must **STOP and report** — never silently substitute a different
version.

## 3. Exact version pins + committed lockfile integrity

Dependencies are pinned exactly and installed only from a committed lockfile
that is verified on install:

- **npm:** direct dependencies that this policy tracks are pinned as exact
  strings in `apps/web/package.json` (no `^`/`~`); `apps/web/.npmrc` sets
  `save-exact=true`; the full transitive closure is frozen in
  `apps/web/package-lock.json`; CI installs with `npm ci`, which fails if
  `package.json` and the lockfile disagree and verifies every package's
  integrity hash. Cross-package version control (e.g. forcing a transitive to a
  fixed patched version) uses the top-level `overrides` map in
  `apps/web/package.json`.
- **Python:** `services/api/requirements.txt` (production runtime) and
  `services/api/requirements-tools.lock` (tooling) are fully hash-pinned uv
  locks installed with `pip install --require-hashes`, so every artifact's hash
  is verified and no range is ever resolved at install time.

The lockfile is authoritative and is regenerated only on a CI runner (never on
the owner's thin-client PC, per `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`).
For npm, regeneration runs under the pinned npm 11.18.0 so `.npmrc`
(`min-release-age`, the `overrides`) is honored.

## 4. Blocking audits on every change AND on a schedule

Audits run in two places in both ecosystems and are **blocking** in all of them:

- **On every change (push / pull request):**
  - **npm:** the `web` job in `.github/workflows/ci.yml` runs
    `npm audit --audit-level=low` **and** a JSON parse
    (`npm audit --json`) that fails the job unless
    `metadata.vulnerabilities.total == 0`. Dev dependencies are included. `npm
    ci` itself stays `--no-audit` (so the install is deterministic) and this
    explicit blocking audit is the gate immediately after it.
  - **Python:** the `exact-production-install` job in
    `.github/workflows/ci.yml` runs `pip-audit -r requirements.txt --no-deps
    --strict` and `pip-audit -r requirements-tools.lock --no-deps --strict`, both
    blocking at every severity, plus the release-age gate over both locks.
- **On a schedule (so a newly disclosed advisory against an already-merged lock
  turns a run red even when nothing changed):**
  - **npm:** `.github/workflows/scheduled-npm-audit.yml` (daily cron +
    `pull_request` on the web dependency artifacts + `workflow_dispatch`) reruns
    the identical blocking audit.
  - **Python:** `.github/workflows/scheduled-audit.yml` (daily cron + PR on the
    Python dependency artifacts + `workflow_dispatch`) reruns the dual blocking
    pip-audit and the release-age gate.

A red scheduled run is the actionable signal; notification routing is wired at
the repository level.

## 5. A post-merge advisory reopens security work and blocks deploy

A new advisory disclosed **after** a lockfile has already merged, and which
affects an installed (already-pinned) version, is a security regression. When the
scheduled audit (or any audit) turns red for such an advisory:

- security work is **reopened** (a new tracked task, not a silent edit),
- **deploy is blocked** until the advisory is cleared by moving to a patched,
  advisory-free version that itself satisfies this policy (age, pins, audit),
- and the fix follows the normal producer → independent gate flow.

No agent may mark the tree clean, waive the finding, or deploy over it.

## 6. CI tooling is pinned

Because the enforcement depends on tool behavior, the tools are pinned:

- **npm 11.18.0** is installed and version-checked (the step fails if the pin did
  not take effect) in the `web` and `web-e2e` jobs of
  `.github/workflows/ci.yml`, in `.github/workflows/generate-lockfile.yml`
  (before lock regeneration), and in `.github/workflows/scheduled-npm-audit.yml`.
  npm 11.18.0 is required because `min-release-age` only exists from npm 11.10.0.
- **Python audit/lock tooling** (uv, pip-audit, pytest, …) is itself
  hash-pinned in `services/api/requirements-tools.lock` and installed with
  `--require-hashes`, and the tooling lock is audited and age-gated exactly like
  the runtime lock.

The pinned tooling versions are themselves subject to Sections 1 and 2 (they must
be advisory-free and at least 7 days old).

## 7. New-package provenance review before admission

Adding a **new** package (in any ecosystem) requires an explicit provenance
review before it is admitted, in addition to Sections 1–3. The review must check
and record:

- **Name / typo-squat check** — the exact package name is the intended one and is
  not a look-alike of a popular package.
- **Maintainers and ownership-change history** — who publishes it and whether
  ownership or publish rights changed recently (a red flag for hijack).
- **Install / lifecycle scripts** — any `postinstall`/`preinstall`/lifecycle
  scripts (npm) or build hooks (Python) are reviewed for what they execute.
- **Registry origin** — it comes from the official registry
  (registry.npmjs.org / PyPI), not an unexpected mirror or URL.
- **Publication date / age** — consistent with Section 2 (>= 7 days), and the
  version history is plausible (not a brand-new package with a single suspicious
  release).

**Prefer an existing dependency or the standard library over adding a new
package.** A new dependency is admitted only when no already-present dependency
or standard-library capability reasonably covers the need. Every new-package
admission is recorded with its provenance findings in the task report and passes
the normal independent security gate.

---

## Emergency exception (narrow, owner-only, auto-expiring)

There is exactly one exception mechanism, and it is deliberately narrow:

- **It may relax ONLY the 7-day release-age requirement (Section 2).** It may
  **never** relax an advisory (Section 1): a version carrying a known advisory
  affecting the installed version is never admitted, emergency or not.
- **It is owner-authorized only.** No agent may grant, assume, or act on an
  exception. An agent that believes an exception is needed must STOP and report
  to the owner.
- **It must be fully recorded**, including all of:
  - the exact package **name and version**,
  - the exact **reason** the sub-7-day version must be admitted now,
  - the **owner approver**,
  - the **timestamp** of approval (UTC),
  - and an explicit **expiry**.
- **It auto-expires** once the package reaches 7 days of age; at that point the
  ordinary rule applies again with no further action, and the exception must not
  be renewed to keep a package permanently exempt.
- **No wildcard, org-wide, permanent, or undocumented exceptions.** An exception
  is scoped to one named package+version for one bounded reason and window. A
  blanket exclusion (for example an `min-release-age-exclude` entry, or a
  standing allowlist) is prohibited.

An emergency exception changes nothing about audits: the blocking and scheduled
audits still run and still fail on any advisory.

---

## Enforcing files (index)

| Concern | npm | Python |
| --- | --- | --- |
| Exact pins / save-exact | `apps/web/package.json`, `apps/web/.npmrc` (`save-exact=true`) | `services/api/requirements.txt`, `services/api/requirements-tools.lock` (hash-pinned) |
| Release-age (>= 7 days) | `apps/web/.npmrc` (`min-release-age=7`, npm >= 11.10.0) | `services/api/scripts/dependency_age_gate.py` |
| Lockfile integrity on install | `apps/web/package-lock.json` via `npm ci` | `--require-hashes` installs |
| Blocking audit on every change | `web` job in `.github/workflows/ci.yml` | `exact-production-install` job in `.github/workflows/ci.yml` |
| Blocking audit on a schedule | `.github/workflows/scheduled-npm-audit.yml` | `.github/workflows/scheduled-audit.yml` |
| Pinned tooling | npm 11.18.0 (ci.yml, generate-lockfile.yml, scheduled-npm-audit.yml) | uv / pip-audit / pytest in `services/api/requirements-tools.lock` |
| Lock regeneration (CI-only) | `.github/workflows/generate-lockfile.yml` | `services/api/scripts/lock_requirements.sh`, `lock_tools.sh` |

This policy must stay consistent with those files. A change to enforcement must
update this document in the same task.
