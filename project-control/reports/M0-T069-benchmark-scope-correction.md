# M0-T069 benchmark — scope correction / evidence record (M0-T075, D-018-R007)

Recorded by the orchestrator under D-018. This is a FOLLOW-UP record: it does
NOT reopen M0-T069, does not alter its historical review or verification
records, and does not dispute its results.

## What M0-T069's 42-case benchmark actually proved (and still proves)

The accepted Unit F benchmark (`M0-T069-benchmark-report.json`, 42 cases,
all byte-identical) is an **INDEX-PARITY benchmark**: it proves that the
incremental A1/A2 **index** — across the five task shapes and the change
classes (cold/warm, one-file, dependency, config, rename, delete, corrupt
cache, interrupted write, concurrent writer) — produces export bytes
identical to a clean full rebuild by the unmodified builder, with warm
zero-reparse, no stale nodes, and recovery validity. That result was true,
independently re-executed by the M0-T069 reviewer, and remains green after
M0-T075 (the extended benchmark retains the cases; the parity suite runs in
permanent CI).

## What it did NOT cover (the honest scope limit)

It did **not** invoke the context COMPILER end-to-end: no case compiled a
task packet through `context_pack.py`, so it proved nothing about
requirement-text inclusion, source-excerpt reopening, graph seeding from
task scope, role sufficiency, or compiler determinism. Its "benchmarks the
pipeline" framing in the D-017 close-out overstated that scope; the
projection/report language now says "index-parity benchmark" explicitly.

## What closes the gap

M0-T075 added the END-TO-END benchmark
(`M0-T075-e2e-benchmark-report.{json,md}`): the same five frozen shapes now
invoke the ACTUAL integrated compiler (same task packet, diff base, role,
provider/model, reasoning setting, source snapshot), proving cold/warm
byte-identical packets, global-budget compliance or nonzero split refusal,
required-evidence completeness (including exact requirement texts
end-to-end), exact provenance, resolved graph/source evidence, honest
advisory-memory handling, and representative-task correctness no worse than
the pre-change G0 baseline (`M0-T075-baseline-g0.json`). A distinct
parser-version case, actual lock-refusal and orphan-quarantine pass
predicates, and the corrected nearest-rank p95 were folded into the extended
index benchmark at the same time.

M0-T069's records stand unchanged; this note is the scope clarification the
owner directed (D-018 paragraph 3).
