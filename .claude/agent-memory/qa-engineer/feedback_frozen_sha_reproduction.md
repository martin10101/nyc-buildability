---
name: frozen-sha-reproduction
description: How a read-only G4 reviewer reproduces a leaf-connector suite + runs a mutation probe at a frozen SHA without any git write
metadata:
  type: feedback
---

As a read-only gate reviewer you CAN independently reproduce tests at the frozen material SHA without checking out or `git worktree add` (both are writes). Method that worked on M5-T044 (api connector, module absent at worktree HEAD):

1. `git archive <material_sha> services/api packages | tar -x -C <scratchpad>/repo_at_material` — read-only, materializes the frozen tree. If a test reads cross-package files (e.g. `packages/contracts/schemas/v1/*.json`), archive `packages` too or you get a spurious FileNotFoundError "error" (that is your extraction gap, NOT a defect — I saw 879 passed + 1 error become 880 passed after adding `packages`).
2. Confirm identity: `git show <sha>:<path> | tr -d '\r' | sha256sum` must equal `tr -d '\r' < <extracted path> | sha256sum` (LF-normalize; checkout CRLF smudges raw digests).
3. Run from `services/api` cwd (the suite does NOT collect from repo root — `No module named 'app'`): `python -m pytest tests/connectors/<file> -q` then `tests/connectors -q` for the wide count.
4. Mutation probe: `cp` the extracted module aside, revert the fix in the throwaway copy (scratchpad, never the repo), run the negative tests with `-k`, confirm they FAIL, then reason about which params are genuinely mutation-sensitive.

**Why:** proves adequacy first-hand instead of trusting the producer's "N passed" claim, and answers "would the OLD code pass these tests?" definitively. Sandbox is Python 3.11; CI is 3.12 — fine for stdlib-only connectors (re/json/datetime).

**How to apply:** any G4/G5 gate where the material lives only in a frozen commit and the reviewer is read-only. Do the archive+mutation in the scratchpad; it touches neither the repo nor git state, so it stays inside the read-only guard.

**Mutation nuance caught on M5-T044:** a regex-tightening test can be non-mutation-sensitive for some params if a downstream backstop also rejects the input (there `normalize_bbl` rejected the Unicode-digit BBL *input* even under the old leaky `^\d{10}$`, and the old anchor already rejected a trailing SPACE). Trailing-NEWLINE is the case that actually leaks past `^...$`+`.match`, so it is the load-bearing negative. Check each param, don't assume the whole parametrize block is mutation-sensitive.
