# D-033 — Supervisor-run gate waves and acceptance; staged R595 activation package (owner, 2026-09-07)

- **Captured:** 2026-09-07 (UTC), session_01WBbzN5Rx17CBSjky5uKmnY, channel: owner terminal prompt.
- **Base identity at capture:** worktree `ctl24`, branch `candidate/D-024-mrl-option-b`,
  HEAD `f2f7963e8c21c161784b5b698434be54b5c71ef8`.

## Verbatim owner text

```
Captured as a directive: plan and implement supervisor-run gate waves and acceptance, and present the staged R595 activation package
```

## Capture context (recorder's note, not owner text)

Given after the owner's architectural critique in the same conversation (2026-09-07): the
orchestrator chat session acting as the management layer grows unbounded context and forces
session handoffs; the owner wants the persistent supervised loop to "mount the full loop,
including whatever job you're doing over here." The orchestrator proposed this exact directive
line and the owner issued it. Framing agreed in that exchange: some management layer must
preserve separation of duties (producer never accepts its own work; reviewer never integrates
its own approvals); the deterministic supervisor controller — not the codex reviewer — is the
correct host for mechanical Tier-A authority actions; **R595/Option-A activation itself remains
an owner-only act** — this directive mandates planning, implementation behind an owner-gated
default-OFF switch, and PRESENTATION of the staged activation package, never activation.
Live context at capture: M2-T020 accepted (161st, first loop-delivered task); R754 closure run
persistent-local-06 (queue v3, M0-T025 → M0-T149) prepared and awaiting the owner's launch.
