# M0-T123 — producer model identity (Amendment-18 discipline applied as standing practice)

Recorded by the orchestrator 2026-08-30. The M0-T123 producer (agent class backend-engineer,
label supervisor-resume-path-producer) ran three bounded rounds (initial + count
reconciliation + hardening), never interrupted.

## Observed identity (final re-read after the hardening round)

```
$ grep -o '"model":"[^"]*"' <producer-subagent transcript>.jsonl | sort | uniq -c
    451 "model":"claude-opus-4-8"
```

**All 451 assistant events across the producer's entire lifetime carry `claude-opus-4-8`
— no second model id ever appeared** (mid-window read: 323/323; final: 451/451).

## Authority

Identical to the M0-T121 record: D-004-R735 (subagent model assignment) via the
`.claude/agents/backend-engineer.md` frontmatter, byte-stable since commit `8b1b386`;
no model override passed at dispatch; no quota/availability/fallback event in the window;
the orchestrator session stayed on Fable 5 throughout. Determination: **AUTHORIZED —
explicitly permitted bounded subagent assignment**; no allowlist consulted or cited.
