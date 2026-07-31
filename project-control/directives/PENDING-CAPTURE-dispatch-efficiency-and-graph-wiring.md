# PENDING CAPTURE — Dispatch Efficiency and Code-Graph Wiring (owner draft)

**Status:** pending-capture (pre-registration only; NOT captured, NOT active, no directive ID assigned).
**Registered:** 2026-07-31, by the orchestrator on owner instruction ("record its SHA-256 and
register it pending-capture, queued behind M0-T027"). Owner explicitly deferred capture:
"Capture waits for my instruction after acceptance [of M0-T027]."
**Updated:** 2026-07-31 — draft revised to v1.1 by the owner (sections 3, 5.2, 5.3, 5.4, 8
reconciled to the pre-flight findings); digest replaced accordingly on owner instruction.
**Updated:** 2026-07-31 — draft revised to v1.2 by the owner (§3 names the sweep identity,
default `progress-auditor`; §7 authorizes one new definition only as fallback); digest
replaced again on owner instruction.
**Queue position:** behind M0-T027 acceptance (unchanged). Do not capture, claim, contract, or
act on the draft while M0-T027 is open, and do not capture without a fresh owner instruction.

## Source

- Draft file: `OWNER_DIRECTIVE_DRAFT_dispatch-efficiency-and-graph-wiring.md` (repository root,
  untracked transient owner input; revision v1.2, 2026-07-31)
- SHA-256 (v1.2 bytes at update):
  `bd6c4ec2151202bb5209ee62f4cc2a3f94538cd40b695604ceff0e32d1c22b6b`
- Superseded digests (retained for provenance):
  - v1.1 (2026-07-31): `357eb3811605576ab0d996e93319bfcd8cdf7cc951753f9f74f12d0ea88f0f7b`
  - v1.0 (registered 2026-07-31): `733bc12d2df44d889c8b34a12823016dbb967b578d8511c3caff4e2fc62ee40e`
- At capture: verify the draft's bytes still match the v1.2 digest (or record the owner's revised
  digest), then capture verbatim through the directive-compliance process. This file is a
  provenance breadcrumb only; it is not a source document and confers no authority.

## Why this file (and not an index.json entry)

`tools/directive_registry.py` loads every `index.json` entry through `_load_directive`, which
records an error when the entry's manifest file does not exist; `proposed` status does not
exempt an entry. Creating a manifest before capture would begin the capture the owner deferred.
This standalone record is outside the index walk and keeps
`tools/validate_directive_compliance.py` green.

## Pre-flight conflict findings — disposition after v1.1 (2026-07-31)

1. §3 vs D-004 one-model-per-spawn / gate-reviewer pinning — **addressed in v1.1** (spawn-level
   tiering via a non-gate, non-producer mechanical-sweep identity; gate-class identities never
   on a lower model; explicit stop-and-amend condition).
2. §5.2 vs reviewer read-only discipline — **addressed in v1.1** (read-only reviewer variant
   mandates `--no-regen`; stale cache is reported, not regenerated; the §5.1 orchestrator
   packet query doubles as the cache warm).
3. "D-005 amendment 2" numbering — **addressed in v1.1** (§5.3 cites
   `D-005-codebase-knowledge-graph-pilot/source-003-amendment.md` and states the directive
   exercises amendment 2 item 8's reserved decision to the extent of §§5.1–5.2 only).
4. Stale orientation SHA `11f3540c` — **addressed in v1.1** (§5.4 marks it an ancestor and
   requires re-verification at capture-time head).
5. D-004-R307 disposition — **addressed in v1.1** (§8 requires capture to record the owner's
   explicit statement on whether Fable 5 restoration discharges the temporary explicit-Opus-5
   gate-reviewer pinning).

## Remaining item from v1.1 review — addressed in v1.2

§3's "dedicated mechanical-sweep identity" vs §7's authorization list — **addressed in v1.2**
(§3 names an existing auditor-class definition, default `progress-auditor`, as the sweep
identity; §7 authorizes creating exactly one new definition only as a fallback if no existing
definition is compatible). No open pre-flight findings remain against v1.2.
