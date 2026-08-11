# M0-T062 — G2 producer self-check (orchestrator)

Scope: two edits, both inside `allowed_paths`.
- `tools/validate_directive_compliance.py` — drained inert `M0-T056` from `_EMPTY_IDENTITY_GRANDFATHERED` + comment.
- `tools/test_directive_compliance.py` — added 3 O1 fail-closed regression tests.

## Checks run (session15-acc HEAD = reviewed sha)

- `python -m pytest tools/test_directive_compliance.py -k "path_free or grandfather or optin or empty_identity or EmptyIdentity or justification"` → **18 passed** — the two affected classes (`EmptyIdentityGuardTests` + `ValidatorEmptyIdentityTests`) total 18, plus the `path_free_opt_in` marker tests; baseline was 15 pre-O1. **Precision note (G3 caught this):** pytest `-k` is case-insensitive *substring* matching, and `empty_identity` (with an underscore) does NOT match the underscore-free class names — so the same expression WITHOUT the camelCase `EmptyIdentity` token matches only **10** (which still includes all 3 O1 tests + the grandfather test). Both the 10- and 18-test runs pass; the 18 covers every test that touches the drained set or the O1 code path.
- `python tools/validate_directive_compliance.py --check` → **exit 0** — the real project-control registry still validates after the drain (c17 fails closed on any newly-introduced empty-identity task; M0-T056 now carried live).
- Full `tools/test_directive_compliance.py` is re-run independently by the required CI `control-plane` job on the PR (merge-gating). Local full-suite parity confirmed separately (see the accept progress note).

## Fail-closed / safety argument

- The drain removes only an UNREACHABLE set member: c17 tests membership only after `if entries or
  cp_entries or opted_in: continue`, and M0-T056's 7 allowed_paths are all tracked at HEAD → it
  resolves non-empty and never reaches the test. No behavior change for M0-T056; c17 now guards it live.
- `sorted(_EMPTY_IDENTITY_GRANDFATHERED)[0]` remains `M0-T026` → the grandfather test fixture is unchanged.
- The O1 tests assert EXISTING fail-closed behavior (`not isinstance(just, str) or not just.strip()`);
  no production code changed. bool/int/None/list/dict and empty/whitespace strings all refuse.

## Not in scope / unchanged

- No runtime/production path touched; no schema change (`additionalProperties` untouched).
- Required CI `control-plane` job re-runs `validate_directive_compliance.py --check` +
  `test_directive_compliance.py` on the PR — independent merge-gating verification.

Self-check PASS. Awaiting independent G3 (code-reviewer) + control-plane-verifier review at the reviewed sha.
