// The one standing not-reviewed label (owner decision D-090-R164/R165, source-027; ADR-007).
// These tests pin the wording, the three required facts, the banned words, the panel guard and
// the a11y/standing behaviour of the component in isolation. Its exactly-once presence on each
// numbered surface is proven where those surfaces are rendered: report-view.test.tsx (the
// report), workspace/__tests__/dashboard-entry.test.tsx (the dashboard, with and without the
// report window open) and entry.test.tsx (every view of the property screen).
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  STANDING_REVIEW_BODY,
  STANDING_REVIEW_HEADING,
  STANDING_REVIEW_SENTENCE_1,
  STANDING_REVIEW_SENTENCE_2,
} from "@/lib/disclaimer";
import { StandingReviewLabel } from "../StandingReviewLabel";

afterEach(cleanup);

// The task's banned words plus their obvious variants and the compliance/approval/guarantee
// family: none of these may appear, because the tool never states a determination.
const BANNED_WORDS = [
  "complies",
  "comply",
  "compliant",
  "compliance",
  "approve",
  "approved",
  "approval",
  "guarantee",
  "guaranteed",
  "certified",
  "certify",
];
const SNAKE_CASE = /\b[a-z0-9]+(?:_[a-z0-9]+)+\b/;

function label(): HTMLElement {
  return screen.getByTestId("standing-review-label");
}

describe("StandingReviewLabel (D-090-R164/R165, ADR-007)", () => {
  it("is one role=note with the heading as its accessible name, visible without a tap", () => {
    render(<StandingReviewLabel />);
    expect(screen.getAllByRole("note")).toHaveLength(1);
    const note = screen.getByRole("note", { name: STANDING_REVIEW_HEADING });
    expect(note).toBe(label());
    // Not behind a disclosure: it is not a <details>/<summary> and is not nested in one.
    expect(note.tagName).not.toBe("DETAILS");
    expect(note.closest("details")).toBeNull();
    expect(within(note).getByText(STANDING_REVIEW_HEADING)).toBeInTheDocument();
  });

  it("carries the three required facts in plain words", () => {
    render(<StandingReviewLabel />);
    const text = label().textContent ?? "";
    // 1. computed from official sources
    expect(text).toContain("official city data");
    expect(text).toContain("Zoning Resolution");
    // 2. not reviewed by a licensed professional
    expect(text).toContain("not reviewed by a licensed architect, engineer or attorney");
    // 3. verify with one before reliance
    expect(text).toContain("verify with");
    expect(text).toContain("before you rely on them");
    // Exactly the settled heading + body, sourced from the shared constants.
    expect(text).toBe(`${STANDING_REVIEW_HEADING}${STANDING_REVIEW_BODY}`);
    expect(STANDING_REVIEW_BODY).toBe(`${STANDING_REVIEW_SENTENCE_1} ${STANDING_REVIEW_SENTENCE_2}`);
  });

  it("contains none of the banned words (never claims compliance, approval or a guarantee)", () => {
    render(<StandingReviewLabel />);
    const text = (label().textContent ?? "").toLowerCase();
    for (const word of BANNED_WORDS) expect(text).not.toContain(word);
  });

  it("survives the panel guard: no internal code or snake_case on the face", () => {
    render(<StandingReviewLabel />);
    expect(label().textContent ?? "").not.toMatch(SNAKE_CASE);
  });

  it("is not dismissible and holds no control (one label, shown always)", () => {
    render(<StandingReviewLabel />);
    const note = label();
    expect(within(note).queryByRole("button")).toBeNull();
    expect(within(note).queryByRole("checkbox")).toBeNull();
    expect(note.querySelectorAll<HTMLElement>("button, input, a, summary")).toHaveLength(0);
  });

  it("passes a hook class through while keeping the base class", () => {
    render(<StandingReviewLabel className="standing-review-label--screen" />);
    const note = label();
    expect(note).toHaveClass("standing-review-label");
    expect(note).toHaveClass("standing-review-label--screen");
  });

  it("renders the heading and the body as distinct readable elements", () => {
    render(<StandingReviewLabel />);
    const heading = label().querySelector<HTMLElement>(".standing-review-label__heading");
    const body = label().querySelector<HTMLElement>(".standing-review-label__body");
    expect(heading?.textContent).toBe(STANDING_REVIEW_HEADING);
    expect(body?.textContent).toBe(STANDING_REVIEW_BODY);
  });
});
