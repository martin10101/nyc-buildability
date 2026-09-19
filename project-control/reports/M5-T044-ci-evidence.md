# M5-T044 — CI evidence at the combined harvest head (orchestrator-captured)

Captured 2026-09-19 (seq-118). Material `1fd07e9a` (cherry-pick of worktree `36a510b4`;
3 files, +583/-37) is the branch tip's parent; the pushed head `a380a956` adds only
control-plane bookkeeping (`git diff 1fd07e9a..a380a956 -- apps/ services/ packages/` is
empty). The head also carries the DISJOINT M5-T043 material `f6e88222` (rules/spatial/web
display files — zero path overlap with M5-T044). All three workflows completed **success**
at `a380a956` (AS-8):

| Workflow | Run id | Conclusion |
|---|---|---|
| CI (api job runs the connectors suite) | 35412920210 | success |
| secret-scan | 35412920196 | success |
| context-budget | 35412920224 | success |

- Local proofs orchestrator-reproduced in `wt-m5t044` at harvest: ruff clean; 54 passed
  (connector suite, up from 26); 880 passed connectors-wide (no regression, leaf isolation);
  modularity exit 0 from the repo root.
- The producer's report distinguishes worker-run working-tree validation from
  orchestrator-captured committed-head evidence and records the deliberate (j) $limit
  deferral per D-069.

## Addendum — corrected-head CI (orchestrator-captured, 2026-09-19)

After the [ORCH-CORRECTED per M5-T044-G3 F1] correction `a471e376` and the resubmission at
`0438a9ae`, the pushed head `880a154d` (resubmission bookkeeping only; the two code files
byte-identical to `a471e376`) ran all three workflows to **success**: CI 35414107043,
secret-scan and context-budget alongside it. All four reviewers delta-attested
CARRIES/EXTENDED on the corrected identity (project-control/reports/
M5-T044-delta-attestations.md); orchestrator local reproduction at the correction: ruff
clean, 55 passed, 881 connectors-wide.
