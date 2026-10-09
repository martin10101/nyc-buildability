# G5 SECURITY / POLICY / SCOPE-CONTAINMENT REVIEW — M4-T015

> Orchestrator note: reviewer return saved VERBATIM from the agent-return channel
> (transport entity-decoding only). Reviewer: security-reviewer. Recorded by the
> orchestrator per ADR-005.

I have completed all the checks I can run in this read-only sandbox. Let me compile the G5 report.

**Task:** M4-T015 — D-045 B2 connector build: DCM Street Center Line street-width connector + fail-closed width classifier
**Producer:** backend-engineer (claude-sonnet-5) — I am the independent security-reviewer, not the producer
**Reviewed material:** commit `8538c272` (34 files), verified byte-identical to working tree at HEAD `b3e66078` (empty diff between the two for all M4-T015 scope files)
**Anchor:** toplevel = `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (primary checkout); HEAD = `b3e66078ee50cbf1a8de89d0b85cdd2dfe50dffb` — matched the expected value, so I ran NO git state-changing command.

---

### Checks I ran directly (reproducible)

1. `git rev-parse --show-toplevel` / `git rev-parse HEAD` — anchor confirmed.
2. `git show --stat 8538c272` + `git diff --stat 8538c272 b3e66078 -- <scope>` — scope inventory; confirmed material unchanged since capture.
3. `git show --name-only 8538c272 | grep -Ei '(requirements|pyproject|package.*json|lock|render.yaml|mappluto_geometry|geoclient_address|pluto_soda|zoning_features|ztldb_soda|/bbl.py|app/rules/|app/api/|app/scenario/|app/config.py)'` → **NONE (clean)**.
4. Read all four new source/test files, MANIFEST.json, the registry-draft diff, the producer report, the evidence map, and the task packet in full.
5. `sha256sum` + `wc -c` spot-check on 8 fixtures (metadata, west_100_st, wide_clean_80, synthetic-error, both paging pages, hedged_below, straddle_74_75_3) → **all 8 match the MANIFEST sha256 and byte counts exactly**.
6. Byte-level non-ASCII scan (perl `/[^\x00-\x7F]/`) across the 4 new files + all fixtures → **0 non-ASCII lines**.
7. Secret-pattern scan (`api_key|secret|token|password|bearer|authorization|private_key|BEGIN`) → only match is the docstring literally stating *"no token exists"* (false positive).
8. Hostname scan in fixtures → `services5.arcgis.com` (26x) + `streets.planning.nyc.gov` (1x, inside the official metadata `description` field).
9. Dangerous-call grep (`eval(|exec(|pickle|subprocess|os.system|__import__|marshal|yaml.load|requests.|httpx|socket.|popen`) → only `re.compile(` false positives; **no dynamic-eval / process / deserialization sinks**.
10. Fixture dir size (`du -sk` = **165 KB**) and count (27 files = 26 data fixtures + MANIFEST).

### Checks relying on orchestrator/producer-captured evidence (not re-executed here)

- Full `pytest services/api/tests/connectors` → **619 passed** (orchestrator reproduced at capture; I verified the test *logic* by reading both test files).
- `modularity_check.py --check` → EXIT 0 (orchestrator reproduced). Note: modularity is G4's mandate, not G5; I only observe the clean responsibility split (pure classifier isolated from I/O connector).
- `ruff 0.13.0` clean on the 4 files (producer-run).

---

### Per-mandate findings

**Mandate 1 — Dependency policy §G (ZERO new packages): PASS.**
No `requirements*/pyproject/package.json/lockfile` appears in the commit (verified via `git show --name-only`). The connector imports only stdlib (`hashlib, json, re, urllib.parse, urllib.request, uuid, collections.abc, dataclasses, datetime`) plus its sibling new module `app.connectors.dcm_street_width_classifier`; the classifier imports only `re` + `dataclasses`. No G5 provenance review is triggered because nothing new is admitted.

**Mandate 2 — Scope containment: PASS.**
All 34 changed files fall inside `allowed_paths` (two named connector modules, two named test files, the fixture dir, the registry draft, the producer report) plus `project-control/reports/M4-T015-evidence-map.json`, which the mandate explicitly designates the orchestrator's file. No `forbidden_paths` entry is touched: no `mappluto_geometry_arcgis.py`, `geoclient_address.py`, `pluto_soda.py`, `zoning_features_arcgis.py`, `ztldb_soda.py`, `bbl.py`, `rules/**`, `api/**`, `scenario/**`, `profile/**`, `spatial/**`, `config.py`, `apps/web/**`, `packages/**`, `tools/**`, `.github/**`, or `render.yaml`. No consumer wiring. Confirmed via the grep in check 3.

**Mandate 3 — Injection surface (core G5 item): PASS.**
- The `where` predicate (`dcm_street_centerline_arcgis.py:295-398`) is assembled ONLY from validated components. `borough` is checked against the fixed `BOROUGH_DOMAIN` allowlist (reject otherwise); `street_name` must pass `_SAFE_STREET_NAME_RE = ^[A-Za-z0-9 .,'\-]{1,100}$` and is then single-quote-escaped via `_escape_sql_literal` (SQL standard `'` → `''`); `object_id`/`object_id_in` are validated positive, non-bool ints (list bounded to 50). The complete `where` string is then percent-encoded with `urllib.parse.quote(where, safe='')`. This is defense-in-depth (allowlist AND escape) and is directly tested: `test_unsafe_street_name_is_disallowed` (`Main St'; DROP TABLE segments; --` rejected), `test_street_name_with_apostrophe_is_escaped_not_rejected` (`O'Brien` → `O''Brien`), `test_unknown_borough_is_disallowed`, plus the "exactly one predicate style" XOR guard.
- URL host/path come from module constants `SERVICE_ROOT`/`LAYER_NAME` only — never caller-influenced. SSRF-proof by construction.
- No `eval/exec/pickle/subprocess/os.system/__import__/marshal` (check 9).
- Bounded no-retry fetch (`default_fetch:419-455`): single `urlopen` attempt, `timeout=30.0`, bounded read (`_MAX_BODY_BYTES = 16 MiB`, over-limit → `MalformedResponseError`), `OSError` → typed `UpstreamError`, no retry loop. `# noqa: S310` is justified (URL built exclusively by `build_*_url`).
- HTTP-200 error-object trap (`_parse_json_object:463-496`): a body carrying an `error` object is raised as `UpstreamError`, never returned as data; unparseable body → `MalformedResponseError` (never coerced to an empty result). Tested: `test_http_200_arcgis_error_object_is_typed_upstream_error` (asserts code 400), `test_malformed_response_is_never_a_valid_empty_result`.

  *ADVISORY (LOW, non-blocking):* `default_fetch` uses the default `urllib` opener, which follows HTTP 3xx redirects. Because the request host is a hardcoded HTTPS constant and never caller-influenced, a redirect-based pivot would require the official ArcGIS host itself to issue a malicious `Location` — outside this connector's threat model. For defense-in-depth consistency you may later pin/validate the final response URL host or disable redirects, but this is not required for PASS.

**Mandate 4 — Fixture hygiene: PASS.**
Fixtures are public official DCM geographic data (street names, OBJECTIDs, boroughs) — no PII, no secrets. MANIFEST sha256/byte entries are self-consistent with stored bytes (8/8 spot-verified byte-for-byte; the suite's own `test_manifest_matches_fixture_bytes_on_disk` enforces the full set both directions). The single synthetic fixture is unambiguously marked: filename `provider_error_http200_synthetic.json`, `"synthetic": true`, `"url": null`, and an explicit DOCUMENTED-SYNTHETIC purpose note per the M2-T009 precedent. Total footprint 165 KB (largest fixture 11.7 KB) — KB-scale, thin-client compliant.

**Mandate 5 — Content hygiene: PASS.**
All four new source/test files and every fixture are pure ASCII. No secrets/tokens. The connector's runtime network surface is exactly the primary ArcGIS endpoint (`services5.arcgis.com/.../DCM_Street_Center_Line/FeatureServer/0[/query]`) with bounded predicates only. The lone `streets.planning.nyc.gov` occurrence is verbatim official DCP content inside the captured metadata `description` field (the DCP Street Map viewer link) — an official NYC DCP domain, not an endpoint the code ever calls. (Observed the verbatim source typo "edcept" preserved unaltered in metadata.json — correct provenance discipline, not a producer edit.)

**Mandate 6 — Legal-safety surfaces: PASS.**
The classifier (`dcm_street_width_classifier.py`) emits `wide` on exactly three genuine mathematical-entailment paths: `clean_numeric_ge_75`, `range_both_endpoints_ge_75`, and `gt_inequality_ge_75` (operator `>`/`>=` with bound ≥ 75). Every other class — cutoff-straddling ranges, sub-75 inequalities, approximations/prose (approx markers checked FIRST, so `"~80"` and `"Probably between 80 - 90"` are narrow despite ≥75 numerals), `<=75` (ambiguous by the strict/non-strict discipline at the threshold), Width Irregular, varies, n/a, Unknown/hedged-unknown, negatives, out-of-order ranges, empty/None, non-string, and the catch-all — fails closed to `narrow_fail_closed` with a typed class and review flag. Exhaustively tested (`test_ambiguous_classes_fail_closed_with_review`, `test_every_documented_class_is_exercised_by_this_suite`). The connector adds a second fail-closed layer (`_mapped_street_override`) that can only make an outcome MORE conservative (paper/record/unmapped/unrecognized-Feat_Type never wide), never more permissive, keeping the raw `width_classification` separate and untouched. No compliance is declared: `basis` strings are non-legal parse explanations, the DCP informational-only disclaimer is carried, and OQ-1/OQ-3 remain explicitly open. Geoclient is neither imported nor wired. The registry draft stays `NON-FINAL`.

---

### Summary

- BLOCKING findings: **none**.
- Advisory (LOW, non-blocking): one — redirect-following in `default_fetch` (defense-in-depth only; host is hardcoded and injection-proof).
- Zero new dependencies; scope fully contained; injection surface disciplined and tested; fixtures hygienic and integrity-verified; pure ASCII, no secrets, official-endpoint-only network surface; fail-closed legal-safety posture proven and defense-in-depth verified.

I did not need to return BLOCKED for any sandbox-execution limitation: the security-relevant properties are verifiable by static inspection and artifact hashing, both of which I performed directly; the full pytest/modularity/ruff runs are corroborated by the orchestrator's capture and by my reading of the test logic.

VERDICT: PASS
