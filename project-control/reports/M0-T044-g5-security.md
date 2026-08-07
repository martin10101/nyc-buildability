# Gate Report

- **Gate ID:** G5 (security-reviewer leg)
- **Task ID:** M0-T044 — Automatic safe GitHub flow (0A.8 item 8; AD-077; Section 19.4 proofs)
- **Reviewer:** security-reviewer (independent; read-only)
- **Producer:** backend-engineer (content commit af46b3e)
- **Result: PASS** (shadow-only acceptance) — 2 new MEDIUM activation-checklist items, 1 LOW, 2 INFO; none blocking.
- **Clean environment/worktree used:** worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T044-github-flow`. Reviewed the current worktree content of the three named files (github_flow.py, test_agent_supervisor_github_flow.py, external_effects.py). Base `origin/main` 341fa4d.

## Acceptance criteria reviewed
AS-1..AS-5 as executable proofs; the seven G5 security dimensions from the packet; the Section 5.2 supervisor-code rubric (security leg); and the security-sufficiency of the pinned G3 MINOR-1/MINOR-2 for a shadow-only acceptance.

## Directive/requirement verification (security-scoped)
I am the security leg; the full requirement-by-requirement compliance pass belongs to `directive-compliance-verifier` (producer ≠ verifier). Verdicts below are the *security-relevant* re-derivation at reviewed content identity.

| Requirement ID | Content identity | Security verdict | Reproduced evidence |
|---|---|---|---|
| D-010-R006 (AD-006 remove owner approval from routine push/PR/merge) | worktree 3 files | PASS | `authorize_push` auto-allows the exact task branch (Tier A); `ReviewRouting.owner_approval_required` hard-`False` with no setter (gf.py:160,182-189); `evaluate_merge` has no owner condition — yet HARD-DENYs (force/main/secret/identity) are preserved via `push_policy`. Removal of approval does not remove hard-deny. |
| D-010-R007 (AD-007 keep PR + protected-main) | worktree 3 files | PASS | Flow uses PR create + `github_pr_merge`, never direct main push; `authorize_push` HARD-DENYs `main`/`master`/`*/main`/force; `evaluate_branch_cleanup` never deletes a protected default. Tests 114-129, 422-426 reproduced. |
| D-010-R010 (AD-010 continue another dependency) | worktree 3 files | N/A (no security surface in this module) | Queue-and-continue is loop/scheduler behavior; not implemented here and not claimed. Defer to directive-compliance-verifier. |
| D-010-R077 (AD-077 prove automatic safe GitHub flow) | worktree 3 files | PASS | The "safe" invariants — hard-denies, secret-block (cond_secret_scan_clean), no-blind-retry (reconcile/guard), journal integrity — are present and proven; residual fail-open items are activation-gated (SEC-2). |
| D-010-R093 (AD-093 no speculative feature) | worktree 3 files | PASS (with note) | Surface = exactly §19.4/§5.5/§5.2; `github_pr_merge` kept out of live `MODELED_EFFECTS`. Note: the generic `extra_specs` override on the live-path class is broader than a merge-only shadow strictly needs (SEC-1). |
| D-010-R116 / R117 (session re-dispatch; SHADOW-ONLY + R595 binding, no new obligations) | worktree 3 files | PASS | SHADOW-ONLY preserved: no live/CI/hook path imports the module (grep repo-wide); R595 activation gate not lifted; `MODELED_EFFECTS` unchanged. |

## Steps independently executed
1. Read all three files under review + supporting `models.py`, `push_policy.py`, `policy.py` (path_matches/file_class/FILE_CLASS_PATTERNS/SECURITY_RELEVANT_CLASSES/CONTROLLER_PATHS/main_branch_names), `durable_state.py` (record_before/after_effect), and the invariant-9 test.
2. Repo-wide grep for `github_flow|shadow_effects_journal|SHADOW_EFFECT_SPECS`, `extra_specs`, `ExternalEffectJournal(`, `MODELED_EFFECTS`, and injection primitives (`subprocess|os.system|Popen|eval(|exec(|shell=|__import__`).
3. Grounded Tier-B/Tier-D in the D-010 source-001.md §5.2 table (lines 631-643) and §5.4 (661-680), and pulled the 7 requirement texts from requirements.json.
4. Ran the full suite: `python -m pytest -q tools/test_agent_supervisor_*.py` → **1271 passed, 2 skipped in 84.9s (exit 0)** — matches the expected 1271/2.

## Expected versus actual
- Expected full suite 1271 passed / 2 skipped → **actual identical.**
- Expected invariant 9 intact (`github_pr_merge` absent from `MODELED_EFFECTS`) → confirmed at external_effects.py:70-94 and `test_invariant_9_no_modeled_effect_performs_a_gated_action` (asserts no member is destructive/named merge/deploy) passes.
- Expected no live wiring → confirmed: the ONLY non-test/non-doc reference to the shadow symbols and the ONLY `ExternalEffectJournal(` call passing `extra_specs` is `github_flow.shadow_effects_journal`, invoked solely by the test's `effects()`. Every other journal constructor (crash/adversarial/invariants/policy/recovery tests and all live paths) passes no extra_specs; default behavior is byte-identical.

## Evidence paths
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/agent_supervisor/github_flow.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/agent_supervisor/external_effects.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/test_agent_supervisor_github_flow.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/agent_supervisor/push_policy.py`, `policy.py`, `durable_state.py`, `models.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/test_agent_supervisor_invariants.py` (lines 319-330)
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/project-control/directives/D-010-autonomous-engineering-restructure/source-001.md` (§5.2 631-643, §5.4 661-680)
- `C:/MLFLL-path-normalized/project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md` (MINOR-1/MINOR-2 at 64-82)

## Regression/security/provenance findings (the seven dimensions)

**Dim 1 — Privilege boundary (PASS with SEC-1).** No escalation into a live side effect exists today: no live/CI/hook path imports `github_flow`/`shadow_effects_journal`/`SHADOW_EFFECT_SPECS`; the live `MODELED_EFFECTS` registry is unchanged; invariant 9 passes; suite green; R595 not lifted. **New attack surface — SEC-1 (MEDIUM):** the `extra_specs` param added to the live-path `ExternalEffectJournal` (external_effects.py:157,166) is consulted BEFORE the registry in `_spec_for` (168-172), so a future caller can (a) make an unmodeled merge/deploy/delete effect journalable-and-performable through the live effect layer, and (b) override a registry spec's `destructive` flag. Nothing prevents/flags a live-path `extra_specs`, and the invariant-9 test inspects only the module-level dict, not instance `extra_specs`. There is a test locking `MODELED_EFFECTS` against merge/deploy/destructive membership (good), but not against the `extra_specs` bypass.

**Dim 2 — Hard-deny bypass (PASS, fail-closed).** Force/`main`/`master`/`*/main`/remote-identity-mismatch/secret → HARD_DENY, re-used from `push_policy` (single authority; `authorize_push` only classifies). Whitespace-padded `"main "` → `.strip()` → deny (push_policy.py:154-159). Homoglyph/nested names produce a *distinct git ref* and never reach the real protected branch. Branch cleanup fails SAFE (RETAIN) for protected/retained/unknown/current-worktree/unmerged; only a regex-bounded (`^task/[A-Za-z0-9]...$`), proven-merged, non-current task branch is deletable; path-traversal-shaped names either fail the regex or trip the `endswith("/main")` guard → RETAIN (gf.py:534-585). MINOR-2's empty-`authorized_branch` fall-through is the one permissive edge and is correctly pinned.

**Dim 3 — Secret handling (PASS; SEC-3 LOW).** The secret-finding block is fed by caller-supplied `secret_scan_findings` (in tests, descriptors like `"aws_key in services/api/app.py"`, not raw secrets). Crucially, github_flow never journals/audits finding text: an ineligible `merge()` returns only refusal CODES (gf.py:730-732), and the effect journal is only reached on an eligible merge, which requires `secret_scan_clean` to be empty — so no audit/effect row can contain a finding (verified by `test_an_ineligible_merge_leaves_no_external_effect`: `pending_effects()==[]`). Residual (SEC-3): condition `detail` strings embed the finding/blocking lists verbatim (gf.py:420,444); a live caller that logs `MergeEvaluation.conditions` could leak if a scanner passes raw secret material.

**Dim 4 — Injection (PASS).** No `subprocess`/`os.system`/`Popen`/`eval`/`exec`/`shell=` anywhere in github_flow.py (grep clean); all side effects cross the injected `GitHubRunner` Protocol; no command is built from branch/title/task-id. Journal keys via `stable_action_id` are `"eff_"` + 32-hex SHA-256 over a canonical-JSON dict — untrusted strings feed the *digest input* only; output is fixed-shape hex (no path traversal, no key injection), and canonical-JSON structuring prevents cross-field delimiter collision.

**Dim 5 — Audit integrity (PASS).** `record_before_effect` is INSERT-once (duplicate action_id → `duplicate_action_id`, never reused; durable_state.py:484-498). `record_after_effect` is an UPDATE guarded on `status=PENDING` (rowcount≠1 → ROLLBACK + `no_pending_effect`; 515-527): a crash-replay can neither erase nor rewrite a row and can only transition PENDING→CONFIRMED/FAILED once. PENDING survives close/reopen and is reconciled, never blindly re-fired (crash tests reproduced). INFO: pre-journal refusals are not audited by this module — the live caller must audit every `FlowResult`.

**Dim 6 — Supply chain / stdlib-only (PASS).** github_flow imports `dataclasses`, `re`, `typing` + supervisor-internal; the external_effects change adds no imports; no dependency manifest/lockfile touched (grep + task forbidden_paths honored).

**Dim 7 — Section 5.2 rubric, security leg (PASS).** As a supervisor-code change, this is **security-acceptable for a shadow-only acceptance**: the live registry/authority is unchanged, no live wiring exists, the crash/replay safety (no-blind-retry, transactional journal, no erase/rewrite) holds from the security view, and every fail-open item lives in a decision layer proven only in shadow and gated behind R595. Control-plane and crash/replay legs are separate reviewers.

## Defects (findings)

- **SEC-1 (MEDIUM, non-blocking, NEW activation item).** `external_effects.py:157,166,168-172,318` — `extra_specs` is an un-guarded per-instance override channel on a live-path module; consulted before `MODELED_EFFECTS`; not covered by the invariant-9 lock. *Future attack scenario:* post-activation, a live journal built with `extra_specs` (convenience reuse of `shadow_effects_journal`, or copy-paste) makes a `github_pr_merge`/delete/deploy effect performable through the live layer without appearing in the registry the invariant test guards — silently expanding the automatic-effect surface past D-007 invariant 9. *Remediation (pre-activation):* (i) reject `extra_specs` keys colliding with `MODELED_EFFECTS`; (ii) reject any destructive `extra_spec`; (iii) test that the live journal path constructs with empty `extra_specs`; (iv) extend the invariant-9 lock to instance `extra_specs`.

- **SEC-2 (MEDIUM, non-blocking, AUGMENTS pinned MINOR-1).** `github_flow.py:106-110, 128-144` — the Tier-B fail-open is broader than MINOR-1 records. Beyond the 8 undetectable semantic classes + `deploy_definition`, `policy.file_class` also returns the *detectable* security-relevant classes `permission_settings` (settings/rules/agents/skills config), `hook` (repo hook dirs), `secret_bearing`, `launcher_script`, `submodule_config`, `attributes_filter` — and `route_for_review` maps NONE of them, so each routes Tier A (auto-merge, no review). D-010 §5.4 item 3 makes weakening "review requirements or the hard-deny policy" a Tier-D owner-stop, yet a permission/rules/hook change within task scope would, live, auto-merge with no review. *Mitigations today:* shadow-only; `cond_changed_paths_fit_task` requires the path be in task scope; `.github/**` IS covered (file_class `workflow`). *Remediation:* broaden the activation-checklist MINOR-1 fix from "8 classes + deploy_definition" to a CATCH-ALL — any `file_class ∈ SECURITY_RELEVANT_CLASSES` not explicitly routed (and specifically permission/hook configuration per §5.4 item 3) must fail TOWARD security/control-plane review or Tier-D owner-stop; add tests for permission-settings, key files, launcher scripts, submodule/attributes configs, bare `deploy_definition`.

- **SEC-3 (LOW, non-blocking).** `github_flow.py:420,444,383` — condition `detail` strings embed finding/path lists verbatim. github_flow never journals them, but a live caller logging `MergeEvaluation.conditions` could leak raw secret material if a scanner supplies it. *Remediation:* require redacted descriptors in `MergeRequest.secret_scan_findings`; route caller-side condition logging through `redaction.py`.

- **INFO-1.** Refusals (`merge_ineligible`, push/PR/cleanup denials) are returned as `FlowResult` but not audited by this module; the live caller must audit every `FlowResult` including refusals.

- **INFO-2 (pre-existing, not introduced here).** `MODELED_EFFECTS` is locked against merge/deploy/destructive membership but not to an exact set; `stable_action_id` truncates SHA-256 to 128 bits. Both adequate for their purpose; no action.

## Disposition of pinned G3 MINOR-1 / MINOR-2 (security-sufficiency)
For a **shadow-only acceptance both pinned dispositions are SECURITY-SUFFICIENT**: each is a fail-open (permissive) *decision* defect that cannot produce a live side effect because (a) no live path imports the module, (b) R595 activation is not lifted, and (c) both are recorded on `M0-T036-ACTIVATION-CHECKLIST.md` as pre-activation MUST-RESOLVE. **However, MINOR-1's pinned description is INCOMPLETE** — see SEC-2; the checklist entry must be broadened before it is treated as the remediation spec. MINOR-2's disposition is complete and correct (remediation = assert non-empty `authorized_branch`; main/master/force stay hard-denied regardless).

## Required rework
None for shadow-only acceptance. NEW pre-activation (R595-gated) items to record on `M0-T036-ACTIVATION-CHECKLIST.md`:
1. **SEC-1** — guard/forbid live-path `extra_specs` (collision-reject, destructive-reject, live-empty test, extend invariant-9 lock).
2. **SEC-2** — broaden the MINOR-1 fix to a catch-all over `SECURITY_RELEVANT_CLASSES` + explicit permission/hook-configuration §5.4-item-3 handling, with tests.
3. **SEC-3** — redaction discipline for secret-scan findings and any caller-side logging of merge conditions.
4. **INFO-1** — live caller must audit every `FlowResult` (including refusals).

## Verification limitation (not a defect)
Per the read-only guard I did not run git; the "later commits are control-plane only" claim rests on the independent G4 attestation plus my direct review of the current worktree content of the three files. The orchestrator confirmed `git diff af46b3e..HEAD` touches only `project-control/**` (zero non-control-plane paths) before recording this gate.

## Reviewer conclusion
**PASS (shadow-only).** The change is security-acceptable under the §5.2 supervisor-code rubric's security leg: no live wiring, live registry/authority unchanged, invariant 9 intact, full suite reproduced (1271 passed / 2 skipped), no injection/subprocess surface, fail-closed hard-denies and branch-cleanup, and crash/replay journal integrity that cannot erase or rewrite a row. No BLOCKING or HIGH findings. Two MEDIUM findings (SEC-1 `extra_specs` live-path guard; SEC-2 broadened Tier-B fail-open including permission/hook configuration) and one LOW (SEC-3) are latent, unreachable in the shadow posture, and are routed to the R595 activation checklist — SEC-2 specifically corrects an incompleteness in the already-pinned MINOR-1.

**VERDICT: PASS** — with the four activation-checklist additions above (SEC-1, SEC-2, SEC-3, INFO-1).
