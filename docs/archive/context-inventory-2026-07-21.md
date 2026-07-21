# Context inventory — 2026-07-21 (durable, non-eager)

Historical/reference record of the context-architecture cleanup (PR #73). Not loaded into any session's
base context. Authoritative live measurement is `python tools/context_budget_check.py` (which also
prints line counts); this file is the fixed before/after snapshot.

## Method
- **Before** measured from the git blob content at base commit `0fb17838d28157bf8a773c92c32056b370cc376f` (`git show <sha>:<path>`).
- **After** measured from this branch's corrected working tree.
- Line endings normalized to LF for reproducibility; **bytes** = UTF-8 byte length; **~tokens** = ceil(chars / 4).
- "Eager" = auto-loaded before any task work = root `CLAUDE.md` + its `@`-imports + unconditional
  `.claude/rules/*.md` (no `paths:`). Path-scoped rules and `@`-referenced docs load on demand and are
  NOT eager. `docs/SESSION_HANDOFF.md` is read by the start-of-session routine (session-start), not auto-injected.

## Before (base `0fb17838d281`)
| Path | Category | Bytes | Lines | ~Tokens |
|---|---|---:|---:|---:|
| `CLAUDE.md` | root | 4,116 | 57 | 1,027 |
| `PRD.md` | @ import | 32,171 | 1133 | 8,026 |
| `GENERATIVE_DEVELOPMENT_STRATEGY_REQUIREMENTS.md` | @ import | 23,734 | 358 | 5,918 |
| `docs/AGENT_OPERATING_SYSTEM.md` | @ import | 6,772 | 154 | 1,683 |
| `docs/GATES_AND_CHECKPOINTS.md` | @ import | 5,204 | 167 | 1,291 |
| `docs/PROJECT_CONTROL_PROTOCOL.md` | @ import | 2,902 | 102 | 721 |
| `docs/ACCEPTANCE_SCENARIO_STANDARD.md` | @ import | 3,127 | 109 | 782 |
| `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md` | @ import | 2,650 | 96 | 660 |
| `docs/IMPLEMENTATION_SEQUENCE.md` | @ import | 3,788 | 88 | 943 |
| `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` | @ import | 4,885 | 86 | 1,216 |
| `.claude/rules/3d-ui-expansion.md` | unconditional rule | 1,645 | 25 | 411 |
| `.claude/rules/expansion-agent-dispatch-hold.md` | unconditional rule | 2,048 | 34 | 510 |
| `.claude/rules/project-control.md` | path-scoped rule | 2,974 | 14 | 740 |
| `docs/SESSION_HANDOFF.md` | session-start | 8,103 | 86 | 2,011 |

### Before — category totals
| Category | Bytes | Lines | ~Tokens |
|---|---:|---:|---:|
| root | 4,116 | 57 | 1,027 |
| @ import | 85,233 | 2293 | 21,240 |
| unconditional rule | 3,693 | 59 | 921 |
| path-scoped rule | 2,974 | 14 | 740 |
| session-start | 8,103 | 86 | 2,011 |

**Eager total (root + @ import + unconditional rule): 93,042 B / ~23,188 tok.** Session-start handoff: 8,103 B / ~2,011 tok.

## After (corrected cleanup)
| Path | Category | Bytes | Lines | ~Tokens |
|---|---|---:|---:|---:|
| `CLAUDE.md` | root | 6,194 | 88 | 1,542 |
| `.claude/rules/3d-ui-expansion.md` | path-scoped rule | 2,303 | 32 | 575 |
| `.claude/rules/backend-api.md` | path-scoped rule | 1,869 | 26 | 466 |
| `.claude/rules/deployment.md` | path-scoped rule | 1,612 | 24 | 398 |
| `.claude/rules/expansion-agent-dispatch-hold.md` | unconditional rule | 1,837 | 31 | 458 |
| `.claude/rules/frontend-web.md` | path-scoped rule | 1,364 | 21 | 339 |
| `.claude/rules/geospatial.md` | path-scoped rule | 1,179 | 21 | 294 |
| `.claude/rules/legal-rules.md` | path-scoped rule | 1,338 | 23 | 330 |
| `.claude/rules/project-control.md` | path-scoped rule | 2,974 | 14 | 740 |
| `docs/SESSION_HANDOFF.md` | session-start | 2,430 | 37 | 603 |

### After — category totals
| Category | Bytes | Lines | ~Tokens |
|---|---:|---:|---:|
| root | 6,194 | 88 | 1,542 |
| unconditional rule | 1,837 | 31 | 458 |
| path-scoped rule | 12,639 | 161 | 3,142 |
| session-start | 2,430 | 37 | 603 |

**Eager total (root + unconditional rule; zero @ imports): 8,031 B / ~2,000 tok.** Session-start handoff: 2,430 B / ~603 tok. Path-scoped rules (3,142 tok across 7 files) load only when their paths are touched.

## Overall reduction (eager, per context load)
| | Bytes | ~Tokens |
|---|---:|---:|
| Before | 93,042 | 23,188 |
| After | 8,031 | 2,000 |
| **Reduction** | **-85,011** | **-21,188 (91.4%)** |

## Estimated recurring reduction
The eager preamble reloads for the main session **and every subagent**. At ~21k tokens saved per
context load: a main session + a 4-reviewer wave (5 contexts) saves ~105k tokens per wave in
preamble alone; the guard (`tools/context_budget_check.py`, CI job `context-budget`) prevents regrowth.

## Archive map
- `docs/archive/README.md` - index (historical, not instruction).
- `docs/archive/expansion-agent-dispatch-prohibition-retired-2026-07-17.md` - retired dispatch prohibition.
- `docs/archive/orchestration-runtime-history.md` - runtime tool/version history.
- `docs/archive/session-handoffs/SESSION_HANDOFF-2026-07-21-pre-refresh.md` - superseded 148-line handoff.
- `docs/archive/context-inventory-2026-07-21.md` - this file.
