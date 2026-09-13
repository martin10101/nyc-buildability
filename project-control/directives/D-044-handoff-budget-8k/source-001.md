# D-044 source-001 (original, verbatim; owner via interactive chat, 2026-09-12 ET / 2026-09-13 UTC)

Owner message (the directive, verbatim):

> We can bump to 8k token budget for handoff

Capture context: issued in the live orchestrator session during /session-handoff, immediately
after the orchestrator noted that the session-handoff profile caps docs/SESSION_HANDOFF.md at
~4000 estimated tokens (the `handoff_token_budget` value in tools/context_budget.json, enforced
fail-closed by tools/context_budget_check.py in the context-budget CI job). The owner's grant
raises that handoff budget to 8000 tokens so the landing handoff can be complete without
over-compression. Scope: the HANDOFF budget only — the eager project-instruction budget
(`eager_token_budget` 6000) and every other guard in the config are unchanged. The one-value
config change is to be executed as a normal gated ledger task citing this directive.
