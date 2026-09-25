# M5-T114 producer report — D-086 P1 visual/state specification

**Task:** M5-T114 (D-086 phase P1, research/docs-only, presentation-only design over existing contracts).
**Producer:** product-design-director (orchestrator-dispatched subagent, no shell).
**Worktree:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t114`.
**Directives cited:** D-086 (R001–R004), D-083 (R001), D-066 (R001), D-087 (R001/R002).

## Files written (3 — exactly the allowed_paths)

| File | Approx size | Contents |
|---|---|---|
| `docs/design/ui-cleanup/P1-VISUAL-STATE-SPEC.md` | ~37 KB / ~430 lines | Design principles; ONE shared status vocabulary (§2); design tokens (§3); global shell/IA (§4); per-surface spec for the seven surfaces with desktop+mobile annotations and normal/boundary/missing/failure states + L-row placement tables (§5); 7×4 coverage matrix (§6); preservation checklist (§7); cross-cutting behaviour incl. 3D/CAD/PDF control organisation (§8); approved copy samples before→after (§9); meaning-change register (§10). |
| `docs/design/ui-cleanup/P1-mockups.html` | ~26 KB | ONE static self-contained file, inline CSS only, no script / no external font/image/CDN. Desktop + phone frames for all seven surfaces using the spec vocabulary; annotations as text; a prominent FICTIONAL-data banner; every sample datum labelled fictional. |
| `project-control/reports/M5-T114-producer-report.md` | this file | Producer evidence. |

No file under `apps/`, `services/`, `packages/`, `.claude/`, and no edit of `docs/UI_DEEP_DIVE_ASSESSMENT.md`,
the P0 files, or `docs/DISCOVERY_BACKLOG.md`.

## Self-check evidence (evidence-status form)

- **[OBSERVED]** All three writes targeted absolute paths under the worktree's allowed set; the Write tool
  returned success for each. Source under `apps/web/src` was opened **read-only** to ground the vocabulary.
- **[OBSERVED]** `P1-mockups.html` static/self-contained check: a Grep over the file for
  `<script|https?://|src=|@import|url(|cdn|<emoji>` returns **No matches found** (only inline `<style>`; the
  one CSS background uses `repeating-linear-gradient`, no `url()`; no emoji — status is carried by the
  documented symbols ✓ ◐ ! ≠ ∅ — and text labels).
- **[BLOCKED → harvest]** `documented_test_commands` (`git diff --stat`, `git status --porcelain`) require a
  shell I do not have. Recipe for the orchestrator at harvest, run from the worktree root:
  `git -C C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t114 status --porcelain` and `git … diff --stat` — expect
  exactly the three allowed_paths modified, nothing else.

## Per-acceptance-scenario evidence

**AS-1 (vocabulary).** Spec §2 gives ONE status vocabulary. Every state maps FROM a named backend status /
returned field, shown verbatim, **never remapped, no number computed in the UI**, each with non-colour
accessible text. Grounded in real source: `lib/coverage.ts:22-77` (six-value `CoverageStatus` enum + symbols +
glosses; `DataCompleteness`), `rule-evaluation-contract.ts:69-134` (`DraftCoverageStatus` excludes `verified`;
`FAIL_SAFE_REASONS`; `wide_street` states), `architect/development-limits.ts:14-209`
(`residentialReference`, `FAILURE_LABELS`, `calculationStatus`, `bulkRow` — all presentation selections, no
arithmetic), `condo-records.ts:724-794` (channel states + `channelWithholdsAllowances`), `address-search.ts`,
`outline-bridge-api.ts`, `proposal-checks-api.ts`, `architect/max-envelope-api.ts` (transport/typed outcome
families). Organised by the five independent §12 questions so no single "confidence score" is invented.

**AS-2 (coverage).** Spec §5 gives desktop + mobile annotations and all four states for each of the seven
surfaces; §6 is the explicit 7×4 coverage matrix with every cell filled (no "n/a" was needed — each surface
has a genuine normal/boundary/missing/failure state). Mockup frames S/C/O/K/P/E/R (desktop + phone) mirror them.

**AS-3 (no-loss).** Every L-marked P0 ledger row for these seven surfaces is placed at its progressive
destination in §5 with its accessibility and print path, citing the ledger row id; the ledger holds the
authoritative per-cell detail. Rows placed (by family):

| Surface | L-rows placed (spec §) |
|---|---|
| Search | SH-01, SH-02, SH-05, SH-10, SH-11, SH-12, SH-13, SH-15; AD01–AD28 (§5.1) |
| Confirmation | AC01–AC11; M01–M13; LC01–LC22 (§5.2) |
| Overview | SH-05, SH-06, SH-08, SH-09, SH-14; ZC-01–ZC-04; A01–A15; LS-P01, LS-P03–LS-P16 (§5.3) |
| Condo | C01–C11 (§5.4) |
| Proposal / drawing | PE-01/02/03/04/07/08/10; DR-01–DR-23; PC-01–PC-06; PV-01/02; ME-01–ME-17; SW-01/02; ZC-04; LS-C01–LS-C28 (§5.5) |
| Evidence | F02/03/04/06/07/08; E01–E16; LS-E01–LS-E11 (§5.6) |
| Report | R01, R02, R03, R04, R05; SH-01 (§5.7) |
| Cross-cutting | LS-F transport family (§2.6); LS-T01–LS-T15 test invariants (§8, §11) |

The preservation checklist (§7) locks: §29 wording/prominence unchanged (verbatim in §4); the exact returned
disclosures (`report.disclosure`, `not_verified_disclaimer`, `wide_street.reason`/`fallback_direction_note`,
"Preliminary development limits" title, condo provenance) unchanged; and the point-of-decision city-warning
visibility (both messages above Continue) unchanged.

**AS-4 (copy + meaning).** §9 gives 12 copy samples as before→after each with the protected meaning. Honesty
vocabulary enforced: proposal geometry "Proposed — not a city record"; engine option "Generated building
option"; **no** use of permitted / approved / maximum-allowed as a claim (the banned terms are named in copy
sample #2 as prohibited). §10 is the meaning-change register: 8 items (MR-1…MR-8) whose change could alter
legal meaning are **NOT adopted** and are listed as questions for qualified review (wide-street 100-ft/formula
wording, null-end "in effect… to present", blanket professional-review over confident states, proposal-check
"short" overage wording, absolute "Every value… official-source fact", condo inline definitions, the
`rectangleSampleDraft` "your input" example, and report-freshness stale-result binding).

**AS-5 (mockups).** `P1-mockups.html` is one static self-contained file (verified no script / no external
resource — see self-check). Fictional sample data throughout, labelled by a prominent banner ("ALL DATA ON
THIS PAGE IS FICTIONAL", address `0000 Example Avenue, Test Borough`, BBL `0-00000-0000`); no real address is
shown as a real record. Desktop + phone frames for all seven surfaces use the spec's status vocabulary and
claim-class chips.

**AS-6 (scope).** Docs-only; exactly the three allowed paths written; no source, test, copy, ledger or
assessment edit (see self-check + files table).

## Not placed here, and why

- **SR01–SR62 (survey review) and DB01–DB22 (internal owner dashboard).** These are the assessment §9
  families and are **out of scope for P1's seven surfaces** — §14 P1 names exactly search, confirmation,
  overview, condo, proposal/drawing, evidence, report; survey and dashboard are the P6 slice ("Survey review;
  optional internal dashboard polish"). Their L-rows remain in the P0 ledgers for P6 and are intentionally not
  placed in this spec. Recorded so the reviewer does not read the omission as a no-loss gap.
- **In-flight drawing/max-envelope copy (DR-01…DR-23, ME-01…ME-17).** Placed at their progressive
  destinations, but the exact strings stay **pinned at `b56f3d5b`** because M5-T078/T079 are in rework; the
  ledger re-pins them at accept (P0 §8). The spec notes this and defers exact-copy verification to re-pin.

## Open questions (with recommended answers)

All decided within the rules and recorded; nothing waits on the sleeping owner.

1. **The 8 meaning-change items (MR-1…MR-8, spec §10).** Recommended: keep as-is today; route each to qualified
   domain/legal review (G6-class) before any wording change; specifically MR-2 (null-end legal-effect framing)
   and MR-7 (`rectangleSampleDraft` "your input") need a reviewed **behaviour** task, not a copy edit. Decision
   taken: **not adopted** in P1.
2. **P5 print decisions P5-D1…P5-D6, F04 spatial caveat, LS-P10 grouped missing fields, LS-P15 captured-JSON
   tier.** Recommended: carry them as explicit open decisions into the P5 slice (spec §5.7); do not silently
   resolve. Decision taken: **carried, not resolved**.
3. **Design-token palette.** The §3 tokens are a presentation proposal; recommended: reconcile against
   `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md` at build (P2+), confirming every status hue keeps ≥4.5:1 contrast and
   its paired symbol. Decision taken: **proposal, confirm at build**.
4. **≤700px environment-badge / nav-footnote hides (`architect.css:138`).** The spec treats these as P0-flagged
   responsive gaps to **close** (badge + review line visible at every width), consistent with SH-02/A01/A03 and
   P5-D1/D2. Recommended: the P2/P3 slices remove the hide with a visibility regression test.

## Discoveries (out-of-scope findings — recorded, never fixed here; for the orchestrator's `DISCOVERY_BACKLOG.md`)

- **DISC-1 (design/architecture).** The web layer has **no single "status" type**: user-facing state is composed
  from at least six independent backend dimensions (the `CoverageStatus` enum, `DataCompleteness`,
  `fail_safe_reason` → `FAILURE_LABELS`, the `calculationStatus`/`bulkRow` derived labels, the condo
  `CondoChannelState`, and the per-endpoint transport outcome unions). A "one status vocabulary" UI primitive
  (P3/P5) must **compose and display** these without collapsing them into one score — the design in §2 keeps
  them as five independent questions. Not a defect; a build-shape constraint for the shared-status component.
- **DISC-2 (mount dependency, already tracked).** The "Generated building option" claim class can only be shown
  with a real candidate once the max-envelope route mounts; today it is unmounted and shown as-is
  (ME-01…ME-17), with split-district disclosure + DB-050/DB-051(f)/(g) still pre-mount. The mockup shows the
  panel "as it exists today" only. This restates DB-050/DB-051 (no new item needed) — flag so P4/P5 does not
  assume a live generated option.
- **DISC-3 (responsive gap).** The `architect.css:138` ≤700px hides drop the internal-build environment badge
  and the reliance nav-footnote on narrow widths — a genuine mobile honesty gap the P2/P3 slices should close
  with a visibility test (overlaps SH-02/A01/A03 open_questions and P5-D1/D2; noted so it is not lost between
  slices).

## Requested status

**awaiting_gate** — the three deliverables are complete inside scope. Required gates G0, G2, G3 with reviewers
visual-quality-reviewer, human-journey-reviewer, directive-compliance-verifier. No blocker; no Tier-D item.

END-OF-REPORT
