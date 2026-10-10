import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ResultDetails } from "../ResultDetails";

/**
 * ResultDetails — the on-demand detail of one answer (presentation contract §2 item 7, §4; M5-T149
 * part A; acceptance UX-09). It is a focus-managed disclosure: a button opens a region, focus moves
 * into the region, and Escape closes it and returns focus to the button. Its content stays in the
 * DOM when closed (the `hidden` attribute), so assistive technology and in-page search still reach
 * the derivation. It renders no content of its own — the caller passes it as children.
 */

afterEach(cleanup);

function renderDetails() {
  return render(
    <ResultDetails name="Floor-area allowance">
      <p data-testid="detail-child">A derivation row.</p>
    </ResultDetails>,
  );
}

describe("ResultDetails focus and disclosure behaviour", () => {
  it("starts closed: a button whose region is hidden but present in the DOM", () => {
    renderDetails();
    const button = screen.getByTestId("answer-details-button");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(button.textContent).toBe("Details");
    const region = screen.getByTestId("answer-details-region");
    expect(region).toHaveAttribute("hidden");
    // the child content is in the DOM even while hidden (in-page search / assistive tech reach it)
    expect(within(region).getByTestId("detail-child").textContent).toBe("A derivation row.");
  });

  it("names the region for assistive technology with the answer's title", () => {
    renderDetails();
    expect(screen.getByTestId("answer-details-region").getAttribute("aria-label")).toBe(
      "Details — Floor-area allowance",
    );
  });

  it("opening moves focus into the region; the button reports expanded", () => {
    renderDetails();
    const button = screen.getByTestId<HTMLButtonElement>("answer-details-button");
    const region = screen.getByTestId<HTMLDivElement>("answer-details-region");
    fireEvent.click(button);
    expect(region).not.toHaveAttribute("hidden");
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(button.textContent).toBe("Hide details");
    expect(document.activeElement).toBe(region);
  });

  it("Escape closes the region and returns focus to the button", () => {
    renderDetails();
    const button = screen.getByTestId<HTMLButtonElement>("answer-details-button");
    const region = screen.getByTestId<HTMLDivElement>("answer-details-region");
    fireEvent.click(button);
    expect(document.activeElement).toBe(region);
    fireEvent.keyDown(region, { key: "Escape" });
    expect(region).toHaveAttribute("hidden");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(document.activeElement).toBe(button);
  });

  it("W2: each opener has a distinguishing accessible name (so several 'Details' do not collide)", () => {
    render(
      <>
        <ResultDetails name="Floor-area allowance">
          <p>a</p>
        </ResultDetails>
        <ResultDetails name="Permitted envelope">
          <p>b</p>
        </ResultDetails>
      </>,
    );
    const buttons = screen.getAllByTestId("answer-details-button");
    expect(buttons).toHaveLength(2);
    const names = buttons.map(b => b.getAttribute("aria-label"));
    expect(names[0]).toBe("Details — Floor-area allowance");
    expect(names[1]).toBe("Details — Permitted envelope");
    expect(names[0]).not.toBe(names[1]);
    // the visible label stays the generic toggle text.
    expect(buttons[0].textContent).toBe("Details");
  });

  it("the button toggles closed again on a second click", () => {
    renderDetails();
    const button = screen.getByTestId<HTMLButtonElement>("answer-details-button");
    const region = screen.getByTestId<HTMLDivElement>("answer-details-region");
    fireEvent.click(button);
    expect(region).not.toHaveAttribute("hidden");
    fireEvent.click(button);
    expect(region).toHaveAttribute("hidden");
  });
});
