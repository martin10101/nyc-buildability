/**
 * Study-contract check primitives (task C-05, plan M1-10): the common.schema.json
 * shapes (BBL, RFC 3339 timestamp, non-empty string) and the object/array checks
 * the study and site-fact validators share. Generic JSON checks come from
 * ../scenario-contract-checks and keep its BODY-INDEPENDENCE INVARIANT: every
 * problem message is a static literal (or interpolates client-owned constants
 * only), so no byte of a rejected document reaches the problem list.
 */

import { Problems, checkNoUnknownKeys, isNonEmptyString } from "../scenario-contract-checks";

/** common.schema.json#/$defs/bbl */
export const BBL_PATTERN = /^[1-5][0-9]{5}[0-9]{4}$/;

/** common.schema.json#/$defs/date_time (pattern enforced, as the schema does). */
export const DATE_TIME_PATTERN =
  /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$/;

/**
 * Fixture-only annotation (packages/contracts README convention). The schemas
 * admit it so an invalid FIXTURE fails only for its stated defect; a real study
 * never carries it (the server-side validator refuses it the same way).
 */
export const FIXTURE_ONLY_KEY = "_expected_failure";

export function hasOwn(value: Record<string, unknown>, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(value, key);
}

export function isOneOf(allowed: readonly string[], value: unknown): value is string {
  return typeof value === "string" && allowed.includes(value);
}

/** Strict JSON number: NaN and Infinity are not JSON and never pass. */
export function isJsonNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

export function isBbl(value: unknown): value is string {
  return typeof value === "string" && BBL_PATTERN.test(value);
}

/** Required keys present, and no key outside required + optional (additionalProperties: false). */
export function checkKeys(
  problems: Problems,
  path: string,
  value: Record<string, unknown>,
  required: readonly string[],
  optional: readonly string[] = [],
): void {
  for (const key of required) {
    if (!hasOwn(value, key)) problems.add(`${path}.${key}`, "required key is missing");
  }
  checkNoUnknownKeys(problems, path, value, [...required, ...optional]);
}

export function checkNoFixtureAnnotation(
  problems: Problems,
  path: string,
  value: Record<string, unknown>,
): void {
  if (hasOwn(value, FIXTURE_ONLY_KEY)) {
    problems.add(
      path,
      `carries the fixture-only key ${FIXTURE_ONLY_KEY}; a real study never emits it`,
    );
  }
}

export function checkNullableNonEmptyString(problems: Problems, path: string, value: unknown): void {
  if (!(value === null || isNonEmptyString(value))) {
    problems.add(path, "must be a non-empty string or null");
  }
}

export function checkBbl(problems: Problems, path: string, value: unknown): void {
  if (!isBbl(value)) problems.add(path, "must be a 10-digit BBL (borough 1-5)");
}

export function checkNullableBbl(problems: Problems, path: string, value: unknown): void {
  if (!(value === null || isBbl(value))) {
    problems.add(path, "must be a 10-digit BBL (borough 1-5) or null");
  }
}

export function checkDateTime(problems: Problems, path: string, value: unknown): void {
  if (!(typeof value === "string" && DATE_TIME_PATTERN.test(value))) {
    problems.add(path, "must be an RFC 3339 timestamp");
  }
}

/** A strictly positive finite number (schema: exclusiveMinimum 0). */
export function checkPositiveNumber(problems: Problems, path: string, value: unknown): void {
  if (!(isJsonNumber(value) && value > 0)) problems.add(path, "must be a number greater than 0");
}

/** An array with at least `minItems` entries; returns it for walking, or null when a problem was recorded. */
export function checkArray(
  problems: Problems,
  path: string,
  value: unknown,
  minItems = 0,
): unknown[] | null {
  if (!Array.isArray(value)) {
    problems.add(path, "must be an array");
    return null;
  }
  if (value.length < minItems) {
    problems.add(path, `must carry at least ${minItems} entries`);
    return null;
  }
  return value;
}

/** An object; returns it for walking, or null when a problem was recorded. */
export function checkObject(
  problems: Problems,
  path: string,
  value: unknown,
): Record<string, unknown> | null {
  if (typeof value === "object" && value !== null && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  problems.add(path, "must be an object");
  return null;
}
