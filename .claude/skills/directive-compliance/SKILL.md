---
description: Capture and enforce owner directives, corrections, PR-review amendments, holds, and replans as first-class, atomic, independently-verified repository state. Invoke the moment the owner gives a directive, correction, restriction, authorization, replan, or new instruction; when a PR review adds an amendment or required correction; before any replan or master-plan change; on "fix everything" / "address all items" / implementation-authorization requests; and whenever anyone claims a task, PR, gate, or milestone is complete or compliant. Manually invocable as /directive-compliance.
---

Purpose: eliminate reliance on chat memory. Every substantive owner instruction becomes durable,
atomic, traceable, independently verified repository state **before** implementation can be declared
complete. This skill records and binds; it never accepts a task, changes the master plan, lifts a
hold, or substitutes for a gate. Authority stays with the orchestrator and the gates (ADR-005).

## 0. Classify (stop early if not a directive)

A **substantive owner directive** is any request that changes, corrects, restricts, authorizes,
replans, implements, dispatches, claims, accepts, merges, or amends repository work. Pure explanations
and read-only status questions are **not** directives unless they introduce a new requirement. If it
is not substantive, do not create a directive record; proceed normally.

## 1. Capture verbatim, before acting

1. **Freeze and report the exact base SHA** (`git rev-parse origin/main`) before changing any file.
2. **Capture the exact text verbatim** into `project-control/directives/D-<nnn>-<slug>/source-001.md`
   (original) — never paraphrase. Corrections/amendments are **new append-only files**
   `source-002-amendment.md`, `source-003-amendment.md`, … — never edit a committed source.
3. **Hash the captured source** (SHA-256) and record it in `manifest.json → sources[].content_digest_sha256`.
   After a directive is active, source files, hashes, and requirement IDs are append-only.

## 2. Decompose into atomic requirements

4. Decompose **every** instruction into atomic, independently-testable requirements with stable IDs
   `D-<nnn>-R<nnn>` in `requirements.json`. Do not combine unrelated requirements into one row.
5. **Separately** capture each category — do not omit any: positive deliverables; prohibitions; holds;
   sequencing; dependencies; owner decisions; unresolved questions; acceptance harnesses; evidence
   requirements; external/time-sensitive-fact checks; and required return-report items.
6. Give every requirement deterministic **applicability** metadata (task IDs/types, milestones, paths,
   lifecycle event, effective date) so the resolver can derive the applicable set and forbid selective
   citation.

## 3. Trace both directions

7. **Forward trace:** every source paragraph/numbered item → at least one requirement ID (no gaps).
8. **Reverse trace:** every requirement and every changed file → its source anchor (nothing invented).
9. **Stop for genuine ambiguity, contradiction, or an unprovable acceptance method** — identify it to
   the owner; never silently interpret.

## 4. Bind and enforce

10. **Bind the applicable IDs** to the task packet (`directive_refs`) and to the review packet. The
    hardened CLI refuses to claim an in-regime task without valid references and refuses submission
    without per-requirement evidence (`tools/project_control.py`; `tools/directive_registry.py`).
11. **Invalidate earlier verification** whenever the reviewed head SHA / path-scoped content identity
    or the directive source changes (stale evidence never satisfies acceptance).
12. **Producer ≠ verifier:** the producer writes `requirements.json`; an independent verifier writes
    `verification.json`. Producer self-verification is prohibited.

## 5. Status discipline (never claim "complete" prematurely)

13. Every requirement ends as **PASS, FAIL, BLOCKED, UNVERIFIABLE, or independently-justified
    NOT_APPLICABLE**. NOT_APPLICABLE needs explicit reasoning and independent approval.
14. **Refuse** "complete", "all addressed", "fully corrected", or equivalent while **any** item is
    pending, failed, blocked, unverifiable, stale, or missing evidence. Generate the return from the
    completed matrix — never from a free-form narrative.

## Validate and review

- Run `python tools/validate_directive_compliance.py --check` (stdlib, read-only) — it shares the
  resolver with the CLI, so both interpret references identically.
- Independent final review uses the read-only `directive-compliance-verifier` agent plus the existing
  required reviewers, at the frozen head. The verifier reports **every** requirement ID individually.

## Two-lane principle & owner boundary

The registry **records** authoritative owner instructions; all work-blocking decisions still flow
through `tools/project_control.py`, blockers, holds, and gates. Shared reference resolution is not a
second gate. This skill authorizes nothing on its own — merging, acceptance, dispatch, task movement,
deployment, purchasing, dependency installation, and PR closure still require their existing approvals.
