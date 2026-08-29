VERDICT: PASS

# G5 Security Review — M0-T111 (D-024 Amendment 8, unit L: one-way Telegram sink)

**Reviewed HEAD:** `4ce8131d0f88fa0e2009a2a7049b4df2d6fcafb8` (confirmed via `git rev-parse HEAD`; matches the expected reviewed head). Deliverable content identity c9b3b9a; the four deliverable files are unmodified in the working tree (only `project-control/state.json` and `project-control/tasks/M0-T111.json` control-plane files show as modified).
**Reviewer:** security-reviewer (read-only). **Gate:** G5 security. **Regime:** in-regime (D-024 Amendment 8, rows R231/R232/R241–R246/R248/R249).
**Scope reviewed:** `tools/agent_supervisor/telegram_sink.py` (340 SLOC), `tools/agent_supervisor/telegram_sink_cli.py` (120 SLOC), `tools/agent_supervisor/cli.py` (+2 lines), `tools/test_agent_supervisor_telegram_sink.py` (559 lines). Underlying S13.10 machinery (`notifications.py`, `redaction.py`, `models.py`) inspected as the reuse boundary.
**Hard safety rule honored:** no live network send performed; every probe used a fake transport or fake opener; the owner canary flag was never invoked.

## Verdict summary

No BLOCKING, MAJOR findings. The unit's security posture is sound: secrets never leave the owner's local environment on any traced path, the sink is structurally one-way, the live send is owner-gated with the refusal strictly ahead of construction, and Telegram failures cannot stop or crash the loop. Two MINOR and two ADVISORY items concern regression-guard robustness and inherited resource behavior; none blocks acceptance.

## Threat-model walk (per surface)

### 1. Secret exfiltration (R243 — crown jewel) — CLEAN

Traced every path the bot token / chat id can take:

- **Resolution:** `resolve_credentials` reads only `SUPERVISOR_TELEGRAM_BOT_TOKEN` / `SUPERVISOR_TELEGRAM_CHAT_ID` from env; on absence it raises `telegram_not_configured` whose message contains only the env-var *names*, never values (probe: `TOKEN in msg? False`).
- **Credentials holder:** `@dataclass(frozen=True)` with `__repr__`/`__str__` overridden to `Credentials(bot_token=[redacted], chat_id=[redacted])`; `__str__ = __repr__`. Verified redacted (L3.3).
- **Transport:** token composes ONLY into the URL path (`https://api.telegram.org/bot{token}/sendMessage`); chat_id + text ride the urlencoded POST body. The URL is a local variable in the closure, never returned, logged, or stored.
- **Exception paths (the key risk):** `deliver` catches every transport exception via `except Exception as exc: ok, detail = False, f"transport {type(exc).__name__}"` — class name only, never `str(exc)`. I probed this directly with an exception whose `__str__()` embeds the token-bearing URL: result detail was `transport LeakyError` — `TOKEN leaked? False | url leaked? False`. I also drove the *real* transport with a fake opener that asserts the token is present in `request.full_url` and then raises a URL-bearing error: contained as `transport FakeHTTPError`, `TOKEN leaked? False`. Grep confirms **no** `str(exc)`, `.args`, `logging`, `print`, or `traceback` anywhere in either module.
- **Downstream artifacts:** `DeliveryResult.detail` = `"failed after N attempt(s): {status-bucket|class-name}"`; audit rows (`notification_delivered` / `notification_delivery_failed` / `telegram_deduplicated`) carry ids, sink, risk class, digest, and that bucketed detail; delivered/dedup rows store hashes + timestamps. L3.2 asserts sentinel absence across notification rows, queue/delivered/dedup rows, audit lines, `NotifyOutcome`, and CLI output; reproduced PASS.
- **CLI:** `telegram status` reports `configured: yes/no` presence only; `telegram canary` output carries delivered/attempts/bucketed detail. No credential reference in the CLI module (grep clean).
- **Fake sentinels:** `FAKE_TOKEN = "0000000000:FAKE-sentinel-bot-token-for-leak-absence"` / `FAKE_CHAT = "FAKE-chat-id-sentinel-887766"` are obviously fake and carry both `gitleaks:allow` and `secretscan:allow` pragmas with a justification comment. Adequate.

### 2. One-way guarantee (R242) — CLEAN (live), regression guard weaker than claimed

The actual code exposes only `sendMessage`; grep for `getUpdates|setWebhook|webhook|get_updates|long_poll|parse_mode|reply_markup` in `telegram_sink.py` matches only the docstring disclaimer. No receive/poll/webhook/command-parsing/approval/merge/execution/config surface. No `subprocess`/`exec`/`eval`. **The live one-way property holds.** See MINOR-1 for the AST-scan robustness caveat.

### 3. Owner gate (R245) — CLEAN

`build_real_transport` raises `live_send_owner_gated` unless `live_send_authorized=True`. The **only** authorized production caller is `telegram_sink_cli.py:66`, reached **after** the refusal guard at lines 59–64 (`if not args.live_canary_authorized_by_owner: return emit_refusal(...)`). Refusal is strictly before transport construction and before any credential read (`resolve_credentials` is invoked only inside `TelegramSink.deliver`, downstream of the flag check). No test constructs an authorized transport with the real opener — L6.3/L6.4 always inject a fake opener; the CLI test asserts refusal without the flag. No non-owner path reaches an authorized live send.

### 4. Injection into Telegram text — CLEAN

The POST body sets only `chat_id`, `text`, `disable_web_page_preview=true`; **`parse_mode` is unset** (verified in source and by probe), so Telegram renders the text as plain text — markdown/HTML/URL shapes in the summary do not activate, and link previews are suppressed. `summary`/`reason`/`where_to_review` are redacted and leak-shape-refused by `build_notification` before composition. See MINOR-2 for the identifier-field caveat.

### 5. Loop safety (R244) — CLEAN

`deliver` has no `raise` site (AST audit: the only raises in the module are `resolve_credentials`→`telegram_not_configured`, `build_real_transport`→`live_send_owner_gated`, and `notify_condition`→`unknown_condition`; none on a delivery/network path). Bounded attempts `MAX_DELIVERY_ATTEMPTS=3` with a 10s per-attempt timeout; on exhaustion the item stays queued and the call returns. `unit_can_proceed=True` is hardcoded on the deliver call and `unit_can_proceed=False` is absent from source, so `run_must_pause` is structurally False on every telegram path (L5.5 asserts the audited `run_must_pause: False`). Dedup register is FIFO-bounded at 64 (reproduced: 69 records → 64 retained, oldest trimmed). See ADVISORY-1 (queue growth) and ADVISORY-2 (`notify_condition` raise).

### 6. R248 / dependency & SSRF posture — CLEAN

Full `6662b88..HEAD` diff touches only the 4 named production/test files plus control-plane records — **no** `.claude/hooks`, `settings.json`, MCP, `agent_dispatch_guard`, or `readonly_agent_guard` changes (L8 `test_R248` and the diff confirm). Transport is stdlib `urllib` only — no new dependency (no `requests`/`httpx`/`aiohttp`). SSRF: the host is a fixed literal `https://api.telegram.org`, scheme fixed `https`, no user-controlled URL component (chat_id/text go in the body); the `# noqa: S310` is justified. urlopen redirect-following is bounded by the fixed TLS host + timeout (INFO-1).

## Findings by severity

### MINOR-1 — L4 one-way AST scan has evasion paths (regression-guard hardening)
`test_no_receive_or_command_surface_exists` reconstructs identifiers/attributes/string-constants from the AST and checks forbidden substrings. Because the AST reconstruction strips parentheses, the `"exec("` and `"eval("` substring checks can **never** match real code (proven: `exec(chr(120))` → scan does not contain `"exec("`). The `subprocess` check is evaded by `from subprocess import run as r` (the alias hides the module name; proven: `subprocess`/`run` both absent from the scan), and method-name checks (`getupdates` etc.) are evaded by string-splitting. The report calls this a scan that "enforces this permanently" — it is a helpful backstop, not a sound guarantee.
**Impact:** low — the *current* deliverable is genuinely one-way (verified by direct code review), so R242 holds live; the risk is that a future edit could slip a receive/exec surface past this specific test.
**Smallest sufficient fix:** scan the raw source text (lowercased, comments/docstrings stripped) for the forbidden tokens rather than only AST-reconstructed identifiers, and drop the trailing `(` from the `exec`/`eval` needles (match bare `exec`/`eval` names). Optionally assert the module imports no `subprocess`/`socket`/`http.client`.

### MINOR-2 — Identifier fields bypass the redaction / leak-shape boundary yet are transmitted
`build_notification` redacts and leak-shape-refuses only `reason`, `summary`, `where_to_review`. `run_id`, `task_id`, `checkpoint_id` are stored verbatim, and `compose_text` transmits `task: {task_id}  run: {run_id}` in the outbound message. Probe: `task_id="*md* [x](http://a)"`, `run_id="<b>evil</b>"` pass through unredacted into the composed text. Rendering is plain text (no `parse_mode`), so this is not an active-injection issue, but a future caller that placed a secret- or auth-link-shaped value in `task_id`/`run_id` would transmit it **un-redacted** (these fields skip `redact_text` and `assert_view_only`).
**Impact:** low — these are structural loop identifiers, not free-form/attacker text, and no current caller populates them adversarially.
**Smallest sufficient fix:** run `task_id`/`run_id` (and `checkpoint_id` if ever composed) through `redact_text` in `compose_text`, or document/validate that identifier fields must never carry sensitive content.

### ADVISORY-1 — Unbounded queue growth under sustained outage with a repeated identical condition
The dedup digest is recorded only on **successful** delivery (`if result.delivered: _dedup_record(...)`). During a Telegram outage, repeated `notify_condition` calls for the same `(condition, task_id, summary)` each re-enqueue a fresh copy (probe: 5 identical failing emissions → queue depth 5, dedup register 0). The `notification_queue` is the pre-existing S13.10 register, unbounded by design; unit L inherits that. Loop safety is unaffected (R244's "downtime cannot stop the loop" holds), and the on-success-only rule is a defensible at-least-once tradeoff (recording before delivery could permanently suppress an important recurring alert). Noted per the threat-model request.
**Optional hardening:** de-duplicate against the pending queue before enqueue, or cap the queue with FIFO/aggregation, so a long outage plus a chatty condition cannot grow memory without bound.

### ADVISORY-2 — The single entry point can raise on an out-of-vocabulary condition
`deliver` never raises, but `notify_condition` raises `TelegramError("unknown_condition", …)` for any condition outside the closed 8-tuple (fail-closed, intentional, tested by L1.2). This is a programming-error guard, not a downtime/network path, so R244 is satisfied; but the report's "never raises into the loop" framing applies to `deliver`, not to the entry point. The future (shadow-only) loop seam that calls `notify_condition` must pass a closed-vocabulary literal or wrap the call.

### INFO-1 — urlopen follows redirects
`urllib.request.urlopen` follows 3xx redirects. Non-exploitable here: the fixed TLS host `api.telegram.org` would have to be compromised to redirect elsewhere, the request is timeout-bounded, and the token lives only in the original request's URL path (a cross-host redirect uses the `Location` URL, which does not carry the token). No action required.

### INFO-2 — Fake sentinels are correctly marked
Sentinels are self-evidently fake and carry both `gitleaks:allow` and `secretscan:allow` pragmas. Adequate.

## Modularity (boundary answers vs. actual diff)
Two new focused modules (`telegram_sink.py` 340 SLOC, `telegram_sink_cli.py` 120 SLOC — both well under the 600 warn threshold); `cli.py` grows by exactly one import + one registration line (its pre-existing symbol-ceiling warning is unchanged and not newly crossed). `python tools/modularity_check.py --check` → **0 failures**, 8 warnings all on pre-existing unrelated files. Responsibilities cleanly separated (domain/transport/dedup vs. CLI wiring vs. reused composition in `notifications.py`). Stable public interface `register_telegram_verbs`. Boundary tests = the L-pack. Consistent with the packet's seven answers.

## Executed vs. inspected

**Executed:**
- `git rev-parse HEAD` / `git status` / `git diff --name-only 6662b88..HEAD` — HEAD confirmed; only 4 production/test files + control records changed.
- `pytest tools/test_agent_supervisor_telegram_sink.py -v` → **31/31 passed**.
- `pytest tools/test_agent_supervisor_adversarial.py tools/test_agent_supervisor_endurance.py -q` → **187 passed** (backs the S13.10 reuse boundary).
- Independent probes (fake transport / fake opener, no socket): exception-path token containment (deliver + real transport), `resolve_credentials` error secrecy, 2xx/3xx bucketing, `parse_mode` absence + body fields, AST-scan evasion demonstration, queue-growth-under-outage, identifier-field passthrough, raise-site AST audit.
- `python -m ruff --version` → 0.13.0 (CI version); `ruff check` on all 4 files → **All checks passed**.
- `python tools/modularity_check.py --check` → 0 failures.

**Inspected (read-only):** full `telegram_sink.py`, `telegram_sink_cli.py`, `cli.py` diff, the L-pack, `notifications.py`/`redaction.py`/`models.py` reuse boundary, `source-008-amendment.md` (rows R241–R245/R248 verbatim), and the design report `M0-T111-telegram-sink.md` §0–§6.

**Not executed:** any live Telegram send (prohibited by the hard safety rule); the whole-supervisor freeze-baseline suite (>1165 tests) — the producer's captured run is relied upon for the baseline count; the security-relevant reuse and delivery paths were reproduced directly above.

**Recommendation:** PASS. MINOR-1 and MINOR-2 are worth a follow-up hardening pass (test robustness + identifier-field redaction) but do not block acceptance; ADVISORY-1/ADVISORY-2 should be carried forward to the loop-integration seam.

*(Saved verbatim from the reviewer's return by the orchestrator; transport entity-decoding only — `&lt;`/`&gt;` decoded.)*
