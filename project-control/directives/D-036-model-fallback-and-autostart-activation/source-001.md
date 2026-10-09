# D-036 source-001 - owner directive (verbatim), 2026-09-07

Channel: owner terminal message, session `session_01WBbzN5Rx17CBSjky5uKmnY`, 2026-09-07 ~15:3xZ.
Immediate context: the orchestrator had reconciled the "built but never armed" state (empty
worker fallback chain after the owner's 2026-08-29 revert-the-pin order; autostart tasks
owner-gated per D-007 S11.4 and never installed; R595 activation staged) and put the arming
list in front of the owner. The owner replied:

## Verbatim

```
ok do it but
1 it needs to know when fable will be back normally Thursday 9pm to check if its back and switch back to fable
2 only go to opus 4.8 xhigh for main agent when quota of the week is exhausted
3 auto start needs to know what time it will be back and if cc is late to reopen it should try each 4 min after up to 50x till its running
```

(Read in context: "do it" = the two offered arming actions - wire the worker fallback chain
and install autostart - subject to the three conditions. "cc" = Claude Code. "season limit" /
"quota of the week" = the weekly Fable usage cap, which normally lifts Thursday 9 PM local.)
