# M0-T182 producer report

Commit sha: the single commit of task M0-T182 on branch
`task/M0-T182-source-map-js-one-time-age-exception` (reported to the orchestrator in the producer
return; a committed report cannot self-reference its own final sha).

## Files changed (vs 035d7596)

- `apps/web/package.json` (+1 line): `overrides` gains `"source-map-js": "1.2.2"`; nothing else.
- `apps/web/.npmrc` (+8 lines): one setting `min-release-age-exclude[]=source-map-js` plus a
  comment naming D-092, the expiry and clean-up task M0-T183; the three existing settings untouched.
- `apps/web/scripts/dependency_age_gate.mjs` (+106/-16 in the stat): `Kind.OWNER_AGE_EXCEPTION`;
  frozen exported `OWNER_AGE_EXCEPTIONS` (one entry); `matchOwnerAgeException()`; one new branch in
  `decide()`; `result().passed` and `formatResult`/`run` extended to treat the exception as a pass
  and print it on its own loud line; header comment made true. 494 -> 584 lines.
- `apps/web/scripts/tests/dependency_age_gate.test.mjs` (+208, 0 removed): S1-S8 tests appended; two
  imports inserted. No existing test touched.
- `docs/DEPENDENCY_SECURITY_POLICY.md` (+39/-~8): sections 1, 2(b), 6 (+ "Exceptions on record"
  table) and 7 made true.
- `project-control/reports/M0-T182-producer-report.md`: this report.

## Scenario evidence

- S1 (exception_applies): tests `S1 exception_applies: distinct owner-exception kind...` and
  `S1 exception_applies: run() exits 0 and prints the exception on its own marked line`. Gate: the
  new `decide()` branch returns `Kind.OWNER_AGE_EXCEPTION`; `result()` marks it `passed:true`;
  `formatResult` prints `>>> OWNER AGE EXCEPTION (D-092) PASS ... age=<n>s expires=<instant> <<<`.
- S2 (boundary): test `S2 boundary: 604799s -> exception; 604800s -> plain ok; another package...`.
  604800 returns OK (the `>= MIN_AGE_SECONDS` branch fires first); 604799 the exception; another
  name at 604799 TOO_NEW.
- S3 (other_version): test `S3 other_version: source-map-js@1.2.3 ... -> too_new`. The version
  condition in `matchOwnerAgeException`.
- S4 (other_package): test `S4 other_package: a different name at 1.2.2 ... -> too_new`. The name
  condition.
- S5 (integrity_binding): test `S5 integrity_binding: (a) lock!=registry -> integrity_mismatch;
  (b) agree but != recorded -> too_new`. (a) is caught by the existing integrity check before the
  branch; (b) by the integrity condition in the matcher.
- S6 (publication_time_binding): test `S6 publication_time_binding: wrong time -> too_new;
  missing/malformed -> missing_timestamp; future -> too_new`. The publication-instant condition,
  the existing timestamp checks, and the `ageSeconds >= 0` guard. Age is always computed from the
  registry time and injected `now`; `published` is only compared.
- S7 (fail_closed_unchanged): tests `S7 fail_closed_unchanged: ... every bad condition` and
  `... provider outage is infrastructure_unavailable`. Every fail-closed check returns before the
  age branch, so the excepted name@version never reaches the exception on a bad condition.
- S8 (single_entry_pin): test `S8 single_entry_pin: exactly one frozen entry ...`. `deepEqual`
  against the one `{source-map-js,1.2.2,integrity,published,D-092}`; `Object.isFrozen` on list and
  entry; push/mutate throw.
- S9 (no_other_behaviour_change): self-check 3 shows 0 removed test lines; all 40 pre-existing
  tests still pass inside the 50; gate deletions are only behavior-preserving rewrites of the
  header comment, `result().passed`, `formatResult` and the `run` summary; `MIN_AGE_SECONDS`, the
  host/integrity checks, retry logic and the npm-CLI advisory code are unchanged; imports stay Node
  built-ins only (`node:fs/https/process/timers/url`).
- S10 (installer_setting): `apps/web/.npmrc` has exactly one added setting
  `min-release-age-exclude[]=source-map-js`; `min-release-age=7`, `save-exact=true`,
  `package-lock=true` unchanged; comment names D-092, expiry and M0-T183.
- S11 (pin_and_lock): orchestrator (lockfile workflow).
- S12 (all_checks_on_the_change): orchestrator (CI on the post-lock head).
- S13 (policy_text): `docs/DEPENDENCY_SECURITY_POLICY.md` sections 1, 2(b), 6 and 7 and the gate
  header comment no longer claim "no exception path"; they state the one owner-authorized
  name@version mechanism bound to registry integrity and publication time, usable only below
  604800 s, each needing owner approval + directive record + G5 review, with advisory/integrity/
  host/unverifiable never exceptionable; the "Exceptions on record" table carries the required
  fields (age 487485 s; reason none given; D-092 message 84; PR/branch; expiry
  2026-10-07T14:08:09.382Z; clean-up M0-T183).

## Self-check results

1. `node --test scripts/tests/*.test.mjs`: before the change `# tests 40 / # pass 40 / # fail 0`;
   after the change `# tests 50 / # pass 50 / # fail 0`.
2. `git diff --stat 035d7596`: the five material files + this report, nothing else.
3. `git diff 035d7596 -- .../dependency_age_gate.test.mjs | grep -c '^-[^-]'` = `0`.
4. Red/green (one condition removed at a time, then restored):
   - (a) version condition removed -> only `not ok ... S3 other_version ...` (# fail 1).
   - (b) integrity condition removed -> only `not ok ... S5 integrity_binding ...` (# fail 1).
   - (c) publication condition removed -> only `not ok ... S6 publication_time_binding ...`
     (# fail 1).
   - restored -> `# pass 50 / # fail 0`.
5. `tools/modularity_check.py --check`: exit `0` (failures 0; the gate file is not flagged).

## Not done / differed / doubts

- Lockfile (S11), CI (S12) and the registry-fact re-verification are the orchestrator's; I ran no
  `npm`/`npx`/installer and did not touch `package-lock.json`, per the packet.
- ESLint was not run locally (it needs an install the packet forbids); the new test regexes use no
  double spaces and no control characters per CODING_RULES. CI lint is the final word.
- All directive registry facts (integrity, publication instant, expiry, age 487485 s) matched the
  inputs exactly; no BLOCKED condition (S14) arose.
- Doubt for reviewers: I made the `run()` PASS summary line mention the count of owner exceptions
  so it is not falsely claiming "every package >= 7 days old" when one is admitted early. This is a
  truthfulness adjustment within the reporting path, not a weakening of any check; please confirm it
  is acceptable (exit code and pass semantics are unchanged).
