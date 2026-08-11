# SECOND independent G3 delta review — M2-T016 — **CONDENSATION, NOT VERBATIM**

> **This file is a CONDENSATION written by the orchestrator. It is NOT the verbatim reviewer return.**
> Per `.claude/rules/project-control.md`, a condensation must say so explicitly and must never be
> labelled verbatim. **The verbatim original is OUTSTANDING** — it was returned through the agent
> channel in session 14 and the orchestrator ran out of context before capturing it in full. It
> remains recoverable from the session transcript and SHOULD be captured before this gate is relied
> on for acceptance. The first reviewer's report IS preserved verbatim, with its delta
> re-attestation, in `M2-T016-delta-G3-code-review.md`.

**Reviewer:** a SECOND independent `code-reviewer`, dispatched after the first went idle twice
without delivering. Both subsequently delivered. Neither communicated with the other.
**Reviewed:** `d45f330..5a684fc` (4 files, +97/-3), worktree `M2-T016-integrate`.
**Verdict:** PASS with required corrections **RC-1, RC-2, RC-3**.

## The headline

RC-1/RC-2/RC-3 are *exactly* the F4/F10/F14 the first reviewer raised. **Two reviewers who never
communicated converged on the same three corrections.** All three were already applied at `e3c2ce6`.
It classified digest-shape validation as REQUIRED where the first called it recommended.

## Two corrections it made to state the orchestrator had already recorded

1. **`blocking_fact_ids` mechanism — the earlier claim was WRONG.** `canOfferConfirm`
   (`model.ts:88-94`) reads `capabilities.can_confirm_document`, the confirmable source states, and
   the server's `confirm_precondition_met`. It **never reads `blocking_fact_ids`**; the `length > 0`
   read is in `dominantAction` (`model.ts:131-146`). So the confirm button cannot be flipped
   disabled→enabled by sanitizing it. The conclusion (never sanitize it) survives on better grounds:
   charset-filtering mangles identity keys so `factsBlockingConfirmation` returns `[]` and the panel
   claims "no material facts to confirm yet" while the server says blocked; and dropping lets
   `dominantAction` fall through to "All material facts are resolved" while
   `confirm_precondition_met` is still false — a false all-clear. Only a **type** filter with a
   dropped-count is ever defensible; never a charset filter. Memory corrected accordingly.
2. **`evidence_id` charset is a client-side guess.** `survey_evidence.schema.json` defines it as a
   non-empty string with construction "implementation-defined"; the `sev:<prefix>:p<n>:<seq>` shape is
   only *suggested*. The shipped generator satisfies the new charset today, but the client is now
   enforcing a rule no contract guarantees (CLAUDE.md #3). Either pin the charset in the schema or
   move to opaque matching plus render-time bounding.

## Process defect against the orchestrator (Finding 15) — ACCEPTED

The orchestrator applied the first reviewer's corrections to the worktree **while the second review
was in flight**, so the second reviewer verified `5a684fc` against a tree that had already moved to
`e3c2ce6`. That is the same stale-head failure mode this whole exercise exists to correct.
**Rule to adopt: freeze the worktree for the duration of a gate wave.**

## Non-blocking follow-ups it raised

- **FU-1** surface a dropped-entry count — `errorCopy.ts` says "The blocking facts are listed below",
  which an empty list would contradict.
- **FU-2** pin the `evidence_id` charset in the schema, or use opaque matching + render-time bounding.
- **FU-3** extract `surveyReviewPath()` / `parseDocumentDigest()` so the digest URL contract is one
  exported pair rather than four `encodeURIComponent` calls agreeing by convention.
- **FU-4** pin the `URIError` → `notFound()` branch (no spec navigates a malformed segment).
- **FU-5** if `blocking_fact_ids` is ever hardened, type filter + dropped-count, never charset.
- **FU-6** freeze the worktree during a gate wave.

## Standing instruction from the reviewer

No gate may be recorded against `5a684fc` now that `e3c2ce6` exists, and the 77-row DCV stamped at
`d45f330` is **stale** — it must be re-stamped at whatever SHA is finally gated, before acceptance.
It also re-raised the `nanoid` policy tension independently: "non-required check" is a CI
configuration fact, not a policy exemption, and an advisory is never waivable.
