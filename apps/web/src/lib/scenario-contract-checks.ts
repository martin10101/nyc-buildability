/**
 * Generic, vocabulary-free runtime check primitives for the scenario contract
 * validator (task M5-T004 rework; split out of scenario-contract.ts under the
 * repository modularity law so the contract module keeps exactly one
 * responsibility — the scenario vocabulary — and these reusable JSON checks
 * keep another).
 *
 * Nothing here knows a single scenario field name. Every function takes the
 * path it is checking, so the caller owns the vocabulary.
 *
 * BODY-INDEPENDENCE INVARIANT (G5 confirmation 1, preserved deliberately):
 * every `message` passed to `Problems.add` is a static string literal or a
 * literal interpolating only CLIENT-OWNED constants (`MAX_DOCUMENT_ARRAY_LENGTH`,
 * a caller's own `allowed` enum array). NO byte of a rejected response body may
 * ever reach the problem list, because that list is rendered by
 * ScenarioValidationFailureState. Any future check must keep this property.
 */

/**
 * Maximum length accepted for ANY array carried by a scenario document — the
 * one shared constant required by the G5 bounding spec. 64 entries is a
 * generous ceiling over the measured committed fixtures (constraints 11,
 * coverage_matrix 11, reasons 1-2, assumptions 0, citations 1).
 *
 * A longer array is REJECTED, never truncated. This asymmetry with string
 * handling (strings truncate, arrays reject) is deliberate: silently truncating
 * an array would DROP contract content — dropping a `reasons` entry hides why
 * no scenario could be stated — which is the exact silent-omission defect class
 * this packet was failed for. Rejection surfaces through the already-tested
 * `validation_failure` card, so it needs no new UI. Exactly 64 is accepted; 65
 * rejects.
 */
export const MAX_DOCUMENT_ARRAY_LENGTH = 64;

/** Upper bound on the problem list itself (the report, not the iteration). */
export const MAX_REPORTED_PROBLEMS = 20;

/** Bounded, append-only problem collector. */
export class Problems {
  list: string[] = [];

  add(path: string, message: string): void {
    if (this.list.length < MAX_REPORTED_PROBLEMS) {
      this.list.push(`${path}: ${message}`);
    } else if (this.list.length === MAX_REPORTED_PROBLEMS) {
      this.list.push("… further problems omitted (bounded report)");
    }
  }
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

export function checkEnum(
  problems: Problems,
  path: string,
  value: unknown,
  allowed: readonly string[],
): void {
  if (!(typeof value === "string" && allowed.includes(value))) {
    problems.add(path, `value is not in the documented enum (${allowed.join(", ")})`);
  }
}

export function checkString(problems: Problems, path: string, value: unknown): void {
  if (typeof value !== "string") {
    problems.add(path, "must be a string");
  }
}

export function checkNonEmptyString(
  problems: Problems,
  path: string,
  value: unknown,
): void {
  if (!isNonEmptyString(value)) {
    problems.add(path, "must be a non-empty string");
  }
}

export function checkNullableString(
  problems: Problems,
  path: string,
  value: unknown,
): void {
  if (!(value === null || typeof value === "string")) {
    problems.add(path, "must be a string or null");
  }
}

export function checkBoolean(problems: Problems, path: string, value: unknown): void {
  if (typeof value !== "boolean") {
    problems.add(path, "must be a boolean");
  }
}

/**
 * A schema-declared array: must BE an array and must be within the shared
 * bound. Returns the array on success so the caller can walk it, or `null` when
 * a problem was recorded (so the caller never walks an unbounded value).
 */
export function checkBoundedArray(
  problems: Problems,
  path: string,
  value: unknown,
): unknown[] | null {
  if (!Array.isArray(value)) {
    problems.add(path, "must be an array");
    return null;
  }
  if (value.length > MAX_DOCUMENT_ARRAY_LENGTH) {
    problems.add(
      path,
      `must carry at most ${MAX_DOCUMENT_ARRAY_LENGTH} entries; a longer array is rejected, never truncated (truncating would silently drop contract content)`,
    );
    return null;
  }
  return value;
}

/**
 * A WEAKLY-TYPED nested array inside an `unknown` provenance blob: the schema
 * does not declare its type, so a non-array is not a contract violation and is
 * ignored here. When it IS an array it is held to the same shared bound,
 * because the renderers map over it.
 */
export function checkOptionalBoundedArray(
  problems: Problems,
  path: string,
  value: unknown,
): void {
  if (!Array.isArray(value)) return;
  if (value.length > MAX_DOCUMENT_ARRAY_LENGTH) {
    problems.add(
      path,
      `must carry at most ${MAX_DOCUMENT_ARRAY_LENGTH} entries; a longer array is rejected, never truncated`,
    );
  }
}

/**
 * A contract scalar (`number | string | boolean | null`) that is REQUIRED to be
 * present — the shape `constraints[].value` and `assumptions[].value` declare.
 * Presence and type are checked separately so a missing key and a wrong type
 * report distinctly.
 */
export function checkRequiredScalar(
  problems: Problems,
  path: string,
  container: Record<string, unknown>,
  key: string,
): void {
  if (!(key in container)) {
    problems.add(path, "required key is missing");
    return;
  }
  const value = container[key];
  if (
    !(
      value === null ||
      typeof value === "number" ||
      typeof value === "string" ||
      typeof value === "boolean"
    )
  ) {
    problems.add(path, "must be a number, string, boolean, or null");
  }
}

/**
 * Reject keys the contract does not document. The schema declares
 * `additionalProperties: false` at every object level; the validator's own
 * docstring has always claimed a "documented key set" check, and this is it
 * (G5 finding 3 / G4 finding 2b: the guarantee was documented but not
 * implemented).
 */
export function checkNoUnknownKeys(
  problems: Problems,
  path: string,
  value: Record<string, unknown>,
  allowed: readonly string[],
): void {
  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) {
      problems.add(
        path,
        `carries a key outside the documented key set (${allowed.join(", ")})`,
      );
      return;
    }
  }
}
