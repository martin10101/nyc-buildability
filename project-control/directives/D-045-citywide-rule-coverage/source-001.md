# D-045 source-001 (original, verbatim) — owner directive, interactive chat (companion session), 2026-09-13

Capture head: `7782be5981d28007075aa71e969df11774e44192` (branch `candidate/D-024-mrl-option-b`).
Frozen origin/main baseline: `d8b3899f61efa6620e18a26541ced96020f5bef9`.
Captured by the companion session (ctl24-8e) per the Part-0 working model; D-042/D-043 peer-capture precedent.

## owner-message-verbatim

Context question (owner, immediately prior — question only, not itself a directive):

> What about the r1 to r12 is it all just as good as r5 or something still needs to be build

The companion session answered: residential FAR coverage exists for all R1–R12 (four reviewed rule
families + the R6–R8 wide-street conditional rule); height/setback exists for the R5 family only
(gap-list A1 is the rest); geometry-dependent mechanics (A2), contextual/Quality Housing + bonus
programs (A3) are built in no district; commercial and manufacturing districts are absent entirely;
special purpose districts and waterfront zoning (A4) are later waves.

Directive (owner, verbatim):

> I wanna build all of this for the mvp can u tell then codex loop to build it ?

## scope-clarification-verbatim (structured question, same session, 2026-09-13)

Because "all of this" was ambiguous over the enumerated groups, the companion session asked one
structured scope question before capture. Question text:

> When you say build "all of this" — how far does the rule-coverage authorization go?

Options presented (labels + full descriptions, verbatim):

1. **Complete residential (Recommended)** — "Heights/setbacks for R1–R4 and R6–R12 (A1), the
   geometry-dependent mechanics like sky-exposure planes plus the street-width data they need (A2),
   and contextual/Quality Housing + bonus programs (A3). Finishes the full residential picture
   citywide. The biggest chunk of professional value; weeks of loop work, one reviewed family at a
   time."
2. **Heights first only (A1)** — "Just the height/setback families beyond R5 — the piece that turns
   \"here's your number\" into \"here's your buildable shape.\" Smaller, faster; A2/A3 wait for a
   later decision."
3. **Residential + commercial/manufacturing** — "Everything in the recommended option PLUS the C-
   and M-district rule families. Much larger: commercial FAR, use groups, overlay math. Doubles-plus
   the campaign; the MVP has been residential-only so far."
4. **Truly everything (incl. A4)** — "All of the above plus special purpose districts and waterfront
   zoning — the large self-contained rule bodies the gap list marked as later waves. The full
   citywide codebase; months of loop work."

Owner's selection (verbatim tool result): **"Truly everything (incl. A4)"**.

## capture-context

- "All of this" therefore authorizes, by the owner's explicit selection of option 4 (which
  incorporates options 1 and 3 by its "All of the above" wording): A1 (height/setback families
  R1–R4 and R6–R12), A2 (geometry-dependent rule mechanics) together with their data inputs
  (gap-list B2 street-width/mapped-street connector; the MapPLUTO geometry connector already exists
  — M5-T020 accepted), A3 (contextual/Quality Housing variants + inclusionary-style bonus
  programs), the commercial (C) and manufacturing (M) district rule families, and A4 (special
  purpose districts + waterfront zoning).
- The selected option text carries two sequencing facts the owner accepted with it: work proceeds
  "one reviewed family at a time" (option 1, incorporated), and A4 is "later waves" after the
  citywide base (option 4's own wording, matching gap-list Part 4 §A4).
- "Tell the codex loop to build it" = the standing build loop / orchestrator sessions integrate this
  campaign into the master plan and execute it as normal gated ledger tasks; the companion session
  relays this directive to the live build session.
- Gap-list authority: Part 4 of `docs/MVP_ARCHITECT_REVIEW_QA.md` marks the gap list "candidates
  only ... OWNER TRIAGE" and D-041-R003 forbids self-assignment. THIS directive is that owner
  triage for the named groups ONLY. Gap-list rows NOT named here (B3 DOB records, B4 landmarks,
  B5 ACRIS, C2, C3, E1–E3, and every group-D owner-gated item) remain untriaged candidates.
- Unchanged by this directive: every rule remains DRAFT/needs-review until G6 qualified legal
  review (owner-gated, Section 20); no compliance declarations; dependency policy §G for any new
  package; the expansion hold outside the released lot-outline increment; PR #241 unmerged;
  D-043's internal-only deploy scope.
