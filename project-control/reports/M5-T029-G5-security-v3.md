# M5-T029 — G5 security review v3

- **Verdict: PASS**
- Reviewer: independent `security-reviewer`
- Producer: `frontend-engineer`
- SHA: `14c0525ddb28f81cd69da82834dbb24c21539210`
- Tree: `79f99a0b353063cb51050a571b23ee6985a09314`
- Content identity: `3aab0196825b9ead61f3ab4f293876f4dd3ef9b02f0bc43d6ac4f62f46deccb3`
- Worktree: `/workspace/scratch/cfa2464c5c7f/nycdf-ui-review-v3`

This was a read-only review. No files, control records, dependencies or git state were changed.

## Asset integrity and execution boundary

All three explicitly authorized public assets were independently compared byte-for-byte with the installed, lock-admitted **MapLibre 6.7.0** distribution.

| Asset | Bytes | Verified SHA-256 |
|---|---:|---|
| `maplibre-gl-worker.mjs` | 19,181 | `742ce5cfac9eb71015e0893e31b7c2bcffdc6e4bd186007a50eb721d693197b5` |
| `maplibre-gl-shared.mjs` | 492,183 | `64e24fd71a28f597891c8b9b5ead9623aee0e20c0ff9e7e8e3fd9b3949c52407` |
| `LICENSE.txt` | 5,984 | `ee5fc05a0677eaf69601d2c7db0d9ecd6cc27c3abc1d0733bc9ed34707cf8ef2` |

Installed and locked versions both equal `6.7.0`. The worker imports its adjacent shared module. The application sets the fixed root-relative URL `/maplibre/6.7.0/maplibre-gl-worker.mjs` before constructing the map. No source record, URL parameter or user input selects executable code. No CSP relaxation or deployment-configuration change was introduced.

## Rendering integrity and tests

The new observer requires:

1. The `lot-outline` source to be loaded.
2. Rendered features from that source in **both** parcel fill and line layers.

Raster readiness and successful layer installation cannot establish parcel readiness. The owning lifecycle imposes a ten-second deadline, removes the failed map and observer, and rejects late completion. Success, failure and unmount dispose the observer.

Independent command from `apps/web`:

```text
./node_modules/.bin/vitest run \
  src/lib/__tests__/map-context.test.ts \
  src/components/address/__tests__/lot-outline-map.test.tsx
```

**PASS: 2 files / 32 tests.**

The browser tests additionally require painted parcel pixels and exercise worker-request failure. Their final execution remained pending at this review’s CI capture; no browser success is claimed here.

## Preserved protections

Byte comparisons confirmed that v2’s identity announcements, escaped evidence, missing-source closure, source-link validation, address/NYZD requests, session context, canonical clients, dependency manifests and deployment configuration remain unchanged. Prior passing security evidence remains applicable. **G5-F1 remains closed.**

## Requirement conclusions

These conclusions cover G5’s security and integrity scope.

| Requirement | Verdict | Evidence |
|---|---|---|
| D-061-R001 | PASS | Presentation adds no authorization authority. |
| D-061-R002 | PASS | Identity rejection and accessible evidence remain; map readiness no longer reports success before parcel rendering. |
| D-061-R003 | PASS | Source records, links and explicit evidence gaps retain reviewed protections. |
| D-061-R004 | PASS | Bounded one-box address entry is unchanged. |
| D-061-R005 | PASS | Exact admitted worker assets, fixed execution path and bounded parcel-render observation. |
| D-061-R006 | PASS | Capability limits and survey/print boundaries remain unchanged. |
| D-061-R007 | PASS for G5 | Independent checks and current security CI pass; remaining gates stay required. |
| D-061-R009 | PASS | No dependency version, lock, backend, contract, credential or deployment-configuration change. |
| D-061-R010 | PASS | Resolver authority, cancellation and recovery remain unchanged. |
| D-061-R013 | PASS through reviewed work | No branch/deployment mutation occurred in this review; prior main/PR protection remains a delivery requirement. |

## CI scope and conclusion

Inspected `/workspace/scratch/cfa2464c5c7f/ui-browser-evidence/14c0525d-ci-status.json`, captured at `2026-09-14T22:07:21.488Z`, and the adjacent modularity log.

At the reviewed SHA:

- Secret-scan run `34902199770`: **SUCCESS**.
- Dependency-security job `104170522160`: **SUCCESS**.
- Web job `104170522173`: **SUCCESS**.
- Modularity job `104170522210`: **SUCCESS** — 435 files, zero failures, 18 existing warnings.
- CI run `34902199768`: 15 completed jobs successful; browser, control-plane and supervisor jobs still running.

**G5 PASS. No open G5 defects at this identity.** This verdict does not waive pending browser/CI gates or assert whole-system security, legal accuracy, deployed CSP compatibility, or live deployment.
