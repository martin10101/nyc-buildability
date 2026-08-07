# D-007 amendment 5 — owner message (verbatim capture)

- Captured: 2026-08-04T07:20:00+00:00 (approx; session-local)
- Channel: owner chat message (this session)
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main); task branch f68f578
- Amends: source-005-amendment.md

## The owner message

Controller pulled --ff-only to 307b7c6. Two items are still not on record and I want them before run 6: (1) CI status — workflow conclusions, not just "wired" — for both bc83092 and 307b7c6 (R554 makes CI-green a packet precondition and neither SHA has been reported); (2) enumerate the 19 diagnostics from this fix — file plus one line each — and confirm none touch validate_decision, the provider-failure classifier, or the audit path; same for the 17 from the runner fix if those were never enumerated. The returncode spot-check is settled — verified independently, keyword arg into the defaulted field, audit carries it — so don't re-litigate that. Then launch run 6: shadow mode only, forward nothing, owner-touch budget unchanged, runtime evidence verbatim to runtime-run6, and report the full cycle — checkpoint validation, the live Codex decision with which model answered and on which attempt, the correlation fields verified, policy classification, the ShadowPlan, and shadow_observation_complete at the acceptance gate.

## Orchestrator reconciliation notes (not owner text)

- The controller's last --ff-only pull actually landed on f68f578 (per the owner's pasted pull
  output in-session), one capture-only commit past 307b7c6 with identical tools/ content.
- Run 6 was already live (launched on the prior "Then launch" instruction) when this message
  arrived; the two report items are delivered alongside it, not before it.
- The 17 runner-fix diagnostics were already enumerated in the prior return (R564).
- 307b7c6's own CI run was cancelled by concurrency supersession when f68f578 was pushed;
  the conclusive run for that content is f68f578's CI = success.
