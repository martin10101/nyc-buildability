import { describe, expect, it } from "vitest";
import {
  BLOCKED_OUTPUTS,
  STUDY_ENUM_ASSERTIONS,
  type BlockedOutput,
  type MutuallyEqual,
} from "../study-vocabulary";

/**
 * Review correction 3: the enum lock must actually fail on drift. Part of this
 * test is checked by `tsc` (the web CI typecheck), not by vitest: the
 * `@ts-expect-error` line below MUST be a type error. If the proof ever stops
 * rejecting a drifted enum, that line compiles, the directive is unused, and
 * `tsc` fails.
 */

/** A runtime array that misses members of the contract union BlockedOutput. */
const DRIFTED_BLOCKED_OUTPUTS = ["floor_area_allowance", "remaining_floor_area"] as const;

describe("enum lock between the runtime arrays and the generated contract unions", () => {
  it("binds one proof slot per locked array to a value", () => {
    expect(STUDY_ENUM_ASSERTIONS).toHaveLength(14);
    expect(STUDY_ENUM_ASSERTIONS.every((slot) => slot === true)).toBe(true);
  });

  it("binding a proof tuple accepts the committed array and rejects a drifted one (compile-time)", () => {
    // The same shape as STUDY_ENUM_ASSERTIONS: a proof tuple bound to `true` values.
    const committed: [MutuallyEqual<BlockedOutput, (typeof BLOCKED_OUTPUTS)[number]>] = [true];
    // @ts-expect-error -- the drifted array misses union members, so the slot is `never` and `true` is refused
    const drifted: [MutuallyEqual<BlockedOutput, (typeof DRIFTED_BLOCKED_OUTPUTS)[number]>] = [true];
    expect([...committed, ...drifted]).toEqual([true, true]);
  });
});
