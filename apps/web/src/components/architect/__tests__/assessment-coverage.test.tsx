import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Scenario } from "@/lib/scenario-contract";
import { AssessmentCoverage } from "../AssessmentCoverage";

afterEach(cleanup);

// AssessmentCoverage reads only `coverage_matrix`; the full Scenario shape is not exercised here,
// so a focused partial is cast for the prop (CODING_RULES: deliberate partial via `as unknown`).
const scenario = {
  coverage_matrix: [
    { constraint_family: "residential_far_cap", rule_status_today: "Assessed", blocks_buildable_envelope: false },
    { constraint_family: "height_limit", rule_status_today: "Open", blocks_buildable_envelope: true },
  ],
} as unknown as Scenario;

describe("D-03 slice 5 rework — AssessmentCoverage shows plain check labels, no raw engine code (§5a item 5)", () => {
  it("renders the human label for each check and emits no raw snake_case constraint_family code", () => {
    const { container } = render(<AssessmentCoverage scenario={scenario} />);
    // Plain labels are shown.
    expect(screen.getByText("Residential FAR cap")).toBeInTheDocument();
    expect(screen.getByText("Height")).toBeInTheDocument();
    // No internal code on the face: the removed .architect-source-key <code> is gone and the raw
    // snake_case tokens never render as text anywhere in the coverage surface. Reverting the fix
    // (re-adding the <code>) puts "residential_far_cap" back into textContent and reddens this.
    expect(container.querySelector(".architect-source-key")).toBeNull();
    expect(container.textContent).not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);
  });
});
