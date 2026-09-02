# M0-T138 G2 self-check (producer; never satisfies an independent gate)

Recorded against the acceptance scenarios of `project-control/tasks/M0-T138.json`; every
executable claim is backed by a raw `tools/gate_runner.py` record in
`project-control/reports/M0-T138-gates/` at repo_head `435531de` (R590).

| Scenario | Result | Evidence |
|---|---|---|
| AS-SB-1 (one concrete owner command; no placeholder; no origin/main; tooth rc0) | PASS | `test_runbook_parse` assertions (section-4 script invocation, `-Phase install`, no `<`, pinned 40-hex SHA, `origin/main` absent) inside `m0t138-ps-tests-controller-update.json` rc0; `m0t138-doc-check-default.json` rc0 (11 presented commands ok) |
| AS-SB-2 (pre-copy fail-closed identity checks + typed rejections a/b/c/d) | PASS | `test_source_binding`: P1 install rc0; REFUSED `not_a_full_sha`, `tree_mismatch`, `subtree_mismatch`, `missing_module`, `source_worktree_exists`; nothing installed on refusal |
| AS-SB-3 (complete bidirectional SHA-256 proof + evidence; e) rejected) | PASS | P1 evidence binds commit/tree + per-file digests; REFUSED `content_mismatch` after post-copy tamper |
| AS-SB-4 (manifest cross-check vs accepted source; f) rejected; independent digests) | PASS | P2 verify-manifest rc0 with python-hashlib-crafted manifest; REFUSED `manifest_digest_mismatch` / `manifest_key_set_mismatch`; evidence gains `manifest_binding` verdict |
| AS-SB-5 (mutations killed; generator fail-closed) | PASS | `test_mutants_detected`: 4/4 DETECTED (tree, module, content, manifest); pattern-count guard asserts exactly-once matches |
| AS-SB-6 (PS 5.1 parse-clean; runner rc0; modularity/governance/ruff clean) | PASS | 13/13 runbook blocks + script parse with zero errors; suite rc0; `m0t138-modularity.json` rc0; `m0t138-directive-registry.json` rc0; `m0t138-context-budget.json` rc0; `m0t138-ruff-root.json` rc1 with stdout_sha256 byte-identical to frozen `final-freeze-ruff.json` (pre-existing F28 only, no `.py` changed) |

Affected-surface regression: `m0t138-supervisor-ps-tests.json` rc0 (accepted suite untouched and
green); `m0t138-pytest-command-docs-manifest.json` rc0 (77 tests — the living-runbook parser
tests that read the edited runbook, plus the manifest binding suite);
`m0t138-doc-check-mrl.json` / `m0t138-doc-check-canary.json` rc0.

Self-verdict: ready for independent G3/G4/DCV review. This record is the producer's own check and
decides nothing (ADR-005; R619).
