# M0-T138 producer report — controller-update source binding (D-024 Amendment 41)

Producer: `controller-update-source-binding-producer` (primary session; sole integrator).
Submission only — NO self-acceptance (R619); G3/G4/DCV review and gate/accept decisions belong to
the independent reviewers and the orchestrator.

## 1. Identity

- Root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`
  (LOCAL ONLY; nothing pushed; PR #241 untouched; remote base 6f5d12a6 untouched).
- Bootstrap Gate 0 verified at start (all seven owner-stated values matched;
  `M0-T138-G0-readiness.md`).
- **Frozen production candidate (the immutable install source): `1489879e1f6787a9d53ed74db4524b24039e03a2`**
  — commit tree `0babc469a07fc9109e5f7ce18ea73bf932952801`, `tools/agent_supervisor` subtree
  `79af11a2c7fa33c8f5c1bf85c17e310736bf30a3`. M0-T136 accepted at e60192ed.
- Commit sequence (one local implementation/evidence sequence, R619):
  `ec4ac9a3` capture (Amendment 41 + R607–R621 + task contract + G0) →
  `435531de` implementation → evidence commit(s) following this report. Every gate record below
  was recorded at repo_head `435531de` by the raw recorder `tools/gate_runner.py` (R590).

## 2. Root cause closed

- `docs/CONTROLLER_UPDATE_RUNBOOK.md` §4 resolved the copy source as
  `git rev-parse origin/main` — mutable and stale: local `origin/main` (d8b3899f) predates
  Tranche B and `git cat-file -e origin/main:tools/agent_supervisor/mrl_launch_draft.py` fails
  (rc 128).
- `record-manifest` (`cli.py::cmd_record_manifest` → `generate_manifest(PACKAGE_ROOT, …)`) hashes
  whatever is installed; nothing anywhere bound a source commit/tree, so a self-consistent but
  wrong installation would certify (`manifest.py::manifest_is_stale` explicitly documents
  self-consistency ≠ authenticity).
- A manually reconstructed command would bypass the checked-in command-document contract
  (`tools/supervisor_command_doc_check.py`, DEFAULT_DOCS = the runbook). Owner decision: REJECTED
  (R607).

## 3. Consolidated trace (performed before any edit, R618)

Traced in one pass: runbook §§1–13; MRL_LAUNCH_RUNBOOK prerequisites; canary-package
prerequisites 1–4; `manifest.py` generate/verify/staleness; `cli.py` record-manifest /
verify-controller (PACKAGE_ROOT-rooted, no source input); `command_docs.py` extraction rules
(fenced blocks + `!` lines; invocation markers include `agent_supervisor/mrl_launch_draft.py`,
so module paths must stay OUT of fenced runbook blocks — hence the checked-in script
indirection); `supervisor_command_doc_check.py` DEFAULT_DOCS; accepted
`tools/agent_supervisor/ps_tests/` house style; every repo consumer of
`CONTROLLER_UPDATE_RUNBOOK` (`grep -rln`) — living docs vs historical reports; Amendment 40 rows
R516/R518/R520–R523/R585–R598 and owner-only R603–R605 (untouched, uninterpreted). The active
controller-update path contained exactly one `origin/main` instruction (runbook §4); the
`M0-T136-failure-surface.md` F22 mention is a historical record and stands.

## 4. Source-binding design (smallest honest repair, R617)

No production supervisor code changed — zero edits under `tools/agent_supervisor/**`. The repair
is documentation + a checked-in operator validator + tests:

1. **Binding contract** `tools/controller_update/source_binding.json` pins: source repo,
   normalized origin URL, the immutable commit SHA `1489879e…`, its accepted commit tree,
   the `tools/agent_supervisor` subtree tree, the required Tranche-B modules (incl.
   `mrl_launch_draft.py`), source-worktree/destination/manifest/evidence paths. It changes only
   through a reviewed commit.
2. **Operator script** `tools/controller_update/update_controller_from_candidate.ps1`
   (PowerShell 5.1, raw-exit-code discipline, typed `REFUSED reason_code` + exit 1, fail closed):
   - `-Phase install` (runbook §4, ONE command): refuses any non-40-hex source
     (`not_a_full_sha` — origin/main can never be a source); verifies repo toplevel identity,
     normalized origin, commit existence/type, commit tree vs accepted evidence
     (`tree_mismatch` — an internally self-consistent wrong commit refuses here), subtree tree
     (`subtree_mismatch`), required modules (`missing_module`); creates a FRESH detached source
     worktree at exactly the pinned commit (refusing `source_worktree_exists`,
     `source_not_detached`, `source_wrong_commit`, `source_unclean`); mirrors the subtree
     (`robocopy /MIR`, caches excluded); proves the installation by a complete bidirectional
     per-file raw SHA-256 comparison (`content_mismatch`); writes
     `controller_update_evidence.json` binding source commit/tree/subtree + per-file digests
     (R611 first arm: the UPDATE EVIDENCE binds provenance).
   - `-Phase verify-manifest` (new runbook §5a, after §5 record-manifest): re-verifies source
     identity and worktree state, re-compares destination vs accepted source (catches a
     destination changed after copying), cross-checks the recorded manifest's key set and
     LF-normalized digests against the ACCEPTED SOURCE tree (`manifest_key_set_mismatch` /
     `manifest_digest_mismatch` — a manifest recorded from a wrong installed tree refuses), and
     binds the verdict into the update evidence.
3. **Runbook** §4 replaced (immutable source binding, one concrete owner command + one
   `source_worktree_exists` recovery command, printed-identity comparison instruction); §5a
   added; §1 table row and §10 rollback line extended. No `origin/main` remains in the runbook.
4. **Tests** `tools/controller_update/ps_tests/` (runner mirrors the accepted fail-fast/fail-closed
   discipline; every case runs the REAL script in a fresh `powershell.exe -File` process against a
   real fixture git repository; the fixture manifest is crafted by an INDEPENDENT python
   hashlib/fnmatch implementation, so the script's manifest projection is cross-checked against a
   second implementation).
5. **Canary prerequisite / handoff (R614):** the accepted `M0-T136-canary-package.md` prerequisite
   already demands "Controller update deployed from the frozen Tranche-B candidate SHA per
   CONTROLLER_UPDATE_RUNBOOK.md sections 3-8" — repairing §4 makes the referenced procedure do
   exactly that, so the accepted evidence needed (and received) NO edit. `MRL_LAUNCH_RUNBOOK.md`
   prerequisites ("sections 3-8") likewise remain correct unmodified. `docs/SESSION_HANDOFF.md`
   seq-73 states the one consistent owner command chain (review → §§3–8 with the one §4 install
   command → §5/§5a → §6–8 → untouched canary package).

## 5. Changed files (complete)

Capture `ec4ac9a3`: `project-control/directives/D-024-fable-codex-loop/`
`source-041-amendment.md` (new) + `manifest.json` + `requirements.json` (R607–R621) +
`verification.json` (pending skeleton row); `project-control/tasks/M0-T138.json` (new);
`project-control/gates/M0-T138-G0.json` (new); `project-control/reports/M0-T138-G0-readiness.md`
(new); `project-control/state.json`.
Implementation `435531de`: `docs/CONTROLLER_UPDATE_RUNBOOK.md` (§1 row, §4 replaced, §5a added,
§10 line); `docs/SESSION_HANDOFF.md` (seq-73); `tools/controller_update/source_binding.json`,
`update_controller_from_candidate.ps1`, `ps_tests/{run_ps_tests,fixtures,test_source_binding,`
`test_mutants_detected,test_runbook_parse}.ps1` (all new).
Evidence commit: `project-control/reports/M0-T138-gates/*.json` (10 raw records),
`M0-T138-producer-report.md`, `M0-T138-G2-self-check.md`, `M0-T138-evidence-map.json`,
`project-control/gates/M0-T138-G2.json`.

## 6. Verification results (raw exit codes; records in `M0-T138-gates/`)

| Record | Command | Raw rc |
|---|---|---|
| m0t138-ps-tests-controller-update | new ps suite (positive + 6 rejection classes + 4 mutants + parse tooth) | 0 |
| m0t138-doc-check-default | `supervisor_command_doc_check.py` (repaired runbook; 11 presented commands) | 0 |
| m0t138-doc-check-mrl / -canary | tooth over MRL runbook / canary package | 0 / 0 |
| m0t138-supervisor-ps-tests | accepted `tools/agent_supervisor/ps_tests` suite | 0 |
| m0t138-pytest-command-docs-manifest | 77 tests: living-runbook command_docs + manifest binding | 0 |
| m0t138-modularity | `modularity_check.py --check` (no limit raised, no exception added) | 0 |
| m0t138-directive-registry | `validate_directive_compliance.py --check` | 0 |
| m0t138-context-budget | handoff/context budget | 0 |
| m0t138-ruff-root | `python -m ruff check .` | 1 (pre-existing F28: stdout_sha256 `74680cc7…` BYTE-IDENTICAL to the frozen `final-freeze-ruff.json`; zero new findings; no `.py` changed) |

Failure inventory gathered before any correction (R618): EMPTY — every suite passed on the first
complete run; the only nonzero code is the pre-existing, digest-identical ruff surface.

## 7. Positive and mutation results (R589/R613)

Positive: fixture install exit 0 with evidence binding commit/tree/digests; independent-python
manifest verify exit 0. Rejections (typed, raw nonzero): `not_a_full_sha` (origin/main as
source), `tree_mismatch` (internally self-consistent wrong commit), `subtree_mismatch`
(accepted subtree mismatch), `missing_module` (no `mrl_launch_draft.py`),
`source_worktree_exists`, `content_mismatch` (destination changed after copying),
`manifest_digest_mismatch` + `manifest_key_set_mismatch` (manifest recorded from the wrong
installed tree). Mutations: 4/4 DETECTED — disabling the tree check, module check, content
comparison, or manifest digest cross-check makes the paired rejection fixture wrongly pass,
which is precisely how the negative tests kill each mutant; the generator fails closed if a
mutation pattern stops matching exactly once.

## 8. Requirement coverage

Per-requirement evidence: `M0-T138-evidence-map.json` (all 15 applicable rows R607–R621).
Independent verification belongs to the directive-compliance-verifier at the submitted head.

## 9. Blockers and follow-ups (all together; none stop review)

1. A binding contract whose SHA/tree/subtree fields were ALL consistently recomputed for a wrong
   commit cannot be distinguished by the script alone; bounded by the reviewed-commit-only
   contract, git history, and the §4 printed-identity comparison against the acceptance record
   (disclosed in §4 of the runbook and here).
2. `tools/controller_update/ps_tests/` is not wired into CI (`.github/workflows/**` forbidden
   for this task) — same standing gap as the accepted supervisor ps_tests; orchestrator
   follow-up.
3. Runbook §2/§7–§10 still name the retired `wt-m0t063` identities (pre-existing M0-T136 §10.4
   follow-up; out of this packet's minimal scope — only `origin/main` removal was ordered).
4. doc-check DEFAULT_DOCS still lacks the MRL runbook (pre-existing M0-T136 §10.1 follow-up).
5. The install script proves provenance at install time; runtime re-verification remains the
   existing manifest/verify-controller/preflight machinery (unchanged, by design R617).

## 10. Standing prohibitions honored (R616)

No push / PR / merge / remote change (branch local-only; PR #241 untouched); no
`C:\SupervisorController` update executed; no canary or provider run; no workflow modified; no
Tranche C work; accepted M0-T136 records untouched (`M0-T136-canary-package.md` unmodified);
owner-only R603–R605 untouched and uninterpreted; no modularity limit raised, no exception added.
