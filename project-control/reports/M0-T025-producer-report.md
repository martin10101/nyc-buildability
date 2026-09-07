# M0-T025 — Producer report / G2 self-check (supervised-loop-fable-worker)

Control-plane hardening for the LOW-1 review finding (`project-control/reports/M0-T024-LOW-1.md`,
preserved under D-002 §2): the directive manifest's `requirements_file` / `verification_file`
references are now explicitly path-contained to the directive's own directory. The change only
narrows what is accepted — every rejection takes the same fail-closed route as a missing file —
and never loosens existing behavior.

Worktree `wt-m0t025`, branch `task/M0-T025-path-containment`, base `29f9ee7b` (certified-candidate
lineage `e0dd4a3a`). Files touched (all inside the packet's allowed paths):

| File | Change |
|---|---|
| `tools/directive_registry.py` | New shared guard `resolve_contained_ref(base_dir, ref)`; registry loader resolves both manifest references through it and records a containment error instead of loading an escaping file |
| `tools/validate_directive_compliance.py` | c14 body-digest path resolves `requirements_file` through the same shared guard; a rejected reference reports `c2 [D-xxx] requirements_file containment: …` and the digest is never computed over an out-of-directory file |
| `tools/test_directive_compliance.py` | New `PathContainmentTests` class: guard unit tests + AS-1 negative validator/registry tests + AS-2 positive no-regression test |

## Design

One guard, two consumers — `resolve_contained_ref` is defined once in `tools/directive_registry.py`
and used by both the registry loader and the standalone validator, so the two sides can never
diverge on what "contained" means. Rejection classes, each with a clear human-readable reason:

1. non-string or empty reference (`must be a non-empty string`);
2. absolute / drive-rooted / rooted reference (`absolute file reference … is rejected`), covering
   POSIX `/rooted`, Windows `C:\…`, and bare-root `\…` forms via `is_absolute() or drive or root`;
3. `..` traversal anywhere in the path parts (`contains '..' traversal`);
4. residual escapes (symlinks, redundant separators) caught by the final `_within()` resolve
   check (`resolves outside the directive's own directory`).

Fail-closed equivalence: a rejected reference appends a directive error and leaves the record
unloaded — exactly the missing-file route. Consequences chain unchanged: `Directive.is_active`
→ `False`, `evaluate_task_refs` → invalid ref (`integrity errors; fail closed`), `accept()`
refuses the task, and the validator exits non-zero. Nothing is silently trusted.

The LOW-1 caveat still holds and is preserved in the guard's docstring: these references are
trusted, checked-in registry data authored by the orchestrator — this is defense-in-depth
hardening, not input sanitization of attacker-controlled data.

## Acceptance-scenario self-check (G2)

| Scenario | Verdict | Evidence |
|---|---|---|
| AS-1 escaping reference REJECTED with clear containment error | PASS | `test_as1_requirements_file_traversal_rejected` (`../../…` → `requirements_file containment` + `'..' traversal`); `test_as1_verification_file_absolute_path_rejected` (absolute path → `verification_file containment` + `absolute file reference`); in both, the escaping target file EXISTS and is byte-identical to the real one, so the only defect is the escaping reference itself |
| AS-1 fail-closed | PASS | `test_as1_registry_fails_closed_on_escaping_ref`: escaping ref → directive error recorded, `requirements == {}` (never loaded), `is_active is False`, `evaluate_task_refs` → `ok: False` with `integrity errors` invalid ref |
| AS-2 in-directory references PASS unchanged | PASS | `test_as2_in_directory_refs_still_pass` (fixture copy of the real 30-directive registry validates to `[]`, every directive loads error-free); suite-level regression: `PositiveTests.test_real_registry_valid` still green; guard unit tests `test_guard_accepts_plain_and_nested_relative_refs` / `test_guard_rejects_traversal_absolute_and_malformed_refs` |
| AS-3 evidence in this report | PASS | this file (G0/G2/G3/G4/G5 sections below) |

## Documented commands (exact, G2/G4 evidence)

Run on Windows 11 in worktree `wt-m0t025` against the working tree at base `29f9ee7b` with the
M0-T025 edits applied. The unit's command broker permits only read-only git, so the commit that
freezes this content is executed by the orchestrator (ADR-005 authority) after this unit:

- `python -m pytest tools/test_directive_compliance.py -q` → **126 passed in 1720.41s
  (0:28:40), exit 0** (revision-unit run, 2026-09-06: full suite green including the six new
  `PathContainmentTests` and every pre-existing c1..c17 adversarial case). NOTE: this run
  predates the lint rider below; the 2026-09-06 loop unit's broker permits only the three
  loop-packet commands, so the post-rider full-suite re-run is deferred to the G3/G4
  reviewers (rider changes are lint-mechanical; see "Lint rider").
- `python tools/validate_directive_compliance.py --check` → **exit 0, no errors** (re-confirmed
  2026-09-06 loop unit, post-rider tree: the real committed 30-directive registry validates
  clean through the new containment guard — the repository-level AS-2 no-regression proof).
- `python -m pytest tools/test_directive_compliance.py -k test_real_registry_valid -q`
  (loop-packet subset) → **1 passed, 125 deselected in 76.89s, exit 0** (2026-09-06 loop
  unit, post-rider tree).
- `python -m ruff check tools/directive_registry.py tools/validate_directive_compliance.py
  tools/test_directive_compliance.py` → **"All checks passed!", exit 0** (2026-09-06 loop
  unit, post-rider tree; was exit 1 with 11 pre-existing findings before the rider).

## Lint rider (2026-09-06 loop unit; zero behavior change)

The loop packet added a documented ruff command over the three task files; it failed with 11
findings, all in pre-existing code OUTSIDE the containment diff (registry `_hash_manifest_entries`
hashing loop ~1341; older test classes). All were fixed mechanically inside the packet's allowed
paths:

- E702 ×7: semicolon-joined statements split onto separate lines (`directive_registry.py`
  `_hash_manifest_entries`; `test_directive_compliance.py` `test_r147_lf_crlf...` `_git` calls).
  Byte-identical hashing semantics — statement order unchanged.
- E741 ×2: `_section_lines` loop variable `l` → `line` (rename only).
- F841 `reg` (test_r141): assignment dropped, fixture-building `self._reg(...)` call KEPT (the
  following `vdc.validate` depends on its side effect).
- F841 `m2` (test_manifest_is_order_independent_and_content_based): the dead assignment is now
  the assertion the comment always described — `assertEqual(m2, m1)` (same file set via a
  directory spec vs an explicit file list → same identity). The property holds by construction:
  `content_manifest` resolves both specs to the same sorted, deduplicated
  (relpath, content-hash) entries before hashing (its docstring: "retained only for legacy
  order-independence tests"). This is the one rider line that strengthens a test rather than
  reformatting; it was not executed in this unit (broker limits above) and is flagged for the
  G3 reviewer's full-suite re-run.

## Gate evidence map

- **G0 (definition-of-ready)** — recorded by the orchestrator before claim:
  `project-control/reports/M0-T025-G0-readiness.md` (PASS, 2026-09-06).
- **G2 (producer self-check)** — this report: scenario table + exact commands above.
- **G3 (independent walkthrough)** — reviewer script: (a) read the LOW-1 required disposition,
  (b) confirm the guard is the single containment authority for both consumers
  (`tools/directive_registry.py` `resolve_contained_ref`, loader loop over
  `requirements_file`/`verification_file`; validator c14 resolution), (c) re-run the two
  documented commands, (d) adversarial spot-check: point a fixture manifest's reference at
  `../…` or an absolute path and observe the containment error and non-zero validator exit.
- **G4 (integration/regression)** — the full 126-test directive-compliance suite passes
  (includes every pre-existing c1..c17 adversarial case) and the real committed registry still
  validates clean (`--check` exit 0): no behavior change for well-formed registries; the change
  is additive narrowing only. No product/runtime code touched (forbidden paths untouched).
- **G5 (security/privacy)** — the finding is itself a security hardening: path containment on
  registry file references. No new I/O, no network, no secrets, no new dependencies; rejection
  messages contain only the offending reference string (already checked-in data). The guard
  rejects before any file read, so an escaping reference is never opened. Residual risk: none
  identified beyond the pre-existing trusted-input posture documented in LOW-1.

## Constraints honored

- Scope: only the four allowed paths were modified; forbidden paths (product/runtime code,
  `.claude/**`, other directives' records, D-002 registry sources) untouched.
- Append-only registry law untouched: no committed `source-*.md`, manifest, or requirement
  record was edited; the change is code + tests + this report.
- Modularity: no new module; `directive_registry.py` grew by ~24 lines inside its cohesive
  responsibility (registry integrity), `validate_directive_compliance.py` by ~8; the shared
  guard avoids duplicating containment logic across the two files.
- Producer ≠ verifier: this report is producer evidence only; independent reviewers
  (code-reviewer, control-plane-verifier, security-reviewer, directive-compliance-verifier)
  gate it, and the orchestrator alone records gates and acceptance.

## Known limits (honest)

- `resolve_contained_ref` guards the two manifest file references named by LOW-1; other
  registry-internal path values (e.g. source `file` entries) keep their pre-existing handling
  (digest-verified against the manifest), unchanged by design — LOW-1's required disposition
  names exactly `requirements_file`/`verification_file`.
- On a traversal `requirements_file` the validator now emits both the loader-side and the
  c14-side containment error (two lines for one defect). Harmless duplication; kept because
  each consumer must fail closed independently.
- The documented pytest run is slow (~each fixture test copies the full 7.7 MB / 265-file real
  registry); pre-existing suite characteristic, not introduced here.

## Handoff to orchestrator (2026-09-07 loop unit)

Producer work is complete; this unit changed no code and re-ran no commands. Per the forwarded
packet instruction, the three loop-packet commands were **not** repeated — no new change or
failure since their 2026-09-06 PASS results warranted a re-run (the only edit this unit is this
report section).

**Result provenance — preserve this distinction at gate time:**

| Provenance | Result | Tree |
|---|---|---|
| Current, supervisor-confirmed (2026-09-06 loop unit) | loop-packet pytest subset `-k test_real_registry_valid` → 1 passed, exit 0; `validate_directive_compliance.py --check` → exit 0; ruff over the three task files → "All checks passed!", exit 0 | post-rider |
| Historical, producer-only (2026-09-06 revision unit) | full `python -m pytest tools/test_directive_compliance.py -q` → 126 passed, exit 0 | **pre**-rider |

The historical full-suite PASS predates the lint rider and must not be substituted for the
mandatory full-suite run on the frozen candidate (packet note: the FULL suite is an orchestrator
gate-wave step before acceptance). In particular, the one strengthened rider assertion
(`test_manifest_is_order_independent_and_content_based` → `assertEqual(m2, m1)`) has never been
executed on the post-rider tree.

**Orchestrator actions pending at handoff (none performed by this producer; ADR-005 authority):**

1. **Reconcile ownership of the uncommitted `project-control/tasks/M0-T025.json` edit** sitting
   in this worktree (the 2026-09-07 orchestrator note trimming documented commands to the fast
   loop subset). That path is outside this producer's `allowed_paths` and the edit is
   orchestrator-authored control-plane state; the orchestrator must claim and dispose of it under
   its own authority **before freezing candidate scope**, so the frozen producer diff contains
   exactly the four allowed paths.
2. Commit/freeze the candidate (the four allowed-path files) and stamp the frozen SHA.
3. Run the mandatory full directive-compliance suite (`python -m pytest
   tools/test_directive_compliance.py -q`, ~27 min) on the frozen candidate; its result
   supersedes the historical pre-rider 126-pass as the authoritative full-suite evidence.
4. Dispatch the required independent gate reviews (G3/G4/G5 + directive-compliance verification)
   to the packet's four reviewers (code-reviewer, control-plane-verifier, security-reviewer,
   directive-compliance-verifier); producer ≠ reviewer.
5. Record gates, submit, and accept — orchestrator-only.

Resulting suite/gate evidence will be recorded here or in the gate reports once it exists; as of
this handoff none of steps 1–5 has been executed.
