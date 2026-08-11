# Gate Report — M0-T057 G3 (independent code review)

Saved verbatim by the orchestrator (transport entity-decoding only). Reviewer: `code-reviewer`
(independent, read-only; ≠ producer `orchestrator`). Reviewed head `8221419` / identity `6525ddfb`.

- **Gate ID:** G3 (independent code review)
- **Task ID:** M0-T057 (empty-identity fail-closed guard — owner directive D-011 item 6)
- **Reviewer:** independent code-reviewer (NOT the producer)
- **Producer:** orchestrator
- **Result: PASS**
- **Clean worktree used:** `.../session15-acc`, HEAD verified `8221419135a51141a4216915262a1979e2823ebf`.

## Acceptance criteria reviewed
M0-T057 must add a fail-closed guard so that an in-regime task whose `allowed_paths` resolve to ZERO tracked files (the deterministic empty-set content identity `e3b0c442…`) is REFUSED at submit/gate/accept, unless it validly opts in as a path-free governance packet (`path_free_governance:true` + non-empty justification) or is in a frozen grandfather allowlist; plus a CI-side static catch (c17); plus non-vacuous tests; without false-positives on real pathspecs and without weakening any existing fail-closed path.

## Directive/requirement verification (G3 code review; the per-requirement DCV is separate)
| Requirement | Identity | Verdict | Evidence |
|---|---|---|---|
| D-011 item 6 — refuse empty-set identity at shared submit/gate/accept | 8221419 | PASS | `frozen_git_identity` empty-set guard (directive_registry.py:1618-1629) + `_task_git_identity` wiring (project_control.py:388-399); test_project_control.py S12 CLI test exercises gate() refuse/permit |
| D-011 item 6 — legitimate opt-in only, malformed fails closed | 8221419 | PASS | `path_free_opt_in` (directive_registry.py:1198-1258); refuse/permit tests OK |
| D-011 item 6 — CI-side static catch (c17) with frozen grandfather allowlist | 8221419 | PASS | `_validate_empty_identity` (validate_directive_compliance.py:269-327), wired into validate() line 358; validate --check exit 0 |

## Steps independently executed (from the worktree at HEAD 8221419)
1. `python tools/validate_directive_compliance.py --check` → exit 0
2. `python tools/test_project_control.py` → all 23 project-control test groups passed, including "S12 empty-identity guard (prose + malformed opt-in fail closed; real path stamps real identity)" — EXIT 0
3. `python tools/test_directive_compliance.py` → Ran 117 tests in 869.884s … OK (exit 0), including the 15 new EmptyIdentityGuardTests/ValidatorEmptyIdentityTests
4. Targeted `python -m unittest …EmptyIdentityGuardTests …ValidatorEmptyIdentityTests -v` → Ran 15 tests … OK
5. Read the guard source directly
6. Verified no false positive against a real production path: `frozen_git_identity(['docs/LEAN_OPERATING_PROCESS.md'])` → real identity `f3a6a363…`, err None
7. `git diff 7bc98f5 HEAD -- tools/validate_directive_compliance.py`; `git show --stat` on both M0-T057 commits (scope check); confirmed intervening accepts did not touch the tool files
8. `ruff check` on the three changed source files

## Expected versus actual
- Prose `allowed_paths` → REFUSED "ZERO tracked files": match (unit + CLI).
- Empty `allowed_paths` → REFUSED: match.
- Valid pathspec → real manifest hash (≠ empty-set): match (confirmed on real repo file `f3a6a363…`).
- Valid opt-in (`path_free_governance:true` + justification) → permitted, stamps preserved empty-set hash: match.
- Malformed opt-in → REFUSED with `path_free_justification` / "must be the boolean true": match (unit + CLI).
- c17: flags prose, passes valid paths, passes valid opt-in, flags malformed opt-in regardless of paths, ignores not-in-regime, does not flag grandfathered. All match.

Guard-correctness detail (source-verified): the empty check `if not entries and not cp_entries and not allow_empty_identity:` is placed after both manifest components resolve and before the material rehash. `allow_empty_identity` defaults False, so every caller fails closed without opting in. `_task_git_identity` reads `path_free_opt_in(t)`, returns closed on `opt_err`, passes `allow_empty_identity=opted_in` — the single shared helper called by submit (~512), accept (~541), gate (~1124), so the three cannot diverge. `path_free_opt_in` uses `marker is not True` (rejecting 1/"true"/truthy non-booleans) and requires a non-empty stripped-string justification; non-dict input fails closed.

Non-vacuity / mutation resistance: `test_non_vacuity_the_optin_flag_flips_refuse_to_the_empty_hash` drives identical prose inputs and asserts refuse with the guard vs. empty-set hash with the flag flipped — disabling the `not allow_empty_identity` clause breaks at least one of test_prose_allowed_paths_are_refused / test_optin_permits_the_preserved_empty_set_hash. Each security-relevant mutation direction is caught.

## Regression/security/provenance findings
- Session-16 M0-T055 drain — VERIFIED SAFE. `_EMPTY_IDENTITY_GRANDFATHERED` is now 8 entries. M0-T055 is accepted, in-regime, allowed_paths=["docs/LEAN_OPERATING_PROCESS.md"] (tracked, identity f3a6a363) → never reaches c17's error arm; draining cannot regress. validate --check stays exit 0. Grandfather test uses sorted(set)[0]=M0-T026 — no test hard-codes M0-T055.
- Session-16 dead-local removal — VERIFIED ZERO BEHAVIOR CHANGE. `top`→`_`, `_ident`→`_`, `active_ids` line removed; grep confirms 0 downstream refs. Behavior-neutral.
- Grandfather scope — not a gate bypass. The allowlist lives ONLY in the c17 CI advisory; `_task_git_identity` does not consult it, so all 8 grandfathered tasks still fail closed at submit/gate/accept. Advisory suppression of known debt, not a lifecycle bypass.
- No existing fail-closed path weakened. require_clean/dirt/reviewed_sha==HEAD guards untouched and still run before the empty check.
- Scope discipline — CLEAN. a98f3af = the 6 allowed files; 8221419 = validate_directive_compliance.py only.
- Fixture correction, not a weakening. test_s9's M9-T900 now gets a real committed allowed_paths before its G0 gate; claim/governance assertions unchanged.
- Lint/hints (honest status): ruff on the 3 changed files reports 5 findings, ALL pre-existing and NONE on M0-T057's added lines (directive_registry.py:1315-1318 4× E702; project_control.py:131 E401). validate_directive_compliance.py is ruff-clean (session-16 removal reduced hints).

## Defects
None blocking.

## Required rework
None required for PASS.

## Observations (non-blocking follow-ups)
- O1 (test-coverage gap; implementation correct). A guard mutation weakening the justification check from `not isinstance(just, str) or not just.strip()` to `just is None` keeps ALL current tests green: no test exercises `path_free_governance:true` + present-but-empty/whitespace/non-string `path_free_justification`. Shipped code is correct and fails closed on those cases; recommend adding one unit case (empty/whitespace justification → refused). Not blocking.

## Reviewer conclusion
The empty-identity guard is correct, fail-closed by default, wired into the single shared submit/gate/accept identity path, mirrored by a stdlib-only CI check (c17), and proven by non-vacuous tests that bite on the security-relevant mutations. No false positive on real pathspecs. The session-16 drain and dead-local removals are behavior-neutral and independently confirmed safe. All three required commands reproduce green at HEAD 8221419. Scope within allowed_paths; no existing gate or fail-closed path weakened.

**VERDICT: PASS**
