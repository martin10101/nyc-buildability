# M0-T047 — G3 code review (VERBATIM reviewer return)

Independent reviewer: `code-reviewer` (read-only; reviewer != producer orchestrator).
Returned via agent channel; saved verbatim.

---

I have all evidence needed. The read-only guard blocks inline interpreter execution and file writes (expected for a reviewer), but JSON validity is conclusively established by byte-identical blob parity with the CI-validated `7ac2f91` plus direct structural inspection. Here is my gate report.

---

# G3 Code Review — M0-T047 (nanoid 3.3.17 remediation, GHSA-2v37-7h3g-55p8)

**Reviewed SHA:** `c032dfe54bc2c947d1b86b7f87988d658a04a6cd`
**Branch:** `control/session15-acceptance` (worktree HEAD == reviewed SHA, confirmed)
**Parity target:** PR #219 tip `7ac2f91`
**Reviewer:** code-reviewer (independent, read-only)

## Scope of change

`git show c032dfe --stat` reports **3 files**, not 2:

| File | Change |
|---|---|
| `apps/web/package.json` | +1/-1: adds `"nanoid": "3.3.17"` to `overrides` |
| `apps/web/package-lock.json` | +3/-3: `node_modules/nanoid` `3.3.16 → 3.3.17` (version + resolved + integrity) |
| `project-control/reports/M0-T047-producer-report.md` | **NEW** (+44): producer evidence report |

## Criterion-by-criterion findings

**1. "Exactly the nanoid change (2 files, nothing else)" — MOSTLY MET, with one noted deviation.**
- The technical remediation is exactly the 2 named files. The full diff was read: no other package, dependency, lockfile entry, workflow, CI config, or policy file changed. The lockfile hunk touches only the nanoid node (version/resolved/integrity); the package.json hunk touches only the added override line.
- **Deviation:** the commit also adds a **third** file, `project-control/reports/M0-T047-producer-report.md`. This is a control-plane *evidence* document (disclosed in the commit message: "+ producer report"), not a code/dependency/lockfile/workflow/policy change. Its full content was read: it describes the change and D-009 posture and correctly defers age-gate authority to the fresh #220 dependency-security CI ("acceptance is contingent on the fresh #220 ... CI being green"). It makes no build-affecting, schema, or legal claim. The parenthetical guard of criterion #1 (no other package/dependency/lockfile/workflow/policy file changed) is satisfied; only the literal file count differs. Flagged for the orchestrator to record consciously.

**2. Blob parity with #219 tip `7ac2f91` — PASS (byte-identical).**
```
c032dfe:apps/web/package.json      = 90e801ae167cf2805d1cafa98289eedd5f58ca47
7ac2f91:apps/web/package.json      = 90e801ae167cf2805d1cafa98289eedd5f58ca47   MATCH
c032dfe:apps/web/package-lock.json = 6e75bff6e7fe519fe547046b1b2565dba8bd0ef9
7ac2f91:apps/web/package-lock.json = 6e75bff6e7fe519fe547046b1b2565dba8bd0ef9   MATCH
```
`git diff c032dfe 7ac2f91 -- apps/web/package.json apps/web/package-lock.json` → empty (exit 0). Both technical files are byte-identical to the CI-validated #219.

**3. Exact pin + lock integrity — PASS.**
- `overrides.nanoid` is the literal string `"3.3.17"` (no `^`/`~`/range). Adjacent overrides (`postcss`, `sharp`, `brace-expansion`, `js-yaml`) are unchanged.
- Lock records for `node_modules/nanoid`: `version 3.3.17`, `resolved https://registry.npmjs.org/nanoid/-/nanoid-3.3.17.tgz`, `integrity sha512-xQLf0A3HOMlgHq0n247/LRuAOYmB7dXJ/DvAxGvsSBij45XtBSmQycu+F8ODbHwns/XyFZagyL1+J0Offw1E0g==` (matches the contract prefix `sha512-xQLf0A3…`). Independent registry-integrity/age validation is the dependency-security CI's job (G5), not G3; parity to #219 means it is the same artifact that already passed those jobs.

**4. Single resolved version + valid JSON — PASS.**
- Every `nanoid` occurrence in the lock enumerated: exactly one installed node `node_modules/nanoid` @ `3.3.17` (line 6237). The other two matches are non-duplicates: the package's own `bin` entry `"nanoid": "bin/nanoid.cjs"` (6249) and a dependent's requirement `"nanoid": "^3.3.16"` (6718), which `3.3.17` satisfies. No nested/split/duplicate nanoid node exists.
- JSON validity: the `overrides` block is structurally well-formed (correct commas/closing brace, verified by inspection), and both files are **byte-identical** to `7ac2f91`, which passed #219 CI (npm install/audit against the lockfile fails on malformed JSON). Direct parser execution was blocked by the read-only guard; validity is established by blob identity to the CI-validated tree.

## Notes / limitations
- The read-only guard correctly blocked inline `node -e` / `python -c` and all file writes. No conclusion depended on those; every material fact was verified via read-only git inspection and blob-hash identity.
- G3 scope is code/lockfile correctness and parity. The 7-day age gate and live registry-advisory/integrity checks are G5/dependency-security-CI responsibilities; acceptance remains contingent on the fresh #220 `web-dependency-security` run being green at today's date (2026-08-11), as the producer report itself states.

## Verdict rationale
All four acceptance criteria are satisfied on substance: the remediation is byte-identical to the CI-validated #219, exact-pinned, integrity-recorded, single-resolved, and valid JSON, with no unexpected package/dependency/lockfile/workflow/policy change. The only deviation from the contract wording is one additional, disclosed, non-code control-plane producer-report file — which does not compromise any acceptance concern. I flag it explicitly for the ledger but do not treat it as gate-blocking.

VERDICT: PASS
