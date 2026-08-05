# D-009 - source-001: Dependency-Security Governance Directive (owner, activated 2026-08-04)

A FRESH standing governance directive, issued and activated by the owner on 2026-08-04, on the strength of
the dependency-security policy the owner has already reviewed. This is NOT a reconstruction of any prior
directive and NOT 'owner-affirmed from a lost transcript' - it is a new directive the owner is activating
now (owner instruction quoted in manifest.owner_approval). The orchestrator drafted the text from the
reviewed policy; the owner is the issuer/activator (project-control rule 4: AI drafts, owner activates).

## Authorization {#authorization}

This directive AUTHORIZES the dependency-security implementation work - specifically task M0-T019, and
future dependency-admission work - to create and modify the governance-classed paths it requires,
namely `.github/workflows/` and `CLAUDE.md`, to implement the permanent dependency-admission rules below.

## Permanent dependency-admission rules {#rules}

1. No dependency (runtime, dev, build, or CI tooling) may carry an unresolved advisory affecting the
   installed version. Audits fail closed on any finding; no agent may waive an advisory.
2. Minimum release age is 7 days (min-release-age=7). Direct and dev dependencies are pinned to exact
   versions (save-exact); committed-lockfile integrity is retained.
3. Enforcement is machine-checked: a deterministic, fail-closed committed-lockfile release-age gate; a
   blocking dependency audit on every change; and a scheduled re-audit workflow. Never warning-only. A
   registry/network failure fails closed with a distinct `infrastructure_unavailable` result and is
   never treated as advisory-free.
4. New-package provenance review is required (name, maintainers, lifecycle scripts, registry origin,
   publication date, ownership changes); prefer existing dependencies / the standard library over new
   packages.
5. Emergency exception: age-requirement ONLY, never an advisory affecting the installed version,
   owner-authorized only, with a full record, auto-expiry at 7 days; no wildcard, org-wide, permanent,
   or undocumented exceptions.
6. The concise permanent dependency-security rule is recorded in `CLAUDE.md` so future orchestrators
   read it.

## Scope {#scope}

Authorizes M0-T019 (and future dependency-admission work) to implement the above, including edits to the
governance paths `.github/workflows/` and `CLAUDE.md`. Governance paths authorized: `.github/workflows/`,
`CLAUDE.md`.
