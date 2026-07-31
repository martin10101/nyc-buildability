# D-004 — source-013 (owner amendment 12, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.

Head at capture time: `origin/main` = `11f3540c602849f4100517f35b7b93eca6742a8d` (confirmed
unchanged before any write, exactly as the owner required); local
`task/M0-T027-closeout-phases-3-4` = `f3014213742a074841ed52cab3e59ea83ccd69c7` — the full
40-character resolution of the frozen closeout identity the owner named as `f301421`. Working tree
clean under `project-control/`.

Requirement IDs added by this amendment start at `D-004-R517`; no existing source file or
requirement row is edited.

## Scoping — binding and unusual, so stated up front

The owner directs that this authorization be captured **under the `D-004-OPTIONB` session
sentinel**, that it is **execution authority and NOT a new M0-T027 task-content or acceptance
requirement**, and that **no requirement newly derived from this message may be scoped to
M0-T027**. Every row below therefore carries `task_ids: ["D-004-OPTIONB"]`.

The mechanical consequence, recorded so it cannot be mistaken for an oversight: because the
canonical resolver derives a task's applicable set by matching `task_ids` against the packet,
**none of rows R517–R552 enters M0-T027's applicable set, and `accept()` will never gate on them.**
They bind the orchestrator's session conduct and are enforced at D-004's own final verification —
the same structural position as the return items R502–R514. This is precisely what the owner
instructed, and it is the mechanism that keeps this authorization from re-creating the very
circularity it exists to resolve.

## Relationship to the stop this resolves

The prior session STOPPED at the `directive-compliance-verifier`'s **BLOCKED** verdict (0 FAIL,
0 BLOCKED-by-defect, 204/233 PASS, 29 UNVERIFIABLE-not-yet-due). This amendment authorizes
Option A (further verification passes as the evidence comes into existence) and authorizes
Option B **only** as the exact conditional fallback for a four-row circularity (`R486`, `R487`,
`R488`, `R501`). It does not waive, weaken, or pre-decide any requirement.

---

## Owner message (verbatim, complete as received)

GO — authorize Option A first, with Option B authorized only as the exact
conditional fallback below.

Capture this authorization under the D-004-OPTIONB session sentinel. It is
execution authority, not a new M0-T027 task-content or acceptance requirement.
Do not scope any newly derived requirement from this message to M0-T027.

Proceed from frozen closeout identity f301421 only after confirming origin/main
is still 11f3540c602849f4100517f35b7b93eca6742a8d and resolving the full commit
identity.

1. Run the second verification pass now. Convert only rows supported by evidence
that already exists. Do not prospectively PASS any unperformed act.

2. Continue through the authorized lifecycle:
   - submit M0-T027 through the CLI;
   - push/open the protected-main PR;
   - require all contracted CI at the exact PR head;
   - merge only when green and otherwise authorized;
   - reconcile the exact merged-main identity;
   - regenerate the evidence map with the canonical resolver;
   - run the independent third verification pass at that merged identity.

3. If every applicable M0-T027 requirement passes, accept through the CLI,
record the checkpoint, clean only M0-T027 closeout-owned branches/worktrees,
and STOP. Do not execute Step 5/M0-T029.

4. If and only if the exact remaining blockers are R486, R487, R488, and R501,
and each remains UNVERIFIABLE solely because it describes acceptance or an act
that occurs after acceptance, invoke Option B:

   - append an owner amendment re-scoping exactly R486, R487, R488, and R501
     from M0-T027 to the D-004-OPTIONB session sentinel;
   - preserve their locked wording and order;
   - do not delete, waive, weaken, rewrite, or pre-mark any of them PASS;
   - keep all four binding as session-level lifecycle obligations;
   - validate the append-only directive manifest, IDs, content digests, and
     validator exit;
   - merge the amendment through the normal protected-main workflow;
   - regenerate the canonical applicable set and evidence map;
   - rerun independent verification at the exact resulting identity;
   - accept M0-T027 through the CLI, then complete checkpoint, cleanup, and
     stop in their required order, preserving truthful sentinel evidence.

Continue the existing explicit-Opus-5 and model-disclosure policy unchanged.

If any other row remains blocked, the remaining set changes, CI fails, identity
drifts, or any substantive finding appears, STOP and report it. Do not amend
around any blocker other than the exact four-row circularity authorized above.
