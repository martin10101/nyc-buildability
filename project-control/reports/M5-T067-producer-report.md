# M5-T067 producer report — DB-040(q)+(r) site-definition store hardening residuals

Task: M5-T067 (backend). Producer: backend-engineer. Branch `task/M5-T067-store-hardening`.
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t067`. HEAD `0b6799fc4a0d078f860da4ddaa4073bed8316fc2`
(the claim-seam; all code/test changes below are uncommitted working-tree edits — the controller commits).

Closes the two LOW security residuals the M5-T062 G5 review routed onward
(`project-control/reports/M5-T062-G5.md`, findings LOW-1 and LOW-2), inside the accepted
in-memory site-definition store. No auth work (B-001-bound), no mount change, no new refusal
code, no contract/route change.

## Evidence-status legend (read this first)

Every line below is tagged so nothing reads as verified that was not run:

- **[OBSERVED]** — a command actually run this session (through the approval broker) or a file
  actually read this session; the exact output/anchor is given.
- **[BLOCKED]** — evidence the packet requires that the producer could NOT capture, because it
  needs cwd `services/api` and the broker runs documented commands from the worktree root (see
  the ROUTED BLOCKER at the end). It must be collected by the supervisor/orchestrator at harvest.
- **[PREDICTED]** — an expected result stated as a recipe only, NOT observed. The mutation
  demonstrations are PREDICTED; they require the scoped pytest, which is [BLOCKED] for the producer.

This report makes NO "all green", "suite passes", or "pre-existing" claim as a verified fact.

## IMPLEMENTATION (code/tests read this session — [OBSERVED] via Read)

Scope = exactly the four allowed paths. Both remediations are present in the working tree; file/line
anchors are against the current working tree.

1. **(q) supersede: SCOPE before STATUS, mirroring revoke** — `services/api/app/site_definition/store.py:298-358`.
   `supersede()` looks the record up directly (`store.py:308-312`), checks the `supersedes_id`
   reference (`313-318`) and the required reason (`319-324`), then binds the **condo-key scope**
   (`329-333`, raises `ConfirmationNotFoundError` on a foreign `condo_key`), and only AFTER that
   reads status (`336-341`, raises `ConfirmationNotActiveError`). So a cross-property probe of a
   KNOWN foreign record is an indistinguishable 404 whatever the record's status; the 409-class
   `ConfirmationNotActiveError` is reachable only on the record's OWN binding. This mirrors
   `revoke()`'s accepted scope-before-status discipline (`store.py:399-437`). The `_record_insert`
   collision/chain-depth guards still raise before any mutation (`store.py:205-238`), so a refused
   probe mutates nothing (the reorder did NOT move those guards).

2. **(r) revoke: identical not-found message for both branches** — `services/api/app/site_definition/store.py:403-429`.
   The missing-record branch (`404-413`) and the existing-but-foreign branch (`419-429`) raise
   `ConfirmationNotFoundError` with byte-identical text:
   `"no site-definition confirmation matching that record id exists for the property addressed by the request path"`.
   Given a known (unguessable uuid4) record id, a missing id and a foreign id are indistinguishable
   by message text. The text echoes neither probed id.

3. **api test: direct full-body equality** — `services/api/tests/api/test_site_definition_api.py:788-834`
   (`test_revoke_not_found_response_is_identical_for_missing_and_foreign_ids`). Asserts a direct
   equality of the two refusal **response bodies** after removing only the documented per-request
   `correlation_id` (`test_site_definition_api.py:820-828`), retaining the explicit `404` /
   `state == "not_found"` / `reject_code == "confirmation_not_found"` / message assertions above it.
   The refusal body shape is `{state, message, reject_code, correlation_id}`
   (`app/api/v1/site_definition.py:301-318`); `correlation_id` is a `uuid.uuid4().hex` per request
   (`site_definition.py:662`) that discloses nothing.

## AS-1 … AS-5 — test anchors ([OBSERVED] the tests EXIST/assert as stated; PASS is [BLOCKED])

Whether these tests PASS was NOT verified this session (scoped pytest is [BLOCKED] — see below).
Only the presence and assertion content are [OBSERVED] via Read.

- **AS-1 (supersede oracle closed)** — `tests/site_definition/test_site_definition_records.py:745-779`
  (`test_supersede_foreign_probe_is_404_whatever_the_record_status`, parametrized
  `active|superseded|revoked`) asserts a foreign-condo supersede probe raises `ConfirmationNotFoundError`
  for all three statuses and leaves both chains unchanged. The 409-own-binding case:
  `test_site_definition_records.py:782-804`
  (`test_supersede_of_a_non_active_own_record_is_still_the_409_conflict`).
- **AS-3 (message unification)** — store level: `test_site_definition_records.py:811-841`
  (`test_revoke_not_found_message_is_identical_for_missing_and_foreign_ids`) asserts
  `str(missing) == str(foreign)` + equal `reject_code`. Route level: `test_site_definition_api.py:788-834`
  asserts equal status/state/reject_code/message AND the direct body equality.
- **AS-2 / AS-4 (mutation sensitivity)** — recipes in the mutation section below; **[PREDICTED]**, not observed.
- **AS-5 (preservation)** — no legitimate same-property path changed; forbidden paths untouched
  (`git status --porcelain` this session shows ONLY the three in-scope files modified + this untracked
  report). Whether the full scoped suite stays green is **[BLOCKED]** pending harvest.

## Documented commands — actual outputs this session ([OBSERVED])

All three ran through the approval broker, which executed them from **cwd = the worktree root**
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t067` (NOT `services/api`). A `cd`/prefixed-path or any
wrapped form is refused by the broker as non-documented, so the producer cannot change the cwd.

- **#1 `python -m ruff check .`** — **[OBSERVED]** cwd = worktree root; **exit 1**; `Found 45 errors`.
  Every finding in the captured output is under `project-control/…` or `tools/…`; NONE reference
  `services/api` or the three in-scope files. (My capture of the 45-finding output was partially
  truncated in transport, so I do NOT assert "zero in services/api" as a fully-enumerated fact.)
  The intended `services/api`-scoped ruff was NOT runnable by the producer → **[BLOCKED]**, harvest.
  I did NOT modify the unrelated root-level findings and make NO "pre-existing" claim about them —
  they are simply outside the four allowed paths.
- **#2 `python -m pytest tests/site_definition tests/api/test_site_definition_api.py -q`** —
  **[OBSERVED]** cwd = worktree root; **exit 4**; `ERROR: file or directory not found: tests/site_definition`;
  `no tests ran in 0.00s`. `tests/site_definition` exists only under `services/api/`, so ZERO tests
  ran. This is the cwd mismatch — NOT a code/test result. The scoped-suite result is **[BLOCKED]**.
- **#3 `python tools/modularity_check.py --check`** — **[OBSERVED]** cwd = worktree root (correct for
  this command); **exit 0**; `selected 472 files; failures 0; warnings 21`. **PASS** — the corroborated
  fact is `failures 0`, so the modularity gate is green independent of the advisory warnings. I make NO
  claim that all 21 warnings name "pre-existing" files: the tool's human-readable output prints only the
  FIRST 20 of the 21 warnings (`tools/modularity_check.py:562`, `for w in payload.get("warnings", [])[:20]`),
  so the full warned-file set was never observed and the 21 files' git history was never checked. What
  IS corroborable from the printed output: none of the three in-scope files (`store.py`,
  `test_site_definition_api.py`, `test_site_definition_records.py`) appears among the 20 printed
  warnings — consistent with `failures 0`, but the 21st (unprinted) warning was not inspected.

## Scoped suite + mutation demonstrations — [BLOCKED for producer], harvest recipe + [PREDICTED]

The scoped pytest and BOTH mutations require cwd `services/api`, which the producer cannot reach
within policy (ROUTED BLOCKER below). Production code is UNCHANGED — **no mutation was applied**
(applying a mutation the producer cannot then observe/verify-restore would risk leaving the tree
mutated, so it was not done). The supervisor/orchestrator must run each from `<worktree>/services/api`:

Harvest recipe (from `<worktree>/services/api`):
1. `python -m ruff check .` → expect clean on the in-scope files.
2. `python -m pytest tests/site_definition tests/api/test_site_definition_api.py -q` → expect the
   scoped suite green; record the exact PASS count.
3. AS-2 mutation, then restore, then re-run (2); AS-4 mutation, then restore, then re-run (2).

- **AS-2 (q) — [PREDICTED]:** in `supersede()` move the STATUS check (`store.py:336-341`,
  `if self._current_status(old_id) is not ConfirmationStatus.ACTIVE`) ABOVE the SCOPE check
  (`store.py:329-333`, `if new_confirmation.condo_key != old.condo_key`). Predicted red:
  `test_supersede_foreign_probe_is_404_whatever_the_record_status[superseded]` and `[revoked]`
  — the foreign probe of a non-active record then raises the 409-class `ConfirmationNotActiveError`
  instead of the expected `ConfirmationNotFoundError` (pytest: `DID NOT RAISE`/wrong-exception on
  `pytest.raises(ConfirmationNotFoundError)`). `[active]` stays green (status passes, scope still
  404s), which is why the reorder is what closes the oracle for the non-active statuses. Restore =
  scope-first (current tree). **NOT observed this session.**
- **AS-4 (r) — [PREDICTED]:** diverge either revoke not-found literal (e.g. append a char to the
  `store.py:410-413` missing-branch text). Predicted red: store-level
  `test_revoke_not_found_message_is_identical_for_missing_and_foreign_ids`
  (`assert str(missing.value) == str(foreign.value)`) and route-level
  `test_revoke_not_found_response_is_identical_for_missing_and_foreign_ids`
  (message equality + the full-body equality). Restore = byte-identical text (current tree).
  **NOT observed this session.**

## Consumer sweep (D-066-R001 impact + message-text scan) — [OBSERVED] via Grep this session

`store.py` is consumed via `site_definition/__init__.py` by `app/api/v1/site_definition.py` (routes,
FORBIDDEN) and `app/api/v1/condo_records.py` (read path, FORBIDDEN). Routes serialize `str(exc)`
verbatim into `message` (`site_definition.py:301-318`) and do NOT branch on refusal message text, so
no runtime consumer depends on the wording.

Message-text/reject-code scan across `services/api/tests` for
`matching that record id | must belong to the property | no site-definition confirmation exists |
confirmation_not_found | must belong to the same condo key`: the ONLY match is my own in-scope
`test_site_definition_api.py:818` (the `confirmation_not_found` reject_code assertion). No test pins
the revoke/supersede not-found message TEXT as a literal (the equality tests compare responses to
each other, not to a hard-coded string). `tests/api/test_condo_records_api.py` references
`site_definition` only on the READ document (additive `site_definition` block: status
confirmed/unconfirmed, byte-identical additive behavior — lines 38/60/638-730); it makes NO
`revoke`/`supersede` call and pins NO revoke/supersede message text.

**Corroborated vs predicted (consumer sweep):** the Grep facts above are **[OBSERVED]** this session
(the scan hits, the single in-scope reject-code assertion, the absence of any literal message-text
assertion, and `test_condo_records_api.py`'s additive-only `site_definition` usage). The CONCLUSION
that the message unification reddens NO out-of-scope suite is **[PREDICTED]** from those facts, NOT a
run result — the actual green of `test_condo_records_api.py` and any other consumer suite is
**[BLOCKED]** (same cwd defect) and must be **supervisor-collected at harvest** to corroborate the
sweep. On the Grep evidence I found nothing to route to the orchestrator as an out-of-scope redness;
if the harvest run surfaces one, it routes to the orchestrator per the consumer-sweep duty (never a
silent out-of-scope test edit).

## correlation_id normalization — unchanged route excerpt ([OBSERVED] via Read, forbidden path)

`app/api/v1/site_definition.py` is a forbidden path and was NOT edited. Supporting the api test's
`correlation_id` removal:
- `_refuse()` builds the refusal body `{state, message: _bounded_message(str(exc)), reject_code,
  correlation_id}` and returns it via `_json` (`site_definition.py:301-318`).
- `correlation_id = uuid.uuid4().hex` is generated fresh per request at each handler
  (`site_definition.py:501, 553, 593, 662`), so it varies between any two responses and discloses
  nothing about record existence. Removing it before the direct body-equality assertion is therefore
  the correct normalization: every OTHER field being equal proves the whole body carries no oracle.

## Disclosed residual — orchestrator follow-up (NOT fixed here; scope held)

`supersede()`'s two not-found branches are NOT unified: the missing-record branch echoes the id
(`store.py:310-312`, `"no site-definition confirmation exists for record id {old_id!r}"`) while the
foreign-scope branch returns the static `"a superseding confirmation must belong to the same condo
key as the record it supersedes"` (`store.py:330-333`). Given a known uuid4 id, this is a message-text
existence oracle for supersede — the analogue of revoke's LOW-2, one class lower because it discloses
existence only via wording on a default-off/unmounted route. Packet (q) is the status-oracle REORDER
only; (r) is REVOKE message unification only. Unifying supersede's messages is OUT of this packet's
scope; preserved here as a follow-up for the orchestrator to contract (a future DB-040 store-hardening
increment).

## ROUTED BLOCKER — supervisor/harness command-cwd defect (route to orchestrator)

The packet's `documented_test_commands` #1 (`python -m ruff check .`) and #2
(`python -m pytest tests/site_definition tests/api/test_site_definition_api.py -q`) are authored for
cwd `services/api` (bare `.` and `tests/…` paths that exist only there); #3 is authored for the repo
root (COMMAND CWD binding input; and `.claude/rules/CODING_RULES.md`: "run api pytest from services/api
cwd"). The broker executed all three from the worktree root, so #1 scanned the whole repo (45
out-of-scope findings) and #2 found no tests. Confirmed empirically THREE times (loop-2 re-feed prior
run + both runs this session). The producer cannot reconcile this within policy: a `cd`/prefixed-path
command is non-documented (the broker refuses it — verified this session) and editing controller/task
configuration is forbidden.

Consequence: the scoped-suite PASS and the AS-2/AS-4 mutation red→restore→green demonstrations
(AS-2, AS-4, and the AS-5 preservation gate) cannot be producer-captured; they must be
**supervisor-collected at harvest** using the recipe above.

Suggested durable fix (orchestrator/supervisor, NOT edited by the producer): store a per-command cwd
in the packet (`services/api` for commands #1/#2, repo root for #3), or rewrite #1/#2 with
`services/api/…`-prefixed paths so they resolve from the worktree root. Either fix lets a future
producer capture this evidence directly.

## Loop-2 re-feed session note (2026-09-21, backend-engineer)

Per the re-feed request: kept M5-T067 pending, retained the [OBSERVED]/[BLOCKED]/[PREDICTED] labels
above, and did NOT (a) repeat the known-failing root-cwd command cycle, (b) edit any controller/task
configuration, or (c) apply an unverifiable mutation to the tree. This session RE-VERIFIED via Read
that the working tree still matches every anchor in the IMPLEMENTATION and AS sections above — the
files are byte-consistent with those line anchors and unchanged since the prior run
(`git status`: same three in-scope files modified + this untracked report). No new documented command
was run because the producer's broker cwd defect (below) persists unchanged and re-running it would
only reproduce the same worktree-root miss.

The execution-context issue is re-ROUTED to the orchestrator/supervisor for harvest collection. The
supervisor must record an explicit cwd and run, from `<worktree>/services/api`:

1. `python -m ruff check .` (the api CI job's first step) — expect clean on the three in-scope files.
2. `python -m pytest tests/site_definition tests/api/test_site_definition_api.py -q` — expect the
   scoped suite green; record the exact PASS count.
3. AS-2 (q): apply the reorder-revert mutation (`store.py`: move the STATUS check at store.py:336-341
   ABOVE the SCOPE check at store.py:329-333) → re-run (2), capture the expected RED
   (`test_supersede_foreign_probe_is_404_whatever_the_record_status[superseded]` and `[revoked]`
   raise `ConfirmationNotActiveError` instead of `ConfirmationNotFoundError`) → restore scope-first →
   re-run (2) green.
4. AS-4 (r): diverge one revoke not-found literal (`store.py:410-413`) → re-run (2), capture the
   expected RED (store- and route-level `*_identical_for_missing_and_foreign_ids` equality) → restore
   byte-identical text → re-run (2) green.
5. Consumer evidence: `python -m pytest tests/api/test_condo_records_api.py -q` — expect green
   (its `site_definition` usage is additive-only and pins no revoke/supersede message text, per the
   [OBSERVED] Grep sweep above). Route any out-of-scope failure to the orchestrator; never edit that
   suite.

The disclosed supersede message-text residual (store.py:310-312 echoes the id vs the static
store.py:330-333 text) stays PRESERVED and unfixed — out of this packet's (q)+(r) scope, a follow-up
for the orchestrator to contract. Not committing, merging, gating, or accepting in this unit.

## Second re-feed re-verification (2026-09-21T04:17Z, backend-engineer)

Re-fed on the same instruction. Took NO new documented-command run (the broker cwd defect below is
unchanged; re-running would only reproduce the worktree-root miss) and made NO controller/config edit.
Re-verified state via native tools only:

- `git status --porcelain` + `git rev-parse HEAD`: HEAD still `0b6799fc4a0d078f860da4ddaa4073bed8316fc2`
  (claim seam, no commits this unit); exactly the three in-scope files modified + this untracked report.
- Read-confirmed the (q) reorder is present — `store.py:308-341`: record lookup → supersedes-ref →
  reason → **condo-key SCOPE (329-333)** → **STATUS (336-341)**, mirroring `revoke()` (`store.py:399-437`).
- Read-confirmed the (r) unification — `store.py:410-413` (missing branch) and `store.py:426-429`
  (foreign branch) raise byte-identical not-found text.
- Grep-confirmed the mutation-sensitive tests EXIST at their anchors:
  `test_site_definition_records.py:746` (`test_supersede_foreign_probe_is_404_whatever_the_record_status`,
  parametrized), `:782` (409-own-binding), `:811` (store-level message equality);
  `test_site_definition_api.py:788` (route-level body equality).

Conclusion unchanged: implementation + mutation-sensitive tests are COMPLETE in the tree; only their
EXECUTION (scoped ruff, scoped pytest, the AS-2/AS-4 red→restore→green demonstrations, and
`test_condo_records_api.py`) is BLOCKED for the producer and must be supervisor-collected at harvest
using the recipe above, then bound to the restored final diff before resubmission for independent
review. Supersede message residual stays PRESERVED as follow-up scope.
