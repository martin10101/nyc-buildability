# M0-T078 G3 independent review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule, .claude/rules/project-control.md). Reviewer: t078-g3-reviewer
(independent; reviewer ≠ producer ≠ verifier).

---

# G3 independent review — M0-T078 (engineering-reliability standard + skill router)

## Verdict: PASS

Reviewed identity: **48a5da9c60d6ab1fb09b83dcffd9c08884a0f032**
Scope: `docs/ENGINEERING_RELIABILITY_STANDARD.md` (new, 284L), `.claude/skills/engineering-reliability/SKILL.md` (new, 38L), `CLAUDE.md` (+2/-1), `AGENTS.md` (+3/-1); task commit b1fb384, merged at 409386c.

All findings are **minor** and **non-blocking**. No must-fix or important finding. I re-derived every conclusion independently rather than accepting the producer's.

---

## What I verified

**1. All ten required principle areas are present and complete.** Spot-checking the hardest requirements from the brief: §1.5 requires "Write exactly ONE root-cause hypothesis before any fix" with a falsifying observation; §3.1 red-before-green plus §3.4 mutation-or-revert proof scoped to critical-class regressions; §4 carries all four states (`pending`/`success`/`error`/`cancelled`) plus supersession (§4.3), cancellation (§4.4), stale-response prevention (§4.5), and semantic dedup (§4.6); §5 binds keys to caller + operation + payload (§5.1) with atomic claim (§5.2) and crash reconciliation (§5.6); §6 covers transient-only (§6.1), bounded attempts *and* elapsed time (§6.2), jitter (§6.3), `Retry-After` (§6.4), exactly one layer (§6.5), ambiguous-effect reconciliation (§6.6); §7 covers typed errors, two-audience payloads, correlation IDs, no leakage, log-once; §8 has all nine verification contexts including clean checkout, platforms, concurrency, unsafe paths, stale state, integration, real flow, frozen identity, independent review; §9 has the three-tier table with cosmetics explicitly non-blocking; §10 is measured-claims-only. No eleventh principle introduced.

**2. Non-duplication — I verified all nine Section-0 rows (brief asked for six), plus five additional inline anchors.** Every cited document genuinely contains the cited rule:
- `.claude/ORCHESTRATION_POLICY.md` §D is "Review independence (frozen SHA)" and contains the producer≠reviewer rule, the exact-reviewed-SHA rule, and invalidation-on-later-commit — verbatim support.
- `.claude/rules/backend-api.md` line 22 is a verbatim match for the jobs row (DB-backed, idempotent, resumable, cancellable, heartbeat/retry/dead-letter).
- `docs/DEPENDENCY_SECURITY_POLICY.md` lines 23-24 carry the exact 604800-passes/604799-fails boundary; ORCH §G is the dependency-security section.
- `docs/CODE_MODULARITY_POLICY.md` §2 responsibility/cohesion, §3 size thresholds, §4 complexity, §6 public-interface preservation, §11 over-fragmentation — all match their descriptions.
- `docs/LEAN_OPERATING_PROCESS.md` Return item 6 contains B3/B5/B6/B8 as cited; Return item 8 contains the "merging materially-different safety cases" prohibition.
- `docs/SECRETS_POLICY.md` §3 is "Handling rules"; `docs/GATES_AND_CHECKPOINTS.md` G5 is the security/privacy gate.
- `AGENTS.md` "Never guess" contains "A missing value reads `unknown`, never zero"; `CLAUDE.md` principle 3 and principle 7 match their citations exactly.
- `docs/ACCEPTANCE_SCENARIO_STANDARD.md` "Universal minimum set" item 6 is "Retry or idempotency case", supporting §5.8.
- `docs/GATES_AND_CHECKPOINTS.md` line 83 "No duplicate or contradictory implementations" is confirmed to sit under the G4 heading, as §2.5 claims.
- `docs/CONTEXT_PIPELINE_RUNBOOK.md` records the M0-T076 frozen e2e baseline, supporting §10.2. LEAN's header rule states "Line-count reduction is never itself an acceptance criterion", supporting §10.7.

I also tested non-duplication from the reverse direction: no pre-existing debugging method exists anywhere in `docs/` or `.claude/rules/`, confirming §1 is genuinely new content.

**3. Every path and anchor resolves.** All 14 backticked repository paths exist. G0-G7 headers, ADR-005, and ADR-006 all exist. Zero broken citations.

**4. The skill is a genuine router.** `find` returns exactly one file — no scripts, assets, sub-directories, agent definitions, or dependencies. Its description-only frontmatter matches the convention of all eleven sibling skills. The description names seven specific trigger conditions rather than matching every task. Both files carry explicit subordination clauses (standard lines 8-11; skill lines 26-29) and no authority-granting language.

**5. CLAUDE.md/AGENTS.md changes are minimal and consistent.** One table row and one prose clause respectively. The "five standard workflows" → "standard workflows" edit is correct and complete: the phrase now appears nowhere in the repository except the producer report describing the change. The five pre-existing skill rows are byte-identical; the new row is appended sixth. The trigger matrices in the standard and the skill agree row-for-row on all seven mappings.

**6. No third-party references, no self-improvement claims.** Zero hits for Superpowers/secondsky/wshobson/marketplace/install. Every hit for faster/cheaper/cost/improvement sits inside a trigger description, a §10 prohibition, or the §10.8 self-disclaimer.

**7. `python tools/context_budget_check.py` → PASS, exit 0.** Eager total 2,956 of 6,000 tokens. `python tools/validate_mcp_policy.py` → exit 0, policy intact.

**8. Acceptance scenarios — I re-executed seven of nine (AS-1, 2, 3, 5, 6, 8, 9), beyond the three requested.** All reproduce. I additionally verified the producer's single measured claim independently: extracting both CLAUDE.md versions and applying the tool's own `ceil(len/4)` formula gives 2467 → 2498 tokens, confirming the stated 31-token increase and the 2,925 → 2,956 eager totals exactly.

---

## Findings

**Finding 1 — MINOR. Location: `project-control/reports/M0-T078-producer-report.md` lines 185-188 (AS-6 digest block).**
The four SHA-256 digests mix two line-ending encodings. Re-running `sha256sum` in the working tree reproduces only two of four: `CLAUDE.md` and `AGENTS.md` digests are of CRLF working-tree content, while the two new files' digests are of LF content. Root cause is `core.autocrlf=true` in this repo.
*Consequence:* a reviewer following the report's instruction that "a reviewer re-running either validator at these digests must observe identical output" sees a mismatch on two files and could wrongly conclude the deliverables drifted after submission.
*I confirmed there is no drift.* Stripping CR from the working-tree copies yields `aedf17fa…` and `53c64fa6…`, matching the report byte-for-byte, and these also equal the committed blob digests at 48a5da9. Content identity is sound; only the presentation is ambiguous. Recommend stating the normalization or using `git hash-object`.

**Finding 2 — MINOR. Location: `docs/ENGINEERING_RELIABILITY_STANDARD.md` §7.1 (line 191-193).**
The line restates LEAN return item 6 (B5) near-verbatim — "stable code + concise message + structured metadata (submitted value, expected rule, failed condition)" — despite the standard's own §0 instruction "Do not copy text between this file and the documents in §0." The same pattern appears more lightly in §8.6 (restating G4's list) and §8.9 (restating CLAUDE.md principle 7).
*Consequence:* if B5's shape is later amended, §7.1 silently contradicts the canonical home and a reader following the standard applies a stale shape. Mitigated by the citation being present and the standard's stated conflict rule making the canonical document win, so this does not block.

**Finding 3 — MINOR. Location: `docs/ENGINEERING_RELIABILITY_STANDARD.md` §6, particularly §6.5.**
§6 states the retry rules correctly but never points to the repository's existing single retry implementation — `services/api/app/resilience/transport.py` and `retry.py` (M2-T011) — which `docs/SOURCE_ACCESS_REGISTRY.md` line 195 records as "implemented once … and consumed by all connectors" with bounded jittered retry and exact `Retry-After` honoring.
*Consequence:* an agent satisfying §6.5 ("Name the layer that retries") from scratch could add a second retry layer, which §2.5 and G4's "No duplicate or contradictory implementations" would then classify as a defect. A one-clause cross-reference in §6.5 closes this. Note this is a *missing cross-reference*, not a duplication — no canonical retry *rule document* exists, so §0's omission of a retry row is correct.

**Finding 4 — MINOR. Location: `project-control/reports/M0-T078-producer-report.md` §1, lines 42-45.**
The report says the frontmatter "names the five invocation triggers"; the description actually names seven, omitting the error-path and reviewing-another-identity triggers from its own enumeration. The deliverable is correct — only the report's prose understates it.

---

## On the producer's flagged judgment calls

Call 1 (CLAUDE.md row added despite auto-discovery) — justified; I confirmed the stale count phrase now appears nowhere in the repo, so the enumeration is truthful and the 31-token cost is verified. Call 3 (AGENTS.md prose clause rather than a table row) — correct form, that section is a sentence with no table. Call 4 (trigger matrix intentionally duplicated) — defensible, and I confirmed the two copies agree exactly on all seven rows, so there is no drift risk today. Call 5 (mutation proof scoped to critical classes) — I judge the scope appropriate, not too narrow.

## Reviewer discipline

No repository write of any kind, no git mutation, no `tools/project_control.py` invocation. I wrote two throwaway copies of CLAUDE.md into the session scratchpad (outside the repo) solely to compute the token delta without touching the working tree. The pre-existing dirty working-tree entries (`project-control/state.json`, `tasks/M0-T078.json`, and the untracked G2/report files) are orchestrator-owned and were not touched by me.

## Commands run

(Recorded verbatim in the reviewer return; ~50 read-only commands: git rev-parse/status/log/show/cat-file/diff, grep sweeps over both new files and all cited documents, sha256sum + CR-stripped digests + committed-blob digests, python tools/context_budget_check.py, python tools/validate_mcp_policy.py, skills frontmatter comparison, docs/adr listing, token-delta recomputation via the tool's own ceil(len/4) formula.)
