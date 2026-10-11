# SESSION HANDOFF — seq 156 (2026-10-11, written during task M0-T190; session 01TpXJN7hC1avVgaNN9B4fCz, transcript `33a4b56e-2b0e-47dd-9b18-d09cf4097f56`)

Orientation only. The ledger (`project-control/`), git and CI win over this prose. Owner's lighter form (D-090 R617 to R625): five things, references in place of copies.

## READ FIRST
- **Research and verification (D-093, standing):** `.claude/rules/research-and-verification.md` (always loaded) and the procedure `docs/RESEARCH_AND_VERIFICATION.md`. Before any change to a property fact, rule applicability, calculation input, result or label, read the procedure and the affected records in `docs/research/evidence-records/`. Check: `python3 tools/research_record_check.py --check`.
- **Path mapping (once; detail in the procedure, section 1):** session entry `CLAUDE.md` principle 21 · rule `.claude/rules/research-and-verification.md` · procedure `docs/RESEARCH_AND_VERIFICATION.md` · research index `docs/RESEARCH_REQUESTS.md` · question records `docs/research/evidence-records/` · rule records `docs/zoning-rule-review/` · law captures `docs/research/zr-snapshots/v1/` · evidence packs `docs/research/owner-research/` · design `docs/design/ARCHITECT_PRESENTATION_CONTRACT.md` · this handoff · ledger `project-control/` · PRIVATE (build server only, not in git): owner questionnaire `/root/project/lanes-runtime/owner-docs/OWNER_QUESTIONS.md`, session notes `/root/project/lanes-runtime/owner-docs/<session>/SESSION_NOTES.md` (latest: `session-2026-10-11a`).
- Session notes: the last STATE/CHECKPOINT lines are the truth. Before saying anything is "not done", open the place where it would be.
- Owner questions are asked in chat AND entered in the questionnaire in the same step.

## 1. Where
- Main checkout `/root/project/nyc-buildability` on `candidate/D-024-mrl-option-b` at main. Origin `https://github.com/martin10101/nyc-buildability`.
- Task branch `task/research-verification-rules`, worktree `/root/project/w-rv` (M0-T190).
- Worktree `/root/project/w-wave20`: detached at main `c8f06029`, web modules installed; ready for the next wave. It gets the D-093 files only when moved to a main that contains them.
- Ledger: 380 accepted before M0-T190.
- Preview from `w-wave20` (ports 3001, 8000): `bash /root/project/lanes-runtime/owner-docs/session-2026-10-08c/preview_results_screen.sh status|stop|start|build /root/project/w-wave20`.

## 2. Done and unfinished
- **D-093** (owner, 2026-10-11): permanent research and verification workflow. Task **M0-T190**: the rule, CLAUDE.md principle 21, the procedure, the record format and five Northern Boulevard records (NB-01 to NB-05), the promotion check `tools/research_record_check.py` (CI), a research line in the SessionStart hook, the always-loaded token cap removed (owner: "No dont move just take of the tkoen restrictions"; nothing moved; B1 open), AGENTS.md pointer, handoff-profile entry. Verification sessions: `project-control/reports/M0-T190-verification-sessions.md`.
- **Found:** the Northern Boulevard evidence pack's `data/` folder had never been in git (`.gitignore` ignores `data/`); restored 2026-10-11, 33 files equal to their manifest SHA-256.
- **Wave 22** merged (pull request 486, main `c8f06029`); final report `N/print-main22/report.pdf` (N = `session-2026-10-10a`).

## 3. Helpers, commands, checks
- Session folder `/root/project/lanes-runtime/owner-docs/session-2026-10-11a`: capture `capture_new_directive.py`, contract `contract_task.py`, scope `amend_task_scope.py` (both D-093 copies), records generator `make_nb_records.py` (re-run with `--revision N --reviews <json>` after a review).

## 4. Exact next action
1. Finish M0-T190 if the ledger does not show it accepted and merged (reviews G1, G3, G4, G5, DCV; CI; pre-merge audit; fail-closed merge), then move `w-wave20` to the new main.
2. Next wave, no owner decision needed, in this order, each reading its record first (D-093):
   - DB-231 special density area from data (record NB-05; the unit limit then shows Conditional on the zoning lot);
   - DB-230 rear yard along the short block, ZR 23-344(b) and (c)(3) (record NB-03; block-frontage measure and line classification for every district 23-344 lists);
   - DB-232 zoning-lot warning from the ACRIS index (record NB-01; new connector, G1);
   - then the setback ZR 23-433 with DB-227; then DB-228 and DB-229.
   Sweep the backlog at the contract seam. Update the record (revision, review) in the same change as its code.

## 5. Blockers, holds, decisions
- **Waiting for the owner (none blocks the work):** A1, A2, C1, C2, D1, B1 to B6, F1 (updated 2026-10-11: the consolidated document list for Northern Boulevard, or permission for records requests). G1 answered (cap removed). Full text: the questionnaire.
- **Standing:** Tier D stops; never merge pull request 241. The expansion hold applies except its scoped releases. Every production switch stays off. No `model:` on an Agent dispatch. No timers, no unattended merges. At most 3 builders and 4 reviewers, never sharing files. Builders never touch ports 3000, 3001, 8000. Seam commands run as `bash <script file>`. Read the ledger status before writing "accepted". Nothing is labelled Verified until the owner answers C1 (the promotion check enforces this). The report's numbers stay until the official documents support a change (D-093). Deliver in the format asked.
