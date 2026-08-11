# M0-T047 — G2 producer self-check (orchestrator)

Reviewed content commit: `c032dfe` on `control/session15-acceptance`.

## Verified
- **Blob parity with #219** (`7ac2f91`): `apps/web/package.json` = `90e801a…`, `apps/web/package-lock.json`
  = `6e75bff…` — byte-identical. The change is exactly nanoid `3.3.16 → 3.3.17` (lock) + exact-pin override.
- **Diff is a strict subset of #219** (2 files, nanoid only; no other package/file touched).
- **Exact pin**: override string is `3.3.17` (no range).
- **Integrity present in lock**: `sha512-xQLf0A3…` for `nanoid-3.3.17.tgz`.

## Machine evidence (authoritative; fail-closed)
- Fresh CI on c032dfe: `web-dependency-security` (audit + committed-lock age gate + npm CLI advisory),
  `web tree re-audit`, `web` (lint+typecheck+build), `web-e2e` — must all be GREEN before accept. These
  re-verify advisory-free + integrity + **age ≥ 7 complete days at today's date (2026-08-11)**.
- #219's identical lock already passed the same full web CI suite; the fresh #220 run reconfirms at HEAD.

## Posture
No local npm run (thin-client). Acceptance is contingent on (1) fresh #220 dependency-security CI green,
(2) G3 (code-reviewer) PASS, (3) G5 (security-reviewer) PASS, (4) D-009 DCV PASS over the real applicable set.

Self-check PASS. Awaiting independent G3 + G5 + DCV and fresh CI.
