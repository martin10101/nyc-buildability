# Memory index

- [No-defaults dataclass test](feedback_no_defaults_dataclass_test.md) — a zero-arg TypeError test does NOT prove each precondition field lacks a default; use dataclasses.fields() (D-052 attestation pattern)
- [Mutation probe outside repo](mutation_probe_outside_repo.md) — how a read-only reviewer runs real mutation testing via git show → scratch copy + no-bytecode/no-cache pytest; ctl24 is a linked worktree
