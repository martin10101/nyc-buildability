# M5-T069 producer report — DB-040(s) supersede not-found message unification

**Task:** M5-T069 — close DB-040(s) / the M5-T067 G5 review's **G5-LOW-1** (supersede's not-found
branches emitted divergent text and an id echo — the last known store existence oracle).
**Producer:** backend-engineer. **Branch:** `task/M5-T069-supersede-messages`.
**Worktree HEAD:** `527e182c5b39fdb99b9f6ec883aac9cd47cf2b59` (unchanged; the producer does not commit —
the candidate is delivered UNCOMMITTED in the working tree for orchestrator integration).

**Evidence legend.** `[WORKER-OBSERVED]` = a command I actually ran this pass in the producer broker
(or a native Grep), real output recorded here — NOT supervisor-corroborated, NOT CI-equivalent.
`[BROKER-LIMIT→harvest]` = a documented command the broker structurally cannot run from its
worktree-root cwd; routed to the orchestrator/CI harvest (cwd `services/api`) with an exact recipe,
never predicted-as-observed. The working tree is delivered in the intended (unmutated) candidate
state; no mutation is left applied.

## Broker boundary (why the scoped ruff/pytest/mutations route to harvest) — [WORKER-OBSERVED this pass]

The producer broker accepts ONLY the exact packet-documented test commands (run from the **worktree
root**) plus enumerated read-only git. It cannot change cwd, so the services/api-scoped commands are
structurally un-runnable here — reproduced this pass, not asserted:

- `python -m pytest tests/site_definition tests/api/test_site_definition_api.py -q` → **exit 4**,
  `ERROR: file or directory not found: tests/site_definition`, `no tests ran`. The suite resolves
  only under `services/api`; the broker ran it from the worktree root.
- `cd services/api && python -m ruff check .` and `git hash-object app/site_definition/store.py` →
  both **REJECTED**: `"the command is not an enumerated read-only git command and is not a
  packet-documented test command"`. The broker cannot cd, so the scoped ruff and the pytest-dependent
  mutation loop cannot execute here.

Per the packet's COMMAND-CWD input ("KNOWN BROKER LIMIT … route it to harvest exactly as T067 did")
and the ADR-005 evidence-capture division, the scoped ruff, the scoped-suite green, and the six
mutations are captured by the orchestrator harvest (recipe below). I did not bypass the broker and I
did not fabricate any outcome I could not run.

## Design choice (AS-2)

**Unification.** All not-found-class refusals in BOTH `supersede` and `revoke` raise
`ConfirmationNotFoundError` with ONE shared module constant `_NOT_FOUND_FOR_ADDRESSED_PROPERTY`
(`store.py:72`), byte-identical to the accepted T067 revoke text, with **no id echo**. A single
constant referenced by all five branches makes byte-identity structural. [WORKER-OBSERVED] the
constant is referenced at exactly the five not-found sites: supersede `:328` (missing), `:334`
(`supersedes_id` mismatch), `:350` (foreign); revoke `:428`, `:441`. AS-2 takes option (a): the
mismatch branch shares the identical text AND is proven to respond identically for a mismatch on an
existing record vs a missing `old_id`.

## Diff — [WORKER-OBSERVED] (`git diff --stat 527e182c` = 3 files, +162/-27)

- `store.py` — NEW constant `:72`; `supersede()`'s three not-found branches (`:328/:334/:350`) now
  raise the shared constant (echo dropped); `revoke()`'s two branches (`:428/:441`) reference the
  same constant (emitted text byte-identical to before). **No check reordered** — only the string
  literal inside each existing `raise` changed; scope-before-status order and `_record_insert` guards
  byte-untouched (AS-4).
- `tests/site_definition/test_site_definition_records.py` (`:863`, `:891`) — two store-level equality
  tests (AS-1/AS-3 and AS-2), mirroring the accepted revoke pair (`:811`).
- `tests/api/test_site_definition_api.py` (`:840`) — one route-level full-body equality test
  (minus `correlation_id`), mirroring the accepted revoke route test (`:788`).

## Verification I could run — [WORKER-OBSERVED this pass]

- **Modularity** — `python tools/modularity_check.py --check` (documented; repo-root cwd is intended)
  → **exit 0**, `selected 473 files; failures 0; warnings 22`. No `site_definition` file is among the
  22 warned (all connectors/scenario/rules/web/supervisor). Complete, not truncated.
- **Ruff (whole-worktree superset only)** — `python -m ruff check .` (documented; broker cwd =
  worktree root, so it lints the WHOLE worktree) → **exit 1**, `Found 45 errors`; every VISIBLE error
  is under `tools/` or `project-control/`, none under `services/`. **Output was truncated
  mid-listing**, and ruff sorts by path (`project-control` < `services` < `tools`), so a hypothetical
  `services/` error would fall in the truncated span — therefore I do **NOT** infer my three
  `services/api` files are ruff-clean from this run, nor that it is CI-equivalent. The authoritative
  api-CI lint is `python -m ruff check .` at cwd `services/api` (its own `pyproject.toml`:
  `E,F,I,UP,B`, line-length 100) → `[BROKER-LIMIT→harvest]`.
- **Consumer sweep** — repo-wide native Grep (the packet's sanctioned method; code-graph `impact` is
  not a documented broker command). Re-run this pass; actual results:
  - `must reference the record it` → matches ONLY in `project-control/reports/` (report prose); **no
    code/test match** — old `supersedes_id`-mismatch literal fully removed.
  - `must belong to the same condo key` → matches ONLY in `project-control/reports/` (M5-T059/T067
    review docs); **no code/test match** — old foreign-scope literal fully removed.
  - `exists for record id` → **2 code matches, both in-scope `store.py`**: `:229` (create-collision
    guard, `"…already exists for record id "`, a different message) and `:282` (`get()` not-found,
    the G5-INFO-1 read surface, explicitly OUT OF SCOPE); **no test match**. The old supersede
    missing-record literal has no consumer.
  - **Conclusion:** no out-of-scope suite or consumer pins any OLD supersede not-found text; nothing
    outside my file scope needs adjusting; the stop-and-report duty had nothing to trip.

## Authorized orchestrator harvest — [BROKER-LIMIT→harvest] (run at cwd `services/api`)

Recorded from ACTUAL output by the harvest; the table below is the expectation to CONFIRM, never a
pre-supplied observation.

1. **Lint (FIRST):** `python -m ruff check .` → record the actual services/api-scoped result.
2. **Scoped suite:** `python -m pytest tests/site_definition tests/api/test_site_definition_api.py -q`
   → expected GREEN, **77** tests (74 post-T067 baseline + 3 new; no existing assertion adjusted —
   consumer sweep found none pinning an old supersede literal, and revoke text is byte-preserved).
3. **Six isolated mutations, then final restored green.**

**Preserve/restore (critical).** The candidate is UNCOMMITTED, so HEAD `527e182c` still carries the
PRE-T069 `store.py`. Do **NOT** restore with `git checkout`/`git restore` (reverts to pre-T069 and
discards the unification). Step 0: copy `app/site_definition/store.py` to a scratch file OUTSIDE the
repo; record `D_cand = git hash-object app/site_definition/store.py` (LF-normalize / strip `\r` on
Windows). For each row: apply the single-line mutation → run the step-2 command → record the FIRST
failing assertion → copy the scratch file back → verify `git hash-object … == D_cand` before the next
row (abort on mismatch). After the last restore, verify `== D_cand` once more and re-run step 2 →
confirm GREEN.

| Row | Branch | Mutation (replace the `raise` arg on the named line) | Expected FIRST failing assertion |
|---|---|---|---|
| A1 | missing `:328` | a different literal | records `:878` `str(missing)==str(foreign)`; api `:874` |
| A2 | missing `:328` | `f"{_NOT_FOUND_FOR_ADDRESSED_PROPERTY} {old_id!r}"` (re-echo) | records `:878`; api `:874` |
| B1 | mismatch `:334` | a different literal | records `:907` (mismatch vs missing) |
| B2 | mismatch `:334` | `f"{_NOT_FOUND_FOR_ADDRESSED_PROPERTY} {new_confirmation.supersedes_id!r}"` | records `:907` |
| C1 | foreign `:350` | a different literal | records `:878` `str(missing)==str(foreign)`; api `:874` |
| C2 | foreign `:350` | `f"{_NOT_FOUND_FOR_ADDRESSED_PROPERTY} {old_id!r}"` | records `:878`; api `:874` |

For every single-branch mutation the two compared branches diverge, so the pairwise **equality**
assertion (store `:878`/`:907`, route `:874`) reddens first and pytest stops there. The `… not in …`
no-echo asserts (`:882/:883/:910/:911`; api `:882/:883`) and the `==_UNIFIED_NOT_FOUND_TEXT` asserts
(`:884/:907`) are additional residual coverage (they catch a both-branch identical echo/drift that
equality alone cannot see), not the first to fail. The harvest records the ACTUAL first failing
assertion per row; it must not mark a later assertion as the failure.

## Acceptance-scenario disposition

- **AS-1/AS-2** (unification incl. mismatch branch): store + route equality tests. Code
  [WORKER-OBSERVED]; green [→harvest].
- **AS-3** (mutation sensitivity): recipe + matrix above; RED outcomes [→harvest].
- **AS-4** (frozen order): diff changes only literal args; no reorder; guards untouched
  [WORKER-OBSERVED diff].
- **AS-5** (preservation): modularity exit 0 [WORKER-OBSERVED]; scoped ruff + scoped suite green
  [→harvest]; no pre-existing assertion adjusted (consumer sweep) [WORKER-OBSERVED].

## Handoff

Producer runs NO control CLI and does NOT commit. Gates G0/G2/G3/G4/G5, acceptance, commits, and all
control-state changes are the orchestrator's. Content identity: HEAD `527e182c` + the uncommitted
working-tree diff (`git diff 527e182c` reproduces it byte-for-byte); the candidate `store.py` is the
mutation-loop restore source and is never regenerated from HEAD.

--- END OF REPORT ---

## [ORCH-HARVEST 2026-09-22, seq 125] Authorized harvest record (cwd services/api, wt-m5t069)

Executed per the recipe above; ACTUAL outputs (the run log lives in the seq-125 orchestrator
transcript; every row restored-and-hash-verified against D_cand before the next):

- Step 0: D_cand = 89f998f59a8201ec97ca4f08fc3ee6028372bc01 (git hash-object, -stripped).
- Step 1 ruff: exit 0 ("All checks passed!").
- Step 2 scoped suite: exit 0 - **77 passed** (matches the expected 74+3).
- Step 3 mutation matrix - all six RED with the PREDICTED first-failing assertion:
  A1 RED first-fail test_supersede_not_found_message_is_identical_for_missing_and_foreign_ids @ test_site_definition_records.py:878;
  A2 RED @ :878; B1 RED test_supersede_supersedes_id_mismatch_shares_the_unified_not_found_text @ :907;
  B2 RED @ :907; C1 RED @ :878; C2 RED @ :878. Restore verified == D_cand after every row.
- Step 4: final hash == D_cand; final scoped suite GREEN (77 passed). Modularity: exit 0
  (473 files, failures 0, pre-existing warnings only).

The [PREDICTED] rows above are hereby elevated to OBSERVED at harvest.
