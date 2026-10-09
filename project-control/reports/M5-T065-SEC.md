# M5-T065 SEC — independent security review (verbatim reviewer return)

Reviewer: security-reviewer (claude-opus-4-8 per D-064), dispatched by the orchestrator at
the seq-124 T065 wave, pinned to the frozen submit head 65faee54 (material d3793c2e).
Wave evidence (the packet's required gates are G0,G2,G3,G4; the security verdict is
roster evidence for acceptance). Recorded by the orchestrator. The return arrived in four
parts (the first transmission truncated in Section 2; the reviewer re-sent the remainder
in three labeled parts) — joined verbatim at the exact break point below.

---

VERDICT: PASS

# M5-T065 — G5 Independent Security Review

**Task:** D-082 map-drawing input slice — keyboard-operable outline input over the read-only lot map + a flag-gated, UNMOUNTED 4326→2263 correspondence-bridge endpoint, typed client, additive draft adoption.
**Reviewer:** security-reviewer (read-only, primary checkout). **Verdict: PASS** (no blocking findings; two LOW/informational advisories for the future mount seam).

## 1. Identity verification (frozen surface)

- Submit head `65faee54`; material `d3793c2e` (parent `e085eba5`, not the contract base `f98924e5`).
- `git show d3793c2e --numstat` = exactly the 12 allowed_paths, no others.
- `git diff 65faee54..HEAD` over all 12 paths = **empty** (working tree equals the frozen surface).
- `main.py` **not** in the material commit and carries **no** `outline_bridge` reference (UNMOUNTED confirmed).
- Material commit touches **no** dependency manifest (requirements/pyproject/package*.json/lockfiles) — AS-3 no-new-dependency holds at the byte level.
- My verdict binds to this frozen path-scoped content; control-plane peer commits landing mid-review (none touch the 12 paths) do not affect it.

Local checks (from `services/api`): `python -m ruff check app/api/v1/outline_bridge.py` → **All checks passed**; `python -m pytest tests/api/test_outline_bridge.py -q` → **38 passed**.

## 2. Adversarial walkthrough & findings

**Exposure posture — PASS.** Two independent controls. (a) Feature flag: the handler calls `internal_rule_eval_enabled()` **first**, before minting a correlation id or reading the body; `_flag_enabled` returns True only for an explicit true token, absent/empty/unknown → False (fail-safe). <!-- gitleaks:allow (generic-api-key FP on this prose) --> Off → `_not_found()` = generic `{"detail":"Not Found"}`, no correlation id, byte-indistinguishable from an unmounted path. (b) Unmounted: `main.py` includes routers explicitly by name (no auto-discovery); `outline_bridge` appears nowhere in `services/api/app/` except its own module. Reachability requires both a future mount **and** the flag on.

**Input validation — PASS.** Raw body bounded before parse via the shared `_read_body_within_ceiling` streaming accumulator (256 KiB, `MAX_BODY_BYTES`) plus a declared-Content-Length fast path — chunked/under-reporting bodies are caught, nothing buffers past the ceiling. Strict JSON (`json.loads` in try/except → typed 422); non-dict body refused; a strict-encoder parity guard (`allow_nan=False` + `ensure_ascii=False`.encode) rejects NaN/Infinity/unpaired surrogates. `srid` pinned to 4326 (no other CRS accepted). BBL validated by `normalize_bbl` (canonical 10-digit, borough 1–5, block/lot ranges) **before any connector call**. `_parse_drawn_vertices` enforces list-of-exactly-2 finite numbers, count ∈ [3, 1200] (`BRIDGE_MAX_DRAWN_VERTICES = ROUTE_MAX_TOTAL_OUTLINE_POSITIONS = 1200`, single-sourced from the downstream check route); `_is_finite_number` excludes bool and non-finite floats.

**Refusal information-leak posture — PASS.** Every reflected refusal message passes through `_bounded_message` (400-char cap with explicit truncation marker). Messages carry only fixed strings, vertex indices, counts, and formatted numbers — no stack traces, filesystem paths, secrets, or internal object reprs. Correlation-id discipline is clean: `uuid.uuid4().hex`, echoed in the `X-Correlation-ID` header and body; the 404 sentinel carries none. The only caller-input reflection is the invalid-BBL message (`payload["message"]`), which echoes the caller's **own** BBL string bounded to 400 chars — the same discipline as the accepted sibling `proposal_validation` route; not a cross-tenant or secret leak.

**Correspondence-math abuse surface — PASS (no quadratic blowup).** The control-point count `N` comes from the **server-fetched** parcel rings, not caller input, and is capped at `BRIDGE_MAX_CONTROL_POINTS = 64` (else refused `too_many_control_points`). The alignment search is 2·N solves × O(N) each = O(N²) ≤ ~8k float ops. Caller-controlled `drawn_vertices` (≤1200) only touch O(n) neighborhood check + O(n) final mapping — no caller-driven quadratic path. `_solve_affine` guards the singular/collinear case (`det <= 1e-12·…` → None). Bounded.

**SSRF / injection — PASS.** The only caller value reaching a connector is the BBL, strictly reduced to a validated 10-digit numeric identifier before `display_ring`/`authoritative_ring` are invoked; connector target hosts are fixed in the connectors, so no caller-controlled URL/host. No SQL/command surface. `_NUMERIC_RE`/`_NEGATIVE_RE` are linear anchored patterns (no ReDoS) even on a 256 KiB string.

**Cross-tenant isolation / service-role / private storage — N/A here (PASS).** The route reads only public MapPLUTO parcel geometry by BBL through read-only accepted connectors; it stores nothing, holds no per-tenant data, uses no service-role key, and touches no storage. Correspondence provenance in the 200 body (`source_id`, `dataset_version`, `normalized_digest`) is public dataset identity, not a secret.

**No secrets / no new dependency — PASS.** No secret literals in any packet file; no CRS library or hand-rolled Lambert/CRS math (only doctrine-comment mentions of "Lambert/CRS"/"shapely"); numstat confirms no manifest/lockfile change.

**Client-side — PASS.** `outline-bridge-api.ts` and `ProposalOutlineDraw.tsx` use **no** `dangerouslySetInnerHTML`/`innerHTML`/`eval`/`new Function` (grep-clean); all server strings render through React escaping after `boundedText`/`boundedToken` (length-cap + control-char strip / charset allowlist). The decode matrix fails closed: response-size bound before parse, exact `(status,state)` pair enforcement on the **raw** state (no laundering), a malformed 200 → distinct `validation_failure` (missing vertices/correspondence, srid≠2263, or a non-finite vertex all refused, never rendered as bare coordinates), unknown pairs → `unexpected_response`. The client computes no coordinate and re-derives no transform (no client-side measurement); the component only collects lng/lat inputs and posts them, adopting server output verbatim into the draft. `role="alert"`/`role="status"` and the announcer copy carry the disclosed residual honestly (no "survey"/"verified"/"best").

**Log redaction — PASS.** `source_unavailable` logs `source_id` + `correlation_id`; the unexpected-error and crs-mismatch paths log `correlation_id` only — never `str(exc)`, no tracebacks, no user input, no BBL.

## 3. Advisories (LOW / informational — non-blocking, for the future mount seam, not defects in this slice)

- **A1 (LOW/informational).** The route reuses the shared `INTERNAL_RULE_EVAL_ENABLED` flag and carries no per-request authN/authZ or rate limit. When a later seam mounts it, an unauthenticated caller (reaching the internal surface with the flag on) can drive **two** upstream MapPLUTO connector fetches per request. This is bounded (BBL-validated, no SSRF, O(N²)≤~8k compute) and identical to the accepted sibling `lot_geometry`/`condo_records` posture. Recommendation: the mount seam should consciously confirm intended exposure and consider rate limiting then.
- **A2 (informational).** The invalid-BBL refusal reflects the caller's own BBL string (bounded to 400 chars via `_bounded_message`). Acceptable and consistent with the sibling route; noted for completeness.

## 4. Commands run
- `git show d3793c2e --numstat` / `git diff 65faee54..HEAD -- <12 paths>` — identity confirmed, frozen (empty diff).
- `git grep` for dependency manifests, HTML sinks, CRS libs, and `include_router(outline_bridge)` — all clean/absent (router referenced only in its own module; main.py includes routers explicitly by name, no auto-discovery).
- `python -m ruff check app/api/v1/outline_bridge.py` — All checks passed.
- `python -m pytest tests/api/test_outline_bridge.py -q` — 38 passed.

**Files reviewed (absolute):** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\api\v1\outline_bridge.py`, `…\services\api\app\api\v1\proposal_validation.py`, `…\services\api\app\connectors\bbl.py`, `…\services\api\app\config.py`, `…\apps\web\src\lib\outline-bridge-api.ts`, `…\apps\web\src\lib\bounded.ts`, `…\apps\web\src\components\architect\ProposalOutlineDraw.tsx`, `…\services\api\app\main.py`.

VERDICT: PASS — no critical/high/medium findings; two LOW/informational advisories for the future mount seam.

--- END OF REPORT ---
