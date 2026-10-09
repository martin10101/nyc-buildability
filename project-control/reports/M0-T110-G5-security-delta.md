DELTA VERDICT: PASS

# G5 Security Delta Re-Attestation — M0-T110 unit K

**Deliverable-content identity re-reviewed:** `c8b38ba1c6855dc7053f2f9404f68ef617a49e89`
**Branch tip:** `2a3cd4e6f3425d68d99f3a7ece23c0af695bd40a` (current HEAD; adds control-plane only on top of the content identity — production/skill files at HEAD are byte-identical to `c8b38ba`).
**Delta diff reviewed:** `git diff eacbb43..c8b38ba` (read-only). Baseline report: `project-control/reports/M0-T110-G5-security.md` at `eacbb43`.

## What I re-checked (executed vs inspected)

**Executed (read-only):**
- `git diff eacbb43..c8b38ba` for the production/skill files and the test file, plus `--stat` for the full delta.
- `pytest tools/test_agent_supervisor_codex_channel.py` → **56 passed** (was 52; +4 delta tests).
- Targeted run of the 5 delta-relevant tests → **5 passed** (`test_an_option_shaped_id_is_refused_before_any_execution`, `test_free_text_rides_behind_the_end_of_options_separator`, `test_a_secret_inside_the_reply_is_redacted_before_store_and_display`, `test_close_executes_without_provider_inputs`, non-text/oversized refusals).
- Direct-CLI re-probe of the downstream parser (`codex show --checkout=…`, `close --help`, `continue -rf …`, valid `cxt_`/`cxm_` ids).
- `python tools/modularity_check.py --check` → **failures 0** (`codex_channel*` not in warn list).

**Inspected:** the `_CODEX_ID` regex and its call-site placement; the skill and `codex_channel.py` docstring additions; the noun change; the two new security tests and the fake-token line.

## ADVISORY-1 — correctly closed

Confirmed. `_CODEX_ID = re.compile(r"^(?:cxt_|cxm_)[A-Za-z0-9]+$")` is applied inside the id-extraction branch of `_codex_argv` **before** `ids = [...]` and before any argv is built (my exact smallest-sufficient-fix shape). An option-shaped token (`--checkout=…`, `--help`, `-rf`) fails the anchored regex → visible hook block naming "not a cxt_/cxm_ id" + "nothing was executed" — never a downstream argparse surprise. This is proven at the **real-subprocess hook boundary** by `test_an_option_shaped_id_is_refused_before_any_execution` (not merely the downstream CLI). The defense now sits one layer earlier than in my baseline analysis, where I had only confirmed the downstream argparse abort. Complementary proof that the free-text field still rides behind `--` (with the thread-id positioned before `--`) is added by `test_free_text_rides_behind_the_end_of_options_separator` against a hostile `-rf; rm -rf / $(whoami) "quoted" line1\nline2` payload.

INFO-1 (45 s interception window) is now documented honestly in the skill; INFO-2 report §3 wording corrected to "write-only/inert" (no aspirational "surfaced" claim); INFO-3 recorded as accepted. All consistent with my baseline findings.

## New security surface introduced by the delta — none

- **`_CODEX_ID` regex:** anchored `^…$`, single `+` quantifier, no alternation-backtracking hazard → no ReDoS. It is a pure *restriction* (adds a refusal), can never widen what reaches argv, and refuses every option-shaped token (all begin with `-`, which fails the character class). Legitimate generated ids (`cxt_`/`cxm_` + hex) match; the precise per-subverb prefix remains enforced downstream (`not_a_thread_id`/`not_a_message_id`), so the hook's acceptance of either prefix is harmless.
- **Inbound reply-redaction test / fake-token line:** the token `ghp_ZYXWVUTSRQPONMLKJIHGFEDCBA9876543210ab` is an obviously-synthetic redaction-proof fixture inside an assertion that it is stripped from both `outcome.reply` and the stored thread (`json.dumps(record)`). It carries both `gitleaks:allow` and `secretscan:allow` pragmas; the coordinator reports both scanners green (CI 20/20), consistent with the accepted M0-T095 fake-token precedent. Not a credential, not a leak.
- **Skill / `codex_channel.py` docstring / noun change:** documentation and cosmetic string only; no logic, no I/O, no new imports.
- **Full delta scope:** touches no dependency manifest, no `settings.json`/`.mcp.json`, no guard hooks (`agent_dispatch_guard.py`/`readonly_agent_guard.py`), no network module. R248 and least-privilege still hold. Modularity failures 0.

All baseline PASS conclusions stand; the delta strengthens the hook attack surface and adds an explicit inbound-redaction proof without opening any new surface.

*(Saved verbatim from the reviewer's SendMessage return by the orchestrator.)*
