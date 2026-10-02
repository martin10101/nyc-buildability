<!-- Directive-compliance verification of M0-T167 (independent directive-compliance-verifier, read-only; restamp pre-authorization: content identity unchanged, disjoint peer commits tolerated); saved verbatim by the orchestrator. -->
=== FULL REPORT: DCV M0-T167 ===
Task: M0-T167 — D-091 T4: admit the Codex CLI (@openai/codex) through dependency security. PR #289. Frozen head 8e61d4a7 (detached at /root/project/rv-289). Base/frozen_baseline c81ba14d. Content identity 9efc9773… (reproduced). Producer: cloud-architect. Required gates G0,G2,G5.

Material commits (within allowed_paths): c557056e (tools/codex_cli/{.gitignore,README.md,package-lock.json,package.json}) + cbe0b3ea (.github/workflows/ci.yml, scheduled-web-audit.yml, README CI section). `git diff c81ba14d..HEAD` non-control files = only those 7 paths + docs/D091_CLOUD_LOOP_DESIGN.md (a D-091 bootstrap file created in the shared contract commits 3f9a8c35/a4ca65c9, not a T167 product). No forbidden path touched; CI change is purely additive (G5 diffed it).

Gate records: G0 PASS (orchestrator/admin, re-recorded at 48ed6c71 after the scope correction — administrative, identity need not be final). G2 PASS (reviewer orchestrator, role self_check, content_manifest_sha256 9efc9773, report M0-T167-G2.md). G5 PASS (reviewer security-reviewer, role independent_review, content_manifest_sha256 9efc9773, report M0-T167-G5-r2.md; history shows round-1 FAIL at 439777e3). Producer (cloud-architect) ≠ G5 reviewer (security-reviewer) ≠ orchestrator. The only commits after the gates' reviewed_sha 6c645a96 (→ current head 8e61d4a7) write gate/state records outside allowed_paths, so the content identity is byte-stable 6c645a96→8e61d4a7 (I recomputed 9efc9773 at 8e61d4a7).

D-091-R001 — "Move the loop to this cloud server" (this task's share = the Codex-admission step). SATISFIED.
Evidence reproduced:
- tools/codex_cli/package.json:8 `"@openai/codex": "0.157.0"` — the binary codex_reviewer.py needs now exists repo-locally on the server.
- tools/codex_cli/README.md:101-127 flags table — every argv token build_argv() in codex_reviewer.py uses (exec, -C, -m, --ephemeral, --ignore-user-config, --strict-config, --sandbox read-only, --json, --output-schema, --output-last-message, -c, `-` stdin) is present in `codex exec --help` 0.157.0; `codex --version` → codex-cli 0.157.0.
- README.md:142-154 — Codex sign-in lives at ~/.codex/auth.json under CODEX_HOME (owner-only, R006); NOT done here. evidence-map D-091-R001 confirms "No sign-in was done."
- No commissioning / no Windows behavior change: G5-r2 §1 confirms ci.yml and scheduled-web-audit.yml changes are purely additive (every existing job/trigger/permission/pin unchanged); node_modules git-ignored and uncommitted (`git ls-files tools/codex_cli` = 4 files).
- gates/M0-T167-G2.json result PASS at 9efc9773.

D-091-R005 — "Codex installed only after the dependency-security check" (advisory-free, exact-pin, integrity-matched, ≥7 days, G5 provenance, no waiver). SATISFIED.
Evidence reproduced:
- Exact pin: package.json:8 and package-lock.json:12 both "0.157.0" (no ^/~); lockfileVersion 3. [verified directly]
- Integrity-matched: package-lock.json:18 integrity sha512-st1R2MhP3ndngOqj2SVh1qk6ED1lpgtlDxipDUyxlKfbsna0imwU2FdTnCjohFQpVh4bR5D5m1hA05AuW2v8Xg== with resolved https://registry.npmjs.org/…; all 7 entries carry registry integrity + registry origin. G5 report §Integrity string-compared all 7 to registry dist.integrity → ALL MATCH; CI `npm ci` re-verifies every tarball.
- Age ≥ 604800 s: README.md:30-44 table — 0.157.0 published 2026-09-25T02:35:19.752Z, 615752 s (7.13 d) at admission; all 7 packages PASS; boundary 0.157.1 at 534500 s (6.19 d) correctly rejected. G5 independently recomputed from the registry (618236 s) and confirmed 0.157.1/0.158.0/0.160.0 all <604800 rejected. CI job `codex-cli-dependency-security` ran `node ../../apps/web/scripts/dependency_age_gate.mjs package-lock.json` → PASS (7/7, min_age=604800 s), log read by the G5-r2 reviewer (G5-r2.md para 3).
- Advisory-free at every severity: README.md:74-78 npm audit total 0 across info/low/moderate/high/critical. CI job steps `npm audit --audit-level=low` + JSON-total==0 (ci.yml). G5 independently queried the npm bulk advisory endpoint + OSV → both empty.
- Lifecycle scripts: README.md:57-62 scripts:{} on every package; installed with --ignore-scripts. [G5 confirmed hasInstallScript unset]
- G5 provenance review: reports/M0-T167-G5-r2.md VERDICT PASS (independent security-reviewer); round-1 B1 "no continuous CI audit of tools/codex_cli" (G5.md) was the only blocker, fixed by cbe0b3ea (two additive fail-closed jobs: ci.yml `codex-cli-dependency-security` every push/PR + scheduled-web-audit.yml `codex-audit` daily), B1 CLOSED in round 2.
- No-waiver continuous audit now in place and GREEN: `gh pr checks 289` — `codex-cli-dependency-security (audit + committed-lock age gate)` PASS and `codex-cli tree re-audit (blocking on any finding / too-new / outage)` PASS.
- Install only after the check: node_modules git-ignored (tools/codex_cli/.gitignore), repo-local, reinstall via `npm ci --ignore-scripts`; no global install (G5 confirmed no global directive). No sign-in.
- gates/M0-T167-G5.json result PASS at 9efc9773.

Conclusion T167: both applicable requirements SATISFIED. PASS.
END-OF-REPORT
=== END REPORT ===
