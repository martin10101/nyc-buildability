# M0-T051 — Directive-compliance verification (FINAL) — VERBATIM verifier return

Orchestrator preservation note: saved verbatim from the directive-compliance-verifier
agent-return channel (transport entity-decoding only: `&amp;`→`&`). Frozen head
`ebd75def98a1afe75879485cb7ba85f278ebd187`. Recorded by the orchestrator 2026-08-08.

---

I have independently confirmed the honest boundary from the source itself: `evaluate_acl_entries` (line 220, "the unit-test surface") is the pure ACE-level verdict, while `evaluate_file` (line 381) additionally requires the write-open probe and `_confirm_owner_elevated` (owner=Administrators via elevated `takeown /A`). The tests call `evaluate_acl_entries` only, so they genuinely prove the DACL/ACE property and do not overclaim. I now have everything needed.

---

# DIRECTIVE-COMPLIANCE VERIFICATION REPORT — M0-T051 (D-010 source-021, R196–R207)

**Verifier:** directive-compliance-verifier (independent; producer = backend-engineer) · read-only
**Frozen head:** `ebd75def98a1afe75879485cb7ba85f278ebd187` (branch `control/M0-T051-explicit-ace-strip`)
**Content identity (allowed_paths, git-canonical):** `835f996e4cb826c81ec5f02eb40a696f1aaa411109a6fa036d3f943ebbb7a81f`
**VERDICT: PASS** (all 12 applicable requirements SATISFIED at the frozen identity; no VIOLATED/UNVERIFIABLE)

---

## 1. Intake review (source-021 → matrix)

**Digest integrity.** `sha256(source-021-amendment.md)` I computed = `6792de3564a9a6131f41bb26a124d65f07b620dcd7710c3efb740363b67c5824` = the manifest `sources[]` entry exactly (`amends: source-020-amendment.md`, sequence 21). `validate_directive_compliance.py --check` exits 0 (clean). All 207 requirement ids locked; R196–R207 present in `locked_requirement_ids`. Manifest `audit_log` records the source-021 capture ("R196-R207 added, bound to M0-T037/M0-T051; digests restamped").

**Resolver / applicable set.** `directive_registry.derive_applicable()` on `project-control/tasks/M0-T051.json`, across ALL active directives, returns **exactly {D-010-R196 … R207}**, `unresolved=[]`. Matches `directive_refs` in the task packet. R196 applicability confirms it also binds `M2-T015`/`M2-T016`/`M0-T037` on `dispatch`+`accept` (the dispatch hold).

**Forward trace (every source obligation → a row):** STOP/4×do-not/NOT_PROTECTED→R196; FIRST unelevated doctor as primary evidence→R197; contract ONE bounded fix→R198; required DACL property (full rights list + "not merely re-grant three")→R199; adversarial regression steps 1–5→R200; step6 read→R201; step7 byte-for-byte→R202; step8 parent→R203; step9 idempotent→R204; step10 RED-on-9625514e→R205; step11 G3/G5/DCV + return new blob before next apply→R206; "do not broaden"→R207. **No source item is missing.**

**Reverse trace (every row → a source anchor):** all 12 carry `source_ref: source-021-amendment.md#explicit-ace-survived` and each maps to a distinct owner sentence. **No invented requirement.**

- **Weakened:** none. R199 preserves the verbatim rights enumeration and the "must not merely replace grants for the three intended principals" clause; R205 preserves the exact barred blob hash; R196/R207 preserve every prohibition.
- **Combined:** R200 groups owner steps 1–5, but those are sub-steps of a single "adversarial regression → prove posture" obligation (all five enumerated verbatim inside R200.text); steps 6–11 are correctly split into R201–R206. This is a defensible atomic decomposition, **not** an improper merge of materially different obligations.
- **Amendment reflection:** source-021 is the sole amendment introducing this wave; fully reflected; digests restamped.

**Intake verdict: PASS.**

## 2. Identity integrity

| Check | Expected | Observed | OK |
|---|---|---|---|
| Frozen HEAD | ebd75de | ebd75de | ✓ |
| Script blob @ HEAD | b6ee6589… (candidate) | `git rev-parse HEAD:…ps1` = b6ee6589d93b4cd95283ce6d45c22f7010aba56a | ✓ |
| Script blob @ main | 9625514e… (barred) | `main:…ps1` = 9625514e79a34c901258975d4964529a9c02378e; main = 33b2e24 (= capture base) | ✓ |
| Content identity @ HEAD vs G3/G5 manifest | equal | 835f996e… == gate `content_manifest_sha256` (G2/G3/G5) | ✓ |
| Code drift since review | none | HEAD is 1 commit past G3/G5 reviewed_sha (5d9b260 → ebd75de); ebd75de touches only control-plane gate JSONs (excluded from manifest); allowed_paths clean, identity unchanged | ✓ |
| Fix delta | script + os_acl test + report | `git diff --stat 33b2e24..bbdfb76` = 3 files (ps1 +41, os_acl.py +313, producer-report +225); rollback region unchanged | ✓ |

Note for the orchestrator: the G3/G5 gate records carry `reviewed_sha=5d9b260`; HEAD is `ebd75de`. Content identity is byte-identical (`835f996e`), so this is bookkeeping only, but the accept-time DCV stamp should resolve to HEAD's identity `835f996e` (it does).

## 3. Per-requirement verdicts (primary evidence I reproduced myself)

| ID | Class | Verdict | Reproduced evidence |
|---|---|---|---|
| **R196** | hold | **SATISFIED** | Live `sha256(C:\Program Files\SupervisorConfig\config.toml)` = `29eb765e…da1cb` (unchanged, not moved). Live `icacls` still shows `NT AUTHORITY\Authenticated Users:(M)` present → **not repaired out-of-band**; fix goes only through the reviewed script. Supervisor SHADOW-ONLY (not activated). M2-T015/M2-T016/M0-T037 all `backlog`, `accepted_at:null` (not dispatched). Delta = 3 allowed files. |
| **R197** | obligation | **SATISFIED** | `reports/M0-T051-doctor-notprotected-evidence.json`: `controller_config_acl.protected=false`, file `NOT_PROTECTED`, reasons = "unelevated principal 'NT AUTHORITY\Authenticated Users' holds M on the file" + "an unelevated open-for-write SUCCEEDED"; ACE list matches the owner's reported post-apply ACL verbatim. I **re-ran** the exact unelevated doctor → `state=NOT_PROTECTED, protected=False, file.state=NOT_PROTECTED`, same reasons; parent PROTECTED. Live posture == committed evidence. |
| **R198** | obligation | **SATISFIED** | `git diff` of the .ps1: exactly one `Invoke-Step $Icacls @($file,"/reset")` and one `@($dir,"/reset")` inserted ahead of the existing `/inheritance:r`; remainder is root-cause/ordering comments. One extra flag per target; no new architecture. |
| **R199** | obligation | **SATISFIED** (DACL/ACE level; ownership sub-property → R206) | `test_adversarial_explicit_ace_is_stripped_file_and_parent` RAN and PASSED on this host: poison gone, DACL == exactly {Administrators, SYSTEM, user-RX}, `evaluate_acl_entries==PROTECTED` on FILE and PARENT. I confirmed `evaluate_acl_entries` (os_acl.py L220) is the pure ACE-level verdict; user holds only RX → no non-elevated write/modify/etc. remains. |
| **R200** | obligation | **SATISFIED** (pre-elevation scope fully executed) | `HardenExplicitAceStripTests` = **5/5 PASSED, 0 skipped** (I ran `pytest -v`). Real `icacls` on a disposable poisoned parent+file (`*S-1-5-11:(M)`); sequence AST-extracted from the actual blob via `Invoke-Expression` of the real `CommandElements`; takeown asserted PRESENT (2×, `/F`+`/A`); 6 icacls calls, `/reset` first per target; final posture Admin-F/SYSTEM-F/user-RX proven. Step-4 "evaluator==PROTECTED" proven at the ACE evaluator; full `evaluate_file` verdict correctly deferred to R206 (see boundary). |
| **R201** | obligation | **SATISFIED** | `test_new_sequence_preserves_unelevated_user_read` PASSED: exactly one user ACE holding `RX`; bytes still readable. |
| **R202** | obligation | **SATISFIED** | `test_new_sequence_preserves_file_contents_byte_for_byte` PASSED: sha256 identical before/after (icacls/takeown never write content). |
| **R203** | obligation | **SATISFIED** | Parent asserted to exactly the three intended ACEs + `evaluate_acl_entries==PROTECTED`; dir `/reset` is non-recursive (no `/T`) — verified in the .ps1 and adversarial/idempotence tests. |
| **R204** | obligation | **SATISFIED** | `test_new_sequence_is_idempotent` PASSED: file+dir DACL identical across two consecutive apply runs. |
| **R205** | obligation | **SATISFIED** | `test_red_on_current_cleared_blob_leaves_poison_effective` **RAN (not skipped) and PASSED**: reconstructs the barred sequence via `git show 33b2e24:…` (= blob 9625514e, no `/reset`, 4 icacls calls), runs it live → poison SURVIVES + `NOT_PROTECTED` (RED); then new sequence → poison GONE + PROTECTED (GREEN). Bidirectional differential on the SAME real evaluator proves the tests discriminate. Producer standalone RED transcript corroborates. |
| **R206** | return | **SATISFIED (conduct-to-date; remainder post-merge)** | G3 (code-reviewer) PASS, G5 (security-reviewer) PASS, both at frozen identity on the narrow delta; this DCV is the third. New blob `b6ee6589` identified and cleared by both reviewers. Per M0-T049-R181 / M0-T050-R193 precedent, the *return* (hand the owner the merged blob + dry-run-first command before the next elevated apply) completes at/after merge — see §6. |
| **R207** | prohibition | **SATISFIED** | Delta = apply-path `/reset` insertions + comments, os_acl test updates/additions, producer report. No ACL-parsing/enumeration, no supervisor redesign, `-Rollback` block unchanged (diff grep `Rollback|/inheritance:e` = 0 hits). Supervisor-freeze rule §2 qualifying evidence (reproduced defect) cited in packet + commit. |

**Test/harness reproduction (mine, this host):**
- `tools/test_agent_supervisor_os_acl.py` → **43 passed, 0 skipped**; the 5 `HardenExplicitAceStripTests` all RAN.
- `tools/test_agent_supervisor_*.py` → **1392 passed, 2 skipped** (0 failures; ≥1165 freeze baseline satisfied; the 2 skips are outside os_acl).
- Full repo `pytest -q` → **2766 passed, 2 skipped**.
- `tools/test_directive_compliance.py` → 102 OK; `tools/test_project_control.py` → all 22 groups OK; `tools/test_directive_reminder.py` → 12 OK; `validate_directive_compliance.py --check` → exit 0.

## 4. Honest proof boundary (verified, not overclaimed)

Confirmed on my own source inspection: the fixture tests assert `evaluate_acl_entries` (ACE/DACL-level — exactly the sub-property the defect violated) and never call `evaluate_file`/`evaluate_controller_config_acl`, which additionally require `probe_write_open==denied` and `_confirm_owner_elevated` (owner→Administrators via elevated `takeown /A`). Unelevated, the user-owned fixture stays user-writable, so a full `evaluate_file` verdict correctly still reads NOT_PROTECTED even with a clean 3-ACE DACL. The ownership/denied-write end-to-end confirmation is legitimately owner-elevated-only and is the express content of R206. **No sub-property is claimed proven that was not.**

## 5. Reviewer independence & sufficiency

Producer = backend-engineer; G3 = code-reviewer; G5 = security-reviewer; DCV = me — four distinct roles (producer ≠ verifier). Both reviews are genuinely **behavioral**: each independently re-ran the os_acl suite (43), the adversarial class (5/5), the RED test live, and the full supervisor suite (1392/2). Both honestly disclosed that the read-only guard blocked their standalone icacls mutations and that they **declined to obfuscate** past it, verifying through the pytest channel instead. I judge that path **sufficient** and independently corroborated it: the pytest tests extract the actual script's argv via the WinPS AST + `Invoke-Expression` (A2/B1 pin the 8 call-sites so the replay cannot drift), drive **real icacls** on real poisoned fixtures, and assert against the **real production evaluator** — and I re-ran all of it myself with identical results, so my verdict rests on reproduced primary evidence, not their attestations.

## 6. Prohibited-action evidence (all clean)

Nothing merged (HEAD **NOT** an ancestor of `main`; main = 33b2e24 unchanged) · nothing accepted (M0-T051 `awaiting_gate`; M0-T037/M2-T015/M2-T016 `backlog`) · nothing dispatched (M2-T015/T016 untouched) · nothing deployed/activated (supervisor SHADOW-ONLY) · config not moved/modified/repaired (SHA `29eb765e…`, poison still present, live doctor NOT_PROTECTED) · no install/purchase/close. Verification.json does not yet contain M0-T051 (correct — orchestrator writes it after validating this report).

## 7. Advisories weighed — none blocks PASS

- **G5 Low-1 (file-before-parent transient, general permissive-parent case):** a sub-second window *during* apply, not an end-state; not the live target (parent already PROTECTED); backstopped by `$ErrorActionPreference=Stop` abort + mandatory post-apply doctor. Does not violate R199's end-state wording. Forward-looking, out of R207 scope.
- **G5 Low-2 (`-DryRun` requires elevation):** pre-existing, unchanged by this delta.
- **Info (RED test git-reachability skip; `-UnelevatedUser` default):** the RED test RAN here (not skipped); CI-history-retention hygiene note only.
- **G3 advisory (unelevated-harness scope):** identical to the honest boundary, carried by R206.

## 8. Discrepancies

None material. The only nuances — (a) gate `reviewed_sha` (5d9b260) trails HEAD (ebd75de) while content identity is byte-identical (835f996e), and (b) R199/R200 prove the ACE/DACL property with the ownership/denied-write end-to-end confirmation deferred to R206 — are both expected, documented, and consistent with the directive's own design and the M0-T049/T050 precedent.

## 9. Recommendation

**PASS.** All 12 applicable requirements (D-010-R196…R207) are independently SATISFIED at frozen head `ebd75de` / content identity `835f996e`. The fix is the smallest correct change inside the existing icacls path; the property holds by construction and is proven by executed, non-vacuous, real-icacls tests with a live RED/GREEN differential against the barred blob; boundaries are honest; prohibitions and holds are intact.

**Remaining post-merge (R206, orchestrator/owner-lane, does not block this verdict):** after Tier-A merge, the orchestrator confirms the merged-on-main script blob is `b6ee6589d93b4cd95283ce6d45c22f7010aba56a`, returns the dry-run-first apply command to the owner, and the owner runs the elevated apply then the **unelevated doctor must show PROTECTED on BOTH file and parent — or STOP** (with the R196 dispatch hold on M2-T015/T016 still active until the owner lifts it).

**Key evidence files (absolute):**
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1` (blob b6ee6589; `/reset` inserts at the two apply blocks)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_agent_supervisor_os_acl.py` (`HardenExplicitAceStripTests`, APPLY_VECTORS 6→8, A2/B1)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\os_acl.py` (`evaluate_acl_entries` L220 vs `evaluate_file` L381)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T051-doctor-notprotected-evidence.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T051-g3-code-review.md` · `…-g5-security.md` · `…-producer-report.md` · `…-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\source-021-amendment.md` · `manifest.json` · `requirements.json` · `verification.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T051.json`
