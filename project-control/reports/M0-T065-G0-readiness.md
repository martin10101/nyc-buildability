# M0-T065 Unit B G0 readiness — bounded context compiler

Recorded by the orchestrator (G0 administrative). Branch
`task/M0-T065-context-compiler`, stacked on accepted A2 (M0-T064) merged to main.

## Checks (6/6 PASS)
1. **Packet complete** — objective, gates G0/G3/G4/G5, reviewers, 13 allowed_paths,
   14 forbidden_paths, 6 acceptance scenarios (AS-1..AS-6), documented_test_commands.
2. **Governing directive active** — D-013 (rows applicable to M0-T065: the compiler
   contract R039/R040, the tier amendment R041/R080, R042/R013 budget discipline,
   plus census/provenance R023/R024/R002) + D-001; validator exit 0.
3. **Dependencies accepted** — A1 (M0-T063) and A2 (M0-T064) accepted and merged to
   main; B imports the A1/A2 index (`repo_fingerprint`, `repo_index_incremental`)
   read-only.
4. **Scope resolvable** — decompose the 850-SLOC `context_pack.py` into 5 focused
   modules + a thin compatibility facade (preserving the public names + CLI that
   `test_context_pack.py` depends on), add index consumption + the R040 coverage/
   provenance emission + the owner-approved adaptive 5K-8K tier amendment. The
   drift-locked budget constants (mirrored from the FROZEN
   `tools/agent_supervisor/review_packet.py`) are NOT modified — the tier layers on
   top and only sets the target; the hard ceiling stays min(ordinary, relative).
5. **Modularity path** — all new modules target < 600 SLOC; the facade shrinks
   `context_pack.py`; `tools/modularity_baseline.json` (digest-protected) is not
   edited. Extract-first (behavior-preserving) before adding features, verified by
   the existing `test_context_pack.py` suite (incl. the load-bearing drift-lock).
6. **No concurrent overlap** — B edits only its own module set + tests + docs; no
   other open task touches these; `.github` CI wiring is the standing M0-T043
   residual and out of scope here.

Conclusion: backlog → ready for claim by the orchestrator.
