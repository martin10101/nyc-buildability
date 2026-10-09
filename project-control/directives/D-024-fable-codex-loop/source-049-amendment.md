# D-024 Amendment 49 — Owner disposition decision A: commit the two M0-T107 drafts as authorized starting state (owner directive, 2026-09-03)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-048-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-03, one message after the resume
  reconciliation reported READY TO RESUME and presented disposition decision A)
- **Context:** Amendment 48 / handoff seq 79 flagged the launch blocker: `wt-m0t107`
  (task/M0-T107-plugin-portability @ c5c6ff77, identity matches the packet) holds two
  UNTRACKED prior-journey drafts at exactly the M0-T107 deliverable paths (lineage
  run_m0t107_j4, authored 2026-08-31 by supervisor-loop-fable-producer — the task's 55%
  progress). The journey script (sha ab051334…, re-verified this session) and its dirty-tree
  guard refuse to launch while the worker tree is not clean. The owner now selects the
  recommended disposition: commit both drafts to the task branch as the authorized starting
  state. Pre-act draft identities (SHA-256, byte-exact, recorded before any git act):
  - `docs/D024_PORTABILITY_PLAN.md` = `7546d4e9e290de631f0b07e9ec36688eb8974e9b0c121679426b61c425a8ae05`
  - `project-control/reports/M0-T107-portability-plan.md` = `b203ebf066b20d4c5005f1e7dbfcede5f950742d2f83f2bba634f5533ef3cb37`
- **Base identity at capture:** control plane `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`,
  branch `candidate/D-024-mrl-option-b` (local only), HEAD
  `2798e148fa8642e5cc0e212d7fed2e48967b1aa4`, tree clean; `origin/main` =
  `d8b3899f61efa6620e18a26541ced96020f5bef9`. Worker `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t107`,
  branch `task/M0-T107-plugin-portability`, HEAD `c5c6ff777928071e3d3a7e555b659256c4d2a667`,
  only the two untracked drafts above. Frozen accepted candidate `3f4cee86` installed.
  M0-T140 + M0-T143 accepted; M0-T107 claimed at 55%.

## Verbatim owner directive

> Commit exactly these two existing M0-T107 drafts to the task/M0-T107-plugin-portability branch as the authorized starting state:
>
> - docs/D024_PORTABILITY_PLAN.md
> - project-control/reports/M0-T107-portability-plan.md
>
> Do not alter their contents, change anything else, push, open a PR, or start the journey. After committing, verify wt-m0t107 is clean and return the commit SHA plus exactly: WORKTREE_CLEAN_READY.
