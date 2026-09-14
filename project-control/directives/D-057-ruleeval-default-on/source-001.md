# D-057 source-001 (original, verbatim) — owner directive, interactive chat (orchestrator session), 2026-09-14

Capture head: `10aaedccb80b3954f03d7bc1b504807ec8fb21c1` (branch `candidate/D-024-mrl-option-b`).
Frozen origin/main baseline: `d8b3899f61efa6620e18a26541ced96020f5bef9`.
Captured during the owner's live D-043 walkthrough, immediately after the M5-T025 review wave
was dispatched.

## owner-message-verbatim

> ?ruleeval=on can you set this permently so i dont have to add this

## capture-context

- The ask: the internal surfaces (address front door + draft rule-evaluation) currently need
  BOTH the server flag INTERNAL_RULE_EVAL_ENABLED and a per-request `?ruleeval=on`
  (`apps/web/src/lib/rule-evaluation.ts` two-factor gate). The owner wants the plain URL to
  work on the internal deploy without the query param.
- Privacy tradeoff DISCLOSED to the owner before capture: the per-request opt-in was one of
  the named privacy layers (D-043 "unlisted + flag-gated + labeling"); with default-on,
  anyone holding the URL sees the full internal flow immediately. The owner ordered it
  anyway — consistent with their already-accepted D-043 §5 exposure posture. The env-level
  gate, internal/dev labeling, and DRAFT-until-G6 discipline are unchanged.
- Design decision (orchestrator, recorded here; preserves every existing consumer): a blunt
  inversion of factor 2 would break the shared single-server Playwright harness (env flag ON
  for the whole harness; a dozen journey specs rely on plain `/property` rendering the
  BBL-only screen — the param exists precisely to keep them clean) and the committed e2e
  expectations in `rule-evaluation-flag-off.spec.ts`. Instead the change is ADDITIVE: a
  second server-read env var `INTERNAL_RULE_EVAL_DEFAULT_ON` (same true-token rule, absent =
  false = today's behavior). Semantics: main flag off -> everything off (unchanged);
  explicit `?ruleeval=on` -> on (bookmarks keep working); explicit `?ruleeval` present but
  not a true token (incl. `off`) -> off (kill switch, unchanged); param ABSENT -> on iff
  INTERNAL_RULE_EVAL_DEFAULT_ON holds a true token. The e2e harness never sets the new var,
  so ZERO e2e spec changes; the owner sets it once on the Render WEB service (server-read
  per request — no rebuild needed, just the automatic restart on env save).
- `apps/web/src/app/property/page.tsx`'s own docstring already described `?ruleeval=off` as
  "only a fail-safe kill switch" — the implementation never matched it; this change closes
  that doc/impl divergence for the default-on deployment mode.
- Executed as ledger task M5-T026 (parallel disjoint packet; loop still on M4-T020; the
  M5-T025 producer has returned, so concurrent writers stay at 2 of 3).
