# SESSION HANDOFF — seq 174 (2026-11-11 02:35 UTC; the owner is shutting down the build server; session 2026-10-27a = `5cb9f851-cfa4-4565-bdd0-8f30581ce977`; notes folder N13 = `lanes-runtime/owner-docs/session-2026-10-27a/`)

Orientation only. The ledger (`project-control/` on `task/wave29-scenario-drawings`), git and CI win over this prose.
Seq 172-173 were kept uncommitted in the primary checkout; this one is committed because the server is going away.

## 1. Where

- The DigitalOcean build server is being shut down (owner, D-094 R321-R324). Everything that lived only there is in the
  PRIVATE repo `martin10101/nyc-buildability-server-backup`: branch `server-backup` (owner-docs incl. N12/N13 and
  `OWNER_QUESTIONS.md`, Claude memory, user settings and skills, owner uploads, `worktrees/INDEX.tsv`, uncommitted work of
  52 work folders as patches) and every server branch (495) plus 137 detached work-folder commits (`backup/detached/*`).
  Restore steps: that repo's README. A new session needs a new Linux build server (the owner's PC is a thin client).
- Main `065e3fb5` (wave 28). Work branch `task/wave29-scenario-drawings` (pushed; this file's commit is its head). Wave 29 is NOT merged.

## 2. Done and unfinished (session 2026-10-27a)

- CI was red from 2026-10-21 on new advisories against pinned packages: blocker **B-032** (open). Repairs:
  - **M0-T199** web lock (next 15.5.28, vitest 4.1.12, overrides vite 7.3.7 + zod 4.6.6; lock by the workflow, run
    40450612409): integrated; reviews code G3+G4 PASS, security G5 PASS (provenance of the new name
    @napi-rs/lzma-linux-x64-gnu: admit). Gates not yet recorded; DCV not yet run.
  - **M0-T200** api tooling lock (uv 0.13.4, setuptools 84.1.0, filelock 4.2.1, certifi 2026.10.19): contracted and
    claimed; its builder was stopped by a usage limit before committing; its partial work (7 files) is in the backup at
    `worktrees/uncommitted/agent-a9d0b80eabc8d98c4/`. Not reviewed. Dispatch a FRESH builder (brief
    `N13/prompt-builder-M0-T200-r1.md`); it may apply that patch and verify it. uv's age is no longer a constraint.
- Integrated on the branch, all reviews PASS, gates/accept owed (they need a green CI run, i.e. M0-T200 first):
  **M5-T178** round 2 (four reviews PASS), **M5-T206** round 2 (three reviews PASS).
- **M5-T173 (W) + M5-T193 (B3)** integrated (`5d671672`, `a50c3c3f` on `b783d161`, `c73b88fd`). At `0b30bd58`: api suite
  10258 passed, 8 skipped; web lint/typecheck/vitest (2792) green. **PDF #6 printed from the real preview at `c12541ef`**
  (`N13/print-w29-c12541ef/`, 11 pages, page diff against main's print in `diff-vs-065e3fb5.txt`). Its five reviews
  (G1 data-contract, G3 code, G3 visual, G4, G5) were stopped by a usage limit with no returns: redo them (brief
  `N13/prompt-review-M5-T173.md`, pinned `c12541ef`; reprint on the new server if the head moves). PDF #6 has NOT been
  sent to the owner and has not been checked page by page.
- Captured: D-094 source-034 (R321-R324, the backup request). Backlog: DB-293 (ci.yml comments name uv 0.11.28),
  DB-294 (absurd entered lot area -> generic 500).

## 3. Exact next action

1. On the new server: clone the main repo, check out `task/wave29-scenario-drawings`, restore `lanes-runtime/owner-docs`
   and the memory from the backup repo (README there).
2. Fresh M0-T200 builder -> integrate -> push -> read CI; expect every job green (B-032 resolved then).
3. Redo the five W/B3 reviews on the PDF #6 print; then gates, DCVs and accepts for M0-T199, M0-T200, M5-T178, M5-T206,
   M5-T173 + M5-T193 at one head; send the owner PDF #6 checked page by page (R317).
4. Then the plan of seq 173 section 4.4 (M5-T180 -> E0-S M5-T199 -> E1 -> E2; website parity parts -> M5-T174; design
   parts; M0-T195 final export).

## 4. Blockers and holds

- B-032 open (api tooling half). Owner questions open: N1, N2, C1, C2 (questionnaire in the backup). Owner decision
  needed for continuing: where the next build server runs.
- Standing restrictions as seq 173 section 5 (never merge PR 241; Tier D stops; expansion hold except scoped releases;
  production switches off; no `model:` on dispatch; heavy runs one at a time under the lock; builders never touch ports
  3000/3001/8000; read CI at the exact head before every gate, accept, merge and handoff; nothing Verified until C1;
  owner updates in four plain bullets, progress by visible proof).
- Usage limits stopped helpers three times this session: brief helpers to write their report early and commit as soon
  as their checks pass.

## Research and verification

Rule `.claude/rules/research-and-verification.md`; procedure `docs/RESEARCH_AND_VERIFICATION.md`. Open records that
condition the next work: NB-01 (zoning lot, access_blocked), NB-04 revision 4 (in W, unreviewed), NB-08/NB-09/NB-10 held.
