# D-037 source-001 - owner directive (verbatim), 2026-09-07

Channel: owner terminal message, session session_01WBbzN5Rx17CBSjky5uKmnY, 2026-09-07 ~18:1xZ.
Context: watching run-15 (M0-T153 acceptance engine) take repeated REVISE rounds from the
gpt-6-astra reviewer, the owner raised the concern:

## Verbatim

```
No. This is a little bit of a problem. My concern is that codex will keep it in a loop. And for any small little feature that is not a blocker, it will keep asking it to redo the whole thing. We need to figure out a way that codex won't, like, you know, become over... overly obsessive on tasks that require minimum fix.
```

Read in context: the reviewer must stop returning REVISE (which forces a full worker redo) for
minor, non-blocking issues; reserve REVISE/redo for real blockers, and let genuinely minor polish
pass as done-with-a-note instead of looping. Must NOT weaken real gates: correctness, safety,
contract/back-compat, tests, and the repo hard CI rules (modularity, security, dependency-security)
remain blocking.
