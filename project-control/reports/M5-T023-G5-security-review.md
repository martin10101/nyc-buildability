# G5 SECURITY/PRIVACY GATE REPORT — M5-T023

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only). Reviewer: independent security-reviewer agent.

## VERDICT: PASS (one required correction — ADVISORY, LOW severity)

Task: M5-T023 — MapLibre lot-outline rendering (first import of admitted `maplibre-gl@6.7.0`) + `lot_geometry` generator wiring (D-040-R001 web half).
Reviewed identity: commit `b99ca6c0` (the only commit in `c6aca328..b99ca6c0` carrying M5-T023 material; commits `0002ddb7..982a3f23` are M5-T024/D-043 control-plane + deploy-checklist doc, out of scope — verified via `git log --name-only`).
Reviewer: security-reviewer (read-only). CI/JS-toolchain evidence captured separately by the orchestrator; I did not block on inability to run npm/Playwright.

---

## Scope-item results

**1. DEPENDENCY POSTURE UNCHANGED — PASS.**
`package.json`, `apps/web/package.json`, and `package-lock.json` are all in `forbidden_paths` and are absent from the diff (confirmed via `git log --name-only b99ca6c0`). The MapLibre runtime is loaded only from the installed package: dynamic `import("maplibre-gl")` (`LotOutlineMap.tsx:227`) and the CSS side-effect `import "maplibre-gl/dist/maplibre-gl.css"` (`layout.tsx:10`). No CDN/unpkg/jsdelivr/maptiler/mapbox/tile/sprite/glyph/font URL anywhere in the new source (grep clean). The map style is fully local/inline (`EMPTY_STYLE`, `LotOutlineMap.tsx:114-124`: `version: 8`, `sources: {}`, one static-color `background` layer). No basemap tile source is wired — matches the packet's by-design statement (`LotOutlineMap.tsx:236-238`).

**2. INJECTION SURFACES — PASS with one ADVISORY finding (see F-1).**
- No `dangerouslySetInnerHTML`, `innerHTML`, `eval`, or `new Function` in any new production/test file (grep clean).
- GeoJSON enters MapLibre only as source `data` (`LotOutlineMap.tsx:251-259`); the Feature `properties` is `{}` (no response field on the map). No response value is interpolated into a MapLibre style expression — all `paint` values are static string literals (`#2f6fb0`, `#1d4e79`, etc.).
- Coordinates are validated as finite numbers before reaching the map: `validateOutlineGeometry` → `isFiniteNumber`/`isValidPosition`/`isValidRing`/`isValidPolygonCoords` (`lot-geometry-api.ts:189-233`); geometry travels only on `single_lot` and structurally unchanged (no first-polygon pick, no dropped ring), asserted by `lot-outline-map.test.tsx:126,157,183`.
- BBL is `encodeURIComponent`-encoded before URL interpolation (`lot-geometry-api.ts:311`), matching `address-api.ts` discipline; the caller (`AddressConfirmCard.tsx:151`) passes only the client-revalidated canonical BBL (`validateBblInput`).
- Bounded reflection is applied to every reflected string via `boundedText`/`boundedToken` in `documentView` (`lot-geometry-api.ts:245-289`).
- No response field is used as a URL/href except the static, already-reviewed `ZOLA_BBL_URL_PREFIX` constant + `encodeURIComponent(canonicalBbl)` (`AddressConfirmCard.tsx:127`). The strong S6 hostile-reflection tests (`address-resolution.test.tsx:634-667`) confirm the reflected-text discipline (`<script>/<img>/<iframe>` payloads render inert, no element materializes, only `#bbl-input` reaches an href).

**3. FLAG / EXPOSURE — PASS.**
No new `NEXT_PUBLIC` variable (only the pre-existing `NEXT_PUBLIC_API_BASE_URL`, `lot-geometry-api.ts:171`). No client-side read of `INTERNAL_RULE_EVAL_ENABLED` — it appears only in a documentation comment (`AddressConfirmCard.tsx:149`) and as a server-side test env var in `fixture_api.py:386`. The lot-outline surface mounts only when a canonical BBL is present (`AddressConfirmCard.tsx:151`), inside the already-flag-gated `AddressResolutionScreen` tree; no second flag read is introduced. The flag-off generic 404 maps to the benign `route_absent` outcome (`lot-geometry-api.ts:403-404`) rendered as "not available in this environment" (`LotOutlineMap.tsx:381-382`) — no internal detail leaked.

**4. HARNESS BOUNDARY — PASS.**
`apps/web/e2e/harness/fixture_api.py` is test scaffolding: it overrides FastAPI dependencies on the real `app` (`get_lot_outline_fetcher`, `get_address_resolver`) only inside `build_app()`, binds to `127.0.0.1` (`:427`), and serves verbatim recorded official geometry fixtures (`services/api/tests/fixtures/mappluto_lot_outline/*`). No production path imports `build_app`/the overrides. No secret material is introduced (synthetic digests are literal `"sha256:" + "a"*64`). The synthetic address-resolver seam (`:331-378`) fabricates a `provenance` object at runtime (source_id `nyc-geoclient`, a Geoclient endpoint URL, a fake digest), but this is generated in the ephemeral test process only, is explicitly labeled synthetic in the docstring, and is **not** written into any committed fixture; the actual data claim rendered as an outline is the real recorded geometry from seam (1). This satisfies "must not fabricate provenance that could leak into committed fixtures presented as official." (Informational: the test-only CORS middleware for `127.0.0.1:3000` is a pre-existing, documented follow-up, not introduced by this task's production surface.)

**5. HEADERS / PII — PASS.**
The client sends only `Accept: application/json` (`lot-geometry-api.ts:331`) — no API keys, tokens, or auth headers. Secret-pattern grep across all new files is clean (only false positives on `outcomeToken`). `X-Correlation-ID` is read from the response, `boundedToken`-bounded, and stored for display (`lot-geometry-api.ts:358`), mirroring the existing `address-api`/`Meta` pattern; it is a reference id, not a secret. No `console.*` in any new production file (grep clean) — no full-response logging.

**6. CSS / SUPPLY CHAIN — PASS.**
`layout.tsx:10` imports the maplibre CSS from `node_modules` (installed package). The `globals.css` additions (`:664-683`, `.lot-outline`/`.lot-outline-map` sizing) contain no remote `@import` or `url()`. Additive layout only.

**7. GENERATOR — PASS.**
`generate_ts_types.py` is a DRY refactor (`_check_generated`/`_write_generated` extraction) plus `lot_geometry` wiring. All writes target `packages/contracts/generated/*` (via `output_path.parent.mkdir` + `write_text`); the only other write is the pre-existing, unchanged `WEB_CONTRACT_PATH` (property_profile). No network (no socket/urllib/requests/httpx), no subprocess/os.system/popen (grep clean). The committed `generated/lot_geometry.ts` is absent from the diff → byte-identity preserved (drift duty held).

---

## Findings

### F-1 (LOW / ADVISORY) — reflected API `attribution` string reaches MapLibre `customAttribution`, an HTML sink, without HTML sanitization
- Location: `apps/web/src/components/address/LotOutlineMap.tsx:218` (`const attribution = view?.attribution ?? ""`) → `:246` (`new gl.AttributionControl({ customAttribution: attribution })`).
- Source of the value: `view.attribution = boundedText(record.attribution, "NYC Department of City Planning (DCP), MapPLUTO")` (`lot-geometry-api.ts:275-278`).
- Issue: `boundedText` (`bounded.ts:35-51`) strips C0/C1 control chars and caps length, but by its own documented contract (`bounded.ts:5-7`) it is safe *because "React already escapes all interpolated text ... the app never uses dangerouslySetInnerHTML."* That guarantee does not hold at this sink: MapLibre GL's `AttributionControl` renders attribution strings as **HTML via `innerHTML`** (its long-standing upstream design, so attributions can carry `<a>` links). `boundedText` does not neutralize `<`, `>`, `"`, or `javascript:`. So a response whose `attribution` field contained e.g. `<img src=x onerror=…>` would be injected into the DOM, bypassing React escaping — a latent DOM-XSS sink. The same `view.attribution` rendered as a JSX text child (`LotOutlineMap.tsx:167`, `AttributionAndAccuracy`) is safe; this is the single exception.
- Current exploitability: LOW. The M5-T020 server route (accepted) sets `attribution` to a server-side constant not derived from user input (the BBL), and transport is first-party HTTPS, so there is no attacker-controlled path into the field today. This is defense-in-depth / latent, not a live vulnerability.
- Test gap: `lot-outline-map.test.tsx` mocks maplibre-gl at the module boundary (`:65-69`), so `MockAttributionControl` only records options (`:47-51`) and never exercises the real `innerHTML` sink; there is no hostile-attribution test analogous to the strong S6 hostile-reflection tests in `address-resolution.test.tsx`.
- Verification caveat: I could not inspect `maplibre-gl@6.7.0` directly (not installed — thin client), so this finding is stated against MapLibre's documented AttributionControl behavior; the remediation is safe regardless of the exact internal.
- Remediation (any one): (a) pass a client-side constant to `customAttribution` (the design only requires the fixed "NYC DCP" attribution text on the map; keep the reflected `view.attribution` for the React-rendered `AttributionAndAccuracy` display), or (b) HTML-escape/allowlist `attribution` before handing it to `customAttribution`, and (c) add a hostile-`attribution` unit assertion. Classified ADVISORY (non-blocking for this gate) given no current attacker-controlled path; recommended as a fast-follow or fold-in before wider (non-first-party / untrusted-upstream) reuse of `LotOutlineMap`.

---

## Reproduction commands (for the orchestrator's record)
- `git log --oneline --name-only c6aca328..b99ca6c0` — confirms M5-T023 material is isolated to `b99ca6c0`.
- `git grep -nE "dangerouslySetInnerHTML|innerHTML|\beval\(|new Function" b99ca6c0 -- <new files>` — clean.
- `git grep -nE "https?://|cdn|unpkg|jsdelivr|tiles?\.|sprite|glyph|maptiler|mapbox" b99ca6c0 -- <new client source>` — only the local `127.0.0.1:8000` API fallback.
- `git grep -niE "api[_-]?key|secret|service[_-]?role|bearer|authorization|supabase" b99ca6c0 -- <new files>` — clean.
- `git grep -nE "subprocess|os\.system|socket|urllib|requests|httpx" b99ca6c0 -- packages/contracts/scripts/generate_ts_types.py` — clean.

## Cross-tenant isolation / service-role secrecy / private storage
Not applicable to this diff (client-side rendering + a stateless read-only GET client + a Python type generator). No service-role key, no Supabase/storage access, no tenant-scoped query in scope. No SSRF surface (the only outbound URL is the app's own API base with an encoded path param). Least privilege and log redaction: satisfied (Accept-only request headers, bounded correlation-id display, no full-response logging).

## Bottom line
The change is a clean, honest, display-only rendering surface with disciplined transport hardening, correct flag inheritance, no external network references, and a byte-identical generated contract. One LOW/ADVISORY defense-in-depth correction (F-1) is recommended. **Verdict: PASS** (F-1 tracked as an ADVISORY required correction; not blocking this gate).
