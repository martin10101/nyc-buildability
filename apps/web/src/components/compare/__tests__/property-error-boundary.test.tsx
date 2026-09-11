import { Component, type ReactNode } from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import PropertyError from "@/app/property/error";

/**
 * Coverage for the /property route error boundary (task M5-T004 rework; G4).
 *
 * WHY IT MATTERS MORE THAN ITS SIZE SUGGESTS. This boundary sits one level
 * ABOVE `compare/`, so it is the fallback for `/property` and
 * `/property/confirm` as well — it reaches two ACCEPTED screens. It shipped
 * with no test of any kind: neither digest branch, neither control, and not the
 * central claim that it catches at all.
 *
 * FILE LOCATION: this packet's `allowed_paths` cover the boundary file itself
 * (`apps/web/src/app/property/error.tsx`) but no test directory beside it, so
 * the test lives with the other Compare tests, as `scenario-contract.test.ts`
 * already does.
 *
 * WHAT "CATCHES AT ALL" MEANS HERE. Next.js wires `error.tsx` as the fallback
 * of a React error boundary it owns; that wiring is the framework's and cannot
 * be exercised under vitest. What CAN be proved is the contract the framework
 * relies on: that this component, used as a boundary's fallback, renders an
 * honest card for a thrown error and recovers when `reset` is called. The
 * minimal boundary below stands in for the framework's, so a regression that
 * broke the fallback — a throw during its own render, say — fails here.
 */

class TestBoundary extends Component<
  { children: ReactNode },
  { error: (Error & { digest?: string }) | null }
> {
  state: { error: (Error & { digest?: string }) | null } = { error: null };

  static getDerivedStateFromError(error: Error & { digest?: string }) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <PropertyError
          error={this.state.error}
          reset={() => this.setState({ error: null })}
        />
      );
    }
    return this.props.children;
  }
}

let shouldThrow = true;

function Thrower() {
  if (shouldThrow) {
    const error: Error & { digest?: string } = new Error(
      "lot_area.provenance.resolved is not a valid React child",
    );
    error.digest = "3405691582";
    throw error;
  }
  return <p data-testid="recovered-child">The property screen rendered.</p>;
}

// React writes the caught error to console.error; that is expected here and
// would otherwise be mistaken for a failing test in CI output.
let consoleError: ReturnType<typeof vi.spyOn>;

beforeEach(() => {
  shouldThrow = true;
  consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
});

afterEach(() => {
  consoleError.mockRestore();
  cleanup();
});

describe("PropertyError — it catches, and what it says when it does", () => {
  it("renders the honest card instead of a blank route when a child throws", () => {
    render(
      <TestBoundary>
        <Thrower />
      </TestBoundary>,
    );

    // The route is NOT blank: the boundary rendered, and the thrown child did
    // not.
    const card = screen.getByTestId("property-error-boundary");
    expect(card).toBeInTheDocument();
    expect(screen.queryByTestId("recovered-child")).toBeNull();
    expect(
      screen.getByRole("heading", { level: 1, name: "This screen could not be displayed" }),
    ).toBeInTheDocument();
    // It is announced, not silently swapped in.
    expect(card.closest('[role="alert"]')).not.toBeNull();
  });

  it("recovers the segment when reset is activated", () => {
    render(
      <TestBoundary>
        <Thrower />
      </TestBoundary>,
    );
    screen.getByTestId("property-error-boundary");

    shouldThrow = false;
    fireEvent.click(screen.getByRole("button", { name: "Try this screen again" }));

    expect(screen.getByTestId("recovered-child")).toBeInTheDocument();
    expect(screen.queryByTestId("property-error-boundary")).toBeNull();
  });
});

describe("PropertyError — it leaks nothing and states what is and is not true", () => {
  it("shows the opaque digest and NEVER the error message", () => {
    // A message shaped like the internal detail a real throw carries — a host,
    // a path, a stack frame. Deliberately NOT a credential-shaped literal: this
    // repository's secret scan treats those as findings wherever they appear,
    // and a test fixture is not worth a red scan job.
    const error: Error & { digest?: string } = new Error(
      "INTERNAL-ONLY at services/api/app/scenario/builder.py:171 host=db-internal-7",
    );
    error.digest = "3405691582";
    render(<PropertyError error={error} reset={() => {}} />);

    expect(screen.getByTestId("property-error-digest")).toHaveTextContent("3405691582");
    const card = screen.getByTestId("property-error-boundary");
    expect(card.textContent).not.toContain("INTERNAL-ONLY");
    expect(card.textContent).not.toContain("db-internal-7");
    expect(card.textContent).not.toContain("builder.py");
  });

  it("omits the reference line entirely when there is no digest", () => {
    render(<PropertyError error={new Error("boom")} reset={() => {}} />);

    expect(screen.queryByTestId("property-error-digest")).toBeNull();
    // Still a complete, honest card — not a degraded one.
    expect(screen.getByTestId("property-error-boundary")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Try this screen again" })).toBeInTheDocument();
  });

  it("says nothing was determined, and keeps the internal banner and a way out", () => {
    render(<PropertyError error={new Error("boom")} reset={() => {}} />);

    const card = screen.getByTestId("property-error-boundary");
    // A partially rendered analysis is not an analysis — the card says so
    // rather than implying a refresh is all that is needed.
    expect(card).toHaveTextContent("Nothing was determined");
    expect(card).toHaveTextContent("should be relied on");
    expect(screen.getByTestId("internal-banner")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Back to property lookup" }),
    ).toHaveAttribute("href", "/property");
  });

  it("invokes reset exactly once per activation", () => {
    const reset = vi.fn();
    render(<PropertyError error={new Error("boom")} reset={reset} />);

    fireEvent.click(screen.getByRole("button", { name: "Try this screen again" }));
    expect(reset).toHaveBeenCalledTimes(1);
  });
});
