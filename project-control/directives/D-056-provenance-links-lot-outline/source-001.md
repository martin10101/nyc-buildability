# D-056 source-001 (original, verbatim) — owner directive, interactive chat (orchestrator session), 2026-09-14

Capture head: `e8913a12674ddb0df757ed85d4e78cbbadd114b1` (branch `candidate/D-024-mrl-option-b`).
Frozen origin/main baseline: `d8b3899f61efa6620e18a26541ced96020f5bef9`.
Captured by the orchestrator session during the owner's live D-043 walkthrough of the internal
Render deploy (the walkthrough findings this order acts on are recorded in
docs/WORKING_KNOWLEDGE.md "D-043 owner walkthrough findings" and commit e8913a12).

## owner-message-verbatim

> So 2 thinks
> Please add the links so when I refresh the page it works
> 2 the zola did not pull the map up it stays blank and also on my screen there is no pale blue
> dod or outline its just gray also would be nice to have a zoom in and out button

## capture-context

- "add the links" = walkthrough Finding 1: the per-fact provenance panels
  (`ProvenanceDisclosure.tsx`, and the same rows in `RuleEvaluationResult.tsx`) name the source
  (internal slug, dataset id, host) as TEXT only; the owner wants a clickable link to the
  official dataset page. "so when I refresh the page it works" = the owner expects the fix on
  the live internal deploy — which requires the owner's Manual Deploy of the hand-created web
  service after the fix lands on `candidate/D-024-mrl-option-b` (auto-deploy is OFF by the
  D-043 checklist), then a refresh.
- "the zola did not pull the map up it stays blank" = walkthrough Finding 3 RETESTED and still
  failing on the owner's machine. Server-side re-verified live at capture time (2026-09-14
  fetch): ZoLa serves its normal Ember SPA shell (title "ZoLa | NYC's Zoning & Land Use Map")
  for the exact `/bbl/<bbl>` URL; the repo's link format was verified from ZoLa's own router
  source + live checks 2026-09-12 (docs/design/zola-deeplink-url-confirmation.md). The blank
  page is the city SPA failing/slow to boot client-side on the owner's browser — external to
  this repository; no code change owed.
- "no pale blue dod or outline its just gray" = walkthrough Finding 2 RETESTED after the
  scroll-zoom instruction: the outline is genuinely not visible on the owner's device (live
  deploy, BBL 3022647515 class input; the map canvas itself renders — gray background +
  attribution — so the defect is in outline layer visibility/framing, not map boot).
- "zoom in and out button" = a visible zoom control (MapLibre NavigationControl) on the
  lot-outline map — currently only scroll/pinch zoom exists (`interactive: true`, no control).
- Execution mode: a direct owner work order to the monitoring session during the D-053 loop's
  M4-T020 run. Hand-conducted as ONE parallel packet with allowed_paths fully disjoint from
  the loop worker's scope (apps/web vs services/api; D-046 3-writer ceiling respected: loop
  worker + one dispatched producer = 2). The D-053 quiet-monitor posture resumes after
  acceptance. Lot-outline map edits sit inside the D-040-R001 scoped release (lot-outline
  increment); the provenance panels are pre-expansion ordinary product surfaces.
