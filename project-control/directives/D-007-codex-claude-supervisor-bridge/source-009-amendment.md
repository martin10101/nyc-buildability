# D-007 amendment 8 — owner message (verbatim capture)

- Captured: 2026-08-04T09:10:00+00:00 (approx; session-local)
- Channel: owner chat message (this session)
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main); task branch d68f388
- Amends: source-008-amendment.md

## The owner message

Two records to capture; neither changes V1.1 scope. (1) Supply-chain note: today's npm worm (keyv/cacheable family, Shai-Hulud variant, Aug 4) was checked against this repo and we are CLEAN — apps/web/package-lock.json last committed 2026-07-17 pins keyv 4.5.4, flat-cache 4.0.1, file-entry-cache 8.0.0 (old majors, pre-attack, integrity-pinned); no cacheable, cache-manager, cacheable-request, @cacheable, or spread-org-scope entries anywhere; CI installs via npm ci only, so today's runs could not resolve poisoned versions; the supervisor is pure Python. House rule until I lift it: no npm install or update anywhere in this repo; the apps/web lockfile is frozen. (2) Backlog note: bastani-inc/atomic (MIT, TypeScript+Rust coding-agent runtime) is recorded as a read-only evaluation reference for B-1 (stage-to-stage handoff prior art) and F-4 (schema-declared stage outputs), and as input to the future V2 multi-lane conversation. No adoption, no dependency, not in V1.1 scope; any future adoption would be a separate owner decision through the dependency-admission process. Capture this message verbatim.
