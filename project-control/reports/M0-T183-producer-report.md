# M0-T183 producer report

Task: clean-up after the one-time owner-authorized age exception for `source-map-js` 1.2.2
(owner directive D-092, requirement D-092-R016). The exception, added by task M0-T182 in commit
`8fe57ca0`, stopped applying by itself at `2026-10-07T14:08:09.382Z` (the version reached
604800 s). This task removes the installer exclusion and the checker's exception mechanism, and
brings the policy text back into line while keeping the dated record.

Producer: frontend-engineer, isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a88aaa82f22e48bde`.
Contract head reset to `950bd4ca3a35779ab0fc3271ec97cb69322d96bf`; no package installed, no
lockfile regenerated.

No other commit touched the three code files between `8fe57ca0` and HEAD
(`git log --oneline 8fe57ca0..HEAD -- <the three files>` is empty), so `8fe57ca0`'s only change
to each was the exception, and restoring to `8fe57ca0^` removes exactly the exception.

## What was removed, per file

### apps/web/.npmrc
Removed the trailing blank line, the six-line D-092 comment block, and the
`min-release-age-exclude[]=source-map-js` line that `8fe57ca0` added. The file now equals its
content at `8fe57ca0^`: `min-release-age=7`, `save-exact=true`, `package-lock=true` unchanged
(S1). Restored with `git checkout 8fe57ca0^ -- apps/web/.npmrc`.

### apps/web/scripts/dependency_age_gate.mjs
Removed the whole exception mechanism that `8fe57ca0` added: the `OWNER_AGE_EXCEPTION` entry in
the `Kind` enum; the frozen `OWNER_AGE_EXCEPTIONS` list; the `matchOwnerAgeException()` function;
the exception branch in `decide()`; the `owner_age_exception` arm of `result()`'s `passed`; the
`>>> OWNER AGE EXCEPTION ... <<<` branch in `formatResult()`; the `exceptions` counter and the
alternate PASS summary in `run()`; and the two header-comment changes (the "AGE-ONLY OWNER
EXCEPTION" block, and the reword of "no allowlist/exception" / "no exception path"). The file now
equals its content at `8fe57ca0^` (S2). Restored with `git checkout 8fe57ca0^ -- <file>`.

### apps/web/scripts/tests/dependency_age_gate.test.mjs
Removed the three added imports (`formatResult`, `OWNER_AGE_EXCEPTIONS`,
`matchOwnerAgeException`) and the entire S1..S8 exception test block (~208 lines). The remaining
40 tests, including the 604800/604799 boundary tests, are the pre-exception suite and all pass.
The file now equals its content at `8fe57ca0^` (S2). Restored with `git checkout 8fe57ca0^ -- <file>`.

### docs/DEPENDENCY_SECURITY_POLICY.md (surgical edits; nothing else changed)
- Section 5 "No agent waiver" paragraph restored to its pre-`8fe57ca0` sentence.
  - Old: "...downgrade to any gate, and no agent may add an exception of any kind. The advisory
    gates contain no exception path whatsoever; the Python age gate contains none. The npm
    committed-lock age gate has exactly one mechanism: ... (section 6). An advisory, an integrity
    mismatch, an unexpected host, or any unverifiable condition is **never** exceptionable."
  - New: "...downgrade to any gate. The age/advisory gates contain no exception path whatsoever."
- Section 2(b) enforcement passage restored.
  - Old: "...and has **no** allowlist and **no** suppression. Its only exception path is the
    age-only owner mechanism of section 6: a frozen, owner-authorized `OWNER_AGE_EXCEPTIONS`
    entry ... This is what stops a hand-edited lock."
  - New: "...and has **no** allowlist/suppression/exception. This is what stops a hand-edited lock."
- Section 6 "Authority" bullet restored to its pre-`8fe57ca0` text, plus the one sentence R016 asks for.
  - Old: "owner only. No agent may create, approve, apply, or widen an age exception. The Python
    machine gate ... contains no exception path at all. The npm machine gate ... has exactly one
    mechanism: a frozen, owner-authorized `OWNER_AGE_EXCEPTIONS` entry ... never makes the gate
    pass on an advisory, an integrity mismatch, an unexpected host, or any other fail-closed
    condition."
  - New: "owner only. No agent may create, approve, or apply an age exception. The machine gates
    (`dependency_age_gate.mjs` / `.py`) contain no exception path, so a "paper" exception cannot
    make a gate pass — the owner action happens outside the tool and the gate is only satisfied
    once real registry time proves the age. An approved exception is implemented by a reviewed
    change to the gate that carries its own expiry and is removed by a second reviewed change, as
    owner directive D-092 was (tasks M0-T182 and M0-T183)."
- Table "Exceptions on record": the `source-map-js` 1.2.2 row STAYS (the dated record); only its
  Clean-up cell changed.
  - Old: "task M0-T183 removes the `.npmrc` `min-release-age-exclude[]=source-map-js` line and the
    `OWNER_AGE_EXCEPTIONS` entry after expiry"
  - New: "task M0-T183 removed the `.npmrc` `min-release-age-exclude[]=source-map-js` line and the
    checker's `OWNER_AGE_EXCEPTIONS` exception on 2026-10-07, after the expiry"
- Section 7 enforcement map: the two temporary parentheticals removed, earlier form restored.
  - Resolver-time age filter (npm): dropped "; plus the temporary
    `min-release-age-exclude[]=source-map-js`, D-092, removed by M0-T183" → back to
    "`apps/web/.npmrc` (`min-release-age=7`, `save-exact=true`)".
  - Committed-lock age gate: dropped "(one owner age exception, section 6)" from the npm cell and
    "(no exception path)" from the Python cell → both back to the bare file paths.

Nothing in the policy lets an agent grant an exception: the restored Authority rule is
owner-only, and the one added sentence describes an owner-authorized, reviewed, self-expiring
change (as D-092 was).

## Check c — three-file comparison with `8fe57ca0^`
`git diff --stat 8fe57ca0^ -- apps/web/.npmrc apps/web/scripts/dependency_age_gate.mjs
apps/web/scripts/tests/dependency_age_gate.test.mjs` printed **empty**, exit 0. All three files
are byte-identical to their pre-exception content. No line of `8fe57ca0` was kept: every line it
added to these files was part of the exception.

## Live age-gate run (check b, run once, reads the npm registry)
`cd apps/web && node scripts/dependency_age_gate.mjs package-lock.json`, exit **0**. Header:
`now=2026-10-07T15:10:49.000Z, min_age=604800s`; 392 unique registry packages, every one an
ordinary PASS. The line for the subject package:

```
  PASS  source-map-js@1.2.2  uploaded=2026-09-30T14:08:09.382Z  age=608559s (7.04d)
```

Registry publication time read: `2026-09-30T14:08:09.382Z`; age `608559 s` (>= 604800 s), so the
ordinary OK path admits it — no exception line, no `owner_age_exception`, nowhere in the output
(a grep of the output for "exception"/"owner_age" matched nothing). Summary line:

```
RESULT: PASS — every committed registry package is >= 7 days old and integrity-verified
```

This is the plain PASS summary (not the exception-count variant), confirming S3: the ordinary
rule now decides. The run was executed after the expiry instant 2026-10-07T14:08:09.382Z.

## Checks with DIRECT exit codes
- a. `node --test scripts/tests/*.test.mjs` (from apps/web): exit **0**, 40 tests pass, 0 fail,
  0 skipped. NOTE: the packet's shorthand `node --test scripts/tests/` (trailing-slash directory)
  does NOT glob on this server's node v22.23.3 — it tries to load `scripts/tests` as a module and
  exits 1 (an invocation artifact, not a defect). I used the authoritative CI form
  (`.github/workflows/ci.yml` line 159 and `npm run depage:test`): `node --test
  scripts/tests/*.test.mjs`.
- b. live age gate, from apps/web: exit **0** (see above; 392 packages, all PASS).
- c. `git diff --stat 8fe57ca0^ -- <the three files>`: exit **0**, output empty.
- d. `grep -n -i "OWNER_AGE_EXCEPTIONS\|owner_age_exception\|matchOwnerAgeException\|
  min-release-age-exclude" -r apps/web/.npmrc apps/web/scripts
  docs/DEPENDENCY_SECURITY_POLICY.md`: exit **0**, exactly ONE match — the dated record cell in
  the policy table (which names what was removed). Nothing in `.npmrc` or `scripts`.
- e. `git diff --stat 950bd4ca... -- apps/web/package.json apps/web/package-lock.json .github`:
  exit **0**, output empty (the pin, the lockfile and every workflow file are untouched).
- f. web checks from apps/web (lockfile packages only):
  - `npx --yes npm@11.18.0 ci --no-audit --no-fund`: exit **0**.
  - `npm run lint`: exit **0** (0 errors; 2 pre-existing warnings in unrelated
    `src/lib/study/__tests__` files, not touched by this task).
  - `npm run typecheck`: exit **0**.
  - `npm run test` (vitest): exit **0**, 111 files / 2423 tests passed.
  - `npm run build`: exit **0**, compiled successfully, 8/8 static pages. (No e2e run needed: no
    website source file changed.)
- g. `git status --porcelain` and `git diff --name-status 950bd4ca... HEAD`: only the four files
  and this report; `apps/web/node_modules` is git-ignored and does not show. (Recorded after the
  commit; see the return message.)

## Doubt / disclosure
- One invocation artifact only: check a's packet shorthand needs the glob form on node v22.23.3
  (recorded above). The gate's behaviour is unchanged; the authoritative CI job runs the glob
  form.
- No package was added, removed or updated; the lockfile was not regenerated. The `source-map-js`
  1.2.2 pin and its integrity in `apps/web/package.json` and `package-lock.json` are byte-unchanged.
- CI on the pushed head stays the final word (web behaviour is never declared verified from
  reasoning alone).
