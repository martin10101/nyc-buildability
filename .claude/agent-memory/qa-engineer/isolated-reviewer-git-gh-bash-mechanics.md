---
name: isolated-reviewer-git-gh-bash-mechanics
description: How a worktree-isolated gate reviewer reads the reviewed branch and gathers CI evidence within the bash isolation guard's rules
metadata:
  type: feedback
---

When running a G4/G5 gate as a worktree-isolated reviewer agent (cwd is `.claude/worktrees/agent-<id>`, NOT the task's `wt-*` checkout), these mechanics work and save a lot of thrashing:

- **Read reviewed-branch code two ways.** (1) The task's shared checkout path (e.g. `C:/.../wt-m0t064/...`) is directly readable with the Read tool — and when HEAD differs from the frozen SHA only in `project-control/**`, the working-tree `apps/web`/`services/api` files ARE the frozen content, so Read them directly. (2) For historical/frozen blobs use `git show <sha>:path` and `git diff <old>..<new> -- path` FROM YOUR OWN worktree — linked worktrees share the object DB, so every commit reachable from any ref (the branch, the base, arbitrary SHAs) resolves. `git rev-parse <sha>^{tree}` confirms the frozen tree identity.

- **The bash isolation guard enforces verifiable, in-worktree commands** — respect it, never engineer around it. It refuses (a) commands that `cd` into the shared checkout before running git (run read-only git from your own worktree instead; linked worktrees share the object DB), and (b) commands it cannot verify (heredocs, multi-pipe one-liners, combined redirects). The COMPLIANT pattern is the same one the orchestrator uses everywhere: put multi-step logic in a script file via the Write tool and run `python <file>` as a single plain command, so every bash call stays simple enough for the guard to verify. The guard's refusal is a correctness signal, not an obstacle.

- **gh read queries DO run** from the isolated reviewer cwd (e.g. `gh pr view/checks`, `gh run view --json headSha,conclusion`, `gh run view --job=<id> --log`). The read-only guard did NOT block them here. Use them for the clean-checkout CI evidence the owner demands: confirm `headRefOid`/`headSha == frozen HEAD`, that each run's `conclusion==success`, then pull the failing/authoritative job log to the scratchpad and grep it.

- **vitest CI reporter is file-level, not per-test.** The web-e2e log prints `✓ src/lib/__tests__/foo.test.ts (N tests)` and a final `Tests <total> passed` — it does NOT name individual describes/tests. To prove new adversarial tests executed, reconcile the per-file COUNT (original + added) and quote the file-level ✓ plus the `Tests N passed (N)` summary; you cannot literally quote a per-test-name line. State this limitation plainly rather than implying you saw each test name.

- **Faithful-validator gates:** verify hand-written key sets / enums / regex against the CANONICAL schema (`packages/contracts/schemas/v1/*.schema.json` + `common.schema.json`), not just the generated TS. Compile-time `MutuallyEqual` proofs lock enum arrays to generated unions, but required-key lists and copied patterns (BBL `^[1-5][0-9]{5}[0-9]{4}$`, digest `^sha256:[0-9a-f]{64}$`) are manual and are where a transcription error would hide.
