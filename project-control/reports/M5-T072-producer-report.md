# M5-T072 producer report — T069 G3-A2 revoke-text cross-op pin (test-only)

**Task:** M5-T072 — close the M5-T069 G3 **Advisory A2** gap: no assertion pinned *revoke*'s raised
not-found text to the unified constant (T067's revoke test asserted only intra-revoke equality;
supersede is pinned). Add the one cross-op pin so a future revoke-only literal fork reddens the suite.
**Producer:** qa-engineer. **Branch:** `task/M5-T072-revoke-text-pin`. **Worktree:** `wt-m5t072`.
**Scope:** test-only, one file; ZERO production edits (store.py and every route FORBIDDEN, untouched at HEAD).

## Evidence legend

- `[OBSERVED]` — a command actually run THIS pass (broker or native tool), real output recorded
  here. NOT supervisor-corroborated, NOT CI-equivalent.
- `[BROKER-LIMIT→harvest]` — a documented command the producer broker can run ONLY from the
  worktree-root cwd (it cannot `cd services/api`). Routed to the authorized orchestrator to run at
  cwd `services/api`, with an exact recipe. Never predicted-as-observed. No mutation is left
  applied; the working tree carries only the pin.

## The gap (spec source) and the fix (AS-1)

Spec: `project-control/reports/M5-T069-G3.md` Advisory A2 — cross-op not-found identity rested on the
shared store constant `_NOT_FOUND_FOR_ADDRESSED_PROPERTY`
(`services/api/app/site_definition/store.py:72`, raised by revoke at `:428` missing / `:441` foreign)
**plus** supersede's pin only; a revoke-only literal fork would redden no test.

Fix — one comment + one assert in the existing revoke-equality test
`test_revoke_not_found_message_is_identical_for_missing_and_foreign_ids`
(`services/api/tests/site_definition/test_site_definition_records.py`):

- New comment `:841`; new pin `:842` — `assert str(missing.value) == _UNIFIED_NOT_FOUND_TEXT`.
- `_UNIFIED_NOT_FOUND_TEXT` (test-local literal at `:855`, a byte-copy of the store constant, NOT
  imported from the store) combined with the pre-existing `str(missing.value) == str(foreign.value)`
  (`:836`) transitively binds **both** revoke branches to the unified constant (not merely to each
  other) — the identical structure the G3 review accepted for supersede's pin (`:886`).

## Diffs — the test-only diff vs the complete working tree [OBSERVED]

Two DISTINCT diffs (the prior pass conflated them — it labelled the test-only stat as the whole
`git diff --stat`, which also carries this report file).

- **Test-only diff** (the behavior change) —
  `git diff --stat -- services/api/tests/site_definition/test_site_definition_records.py`:

  ```
   services/api/tests/site_definition/test_site_definition_records.py | 2 ++
   1 file changed, 2 insertions(+)
  ```

  Both added lines are inside the one revoke test; **every existing assertion byte-unchanged**;
  +2/-0. This matches the BEHAVIOR-PRESERVATION bound ("an assert line extending the existing
  equality chain, plus at most a one-line comment").

- **Complete working-tree diff** — `git status --porcelain` / `git diff --stat` show EXACTLY two
  files: the test file above (**+2/-0**) **and this producer report**
  (`project-control/reports/M5-T072-producer-report.md`, the allowed evidence file). No production
  source, no route, no other test is touched.

Consumer-sweep duty is nil by construction (assert-only addition, no behavior-contract change —
CODE-GRAPH NAVIGATION BLOCK input).

## Bounded source context (the existing missing/foreign equality + the constant definition)

Store constant — the byte source of the pin, `services/api/app/site_definition/store.py:72`:

```python
_NOT_FOUND_FOR_ADDRESSED_PROPERTY = (
    "no site-definition confirmation matching that record id exists "
    "for the property addressed by the request path"
)
```

Revoke's two raise sites share that ONE constant — `store.py:428` (missing id) and `:441`
(foreign-scope):

```python
:428  raise ConfirmationNotFoundError(_NOT_FOUND_FOR_ADDRESSED_PROPERTY)   # record is None (missing id)
:441  raise ConfirmationNotFoundError(_NOT_FOUND_FOR_ADDRESSED_PROPERTY)   # not the addressed property (foreign)
```

Test — the pre-existing intra-revoke missing/foreign equality and the new cross-op pin,
`test_site_definition_records.py`:

```python
:836  assert str(missing.value) == str(foreign.value)          # existing (missing == foreign)
:837  assert missing.value.reject_code == foreign.value.reject_code
:839  assert "does-not-exist" not in str(missing.value)        # existing no-echo asserts
:840  assert record.record_id not in str(foreign.value)
:841  # [M5-T072 / T069 G3-A2] cross-op pin: revoke text == the shared unified constant.
:842  assert str(missing.value) == _UNIFIED_NOT_FOUND_TEXT      # NEW pin
```

Test-local unified constant — byte-copy of the store constant, `test_site_definition_records.py:855`:

```python
_UNIFIED_NOT_FOUND_TEXT = (
    "no site-definition confirmation matching that record id exists "
    "for the property addressed by the request path"
)
```

`:836` (missing == foreign) + `:842` (missing == constant) ⇒ foreign == constant too: both branches
are now pinned to the constant, not merely to each other.

## Verification [OBSERVED this pass]

- **Modularity** — `python tools/modularity_check.py --check` (documented; repo-root cwd, which for
  this worktree IS the worktree root) → **exit 0**, `selected 475 files; failures 0; warnings 22`.
  All 22 warnings are pre-existing (connectors / scenario / rules / web / supervisor); **no
  `site_definition` file is among them**.
- **Broker cwd limit (why ruff + scoped pytest are routed, not run here)** — the producer broker
  runs documented commands from the worktree ROOT and cannot `cd services/api`. So the api-scoped
  ruff and the scoped pytest cannot produce acceptance-grade output from this worktree: the
  worktree-root ruff lints the WHOLE tree (pre-existing errors under `project-control/`/`tools/`,
  none under `services/`) and the worktree-root pytest cannot resolve `tests/site_definition`. Those
  worktree-root forms are **not** acceptance evidence and are **not** presented as such — both are
  routed below to run at cwd `services/api`.
- **Forwarded-pass re-confirmation (2026-09-23):** the two-line pin (`:841` comment + `:842` assert)
  is preserved and byte-matches this report; the working tree stays confined to the two allowed
  files (the test file, +2/-0, and this report). Modularity re-run this pass → the same
  **exit 0 / `selected 475 files; failures 0; warnings 22`** (no `site_definition` file among the
  22). The producer broker **REFUSED** a non-documented digest pipe (`… | sha256sum`: *"not an
  enumerated read-only git command and is not a packet-documented test command"*) — confirming only
  the packet's documented commands run here, so the api-scoped ruff, the scoped pytest, and the AS-2
  both-branch mutant remain routed to the authorized-orchestrator harvest below as the **digest-bound
  transcripts** (cwd `services/api`, ruff FIRST then pytest). Their results are **UNKNOWN until
  harvested**; no acceptance is recorded here.

## Authorized-orchestrator harvest [BROKER-LIMIT→harvest] — run at cwd `services/api`

All paths below are relative to cwd `services/api` (git pathspecs relative to that cwd). Record the
ACTUAL command, cwd, exit code, and — for the mutant — the FIRST failing assertion. Expectations are
to CONFIRM, never pre-supplied observations.

1. **Lint (FIRST):** `python -m ruff check .` → expect clean for the one edited test file (the pin
   comment is ~86 cols, under the api line-length 100).
2. **Scoped suite (restored candidate):**
   `python -m pytest tests/site_definition tests/api/test_site_definition_api.py -q`
   → expect GREEN; the T069 baseline **+0** new tests (the pin extends an existing test; no new
   function, no existing assertion changed).
3. **AS-2 — the identical both-branch revoke-only mutant, passing WITHOUT the pin then failing WITH
   it.** store.py is UNMUTATED in the candidate and at the T069-accepted unified state at HEAD, so
   the restore is a plain checkout — never regenerate store.py.
   - **a. Mutant:** replace BOTH revoke raise args — `app/site_definition/store.py:428` **and**
     `:441` — with the SAME new divergent literal, e.g.
     `ConfirmationNotFoundError("revoke-only divergent not-found text")`. Forking BOTH is the A2
     gap; a single-branch fork (`:428` OR `:441` alone) reddens the pre-existing `:836` equality
     first, so it was already covered pre-pin — the both-branch fork is what exhibits the pin's
     unique value.
   - **b. WITHOUT the new pin:** temporarily delete the pin line
     (`tests/site_definition/test_site_definition_records.py:842`) and re-run step 2 → the revoke
     test **PASSES** (pre-pin GREEN — intra-revoke `:836`, reject_code `:837`, and both no-echo
     asserts `:839`/`:840` all hold because both branches share the new literal). Record exit 0.
     This is exactly the gap A2 named.
   - **c. WITH the new pin:** restore the pin line (`:842`) and re-run step 2 → the revoke test
     **FAILS** at `tests/site_definition/test_site_definition_records.py:842`
     `assert str(missing.value) == _UNIFIED_NOT_FOUND_TEXT`. Record the ACTUAL AssertionError
     (expected form: `'revoke-only divergent not-found text' == 'no site-definition confirmation
     matching that record id exists for the property addressed by the request path'`). The pin is
     the SOLE catcher of a revoke-only both-branch fork.
   - **d. Restore production source + pinned candidate:**
     `git checkout -- app/site_definition/store.py` (restores store.py to HEAD). **Never
     `git checkout` the test file** — it would discard the pin; the pin from step c stays.
   - **e. Verify final diff = only the two allowed files:** from the repo root,
     `git diff --stat` → EXACTLY
     `services/api/tests/site_definition/test_site_definition_records.py` (+2/-0) and
     `project-control/reports/M5-T072-producer-report.md`; store.py clean.
   - **f. Restored-candidate re-run:** re-run step 2 → expect GREEN, and record it as the restored
     candidate's scoped-suite result.

   (Corroborating, optional) Forking the shared constant `_NOT_FOUND_FOR_ADDRESSED_PROPERTY`
   (`store.py:72`) reddens BOTH the revoke pin `:842` and supersede's pin `:886` (constant-wide
   drift). Step 3 (revoke-only fork) is the decisive A2 proof.

## Acceptance-scenario disposition

- **AS-1 (the pin):** revoke's raised text (both branches, via the transitive `:836`+`:842` chain)
  pinned to `_UNIFIED_NOT_FOUND_TEXT`. Diff [OBSERVED, +2/-0]; green [→harvest step 2].
- **AS-2 (mutation sensitivity):** the identical both-branch revoke-only mutant — without-pin PASS
  then with-pin FAIL at `:842` — recipe + first-failing-assertion above. RED/GREEN outcomes
  [→harvest step 3].
- **AS-3 (no scope creep):** working tree confined to the pin (one test file, +2/-0) plus this
  report [OBSERVED]; scoped-suite green + scoped ruff clean [→harvest 1–2]; modularity exit 0
  [OBSERVED].

## Handoff

Producer runs NO control CLI and does NOT commit. Gates G0/G2/G3/G4, acceptance, commits, and all
control-state changes are the orchestrator's. store.py is the mutation-loop restore source and is
never regenerated (HEAD already carries the T069-accepted unified store.py). Do not present
worktree-root runs as acceptance evidence; do not mark gates accepted.

--- END OF REPORT ---

---

## [ORCH-HARVEST] Authorized-orchestrator harvest transcript (2026-09-23, cwd services/api, wt-m5t072)

All commands run at cwd `services/api` in wt-m5t072 at the harvested material (in-wt commit
cherry-picked to ecb6a13f, LF-normalized MATCH x2).

1. **Lint [OBSERVED]:** `python -m ruff check .` → **All checks passed!** (exit 0).
2. **Scoped suite [OBSERVED]:** `python -m pytest tests/site_definition
   tests/api/test_site_definition_api.py -q` → **77 passed** (the T069 baseline +0, as predicted).
3. **AS-2 both-branch revoke-only mutant [OBSERVED]:**
   - (a) mutant applied at exactly `store.py:428` and `:441` (script-verified those two lines and
     no other; the three supersede sites untouched).
   - (b) WITHOUT the pin (line temporarily deleted): `tests/site_definition` → **43 passed** —
     the both-branch fork is INVISIBLE pre-pin. Exit 0 recorded. Exactly the A2 gap.
   - (c) WITH the pin restored: the revoke test **FAILED at the pin**, first failing assertion
     `assert str(missing.value) == _UNIFIED_NOT_FOUND_TEXT` with
     `AssertionError: assert 'revoke-only ...ot-found text' == 'no site-defi... request path'` —
     the pin is the SOLE catcher of a revoke-only both-branch fork.
   - (d-e) `git checkout -- app/site_definition/store.py`; final working tree CLEAN (the material
     is the in-wt commit; `git diff --stat` empty; store.py at the T069-accepted state).
   - (f) restored-candidate re-run → **77 passed**.

Every [BROKER-LIMIT→harvest] row above is hereby elevated to OBSERVED. CI on the pushed head is
the remaining backstop.
