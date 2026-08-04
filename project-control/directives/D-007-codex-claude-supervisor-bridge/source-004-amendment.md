# D-007 amendment 3 — owner message (verbatim capture)

- Captured: 2026-08-04T00:32:38+00:00
- Channel: owner chat message (this session)
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main)
- Amends: source-003-amendment.md (Part 1 CI-wiring execution)

## The owner message

OWNER AUTHORIZATION — Option A. Capture this message first, then execute
under PR #152:

Admit tzdata (2025.2, the version already proven on my machine) through the
standing dependency-security process: one additive line in
services/api/requirements-tools.in, regenerate the hash-pinned tooling lock
via the pinned-uv workflow, age gate and scans as normal. Diff confined to
that .in line plus the regenerated lock file(s); nothing else in
services/api/** changes. The CI job keeps installing from the lock — no
workflow edit. PR #152 continues to queue for my merge with the new run
green.

Keep the finding in the decision packet's residual-risks section as
proposed, recorded as RESOLVED-BY-ADMISSION with the root cause (hidden
runtime dependency masked by an out-of-lock local install) — and add one
packet recommendation for later: whether doctor/preflight should verify
timezone-database resolvability so a fresh machine fails at setup, not at
its first wake. No build work on that now.

Option B declined — wrong platform, the target is Windows. Option C
declined — no stalling the finale over a one-line admission the age gate
trivially passes.
