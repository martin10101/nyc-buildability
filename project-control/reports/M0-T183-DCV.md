# M0-T183 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `716bd7fd3ad541c2c022ac0c10b4ec4f7d44d572` (branch `task/M0-T183-age-exception-cleanup`, pull request 463, review copy `/root/project/rv-m0t183-a`). Owner directive D-092. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review.
Applicable row for this task (`evaluate_task_refs`: applicable == cited): D-092-R016 (1 row).

## Verdict: PASS for the row. No required correction blocks acceptance.

- **The row:** after the seven-day point a second, reviewed change removes the installer exclusion and the checker's exception entry, as a separate tracked task. The verifier found: the task is a ledger task of its own with gates G0, G2, G3, G4 and G5 all PASS; its change is separate from the commit that added the exception; the installer setting, the checker and its tests are byte-identical to their content before the exception (the three-file comparison is empty, and a search of them for the exclusion, the mechanism's names, the package and the directive finds nothing); the reviewers were not the producer; the task was claimed at 15:05 UTC and built at 15:19 UTC, after the seven-day point 14:08:09 UTC; the policy keeps the dated record; the package file, the lockfile and the workflows are unchanged.
- **Its ruling on the orchestrator's decision to remove the whole mechanism and not only the entry:** within the owner's words; no further owner approval is needed. The mechanism was introduced in full by the earlier task solely for this one exception; removing it returns the files exactly to their earlier state; the owner's "only this 1 time ... no standing permission" supports removing the scaffold; nothing the owner kept is removed (the pin, the dated record, the owner-only rule). The decision is labelled as the orchestrator's in the packet and the G0 report and is presented nowhere as the owner's.
- **The owner message recorded on this branch** (D-090 source 053, a request for an explanation): the verifier confirms that the capture claims no decision and no verification, and that nothing in the D-092 folder changed.
- **What it could not check, in its own words:** the live run of the age gate (its instructions forbade it; the builder and both reviewers ran it, and the row does not depend on it); CI on the pushed head; the long directive test suite, which is CI's.
- The directive validator, run by the verifier in the review copy: exit 0. The checker's tests: 40 pass, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping this verdict at a later head.

How the return arrived (2026-10-07): at 15:34 UTC as one message. It is reproduced below unchanged (copied by script from the session transcript `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl`, line 5790; only the two-space indent the transport adds to every line was removed).

---

```
DIRECTIVE-COMPLIANCE VERIFIER — M0-T183 (owner directive D-092, clean-up of the one-time age exception)
Role: independent directive-compliance verifier; I produced none of this work or its records. Frozen head verified: `git -C /root/project/rv-m0t183-a rev-parse HEAD` = 716bd7fd3ad541c2c022ac0c10b4ec4f7d44d572. I am an AI agent; this is not a human or professional review. Binding confirmed: `directive_registry.load_registry(...).evaluate_task_refs(M0-T183.json)` -> ok=True, applicable==cited==['D-092-R016'], no missing/invalid.

ROW M0-T183 D-092-R016: PASS
 - Tracked clean-up task exists and is separate: `project-control/tasks/M0-T183.json` is its own ledger task with gates G0/G2/G3/G4/G5 all PASS (`project-control/gates/M0-T183-G*.json`); material commit bf134ab0 is distinct from M0-T182's exception commit 8fe57ca0 (`git show -s 8fe57ca0` = "M0-T182 ... age exception ... pin, gate rule, installer exclusion, tests").
 - Neither exclusion nor exception entry remains: `git diff --stat 8fe57ca0^ 716bd7fd -- apps/web/.npmrc apps/web/scripts/dependency_age_gate.mjs apps/web/scripts/tests/dependency_age_gate.test.mjs` is EMPTY (exit 0); grep of those three files for min-release-age-exclude|OWNER_AGE_EXCEPTIONS|matchOwnerAgeException|owner_age_exception|source-map-js|D-092 returns nothing (exit 1). `apps/web/.npmrc` holds only min-release-age=7, save-exact=true, package-lock=true (lines 10/14/19).
 - Second, reviewed change by non-producers: material commit bf134ab0 (five files: the four + producer report); G3/G4 by code-reviewer, G5 by security-reviewer (producer was frontend-engineer); G2/G3/G4/G5 share one content identity content_manifest_sha256 68b19630... and the four source files are byte-unchanged bf134ab0..HEAD (no post-submit drift).
 - After the seven-day point 2026-10-07T14:08:09.382Z: claimed 15:05:18Z, material commit bf134ab0 at 15:19:58Z (`git log 51b3375a..HEAD`); G0 report line 6 states it was written 2026-10-07 15:04:58 UTC.
 - Dated record kept: `docs/DEPENDENCY_SECURITY_POLICY.md` "Exceptions on record" table still holds the source-map-js 1.2.2 row, clean-up now "task M0-T183 removed ... on 2026-10-07, after the expiry"; section 6 keeps owner-only authority ("No agent may create, approve, or apply an age exception") plus the new reviewed-change sentence; enforcement map dropped the temporary exclusion.
 - Nothing else changed: `git diff --stat 51b3375a 716bd7fd -- apps/web/package.json apps/web/package-lock.json .github` EMPTY; source-map-js pinned "1.2.2" (package.json line 51; lockfile resolves 1.2.2). `.claude/` and `CLAUDE.md` unchanged.

Ruling on removing the whole mechanism (not only the entry): WITHIN the owner's words; no further owner approval needed. The empty three-file diff proves the mechanism (OWNER_AGE_EXCEPTIONS list, matchOwnerAgeException, owner_age_exception result kind, its report line and tests) was introduced in full by M0-T182 solely to implement this one-time exception; removing it returns the files exactly to their pre-exception state. R013 ("creates no standing permission; any later case needs a new approval") supports removing the scaffold rather than leaving dead, untested exception code in a security gate. It removes nothing the owner kept (the 1.2.2 pin, the dated record, and the owner-only rule all remain). It is explicitly labelled THE ORCHESTRATOR'S DECISION in the task objective and in G0 report line 8 ("for the G5 reviewer to judge"); it is NOT presented anywhere I read as the owner's decision. The D-090 source-053 capture on this branch (owner message 109) states "neither row is verified. Both rows are pending" and "it decides nothing" — it claims no decision or verification; `git diff --stat 51b3375a HEAD -- project-control/directives` shows only the three D-090 files, nothing in the D-092 folder.

Harness: `python tools/validate_directive_compliance.py --check` exit 0. `cd apps/web && node --test scripts/tests/*.test.mjs` exit 0, 40 tests / 40 pass / 0 fail.

Carry-forward condition (blob-level predicate): this PASS may be stamped at a later head without re-asking me iff these blobs are byte-identical to the frozen head — apps/web/.npmrc, apps/web/scripts/dependency_age_gate.mjs, apps/web/scripts/tests/dependency_age_gate.test.mjs, docs/DEPENDENCY_SECURITY_POLICY.md, and project-control/reports/M0-T183-producer-report.md — AND apps/web/package.json, apps/web/package-lock.json, and .github/ unchanged, AND the D-092-R016 row, the D-092 manifest, and the source files it traces to unchanged. I tolerate later commits only under project-control/ (e.g. the verification row, gate/state records) and added lines of docs/DISCOVERY_BACKLOG.md; any change to the blobs above voids the carry-forward.

Required corrections that BLOCK acceptance: none.

Non-blocking observations: (1) `node --test scripts/tests/` with a bare folder name exits 1 on this server; the glob form CI uses runs clean (40 pass) — matches the progress-log note. (2) Policy section-6 sentence cites the pattern "as owner directive D-092 was (tasks M0-T182 and M0-T183)" — accurate.

What I could not check myself: (a) the live npm-registry age-gate run (prohibited by my instructions; the builder/reviewers ran it — I treat their age readings, e.g. ~608k–609k s, as CLAIMS; R016 does not depend on them, it is met by the task existing and the files reverted, which I verified from git); (b) CI green on the pushed head of PR 463 (I did not query gh; CI is the final word, orchestrator-captured); (c) I did not run tools/test_directive_compliance.py (prohibited; CI's job).

VERDICT: PASS.
END-OF-REPORT
```
