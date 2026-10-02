<!-- Directive-compliance verification of M0-T165 (independent directive-compliance-verifier, read-only); saved verbatim by the orchestrator. -->
=== FULL REPORT: DCV M0-T165 ===

Head reviewed: 6f80c23717932eef8baa4a7069df7ca3ed098ffe (PR #288 headRefOid confirmed; branch task/M0-T165-linux-platform-seam, base candidate/D-024-mrl-option-b, PR OPEN/not merged). The rv-288 review worktree is at 23816db2 (an ancestor of the PR head; `git checkout --detach` is blocked by my read-only guard, so I inspected the PR head directly via git plumbing — valid, since all code files are byte-identical between 23816db2 and 6f80c237). Read-only throughout; no repo/gh/ledger writes; did not run tools/test_directive_compliance.py.

VERDICT: PASS. Both applicable requirements satisfied for THIS task's share. No blocking items.

CONTENT IDENTITY — CONFIRMED
- `frozen_git_identity` (the function `_task_git_identity`/submit/gate/accept all use) for M0-T165's seven allowed_paths at 6f80c237 = 815ed89c16552b358bb737346596d77bfa6dd6cea1bdbcdff9a8c55bd8624858 — matches the given content identity exactly.
- Identity is byte-stable at 815ed89c across the submit commit 23816db2, the G5 commit f7d1c225, and the PR head 6f80c237 (recomputed each). The producer commit 5740b823 differs (60383406) only because producer-report.md was added one commit later (00126115). Lineage is linear: 5740b823 (producer) → 00126115 (report) → cf497c5e (evidence-map) → 23816db2 (submit) → f7d1c225 (G5) → 6f80c237 (G2/G3/G4).

GATES (all PASS; content manifest 815ed89c for the substantive gates)
- G0 orchestrator/administrative, manifest 32f20119 at contract head a4ca65c9 (readiness).
- G2 orchestrator/self_check, G3+G4 code-reviewer/independent_review, G5 security-reviewer/independent_review — all PASS, all content_manifest_sha256 = 815ed89c. The reviewed_sha fields (f7d1c225 for G2/G3/G4, 23816db2 for G5) are ledger-advancing commits carrying the same identity; not a defect.

INDEPENDENT EVIDENCE I REPRODUCED (not the producer's say-so)
- Scope: producer commit 5740b823 changed EXACTLY the 6 in-scope files (config.py, os_acl.py, platform_paths.py new 114L, posix_acl.py new 180L, process.py, test new 400L). No out-of-scope/forbidden path touched.
- os_acl.py purely additive: existing evaluate_controller_config_acl / evaluate_file / evaluate_directory / _combine / _run_icacls / _query_owner byte-unchanged (diff adds only the lazy-dispatch controller_config_acl_verdict + a docstring line). Windows path byte-identical.
- posix_acl.py: fail-closed POSIX verifier — PROTECTED only for root-owned (uid 0), not group/world-writable file in a root-owned non-writable parent, no symlinks (uses os.lstat so a symlink can't resolve to a root target and false-pass); missing/unreadable/non-POSIX → UNKNOWN, never read as protected; same AclVerdict/ControllerConfigAclVerdict dataclasses and combine rule as os_acl.
- platform_paths.py: POSIX config hardcoded /etc/nyc-supervisor/config.toml, ignores injected env; no C:\ / %LOCALAPPDATA% ever returned on POSIX; Windows branch byte-matches runbook; runtime delegates to durable_state (single source).
- process.py: DISABLE_AUTOUPDATER belt for the two bare probes returns {}/no-op on Windows; FORCED_CLAUDE_CHILD_ENV value byte-identical (constant rename only); no import-time os.environ mutation.
- Tests: tools/test_agent_supervisor_platform_seam.py → 34 passed (venv python 3.12). Working-tree files byte-identical to 6f80c237 (empty diff), so this tests the reviewed content. Each acceptance scenario (primary/boundary/missing-ambiguous/failure/regression-parity) maps to a fail-on-mutation test.
- Regression: os_acl + process suites → 3 failed / 52 passed / 19 skipped. The 3 failures are pre-existing Windows-only tests (icacls/System32 absolute-path + writable-probe assertions) that fail on any Linux host; M0-T165 did NOT change the os_acl test file and did NOT touch the icacls functions, so they are environment artifacts, NOT regressions. CI runs the suite on windows-latest where they pass.
- Independent G3/G4 (code-reviewer) and G5 (security-reviewer) reports, read verbatim, reach the same findings (additive; os_acl lines 1-464 byte-identical sha256 6a48b0a0 both sides; fail-closed intact; Windows byte-unchanged; 34 tests pass; 3 os_acl failures pre-existing; no supervisor module yet consumes the new symbols). Producer ≠ either reviewer; both read-only.
- CI: gh pr checks 288 = 40 pass, 0 non-pass (the one flaky supervisor-bridge check was re-run green). This clears the single merge precondition both reviewers flagged (CI hygiene — an integration precondition, never an M0-T165 defect).

PER-REQUIREMENT RULINGS (this task's share)
- D-091-R001 (move the loop to this server — this task's step): PASS. Delivers the first code step of the move: the Linux platform seam (posix_acl.py POSIX config-protection verdict in os_acl's shape; platform_paths.py Linux config/activation/runtime resolver with no Windows path on POSIX; os_acl.controller_config_acl_verdict POSIX dispatch, Windows unchanged; config.default_config_path; process.py DISABLE_AUTOUPDATER belt for the bare probes), proven by 34 passing tests, within scope, identity 815ed89c. R001 overall (a certified Linux loop actually running) remains an open directive-level obligation spanning M0-T165..T168 and later tasks; this task's share is complete and the deferred call-site wiring is honestly disclosed as M0-T166.
  Evidence: tools/agent_supervisor/posix_acl.py, platform_paths.py, os_acl.py (controller_config_acl_verdict), config.py (default_config_path), process.py (posix_autoupdater_belt/bare_probe_env/apply_posix_autoupdater_belt) @6f80c237; tools/test_agent_supervisor_platform_seam.py 34 passed; producer commit 5740b823; evidence-map D-091-R001. reviewed_sha 6f80c237.
- D-091-R007 (reviewed and certified before use; certification later): PASS. The loop changes were independently reviewed and gated before any use — G2 self-check, G3/G4 independent code-reviewer, G5 independent security-reviewer, all PASS at identity 815ed89c; no fail-closed check weakened; Windows behavior byte-unchanged; no live loop started or commissioned (nothing consumes the new symbols yet). Controller recertification is correctly deferred to a later D-091 task, matching R007's "certification later." This task's share (reviewed+gated before use) is satisfied.
  Evidence: project-control/gates/M0-T165-G{2,3,4,5}.json all PASS (manifest 815ed89c); reports M0-T165-G3G4.md and M0-T165-G5.md (independent reviewers, read-only; additive + fail-closed + Windows-unchanged reproduced); 34 tests + os_acl byte-identity reproduced by me; CI 40/40; evidence-map D-091-R007. reviewed_sha 6f80c237.
Neither requirement is DISCHARGED at the directive level (both remain pending overall); THIS task's share of each is PASS.

EXACT verification.json VALUES (for the M0-T165 task_verifications row)
- verifier: directive-compliance-verifier
- reviewed_sha: 6f80c23717932eef8baa4a7069df7ca3ed098ffe
- reviewed_manifest_sha256: 815ed89c16552b358bb737346596d77bfa6dd6cea1bdbcdff9a8c55bd8624858
- requirements:
  - D-091-R001: state PASS; reviewed_sha 6f80c23717932eef8baa4a7069df7ca3ed098ffe; evidence ["tools/agent_supervisor/posix_acl.py + platform_paths.py + os_acl.controller_config_acl_verdict + config.default_config_path + process.py POSIX autoupdater belt @6f80c237 (producer 5740b823)", "tools/test_agent_supervisor_platform_seam.py 34 passed (venv)", "scope = 6 allowed-path files only; identity 815ed89c", "project-control/reports/M0-T165-evidence-map.json D-091-R001"]
  - D-091-R007: state PASS; reviewed_sha 6f80c23717932eef8baa4a7069df7ca3ed098ffe; evidence ["gates M0-T165-G{2,3,4,5}.json all PASS, content_manifest 815ed89c", "reports M0-T165-G3G4.md (code-reviewer) + M0-T165-G5.md (security-reviewer): additive, fail-closed preserved, Windows byte-unchanged, no live loop/commissioning", "recertification deferred to a later D-091 task", "CI gh pr checks 288 40/40", "evidence-map D-091-R007"]

RESTAMP PRE-AUTHORIZATION (stated up front)
The orchestrator MAY restamp reviewed_sha from 6f80c237 to the later live HEAD H' at accept time WITHOUT re-review iff ALL hold (blob-level predicate):
1. `_task_git_identity`/`frozen_git_identity` for M0-T165's allowed_paths at H' returns identity == 815ed89c16552b358bb737346596d77bfa6dd6cea1bdbcdff9a8c55bd8624858 and resolves to H'. (Authoritative, path-scoped guarantee that every reviewed work-product blob — the 5 modules, the test, and producer-report.md — is byte-identical at H'.)
2. `git diff 6f80c237 H' -- . ':(exclude)project-control'` is EMPTY (no non-ledger file — code, test, docs — changed).
3. `material_digest(M0-T165 packet @H') == material_digest(@6f80c237)` (packet changed only in lifecycle fields), and the only project-control changes between 6f80c237 and H' are accept-seam ledger records (state.json, tasks/M0-T165.json lifecycle, directives/.../verification.json, M0-T165 gate/report records), with producer-report.md content unchanged.
Predicate 1 alone is sufficient and dominant; 2 and 3 are belt-and-suspenders.
DISJOINT PEER COMMITS: TOLERATED. Because the predicate-1 identity is scoped to M0-T165's allowed_paths, a disjoint peer/lane commit between freeze and accept that touches NO M0-T165 allowed_path leaves the identity at 815ed89c and the restamp is safe. If any commit (peer or seam) touched one of M0-T165's allowed_paths (os_acl.py, config.py, process.py, posix_acl.py, platform_paths.py, test_agent_supervisor_platform_seam.py, or M0-T165-producer-report.md), predicate 1 fails → re-review required. If you want to tolerate disjoint peer CODE commits too, rely on predicates 1+3 and scope predicate 2 to M0-T165's own paths rather than all non-project-control paths.

NON-BLOCKING NOTES
- N1: os_acl.controller_config_acl_verdict is not yet wired into cli.py's doctor posture (cli.py is outside this packet's allowed_paths; deferred to M0-T166). Until then the Linux doctor surfaces UNKNOWN via the Windows-only entry — fail-closed-safe. Honestly disclosed in the producer report and both reviews.
- N2: On this Linux host 3 os_acl tests fail (Windows icacls/System32 assertions lacking skip guards); unrelated to M0-T165, which did not touch those functions or that test file. CI on windows-latest is the authoritative regression evidence and is green.
- N3: The G3/G4 and G5 reports were written against reviewed_sha 23816db2 (then-HEAD), whose M0-T165 content identity is the same 815ed89c as the PR head 6f80c237; the gate records carry that identity, so the reviews bind the reviewed content, not a stale tree.

=== END REPORT ===
