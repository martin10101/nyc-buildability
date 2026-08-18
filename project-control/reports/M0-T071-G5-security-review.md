VERDICT: PASS

# G5 Security Review — M0-T071 (D-015): transitive nanoid 3.3.17 → 3.3.18

**Task:** Bounded dependency-security repair — transitive `nanoid` 3.3.17 → 3.3.18 (GHSA-2v37-7h3g-55p8), directive D-015, closes B-019.
**Reviewed SHA (frozen):** `e7c7d37745e35c56abb39f854bc14c44d6e87723` — verified equal to the required head.
**Base:** parent is `5c71fe0e08c8717cc20ac232d8bd0d8a328525e1` (origin/main, PR #221 merge). Single-parent commit — not a merge, unstacked directly on origin/main.
**Reviewer:** security-reviewer (independent, read-only); all conclusions independently re-derived from source (registry, GitHub advisory DB, the committed lock, and the machine age gate). Producer reports treated as unverified claims.

## Scope of the diff (13 files)
- `apps/web/package-lock.json` — single `node_modules/nanoid` entry: version/resolved/integrity 3.3.17 → 3.3.18. No other package touched.
- `apps/web/package.json` — one line: `overrides.nanoid` 3.3.17 → 3.3.18. No `dependencies`/`devDependencies`/`scripts` change.
- Control-plane records (D-015 directive capture, M0-T071 task/gate/reports, `directives/index.json`, `state.json`) — governance bookkeeping; no runtime or security-config effect.

## Findings by severity
- **SEC-CRITICAL:** none.
- **SEC-MAJOR:** none.
- **SEC-MINOR:** none.
- **SEC-INFO-1:** `apps/web/.npmrc` does not set `ignore-scripts=true`; it relies on the owner's machine-global `ignore-scripts` policy. This is **unchanged base state** (byte-identical diff) and out of scope for this task. Mitigant: nanoid 3.3.18 declares **no** `scripts` object in its published metadata (no preinstall/postinstall/install hook), so this bump introduces no install-time script surface. `.npmrc` retains `package-lock=true`, `save-exact=true`, `min-release-age=7`.
- **SEC-INFO-2:** `npm audit` emits `npm warn Unknown project config "min-release-age"` — a benign, pre-existing npm-version warning about the custom resolver-time key; not introduced by this change and not a suppression.

## Reproduced evidence

**Supply-chain integrity (artifact-level, byte-for-byte):**
- Lock integrity = `sha512-DTg4MJbGMWkfi6VZFdNt2/caMbQy4Ou+Op/hJQvGEWcnVfoA1QA+xzRKAzw9jD6+GVOOeYr/mIcuDSdug6F6+w==`
- npm registry `dist.integrity` for 3.3.18 (`https://registry.npmjs.org/nanoid/3.3.18`) = **identical**.
- Downloaded the actual tarball and computed its SRI: `openssl dgst -sha512 -binary | base64` = **identical** to lock and registry; sha1 shasum `f66a2de1199ffde0fcf21c8a5f13106b1c081913` = registry `dist.shasum`. (This is the same guarantee `npm ci` enforces; it fails closed on any mismatch.)
- `resolved` = `https://registry.npmjs.org/nanoid/-/nanoid-3.3.18.tgz` — genuine registry, no substitute registry, no git/tarball URL.
- Registry provenance: published via GitHub OIDC trusted publisher, SLSA provenance attestation + signature present.

**Advisory posture (GitHub advisory DB — authoritative; all four npm nanoid advisories):**
- GHSA-2v37-7h3g-55p8 (high, CVE-2026-67213): 3.x range `< 3.3.18`, first patched `3.3.18` → 3.3.18 **not** vulnerable.
- GHSA-28wg-ghj8-5hjv (high): `< 3.3.16` → patched.
- GHSA-mwcw-c2x4-8c55 (medium): `< 3.3.8` → patched.
- GHSA-qrpm-p2h7-hrv2 (medium): `>= 3.0.0, < 3.1.31` → patched.
- The 4.x/5.x ranges (`>= 4.0.0`) do not apply — installed line is 3.3.18.
- `npm audit --package-lock-only --json`: info 0 / low 0 / moderate 0 / high 0 / critical 0 / **total 0** across 560 audited deps. `npm audit --audit-level=low` → `found 0 vulnerabilities`.

**Age gate (machine gate, run on committed lock):**
- `node scripts/dependency_age_gate.mjs package-lock.json` → `RESULT: PASS — every committed registry package is >= 7 days old and integrity-verified` (549 unique registry packages).
- `PASS nanoid@3.3.18 uploaded=2026-08-07T16:41:05.696Z age=918482s (10.63d)` — ≥ 604800 s.
- The age-gate script is **byte-identical** to base (empty diff); reading it confirms no allowlist, no `--ignore`, no suppression, no exception path exists in the tool.

**No weakening / no suppression added:**
- `.npmrc` (apps/web) — **byte-identical** (empty diff).
- No changes under `.github/**` (CI gates unchanged), `tools/agent_supervisor/**`, `scripts/**`, or any `settings.json`/`settings.local.json`/permissions file (path-scoped diff returned empty).
- No waiver/exception/allowlist/audit-suppression file added anywhere; every `waiver`/`suppress`/`allowlist` string in the diff is **prohibition text** inside D-015 records (D-015-R... prohibitions stating no waiver is requested/authorized/used).

**Prohibition & scope sweep:**
- No `project-control/tasks/M0-T070.json` or `D-014-*` file is modified — those names appear only as prohibition/context text inside the D-015 records.
- Single-parent commit on origin/main; nothing merged; branch deliberately unstacked.
- `directives/index.json` preserves all base directives (D-001…D-012) and appends only D-015 (reindent-only churn otherwise); `state.json` adds M0-T071 to `active_tasks` + timestamp. No security effect.

## Explicit answers
1. **Is the integrity hash genuine and registry-verified?** **YES.** Lock SRI matches the npm registry's published `dist.integrity` for 3.3.18 byte-for-byte, and matches the recomputed sha512 of the actual downloaded tarball (and sha1 shasum). `resolved` points at registry.npmjs.org.
2. **Is 3.3.18 advisory-free at every severity?** **YES.** Outside every vulnerable range of all four nanoid npm advisories (2 high, 2 medium); `npm audit` JSON = 0 at info/low/moderate/high/critical.
3. **Does the age gate pass with no waiver and no suppression added?** **YES.** Machine gate PASS at age 918482 s (> 604800 s); `.npmrc` and the age-gate script are byte-identical to base; no waiver/exception/allowlist/audit-suppression file added or modified.
4. **Is any gate, config, or policy file weakened?** **NO.** `.github/`, supervisor, `.npmrc`, scripts, and settings/permissions are all untouched; `package.json` changed only the `overrides.nanoid` value (no new dependency, no script).
5. **Does the diff stay inside the authorized scope?** **YES.** Two implementation lines (lock + override) plus D-015/M0-T071 control-plane records; no M0-T070/D-014 surface modified; single-parent, unstacked on origin/main; nothing merged.

**Recommendation to orchestrator:** record G5 = **PASS**.
