# M0-T040 G3 code review — verdict preserved verbatim

**Reviewer:** code-reviewer (independent, read-only). **Recorded by:** orchestrator (producer backend-engineer ≠ reviewer).
**Reviewed:** frozen HEAD `ca7a84a1d1bd0158c49ec6b39cf1adf6cc16cb79` (deliverable commit `b841b4f`; later commits control-records only; base `b1a9186`). **Result: PASS (no blocking defects; 2 informational).**

---

- **Gate ID:** G3 — task M0-T040 "Phase 2: authority policy simplification — Tier A/B/C/D, ADR-006, policy tests (AD-006..AD-010)" under D-010
- **Result: PASS**

## Directive/requirement verification (re-derived from source-001 §5/6/20/22 + source-003 at ca7a84a)

| Requirement ID | Verdict | Reproduced evidence |
|---|---|---|
| D-010-R006 | PASS | ADR-006 Tier A = 18 Section 5.1 actions verbatim; CLAUDE.md/rules/protocol route ordinary work through tiers with no owner approval; tier-A tests green |
| D-010-R007 | PASS | §5.5 "use pull requests; do not replace with direct pushes to main"; Tier D items 1–2 preserved; PROTOCOL "No direct producer merge to main" retained |
| D-010-R008 | PASS | Tier B map = 11 Section 5.2 rows verbatim; every class bound to its named review (test green) |
| D-010-R009 | PASS | Tier D = 14 Section 5.4 items verbatim in order; ADR states Tier D is the merge-authority projection of Section 20; CLAUDE.md human-only list kept; order+content+len-14 test green |
| D-010-R010 | PASS | Tier C = 7 Section 5.3 items; continues another accepted dependency, never escalates to an owner stop (test green) |
| D-010-R061 | PASS | ADR-006 G6 split §6.1/§6.2; GATES_AND_CHECKPOINTS G6 paragraph; test green |
| D-010-R062 | PASS | §6.1 block verbatim + explicit draft/needs-review downstream-consumption statement |
| D-010-R063 | PASS | §6.2 "G6 is required only for…"; gates doc mirrors; Tier D items 10–11 keep hard-deny |
| D-010-R104 | PASS | "Activation caveat — R595 prerequisite intact" in ADR + CLAUDE.md + rules; test green; nothing weakens it |
| D-010-R107 | PASS | Tier A + continuation policy permits beginning bounded work without routine approval |
| D-010-R111 | PASS | Owner line captured verbatim in source-003 (sha256 6c55718f…); deliverable commit b841b4f contains exactly the 7 reviewed files |
| D-010-R112 | PASS (sequence honored) | This G3 is part of the required G3+G5+DCV pre-merge sequence; roster includes security-reviewer + directive-compliance-verifier |

## Expected versus actual (7 checks — all PASS)

1. **SCOPE:** 16 files: 7 deliverables + M0-T040 control records + source-003 amendment (append-only, digests restamped, validator-confirmed). No forbidden path (tools/project_control.py, tools/agent_supervisor/, apps/, services/, .github/workflows/ untouched).
2. **AS-1 tier fidelity:** Tier A 18 / B 11 / C 7 / D 14-in-order / §5.5 10 / §6.1 8 / §6.2 8 — each verbatim vs source-001 (only deviation: Tier D item 11 apostrophe glyph, disclosed, immaterial). Supersession scoped "FOR ORDINARY TIER A WORK" only; "What ADR-005 keeps" preserves orchestrator-only CLI/git/gh, producers-in-scope, reviewers read-only; activation caveat states policy ≠ activation.
3. **AS-2 test suite:** 22/22 OK; parses the anchored ADR blocks (drop/add/reword a tier item in the ADR → suite fails on parsed==canonical AND len checks); classify_merge has exactly 10 §5.5 conditions, count-enforced.
4. **AS-3 incident replay:** allowlisted merge without checks/review → NOT_PERMITTED; allowlist-alone-not-authorization test; ordinary green merge → PERMITTED_TIER_A; D-004 source-020 (orchestrator executed #143–#146; "silent classifier … is not an authorization"; basis of R721) and source-022 ("#143,#144,#145 — RATIFIED … R718-R724 stands") corroborate.
5. **AS-4 surgical edits:** CLAUDE.md +20/−5 (human-only list preserved verbatim; "Tier D hard stops" ADDED to override clause — strengthens); rules +2; PROTOCOL +1; GATES +2 (no renumbering; G7 intact). No lingering owner-approval-for-ordinary-work passage.
6. **Cross-suite:** validator exit 0 (9 directives); test_project_control all 22 groups OK.
7. **Secrets/PII/quality:** none found; prose precise and internally consistent.

## Defects

None blocking. **INFO-1:** Tier D item 11 apostrophe normalization (U+2019→ASCII), disclosed, ADR+canonical mutually consistent so drift guard sound. **INFO-2:** DriftGuardSelfTest mutates the in-memory canonical (near-tautological), but the substantive drift protection lives in the parse-and-compare tests, independently confirmed to read the real ADR blocks.

## Reviewer conclusion

**PASS.** ADR-006 reproduces D-010 Sections 5/6 faithfully; supersession scoped to Tier A only; ADR-005 core preserved; R595 + every Section 20 / Tier D hard stop intact; 22-test suite green and drift-enforcing; incident replay present, green, corroborated; doc edits minimal and non-weakening; validator + control-plane suites green; scope clean. Record G3 = PASS and proceed to G5 security + DCV per R112 before any merge.
