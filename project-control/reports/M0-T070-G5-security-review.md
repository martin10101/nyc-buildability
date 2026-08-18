VERDICT: PASS

# G5 Security Gate Report — M0-T070 (D-014) supervisor command-authority repair

**Reviewer:** security-reviewer (independent, read-only; producer = orchestrator).
**Reviewed SHA:** `6aae5857fdcdf55f5197e542013bdc81f8035d14` (base `de2f224`) — verified via `git rev-parse HEAD` against the worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t070`. Match confirmed.
**Scope:** diff `de2f224..6aae5857` (19 files, +2784/-6). Security-relevant code: `tools/agent_supervisor/{policy.py,cli.py,broker.py,durable_state.py}`, `schemas/task_packet_commands.schema.json`, `fixtures/m0_t063_documented_test_command.json`, `tools/test_agent_supervisor_command_authority.py`.
Every claim re-derived from source; producer reports treated as unverified claims.

## Reproduction

- `python -m pytest tools/test_agent_supervisor_command_authority.py tools/test_agent_supervisor_policy.py tools/test_agent_supervisor_broker.py -q` → **176 passed, 1 skipped**.
- Full regression: `python -m pytest tools/test_agent_supervisor_*.py -q` → **1557 passed, 2 skipped, 0 failed** (142 s). Independently re-establishes the M0-T039 freeze baseline (≥1165, 0 failures) with the repair applied — AS-11 confirmed, no deny/authorization regressions.
- Independent adversarial probe of the real validator (`validate_documented_test_commands`): trailing-newline, interior-newline, NUL, tab, vertical-tab, CR, and a Cyrillic homoglyph (`U+0430`) are all **REJECTED**; wildcard shapes `p* …` / `python *` are accepted (analysis below).

## Findings by severity

### SEC-CRITICAL — none.
### SEC-MAJOR — none.
### SEC-MINOR — none blocking.

### SEC-INFO

**SEC-INFO-1 — Wildcard breadth is permitted in documented shapes (bounded, by design, reused from standing grants).** `tools/agent_supervisor/policy.py:872-873` allows `*`/`?` in the profile, and the validator accepts a leading-alnum program with a trailing wildcard (`p* tools/test.py`) or a whole-token wildcard arg (`python *`) — reproduced as ACCEPT. At runtime `_shape_matches` (`policy.py:838-852`) then fnmatch-matches such a shape against a proposed command with the **same token count**. Two mitigations bound this to non-exploitable: (a) `test_no_wildcard_program_can_be_documented` (`tools/test_agent_supervisor_command_authority.py:326`) plus the `^[A-Za-z0-9]` anchor reject a *leading* wildcard program (`*`, `?`, `* …`); (b) `_auto_test_command` (`policy.py:1424`) refuses any proposed command carrying substitution/metacharacters, and `_hard_deny` runs first in `evaluate` (`policy.py:1515-1517`). So the worst case is a G0-reviewed packet author documenting `python *`, which AUTO-classifies a **2-token, metacharacter-free** `python <arg>` invocation — not shell chaining, not a general allowlist, and it cannot bypass HARD_DENY. Same `_shape_matches` semantics standing grants already use (called out in `policy.py:868-871` and the schema `description`). Recommendation (non-blocking, defense-in-depth): consider forbidding `*`/`?` in the program token (index 0) to mirror the evident intent of rejecting leading-wildcard programs. Does **not** affect the actual M0-T063 fixture, which documents exact shapes only.

**SEC-INFO-2 — `replay.build_authority` does not run the validator** (`tools/agent_supervisor/replay.py:258-265` passes `documented_test_commands` from the case file unvalidated). This is the cited precedent, not a production authorization path: replay reconstructs already-recorded decisions for offline deterministic/audit comparison and never grants a live command. The one **live** constructor, `production_task_authority`, validates. Noted for completeness; no live impact.

**SEC-INFO-3 — Regex `$`/trailing-newline quirk is fully neutralized (defense-in-depth note).** Python `re` `$` matches before a trailing `\n`, so `_DOCUMENTED_COMMAND_PROFILE.match("python\n")` returns a match in isolation (confirmed). It cannot reach AUTO: the earlier `entry != entry.strip()` guard (`policy.py:912-914`) rejects it, and `parse_command`'s `has_metacharacter` (`\n`,`\r` ∈ `SHELL_METACHARACTERS`, `policy.py:488`) rejects it again at `policy.py:928-934`. Triple-guarded; no action needed.

## Character-profile / validator adversarial analysis

- **`-` placement (`policy.py:873`):** the hyphen is the last member of the class (`…\[\]-]`), a literal — no unintended range. No `X-Y` range exists except the intended `A-Z`, `a-z`, `0-9`.
- **`[`/`]` (`\[\]`):** literal, present only to support fnmatch `[seq]` classes in documented shapes. They are glob/pattern chars, not command-injection metacharacters; the injection set (`; & | < > $ ` + backtick + `( ) { } ' " \ # ~ ^ % !` and controls) is entirely **outside** the class, and `parse_command`'s substitution/metacharacter checks reject any that slip in char-wise (e.g. `eval `, `${…}`).
- **Unicode/homoglyph/NUL/control:** the class is an explicit ASCII set (not `\w`), so homoglyphs, fullwidth, NUL, tab, VT, FF, CR, LF are all rejected — reproduced.
- **`.split()` vs `shlex` divergence in `_shape_matches`:** benign, because the profile forbids quotes and backslash, so whitespace-split and shlex tokenization coincide for any profile-conforming documented shape.
- **`_program_name` suffix stripping (`policy.py:566-572`):** pre-existing, unchanged by this diff; applied symmetrically to pattern and candidate. Not a new capability.
- **argv-vs-command_text (`policy.py:1128-1131`):** the argv branch of `parse_command` checks `SHELL_METACHARACTERS` per token, so injected `;|&<>` cannot evade the guard. Unchanged by this diff.
- **TOCTOU:** validated commands are frozen into the immutable `frozen=True` `TaskAuthority` tuple at loop start (`policy.py:957,991`; `cli.py:2528-2531`) and read from there during evaluation; no re-read, no TOCTOU.

## Revoke-all / status reconciliation analysis

- **ask_id derivation is exact (no cross-request resolution).** `defer` mints `ask_<request_id>` (`broker.py:518`); `revoke_all` resolves `ask_{key[len(APPROVAL_PREFIX):]}` = `ask_<request_id>` (`broker.py:684-685`); `resolve_ask` UPDATEs `WHERE ask_id = ? AND answered_at_utc = ''` (`durable_state.py:628-632`). Unique request_id ⇒ exactly one row. `test_resolve_ask_is_idempotent_and_reports_misses` confirms miss/idempotence.
- **Audit history preserved, never forged.** `resolve_ask` UPDATEs, never DELETEs, and leaves question/`request_digest`/`created_at_utc`/`classification` intact; idempotent `WHERE answered_at_utc=''` means an already-answered row is not overwritten; `revoke_all` appends an `approvals_revoked` audit entry (`broker.py:690-693`). `test_the_revoked_ask_row_is_preserved_history_not_deleted` verifies row + digest + REVOKED record survive.
- **Status read path is read-only.** `cmd_status` (`cli.py:1346-1370`) uses only `all_state`/`open_asks`/`integrity_check`/`last_transition` (all SELECTs, `durable_state.py:391-395,608-614`) plus local dict copies; no `set_state`/`resolve_ask`/UPDATE. `test_a_pre_fix_journal_reports_revoked_history_without_mutation` reproduces the live A1 shape and asserts the unanswered row is still unanswered after status — the journal is not mutated.
- **A genuinely pending request is never hidden.** `cli.py:1363` keeps an ask open when the approval record is absent (`not isinstance(record, dict)` — loop-origin asks `rotation_pause/…`, `model_chain_exhausted/…` at `loop.py:1361,1513`, which never use the `ask_` prefix) or `status == PENDING_OWNER`. Only non-PENDING records (REVOKED/APPROVED/DENIED) are labeled non-actionable. `test_a_loop_origin_ask_without_approval_record_stays_open` confirms.
- **Transaction safety:** connection is autocommit (`isolation_level=None`, `durable_state.py:227`); `resolve_ask` uses the same `BEGIN IMMEDIATE`/`COMMIT`/`ROLLBACK` idiom as `set_state` (`durable_state.py:373-383` vs `619-636`), so `revoke_all`'s sequence of `set_state` then `resolve_ask` cannot raise a nested-transaction error / partial revoke.

## Structural / least-privilege checks

- **No general allowlist / bypass / always-allow.** Field is bounded: ≤16 entries (`policy.py:868`), ≤512 chars (`policy.py:869`), closed profile, unique, per-task; AUTO still requires exact `_shape_matches` and HARD_DENY runs first.
- **Single live authority constructor.** `_run_loop` uses `production_task_authority` (`cli.py:2544`); AST pin `test_run_loop_builds_authority_only_through_the_production_path` forbids any other `TaskAuthority`/`from_packet` call there. The other two constructions are the doctor probe (`cli.py:566`, empty `documented_test_commands`, non-production) and the operator broker (`cli.py:1426`, `active=False`, non-classifying).
- **No new dependency.** Validator is pure stdlib (`re`, `shlex`); the JSON schema is loaded only by tests for the lockstep assertion (`test_schema_pattern_equals_validator_profile` pins schema regex == validator regex byte-for-byte). No `jsonschema` import in runtime code.
- **No protected paths touched.** Diff contains no `settings`, `.claude/`, `.github/`, or controller-config changes (verified by name-status). `policy.py` diff is a single purely-additive hunk (`@@ -856,6 +856,88 @@`); `_hard_deny`, `evaluate` ordering, `_auto_test_command`, `OWNER_GATES`, control/destructive markers are unchanged.

## Explicit answers

1. **Can any input outside the closed profile gain AUTO?** **No.** Anything outside the profile raises `PolicyError` (run refuses); the runtime AUTO path independently blocks substitution/metacharacters, requires equal token count and an exact `_shape_matches` against a validated shape, and HARD_DENY is evaluated first. Profile-external characters can appear in a proposed command only at a documented `*`/`?` position and only when metacharacter-free — which cannot yield shell semantics (SEC-INFO-1).
2. **Does any general allowlist / bypass / always-allow exist?** **No.** Bounded per-task field; sole live authority constructor validates; no settings/`.claude/`/`.github` bypass; empty/absent field = no grant.
3. **Is any fail-closed path weakened?** **No.** `policy.py` change is purely additive; all deny logic unchanged; malformed field aborts the run; absent field returns `()`.
4. **Can the status read path mutate a journal?** **No.** Reads-only + local dict copies; proven by the pre-fix-journal non-mutation test.
5. **Can revoke-all reconciliation lose or forge audit history?** **No.** UPDATE-not-DELETE, idempotent, exact-id targeted, audit entry appended; row and digest preserved.

**Result:** All D-014 AS-1..AS-10 and prohibitions (deterministic fail-closed authorization, no broad grants/settings bypass, no fail-closed weakening, read-only status, immutable live journal) are satisfied and independently reproduced. Two non-blocking defense-in-depth observations (SEC-INFO-1 wildcard-in-program-token hardening; SEC-INFO-2 replay validator parity) are recorded for future consideration and do not affect this task's security posture.

**VERDICT: PASS**
