# M5-T022 Producer Report — maplibre-gl@6.7.0 admission (D-040-R001)

Producer: orchestrator. Packet 41abe763-era; G0 PASS; claim recorded. Cites
D-040:D-040-R001 (applicability append, digest a4145aeb -> 6d8c506f).

## 1. What changed (all inside allowed_paths)

- `apps/web/package.json` — ONE added dependency: `"maplibre-gl": "6.7.0"` (exact pin;
  nothing else touched). 6.7.0 is the newest age-gate-passing version (published
  2026-09-02 per the pinned research + registry .time; ~11 days at admission; 6.8.0
  2026-09-07 ~6d and 6.9.0 2026-09-09/10 still FAIL the gate). OSV/Snyk clean;
  BSD-3-Clause; the one historical advisory (CVE-2026-85061 attribution-HTML XSS) was
  fixed in 6.4.1 and is absent from 6.7.0.
- `apps/web/package-lock.json` — regenerated + PROVEN + committed by the workflow bot
  (6d776102, +200/-1): maplibre-gl 6.7.0 plus its transitive tree.

## 2. The transitive tree (enumerated from the lock diff — 22 added nodes, 0 removed)

| Node | Version | Registry | Integrity |
|---|---|---|---|
| maplibre-gl | 6.7.0 | npmjs | sha512 |
| @maplibre/geojson-vt | 6.1.1 | npmjs | sha512 |
| @maplibre/maplibre-gl-style-spec | 26.4.1 | npmjs | sha512 |
| @maplibre/mlt | 1.2.0 | npmjs | sha512 |
| @maplibre/vt-pbf | 4.3.2 | npmjs | sha512 |
| @mapbox/jsonlint-lines-primitives | 2.0.3 | npmjs | sha512 |
| @mapbox/point-geometry | 1.1.0 | npmjs | sha512 |
| @mapbox/tiny-sdf | 2.2.0 | npmjs | sha512 |
| @mapbox/unitbezier | 1.0.0 | npmjs | sha512 |
| @mapbox/vector-tile | 3.0.0 | npmjs | sha512 |
| @types/geojson | 7946.0.16 | npmjs | sha512 |
| earcut | 3.2.3 | npmjs | sha512 |
| gl-matrix | 3.4.4 | npmjs | sha512 |
| json-stringify-pretty-compact | 4.0.0 | npmjs | sha512 |
| kdbush | 4.1.0 | npmjs | sha512 |
| murmurhash-js | 1.0.0 | npmjs | sha512 |
| pbf | 5.1.2 | npmjs | sha512 |
| potpack | 2.1.0 | npmjs | sha512 |
| protocol-buffers-schema | 3.6.1 | npmjs | sha512 |
| quickselect | 3.0.0 | npmjs | sha512 |
| resolve-protobuf-schema | 2.1.0 | npmjs | sha512 |
| tinyqueue | 3.0.0 | npmjs | sha512 |

Every node resolves from registry.npmjs.org with sha512 integrity; every node passed the
workflow's committed-lock 7-day age gate and the blocking whole-tree audit (total==0 at
every severity) BEFORE the bot commit. The G5 provenance review covers this table.

## 3. The proof chain

generate-lockfile run 34729750887: SUCCESS end-to-end on the first dispatch — npm 11.18.0
pinned -> lock regenerated (.npmrc min-release-age=7 + save-exact) -> npm ci deterministic
(integrity + lock<->package.json) -> blocking npm audit PASS + audit JSON total==0 every
severity -> committed-lock release-age gate PASS (all 575 nodes incl. the 22 new) ->
npm CLI advisory PASS -> bot commit 6d776102.

CI at the post-lock head: pending the push of this report (bot pushes do not trigger
ci.yml); the run is the executable authority for S3 (the branch must STAY fully green
with the package admitted; no source imports maplibre yet, so web/web-e2e behavior is
unchanged - the unused-dependency window is intended, the rendering packet follows).

## 4. Honest notes

- The admission deliberately lands BEFORE any source uses the package (S1 posture of the
  web rendering packet consumes it next); the CI web build proves the dependency graph
  installs and builds cleanly.
- No deploy (D-042-R003 posture unchanged); render.yaml/.github untouched (forbidden).
