# M0-T071 — G0 contract readiness review

- Task: M0-T071 — transitive nanoid 3.3.17 → 3.3.18 (GHSA-2v37-7h3g-55p8; closes B-019) under D-015.
- Reviewed at: 2026-08-18, branch `task/M0-T071-nanoid-ghsa-2v37`, base = current origin/main
  `5c71fe0e08c8717cc20ac232d8bd0d8a328525e1` (deliberately unstacked from the control and
  M0-T070 branches so the dependency gate goes green on main first).

## Contract completeness

- Owner authorization captured verbatim as D-015 (28 requirements, source sha256 `4ec12dddd8fa439c…`),
  including the verified owner decision block: 3.3.18 is the GHSA patched version, published
  2026-08-07, age-gate already satisfied, **no age waiver requested or authorized**.
- Reconciliation items 1–7 completed read-only before contracting: origin/main SHA verified;
  B-019 + the 3.3.17 lock entry confirmed; dependency path `postcss → nanoid ^3.3.16` confirmed
  (sole dependent, single lock instance); 3.3.18 age computed from registry time
  (2026-08-07T16:41:05.696Z → ≈917,151 s ≥ 604,800); all four nanoid GHSA advisories checked —
  3.3.18 affected by none; next free ledger ID M0-T071 (repo-wide grep + origin/main git grep
  empty); fresh worktree `wt-m0t071` created from origin/main, clean.
- Directive regime: `D-001:ALL; D-015:ALL`; resolver returns `ok: true`, 21 applicable rows,
  no selective-citation gap for the packet's allowed_paths.
- Scope minimal: one lockfile, two report files. package.json and .npmrc are explicitly
  forbidden (no direct dependency, no config change); D-014/M0-T070 paths forbidden
  (prohibitions 1–2); supervisor and CI config forbidden.
- Gate profile G0/G2/G4/G5 with independent qa-engineer (G4) + security-reviewer (G5) in
  parallel after the frozen implementation commit, per the owner's one-producer instruction.
- Rollback: delete branch `task/M0-T071-nanoid-ghsa-2v37` + remove `wt-m0t071` before merge.

## Verdict

G0 PASS — contract is complete, bounded, in-regime, and executable.
