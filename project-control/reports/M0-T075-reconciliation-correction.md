# M0-T075 e2e "no-worse" result — honest reconciliation (M0-T076 / D-019-R005)

**Status: historical correction only. No M0-T075 record is reopened, disputed, or
rewritten.** This note is analogous to `M0-T069-benchmark-scope-correction.md`: it
states precisely what an accepted result did and did not demonstrate, so the ledger
stays honest without altering accepted history.

## What M0-T075 recorded

M0-T075 (PR #238, accepted at reviewed SHA `db82e0a`, merged `3c10894`) captured a
G0 baseline at `project-control/reports/M0-T075-baseline-g0.json` and recorded an
end-to-end "no worse than baseline" comparison as PASS.

## What was actually true (independently reproduced, 2026-08-19)

Running the exact documented M0-T075 e2e command from a **clean checkout of merged
main** (`3c10894`) EXITS 2, not 0:

```
python tools/context_benchmark.py --e2e \
  --baseline project-control/reports/M0-T075-baseline-g0.json ...
# -> exit 2; baseline_comparison.no_worse_than_baseline = false
#    baseline_sources_missing_now = ["git_diff"]  (for M0-T066 and M0-T067)
```

Cause: the M0-T075 baseline was captured while the control-plane working tree was
**dirty**, so it recorded a `git_diff` source. A clean checkout has no working-tree
diff, so that `git_diff` source id is "missing now" and the source-id-membership
predicate fails. The committed "no-worse" PASS was therefore an **artifact of the
dirty capture state**, and the comparison measured **source-id set membership**, not
meaningful required evidence.

This does not mean M0-T075's compiler is wrong: its shape checks (cold/warm
determinism, budget-or-split, provenance, resolved graph/source evidence,
requirement texts) reproduce cleanly. Only the *baseline comparison* was
state-dependent and count-based.

## What M0-T076 changed (no M0-T075 record touched)

- A NEW, clean-captured, state-invariant baseline lives at
  `project-control/reports/M0-T076-baseline-g0.json`
  (schema `context_benchmark_e2e_baseline/v1`). M0-T075's baseline file is
  **unmodified**.
- The e2e comparison now measures each frozen hermetic shape's **required-evidence
  + relevance fingerprint** (sufficiency, exit, requirement ids/texts, resolved
  graph/source evidence, ontology, advisory-memory handling) — never a
  working-tree-diff source-id count.
- The exact documented command
  (`--e2e --baseline project-control/reports/M0-T076-baseline-g0.json`) exits `0`
  from independent clean checkouts and runs in permanent CI (`context-pipeline`).

The M0-T075 acceptance, gates, and PR stand exactly as recorded; this is scope
honesty, not a reopening.
