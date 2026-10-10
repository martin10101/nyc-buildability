// Presentation adapter: a document value and its unit, formatted for reading (M5-T148 part B;
// presentation contract §4 "label → value and unit, or unavailable state", §8 "format numbers").
// Pure. It FORMATS what the document holds and decides no law and recalculates nothing (ruling
// V2, D-090-R855). The data is never changed: a FormattedMetric is a display string built from a
// copy of the value, never a mutation of it.
//
// A value that is present (including exactly 0) is formatted with its unit. A value that is absent
// (null or undefined) gives a not-known state and NEVER a number — presence is tested with
// `== null` and `Number.isFinite`, never a truthiness test, so `0` is a value and never falls back
// to a zero or to "Not known" (the contract forbids `value || 0`, §8).

import { displayQuantity, quantityText, type Unit } from "./three-answers";

/** The screen word a value with no number carries. The owner's wording (ruling V3); never a digit. */
export const METRIC_NOT_KNOWN = "Not known";

/**
 * A value formatted for reading, OR the not-known state. `kind` tells the two apart so a caller can
 * never read a number off a not-known metric. `number` and `unit` are kept apart from `text` so a
 * headline can size the digits and the unit differently (the three-answers panel's DisplayQuantity
 * shape), while `text` is the one-line form, e.g. "20,150 sq ft".
 */
export type FormattedMetric =
  | { kind: "value"; text: string; number: string; unit: string }
  | { kind: "not_known"; text: string };

/**
 * Format a document value and its unit for reading. `null`/`undefined`, and any non-finite number
 * (NaN, Infinity — never a real measurement), give the not-known state and never a digit; every
 * finite number, INCLUDING 0, is formatted ("0 sq ft", never "Not known"). An unknown unit shows
 * the bare number (three-answers' displayQuantity fallback), never a raw unit code. The input value
 * is only read, never changed; full precision stays in the data.
 */
export function formatMetric(value: number | null | undefined, unit: Unit): FormattedMetric {
  if (value == null || !Number.isFinite(value)) {
    return { kind: "not_known", text: METRIC_NOT_KNOWN };
  }
  const quantity = displayQuantity(value, unit);
  return { kind: "value", text: quantityText(quantity), number: quantity.number, unit: quantity.unit };
}
