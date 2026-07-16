# Gate Report — M0-T009 — G5 Security and Privacy Gate

- **Task:** M0-T009 — Canonical contract schemas, fixtures, and CI contract validation (defect D3 remediation)
- **Gate:** G5 (security and privacy)
- **Reviewer:** security-reviewer (independent of producer)
- **Date:** 2026-07-15
- **Worktree reviewed:** `.claude/worktrees/agent-ac0ceadafeac708be` (branch for M0-T009)
- **Verdict:** **PASS** (no critical/high/medium findings; two LOW, one INFO; follow-up scope recommended)

## Review scope

Diff under review: `.github/scripts/validate_contracts.py`, `.github/workflows/ci.yml` (contracts job), `packages/contracts/schemas/v1/*.schema.json` (6 schemas), `packages/contracts/fixtures/**` (valid, invalid, invalid_schemas). No implementation was modified by this review.

## Methodology note — live probing curtailed by owner

Two live probes (A and B) were executed earlier in this review before the environment owner denied further live/temp-dir probe commands. **All remaining checklist items were closed by static analysis** of the worktree sources, per the owner's instruction. No conclusions below depend on unexecuted probes.

## Probe results (executed before curtailment)

### PROBE A — modern `referencing.Registry` path (validate_contracts.py:81-89)

A crafted remote `$ref` (absolute `https://` URI not present in the registry) was fed to the `Draft202012Validator(schema, registry=registry)` path. Result: `referencing.exceptions.Unresolvable` raised with **no network attempt** (socket guard stayed silent). The modern path is fail-closed offline. **PASS.**

### PROBE B — legacy `jsonschema.RefResolver` fallback (validate_contracts.py:90-99)

The legacy branch **does attempt `requests.get`** on a store miss for a crafted absolute `$ref`. Code-path trace:

1. `load_jsonschema_engine().make_validator` first tries `from referencing import Registry, Resource` (line 81). Only on `ImportError` does it fall to the legacy branch (line 90).
2. Legacy branch builds `store = {doc["$id"]: doc ...}` from repo-loaded schemas only (lines 91-95) and constructs `jsonschema.RefResolver(base_uri=schema.get("$id",""), referrer=schema, store=store)` (lines 96-98).
3. During `validator.iter_errors(instance)` (line 476), a `$ref` resolving to an absolute URI **not in `store`** reaches `RefResolver.resolve_from_url` → `resolve_remote`, whose library implementation issues `requests.get(uri)` (or `urlopen` if requests is absent) — an outbound network fetch of attacker-chosen URI content that would then be trusted as a schema.

**Adjudication: LOW (defense-in-depth gap, not an exploitable path here), because:**

- jsonschema >= 4.18 (installed: 4.26.0) makes `referencing` a **hard dependency**, so the `ImportError` at line 81 cannot fire in any environment where `jsonschema` itself imports; the legacy branch is effectively dead code.
- The CI contracts job (`ci.yml:68-75`) installs **nothing** ("Uses only the runner's preinstalled Python; no extra dependencies"), so in CI the validator runs pure-stdlib (layer-2 structural + mini-validator) with zero network-capable validator code in play.
- **Zero remote `$refs` exist in the shipped contract set** — verified by grep: no `"$ref": "http(s)://..."` anywhere under `packages/contracts/`; all refs are relative file refs (`common.schema.json#/$defs/...`, `analysis_state.schema.json`) or `#`-fragments.
- Schemas and fixtures are repo-committed and review-gated (G3/G5); an attacker would need commit access, at which point they have stronger primitives than a `$ref`.

## Findings

| # | Severity | Location | Finding | Reproduction | Remediation |
|---|----------|----------|---------|--------------|-------------|
| F1 | LOW | `.github/scripts/validate_contracts.py:90-99` | Legacy `RefResolver` fallback can fetch remote `$ref` URIs over the network on a store miss (PROBE B). Dead code under jsonschema >= 4.18 and inert in the no-install CI job, but a latent SSRF/remote-schema-trust primitive if the environment ever regresses to old jsonschema or the fallback is copied elsewhere. | Environment with jsonschema < 4.18 (or `referencing` removed); add a schema containing `"$ref": "https://attacker.example/x.json"`; run the validator with the jsonschema engine active; observe outbound GET. | Delete the legacy branch entirely, or guard it: pass a `handlers={"http": _refuse, "https": _refuse}` dict to `RefResolver`, or raise on any absolute `$ref` not in `store` before constructing the validator. Fold into M0-T005-R1 or a contracts follow-up task. |
| F2 | LOW | `.github/scripts/validate_contracts.py:443,461,492,498,507,519,524,527` and error strings embedding `{instance!r}` (e.g. lines 269, 272, 275) | CI log injection: fixture file paths and fixture/schema **values** are echoed to stdout/stderr unsanitized. A crafted filename or JSON string value containing newlines could forge `OK ...` lines or emit GitHub Actions workflow commands (`::add-mask::`, `::error::`) in the contracts job log. Same pattern as M0-T005 G5 finding F1 in `secret_scan.py` (also LOW). Blast radius is bounded: workflow-level `permissions: contents: read` (ci.yml:12-13), no secrets referenced in the job, and all inputs are repo-committed and review-gated. Note `!r` (repr) already escapes newlines inside values; the residual vector is filenames and the non-repr path interpolations. | Commit a fixture named with an embedded newline (or a value printed without repr); observe forged log line in the contracts job. | Sanitize (strip/escape control characters) in one shared print helper; optionally set `ACTIONS_STEP_DEBUG`-safe printing. Same remediation batch as the M0-T005 F1 fix. |
| F3 | INFO | `.github/scripts/validate_contracts.py:372,497` | Non-UTF-8 fixture/schema file raises `UnicodeDecodeError`, which is not in the `(OSError, json.JSONDecodeError)` handler, so the run crashes with a traceback. Fail-closed (exit code 1), so no gate risk — cosmetic robustness only. | Commit a UTF-16 encoded fixture; validator exits 1 with traceback instead of a clean `FAIL` line. | Add `UnicodeDecodeError` (or `ValueError`) to the `load_json` caller handlers. |

No critical, high, or medium findings.

## Static-analysis closure of remaining checklist items

### (a) DoS / robustness — recursion and crash paths

- `structural_check` (line 108), `validate_instance` (line 248), and `resolve_ref` recursion have **no explicit depth limit** (no `setrecursionlimit`/`RecursionError` handling — grep-confirmed). Traced crash behavior:
  - Deeply-nested JSON: CPython's `json.load` raises `RecursionError` on pathological nesting; `load_json`'s callers catch only `(OSError, json.JSONDecodeError)` (lines 442, 497, 537), so `RecursionError` propagates out of `main()`; the entry point is `raise SystemExit(main())` with no blanket handler, so Python exits with a traceback and **exit code 1 — fail-closed, never exit 0**.
  - Cyclic `$ref` (schema referencing itself) in the mini-validator: unbounded mutual recursion → `RecursionError` → same uncaught path → exit 1.
  - The broad `except Exception` at line 477 covers **only the optional jsonschema engine** and degrades loudly (prints NOTE, keeps the independently-computed stdlib mini-validator verdict from line 471); it cannot convert a mini-validator crash into a pass because `mini_errors` is computed before the try block.
- Every FAIL path increments `failures`; `main` returns `1 if failures else 0` (line 552). No code path prints FAIL and still returns 0. Empty/missing schema root returns 1 (lines 419-425). Invalid fixtures that unexpectedly pass are themselves failures (lines 526-528, 547-549). **PASS** (with F3 as cosmetic note).

### (b) CI log injection and blast radius

Covered as F2 (LOW). Workflow-level `permissions: contents: read` (ci.yml:12-13); the contracts job checks out and runs one stdlib script; no secrets, no write token, no artifact upload. **PASS with LOW finding.**

### (c) Fixtures privacy sweep

- `fixtures/valid/source_fact/geosearch_bbl_fact.json` and `fixtures/valid/property_profile/full_example.json` cite **120 Broadway, Manhattan, BBL 1000477501, BIN 1001026** — a public commercial landmark building drawn from the documented live GeoSearch v2 public-record response (research doc M0-T002). This is public government record data about a commercial property, which is the product's subject matter; no personal data, tenant data, or owner PII is present. **Acceptable.**
- The synthetic lot-area fact is explicitly labeled (`source_id: "test-fixture-synthetic"`, notes field states "SYNTHETIC test data"), satisfying PRD s34 labeling and the source_fact schema's own synthetic-source rule.
- No credentials, tokens, keys, or secrets in any schema or fixture; main's secret scanner (M0-T005) passed post-merge on the same file shapes. **PASS.**

### (d) AI-boundary posture in the contracts

- `source_fact.schema.json:61-66` — `confidence` is `type: number, minimum: 0, maximum: 1`, with description restating PRD s12: confidence must never substitute for legal-review/coverage status. **Bounded and typed.**
- `coverage_status.schema.json:6-14` — closed 6-value enum exactly matching PRD s12; `$defs/data_completeness` closed 3-value enum. No free-text status possible.
- `analysis_state_transition.schema.json:29-33` — `actor` is a closed enum `["system", "user"]` with **deliberately no `ai` value**; description cites PRD s32.1 (AI may not choose or skip workflow states). `correlation_id` required for audit traceability.
- `normalized_value` documented as produced by deterministic normalization code, never AI (source_fact.schema.json:38). **PASS.**

### (e) jsonschema 4.26.0 dependency desk-check

Desk-check from advisory knowledge (no live advisory query — owner-curtailed): no published CVEs are known against the Python `jsonschema` package affecting 4.x as of the reviewer's knowledge (through January 2026). Risk is further bounded because the CI contracts job installs no packages, so jsonschema executes only in developer environments as an optional strengthening layer; degraded stdlib mode is the CI baseline and its banner makes the mode visible (lines 429-434). **PASS (desk-check).**

### (f) Validator code-safety sweep

Full read of `validate_contracts.py` (557 lines): imports are `json`, `re`, `sys`, `pathlib.Path`, `urllib.parse.urljoin` (stdlib) plus optional `jsonschema`/`referencing` inside guarded try/except. **No `eval`, `exec`, `subprocess`, shell invocation, environment mutation, or file writes** — the only file I/O is read-mode `path.open(encoding="utf-8")` (line 372). `re.compile`/`re.search` operate on repo-committed patterns only (ReDoS would require a committed malicious pattern and would at worst hang CI, fail-closed). Input validation of contract values is itself strong: BBL `^[1-5][0-9]{5}[0-9]{4}$`, BIN `^[1-5][0-9]{6}$`, enforced RFC 3339 patterns independent of format-checker availability (common.schema.json). **PASS.**

## G5 checklist

| G5 item | Verdict | Evidence |
|---|---|---|
| RLS and cross-tenant isolation | N/A | Diff contains no database objects, RLS policies, or tenant-scoped runtime code; contracts are static JSON + a CI validator. Tenancy fields are not present in these contracts (introduced in later milestones). |
| Service-role secrecy | PASS | No secrets, keys, or Supabase references anywhere in the diff; ci.yml states and shows no secret usage; contracts job uses no `secrets.` context. |
| Input validation | PASS | Closed enums, bounded numerics, anchored BBL/BIN/ZIP/timestamp patterns (common.schema.json:7-43); validator rejects unknown keywords, dangling `$refs`, invalid patterns; invalid-fixture and invalid-schema suites prove rejection paths. |
| SSRF / injection defenses | PASS (LOW F1) | Modern referencing path fail-closed offline (PROBE A); legacy RefResolver network path exists but is dead code + inert in CI + zero remote $refs shipped (PROBE B, F1). No subprocess/shell/eval (item f). |
| Upload controls | N/A | No upload surface in this diff. |
| Prompt-injection defenses | PASS | Contracts enforce the AI boundary structurally: no `ai` actor in state transitions, closed coverage enums, bounded confidence that cannot substitute for review status (item d). No AI invocation in the diff. |
| Private storage | N/A | No storage buckets or artifacts created; fixtures are small text files in Git per low-storage policy. |
| Sensitive-log redaction | PASS (LOW F2) | Validator logs schema/fixture paths and values only — all repo-committed, non-sensitive test data; residual log-injection shaping is F2 (LOW), consistent with M0-T005 F1 precedent. |
| Least privilege | PASS | Workflow-level `permissions: contents: read` (ci.yml:12-13); contracts job installs nothing, runs one stdlib script, references no secrets, produces no writes. |
| Dependency vulnerabilities | PASS | Contracts job has zero dependencies; optional jsonschema 4.26.0 desk-check clean (item e). |
| DoS / fail-closed exit behavior (task-specific) | PASS (INFO F3) | All crash paths traced to nonzero exit; no FAIL-then-exit-0 path exists (item a). |
| Fixture privacy (task-specific) | PASS | Public-record commercial property data plus clearly-labeled synthetic values; no PII/credentials (item c). |

## Recommended follow-up scope (non-blocking)

1. **Fold RefResolver hardening into M0-T005-R1 or a small contracts follow-up:** delete the legacy `except ImportError` branch at validate_contracts.py:90-99 (jsonschema >= 4.18 guarantees `referencing`), or guard it with refuse-handlers for `http`/`https` schemes. (F1)
2. Batch the log-sanitization helper with the M0-T005 F1 remediation so both `secret_scan.py` and `validate_contracts.py` share one control-character-stripping print path. (F2)
3. Optionally add `UnicodeDecodeError` to the `load_json` caller handlers for a clean FAIL line instead of a traceback. (F3)

## Reviewer attestation

Producer and reviewer identities differ. Implementation was not modified. Live probing was curtailed by the environment owner after probes A and B; remaining items were closed via static analysis as recorded above. Gate recording in the ledger is the orchestrator's responsibility per ADR-005.
