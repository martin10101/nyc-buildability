# G5 Security Gate Report - M0-T148

- Task: M0-T148 - evidence-packet completeness repair (untracked contents, task contract, supervisor-executed test transcripts)
- Reviewed identity: frozen HEAD 7772626e (content of commit 53d642a1), branch candidate/D-024-mrl-option-b
- Reviewer: security-reviewer (independent, read-only; producer backend-engineer)
- Verdict: PASS (no critical/high/medium defects; LOW-1/LOW-2/LOW-3 by-design residuals below)

## Verification performed
- Re-ran both changed suites at the reviewed identity: reviewer 117 passed, loop 126 passed.
- Traced the full trust chain in code: evidence.py, loop.py, codex_reviewer.py, redaction.py, process.py, policy.py, review_packet.py, cli.py, launch_seam.py.

## Surfaces
1. Prompt injection - PASS. New sections named in REVIEW_INSTRUCTIONS with the only-instructions-are-mine framing extended to untracked_content/command_transcripts/task_packet (codex_reviewer.py:863-903); single json.dumps serialization means no string-container breakout (codex_reviewer.py:928-930); reserved instruction key refused if pre-present; prohibited-key scan unaffected by hostile file names.
2. Secret leakage - PASS w/ LOW-1. redact_structure runs over the WHOLE assembled packet including extra_sections (evidence.py:711-727, redaction.py:117-159); mutation test proves redaction is load-bearing. Enumeration uses porcelain untracked (git-ignored files - .env etc. - never enumerated). LOW-1 residual: a non-ignored untracked secret matching no pattern would ship to the external reviewer - identical residual as accepted for diff_content (M0-T147); defense-in-depth present.
3. Command execution - PASS w/ LOW-2. Commands only from validate_documented_test_commands (policy.py:881-939, fail-closed profile, no shell metacharacters); argv-only execution, shell=False, minimal_env, assert_argv_safe, 300s timeout, double-bounded capture, full-outcome digest (evidence.py:470-523, process.py). Task packets are orchestrator-authored (ADR-005) - workers cannot inject commands. LOW-2: documented commands execute worker-authored test files on the host at review time - the intended mechanism, contained (minimal_env, job object, timeout); retain in the R247 recertification record.
4. Path traversal - PASS. Every new read goes through read_file with post-resolve containment (symlink/junction-safe, evidence.py:393-399); C-quoted porcelain names decode then re-check; blank task id refused. Verified by tests.
5. Resource exhaustion - PASS. MAX_UNTRACKED_FILES=32 with fail-visible count_cap_exceeded naming omitted files; per-file 16384-byte bound with FULL-content digest; binary-safe reads; whole-packet 262144 cap fails closed to STOP_FOR_OWNER -> WAIT_FOR_OWNER + owner touch (evidence.py:739-744, loop.py:1995-2004).
6. Read-only git - PASS. assert_read_only_git unchanged and guarding; the new methods add NO git invocation.

## Non-blocking observations
- LOW-3: sensitive-key over-redaction - an untracked deliverable NAMED like a secret (e.g. token_store.py) is wholesale-masked (safe direction; could cause a spurious REVISE). Informational.

Conclusion: all six surfaces handled correctly with reproducible positive/negative/mutation tests at the reviewed identity. PASS; carry LOW-1/LOW-2 into the R247 recertification note.
