# M0-T044 — Directive-Compliance FINAL Verification (D-010)

Verifier: directive-compliance-verifier (independent; producer = backend-engineer)
Frozen head: fe6fd8ed648608781b163e22ad3fd2377d82ba12  (branch task/M0-T044-github-flow, orch worktree, clean tree)
Producer content commit: af46b3e  (all later commits touch only project-control/**)
VERDICT: ACCEPT-READY (PASS)

## Method disclosure
Read-only. Verified at the frozen head; treated all producer/gate reports and the
evidence map as claims and reproduced each from primary evidence (source files,
executed tests, git objects, recomputed content identity). No project_control.py /
git / gh writes. Executed checks listed below.

## Executed checks (all reproduced by the verifier)
- git rev-parse HEAD = fe6fd8e; git diff --name-only af46b3e..HEAD = project-control/** only.
- git diff --name-only 341fa4d..HEAD = 3 code files + project-control bookkeeping; forbidden-path scan = NONE.
- python -m pytest tools/test_agent_supervisor_github_flow.py -q  -> 57 passed.
- python -m pytest tools/test_agent_supervisor_*.py -q  -> 1271 passed, 2 skipped.
- python -m pytest tools/test_agent_supervisor_invariants.py -q  -> 45 passed (invariant-9 registry lock incl.).
- python tools/validate_directive_compliance.py --check  -> exit 0 (no violations).
- python tools/test_directive_compliance.py  -> Ran 102 tests, OK.
- python tools/test_project_control.py  -> all 22 groups OK.
- python tools/test_directive_reminder.py  -> Ran 12 tests, OK.
- frozen_git_identity over M0-T044 allowed_paths at HEAD  -> 16149fc32263...ac4a59 (== G2..G5).
- sha256sum source-001/006/007  -> match manifest content_digest_sha256.
- grep: github_pr_merge absent from MODELED_EFFECTS; zero live importers of github_flow.
- Re-derived §5.5 (10 conditions) and §19.4 (10 items) 1:1 against source-001.md.

## Requirement verdicts (primary evidence)
R006 SATISFIED  — owner_approval_required hard-False (github_flow.py:160,186); no owner predicate in
                  evaluate_merge (:489-500); no-owner tests pass (lines 383, 397).
R007 SATISFIED  — main/master/*/main/force HARD_DENY (authorize_push :221-237; PushAuthorizationTests);
                  PR first-class (create_pull_request :695); no direct-main-push path (runner protocol :601-608).
R010 SATISFIED (scope-noted) — refusals are non-terminal FlowResult data (:615-624), no residue
                  (test_an_ineligible_merge_leaves_no_external_effect: pending_effects()==[]); loop-level
                  continue is out-of-scope (loop.py) — in-scope enabling property met and reproduced.
R077 SATISFIED  — 57/57 new + 1271/2 full suite; §19.4 register meta-test (line 629) maps 10 items to real
                  tests; 10 §5.5 predicates (MERGE_CONDITIONS :475-486) exist individually.
R093 SATISFIED  — producer diff == §19.4/§5.5/§5.2 surface only; github_pr_merge not in MODELED_EFFECTS;
                  invariant-9 test passes; no live importer.
R116 SATISFIED  — source-006 digest 2ac4eb04...900b == manifest; M0-T044 is the handoff-ordered unit after
                  accepted M0-T043 (branch base 341fa4d = M0-T043 merge); holds/SHADOW-ONLY/R595 untouched.
R117 SATISFIED  — source-007 digest 6f9e2eb0...df33 == manifest; order M0-T043->M0-T044->M0-T045 consistent.

## Material identity
content_manifest_sha256 = 16149fc32263f4ed9509e3c15b71f328cc4701b88252c7bf22bbcaff13ac4a59,
consistent G2..G5, independently recomputed at HEAD (clean tree). G0 differs (cdaeeb7a, pre-work base — expected).
Orchestrator stamps verification.json reviewed_sha at accept-time HEAD; reviewed content byte-identical since af46b3e.

## Honest trail
G3 MINOR-1/MINOR-2, G5 SEC-1/SEC-2/SEC-3/INFO-1 disclosed in gate reports AND pinned in
project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md (two M0-T044 sections). G4 OBS-1/OBS-2 cross-referenced
there as duplicates of MINOR-2/MINOR-1. All are fail-open decision defects, unreachable in shadow (no live
importer; R595 not lifted), MUST-RESOLVE pre-activation. Non-blocking for shadow-only acceptance.

## Prohibited actions (all clear)
Not accepted (state.json accepted_tasks = 62, M0-T044 absent). Not merged to main (af46b3e not in main;
main tip 341fa4d). No directives/ edit, no dependency/lockfile change, no forbidden-path touch, no
blocker/hold closure on the branch. Producer != verifier.

## Conclusion
All 7 bound requirements SATISFIED on reproduced primary evidence; material identity reproduced; prohibited-
action gates clear; residuals honestly pinned. ACCEPT-READY for the shadow-only, R595-gated task.
