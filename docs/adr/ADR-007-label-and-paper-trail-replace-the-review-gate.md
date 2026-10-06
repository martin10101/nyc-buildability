# ADR-007 — A standing label plus a per-stat zoning-law paper trail replace the professional-review gate

- **Status:** Accepted (owner-directed, D-090 source-027 / owner message 62, 2026-10-04)
- **Date:** 2026-10-04
- **Decider:** Project owner (directive D-090-R164, R165) + orchestrator
- **Session:** Claude Code session 4d3637bc-346a-4b44-a0e7-b9688bc4f91a
- **Supersedes:** the posture that G6 qualified-reviewer approval is a gate that blocks showing or
  exporting values, and the Section 20 / Tier D "legal/zoning approval" owner-stop, as it applied to
  showing and exporting feasibility results. ADR-005 execution authority and the ADR-006 tier model
  are unchanged except where this ADR names them below.
- **Directive requirements:** D-090-R163 (Lane A merge authority to the orchestrator),
  D-090-R164 (this decision), D-090-R165 (the label + paper-trail + not-sure build obligation),
  D-090-R166 (the target is every property type, the full scope; built one zone at a time per the
  owner's later correction, D-090-R167).

## Context

The owner decided, in message 62 of 2026-10-04 (captured verbatim in
`project-control/directives/D-090-product-plan-2026-09-28-start-building/source-027-amendment.md`):

> On yes no I let u decide based on best for program and no professional review stop asking for that
> we just put a label on website 1 time that it needs to be reviewed our part is we leave a paper
> trail and links directly to the zoning low for each stat etc thats it stop bugging out about it
> since we are building it with data from source and if program is not sure it says so not like the
> mistakes of the pdf company we are not narrow ing the target we going to work on it all at once

On their face, three permanent principles and one hard stop conflict with this:

- **Principle 1** said qualified humans approve legal interpretations.
- **Principle 12** said no rule becomes `published` without qualified-reviewer approval.
- **Principle 13** said to stop and open a blocker when a legal interpretation needs a human.
- The **Authority** section and ADR-006 **Tier D** listed "legal/zoning approval" among the actions
  only the owner performs, so a result could not be shown or exported until a human reviewer signed.

The owner is the authority over these rules. The owner's liability reasoning, stated plainly: the
numbers are built with data from the official source; every stat leaves a paper trail that links
directly to the zoning-law text it rests on; when the program is not sure it says so; and the website
carries one standing label that the results need professional review. That is the opposite of the
competitor PDF company, whose mistake was presenting unsourced numbers as finished answers. The
owner's instruction is to stop asking for a professional-review sign-off and instead ship behind the
label and the paper trail.

The orchestrator records the decision here and amends CLAUDE.md, the gate doc, and the product-flow
doc under this directive, both producer and reviewer independent, rather than keep asking.

## Decision

1. **G6 qualified-reviewer approval is no longer a gate that blocks showing or exporting a value, and
   is never asked of the owner again.** No agent asks the owner for professional or legal sign-off.

2. **Professional review becomes optional and advisory.** A reviewed rule may be marked as reviewed
   when a review actually happens, and that fact is recorded, but nothing in the product or the
   pipeline waits for it. G6 stays in the gate catalogue as an optional, advisory record of a review
   event, not a blocking gate.

3. **One standing label on every surface and every export.** Every website surface (cards, drawings,
   compare view, evidence view) and every exported report carries one always-visible label: the
   results are computed from official public sources, have not been professionally reviewed, and must
   be verified by a licensed New York professional before reliance. The label is shown one time per
   surface, plainly, not per value.

4. **A per-stat paper trail to the zoning law.** Every printed stat links directly to the
   zoning-law text it rests on: the captured, pinned source snapshot plus the official page. A value
   with no resolvable law link is a defect.

5. **The program says "not known" / "not covered" instead of guessing.** When an input is missing or
   a rule family is not yet covered, the program fails closed to a labelled "not known" or
   "not covered" with the reason, on every surface and export. It never fills the gap with a guess.

6. **The draft register and the ban on compliance declarations stay.** Rules stay in the draft
   register. The program never says a project "complies", is "approved", or is "guaranteed", and
   never represents a result as a legal opinion, permit approval, or professional certification.

7. **Rule status vocabulary.** `needs_review` stays the default status for an authored rule.
   `published` now means "shipped under the standing label", not "professionally approved". The
   qualified-professional event that `published` formerly required is replaced by the standing label
   and the paper trail; where a professional review does happen it is recorded as an advisory fact,
   not a precondition. `verified` keeps its meaning (the orchestrator's reading; the owner did not
   mention it): it is used only for a rule or result a qualified professional has actually reviewed,
   with that review recorded. Nothing shipped under the label is called `verified`.

### Effect on ADR-006 Tier D

ADR-006 Tier D item 10 ("publishing or labeling a rule `published`/`verified` without the required
qualified professional event") is reinterpreted by this ADR: `published` now means "shipped under the
label", so shipping under the label is permitted and is no longer a hard deny; labelling a rule or
result `verified` without that event stays a hard deny. ADR-006 Tier D item 11
(representing a result as a legal opinion, permit approval, or professional certification) and the ban
on compliance declarations stay in force unchanged. ADR-006 is an immutable record; this ADR
supersedes those two readings in prose. The Tier D hard stops for production approval, production
deployment, payments, secrets, credentials, and paid-account creation are not touched by this ADR.

## Consequences

**What changes:**

- **Lanes A–E** no longer wait on a qualified-reviewer sign-off to ship a rule or a value. A rule
  reaches `published` ("shipped under the label") once it has source linkage, deterministic tests,
  and independent agent review and green CI. Review per change by a different agent still applies.
- **The report** carries the one standing label and a direct zoning-law link for every stat; values
  the program is not sure about print as "not known" / "not covered" with the reason.
- **Owner-update wording** no longer asks the owner for professional or legal review and no longer
  reports a result as blocked on it. The owner is told a value is shipped under the label with its
  law link, or that the program is not sure and why.
- **D-090-R163:** the orchestrator decides Lane A merge yes/no on what is best for the program; every
  merge still needs a different agent's PASS at the exact head and every check green.

**What does NOT change:**

- Review per change by a different agent (producer is never the reviewer).
- Green CI on every PR and fail-closed merges.
- ADR-005 execution authority (orchestrator-only ledger/git/gh; producers in scope; reviewers
  read-only) and the ADR-006 tier model.
- Tier D hard stops for production approval, production deployment and infrastructure mutation,
  payments, secrets and secret rotation, credentials, verification codes, and paid-account creation.
- The draft register, provenance on every material value, and the ban on compliance declarations.

## Alternatives considered

- **Keep the professional-review gate as blocking.** Rejected by the owner: it stalls the build, asks
  the owner for a sign-off the owner has declined to require, and the label plus the per-stat paper
  trail plus the "not sure" behaviour carry the same honesty to the user without the stop.
- **Put the label only on the exported report, not the website surfaces.** Rejected: the owner asked
  for the label on the website, and a user reads values on the cards and the compare view before any
  export. One standing label on every surface and every export is clearer and harder to miss.

## Record

- Owner decision: D-090-R164 (decision), D-090-R165 (build obligation), D-090-R163 (Lane A merge
  authority), D-090-R166 (the target is every property type, the full scope; built one zone at a
  time per the owner's later correction, D-090-R167, source-028), source-027 / owner message 62,
  2026-10-04.
- Captured verbatim: `project-control/directives/D-090-product-plan-2026-09-28-start-building/source-027-amendment.md`.
- This ADR and the CLAUDE.md amendment are both independently reviewed before merge.
