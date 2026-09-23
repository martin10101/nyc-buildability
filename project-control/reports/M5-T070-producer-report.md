# M5-T070 producer report — Preliminary-development-limits panel (D-082-R003 + D-083)

Status at this checkpoint: **IN_PROGRESS** (test authoring increment; not submittable yet).
Run lineage: `persistent3-local-16-m5t070`. Worktree HEAD: `a66cf818` (no commits this unit —
producer edits are uncommitted working-tree state, harvested by the orchestrator).

## Provenance note (read first)

On entry this worktree already carried a COMPLETE, uncommitted production implementation of all
five source files (the orientation packet's "fresh unit / no prior progress" did not match the
tree — a prior unit of this lineage left the production code uncommitted, tests unwritten). This
unit did **not** author the production source; it verified the source against the contract and
wrote the missing test suites. The orchestrator/DCV must confirm production-code provenance at
harvest and prove behavior in CI (thin client: no web tests run locally — CODING_RULES).

## Implementation surface (inherited production code, verified this unit)

- `apps/web/src/lib/architect/max-envelope-api.ts` — typed client for the UNMOUNTED
  `POST /api/v1/max-envelope`. Mirrors the exact (status,state) matrix (`DOCUMENTED_PAIRS`
  :194), bounds every reflected string, size-bounds before parse (:427), derives the
  D-083-R004 incomplete-aggregate predicate (`envelopeAggregateIsComplete` :538), the adoption
  gate (`candidateIsAdoptable` :545), answer-first request assembly (`maxEnvelopeRequestForProfile`
  :506, sends NO geometry). No client CRS math.
- `apps/web/src/components/architect/MaxEnvelopePanel.tsx` — answer-first panel; heading class
  "Preliminary development limits" (:223), verbatim disclosure (:130), per-dimension binding
  provenance + gap + surfaced-never-resolved advisory (`DimensionRow` :51), "Generated building
  option" as the ONLY building-shaped claim (:154), no unrestricted-green aggregate (:134),
  typed degradation card (:246), one-action adoption via the ONE draft model (:112).
- `apps/web/src/lib/architect/proposal-draft.ts` — `draftFromCandidate` (:393) seeds the ONE
  draft model from a candidate verbatim (no math/CRS), provenance labeled PROPOSED.
- `apps/web/src/components/architect/ArchitectEntry.tsx` — `ProposalSurface` (:44) composes the
  panel ADDITIVELY above the accepted `ProposalEditor`; adoption lifts to `adoptedDraft`.
- `apps/web/src/components/architect/ProposalEditor.tsx` — accepts `adoptedDraft` (:60); a new
  non-null draft replaces the working draft; manual entry unchanged (:87 effect).

## Tests authored this unit (acceptance-scenario coverage)

- `__tests__/max-envelope-api.test.ts` (NEW full suite) — AS-1 (disclosure verbatim, binding
  provenance, gap by reason, advisory both ids), AS-5 (documented (status,state) matrix; malformed
  200 → validation_failure; size-bound-before-parse; exact request assembly; null on no lot area),
  AS-4 (candidate bounding + adoptability gate; malformed candidate dropped), **AS-3
  mutation-sensitive** (gap→binding flips aggregate; advisory alone keeps incomplete).
- `components/architect/__tests__/max-envelope-panel.test.tsx` (NEW full suite) — AS-1/AS-2 render,
  AS-2 source-grep proving ABSENCE of "maximum allowed building"/"demonstrated maximum",
  **AS-3 mutation** on `data-complete`, AS-4 adoption (`onAdopt` seeded draft), AS-6 degradation
  (no-context / retryable failure / feature-off no-retry).
- `lib/architect/__tests__/proposal-draft.test.ts` (APPENDED) — `draftFromCandidate` verbatim
  pass-through, D-083 claim-class label + PROPOSED provenance, runnable-after-seed (AS-4).
- `components/architect/__tests__/proposal-editor.test.tsx` (APPENDED) — adoption replaces the
  working draft, seeds the numeric authority, announces PROPOSED, manual entry stays available (AS-4).

## Self-checks

- `python tools/modularity_check.py --check` → `failures 0; warnings 22` (all 22 pre-existing,
  none in this packet's files). Exit 0.
- Web suites NOT run locally (thin client). Web behavior proves ONLY in CI on the pushed head.

## Remaining before submittable (honest gap)

1. **AS-5 e2e** — `apps/web/e2e/proposal-editor.spec.ts`: add a test that stubs
   `**/api/v1/max-envelope` (asserting POST + no geometry sent), opens the proposal view, asserts
   the panel renders and one-action adoption seeds the editor. Deferred here because the chosen
   BBL's fixture lot area (which decides whether the panel fetches) must be confirmed first; a
   speculative e2e I cannot run risks a red CI spec. Follow the existing `page.route` stub
   precedent (spec :136, :286).
2. **AS-6 entry integration** — optionally add an additive-composition assertion to
   `entry.test.tsx` (panel + editor both present; panel degrades without breaking the editor).
   Note: `ProposalSurface` wires the panel with the DEFAULT fetch, so it auto-fetches on mount in
   tests — assert via the degraded failure card or inject a fetch seam.
3. CI green on the pushed head across web-unit + web-e2e + the accepted T060/T065/T066 specs.
