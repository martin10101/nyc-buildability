# Zoning-law library — first pass (documents only)

**Unreviewed draft: discovery aid; each item links its source; nothing here is professionally
reviewed (ADR-007).** Legal readings in this library are drafts tied to the cited source text. Where
the producer is not sure, it says "not sure". Nothing here is labelled Verified; nothing here calls a
result compliant, buildable, or feasible.

## What this library is

A catalog, built from captured primary sources, of the Zoning Resolution (ZR) sections that bear on a
**R6B residence district with a C2-2 commercial overlay** — the benchmark lot **215-16 Northern
Boulevard** (Queens) — and on the **eleven development options** the report offers. It records, for each
section:

- whether the verbatim text is **captured** in `docs/research/zr-snapshots/v1/` (with the snapshot id
  and content digest copied from the snapshot) or **NOT CAPTURED**;
- which cross-references it names, and whether each is captured;
- which rule file (if any) under `services/api/app/rules/rulesets/` **handles** it, or why it is **not
  handled**;
- a coverage status from the one project vocabulary (`docs/LEGAL_CORPUS_COVERAGE_MATRIX.md` §2);
- the last-amended date and a scope note (followed / terminal / out of scope + reason).

It was generated at commit `aac892fc` from four read-only research-helper returns (H1 closure, H3 DOB
bulletins, H4 BSA/DCP, H6 options — saved outside git) **plus the producer's own checks** against the
snapshots and the rule files. The helper summaries were checked, not copied.

## Files

| File | Holds |
|---|---|
| `benchmark-r6b-sections.json` | One entry per ZR section in the closure + the 12-10 defined terms the sections rely on. The machine-readable core. |
| `cross-reference-closure.md` | How the traversal ran: the start set, what was followed, what was marked terminal or out of scope and why. |
| `coverage.md` | Handled vs not handled, grouped plainly; the not-handled families the remaining options need. |
| `options-sections.md` | The eleven options in the owner-approved order, each with the sections it needs and their captured/handled state; the open "split lot" question. |
| `pitfalls.md` | A checklist from official guidance (DOB Buildings Bulletins, BSA calendar numbers, DCP guidance), each item cited, never bulk-copied, never presented as the program's finding. |
| `research-log.md` | Every search the library rests on, access blocks, and the open discrepancies. |

## Scope and limits

- **Scope:** R6B + C2-2, the one benchmark lot, and the eleven options. The traversal is bounded to the
  R6B / C2-2 frontier and the options; sections that cannot apply to an R6B or C2-2 lot (R1-R5 height,
  towers, other-equivalency overlays, special-geography bodies) are recorded as out of scope with the
  reason, not dropped.
- **Documents only.** This library builds no corpus code. The cross-reference *closure engine* is a
  separate, still-backlog task (M3-T004); the construction-code corpus is M3-T005. This library feeds
  those tasks and does not duplicate them.
- **Captured ≠ handled ≠ verified.** A captured section has its verbatim text in the snapshot set; a
  *handled* section additionally has a rule file that computes a value from it; neither state is a
  professional verification. Only six sections are handled today; the rest are catalogued so the gaps
  are visible.
- **Not sure** is stated where the producer could not open a primary source (e.g. ZR 23-154, HTTP 403)
  or where a meaning is unresolved (the "split lot" reading).
- A tax lot is never equated with a zoning lot; an index entry never stands for the instrument; a BSA
  resolution or DOB determination is project-specific and never a general rule.

## How to extend it

1. Add newly captured sections to the snapshot set under `docs/research/zr-snapshots/v1/` (its own
   task), then add an entry here copying the snapshot id and content digest exactly.
2. When a rule file begins to compute a section, change its `handled_by` and `coverage_status` here and
   in `coverage.md`.
3. Keep every capture claim matching the snapshot folder — re-run the producer's capture-claim check
   (see `research-log.md` and the producer report for the command).
4. Legal readings stay unreviewed drafts with a source link; record new conflicts, do not resolve them
   silently.
