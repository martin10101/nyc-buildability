# M0-T147 G5 reports (verbatim reviewer returns, both rounds)

Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
(2026-09-06; transport entity-decoding only). ROUND 1 reviewed 3360cceb → **PASS with one
required correction (M-1) + two LOW hardening items**; corrections applied at dee758f4;
ROUND 2 (delta) → **PASS at dee758f4, no outstanding blocking corrections**.

Key round-1 substance (full text preserved in the session record):

- **Verdict PASS** (gate semantics: PASS with required corrections — corrections blocking for
  acceptance). Suite reproduced 94 passed; acceptance scenarios S1–S4 all PASS; supervisor-
  freeze qualifying-evidence citation verified in packet AND commit; forbidden paths untouched.
- **Trust boundary (adversarial):** the change does NOT widen the worker's ability to deceive
  the reviewer — equal-or-narrower than the M0-T131 live-read contract. Collection-path
  defenses verified: `minimal_env()` strips GIT_CONFIG*/GIT_DIR/GIT_EXTERNAL_DIFF/GIT_ATTR*;
  `--no-pager` forced; `assert_read_only_git` denies `-c/--exec-path/--git-dir/--work-tree/-C`
  and `--ext-diff/--textconv/--exec/--output`. Cross-check hardening: changed_files +
  diff_summary collected alongside; a gitdir redirection breaks origin_main/ahead_behind into
  visible failed_collections → REVISE, never silent approval.
- **M-1 (MEDIUM, required, now applied):** injection immunization was claude_checkpoint-scoped
  while diff_content is a guaranteed worker-authored channel; exact remediation wording
  specified and applied verbatim + two removal-sensitive anchors.
- **Execution-rejection clause not abusable:** scoped to the reviewer's own environment; the
  fail-safe for evidence gaps is REVISE (bounce to worker), never COMPLETE — a worker cannot
  convert an evidence gap into an approval.
- **DoS/packet bounds correct:** 16,384-byte per-section truncation with explicit marker;
  oversize packet → STOP_FOR_OWNER (fail-closed). Redaction verified to recurse into the new
  section (`redact_structure`). Reviewer argv unchanged (still --sandbox read-only; forbidden
  flags intact).
- **LOW-1 (follow-up, recorded):** `run()` materializes child stdout before the 8 MB cap;
  `git diff` scales with file content → transient collector memory balloon possible on the
  thin client (fail-closed via timeout + no-packet→no-review). Shared-module fix out of this
  task's scope; tracked as follow-up.
- **LOW-2 (applied):** collect with `--no-ext-diff --no-textconv` so a configured
  textconv/external-diff driver can never shape the evidence.

Round-2 delta substance:

- M-1 RESOLVED exactly as recommended; both anchors load-bearing.
- LOW-2 RESOLVED and load-bearing: exact-tail assertion updated (reverting the tail reds the
  test). Independently verified both `--no-*` flags pass `assert_read_only_git` (the enabling
  inverses remain blocked as distinct tokens) and `assert_argv_safe`.
- Suite 94 passed at dee758f4. LOW-1 deferral appropriate.
- **DELTA VERDICT: PASS at dee758f4c455b72d1faf4bbac42a4b3980ed37fc; overall G5 verdict for
  M0-T147 stands as PASS at this SHA (no outstanding blocking corrections).**
