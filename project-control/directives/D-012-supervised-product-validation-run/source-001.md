# D-012 — First bounded supervised-auto product validation run (owner-authorized)

Captured verbatim from the owner's typed instruction (session 19, 2026-08-12), across the exchange in
which the owner authorized the supervisor to make its first real product change. Frozen baseline
origin/main = `0d42953f1225135a88dc208e2c3256f06b96199e`.

## Owner instruction (verbatim)

> lets give it a real but small tesk for the nyc program to make

(In response to the orchestrator's structured question "What kind of small, real task should the
supervisor do for its first product run?", the owner selected the option:)

> Small utility + test

(In response to the orchestrator's concrete proposal — add a pure `pluralize(count, singular, plural?)`
helper to `apps/web/src/lib/format.ts` plus unit tests in `apps/web/src/lib/__tests__/format.test.ts`,
run supervised in an isolated worktree with those two files as the only allowed_paths, owner-gated
forwards, nothing merged without the normal gates — the owner replied:)

> yes lets run but can he do it in a new seasen

## Orchestrator interpretation (recorded for traceability, not a substitute for the verbatim text)

The owner authorizes the FIRST bounded supervised-auto product-task validation run: the supervisor
spawns a fresh, separate, contained worker session (a new `claude-opus-4-8` process — "a new session")
that makes a small, pure, self-contained utility change (`pluralize`) to exactly two files, under
supervised mode (owner approves every forward), touching no other paths, and NOT merging to `main`.
This is a one-off, bounded, owner-typed per-tier activation decision for validation; it does NOT
activate standing limited-auto autonomy and does NOT alter R348 (R595 lifts only the turnover channel)
or any other active hold. Any merge of the produced change is a separate step through the normal
ledger gates.
