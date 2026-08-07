# M0-T040 Producer Report — Phase 2 authority policy simplification (ADR-006, Tier A/B/C/D)

- **Task:** M0-T040 (governance) under directive D-010, directive_refs = ALL
- **Producer:** backend-engineer
- **Worktree:** C:/Users/MLFLL/Downloads/nyc-zoning/orch, branch task/M0-T040-authority-policy
- **Requested status:** awaiting_gate (G0, G2, G3, G5)

## 1. Files created / edited (one-line diff summaries)

| File | Kind | Summary |
|---|---|---|
| `docs/adr/ADR-006-autonomy-tiers.md` | NEW | Accepted ADR defining Tiers A/B/C/D verbatim from D-010 Section 5.1-5.5 (anchor-delimited machine-readable lists), the D-004-R721 supersession for Tier A only, the ADR-005 core-preservation statement, the R595/activation caveat, and the G6 engineering-vs-publication split (Section 6.1/6.2). |
| `tools/test_authority_policy.py` | NEW | stdlib `unittest` suite (22 tests). Parses tier tables FROM the ADR between anchors and set/sequence-compares against an in-test canonical table taken verbatim from D-010 Section 5; encodes the Section 5.5 merge classifier; replays PRs #143-#146. |
| `CLAUDE.md` | EDIT (+20/-5) | "Authority and human-only actions" section now references the ADR-006 tiers; keeps every human-only item and the gates/holds language; adds the R595/manual-Tier-A caveat. |
| `.claude/rules/project-control.md` | EDIT (+2) | Added an ADR-006 tier paragraph after the ADR-005 paragraph; explicitly does not relax producer/reviewer separation or ledger discipline. |
| `docs/PROJECT_CONTROL_PROTOCOL.md` | EDIT (+1) | Worktree/branch convention: added a tier-authority bullet after "Merge only after required gates pass". |
| `docs/GATES_AND_CHECKPOINTS.md` | EDIT (+2) | G6 section: added the engineering-vs-publication split (AD-061..AD-063) without renumbering gates. |
| `project-control/reports/M0-T040-producer-report.md` | NEW | This report. |

`git status --short` shows exactly these 6 repo files (4 modified, 2 untracked) plus this report; nothing outside `allowed_paths` was touched.

## 2. Test results (exact counts)

- **New suite** `python -m unittest tools.test_authority_policy`: **Ran 22 tests — OK** (0 failures, 0 errors). Groups: ADR parse/drift (Tier A/B/C/D set+sequence equality, 5.5 conditions, supersession, R595 caveat, G6 split), merge-condition count (classifier == 10 Section 5.5 conditions), PRs #143-#146 replay (4 cases), and drift-guard self-tests (4 cases).
- **`python tools/validate_directive_compliance.py`**: `directive registry OK: 9 directive(s), 9 active; source hashes, ID append-only, and producer/verifier separation verified.`
- **`python tools/test_project_control.py`**: exit code 0 — `OK: all 22 project-control test groups passed` (S9/S10/S11 lifecycle/acceptance/independence groups all OK; the change to control-plane authority docs did not regress the CLI behavior — no `tools/project_control.py` code was touched).

## 3. Incident record found (PRs #143-#146) — citations

Primary records located and cited in ADR-006 "Incident lesson":

- `project-control/directives/D-004-agent-teams-runtime-adoption/source-020-amendment.md` (owner amendment 19, verbatim). Establishes: the orchestrator itself executed the merges of **PRs #143, #144, #145, AND #146** (not one merge); the mechanism was that allowlisted commands `Bash(gh pr *)`, `Bash(git push *)`, `Bash(git merge*)` **bypass the auto-mode classifier entirely**; owner ruling "a silent classifier — including an allowlist bypass — is not an authorization"; standing rule "from this message forward queue every merge for me regardless of classifier behavior" (basis of D-004-R721). Head at capture: branched from `origin/main = b5589d05...` (merge commit of PR #146).
- `project-control/directives/D-004-agent-teams-runtime-adoption/source-022-amendment.md` (owner amendment 21). Ruling 2: "Merges #143, #144, #145 — RATIFIED. Content was verified through independent paths; nothing is reverted; the incident finding R718-R724 stands unmodified on the record." Head at capture: `origin/main = e7f5078b...`.
- Corrective requirement lineage: the incident finding is D-004-R718..R724; the standing queue-all-merges rule is **D-004-R721**, which ADR-006 narrows for Tier A only (D-004 requirements.json and manifest.json both reference "143").

Honesty note: the record is complete and consistent with the task briefing. No thinner-than-expected gap. The record does NOT contain a formal per-PR CI transcript in these amendment files (it states each merge was "CI-green at its exact head" as an anchor); ADR-006 relies on the owner-ruled principle (allowlist != authorization) rather than re-deriving CI status, which is the load-bearing lesson.

## 4. How AS-1..AS-4 are satisfied

- **AS-1** (ADR defines Tiers A-D exactly per Section 5; records D-004-R721 supersession for Tier A ordinary merges; keeps orchestrator-only CLI/git authority = ADR-005 core; preserves every Section 5.4 hard-deny item and Section 20 hard stop): ADR-006 reproduces Section 5.1 (18 Tier A actions), 5.2 (11-row Tier B map), 5.3 (7 Tier C items), 5.4 (all 14 Tier D items, verbatim + in order), and 5.5 (10 merge conditions verbatim) between machine-readable anchors. The "What ADR-005 keeps" section states the orchestrator-only `project_control.py`/git/gh authority and producer-in-scope / reviewer-read-only rules are unchanged. The "Supersession record" limits D-004-R721's narrowing to ordinary Tier A and states Tier B/C/D + Section 20 unchanged. Tests `test_tier_*_match_canonical`, `test_tier_d_items_match_canonical` (order+content, exactly 14), and `test_supersession_recorded_for_tier_a_only` enforce this.
- **AS-2** (deterministic full-tier test suite, green): `tools/test_authority_policy.py` — every Tier A action classified automatic-after-checks (`test_tier_a_all_classified_automatic_after_checks`); every Tier B class bound to its named specialist review (`test_tier_b_every_class_bound_to_review`); Tier C queue-and-continue never escalating to owner (`test_tier_c_never_escalates_to_owner`); every Tier D item hard-denies (`test_tier_d_every_item_hard_denies`); all 10 Section 5.5 conditions required (`test_merge_conditions_match_canonical`, `test_classifier_covers_every_5_5_condition`). 22/22 green.
- **AS-3** (PRs #143-#146 replay -> queue/deny, never silent merge): `PRs143to146ReplayTest` — `test_allowlisted_merge_without_checks_is_not_permitted` and `test_allowlist_alone_is_not_authorization` assert an allowlisted-command merge without green required checks + specialist review classifies NOT_PERMITTED; `test_ordinary_green_check_merge_is_tier_a_permitted` asserts an ordinary green-check merge is PERMITTED_TIER_A; `test_secret_finding_blocks_even_when_otherwise_green` guards the secret-scan condition. Green.
- **AS-4** (CLAUDE.md/rules leave no passage requiring owner approval for ordinary Tier A work; G6 split recorded; no Tier D weakened; R595 prerequisite untouched, D-010-R104): CLAUDE.md now routes ordinary Tier A merges/continuation through ADR-006 with no owner-approval requirement, while keeping the credentials/payment/secrets/production/legal human-only list and the Tier D hard stops. `.claude/rules/project-control.md` and both docs mirror the tier model; the GATES doc records the G6 engineering-vs-publication split (AD-061..AD-063). ADR-006's activation caveat and CLAUDE.md/rules text state R595 remains a mandatory blocking prerequisite (D-010-R104) — no doc weakens a Tier D item; `test_r595_activation_caveat_present` and `test_g6_split_recorded` enforce.

## 5. Requirement mapping (R006..R010, R061..R063)

| Req | Text (AD) | Where satisfied |
|---|---|---|
| D-010-R006 | AD-006 remove owner approval from routine work | ADR-006 Tier A + supersession record; CLAUDE.md + rules + PROTOCOL edits; `test_tier_a_*` |
| D-010-R007 | AD-007 keep PRs and protected-main workflow | ADR-006 Section 5.5 "use pull requests; do not replace with direct pushes to main"; Tier D items 1-2 preserved; PROTOCOL "No direct producer merge to main" retained |
| D-010-R008 | AD-008 Tier B after specialist review, no routine owner approval | ADR-006 Tier B map; `test_tier_b_every_class_bound_to_review` |
| D-010-R009 | AD-009 keep Section 20 hard stops | ADR-006 Tier D (= Section 20 projection) reproduced verbatim; CLAUDE.md keeps Tier D hard stops; `test_tier_d_*` |
| D-010-R010 | AD-010 continue another accepted dependency when noncritical item blocked | ADR-006 Tier C; `test_tier_c_never_escalates_to_owner`; rules/PROTOCOL Tier C language |
| D-010-R061 | AD-061 separate engineering acceptance from professional publication | ADR-006 G6 split 6.1/6.2; GATES_AND_CHECKPOINTS G6 edit; `test_g6_split_recorded` |
| D-010-R062 | AD-062 downstream may use draft/needs-review rules with visible status | ADR-006 Section 6.1 list ("draft/extracted_draft/needs_review", "never labeled verified", "UI/reports show draft state") |
| D-010-R063 | AD-063 require G6 only for publication/verified claims | ADR-006 Section 6.2; GATES doc "G6 is required only for..."; Tier D items 10-11 keep hard-deny |

Additional binding refs honored: D-010-R107 (begin bounded work without routine approval) reflected in the Tier A/continuation policy; D-010-R104 (R595 activation prerequisite intact) reflected in the ADR activation caveat and CLAUDE.md/rules.

## 6. Section 5/6 items I could NOT faithfully carry over

None. All Section 5.1 (18 actions), 5.2 (11 rows), 5.3 (7 items), 5.4 (14 items), 5.5 (10 conditions), and Section 6.1/6.2 lists were reproduced verbatim and are enforced by tests. Minor formatting normalization only: Tier D item 11 uses a straight ASCII apostrophe ("architect's") consistently in both the ADR and the test canonical to avoid encoding hazards; wording is otherwise identical to the directive.

## 7. Scope / process confirmation

- Only `allowed_paths` files were created/edited (confirmed by `git status --short`): `docs/adr/ADR-006-autonomy-tiers.md`, `tools/test_authority_policy.py`, `CLAUDE.md`, `.claude/rules/project-control.md`, `docs/PROJECT_CONTROL_PROTOCOL.md`, `docs/GATES_AND_CHECKPOINTS.md`, and this report.
- No forbidden path touched: `tools/project_control.py`, `tools/directive_registry.py`, `tools/agent_supervisor/**`, `.github/**`, `apps/`, `services/`, `project-control/directives/**` are all unchanged.
- No `tools/project_control.py` lifecycle command, `git commit/push`, or `gh` was run by the producer. Ledger/git integration is left to the orchestrator.
