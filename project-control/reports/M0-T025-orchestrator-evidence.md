# M0-T025 — orchestrator-captured gate-wave evidence (2026-09-07)

Captured by the orchestrator (session_01WBbzN5Rx17CBSjky5uKmnY) under the
evidence-capture division of labor (.claude/rules/project-control.md): reviewers
verify this stored evidence; they do not need to re-execute the slow commands.

## Identity

- Frozen producer candidate: `20f7651c` (`task/M0-T025-path-containment`, wt-m0t025)
- Merged into `candidate/D-024-mrl-option-b` at: `56db6a17` (merge commit; the four
  allowed-path blobs are identical between the two)
- Producer: supervised-loop-fable-worker via supervisor run `persistent-local-06`
  (astra verdict COMPLETE, checkpoint `M0-T025-persistent-local-06-u01-cp1`,
  audit seq 45-53)
- Submission: awaiting_gate at reviewed sha `56db6a17`, evidence map
  `M0-T025-evidence-map.json` (applicable set empty)

## Command evidence at the frozen candidate (wt-m0t025 @ 20f7651c, 2026-09-07 ~04:42Z)

| Command | Result |
|---|---|
| `python tools/validate_directive_compliance.py --check` | exit 0 (quiet success; real 30-directive registry validates through the new containment guard) |
| `python -m ruff check tools/directive_registry.py tools/validate_directive_compliance.py tools/test_directive_compliance.py` | "All checks passed!", exit 0 |
| `python tools/modularity_check.py --check` | exit 0 — "selected 354 files; failures 0; warnings 12" (all 12 warnings pre-existing files outside this diff) |
| `python -m pytest tools/test_directive_compliance.py -q` (full ~27-min suite) | RUNNING at the frozen tree; log will be committed as `M0-T025-full-suite-20f7651c.log` with the exit code appended; G4 dispatches only after this lands |

## Provenance note (from the producer report, preserved)

The historical full-suite 126-pass predates the lint rider; the run above at
`20f7651c` is the authoritative full-suite evidence, and it is the first
execution of the strengthened rider assertion
(`test_manifest_is_order_independent_and_content_based` -> `assertEqual(m2, m1)`)
on the post-rider tree.
