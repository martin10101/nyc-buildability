import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  dashboardFailureNotice,
  type DashboardFailureOutcome,
} from "../dashboard-failure";
import { DashboardFailureNotice } from "../DashboardFailureNotice";

afterEach(cleanup);

// A distinctive correlation id so a test can prove it never reaches the face (plan §5a item 5).
const REF = "corr-abc-123";

// One representative outcome per documented lookup failure (src/lib/api.ts). Each is exactly its
// union member's shape, so a contract field rename fails this file.
const OUTCOMES: Record<string, DashboardFailureOutcome> = {
  no_match: { kind: "no_match", bbl: "1000010010", message: "Enter the billing lot.", correlationId: REF },
  validation_error: { kind: "validation_error", code: "invalid_block", message: "Block is out of range.", correlationId: REF },
  rate_limited: { kind: "upstream_failure", state: "rate_limited", httpStatus: 429, message: "x", correlationId: REF },
  source_unavailable: { kind: "upstream_failure", state: "source_unavailable", httpStatus: 503, message: "x", correlationId: REF },
  timeout_upstream: { kind: "upstream_failure", state: "timeout", httpStatus: 504, message: "x", correlationId: REF },
  schema_drift: { kind: "upstream_failure", state: "schema_drift", httpStatus: 502, message: "x", correlationId: REF },
  internal_error: { kind: "internal_error", message: "x", correlationId: REF },
  server_contract_error: { kind: "server_contract_error", state: "internal_contract_error", message: "x", correlationId: REF },
  validation_failure: { kind: "validation_failure", problems: ["answers[0].value: missing"], correlationId: REF },
  network_error: { kind: "network_error", message: "The network request failed before a reply." },
  client_timeout: { kind: "client_timeout", timeoutMs: 12000 },
  unexpected_response: { kind: "unexpected_response", httpStatus: 500, receivedState: "no_match", correlationId: REF },
  aborted: { kind: "aborted" },
};

describe("dashboardFailureNotice (plan §5a failure notices, queue D-03)", () => {
  it("returns no notice for a superseded (aborted) request", () => {
    expect(dashboardFailureNotice(OUTCOMES.aborted)).toBeNull();
  });

  it("keeps every internal code off the face and only in the technical details (§5a item 5)", () => {
    for (const [name, outcome] of Object.entries(OUTCOMES)) {
      const notice = dashboardFailureNotice(outcome);
      if (!notice) continue;
      const face = `${notice.title} ${notice.body} ${notice.recovery}`;
      const codes = notice.technical.map(detail => detail.value);
      // The reference id, the HTTP status, the machine state and the rejection code are codes:
      // they appear in `technical` and never on the plain face.
      expect(face, `${name} face has no reference id`).not.toContain(REF);
      for (const code of codes) {
        expect(face, `${name} face has no code "${code}"`).not.toContain(code);
      }
      if (outcome.kind !== "network_error" && outcome.kind !== "client_timeout") {
        expect(codes, `${name} carries its reference id behind details`).toContain(REF);
      }
    }
  });

  it("marks a source outage and an app-side fault retryable, but a no-match / rejected id not", () => {
    expect(dashboardFailureNotice(OUTCOMES.source_unavailable)?.retryable).toBe(true);
    expect(dashboardFailureNotice(OUTCOMES.internal_error)?.retryable).toBe(true);
    expect(dashboardFailureNotice(OUTCOMES.network_error)?.retryable).toBe(true);
    expect(dashboardFailureNotice(OUTCOMES.no_match)?.retryable).toBe(false);
    expect(dashboardFailureNotice(OUTCOMES.validation_error)?.retryable).toBe(false);
  });

  it("names the client timeout in whole seconds on the face, with no code behind it", () => {
    const notice = dashboardFailureNotice(OUTCOMES.client_timeout);
    expect(notice?.body).toContain("within 12 seconds");
    expect(notice?.technical).toHaveLength(0);
  });

  it("lists each client-validation problem as its own technical row", () => {
    const notice = dashboardFailureNotice(OUTCOMES.validation_failure);
    expect(notice?.technical.filter(detail => detail.label === "Format problem")).toHaveLength(1);
  });
});

describe("DashboardFailureNotice component (plan §5a)", () => {
  it("renders a plain title and body, with the codes hidden until the details are tapped", () => {
    const { container } = render(
      <DashboardFailureNotice outcome={OUTCOMES.source_unavailable} onRetry={vi.fn()} />,
    );
    expect(screen.getByTestId("dashboard-failure-title")).toHaveTextContent(
      "The city data source could not be reached",
    );
    // The reference id, HTTP status and machine state live inside the details, not on the face.
    const technical = screen.getByTestId("dashboard-failure-technical");
    expect(within(technical).getByText(REF)).toBeInTheDocument();
    expect(within(technical).getByText("503")).toBeInTheDocument();
    expect(within(technical).getByText("source_unavailable")).toBeInTheDocument();
    expect(screen.getByTestId("dashboard-failure-title")).not.toHaveTextContent(REF);
    expect(screen.getByTestId("dashboard-failure-body")).not.toHaveTextContent("503");
    // The details element starts closed, so the codes are not shown until the architect taps it.
    expect(technical).not.toHaveAttribute("open");
    const codeNodes = container.querySelectorAll<HTMLElement>("p code");
    expect(codeNodes).toHaveLength(0);
  });

  it("offers one Try again for a recoverable fault and calls back on click", () => {
    const onRetry = vi.fn();
    render(<DashboardFailureNotice outcome={OUTCOMES.internal_error} onRetry={onRetry} />);
    fireEvent.click(screen.getByTestId("dashboard-failure-retry"));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("offers no Try again when retrying cannot help (no city record)", () => {
    render(<DashboardFailureNotice outcome={OUTCOMES.no_match} onRetry={vi.fn()} />);
    expect(screen.queryByTestId("dashboard-failure-retry")).not.toBeInTheDocument();
    expect(screen.getByTestId("dashboard-failure-body")).toHaveTextContent("BBL 1000010010");
  });

  it("renders nothing for a superseded (aborted) request", () => {
    const { container } = render(
      <DashboardFailureNotice outcome={OUTCOMES.aborted} onRetry={vi.fn()} />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});
