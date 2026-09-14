# Wave-4 DCV verification — M4-T018 + M4-T019 (verbatim verifier return)

Recorded by the orchestrator from the independent directive-compliance-verifier's return.
Frozen verification head a7cc1757; restamped to d752c09b under §4's conditional
pre-authorization (orchestrator verified all four conditions mechanically at restamp:
material diffs EMPTY over the three material files + classifier; cited D-045/D-046/D-051/
D-052 requirements.json diffs EMPTY; the a7cc1757..d752c09b delta is docs + the D-054
capture + index only — no prohibited surface; D-054 rows bind only its sentinel so c6 stays
clean; no hold lifted, PR #241 unmerged). HTML entities transport-decoded. Verdict:
**PASS — all 20 rows SATISFIED**.

---

## (1) Frozen-head confirmation

`git rev-parse HEAD` = **`a7cc175759f86dcbb3fcf5ac4ff6e64bfbf373fc`** — CONFIRMED on branch
`candidate/D-024-mrl-option-b`. Working tree carries only agent-memory/scratchpad noise;
every wave control-plane record is committed at HEAD. Primary checkout inspected directly.

**Independent reproduction (primary, not producer claims):**
- `cd services/api && python -m pytest tests/connectors/test_dcm_street_width_policy.py -q`
  → **94 passed** (0.16s). Matches the expected post-F1 count.
- `cd services/api && python -m ruff check .` → **All checks passed! (EXIT 0)**.
- `python tools/validate_directive_compliance.py --check` → **EXIT 0**.
- `python tools/test_project_control.py` → all 23 groups passed.
  `python tools/test_directive_reminder.py` → 12 tests OK.
- `python tools/test_directive_compliance.py` did NOT finish in-session (>25 min
  subprocess-heavy runtime on Windows). Environmental runtime limit, not a failure, and not
  the primary evidence for any requirement — the load-bearing registry-integrity check
  passed clean. No requirement rendered UNVERIFIABLE by it.

**Material identity (git diff, byte-level):** policy module byte-identical a6c73ec0→a7cc1757;
test file byte-identical 42e57a6a→a7cc1757 (F1 correction is the last edit); T018 report
byte-identical 00b28626→a7cc1757; accepted classifier byte-unchanged 8538c272→a7cc1757.
Post-integration commits touch only project-control/directive records (+ the allowed F1
test-file edit in 42e57a6a). `git diff 293d6c03..a7cc1757` over services/api/app/rules,
docs/research/zr-snapshots, pyproject.toml, uv.lock, package-lock.json, tools, .github,
apps, packages is **empty**. The interleaved D-053 capture (fef69aae) is
directive-registry-only and touches neither task's allowed_paths.

## (2) Per-requirement verdicts (all SATISFIED; evidence reproduced independently)

### M4-T018 (research)
- **D-045-R002** — build inputs specified WITH their data needs and honest gaps ("No
  accepted connector computes 'average width of a portion'…") — no manufactured numbers.
  (report §3.1, §3.2, §5)
- **D-045-R008** — one bounded gated research task (G0→G1). (packet; gate records)
- **D-045-R009** — coverage-scope-only: one file changed; snapshot/rules/deps byte-unchanged;
  DRAFT posture preserved; conflict routed, not adjudicated. (wave diff; report §2.3–2.4)
- **D-046-R001** — parallel dispatch with T019 into isolated worktrees pinned to 293d6c03.
  (commit 9e89497a; progress logs)
- **D-046-R002** — allowed_paths provably disjoint from T019. (both packets)
- **D-051-R001** — every negative bounded to named sources; Allen St demapping flagged as
  unverified lead only. (report §0-S4, §2.4, §4)
- Capture provenance checked: sha256 4a75e22f… (1,316,658 bytes), print/PDF 504 disclosed,
  amendment date 3/26/2026 read from the term's own time element — consistent with the G1
  capture-review's byte-exact reproduction.

### M4-T019 (build)
- **D-052-R001** — WIDE_THRESHOLD_FT=75.0; exactly 75 = wide; precondition gate (incl.
  exceptions_checked) runs BEFORE thresholding → UNRESOLVED, never silently thresholded.
  (module L200/211-237/337-402; tests L61-72, L171-178; 94 passed)
- **D-052-R002** — AttestedPreconditions frozen, NO defaults; nearest_centerline_only AND
  unrecognized methods → refusal; assumption wording only on issued classifications,
  "never a verified NYC DCP guarantee". (module L94-96/105-111/337-364/445-464; tests)
- **D-052-R003** — one-sided-bound gate; straddling → UNRESOLVED, no endpoint pick; all 7
  owner literals pass verbatim + structural property test. (module L424-443; tests L80-108)
- **D-052-R004** — approximations/unrecognized/conflicting → UNKNOWN routed to map
  resolution; module performs NO arithmetic on bounds; negative test per forbidden move.
- **D-052-R005** — provenance quintuple preserved, present on refusals; UNKNOWN records
  routed_to=map_resolution. (module L162-185/391-464; tests L259-279)
- **D-052-R006** — UNKNOWN first-class and distinct from narrow despite the classifier's
  narrow_fail_closed disposition; no consuming rule wired; no fallback. (test L311-322)
- **D-052-R007** — DRAFT label always populated; tests cover thresholds/ranges/frontage/
  exceptions; G4 confirmed adequacy.
- **D-051-R002** — raw text + ambiguity_class preserved end-to-end; unknown never presented
  as verified narrow.
- **D-051-R003** — module emits data states only; imports/wires no rule; per-rule fallback
  separation clean (deferred to B7 per R006).
- **D-045-R002** — consumes the accepted classifier output; honest UNKNOWN/UNRESOLVED where
  inputs insufficient — never a guessed number.
- **D-045-R008** — single bounded feature task (G0/G3/G4).
- **D-045-R009** — two new files only; classifier byte-unchanged; DRAFT intact; no
  dep/rule/snapshot change.
- **D-046-R001 / D-046-R002** — parallel dispatch; disjoint scopes.

**c6 selective-citation:** only D-045/D-046/D-051/D-052 reference these task ids; computed
applicable sets match cited exactly for both tasks. **D-053 has zero requirements applicable
to either task** (all rows scope to its sentinel) — c6 CLEAN including D-053.

**Gate independence:** T018-G1 data-contract-verifier (producer official-source-researcher);
T019-G3 code-reviewer + G4 qa-engineer (producer backend-engineer). G3/G4 reviewed_sha
fef69aae — material there byte-identical to HEAD, reviewed content identity preserved. The
ORCH-CORRECTED F1 test (per-field default-is-MISSING assertions) genuinely catches mutation
M6 (a defaulted field would set field.default=True ≠ MISSING) — present + passing at HEAD.

## (3) Control-plane discrepancies

No violating discrepancies. Two benign notes: (1) commit 42e57a6a combines the allowed
T019 test-file edit with control-plane records — the orchestrator's ORCH-CORRECTED
application, legitimate under ADR-005 (orchestrator owns both surfaces), not a
producer-scope breach; (2) the 60% progress entry says "93 policy tests" — post-F1 count is
94, expected (F1 added one test). Prohibited-action evidence: both tasks awaiting_gate (NOT
accepted) at review time; no auto-accept/merge/deploy/install/purchase/close in any wave
commit; **PR #241 OPEN, mergedAt=null** (title still "DO NOT MERGE until owner authorizes");
no hold lifted; D-053 capture activates no live actuation (R595 stays shadow).

## (4) Conditional restamp pre-authorization

Restamp reviewed_sha from a7cc1757 to a later commit C iff, verified at C: (1) material
byte-identity — empty diff for the three material files, classifier unchanged vs 8538c272;
(2) cited-directive requirements.json (D-045/D-046/D-051/D-052) byte-identical; (3′) no
prohibited surface in a7cc1757..C and no requirement becomes applicable-but-uncited for
these tasks (re-run applicable==cited incl. any new directives); (4) no hold lifted, PR
#241 unmerged, no out-of-scope accept/merge/deploy/close. If all four hold, the §2 verdicts
carry unchanged to C (control-plane-only advance, e.g. verification.json recording or a
further disjoint-directive capture). [Orchestrator: all four verified TRUE at C=d752c09b —
see header.]

## Overall verdict: **PASS**

All 6 M4-T018 rows and all 14 M4-T019 rows SATISFIED on reproduced primary evidence. Zero
VIOLATED, zero UNVERIFIABLE. Material identity, classifier immutability, disjointness,
c6-completeness (incl. D-053), gate independence, DRAFT posture, and prohibited-action
absence all confirmed. The orchestrator may record this result after validating it; the
verifier wrote nothing.
