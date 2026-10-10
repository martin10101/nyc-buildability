// Presentation adapter: the document's value_state mapped to the owner's screen status words
// (M5-T148 part B; ruling V3, D-090-R641; presentation contract §4 "Status meaning is not a
// styling decision"). Pure. It decides no law and recalculates nothing (ruling V2): it only reads
// a state the document already set and names it in the owner's words.
//
// The owner's settled screen statuses (row R641): settled, conditional, not known. A withheld value
// is "Not known" with its reason and NO digit; a conditional value is "Conditional"; a settled value
// has no marker. "Verified" is NEVER produced (ruling V3/V8) — there is no code path to it, and the
// PDF's six labels (owner question C2) are not mapped onto the screen in this wave.

import type { ValueState } from "../../../../../packages/contracts/generated/results";

/** The owner's screen word for a value that carries no number (ruling V3). Never a digit. */
export const STATUS_NOT_KNOWN = "Not known";
/** The owner's screen word for a value shown under a stated condition (ruling V3). */
export const STATUS_CONDITIONAL = "Conditional";

/**
 * A value's status in the owner's words. A settled value carries NO marker (`kind: "settled"`), so
 * a caller shows nothing beside it. A withheld value carries its reason and no number. There is no
 * "verified" case and no numeric field anywhere in this type, so presentation can never promote a
 * withheld value to a number or a draft value to verified (acceptance UX-03).
 */
export type PresentedStatus =
  | { kind: "settled" }
  | { kind: "conditional"; label: string }
  | { kind: "not_known"; label: string; reason: string };

/**
 * Map a document value_state to the owner's screen status. An absent state (a value with no
 * value_states entry) is settled — it shows no marker. A `settled` state is likewise unmarked.
 * `conditional` → "Conditional". `withheld` → "Not known" with the document's reason and no digit.
 * The union is exhaustive, so a `way` added to the contract later fails type-checking here rather
 * than silently defaulting to a wrong word.
 */
export function presentStatus(state: ValueState | null | undefined): PresentedStatus {
  if (state == null) return { kind: "settled" };
  switch (state.way) {
    case "settled":
      return { kind: "settled" };
    case "conditional":
      return { kind: "conditional", label: STATUS_CONDITIONAL };
    case "withheld":
      return { kind: "not_known", label: STATUS_NOT_KNOWN, reason: state.reason };
  }
}
