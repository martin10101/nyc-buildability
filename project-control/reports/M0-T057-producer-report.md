# M0-T057 — Producer report: fail-closed guard against empty-set content identity

Owner directive **D-011 item 6**. Producer deliverable only; an independent gate reviews this.

## 1. The defect

`tools/directive_registry.py::frozen_git_identity()` hashes the manifest of the tracked
objects a task's `allowed_paths` resolve to. When those pathspecs resolve to **zero**
tracked objects, the manifest is empty and `sha256(b"")` is the deterministic empty-set
hash `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. "Verified at this
identity" then binds **no code**: `submit`/`gate`/`accept` (and
`tools/validate_directive_compliance.py`) all compare that constant with itself, so the
freshness/dirt guards see nothing. Two shapes reach it: an empty `allowed_paths` list, and
— more insidiously — a **prose** `allowed_paths` entry such as
`"apps/web/src/** (survey review feature areas)"` or
`"services/api/app/corpus/ingest/** (OWNED by M3-T002)"`, which git (with
`GIT_LITERAL_PATHSPECS=1`, already set by `_run_git`) matches literally and therefore
matches nothing.

**Measured baseline (commit 7cc1fed):** 9 of 45 in-regime ledger tasks already resolve
empty at HEAD — `M0-T026`, `M0-T032`, `M0-T054` (accepted), `M0-T055` (in_progress),
`M0-T056` (empty `allowed_paths`), and `M3-T002…M3-T005` (prose `allowed_paths`). This is
the exact debt D-011 item 6 exists to close; per the task, their historical remediation is
handled **separately** and is out of scope here.

## 2. The guard and the opt-in marker

### Marker design (minimal, additive, shared)
A task is a **legitimately path-free governance packet** — the only case allowed to stamp
the empty-set identity — **iff** it explicitly declares both:

```json
"path_free_governance": true,
"path_free_justification": "<why this packet binds no tracked content>"
```

`additionalProperties` on the task packet already admits both keys, so there is **no schema
change**. The marker is interpreted by one shared helper,
`directive_registry.path_free_opt_in(task) -> (opted_in: bool, error: str | None)`, so the
CLI and the validator can never diverge on what "path-free" means. It fails closed on every
ambiguity:
- marker **absent** → `(False, None)` (not opted in; an ordinary task with real paths never
  reaches the empty check, so it needs no marker);
- marker present but **not the boolean `true`**, or `true` **without** a non-empty
  justification → `(False, reason)` — an explicit refusal, because a half-declared opt-in
  looks deliberate while binding nothing.

### Where the guard lives (fail-closed, shared path)
- `directive_registry.frozen_git_identity(...)` gains one parameter
  `allow_empty_identity: bool = False`. After resolving both manifest components (raw-blob
  entries outside `exclude_prefixes` + MATERIAL entries inside `control_plane_prefixes`),
  if **both are empty** and `allow_empty_identity` is False it returns
  `(None, None, "<...ZERO tracked files...>")`. The default is False, so the safe behavior
  (fail closed on a zero-file scope) is what any caller gets without opting in. The
  pre-existing empty-set constant/behavior is **preserved** for the opt-in case only.
- `tools/project_control.py::_task_git_identity(reg_mod, t, ...)` — the **single** helper
  that `submit` (line ~512), `accept` (~541) and `gate` (~1124) all call — now computes
  `opted_in, opt_err = reg_mod.path_free_opt_in(t)`, returns closed on `opt_err`, and passes
  `allow_empty_identity=opted_in`. This is the exact same fail-closed path submit/gate/accept
  already share, so none of the three can diverge.
- `tools/validate_directive_compliance.py::_validate_empty_identity(tasks_dir)` (new check
  **c17**, wired into `validate()`) is the CI-side static catch. For every in-regime task
  file: a **malformed** opt-in is always an error (git-free); an `allowed_paths` set that
  resolves **empty at HEAD** while the task is neither a valid opt-in nor grandfathered is
  an error. When the checkout is not a git work tree the empty-resolution arm is skipped
  (the malformed-opt-in arm still runs; the `project_control.py` guard remains the
  fail-closed backstop at every transition).

### Grandfather allowlist (judgment call — flagged for the gate)
Because 9 in-regime tasks already resolve empty at 7cc1fed and the task requires the
validator to stay **EXIT 0** while forbidding me from rewriting those packets, c17 carries a
**frozen allowlist** `_EMPTY_IDENTITY_GRANDFATHERED` of exactly those 9 task IDs (idiomatic
to this codebase's migration-manifest grandfathering). This keeps the current repo EXIT 0
while c17 fails closed on any **newly-introduced** empty-identity task. Draining an entry is
safe: once a task's `allowed_paths` match real tracked files it resolves non-empty and never
reaches c17 regardless of membership. This differs from the "no special-cased task id"
principle of the lifecycle-classification mechanism: that allowlist would let a task **skip a
real gate**; this one only suppresses a **CI advisory** for known debt — the
`project_control.py` guard still fails those 9 closed at submit/gate/accept. Surfaced here
for the reviewer's judgment.

## 3. Tests (all new; git-fixture based)

`tools/test_directive_compliance.py` — two new unittest classes:
- `EmptyIdentityGuardTests` (9 tests): marker semantics (absent → not-opted/no-error;
  present-without-justification → refused; non-boolean → refused; valid → permitted **and
  the justification is recorded**); `frozen_git_identity` refuses prose paths and empty
  paths ("ZERO tracked files"); a **valid pathspec yields a real manifest hash** equal to
  `git_tree_manifest` (not the empty-set); opt-in permits the preserved empty-set hash; and
  the non-vacuity test below.
- `ValidatorEmptyIdentityTests` (6 tests): c17 flags prose paths; passes valid paths; passes
  a valid opt-in; flags a malformed opt-in regardless of paths; ignores not-in-regime tasks;
  does not flag a grandfathered task.

`tools/test_project_control.py` — `test_s12_empty_identity_guard` (added to `ALL_TESTS`):
end-to-end via the CLI `gate` on an in-regime task — a real pathspec stamps a real (non
empty-set) identity; prose `allowed_paths` fail closed with "ZERO tracked files"; a
malformed opt-in fails closed with "path_free_justification".

Fixture correction (not a weakening): `test_s9_directive_claim_and_governance`'s `M9-T900`
was gated at G0 with **no** resolvable scope, so it relied on the old vacuous empty identity.
It now gets a real committed `allowed_paths=["probe.txt"]` before its G0 gate; all its
claim/governance assertions are unchanged.

### Non-vacuity mutation (proof the tests bite)
Mutating the guard to `if False and not entries and not cp_entries and not allow_empty_identity:`
(i.e. disabling it) and running the three guard tests produced:

```
FFF  [100%]
AssertionError: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' is not None
FAILED ...EmptyIdentityGuardTests::test_empty_allowed_paths_are_refused
FAILED ...EmptyIdentityGuardTests::test_non_vacuity_the_optin_flag_flips_refuse_to_the_empty_hash
FAILED ...EmptyIdentityGuardTests::test_prose_allowed_paths_are_refused
3 failed, 114 deselected
```

The empty-set hash `e3b0c442…` reappears the instant the guard is removed; the mutation was
then reverted (final guard line restored, confirmed by grep).

## 4. Verification commands & results

- `python tools/validate_directive_compliance.py --check` → **EXIT 0** (before and after).
- New unit classes: `15 passed, 102 deselected` (targeted run).
- `test_s12_empty_identity_guard`: `1 passed`.
- `test_s9_directive_claim_and_governance` (after fixture fix): `1 passed`.
- `python -m pytest tools/test_directive_compliance.py tools/test_project_control.py -q`:
  first full run surfaced the pre-existing `test_s9_directive_claim_and_governance`
  reliance on the vacuous identity (1 failed / 139 passed); after the fixture correction the
  combined suite is green — see the final line below.
- `ruff check .` from `services/api` (the CI ruff scope) does not lint `tools/`; the 16 ruff
  findings on `tools/` are all pre-existing (E702/E401/E402/E741/F841 in unchanged code) —
  **none** in the lines added here.

**Combined-suite final result:**
`python -m pytest tools/test_directive_compliance.py tools/test_project_control.py -q`
→ **`140 passed in 563.13s`** (exit code 0), after the fixture correction.

## 5. Files changed (all within allowed scope)
- `tools/directive_registry.py` — `PATH_FREE_MARKER`/`PATH_FREE_JUSTIFICATION`/
  `EMPTY_MANIFEST_IDENTITY` constants, `path_free_opt_in()`, `allow_empty_identity` param +
  empty-set guard in `frozen_git_identity()`.
- `tools/project_control.py` — `_task_git_identity()` reads the opt-in and passes
  `allow_empty_identity` (the shared submit/gate/accept path).
- `tools/validate_directive_compliance.py` — `_validate_empty_identity()` (c17) + grandfather
  allowlist, wired into `validate()`.
- `tools/test_directive_compliance.py` — `EmptyIdentityGuardTests`, `ValidatorEmptyIdentityTests`.
- `tools/test_project_control.py` — `test_s12_empty_identity_guard` (+ `ALL_TESTS`); `M9-T900`
  fixture correction.

## 6. Scope discipline / assumptions / limitations
- No existing accepted or in-flight packet was rewritten or re-bound (the 9 empty-resolving
  tasks are untouched; historical remediation is separate). Nothing else corrected.
- The guard now also makes an in-regime **G0** gate fail closed on a zero-file scope, because
  the task directed wiring into the *shared* submit/gate/accept path. This is intended and
  correct (it forces a malformed/empty scope to be fixed before the task advances); the one
  existing test that relied on the old vacuous behavior was corrected as a fixture, not a
  weakening.
- **Environment note (return to orchestrator):** the harness placed my Bash/git sandbox in
  worktree `agent-a1c91dcf82311bca1` (branch `worktree-agent-a1c91dcf82311bca1`), not the
  named `M0-T057-guard`; `git -C`/`cd` to `M0-T057-guard` is refused by the isolation guard.
  Both worktrees are at base `7cc1fed`, so the diff is identical. All edits and the commit
  are in `agent-a1c91dcf82311bca1`. The orchestrator should integrate that commit onto
  `task/M0-T057-empty-identity-guard`.
