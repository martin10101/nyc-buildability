# M5-T032 G5 security review (verbatim reviewer return; security-reviewer, read-only, pinned c2437717)

The reviewer's Write tool was disabled this session; the return below is saved verbatim by
the orchestrator per the report-preservation rule.

---

## G5 Security Review — Task M5-T032

**Verdict: PASS**

**Scope:** Frontend-only diff (`apps/web`), reviewed at pinned HEAD `c2437717af33601d61ef467e39fe162e8b797361` (verified `git rev-parse HEAD` matches). Range `15701458..2b440f41`. Reviewer read-only; no writes performed (Write disabled).

### Findings

No critical, high, medium, or low security findings. All seven required checks pass.

1. **Injection into hrefs/DOM — CLEAN.** Every rendered link (`EvidenceInspector.tsx:42`, `EvidenceRecord.tsx:30`, `ReportSources.tsx:32`, `ProvenanceDisclosure.tsx:47`) is built only from `zolaLotUrl` / `plutoRecordUrl` / `datasetLandingUrl`, each returning `null` or `constant-prefix + regex-validated token`. Suggestion/response text (`AddressAutocomplete.tsx`, `AddressResolutionScreen.tsx`) renders through React escaping into inputs and list items only; `onFallback(text)` feeds `street` input `value` (safe). No `dangerouslySetInnerHTML`/`innerHTML`/`eval`/`.href=`/`window.open` added. Hostile-payload tests remain meaningful — `provenance-link.test.ts:139` rejects `javascript:alert(1)`, `1008350041&$limit=1`, `%0A`, CRLF, fullwidth digits, over-length.

2. **URLs from constant prefix + validated token, never server-echoed — CONFIRMED.** `provenance-link.ts:53` `zolaLotUrl` = `ZOLA_LOT_PREFIX` + BBL matching `/^[1-5][0-9]{9}$/` (len 10). `plutoRecordUrl:41` and `datasetLandingUrl:36` unchanged constant-prefix pattern. `sourceFactLinks:80` gates `zolaUrl` on `currentRecordUrl !== null`, so wrong-lot / wrong-source / dataset-conflict all close the ZoLa link (BBL double-validated). Module comment retains "never `request_url`".

3. **Response-size bound + control-char rejection retained on /search — CONFIRMED.** `fetchAddressSearch` (`address-search.ts:178`) → `fetchGeoSearchWithRetry` → `fetchGeoSearchOnce:111` → `boundedBody` (`MAX_BYTES` 128000, throws `too-large`) and `parseAddressSuggestions` → `boundedString:51` (rejects `[\u0000-\u001f\u007f]`, length caps). Autocomplete and /search share the exact same path.

4. **No new external hosts — CONFIRMED.** New constants: `GEOSEARCH_SEARCH = https://geosearch.planninglabs.nyc/v2/search` (same host as existing autocomplete) and `ZOLA_LOT_PREFIX = https://zola.planning.nyc.gov/bbl/` — the DCP-branded host and recommended `/bbl/` convenience route documented in `docs/design/zola-deeplink-url-confirmation.md` (verified 2026-09-12). All other `evil.example` hosts are negative test fixtures. Query text is `encodeURIComponent`-wrapped into `?text=`; host/path are constants (no SSRF).

5. **Retry/backoff not weaponizable — CONFIRMED.** `fetchGeoSearchWithRetry:156`: `maxAttempts` default 3, floored to ≥1 via `Math.max(1, …)`; retries ONLY `source_unavailable` (5xx); timeout, 429, malformed, transport error, and success return immediately (deadline never stacked). Headers are the constant `{ Accept: "application/json" }` — no echo; `credentials: "omit"`, `referrerPolicy: "no-referrer"`. `backoff:98` resolves early on external abort.

6. **`target="_blank"` links keep `rel="noopener noreferrer"` — CONFIRMED** on all new anchors (ZoLa link in all four components; pre-existing GeoSearch docs link unchanged).

7. **No secrets/keys — CONFIRMED.** Scan of added lines found no api-key/secret/token/bearer/authorization/service-role material.

### Broader G5 checklist
Cross-tenant isolation, service-role secrecy, private storage, upload controls, and log redaction are **N/A** — no server, DB, storage, upload, or logging code changed; suggestions never supply the authoritative BBL (picked candidate still routes to Geoclient resolution/confirmation). SSRF/injection defenses and least privilege (credentials omit, no-referrer, no cookies) verified above. Prompt-injection surface: response text is strict-schema + bounded + control-char-filtered and never fed to an LLM nor into an href.

**Files (all absolute):**
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\address-search.ts`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\provenance-link.ts`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\architect\AddressAutocomplete.tsx`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\address\AddressResolutionScreen.tsx`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\architect\{EvidenceInspector,EvidenceRecord,ReportSources}.tsx`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\property\ProvenanceDisclosure.tsx`

Note: I could not write the reviewer memory note (`Write` tool disabled this session); no repository state was modified.

**Verdict: PASS** — orchestrator may record the G5 gate at HEAD `c2437717`.
