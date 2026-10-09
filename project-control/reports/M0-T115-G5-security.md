# G5 Security Review — M0-T115 (broker ask-row resolution + recovery-probe read-time reconciliation)

**Verdict: PASS**
**Frozen review identity:** `4d3760e10aae9b0e1d074dbe95760702dc36518b` — verified `git rev-parse HEAD` == frozen SHA (branch `control/D-024-fable-codex-loop`). No identity mismatch; review proceeded.
**Reviewer:** independent G5 (read-only; no writes, no git/gh mutations, no ledger edit).
**Range reviewed:** `git diff 871cab8..4d3760e` (7 commits).

## Scope of the change
Production code touched: only `tools/agent_supervisor/broker.py` (+15) and `tools/agent_supervisor/recovery_probes.py` (+26), plus tests `tools/test_agent_supervisor_command_authority.py` (+46) and `tools/test_agent_supervisor_recovery_probes.py` (+58). Everything else in the diff is project-control ledger (directive capture, gates G0/G2, task/report files, `state.json`). `cli.py` deliberately untouched (smallest fitting change). No other supervisor module changed.

## Central question — does anything WEAKEN the fail-closed geometry? No.

### (a) Probe reconciliation marks an ask answered only on a genuine owner answer — CONFIRMED
`probe_pending_requests` (recovery_probes.py:428-460): after `open_asks()`, it loads `all_state()` and drops an ask from the blocking set **only** when `_owner_answered` is true, defined as `isinstance(record, dict) and record.get("status") != STATUS_PENDING` where `STATUS_PENDING = "PENDING_OWNER"` (broker.py:70) and the key is `APPROVAL_PREFIX + ask_id[len("ask_"):]` = `"approval/" + request_id` (matches broker `_key`, broker.py:329-330). Verified fail-closed branches:
- **Missing record** → `state.get(...)` is `None` → `isinstance(None, dict)` False → stays blocking. ✓
- **Malformed (non-dict) record** → False → stays blocking. ✓
- **Still-PENDING record** → `status == PENDING_OWNER` → not answered → stays blocking. ✓
- **Unreadable `open_asks()`** → `_unknown("pending_requests_unreadable")` (never empty). ✓
- **Unreadable `all_state()`** → new branch returns `_unknown("pending_requests_unreadable")` (never empty). ✓
- **Non-broker ask** (`ask_id` not starting `"ask_"`) → `_owner_answered` returns False → stays blocking. I verified every non-broker minting site: `rotation_pause/…` (loop.py:1157), `turnover_refused/…` and `model_chain_exhausted/…` (loop_turnover.py:233,286), and `oper_…` (`OPERATOR_ASK_PREFIX = "oper_"`, operator_ask.py:76). None use the `ask_` prefix, so no collision is possible. ✓

This is logically **identical** to the already-accepted M0-T070 status-command reconciliation (cli.py:1499-1502), which keeps an ask open when `not isinstance(record, dict) or status == PENDING`. The probe's `not _owner_answered` is the exact De Morgan inverse. No new geometry is introduced — an accepted, reviewed pattern is reused.

### (b) Broker resolves ask rows only after a digest-verified owner answer — CONFIRMED
`approve_once` (broker.py:610-647) and `deny_request` (broker.py:649-678) both check `displayed_digest != stored` FIRST and, on mismatch, return a `HARD_DENY / digest_mismatch` outcome via `_audit_record_only` and `return` **before** reaching `resolve_ask`. A digest-mismatched answer resolves **nothing**. `resolve_ask` is called only on the success paths (`approve_once` after status→APPROVED; `deny_request` after status→DENIED). Test `test_a_digest_mismatch_deny_leaves_the_ask_row_open` asserts exactly this (open_asks stays 1). ✓

### (c) No history rows deleted or rewritten — CONFIRMED
`resolve_ask` (durable_state.py:673-692) is `UPDATE queued_asks SET answered_at_utc=?, answer=? WHERE ask_id=? AND answered_at_utc=''` — never DELETE; the question and its `request_digest` remain auditable. Returns `cursor.rowcount > 0`, so a **second** call finds no unanswered row → returns False → idempotent. The broker ignores the return, which is correct (resolving an already-resolved ask is a safe no-op). ✓

### (d) No policy tier / allowlist / classification / limited-auto / activation surface touched — CONFIRMED
Grep of the production diff for `limited.?auto|activat|allowlist|R595|policy_tier|classif|enable` → none. Supervisor stays SHADOW-ONLY; `remote_approvals.py` still writes `LIMITED_AUTO_KEY=False` (untouched). The directive-capture text in the ledger REINFORCES the hold (R276: "Resume M0-T107 limited-auto ONLY after every suite/gate/review/manifest/preflight passes; on ANY failure remain stopped … never bypass a gate"). Nothing flips activation. ✓

## Adversarial scenarios
1. **Forged `ask_`-prefixed row, no approval record** → missing record → blocks. SAFE. ✓
2. **Approval record dict with `status` key absent** → `record.get("status")` is `None`, `None != "PENDING_OWNER"` → would count as answered. **Reachability assessed:** I confirmed via grep that the ONLY writer of `approval/*` keys is the broker (broker.py:335,638,668 via `_key`); no other module writes that keyspace (`set_state('approval/…')` outside broker.py = NONE). Every broker write sets a defined status. So an absent-status record is unreachable through any in-code path — it requires out-of-band tampering of the SQLite journal, which is full host compromise (an attacker with journal write could equally forge `status="DENIED"` or directly stamp `answered_at_utc`). This is also identical behavior to the already-accepted M0-T070 status command. Classified **LOW / informational hardening**, not a reachable weakening — see Findings.
3. **REVOKED record** → `"REVOKED" != PENDING` → answered/closed → not blocking. Matches revoke semantics (a revoked approval is a closed question; blocking forever on it was the M0-T070 bug). SAFE. ✓ (CONSUMED and INVALIDATED behave the same and are likewise genuinely-closed states.)
4. **`resolve_ask` called twice** → idempotent, returns False. ✓

## Secrets / dependencies / config / PR / activation
- **gitleaks:** `gitleaks.exe detect --source . --no-banner --redact --log-opts "871cab8..4d3760e"` → `no leaks found`, 7 commits scanned, **EXIT 0**.
- **New dependency:** none. The only added production import is internal: `from .broker import APPROVAL_PREFIX, STATUS_PENDING`. The `requirements.json` in the diff is the D-024 **directive** file (`project-control/directives/…`), not a Python dependency manifest.
- **.claude/** / hooks / MCP / settings:** none touched.
- **Secrets (manual scan of full diff):** none (no keys/tokens/private-key blocks; the "owner denied three ASK" text is the reproduced-defect narrative).
- **PR #241:** no reference anywhere in the diff; a code diff cannot mutate a PR. NOTE: per my read-only gate protocol I did **not** run `gh pr view 241`; live confirmation that PR #241 remains OPEN/unmerged is deferred to the orchestrator (memory records a standing owner hold: never merge PR #241).
- **state.json:** `M0-T115` added to `active_tasks` (correct — not `accepted_tasks`; no self-acceptance).

## R273 — no writes to the live runtime journal — CONFIRMED
The probe path is read-only (`open_asks()`, `all_state()` — SELECTs only); test `test_a_pre_fix_denied_request_journal_does_not_block_restart` proves it (open_asks still == 1 after the probe passes). The broker `resolve_ask` calls execute only inside future owner `deny`/`approve-once` actions, not during review/import. All tests use temp journals. No code or command in this unit writes the live journal.

## Tests run
`python -m pytest tools/test_agent_supervisor_recovery_probes.py tools/test_agent_supervisor_command_authority.py -q` → **117 passed** (Python 3.11.9, 14.3s). Includes all 8 new tests: deny/approve-once resolve the ask row; digest-mismatch leaves it open; pre-fix DENIED/APPROVED journals don't block (read-only proof); PENDING blocks; missing record blocks; non-broker ask blocks.

## Findings
- **CRITICAL:** none.
- **HIGH:** none.
- **MEDIUM:** none.
- **LOW / informational #1 (hardening, pre-existing, non-blocking):** `_owner_answered` treats any status other than exactly `PENDING_OWNER` as answered. An approval record with a missing/garbage `status` (unreachable in-code — only the broker writes `approval/*`, always with a defined status; equals the accepted M0-T070 status-command logic) would count as answered. **Remediation (optional):** switch to an explicit answered-status allowlist (`DENIED, APPROVED_ONCE, CONSUMED, REVOKED, INVALIDATED`) so an unknown status fails closed to "still blocking." No behavior change for any broker-written record; defense-in-depth only.
- **LOW / informational #2 (coverage):** the new `all_state()`-unreadable branch (recovery_probes.py:441-444) has no dedicated unit test, though it mirrors the tested `open_asks()`-unreadable pattern. Optional to add.

## Commands run (read-only)
- `git rev-parse HEAD` / `--abbrev-ref HEAD`
- `git log --oneline 871cab8..4d3760e`; `git diff --stat 871cab8..4d3760e`; `git diff 871cab8..4d3760e` (full + per-file)
- `git diff --name-only 871cab8..4d3760e | grep -iE 'requirements|pyproject|package…|\.claude/|hook|mcp|settings'`
- `python -m pytest tools/test_agent_supervisor_recovery_probes.py tools/test_agent_supervisor_command_authority.py -q`
- `C:/Users/MLFLL/.gitleaks/gitleaks.exe detect --source . --no-banner --redact --log-opts "871cab8..4d3760e"`
- Grep sweeps: ask-row minting sites, `set_state` writers of `approval/*`, constants, cli.py reconciliation.

**Bottom line:** The diff does not weaken the fail-closed geometry. The probe reconciliation only ever removes an ask from the blocking set on a genuine, digest-verified owner answer; missing/malformed/pending records and non-broker asks still block; unreadable journal/state fails closed; no history is deleted; `resolve_ask` is idempotent; no policy tier, allowlist, classification, limited-auto, or activation surface is touched (supervisor stays SHADOW-ONLY); no secrets, no new dependency, no `.claude`/hook/MCP change; R273 upheld. **Verdict: PASS** with two non-blocking LOW/informational notes and one deferred process item (live `gh` PR-241 state confirmation, not run per read-only protocol).
