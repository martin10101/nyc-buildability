import { describe, expect, it } from "vitest";
import {
  STATUS_CONDITIONAL,
  STATUS_NOT_KNOWN,
  presentStatus,
} from "@/lib/architect/result-status";
import type { Results } from "@/lib/architect/three-answers";
import { loadResultsFixtures } from "@/test-support/results-fixtures";

/**
 * M5-T148 part B scenario S5: the document's states mapped to the owner's screen words (ruling V3).
 * A withheld value is "Not known" with its reason and no digit; a conditional value is
 * "Conditional"; a settled value has no marker; "Verified" is never produced.
 */

type ValueState = NonNullable<
  Extract<Results["answers"]["floor_area_allowance"], { status: "available" }>["value_states"]
>[string];
type WithheldState = Extract<ValueState, { way: "withheld" }>;

const SETTLED: ValueState = { way: "settled" };
const CONDITIONAL: ValueState = {
  way: "conditional",
  conditions: [
    { kind: "user_statement", assumption: "If the lot is not in a special density area", settled_by: "a statement" },
  ],
};
const WITHHELD: WithheldState = {
  way: "withheld",
  label: "Legal dwelling-unit limit",
  reason: "The dwelling-unit formula applicability is unresolved for this lot.",
  gap_kind: "missing_information",
  resolved_by: "A statement that the lot is not in a special density area.",
};

describe("presentStatus (scenario S5)", () => {
  it("a settled value has no marker", () => {
    expect(presentStatus(SETTLED)).toEqual({ kind: "settled" });
  });

  it("an absent or null state is treated as settled (no marker)", () => {
    expect(presentStatus(undefined)).toEqual({ kind: "settled" });
    expect(presentStatus(null)).toEqual({ kind: "settled" });
  });

  it("a conditional value is 'Conditional'", () => {
    expect(presentStatus(CONDITIONAL)).toEqual({ kind: "conditional", label: STATUS_CONDITIONAL });
    expect(STATUS_CONDITIONAL).toBe("Conditional");
  });

  // Mutation proof partner: a withheld value is "Not known" with its reason and NO numeric field,
  // so presentation can never give a withheld value a digit.
  it("a withheld value is 'Not known' with its reason and no digit", () => {
    const status = presentStatus(WITHHELD);
    expect(status).toEqual({ kind: "not_known", label: STATUS_NOT_KNOWN, reason: WITHHELD.reason });
    expect(STATUS_NOT_KNOWN).toBe("Not known");
    expect(status).not.toHaveProperty("value");
    expect(status).not.toHaveProperty("number");
  });

  it("maps every value_state of every committed fixture and never produces 'Verified'", () => {
    let withheldSeen = 0;
    let conditionalSeen = 0;
    for (const { name, doc } of loadResultsFixtures()) {
      for (const key of ["floor_area_allowance", "permitted_envelope", "building_option"] as const) {
        const answer = doc.answers[key];
        if (answer.status !== "available" || !answer.value_states) continue;
        for (const [stateKey, state] of Object.entries(answer.value_states)) {
          const status = presentStatus(state);
          const where = `${name}/${key}/${stateKey}`;
          if (state.way === "withheld") {
            withheldSeen += 1;
            expect(status, where).toEqual({
              kind: "not_known",
              label: STATUS_NOT_KNOWN,
              reason: state.reason,
            });
          } else if (state.way === "conditional") {
            conditionalSeen += 1;
            expect(status, where).toEqual({ kind: "conditional", label: STATUS_CONDITIONAL });
          } else {
            expect(status, where).toEqual({ kind: "settled" });
          }
          expect(JSON.stringify(status), where).not.toContain("Verified");
        }
      }
    }
    // The benchmark carries withheld and conditional states, so the fixtures exercise both paths.
    expect(withheldSeen).toBeGreaterThan(0);
    expect(conditionalSeen).toBeGreaterThan(0);
  });
});
