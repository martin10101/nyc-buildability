DELTA VERDICT: PASS

# G5 Security Delta Re-attestation — M0-T111 (D-024 Amendment 8, unit L)

**Reviewed delta:** `git diff 4ce8131..8574c58` (deliverable-content identity `8574c58b3425137aa41457c6d7ba3c3923b8605e`); branch tip `6cbac33e270758cda0e49c5e9e87bb55e92804de` (confirmed via `git rev-parse HEAD`; control-plane-only on top of the deliverable). Read-only; no live send; the new authorized-canary test clears the env in-process, so no socket was opened.
**Prior verdict:** PASS with MINOR-1, MINOR-2, ADVISORY-1, ADVISORY-2. This pass verifies only the delta against those findings.

## Delta scope
Production changes are confined to `telegram_sink.py` (+45/-6, now 375 SLOC) and `telegram_sink_cli.py` (import reorg only) plus the test pack (+129); the rest are gate/DCV report records. No new production file, no dependency, no hooks/settings/MCP/guard change. `modularity_check --check` → 0 failures (8 pre-existing warnings, none on the telegram modules). L-pack 35/35; ruff 0.13.0 clean.

## What I re-checked (independent, reproduced)

**MINOR-1 — one-way scan soundness — CLOSED.** `functional_text` now folds `ast.Import`/`ast.ImportFrom` module+alias names into the blob and matches `exec`/`eval`/`subprocess`/`socket`/`http.client`/`asyncio` as exact line-tokens; the vacuous paren-suffixed needles are gone. I replicated the updated extractor against my original adversarial sample (`import subprocess`, `exec(chr(120))`, `eval(chr(121))`, `from subprocess import run as r`, `import socket`): all of `exec`, `eval`, `subprocess`, `socket` are now caught — the exact evasions my prior probe demonstrated (subprocess-via-from-import; never-firing `exec(`/`eval(`) are fixed. Residual (INFO, not a regression): a dotted stdlib module reached via `from http import client` would not match the `http.client` token — far below the original vacuous-check problem and not present in the deliverable.

**MINOR-2 — identifier-field redaction — CLOSED.** `compose_text` now runs `task_id`/`run_id` through `redact_text` before transmission and applies a hard `MAX_OUTBOUND_CHARS = 3500` cap with a visible `...[truncated]` marker. Probe with a `ghp_…` fake token in both fields: token absent from the composed text (masked to `[REDACTED:github_pat]`/over-eager `openai_key`); a 5000-char `where_to_review` is bounded to ≤ MAX with the truncation marker. The identifier fields now meet the redaction standard the other fields already had.

**ADVISORY-1 — queue growth under outage — addressed for the common case; residual is inherited, not new.** `notify_condition` now consults `_already_queued` (a read-only scan of the frozen S13.10 `QUEUE_KEY`) and returns a visible `already_queued` outcome instead of re-enqueueing. Probes: (a) clean-summary — 6 failing emissions hold queue depth at 1; (b) two *distinct* summaries both deliver and neither is suppressed (no false-positive alert loss — the safety-critical direction is preserved); (c) residual edge — when the summary carries a redacted/truncated value, `_already_queued` recomputes the digest from the *stored* (post-builder) summary, which mismatches the *raw*-summary digest, so the queue reverts to the pre-existing unbounded behavior (depth 4 over 4 emissions). This residual is the original inherited S13.10 register behavior for a narrow case, not a new surface, and at-least-once delivery is preserved. Not a blocker.

**ADVISORY-2 — documented** in report §7 (deliver never raises; `notify_condition`'s only raise is the typed closed-vocabulary programming-error guard).

## New-surface assessment
- `_already_queued`: read-only scan of existing queue state; recomputes SHA-256 digests over already-redacted stored fields; no mutation, no I/O, no secret handling; cannot suppress a distinct alert (verified). No new surface.
- New compose-path redaction + truncation: strictly reduces what leaves the process (masks more, shortens); a defense, not a surface.
- New sentinels (`ghp_FAKEsummaryLeakSentinel…`, `ghp_FAKEtaskidLeakSentinel…`): test-only literals, obviously fake, both carry `gitleaks:allow` + `secretscan:allow` pragmas. No new surface.
- New authorized-canary-no-env CLI test: exercises the authorized path with `TOKEN_ENV`/`CHAT_ID_ENV` cleared (`mock.patch.dict(..., clear=True)`), so `resolve_credentials` refuses before any transport call (attempts=0, no socket). Safe by construction; honors the no-live-send rule.
- CLI import reorg (`NotificationQueue` from `.notifications`): cosmetic; the R245 owner-gate ordering is unchanged — refusal guard still precedes `build_real_transport(live_send_authorized=True)`, verified programmatically.

## Unchanged security invariants (re-confirmed under the delta)
R243 secret containment (exception paths still class-name-only; no `str(exc)`/logging added), R242 one-way (no receive/exec path introduced), R245 owner gate (refusal-before-construction intact, single authorized caller), R248 (stdlib-only, no hooks/settings/MCP), and loop safety (`deliver` still has no raise site; `unit_can_proceed=True` hardcoded) all hold.

**Conclusion:** The delta closes MINOR-1 and MINOR-2, substantially addresses ADVISORY-1 (common case bounded; residual is inherited, non-security, with no alert loss), and documents ADVISORY-2. No new security surface is introduced. DELTA VERDICT: PASS.

*(Saved verbatim from the reviewer's SendMessage return by the orchestrator.)*
