# Gate Report

- Gate ID: G5 (security and privacy)
- Task ID: M1-T002 — PLUTO SODA connector (64uk-42ks) with provenance and contract tests
- Reviewer: security-reviewer (independent; did not produce this work; did not run G1 or G3)
- Producer: backend-engineer
- Result: **PASS** — 4 low-severity hardening findings + 1 informational note; none blocks merge
- Review location: `.claude/worktrees/M1-T002`, branch `task/M1-T002-pluto-soda-connector`, HEAD `fe87b99` (base `9e22839` + review fixup), reviewed read-only
- Date: 2026-07-16
- Method: read task packet S1–S8 (esp. S5) first, then implementation (`services/api/app/connectors/bbl.py`, `pluto_soda.py`), tests, and all 18 fixtures; re-ran the full suite; executed original adversarial probes (token-leak forcing, hostile JSON, log-injection, URL-injection) against the real code paths; read G1/G3 reports for context and the producer report last. No implementation modified; no scratch files left behind (probes ran inline via stdin).

Scope note: this task has no auth/RLS/storage/upload surface. G5 scope here is the external-call surface: secret handling, SSRF/injection, untrusted-response handling, error hygiene, dependency surface, fixture hygiene, provenance integrity.

---

## 1. Commands executed (reproducible)

| # | Command | Result |
|---|---|---|
| 1 | `cd .claude/worktrees/M1-T002/services/api && python -m pytest tests -q` | **101 passed in 1.28s** (matches producer claim; includes `test_s5_error_payloads_never_contain_token_or_stack_trace`, `test_s5_tokenless_operation_sends_no_token_header`, the F5 urllib-transport translation tests, and S4 pre-network rejection tests) |
| 2 | ripgrep `(?i)(token|secret|password|api[_-]?key|authorization|bearer|X-App-Token)` over `tests/fixtures/pluto/` | Only capture-method prose and the F07 doc citation; **no credential values in any of the 18 fixtures** |
| 3 | Adversarial probe script (P1–P5, section 3 below) run against the real module | Outputs recorded below |

## 2. G5 checklist walkthrough

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1 | Secret handling (SOCRATA_APP_TOKEN) | **PASS** | Full trace in section 3. Env-only read (`pluto_soda.py:530-531`), header-only emission (`_build_headers`, :317-323), never in URL (:533 — URL is `BASE_URL + "?bbl=" + canonical`, canonical is regex-pinned digits), logs emit only `token_configured=bool` (:534-537), error payloads never include headers (`to_payload`, :201-209), HTTPError is converted to a plain `TransportResponse` and the exception object discarded (:270-272), `TransportFailure` message carries only the failure type name (:278). Existing token-absence test passes; my forced-leak probes found no leak. |
| 2 | SSRF / URL construction | **PASS** | `BASE_URL` is a module constant pinned to `https://data.cityofnewyork.us` (:82); no config/env-driven host. Only canonical 10-digit BBLs reach URL assembly (`normalize_bbl` at :529 raises before any I/O; `_CANONICAL_RE ^[1-5][0-9]{5}[0-9]{4}$` in `bbl.py:36` plus defense-in-depth recheck at `bbl.py:162`). `build_page_url` (:752-760) interpolates only bounds-checked ints; there is no `$select`/`$where` assembly from caller data anywhere in the module. Probe P5: every metacharacter payload (`&$where=`, `%0d%0a`, SQL-quote, `#`) rejected pre-network with `BBLValidationError`; zero transport calls. |
| 3 | Input validation | **PASS** | S4 tests re-run (suite): 9/11 digits, borough 6, non-numeric, negative, non-integer decimal all raise typed `BBLValidationError` with `transport.calls == []`. No path where unvalidated input reaches the transport: `fetch_by_bbl` normalizes at :529 before building the URL; there is no other network entry point. |
| 4 | Untrusted-response handling | **PASS with findings F1, F2, F4** | Non-JSON 200 → typed `SourceUnavailableError`; non-array → `SchemaDriftError`; >1 record → drift; record/query BBL mismatch → drift; unknown columns → drift signal, no fact. D2 non-finite guard verified (`_normalize_value`, :463-469; probe-independent suite test asserts `json.dumps(..., allow_nan=False)` passes). Control characters: the connector never logs untrusted response strings — logged values are the canonical BBL, the internally built URL, counts, and `version_raw` only after regex validation (:617 precedes :730). Gaps: no response-size cap (F1), uncaught `RecursionError` on hostile deep nesting (F2), unsanitized `errorCode` in payload detail (F4). |
| 5 | Error hygiene | **PASS** | `to_payload()` contains `error_type/message/correlation_id/source_id/dataset_id/detail` — no stack traces, no headers, no bodies (5xx/429 bodies are dropped). `version_raw` and `record_bbl_raw` are `repr()`-sanitized (:622, :641). Retry bounded: default 3 attempts, exponential backoff 0.5s/1.0s (suite-asserted), retry only on 429/5xx/timeout/network; 400s never retried; `schema_drift` raised immediately on first sight (:379-392) — no amplification against the shared tokenless pool. |
| 6 | Dependency surface / least privilege | **PASS** | Runtime imports are stdlib-only (`json, logging, math, os, re, time, urllib, uuid, dataclasses, datetime, collections.abc`). `pyproject.toml`: runtime deps unchanged; `jsonschema` in the `dev` extra only. GET-only transport, explicit timeout, no cookies, no auth beyond the optional app token. |
| 7 | Fixture hygiene | **PASS** | 18 fixtures scanned: no tokens, keys, passwords, or auth headers. F07 (429) is `capture_method: "synthetic-from-official-doc"` with `retrieval_timestamp_utc: null`, enforced by `test_every_fixture_embeds_url_timestamp_and_capture_method`; the other 17 record live tokenless KB-scale captures with URL + timestamp. |
| 8 | Provenance integrity (never-guess) | **PASS** | Single fact-emission path (:687-727) iterates `record_keys & PLUTO_COLUMNS` only — a fact cannot exist without a response field. `no_match` emits zero facts and `dataset_version=None`. Absent keys → `absent_columns`; unknown keys → drift signal, no fact. YearBuilt 0 → normalized `None` (unknown) with the raw `"0"` preserved verbatim. Unparseable values pass through verbatim with drift signals, never coerced. Facts refuse to exist without a regex-valid release version (:616-623). |
| 9 | Prompt-injection defenses | **N/A-by-design, PASS** | Deterministic code only; no AI invocation anywhere in the connector; response text is never fed to a model or a tool interpreter by this module. |

## 3. Token-leak trace and adversarial probes

Token flow (every path traced): `os.environ["SOCRATA_APP_TOKEN"]` (:530-531) or explicit `app_token=` param → `_build_headers` (:317-323, `X-App-Token` only) → transport `headers` argument → `urllib.request.Request(url, headers=...)` (:264). The token never enters: the URL (:533), any log call (:534-537, :359-368, :374-378, :396-399, :576-579, :730-735 — audited each; none logs headers), any exception constructor, any `detail` dict, any fact, or any fixture. The `Request` object holding the header is local to `urllib_transport` and is not referenced by any raised exception.

Probe results (run against the real module, worktree HEAD):

| Probe | Setup | Result |
|---|---|---|
| P1a | Real `urllib_transport`, monkeypatched `urlopen` raising `HTTPError(500)` carrying headers, request headers containing canary token | HTTPError converted to `TransportResponse(500, body)`; exception discarded; **no token in any surviving object** |
| P1b | `URLError(OSError("...X-App-Token=<canary>..."))` — a hostile proxy-style reason string | `TransportFailure` message is exactly `network failure: OSError` (type name only — the connector's own surface is clean). The canary is reachable only via the chained `__cause__` if a *caller* formats the full traceback — see informational note F5 |
| P2 | `fetch_by_bbl` with env token set, transport failing repeatedly, DEBUG-level capture of the connector logger | Typed payload and full DEBUG logs **token-free**; no `Traceback` string in payload |
| P3 | 200 response body of 100,000 nested `[` | **Uncaught `RecursionError`** escapes `fetch_by_bbl` (finding F2) |
| P4 | 400 body with `errorCode` containing CRLF + fake log line | errorCode kept verbatim (raw CRLF) inside `detail`; **the connector itself logged nothing** (finding F4, caller-side advisory) |
| P5 | BBL inputs with `&$where=`, `%0d%0a`, `' OR '1'='1`, `#`, trailing space | All metacharacter payloads rejected pre-network; trailing-whitespace input is stripped to the canonical digits and proceeds safely (digits-only URL) |

## 4. Findings

| # | Severity | Finding | Location | Exploitability | Remediation |
|---|---|---|---|---|---|
| F1 | **Low** | No response-size cap: `response.read()` / `exc.read()` read the entire body and `json.loads` runs on it unbounded. A compromised or misbehaving endpoint (TLS-protected official host, so compromise is prerequisite) could return a multi-GB body and exhaust worker memory; expected per-BBL bodies are ~1.5 KB. | `pluto_soda.py:265-272` (transport), `:555` and `:329` (parse) | Low — requires Socrata/TLS compromise; no attacker-controlled URL | Bounded read (e.g. `response.read(10 * 1024 * 1024 + 1)` and reject oversize as `SourceUnavailableError`/drift) |
| F2 | **Low** | Deeply nested hostile JSON raises an **uncaught `RecursionError`** (probe P3), escaping the typed-error contract (S5: typed failures only) and surfacing a raw stack to the caller/worker. | `pluto_soda.py:554-561` (catches only `JSONDecodeError`/`ValueError`), same class in `_classify_400` `:327-330` | Low — same prerequisite as F1 | Add `RecursionError` to both except clauses, mapping to `SourceUnavailableError` (or drift) |
| F3 | **Low** | `urllib`'s default `HTTPRedirectHandler` forwards all request headers except Content-Length/Content-Type on redirects — **including `X-App-Token` to a cross-host redirect target**. An open redirect on or compromise of `data.cityofnewyork.us` would exfiltrate the token. This is the only token-egress vector found. | `pluto_soda.py:260-278` (`urllib_transport` uses default opener) | Low — requires an open redirect/compromise on the pinned official host; token is also low-value (rate-limit quota only) | Disable redirect following (custom opener without `HTTPRedirectHandler`, treating 3xx as `SourceUnavailableError`) or verify the final response host before returning |
| F4 | **Low** | Untrusted Socrata `errorCode` string is embedded **verbatim** (control characters preserved — probe P4) in the typed payload `detail`, unlike `version_raw`/`record_bbl_raw` which are `repr()`-sanitized. The connector never logs it (verified), but any caller that logs `to_payload()` as plain text inherits the M0-T005/M0-T009 log-injection class. | `pluto_soda.py:386, :391` (also `detail.reason` at `:365` — currently safe by construction) | Low — needs a hostile/compromised response AND a caller that logs payloads unsanitized | `repr()`-sanitize (or allowlist-match) `error_code` before placing it in `detail`, consistent with the existing pattern |
| F5 | **Info** | `raise ... from exc` in the transport preserves the underlying exception chain (probe P1b). The connector's own messages and payloads exclude chain internals, but downstream consumers must log `to_payload()` — never `traceback.format_exception` of connector errors — to keep the no-internals/no-secrets guarantee. | `pluto_soda.py:274-278` | Advisory | Document as a consumer contract rule for the property-profile API task (carry-forward) |

No critical, high, or medium findings. F1–F4 are defense-in-depth hardening against a compromised/misbehaving official endpoint; none is reachable by an unprivileged user of this system, because the only user-influenced input (BBL) is regex-pinned to 10 digits before any I/O and the host is constant.

## 5. Verdict

**PASS.** S5 security expectations are met: the token cannot leak on any traced path (request URL, logs, payloads, exception messages, fixtures, facts); URL injection via BBL is impossible; malformed input never reaches the transport; retries are bounded with schema-drift never retried; the connector is stdlib-only with jsonschema dev-only; fixtures are credential-free with F7 labeled synthetic; every emitted fact traces to a response field. Findings F1–F4 are recommended as a single small hardening follow-up task (all four are localized to `urllib_transport` + two `except` clauses + one `repr()`), to be completed before the property-profile API exposes this connector to production traffic; F5 is a documentation carry-forward for that API task. Nothing blocks merge.
