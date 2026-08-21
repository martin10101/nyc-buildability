# D-023 campaign findings pool (for the single consolidated correction round)

Per D-023-R016/R017 (complete the investigation, then ONE consolidated correction — no
drip-feeding), every non-blocking finding from per-task gates accumulates HERE and is
addressed once, at M0-T085, against the frozen campaign identity. Must-fix findings block
their own task's gate immediately and never wait for this pool.

Severity vocabulary: docs/ENGINEERING_RELIABILITY_STANDARD.md §9.

## Open findings

| # | Source | Severity | Location | Finding (condensed; verbatim in source report) |
|---|---|---|---|---|
| F-001 | M0-T078 G3 | minor | M0-T078-producer-report.md AS-6 | Digest block mixes CRLF/LF encodings; state normalization or use git hash-object (no drift — verified). |
| F-002 | M0-T078 G3 | minor | ENGINEERING_RELIABILITY_STANDARD.md §7.1 (also §8.6, §8.9) | Near-verbatim restatement of LEAN B5 / G4 list / principle 7 despite §0's no-copy rule; cite instead. |
| F-003 | M0-T078 G3 | minor | ENGINEERING_RELIABILITY_STANDARD.md §6.5 | Add one-clause cross-reference to the existing single retry layer (services/api/app/resilience/, M2-T011) to prevent a second retry layer. |
| F-004 | M0-T078 G3 | minor | M0-T078-producer-report.md §1 | Report prose says "five invocation triggers"; frontmatter names seven. Deliverable correct. |
| F-005 | M0-T078 G5 | minor | ENGINEERING_RELIABILITY_STANDARD.md §9.2 | "Unexplained severity is downgraded when challenged" names no adjudicator; name the reviewer of record or the gate, never the producer. |
| F-006 | M0-T078 G5 | minor | ENGINEERING_RELIABILITY_STANDARD.md §9.1 | Phrasing could be cited against defense-in-depth G5 findings; clarify that a named plausible mechanism suffices for security findings. |

## Resolved findings

(none yet)
