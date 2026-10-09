# M5-T050 source-sections index (frozen submission identity)

Material: commit `939da50b9788051cc63739f1653c3678bdda1523` (task branch, run 54 build,
orchestrator-committed) → cherry-pick `bcfcc538c734da2f1c763f3351fb1fcc984518a1` on
candidate/D-024-mrl-option-b. CI at the covering head 499ae642: run 35440808156, ALL jobs
success — the authoritative web proof for riders a–e/h/i (M5-T050-ci-evidence.md).

SHA-256 digests are LF-normalized (CRLF→LF before hashing), pasted verbatim from the tool
output.

| sha256 (LF-normalized) | file |
|---|---|
| `89f464210e4b95cf15a95f19e3b8d2284b83c5e04a3f90f6d66837cbe9a3982f` | services/api/app/api/v1/lot_geometry.py (rider f: docstring names the record-address channel — comment-only diff) |
| `26e926f2dd36d1d6a98937ee8f9987990eacc5e36d3b0b6fe70afa107a9cc253` | services/api/tests/api/test_lot_geometry_api.py (rider g: binding RA-3 reason assertion) |
| `2ae949d5c42c001fa6badcc15f2b5c3520487baf6719f85d59287a58152a5153` | apps/web/src/components/address/AddressConfirmCard.tsx (riders a/b/c/d/i: last-child record note, aria raw-value exposure, conditional entered-note, why-they-differ note, title-attr bound) |
| `8a87c7559c1881d6b7647b5c9839df580b2f9f69122bed875be974c2cc29c7db` | apps/web/src/components/address/__tests__/address-confirm.test.tsx (S11 rider groups incl. the structural pure-append CLS proof) |
| `a95c1a223fdc177ee7413f8b01ac8f6ee3bbbc57cbb015cd1707758eb4c82ca8` | apps/web/src/lib/record-address.ts (riders h/i: 6/6 typed error states, credentials omit, 422 json-safety parity, bounded message) |
| `0313417ba0a52da68430fdd030a11f675a93ddb5ee9ff5e901b48e5d36fe9731` | apps/web/src/lib/__tests__/record-address.test.ts |
| `2d3b6ecf256723d8eefdde09a5b8592498ceb3ba197f55c2009f5fd02b9ab678` | apps/web/src/lib/address-search.ts (UNCHANGED from M5-T047 accepted state — rider e proved test-side only; in the index because it is an allowed_path the reviewers must confirm untouched) |
| `46b5c6782369f4c179c565633d07ac241b1caab7290ebd48bb9b21f002dfb93c` | apps/web/src/lib/__tests__/address-search.test.ts (rider e: de-vacuated length-bound tests, non-empty features, exact-512 boundary) |
| `837ea0aa17a03ff850cd48becbbc8d0b08ed684821b40de56d43962aa8120bda` | project-control/reports/M5-T050-producer-report.md (producer evidence, verbatim from the worktree) |

Orchestrator reproduced before commit (in wt-m5t050): ruff clean; pytest
tests/api/test_lot_geometry_api.py 33 passed; tests/api 439 passed; modularity exit 0.
Web behavior proves ONLY in CI: run 35440808156 (web + web-e2e jobs success at 499ae642).

Producer-flagged reviewer items (report §Honest limitations): (1) jsdom asserts the
STRUCTURAL CLS mechanism (pure append below all settled elements), not pixels — the
real-browser pixel measurement needs an e2e spec OUTSIDE this packet's allowed_paths
(routed to the orchestrator, deliberately not edited in-packet); (2) the record note
now renders as the card's LAST element (below actions + footer) — a reading-order/IA
tradeoff the journey reviewer must explicitly weigh.
