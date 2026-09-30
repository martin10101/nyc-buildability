---
name: static-mutation-review-thin-client
description: G4 test-adequacy method for web packets on this thin client (no node_modules) - paper mutation table + red-on-old verification via git show at the pinned head
metadata:
  type: project
---

On this repo's thin client there is NO node_modules, so a G4 reviewer cannot run vitest; CI (web + web-e2e) on the pushed head is the executable authority.
**Why:** owner storage policy (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md); every producer since M5-T023 discloses the same limit.
**How to apply:** review STATICALLY at the pinned sha via `git show <sha>:<path>` (checkout HEAD often differs). Method that worked for M5-T025:
- Build a paper mutation table per key behavior (drop validation, swap reflected string into href, revert constant, remove guard/handler) and name the exact test line that goes red; a self-referential assertion (`toBe(CONST)`) is theater unless paired with an absolute pin (`toBeGreaterThan(18)` / exact literal).
- For "red-on-old" regression-guard claims, diff the OLD component and OLD test mock at the contract head: distinguish (a) trivially red (new exports missing → import failure), (b) mock-semantics red (new mock drops old event path), and (c) the discriminating behavioral case — e.g. old wiring re-added WITH the new exports (once("load") without an isStyleLoaded check) must still fail some test; that test is the load-bearing one.
- Check test-fixture factories deep-clone (structuredClone) before trusting per-test mutation isolation.
- Verify the commit's parent vs the stated contract head: if the material files are byte-identical between them, the "old" baseline claims hold even when other commits interleave.
- Verdict PASS is conditioned on CI green at the reviewed sha; that is the packet's own documented_test_commands authority, not a producer correction.
- **Identity-carry attestation ("does your PASS carry to the corrected head?")**: never accept "comment-only" on description. Prove it — dump both revisions of each file in your surface with `git show <sha>:<path> > scratchpad/x`, strip comments with a string-literal-aware stripper, and compare sha256 of the code-only text (script pattern: scratchpad/strip_comments.py). Identical code-only digests + `git diff --stat` showing the other surface files untouched = adequacy carries. Also confirm the web CI lint config has no max-len/prettier check, since comment-only edits CAN break lint where one exists (apps/web/eslint.config.mjs = next/core-web-vitals + next/typescript only: no line-length rule).
