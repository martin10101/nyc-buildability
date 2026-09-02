# M0-T138 G4 independent QA review (verbatim reviewer return)

Reviewer: `qa-engineer` (independent read-only agent; not the producer). Returned via the
agent-return channel and saved verbatim by the orchestrator (transport entity-decoding only).

---

**VERDICT: PASS**

# G4 QA Gate Report — M0-T138 (D-024 Amendment 41: controller-update source binding)

**Reviewer:** qa-engineer (independent; not the producer). **Read-only** — no repo writes, no ledger/git/gh.
**Identity verified:** ctl24 is on `candidate/D-024-mrl-option-b` at `99cd3dad` (ref read from `<pack>/.git/worktrees/ctl24/HEAD` → `refs/heads/candidate/D-024-mrl-option-b` = 99cd3dad). Implementation commit `435531de` changed 9 files (0 `.py`; only `.md`/`.ps1`/`.json`). ctl24 working copies of `source_binding.json` and `update_controller_from_candidate.ps1` are byte-identical (CR-normalized) to the committed blobs at 99cd3dad — no shared-tree drift; execution hit the exact reviewed content.
**Note on my worktree:** my dispatched worktree was isolated on a stale origin/main base (d8b3899f, far behind 99cd3dad); I reviewed the ctl24 shared checkout at the reviewed SHA instead — read-only, no `git reset`.

## Command surface — measured vs recorded (all repo_head 435531de)

| # | Command | Measured raw | Recorded | Match |
|---|---|---|---|---|
| 1 | controller_update ps_tests | 0 | 0 (ps-tests-controller-update) | OK |
| 2 | agent_supervisor ps_tests | 0 | 0 (supervisor-ps-tests) | OK |
| 3 | doc_check default (11 cmds, 0 fail) | 0 | 0 (doc-check-default) | OK |
| 4 | doc_check MRL (6 cmds, 0 fail) | 0 | 0 (doc-check-mrl) | OK |
| 5 | doc_check canary (3 cmds, 0 fail) | 0 | 0 (doc-check-canary) | OK |
| 6 | pytest command_docs+manifest (77 passed) | 0 | 0 (pytest-command-docs-manifest) | OK |
| 7 | modularity --check (352 files, 0 fail, 12 pre-existing warns) | 0 | 0 (modularity) | OK |
| 8 | validate_directive_compliance --check | 0 | 0 (directive-registry) | OK |
| 9 | context_budget_check (PASS) | 0 | 0 (context-budget) | OK |
| 10 | ruff digest `74680cc7…54cd63` | rc 1 | rc 1 (m0t138-ruff-root + M0-T136 final-freeze) | OK |

Ruff digest byte-identical to BOTH recorded files and the expected frozen digest — zero new findings (surface frozen at the M0-T136 accepted state). No deviation on any command.

## Negative / mutation coverage (six R613 classes)
All six exercised on a real deterministic git fixture (writes only to %TEMP%), each with a typed reason + raw nonzero: **a** not_a_full_sha (origin/main), **b** tree_mismatch, **c** missing_module (no mrl_launch_draft.py), **d** subtree_mismatch, **e** content_mismatch (post-copy byte mutation), **f** manifest_digest_mismatch + manifest_key_set_mismatch. Plus the extra `source_worktree_exists` guard. Positive control: -Phase install exits 0 with bidirectional SHA-256 evidence. **4/4 mutants DETECTED** (tree/module/content/manifest-check disablement each killed by its rejection fixture — checks proven load-bearing, not vacuous). AS-SB-1..AS-SB-6 all independently reproduced PASS; runbook has 13 parse-clean PS 5.1 blocks, 0 `origin/main`, literal pinned SHA at §4, verify-manifest at §5a. Binding contract is **truthful**: `1489879e^{tree}`=0babc469 and `1489879e:tools/agent_supervisor`=79af11a2, both matching the pinned values and the M0-T136 accepted identity, required_modules includes mrl_launch_draft.py.

## Live-controller safety
Update did NOT run: `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_update_evidence.json` absent; `C:\SupervisorController` newest write is `model_selection.toml` 2026-09-01 00:22 (bulk 2026-08-18) — no 2026-09-02 robocopy /MIR, so my review left the controller untouched. Minor non-blocking observation: that mtime is 22 min into 2026-09-01 rather than strictly before it, but it predates both the implementation (2026-09-02 01:32) and this review, and is pre-existing owner state unrelated to M0-T138.

**Conclusion:** Every required scenario and the full regression surface reproduce green at the reviewed content with returncodes matching the recorded evidence, the six rejection classes and four mutants give real fail-closed coverage, and nothing touched the live controller — **PASS**.

(Reviewer-scope note: the D-024 ALL directive requirement-to-evidence pass is the separate `directive-compliance-verifier` gate recorded in verification.json; this G4 covers the executable acceptance + regression surface.)
