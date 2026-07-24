# Directive-compliance bootstrap (D-001 / M0-T023)

This note explains how the Owner Directive Compliance System was proven **on its own
implementation** without circularly depending on enforcement code that did not yet exist,
and it separates the actions performed under the **old** CLI from validations **replayed**
under the completed **new** CLI (directive D-001, amendment correction 7).

## The bootstrapping problem

The system enforces that an in-regime task cannot be claimed/submitted/accepted without valid
directive references, per-requirement evidence, and independent verification. But the very task
that *builds* that enforcement (M0-T023) cannot be gated by code that does not exist at the
moment it is created. Resolving this by hand-waving ("trust me, it complies") would defeat the
purpose. Instead the bootstrap is explicit and auditable.

## Sequence (what actually happened, in order)

1. **Reconcile + freeze base.** `origin/main = 1acb9b5` was frozen and reported before any file
   changed. No accepted task was reused or altered.
2. **Capture D-001 (registry data, not enforcement).** The verbatim owner directive was written
   to `D-001-.../source-001.md`, the Option-1 approval + 8 corrections to
   `source-002-amendment.md`, hashed, and decomposed into `requirements.json` (89 atomic rows).
   This is pure provenance data; it enforces nothing by itself.
3. **Create M0-T023 under the OLD CLI (pre-enforcement).** The task packet was created with the
   *existing, unmodified* `tools/project_control.py new-task` — which has no directive-reference
   enforcement. This is a **bootstrap action under the old CLI**: it could not have been blocked
   by the new rules because they were not yet written.
4. **Hand-stamp the packet in-regime.** `M0-T023.json` was then edited to add
   `directive_refs: [{directive_id: D-001, requirement_ids: ALL}]` and
   `directive_regime_version: 1.0`. This is the deliberate, recorded regime-entry stamp
   (`directive_regime_note` in the packet documents it).
5. **Build the enforcement (new CLI + resolver + validator + tests).** Only after the packet
   existed were the enforcement code paths added to `project_control.py`, the shared
   `directive_registry.py` resolver, and `validate_directive_compliance.py`.
6. **Replay validations under the NEW CLI.** With enforcement now present, the new rules were
   run *against M0-T023's own packet and registry* to prove they pass on a correctly-formed
   in-regime task and fail closed on malformed ones. These are **new-CLI replayed validations**,
   not the original bootstrap creation:
   - `python tools/validate_directive_compliance.py --check` → exit 0 over the D-001 registry.
   - The resolver's `evaluate_task_refs(M0-T023)` → `ok=True`, all 89 applicable requirements
     covered, `missing_ids=[]` (test `test_bootstrap_self_proof`).
   - The CLI enforcement is proven by `test_project_control.py` S9 (claim requires refs;
     selective citation refused; governance-path guard; evidence map; content-manifest identity;
     accept requires independent verification; migration table / no deadlock).

## Why this is not circular

- The **creation** of M0-T023 used the old CLI (no new rule could gate it) — honestly a
  pre-enforcement action.
- The **enforcement rules** are then validated by (a) the deterministic validator over the real
  registry, and (b) adversarial unit tests over *synthetic* fixtures that exercise every failure
  mode independently of M0-T023. The system's correctness does not rest on M0-T023 being
  well-formed; it rests on the tests, which include negative cases.
- M0-T023 is finally submitted/verified **under the new CLI** exactly as any future in-regime
  task would be, demonstrating the closed loop on a real task.

## Old-CLI vs new-CLI ledger of actions (for the return evidence)

| Action | CLI used | Why |
|---|---|---|
| `new-task M0-T023` | OLD (unmodified) | enforcement did not exist yet; cannot self-gate its own creation |
| Hand-stamp `directive_refs` + `directive_regime_version` | manual packet edit | explicit, recorded regime entry (correction 4) |
| Registry integrity, ref resolution, coverage, fail-closed | NEW validator + resolver | replayed proof over the real registry |
| Claim / self-check / submit of M0-T023 | NEW CLI | closes the loop on a real in-regime task |
| Independent verification (`verification.json`) | NEW (verifier agent, read-only) | producer ≠ verifier at frozen head |

## Boundary

Nothing in this bootstrap accepts or merges M0-T023. Acceptance remains owner-gated and requires
independent final verification at the frozen content identity (see `manifest.json → owner_approval`).
