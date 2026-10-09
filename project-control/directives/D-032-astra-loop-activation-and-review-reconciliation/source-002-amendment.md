# D-032 source-002 — amendment (owner, 2026-09-06, during first live loop run)

Verbatim owner message (terminal, while run persistent-local-02 was starting in the owner's
window):

---BEGIN VERBATIM---
ok but I dont want it to stop i want this to go on for 24 hours and get the program build will that happen?
---END VERBATIM---

Effect on D-032 (append-only; extends R001's full-time-loop intent):

1. **Continuous product building authorized.** The loop's target shifts from the two
   commissioning hardening tasks to the PRODUCT delivery path of D-032-R015: the orchestrator is
   directed to create the mapped product tasks (starting M2-T020 real-spatial-provider wiring),
   ready them (G0 + claim + isolated worktrees + packets with documented_test_commands), extend
   the owner packet queue, and keep the loop fed and relaunched toward "get the program built".
2. **Honest bound recorded:** a literally uninterrupted 24-hour run is NOT possible under the
   currently certified posture — each `start` is one operator launch bounded by --max-tasks/
   --max-cycles and per-task counters, auto-relaunch (autostart/watchdog) remains R595/Option-A
   owner-gated, B-001 (owner credentials) gates the persistence milestone, and hook-class edits
   are never auto-approved. The deliverable is therefore: maximum hands-off building via an
   extended queue + prompt relaunches (orchestrator-relayed or owner-pasted), with every stop
   being a designed safety stop, not silence.
3. All D-032 prohibitions and holds unchanged (no push/PR/merge/deploy; PR #241; no gate bypass;
   R595/Option-A + R603-R605 owner-only).
