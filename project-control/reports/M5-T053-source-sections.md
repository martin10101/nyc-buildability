# M5-T053 source-sections index (frozen submission identity)

Material: commit `d0e854c1bc941c100652d1896b7229d27e8f17d3` (task branch, run 57 through six
revision rounds, orchestrator-committed at the breaker close) → cherry-pick
`25617bbdc4a3c71d915f71ac81f0aa7dc24fd22a` on candidate/D-024-mrl-option-b.
CI at that head: run **35454834946**, ALL jobs success (0 non-success) —
M5-T053-ci-evidence.md.

SHA-256 digests are LF-normalized (CRLF→LF before hashing), pasted verbatim. (Computed at
the current head after the disjoint M5-T051 cherry-pick f1ec64a8 — which touches none of
these five paths; byte-stability from 25617bbd is the reviewers' empty-diff check.)

| sha256 (LF-normalized) | file |
|---|---|
| `af1de9339272ce9201fb808ff7885045fa912773fbaf90af6607524481d6ff39` | services/api/app/scenario/proposal_input_gate.py (DB-034(a) global vertex budget counted BEFORE quadratic work; DB-034(b) string ceilings + bounded-repr; monotone wrapper over the accepted validator, read-only) |
| `3beb5b8d7e6b576bc262668b0d87fd5ae53ee14500989311318d9136c942ac79` | services/api/app/api/v1/proposal_validation.py (stateless POST: bounded body, strict-JSON NaN/Inf refusal, typed refusals verbatim, acceptance echo with ZERO derived values) |
| `3bc3d9974a6542fd4ab68c494e2d86b91b7b313542af45994ff388c9d9b13b3d` | services/api/app/main.py (the one mount line added on top of the accepted T052 state) |
| `eaea6f99b8f5d2fe1be924ef36166c084cc7df3f50a5893699882b9458cb1aa2` | services/api/tests/api/test_proposal_validation_api.py (43 tests: budget/ceiling boundaries incl. the many-levels probe, bounded-repr echo, oversized body, non-finite, B0-fixture passthrough, monotone-gate property) |
| `ad2442cf0878a7960a899e734f60cd4d8271498e39939ea463dce7fd47df02c0` | project-control/reports/M5-T053-producer-report.md (producer evidence, verbatim from the worktree; notable for its honest carry-forward-unverified stance and real captured transcripts) |

Orchestrator reproduced at harvest (wt-m5t053, documented cwds): ruff clean; pytest
tests/api/test_proposal_validation_api.py 43 passed; tests/api 497 passed; modularity
exit 0. The DISJOINTNESS design (the wrapper gate module instead of editing proposal.py,
which the then-live M5-T051 lane owned) held: proposal.py and tests/scenario/ are absent
from the material commit.
