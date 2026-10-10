import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ReportPreview } from "../ReportPreview";
import type { ReportRequestBody } from "@/lib/report-api";

/**
 * M5-T153 scenario S4: the report action in the Results window (controlled) and in the workspace
 * report tool (withInputs). It loads the report, shows it in a no-script sandboxed frame, prints
 * from the parent, and — after the inputs change — marks the shown report OUT OF DATE and disables
 * printing until it is reloaded. The route is stubbed with ruling X9 d's shape (a text/html string).
 */

afterEach(cleanup);

const BBL = "4073340070";
const STANDARD: ReportRequestBody = { housing_program: "standard_residence" };
const REPORT_HTML = "<!doctype html><html><body><h1>Decision summary</h1></body></html>";

function htmlResponse(html: string, status = 200): Response {
  return new Response(html, { status, headers: { "Content-Type": "text/html; charset=utf-8" } });
}
function jsonResponse(body: unknown, status: number): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}
function stub(response: Response) {
  return (async () => response) as typeof fetch;
}

describe("ReportPreview — the report action (controlled mode)", () => {
  it("loads the report on Create and shows it in a no-script sandboxed frame with a Print control", async () => {
    render(<ReportPreview bbl={BBL} request={STANDARD} fetchImpl={stub(htmlResponse(REPORT_HTML))} />);
    fireEvent.click(screen.getByTestId("report-create"));
    const frame = await screen.findByTestId("report-frame");
    // The frame runs NO script; the only sandbox tokens are what printing from the parent needs.
    expect(frame.getAttribute("sandbox")).toBe("allow-same-origin allow-modals");
    expect(frame.getAttribute("sandbox")).not.toContain("allow-scripts");
    expect(frame.getAttribute("srcdoc")).toBe(REPORT_HTML);
    const print = screen.getByTestId("report-print");
    expect(print).not.toBeDisabled();
  });

  it("shows a loading state while the report is being prepared", async () => {
    let resolve!: (r: Response) => void;
    const pending = new Promise<Response>(r => {
      resolve = r;
    });
    render(<ReportPreview bbl={BBL} request={STANDARD} fetchImpl={(async () => pending) as typeof fetch} />);
    fireEvent.click(screen.getByTestId("report-create"));
    expect(await screen.findByTestId("report-loading")).toBeInTheDocument();
    resolve(htmlResponse(REPORT_HTML));
    await screen.findByTestId("report-frame");
  });

  it("shows plain words for a not-available route, a refusal, and a failed fetch — no developer text", async () => {
    render(<ReportPreview bbl={BBL} request={STANDARD} fetchImpl={stub(jsonResponse({}, 404))} />);
    fireEvent.click(screen.getByTestId("report-create"));
    const notAvailable = await screen.findByTestId("report-not-available");
    expect(notAvailable.textContent ?? "").not.toMatch(/404|\/report/);
    cleanup();

    const message = "The report is not available for this lot until a record can be read.";
    render(
      <ReportPreview bbl={BBL} request={STANDARD} fetchImpl={stub(jsonResponse({ message }, 503))} />,
    );
    fireEvent.click(screen.getByTestId("report-create"));
    expect((await screen.findByTestId("report-refused")).textContent).toBe(message);
    cleanup();

    render(
      <ReportPreview
        bbl={BBL}
        request={STANDARD}
        fetchImpl={(async () => {
          throw new Error("ECONNRESET");
        }) as typeof fetch}
      />,
    );
    fireEvent.click(screen.getByTestId("report-create"));
    const error = await screen.findByTestId("report-error");
    expect(error.textContent ?? "").not.toMatch(/ECONNRESET|500|fetch/i);
  });

  it("marks the report out of date after the inputs change and DISABLES printing until reloaded", async () => {
    const { rerender } = render(
      <ReportPreview bbl={BBL} request={STANDARD} fetchImpl={stub(htmlResponse(REPORT_HTML))} />,
    );
    fireEvent.click(screen.getByTestId("report-create"));
    await screen.findByTestId("report-frame");
    expect(screen.getByTestId("report-print")).not.toBeDisabled();

    // An input changed: the SAME loaded report is now for the earlier inputs.
    rerender(
      <ReportPreview
        bbl={BBL}
        request={{ housing_program: "standard_residence", floor_to_floor_ft: 14 }}
        fetchImpl={stub(htmlResponse(REPORT_HTML))}
      />,
    );
    expect(screen.getByTestId("report-stale")).toBeInTheDocument();
    expect(screen.getByTestId("report-print")).toBeDisabled();
    // The action now offers to update the report.
    expect(screen.getByTestId("report-create").textContent).toBe("Update report");
  });

  it("disables Create when the current inputs are not valid (no body to send)", () => {
    render(<ReportPreview bbl={BBL} request={null} fetchImpl={stub(htmlResponse(REPORT_HTML))} />);
    expect(screen.getByTestId("report-create")).toBeDisabled();
    expect(screen.getByTestId("report-invalid-inputs")).toBeInTheDocument();
  });
});

describe("ReportPreview — the workspace report tool (withInputs)", () => {
  it("renders the results inputs form and loads the report from it", async () => {
    const fetchImpl = vi.fn(async () => htmlResponse(REPORT_HTML));
    render(<ReportPreview bbl={BBL} withInputs fetchImpl={fetchImpl as unknown as typeof fetch} />);
    expect(screen.getByTestId("results-form")).toBeInTheDocument();
    fireEvent.click(screen.getByTestId("report-create"));
    await screen.findByTestId("report-frame");
    const [, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
    expect(JSON.parse(String(init.body))).toEqual({ housing_program: "standard_residence" });
  });

  it("refuses a non-positive height and sends no request", async () => {
    const fetchImpl = vi.fn(async () => htmlResponse(REPORT_HTML));
    render(<ReportPreview bbl={BBL} withInputs fetchImpl={fetchImpl as unknown as typeof fetch} />);
    fireEvent.change(screen.getByTestId("results-floor-to-floor"), { target: { value: "0" } });
    fireEvent.submit(screen.getByTestId("results-form"));
    await waitFor(() =>
      expect(screen.getByTestId("results-floor-to-floor-error")).toBeInTheDocument(),
    );
    expect(fetchImpl).not.toHaveBeenCalled();
  });
});
