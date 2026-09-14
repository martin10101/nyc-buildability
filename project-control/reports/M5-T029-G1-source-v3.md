**G1 — PASS, source scope only.** Task M5-T029. Independent reviewer: source_verifier. Producer: frontend-engineer.

Reviewed SHA: `14c0525ddb28f81cd69da82834dbb24c21539210`  
Submitted tree: `79f99a0b353063cb51050a571b23ee6985a09314`  
Submission identity: `3aab0196825b9ead61f3ab4f293876f4dd3ef9b02f0bc43d6ac4f62f46deccb3`

Review used `/workspace/scratch/cfa2464c5c7f/nycdf-ui-review-v3`. HEAD was independently confirmed through read-only metadata; tree and submission identity are from the orchestrator’s frozen capture. No reviewer edits, git commands or control mutations occurred.

This narrow recheck covers the worker assets, loading configuration, parcel-readiness boundary, tests and expanded agency caption. Passed v2 source evidence is retained for unchanged implementation.

The three admitted public assets are byte-identical to both the installed MapLibre 6.7.0 package and the [registry archive named in the unchanged lock](https://registry.npmjs.org/maplibre-gl/-/maplibre-gl-6.7.0.tgz). Independent bounded retrieval returned HTTP 200 and 4,107,944 bytes; its SHA-512 matched the lock integrity value.

| Asset | Bytes | Independently computed SHA-256 |
|---|---:|---|
| `maplibre-gl-worker.mjs` | 19,181 | `742ce5cfac9eb71015e0893e31b7c2bcffdc6e4bd186007a50eb721d693197b5` |
| `maplibre-gl-shared.mjs` | 492,183 | `64e24fd71a28f597891c8b9b5ead9623aee0e20c0ff9e7e8e3fd9b3949c52407` |
| `LICENSE.txt` | 5,984 | `ee5fc05a0677eaf69601d2c7db0d9ecd6cc27c3abc1d0733bc9ed34707cf8ef2` |

The complete upstream license/notices and worker’s relative shared-module import are preserved. The application sets the fixed same-origin worker URL before constructing the map. No user or source field selects that URL. This arrangement follows [official MapLibre guidance for Next.js](https://maplibre.org/maplibre-gl-js/docs/#installation).

Readiness now requires the loaded `lot-outline` source and returned features from both parcel fill and line layers. Layer installation or raster success alone cannot announce a displayed parcel. A ten-second deadline produces the existing fallback; observers/maps are disposed, and late callbacks cannot restore success. Actual pixel rendering remains separately verified by G3/CI.

Independent execution from `apps/web`:

`./node_modules/.bin/vitest run src/lib/__tests__/map-context.test.ts src/components/address/__tests__/lot-outline-map.test.tsx`

Result: **two files / 32 tests PASS**. Modularity: **435 files, zero failures, 18 existing warnings**. Comparison of **642 protected/shared/client/dependency files found zero changes**. GeoSearch/NYZD clients, hooks, official links, map-source constants and geometry handling remain unchanged.

| Requirement | G1 conclusion |
|---|---|
| D-061-R001 | PASS retained; visual quality remains separate. |
| D-061-R002 | PASS retained; source details and limitations remain accessible. |
| D-061-R003 | PASS retained; new asset provenance independently verified. |
| D-061-R004 | PASS retained; address mapping unchanged. |
| D-061-R005 | PASS for source/readiness contracts; actual rendering pending. |
| D-061-R006 | PASS retained; capability claims unchanged. |
| D-061-R007 | PASS for G1 and targeted tests; complete CI not certified. |
| D-061-R009 | PASS; protected implementation and dependencies unchanged. |
| D-061-R010 | PASS retained; official resolver remains authoritative. |
| D-061-R013 | PASS within retained source-review scope; delivery verification remains separate. |

The v2 live F1 closure remains valid: official `M1-2/R6`, `M1-4/R6A` and `M1-2/R6B` labels parse without altering returned geometry. Address suggestions remain candidates; zoning polygons remain context, never legal determinations. Previously documented source freshness, quota and capture-date limits remain.

Producer-captured HTTP evidence records correct module MIME types and matching asset hashes; this reviewer did not rerun browser serving or WebGL. Full 617-test/build/type results remain producer evidence. **CI 34902199768 and actual-render G3 verification are pending.** No remaining G1 source defect was found; this verdict does not certify task completion or deployment.
