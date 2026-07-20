# M2-T007 - G5 Security Review (security-reviewer)

Reviewer: security-reviewer (independent; producer was backend-engineer). Verdict protocol: ADR-005 — this return IS the report; the orchestrator records the gate.

*(Orchestrator note: saved verbatim from the reviewer's agent-return channel per the report-preservation rule; transport entity-decoding only.)*

## 1. Scope and method

Target: committed state of worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T007`, branch `task/M2-T007-zoning-features-connector`, commit `4468954` (= PR #39). Change set verified via `git diff --name-status main...HEAD`: exactly one modified file (`docs/research/source-registry-drafts/zoning-features.json`) plus new files under `services/api/app/connectors/zoning_features_arcgis.py`, `services/api/tests/connectors/test_zoning_features_arcgis.py`, `services/api/tests/fixtures/zoning_features/**`, and the producer report — all inside the packet's allowed_paths; no contract, resilience, profile, workflow, or web files touched. No implementation was modified by this review.

Method: full read of the 1904-line connector, the 1041-line test module (s11 set in detail), `build_fixture_pack.py`, MANIFEST.json spot checks, and the registry draft; grep scans for dangerous constructs and secret-shaped strings; live read-only execution of the test suite in the worktree; interactive adversarial probes (layer allowlist, where-clause reconstruction, outFields smuggling) against the imported module. Producer report section 10 read last and cross-checked. Prior-art baselines applied from my pluto/hardened-client review memory.

Executed evidence (offline, no network — all HTTP replayed through FakeTransport):
- `python -m pytest tests/connectors/test_zoning_features_arcgis.py -q -k "s11 or s5 or s12"` → 30 passed, 50 deselected (0.50s)
- `python -m pytest tests/connectors/test_zoning_features_arcgis.py -q` → 80 passed (0.84s)
- `python -m pytest -q` (full services/api suite, ZF-S13 regression) → 356 passed (13.43s)
- Adversarial REPL probes (section 2.1/2.2 below), all behaving as designed.

N/A duties, stated explicitly: **auth/RLS/tenancy** — no auth surface, no database, no tenant data in this task; **storage buckets** — no storage writes (B-001 persistence boundary respected; fixtures are committed KB-scale test files); **uploads** — no upload path exists. Nothing in the diff touches those planes.

## 2. Findings per duty

### Duty 1 — SSRF / arbitrary-request prevention: PASS

- Every URL originates from the pinned constant `SERVICE_ROOT` (`zoning_features_arcgis.py:135`) plus an exact-match layer key. `_require_layer` (line 413-423) is the ONLY path from caller input into a URL segment: `isinstance(layer, str) and layer in LAYER_SPECS` — dict-key membership, no normalization, no case folding, no strip. Probes confirmed refusal (typed `disallowed_request`, zero transport calls) for: `nyzd/../pluto`, `nyzd?`, `nyzd#frag`, `nyzd/FeatureServer`, ` nyzd`, `nyzd` with trailing tab, `Nyzd`, `b"nyzd"`, absolute URLs, `None`, `123`, empty string. Test `test_s11_non_allowlisted_layer_refused_before_network` (test file line 845) asserts `transport.calls == []`.
- `build_metadata_url` / `build_count_url` / `build_query_url` (lines 432-572): where clause is either the literal `1=1` or must round-trip through `_require_known_where` (line 479-496), which regex-parses and re-validates field membership + value charset — any accepted where is exactly reproducible by `build_attribute_where`. outFields either literal `*` or every entry checked against the layer's known-field inventory (line 515); orderByFields checked against `_FIELD_NAME_SAFE_RE` AND the field inventory (line 531-535); `resultRecordCount` bounded 1..2000 with bool rejection (line 543); `resultOffset` bounded 0..1,000,000 (line 553). Probe `out_fields=["ZONEDIST&f=html"]` refused — parameter smuggling through the comma-join is impossible because field names are restricted to `[A-Za-z0-9_]{1,64}` set-membership.
- The where value is percent-encoded via `quote(where, safe='')` (line 566) — verified in probe output that `'` and space arrive encoded.
- Redirects: the connector reuses `pluto_soda.urllib_transport` with `_NoRedirectHandler` (pluto_soda.py:349-364) — all 3xx refused, never re-issued; in `_request_with_retry` a 3xx falls into the non-retryable unexpected-status branch (line 669-676) and raises typed `UpstreamError`. No redirect can move the request off the pinned host.
- `ResilientZoningFeaturesClient.extract_layer` runs `_require_layer` BEFORE the cache lookup (line 1774, comment "allowlist BEFORE cache"), so the cache cannot launder a disallowed layer; test `test_s11_resilient_client_refuses_before_cache_and_network` asserts zero calls AND zero cache_miss emissions.
- `test_s11_every_built_url_targets_the_pinned_official_root` (line 910) asserts the literal pinned prefix on all three builder outputs.
- Capture script `build_fixture_pack.py`: all URLs are static constants in `CAPTURE_PLAN` under the same `SERVICE_ROOT` (line 37); no argv/env/caller input reaches URL construction (argv selects only the phase name). Bounded in target, though not in transport hardening — see O3.

### Duty 2 — Injection: PASS

- Where-clause: value charset `[A-Za-z0-9 .,'()/&+-]{1,120}` (line 259) excludes `;`, `%`, `=`, `*`, backslash, and control characters; single quotes doubled (line 475). Adversarial reconstruction probes: `ZONEDIST='a'='a'`, `1=1 OR 1=1`, `ZONEDIST='%27) UNION SELECT'`, `OBJECTID='1'` (non-queryable field), trailing `/*` — all refused. The one accepted probe, `ZONEDIST=''' OR 1 --'`, de-escapes to the allowlisted-charset value `' OR 1 --` and is byte-identical to `build_attribute_where("nyzd","ZONEDIST","' OR 1 --")` output — a correctly escaped string literal, not injection. `test_s11_quote_in_value_is_escaped_not_injected` covers the escaping positively.
- Hostile upstream bodies: parsed only after the transport's 10 MiB bounded read (`pluto_soda.py:381-389`, `MAX_RESPONSE_BYTES` at line 100); `_parse_json_object` (line 727) catches `JSONDecodeError`/`ValueError`/`RecursionError` and types them `malformed_response`; non-dict roots refused; ArcGIS error-with-200 typed as upstream error with code int-checked-or-repr'd and message through `_safe_text`. No decompression surface: the request sends no Accept-Encoding, and urllib does not transparently decompress.
- Hostile strings into payloads/logs: every upstream-controlled string entering a detail payload or drift signal passes `_safe_text` (allowlist `_SAFE_TEXT_RE` or `repr()` fallback, line 383-389), `_safe_field_name` (line 392), or `_sanitize_retry_after` (line 594); response keys sanitized via `sorted(map(_safe_text, doc.keys()))` (line 787); spatial-reference and where echoes use `repr()`. Logger calls (lines 639-667, 1189, 1370, 1644) interpolate only connector-built URLs, integers, and correlation ids — never bodies, headers, or raw upstream text. Control-character injection into logs from upstream data is therefore closed; caller-side correlation_id residual noted as O1.

### Duty 3 — Secrets: PASS

- Zero token/credential handling exists: the only header ever sent is `{"Accept": "application/json"}` (line 636), asserted by `test_s11_no_tokens_or_secrets_in_requests_fixtures_or_manifest` (line 925-936), which also scans MANIFEST.json for `token=`, `apikey`, `api_key`, `authorization` and every fixture's `request_url` for `token`. I independently grepped fixtures, MANIFEST, and the registry draft for `token|secret|apikey|api_key|authorization|bearer|password`: the only hits are the benign manifest sentence "no tokens exist in this pack" and a registry note referencing the Socrata X-App-Token *model* on the separate blob record (no value present). The s11 test's needle set is narrower than my grep but its actual coverage is adequate for this keyless pack, and my wider scan found nothing it misses.
- No secret-bearing headers are logged anywhere (headers never enter payloads or log lines; only the sanitized Retry-After value does, into a detail dict).

### Duty 4 — Sensitive-log redaction: PASS

- `ZoningFeaturesConnectorError.to_payload` (line 291-299) emits error_type/message/correlation_id/source_id/layer/detail only — no stack traces, no response bodies, no headers. Detail dicts contain connector-built URLs, integers, and sanitized strings exclusively (verified per raise site across the whole module).
- Correlation ids are `uuid.uuid4().hex` when not supplied (lines 1019, 1232, 1297, 1431, 1773) — random, non-guessable, non-sensitive; `test_s13_correlation_id_minted_when_absent` confirms.

### Duty 5 — Least privilege / resource bounds: PASS

- Response size: 10 MiB per response via reused bounded read. Retries: `max_attempts` bounded (default 3; only 429/5xx/timeout/network retried, line 600-619); Retry-After beyond `retry_after_cap` fails typed instead of blocking (line 684-687). Pages: budget = `ceil(count/page_size) + 2` hard-capped at `HARD_MAX_PAGES` 200 (lines 1494-1510); every loop iteration provably progresses or raises typed (`test_s5_page_budget_exhaustion_bounds_requests` asserts the exact request ceiling). Request budget: one `AnalysisBudget` unit consumed BEFORE each network attempt (line 623-634), never masked by cache/LKG (line 1827-1828). Cache/LKG stores: `TTLCache` bounded by `cache_max_entries`; LKG is an `OrderedDict` evicted at `lkg_max_entries` under a lock (lines 1849-1856) — no unbounded memory store. Fixtures: 860 KB total, largest single file 106 KB — KB-scale, low-storage compliant.
- Filesystem: the connector performs zero filesystem writes; only the test module reads fixtures and only `build_fixture_pack.py` (producer-local, not CI) writes into its own fixture directory.
- Dangerous constructs: grep for `eval(|exec(|pickle|yaml.|subprocess|os.system|__import__|socket.|requests.|httpx` across connector, tests, and capture script — zero hits (one comment-line false positive in the test file).

### Duty 6 — Dependency surface: PASS

Imports are stdlib (`copy, hashlib, json, logging, math, re, threading, time, uuid, collections, dataclasses, datetime, random, urllib.parse`) plus existing in-repo modules (`app.connectors.pluto_soda` read-only reuse, `app.resilience.*` M1-T009 framework). No new third-party dependency; no packaging/CI file changed (diff file list confirms). The reuse of the hardened pluto transport shrinks rather than expands the attack surface.

### Duty 7 — Prompt-injection relevance: PASS (data-only)

No AI consumption exists in this task. Upstream JSON is parsed into typed dataclasses; upstream text is either verbatim *data* (feature attributes/geometry, preserved for provenance and digesting) or sanitized display strings in error payloads. No path renders upstream text as instructions, tool input, or prompt content. Note for future tasks: `features[].attributes` values flow verbatim to downstream consumers by design — any later AI layer must treat them as untrusted data per PRD section 17.

## 3. Defects

None. No Critical, High, Medium, or Low defects found.

## 4. Observations (non-blocking, Low)

- **O1 — caller-supplied correlation_id is not shape-bounded.** All public functions accept an arbitrary `correlation_id: str` that is interpolated into log lines (e.g. line 640-642) and payloads unsanitized. Callers are internal code today (same accepted posture as pluto_soda), but when this connector is wired to an HTTP endpoint that forwards client correlation ids, apply the M2-T002 token allowlist (64-char `[A-Za-z0-9._-]`) at that boundary. Not a defect in this diff.
- **O2 — aggregate extraction memory is bounded only by page_budget x per-response cap.** A compromised pinned host could claim a large count and serve up to 200 pages x 10 MiB each (~2 GiB parsed worst case) before the count-mismatch check. Real layer sizes are 3-4 orders of magnitude smaller and the host is a single pinned official origin, so risk is minimal; a follow-up could add an aggregate feature-count/byte ceiling when the persistence worker (registry "REMAINING PLAN") is built.
- **O3 — build_fixture_pack.py `capture()` uses the default urllib opener** (follows redirects, unbounded `read()`), unlike the runtime transport. Its URLs are static constants under the pinned root, it is producer-local, never executed in CI, and handles no secrets — acceptable as-is; reuse `urllib_transport` if the script is ever promoted beyond fixture capture.
- **O4 — s11 secret-scan needle set is narrower than a full credential grep** (no `bearer`/`password`/`secret` needles, manifest-only for some). My independent wider grep found nothing; consider widening the needles when the pattern is copied to M2-T008/T009.

## 5. Verdict

**PASS** — the connector is allowlist-bounded at every URL construction path with pre-network typed refusal (probe- and test-proven), reuses the hardened redirect-refusing bounded transport, handles no secrets, redacts hostile upstream text from logs and payloads, bounds every retry/page/memory/store resource, adds no dependencies, and all 80 connector tests plus the full 356-test api suite pass offline; only Low, non-blocking observations remain.

Relevant files (worktree root `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T007`):
- `services\api\app\connectors\zoning_features_arcgis.py`
- `services\api\tests\connectors\test_zoning_features_arcgis.py`
- `services\api\tests\fixtures\zoning_features\build_fixture_pack.py`
- `services\api\tests\fixtures\zoning_features\MANIFEST.json`
- `docs\research\source-registry-drafts\zoning-features.json`
- `services\api\app\connectors\pluto_soda.py` (reused transport, unmodified)
