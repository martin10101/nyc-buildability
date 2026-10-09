# M0-T138 Directive-Compliance Verification (D-024 Amendment 41, R607–R621)

Independent DCV return saved verbatim by the orchestrator (transport entity-decoding only),
followed by a clearly-labeled orchestrating-verifier addendum with this session's own
adversarial reproductions that the DCV rows reconcile against.

---

# DCV Report — M0-T138 under D-024 Amendment 41 (R607–R621)

**Verifier:** directive-compliance-verifier (independent; ≠ producer `controller-update-source-binding-producer`). **Mode:** read-only.

## Identity (verified first — all match)
HEAD `99cd3dad52088bfb92c5c3ec9cc04c392f0d024e`, branch `candidate/D-024-mrl-option-b`, clean tree. No upstream (`@{u}` fails); no `origin/*candidate*` branch → nothing pushed. Frozen `1489879e…` is a `commit`, tree `0babc469…`, `tools/agent_supervisor` subtree `79af11a2…` (all match binding contract exactly). Commit graph `e60192ed..HEAD` = exactly 4 linear commits (capture `ec4ac9a3` → impl `435531de` → evidence `8e2cb909` → submit `99cd3dad`), no merge. Zero changes under `tools/agent_supervisor/**`, zero `.github/**`, zero M0-T136 files. requirements.json: R603/R604/R605 byte-identical base↔HEAD; only R607–R621 added (count 606→621), no pre-existing requirement removed. `validate_directive_compliance.py --check` rc=0; manifest audit_log entry "Amendment 41 captured verbatim", 41 source_files. No drift in `tools/controller_update/**` or the runbook between gate-capture `435531de` and HEAD.

## Per-requirement verdicts

| ID | Verdict | Primary evidence I reproduced |
|---|---|---|
| R607 | PASS | `docs/CONTROLLER_UPDATE_RUNBOOK.md` §4 presents ONE checked-in command (line 83), no hand substitution; command-document tooth over the runbook = `m0t138-doc-check-default.json` rc=0 (repo_head 435531de). Manual shortcut eliminated. |
| R608 | PASS | `tools/controller_update/source_binding.json` L6 `commit_sha=1489879e…40hex`; installer L155-158 refuses any non-40-hex (`not_a_full_sha`); test `test_source_binding.ps1` L61-64 `origin/main`→REFUSED not_a_full_sha, nothing installed. |
| R609 | PASS (with note) | `update_controller_from_candidate.ps1` `Assert-SourceIdentity` L168-228 (toplevel, normalized origin, commit exists/type, commit tree vs `0babc469…`, subtree vs `79af11a2…`, required modules) + `Assert-SourceWorktreeState` L230-254. Fixture-covered: tree_mismatch (L67-70), subtree_mismatch (L73-75), missing_module (L78-80). NOTE: the three worktree-state codes `source_not_detached`/`source_wrong_commit`/`source_unclean` are present in the script but NOT triggered by any checked-in fixture (suite exercises `source_worktree_exists`; install creates a fresh detached worktree); they were proven empirically by the orchestrating verifier's scratch reproductions. Evidence-map R609 wording overstates fixture coverage — behavior itself is correct. I independently confirmed all frozen-commit modules exist (`git cat-file -e 1489879e:…mrl_launch_draft.py` etc. all OK) and are absent on stale `origin/main` (rc 128). |
| R610 | PASS | `Compare-InstalledTree` L256-290 = complete bidirectional per-file raw SHA-256; test P1 (evidence.installed_file_count≥9), `content_mismatch` rejection (L120-122), mutant `m_content` killed. |
| R611 | PASS | install writes `controller_update_evidence.json` binding commit/tree/subtree + `installed_files_sha256` (L314-333); test P1 asserts evidence binds SHA+tree; verify-manifest binds `manifest_binding.verdict` (L399-406); mutant `m_manifest` killed. Fail-closed adversarial binding demonstrated. |
| R612 | PASS | Operator script checked in; `test_runbook_parse.ps1` parse-tests the script + every fenced block on PS 5.1 (zero errors, rejects `&&`), asserts §4 pins the concrete 40-hex SHA with no `<placeholder>`; `m0t138-doc-check-default.json` (the tooth, DEFAULT_DOCS=runbook) rc=0. |
| R613 | PASS | Six rejection classes all fixture-covered: not_a_full_sha (origin/main), tree_mismatch (self-consistent wrong commit), missing_module, subtree_mismatch (tree/SHA mismatch), content_mismatch (dest changed), manifest_digest_mismatch+manifest_key_set_mismatch (manifest from wrong tree). `test_mutants_detected.ps1` kills 4 mutants (tree, module, manifest, content); generator fails closed if a pattern ≠1 match. Recorded rc=0 at `m0t138-ps-tests-controller-update.json`. |
| R614 | PASS | `git show HEAD:…RUNBOOK.md \| grep origin/main` → none. §5a verify-manifest added; canary/MRL prerequisites reference §§3-8 (unchanged, now correct); `SESSION_HANDOFF.md` seq-73 states one owner command chain. |
| R615 | PASS | One task `M0-T138.json` (status awaiting_gate); amendment header + R615 text declare BLOCKING, one bounded follow-up, not Tranche C; no Tranche-C work in diff. |
| R616 | PASS | No push (no upstream/no remote candidate branch); no `.github/**` change; linear graph, no merge; zero `tools/agent_supervisor/**` change; R603-R605 byte-identical; M0-T136 canary package not in diff. Controller-side prohibitions (`C:\SupervisorController` untouched, `controller_update_evidence.json` absent) lie outside my read-only guard's permitted scope — verified indirectly (no push, no source-worktree-creation path exercised in-repo) and reconciled with the orchestrating verifier's reproduction. |
| R617 | PASS | Zero edits under `tools/agent_supervisor/**` (diff scope); repair = doc + checked-in validator + tests; `m0t138-modularity.json` rc=0, no modularity limit/config file in diff (only the gate report). Smallest-honest-repair path taken. |
| R618 | PASS | G0-readiness "consolidated trace" + producer report §3 document the pre-edit one-pass trace; 10 raw gate records carry raw returncodes; runbook edited (63/401 lines) not rewritten; "Failure inventory EMPTY"; `ruff` rc=1 with stdout_sha256 `74680cc7…` BYTE-IDENTICAL to accepted `M0-T136-gates/final-freeze-ruff.json` (ruff lints only .py; new files .ps1/.json → zero new findings). |
| R619 | PASS | Canonical mechanics: one task, one impl/evidence commit sequence; only G0 (administrative, reviewed_sha e60192ed) and G2 (role=self_check, PASS) recorded — NO G3/G4/accept; task status `awaiting_gate`. No self-acceptance. |
| R620 | PASS (with note) | Producer report carries all return items: changed files (§5), source-binding design (§4), positive+mutant results (§7), candidate SHA `1489879e` (§1), final status (submitted). Terminal token `CONTROLLER_UPDATE_SOURCE_BINDING_SUBMITTED` recorded in `M0-T138-evidence-map.json` L46 as delivered via "producer report + session return message". NOTE: the literal token string appears in-repo only in the evidence-map; the return-channel message is ephemeral and not a reproducible repo artifact. |
| R621 | PASS | `M0-T138-G0-readiness.md` table verifies all seven Bootstrap Gate-0 values (root, branch, HEAD e60192ed, frozen 1489879e + tree + subtree, clean tree, M0-T136 accepted, /mcp empty) re-measured live; `M0-T138-G0.json` PASS. |

## Overall verdict: **PASS** (all 15 of R607–R621 SATISFIED)

## Discrepancies found (all non-material; none blocks completion)
1. **requirements.json em-dash re-serialization.** The capture commit re-serialized 26 em-dashes in *pre-existing* rows from raw UTF-8 bytes (`E2 80 94`) to ASCII-escaped `\u2014`. Under strict UTF-8 decode, changed pre-existing requirement set = **[]** (json.loads yields identical strings); R603-R605 semantically identical; `validate_directive_compliance.py --check` rc=0. The append is semantically R607–R621 only; the byte-level em-dash normalization touched pre-existing lines but changed no requirement meaning.
2. **R609 evidence-map overstatement** (stated above): three worktree-state refusal codes are correct in the script but not fixture-tested in the checked-in suite; proven only by independent verifier reproduction. Does not affect the PASS.
3. **R620** (stated above): terminal-token literal exists in-repo solely in the evidence-map; the producer's return message is not a reproducible repo object.

No VIOLATED or UNVERIFIABLE requirement. Recording of this result (including `verification.json`) is the orchestrator's action; I performed no writes.

---

## Orchestrating-verifier addendum (independent reproductions this DCV reconciles against)

Recorded by the orchestrating independent-verifier session (≠ producer), 2026-09-02, at HEAD
`99cd3dad` (implementation trees byte-identical to candidate `435531de`). Every command below was
executed by this session with raw exit codes; scratch mutations were confined to the session
scratchpad (`%TEMP%\claude\…\scratchpad\vwork`), never the repo, the live controller, or
`%LOCALAPPDATA%`.

1. **Suite reproduction at HEAD:** `tools/controller_update/ps_tests/run_ps_tests.ps1` raw 0
   (all assertions PASS); `tools/agent_supervisor/ps_tests/run_ps_tests.ps1` raw 0; doc-check
   default/MRL/canary rc 0/0/0 (11/6/3 commands); pytest command_docs+manifest 77 passed rc 0;
   modularity rc 0; validate_directive_compliance rc 0; context budget rc 0; `python -m ruff
   check .` rc 1 with stdout_sha256 `74680cc7ae31e75d9775f38dbe23a2834ac6905f34c0725a415255735f54cd63`
   — byte-identical to BOTH the frozen `M0-T136-gates/final-freeze-ruff.json` and
   `m0t138-ruff-root.json` (21138 bytes, 52 pre-existing findings, zero new).
2. **Beyond-suite rejections (scratch fixture repo, real script, fresh powershell.exe):**
   abbreviated 12-hex SHA → `not_a_full_sha`; branch name (`master`) → `not_a_full_sha`;
   literal `HEAD` → `not_a_full_sha`; branch-attached source worktree → `source_not_detached`;
   worktree detached at wrong commit → `source_wrong_commit`; dirty worktree →
   `source_unclean`; deleted destination file → `content_mismatch` (missing); planted
   destination file → `content_mismatch` (unexpected); swapped contents of two destination
   files → `content_mismatch`; genuinely LF-flipped destination file (raw bytes changed,
   LF-normalized digest identical) → `content_mismatch` — proving the narrow CRLF→LF
   normalization (manifest cross-check only, mirroring `manifest.py::_hash_file`) cannot hide
   a raw content change.
3. **Uppercase-SHA characterization:** an UPPERCASE spelling of the pinned full SHA passes the
   case-insensitive PowerShell regex and git resolves it to the SAME immutable commit; the
   accepted tree/subtree/module checks still bind, and install proceeds from the identical
   object. Not a mutable-ref hole (observation only; the checked-in binding is lowercase and
   changes only through a reviewed commit).
4. **Mirror confinement:** every filesystem-mutating operation in the script and suite is
   parameterized by the test-written binding (destinations, worktrees, manifests, evidence all
   under `%TEMP%` GUID dirs); the checked-in `source_binding.json` was never used for any
   install during verification. A deliberate scratch-only probe confirmed robocopy `/MIR`
   follows a junction destination — in production reachable only by machine-level substitution
   of the reviewed destination path, the same disclosed residual trust boundary as a recomputed
   binding contract (runbook §4 printed-identity comparison + reviewed-commit-only contract);
   runbook §3's unique timestamped non-destructive backup precedes §4 and §10 restores it.
5. **Live surfaces:** `C:\SupervisorController\tools\agent_supervisor` newest write 2026-08-18
   (plus pre-existing owner `model_selection.toml` 2026-09-01 00:22 at the controller root,
   outside the mirrored subtree); `controller_update_evidence.json` ABSENT;
   `wt-controller-src` ABSENT and not in `git worktree list`; no provider invoked; nothing
   pushed (no upstream configured).
6. **Registry append-only:** independent decode of `requirements.json` at `e60192ed` vs HEAD:
   pre-existing rows semantically changed = [], removed = [], added = exactly R607–R621 —
   confirming the DCV's em-dash finding as byte-level serialization only.
7. **Material identity:** `_task_git_identity` at HEAD = `dd8cf45d149735956414f5c6088836410e5b242adc227507975f868d52ae83ee`,
   equal to the submit record; resolved reviewed commit `99cd3dad…`.

Verdict recorded on the strength of the DCV rows, the G3/G4 independent PASS verdicts, and the
reproductions above: **all 15 applicable requirements R607–R621 PASS at the reviewed identity.**
