import { describe, expect, it } from "vitest";
import { classifyResponse, isResponseCurrent, type ResponseDecision } from "../study-revision";

/**
 * The late-response rule (task C-06, plan M1-11; plan section 9 "Late responses
 * never overwrite newer ones"). A response is applied only when its token equals
 * the option's current revision; any other token is dropped and recorded as
 * ignored, never applied.
 */
describe("classifyResponse (late-response token comparison)", () => {
  const cases: ReadonlyArray<{
    label: string;
    response: number;
    current: number;
    expected: ResponseDecision;
  }> = [
    {
      label: "equal token -> applied",
      response: 7,
      current: 7,
      expected: { apply: true },
    },
    {
      label: "older token -> dropped as a stale response",
      response: 6,
      current: 7,
      expected: { apply: false, ignored: "stale_response", responseRevision: 6, currentRevision: 7 },
    },
    {
      label: "much older token -> dropped as a stale response",
      response: 1,
      current: 9,
      expected: { apply: false, ignored: "stale_response", responseRevision: 1, currentRevision: 9 },
    },
    {
      label: "newer token -> fail closed, dropped as a revision mismatch",
      response: 8,
      current: 7,
      expected: { apply: false, ignored: "revision_mismatch", responseRevision: 8, currentRevision: 7 },
    },
  ];

  it.each(cases)("$label", ({ response, current, expected }) => {
    expect(classifyResponse(response, current)).toEqual(expected);
  });

  it("isResponseCurrent is true only for the exact current revision", () => {
    expect(isResponseCurrent(7, 7)).toBe(true);
    expect(isResponseCurrent(6, 7)).toBe(false);
    expect(isResponseCurrent(8, 7)).toBe(false);
  });
});
