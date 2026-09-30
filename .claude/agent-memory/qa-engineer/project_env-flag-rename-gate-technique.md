---
name: env-flag-rename-gate-technique
description: How to review an env-var rename/unification gate on the thin-client apps/web (mutation adequacy + CI-vs-reviewed-HEAD identity); learned on M5-T019 (INTERNAL_RULE_EVAL_UI -> INTERNAL_RULE_EVAL_ENABLED, D-040-R002)
metadata:
  type: project
---

Reviewing a pure env-var rename gate on apps/web (M5-T019, D-040-R002 flag unification).

**Mutation adequacy — what actually kills the partial-rename mutants (verify these, don't assume):**
- The rule-evaluation unit test's `const KEY` literal and the lib's `export const ..._ENV_VAR` value MUST match. A one-sided rename (lib-only or test-only) is killed by the existing `"is ON only with env AND opt-in"` assertion: it sets `process.env[KEY]=1` and expects `ruleEvaluationSurfaceEnabled({ruleeval:"on"})===true`; if lib reads a different name the env is unset -> false -> FAIL. So CI's vitest run is the real backstop for KEY<->const drift.
- A config/lib split (playwright.config sets one name, lib reads another) is killed by the web-e2e Playwright specs (rule-evaluation.spec expects the panel visible).
- The "old-name-inert" guard test only DISCRIMINATES if it both sets the OLD name AND deletes the NEW name, then asserts false. Otherwise it's tautological (passes for any impl). It kills the "read both names (NEW ?? OLD)" mutant.
- Token-set-widened mutant is killed by the env-gate `it.each` matrix (`["maybe",false]`, `["",false]`, `["off",false]`) — which tests `ruleEvaluationFlagEnabled(token)` by explicit ARG, so it is name-independent and survives a rename intact.

**CI-evidence identity trap (thin client, web suites CI-only):** the captured CI head can differ from the reviewed HEAD by control-plane-only commits. On M5-T019 producer material was b30f709c, CI ran at 634f1060 (=+progress commit), reviewed HEAD was 1c84d779 (=+CI-evidence +submit commits). Before trusting the CI green, verify via `git -C <worktree> show --stat <sha>` that every commit between the CI head and the reviewed HEAD touches ONLY project-control/** — then the apps/web material CI validated is byte-identical to the reviewed identity. Run git from your OWN worktree with `-C`; the dispatch guard refuses `cd` into the shared ctl24 checkout and refuses compound/loop git.

**Untested-invariant gaps to name as ADVISORY (pre-existing, not introduced by a rename):** (a) no dedicated regression test pins the non-`NEXT_PUBLIC_` server-side-only posture — a coordinated const+KEY mutation to a NEXT_PUBLIC name would survive; verified only by source + a one-time grep; (b) no e2e proves env-absent->disabled end-to-end (single-server harness sets the flag once); covered only at unit level (OFF-by-default + absent + inert-guard).

**Deploy half-split check:** grep the WHOLE repo for the old name; render.yaml / .github / .env.example must carry NEITHER flag (they did) so the only owner action is the Render dashboard rename (the D-040-R002 return note). Remaining old-name hits in docs/ + other agents' memory are historical/descriptive, out of scope, not a functional half-split.

See [[env-var-rename-modularity-noop]] — a pure rename adding only comment lines never moves a file across a modularity threshold (rule-evaluation.ts stayed 503 SLOC, warn=600).
