# M0-T185 registry research — sharp 0.35.4 -> 0.35.5

Independent second reading by the producer (frontend-engineer). Every value below was read on the day from the official sources named — the GitHub advisory API and registry.npmjs.org — not copied from the task packet or the G0 report.

- **Reading clock (authoritative):** registry.npmjs.org `Date` response header `Tue, 06 Oct 2026 15:31:48 GMT` (the policy's clock is the registry's own UTC clock, not the local/CI clock).
- **Source of ages:** `(reading clock) - time[version]` in whole seconds, per `registry.npmjs.org/<pkg>` `time` fields.

## Outcome: proceed (no STOP condition)

No package is younger than 604800 s, no package NAME is new to the lock, and no advisory affects any new version. The pin to 0.35.5 is made.

**One correction to the G0/packet reading (not a STOP, recorded for the reviewers):** the G0 report states `@img/sharp-wasm32` "is not listed by 0.35.5 and is expected to leave the lock." The registry shows otherwise. `@img/sharp-wasm32` is a *regular* `dependencies` entry of `@img/sharp-freebsd-wasm32` and `@img/sharp-webcontainers-wasm32` (both at 0.35.5), so it **stays** in the lock and bumps 0.35.4 -> 0.35.5. It is not referenced by `sharp`'s own `dependencies`/`optionalDependencies` in either version. Consequence: **27** packages change version, not 26, and **nothing leaves** the lock. The packet's "23 @img/sharp-*" is also imprecise: `sharp` directly lists 15 `@img/sharp-*` platform packages + 10 `@img/sharp-libvips-*` as optionalDependencies; the 16th platform package (`@img/sharp-wasm32`) arrives transitively. This changes only how the lock diff is described; the machine gates in the workflow decide at run time (S3/S6).

## The advisory (GHSA-wq5f-xc86-pv6w)

Read from `https://api.github.com/advisories/GHSA-wq5f-xc86-pv6w` (HTTP 200).

| field | value |
|---|---|
| ghsa_id | GHSA-wq5f-xc86-pv6w |
| cve_id | None (GitHub API reports null; the summary names CVE-2026-96889) |
| severity | high |
| summary | sharp : Vulnerability in librsvg dependency CVE-2026-96889 |
| published_at | 2026-10-06T13:43:57Z |
| affected package | sharp (npm) |
| vulnerable range | `< 0.35.5` |
| first patched | 0.35.5 |

`0.35.5` is outside the vulnerable range `< 0.35.5`, i.e. it is the first patched version.

## sharp 0.35.5 vs 0.35.4 — dependency lists

- `dependencies` (0.35.5): `{"semver": "^7.8.5", "@img/colour": "^1.1.0", "detect-libc": "^2.1.2"}`
- `dependencies` (0.35.4): `{"semver": "^7.8.5", "@img/colour": "^1.1.0", "detect-libc": "^2.1.2"}` — **identical**.
- `optionalDependencies`: the 25 names are **identical** between 0.35.4 and 0.35.5 (15 `@img/sharp-*` platform + 10 `@img/sharp-libvips-*`); every @img/sharp-* version moves 0.35.4->0.35.5 and every @img/sharp-libvips-* version moves 1.3.3->1.3.4. No name added or removed.
- sharp 0.35.5 `dist.integrity`: `sha512-Ywn4OnzGukp7CDMrp08RQ50YKmuwG47brZgIVPTvBaaAfQlRlygrRqSrxdCiL9M+LlzLBiJ68IR1QqvzHyjC7g==`; published `2026-09-27T13:46:24.509Z`.

## Every package whose locked version changes (27)

| package | old -> new | published (UTC) | age at reading (s) | >= 604800 | dist.integrity (registry) |
|---|---|---|---|---|---|
| `sharp` | 0.35.4 -> 0.35.5 | 2026-09-27T13:46:24.509Z | 783923 | yes | `sha512-Ywn4OnzGukp7CDMrp08RQ50YKmuwG47brZgIVPTvBaaAfQlRlygrRqSrxdCiL9M+LlzLBiJ68IR1QqvzHyjC7g==` |
| `@img/sharp-darwin-arm64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:45:21.388Z | 783987 | yes | `sha512-QRUlFQ0WxvdWyqqG/WtI3iupfD5rBzmCHXSdPsY91sAtVtTo7Q4cb6zOccZ3gqEqkr0f1As1ehLqmEpDsRf+lg==` |
| `@img/sharp-darwin-x64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:47:07.861Z | 783880 | yes | `sha512-+BR255RhDlpygUpOc/Jdt1nT6DQ3XG/ERo5wbcdOf5Q320dKtPCKPLR1LJs9VGXRaMa8l1uUa0tkCNOXiAxZUw==` |
| `@img/sharp-freebsd-wasm32` | 0.35.4 -> 0.35.5 | 2026-09-27T13:45:49.555Z | 783958 | yes | `sha512-Y/z91nEZ4uIBX5X3nfTovjU9lHNKFYbL2lpHCLVNmXQK03VIZvXBBt0KxbPGp2SdGSF+2mQU4e+hQaWOt86iAw==` |
| `@img/sharp-linux-arm` | 0.35.4 -> 0.35.5 | 2026-09-27T13:47:45.455Z | 783843 | yes | `sha512-LEaXK2WdXVK5ykcw0buWyPMsmLLL2vpHLD6yrNSW+JGEL3BZPA4tpKN6iaMc4AxTTAoaX/sU1rOL51lcIz48ZQ==` |
| `@img/sharp-linux-arm64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:45:56.196Z | 783952 | yes | `sha512-LYVx5JTsOM2CBzmxreh+nl64/3H6Xb09iSLknqH47z2T2DFFxDeFLP5y4dJwe6H7uGQlHPyEEtIqyo3DYsRwdQ==` |
| `@img/sharp-linux-ppc64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:45:59.613Z | 783948 | yes | `sha512-QVxAAq8evVRI9ia2vqgwrmWucn5Dfv+JdWzj75pD8omHLPSP7f8p20O8jxzjCcuCEQEOtYOZUmX1hkiZ0kdevA==` |
| `@img/sharp-linux-riscv64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:45:42.118Z | 783966 | yes | `sha512-LtdreXguaavKODPIfzJ4kffx7UNt1omwtK0rch4EBbbSTXPnxWmYSayXdLJw0fJzQ97kHt1gL/yh4tvU+nCyRQ==` |
| `@img/sharp-linux-s390x` | 0.35.4 -> 0.35.5 | 2026-09-27T13:46:05.751Z | 783942 | yes | `sha512-UZasTOFiYzotTsGOCu42BfUzP6Tu6Do/947iRm1RsLKvlllxwGcn4RN27LibGWceix4Y+Pmw3jsnTcCQIgWjqA==` |
| `@img/sharp-linux-x64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:45:49.001Z | 783959 | yes | `sha512-SxFtLTeJInhAA9Q836kux2vZNeOBQEx658qvbboZScr0wIARym3IcGmW7KpVD5sbVg0Ojy+udFQdayYIZyoNog==` |
| `@img/sharp-linuxmusl-arm64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:47:04.679Z | 783883 | yes | `sha512-9HbMclmI1zlNkFRs3z9/eBtDjfD0sGlrX1z6b1qwmiFY5ElDLh4BC0LPBdVp7z1DXFiKlIcznf+ZlsuZzLxQqg==` |
| `@img/sharp-linuxmusl-x64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:46:37.431Z | 783911 | yes | `sha512-4KOphqB035HrVdqLZfCgMzzERrQkkzOwRhl4OAkRO1YCldbaFjySXMaK534Mo0V+LndnlJk+sbUyLeU0ULyD1A==` |
| `@img/sharp-wasm32` | 0.35.4 -> 0.35.5 | 2026-09-27T13:46:20.726Z | 783927 | yes | `sha512-Ptsga1su4tQx+LLF1ECS9U6nz5kmrXKo6XVbtR48Ke3ZRxxgaWBu7IDtEe1quo8hiupwm6WFqxVlXaSf7IINGQ==` |
| `@img/sharp-webcontainers-wasm32` | 0.35.4 -> 0.35.5 | 2026-09-27T13:45:43.110Z | 783965 | yes | `sha512-hfhF/FmoQyTUkA0bIKFOtw536BQSeBMe6BF6QyWlrPxT754+TFLaZ7sKKTfvvM0yJgKgaYTwnFCIZ/GuDw5SUA==` |
| `@img/sharp-win32-arm64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:46:30.234Z | 783918 | yes | `sha512-X4t7g+7ZA5DKblCBEXGjUqqemj4vczING/5viFwAL8h4N3qYeyjwdCvRLHi4EdOUI+2Z7UFlp1VM+p/AuEtm6Q==` |
| `@img/sharp-win32-ia32` | 0.35.4 -> 0.35.5 | 2026-09-27T13:46:35.530Z | 783912 | yes | `sha512-5Zm82LoBc43nhwNybZlG7Y1KO//Zhsn306fQl29ZOuStHLGTo3BWL83q3cznX0poxSAMuYL1On/BHBxkBeKr6A==` |
| `@img/sharp-win32-x64` | 0.35.4 -> 0.35.5 | 2026-09-27T13:47:32.335Z | 783856 | yes | `sha512-x76eH0vEiHlcMQu8Y8IenntaACtddpT6W0wmXtWrnKcnKI7ME5DdgqhAD6SEWOEl1v2zDvkZDhFA9KnURwpfqg==` |
| `@img/sharp-libvips-darwin-arm64` | 1.3.3 -> 1.3.4 | 2026-09-27T12:10:42.328Z | 789666 | yes | `sha512-5R89nBYiRdUlSWJxPhO+GVtaXzXSxKnRu/xqMn3KTA3L9EB9Oy/P+Nn2f2vlhPuUdy/Zusb2DarbyTpGCfEDuw==` |
| `@img/sharp-libvips-darwin-x64` | 1.3.3 -> 1.3.4 | 2026-09-27T12:10:37.715Z | 789670 | yes | `sha512-iR2OKH80yi0U+dUplyh3/xdpFvps6YkCwsXenIJxqxR1v9o+xtKTGbS9H7cps+2Vxjc8B1j96p75NmTGjIhtpQ==` |
| `@img/sharp-libvips-linux-arm` | 1.3.3 -> 1.3.4 | 2026-09-27T12:10:47.428Z | 789661 | yes | `sha512-LmRtTsOHuvM2+wlO2Db37dx5MiZhB0FvSunciw48YjdOkZz9KAiRbm8ujeMOA1INqmei5NapFxYEK1D1ZSidmw==` |
| `@img/sharp-libvips-linux-arm64` | 1.3.3 -> 1.3.4 | 2026-09-27T12:10:53.588Z | 789654 | yes | `sha512-Y3dgX/6lE2QhQb+Gxy0WZxfg9MEm/JBjamZpS2IklP7xIQoKN4hzAm7KcMVGtaVDt3neE9OKBC7vAfonA/Lr1A==` |
| `@img/sharp-libvips-linux-ppc64` | 1.3.3 -> 1.3.4 | 2026-09-27T12:11:07.582Z | 789640 | yes | `sha512-Le6boB8Tai0Nis+gIxIpKx68UDVVIqdR8Tin5Yf1z2LJJQLDJvCDRqRu+jC2qCoD+eIomonmOwB4smBRxfVpYQ==` |
| `@img/sharp-libvips-linux-riscv64` | 1.3.3 -> 1.3.4 | 2026-09-27T12:11:13.523Z | 789634 | yes | `sha512-aHkkIEHPRdQEegJN20MLmGtxYD9R2wQr3Cwpddnu5+YKMt6Uzax7S9h5gpZTo8wyrGuZSlfQ63OevL5mTyOC7Q==` |
| `@img/sharp-libvips-linux-s390x` | 1.3.3 -> 1.3.4 | 2026-09-27T12:11:18.421Z | 789630 | yes | `sha512-ra/mB6MikESDUO7Yg+Mi95bFBb9GsObURuhnOv3OqknjGe9sZrG8tCe9q0xSIGrtLgvgw0gKnFWcK4blSgQOuQ==` |
| `@img/sharp-libvips-linux-x64` | 1.3.3 -> 1.3.4 | 2026-09-27T12:11:24.775Z | 789623 | yes | `sha512-GJ//SSXbnwSDes02umB3nDJLFcQzw8a18V8fyhqr6tV515tOEMdImjjxj1AoafMRz56F3PHgftnj1QEKSU1zkw==` |
| `@img/sharp-libvips-linuxmusl-arm64` | 1.3.3 -> 1.3.4 | 2026-09-27T12:10:57.585Z | 789650 | yes | `sha512-hvulFwtjUcagsis6BBxHwGFwWoNZjgYmULGVrZcyfNbjA8hKILbRxGg15/7w5HDyXHXUos/j6baAWqnCyQ2DWA==` |
| `@img/sharp-libvips-linuxmusl-x64` | 1.3.3 -> 1.3.4 | 2026-09-27T12:11:03.153Z | 789645 | yes | `sha512-6zXKeE/p39I1AmA3cJG35eyBGNqNddLnUXjhwBnsGjFPWqf5VKkDBEqaEkPDoTEtkxwi2vv8Tcr2mDyP4So7Fg==` |

- **Count:** 27 (1 sharp + 16 `@img/sharp-*` platform + 10 `@img/sharp-libvips-*`).
- **Youngest:** `@img/sharp-linux-arm` 0.35.5, 783843 s old (> 604800). Every one of the 27 meets the 7-day rule.
- Each `dist.integrity` above is the registry's own value for that exact version; the generate-lockfile workflow's age gate independently re-checks lock integrity == registry integrity and age at run time.

## Name-set comparison with the current lock (`apps/web/package-lock.json`)

- Names 0.35.5 brings that are **absent from the current lock**: none. (No new package name -> no §5 provenance admission needed.)
- Names in the current lock that **0.35.5 no longer lists**: none.
- The transitive closure of `sharp@0.35.4` and `sharp@0.35.5` over `dependencies`+`optionalDependencies` (restricted to `@img/*` and `sharp`) is the **same set of 28 names** for both versions; `@img/colour@1.1.0` is a regular dependency and is **unchanged**.

## Any other advisory against the new versions

Queried the GitHub advisory database (HTTP 200 each):

1. `GET https://api.github.com/advisories?ecosystem=npm&affects=sharp@0.35.5` -> `[]` (empty: no advisory affects sharp at 0.35.5).
2. `GET https://api.github.com/advisories?ecosystem=npm&affects=<all 27 changed packages at their new versions>` -> `[]` (empty). The 27-item `affects` list sent was:

   `@img/sharp-darwin-arm64@0.35.5, @img/sharp-darwin-x64@0.35.5, @img/sharp-freebsd-wasm32@0.35.5, @img/sharp-libvips-darwin-arm64@1.3.4, @img/sharp-libvips-darwin-x64@1.3.4, @img/sharp-libvips-linux-arm@1.3.4, @img/sharp-libvips-linux-arm64@1.3.4, @img/sharp-libvips-linux-ppc64@1.3.4, @img/sharp-libvips-linux-riscv64@1.3.4, @img/sharp-libvips-linux-s390x@1.3.4, @img/sharp-libvips-linux-x64@1.3.4, @img/sharp-libvips-linuxmusl-arm64@1.3.4, @img/sharp-libvips-linuxmusl-x64@1.3.4, @img/sharp-linux-arm@0.35.5, @img/sharp-linux-arm64@0.35.5, @img/sharp-linux-ppc64@0.35.5, @img/sharp-linux-riscv64@0.35.5, @img/sharp-linux-s390x@0.35.5, @img/sharp-linux-x64@0.35.5, @img/sharp-linuxmusl-arm64@0.35.5, @img/sharp-linuxmusl-x64@0.35.5, @img/sharp-wasm32@0.35.5, @img/sharp-webcontainers-wasm32@0.35.5, @img/sharp-win32-arm64@0.35.5, @img/sharp-win32-ia32@0.35.5, @img/sharp-win32-x64@0.35.5, sharp@0.35.5`

Both queries returned HTTP 200 with an empty array. No query failed; nothing was assumed. GHSA-wq5f-xc86-pv6w itself lists `sharp` vulnerable `< 0.35.5` only, so 0.35.5 is not in its range.

## What this shows and what it does not

**Shows:** on the registry and advisory databases as read at `Tue, 06 Oct 2026 15:31:48 GMT`, pinning `sharp` to exactly `0.35.5` moves 27 packages to versions that are each advisory-free at every severity, each at least 604800 s old, each from `registry.npmjs.org`, and each with a known `dist.integrity`; it introduces no new package name and removes none; and the advisory that currently reddens the gate (GHSA-wq5f-xc86-pv6w) does not apply to 0.35.5. So the repair needs no exception of any kind.

**Does not show / out of scope here:** this is a reading of registry metadata, not a proof of the regenerated lock. It does not run `npm install`/`npm ci` and does not itself write `apps/web/package-lock.json` (only `.github/workflows/generate-lockfile.yml` does). It cannot guarantee the registry state at the moment the workflow runs, nor that `npm install --package-lock-only` touches only these 27 entries — the workflow's blocking `npm audit` (total == 0 at every severity), the committed-lock age gate (`dependency_age_gate.mjs`), the npm-CLI advisory check, and an entry-by-entry lock comparison are the authorities that decide at run time (S3, S4, S6). If any of them reports a finding, an under-age package, a new name, or a registry outage, the task stops and reports — no waiver, no gate change.

