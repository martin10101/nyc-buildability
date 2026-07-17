import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PropertyLookup } from "@/components/property/PropertyLookup";
import {
  baseProfile,
  cr500NoMatchResponse,
  jsonResponse,
  partialProfile,
} from "@/test-support/fixtures";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function submitBbl(value: string) {
  fireEvent.change(screen.getByLabelText("BBL"), { target: { value } });
  fireEvent.click(screen.getByRole("button", { name: "Look up property" }));
}

describe("PropertyLookup — client validation before network (S3)", () => {
  it("shows a validation message for '1-00001-0100' and never calls fetch", async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(<PropertyLookup />);
    submitBbl("1-00001-0100");
    expect(await screen.findByTestId("client-validation-error")).toHaveTextContent(
      "digits only",
    );
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("shows a length message for '123' and never calls fetch", async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(<PropertyLookup />);
    submitBbl("123");
    expect(await screen.findByTestId("client-validation-error")).toHaveTextContent(
      "exactly 10 digits",
    );
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});

describe("PropertyLookup — profile rendering (S1/S2)", () => {
  it("renders the split-zone profile: districts, units, coverage wording, counts", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(baseProfile(), 200)),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");

    // Identity and both split-zone districts visible. (getAllByText:
    // district codes also appear inside their provenance drill-downs.)
    expect(screen.getByText("BBL 1000010010")).toBeInTheDocument();
    expect(screen.getAllByText("R3-2").length).toBeGreaterThan(0);
    expect(screen.getAllByText("C4-1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("GI").length).toBeGreaterThan(0);

    // Fact value with units (lotarea 7,577,714 square feet).
    expect(screen.getAllByText("7,577,714").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/square feet/).length).toBeGreaterThan(0);

    // Coverage labels use the exact PRD section 12 enum wording.
    expect(screen.getAllByText("conditional").length).toBeGreaterThan(0);

    // data_completeness banner shows the exact enum value. M2-T004 corrected
    // the completeness basis (documented 19-column feasibility set replaces the
    // 108-column denominator), so the F05 ground-truth fixture now reads
    // "complete" (G1/G3 correction C1/D1, orchestrator-authorized).
    expect(screen.getByTestId("completeness-banner")).toHaveTextContent(
      "complete",
    );

    // Missing inputs: total count always visible (fixture has 24 entries).
    expect(
      screen.getByRole("heading", { name: /Missing official inputs \(24\)/ }),
    ).toBeInTheDocument();

    // No conflicts in this profile -> explicit empty state, never hidden.
    expect(
      screen.getByText(/No cross-source conflicts were detected/),
    ).toBeInTheDocument();

    // Honesty: no status badge claims "verified" and "best" appears nowhere.
    expect(document.body.textContent).not.toMatch(/\bbest\b/i);
    expect(document.querySelector(".status-verified")).toBeNull();
  });

  it("tolerates absent identity.address and geometry (S6 partial data)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(partialProfile(), 200)),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");
    expect(
      screen.getByText(/No address could be stated for this lot/),
    ).toBeInTheDocument();
  });
});

describe("PropertyLookup — failure states and retry (S5)", () => {
  it("renders a typed 503 state and recovers via Retry", async () => {
    const fetchStub = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ state: "source_unavailable", message: "outage" }, 503),
      )
      .mockResolvedValueOnce(jsonResponse(baseProfile(), 200));
    vi.stubGlobal("fetch", fetchStub);
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-source_unavailable");
    expect(screen.getByText(/Retrying is safe/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Retry lookup" }));
    await screen.findByTestId("profile-view");
    expect(fetchStub).toHaveBeenCalledTimes(2);
  });

  it("renders the generic 500 state with its correlation id", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(
          { state: "internal_error", message: "generic" },
          500,
          "corr-internal-1",
        ),
      ),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-internal-error");
    expect(screen.getByTestId("correlation-id")).toHaveTextContent("corr-internal-1");
  });

  it("renders the recoverable network-failure state when fetch throws", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("fetch failed");
      }),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-network-error");
    expect(screen.getByRole("button", { name: "Retry lookup" })).toBeInTheDocument();
  });

  it("renders 422 detail.code when the server rejects a BBL the client allowed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(
          {
            state: "validation_error",
            message: "BBL tax block must be 1-99999; got '00000'",
            detail: { code: "invalid_block", raw_value: "'1000000000'" },
          },
          422,
        ),
      ),
    );
    render(<PropertyLookup />);
    submitBbl("1000000000"); // passes the client mirror (documented gap)
    await screen.findByTestId("state-validation-error");
    expect(screen.getByTestId("validation-code")).toHaveTextContent("invalid_block");
    expect(screen.getByTestId("validation-message")).toHaveTextContent("tax block");
  });
});

describe("PropertyLookup — hardened boundary (M2-T002 S2/S3)", () => {
  it("S2 BLOCKING: the recorded 500+no_match fixture renders unexpected_response, NEVER the no-match screen", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => cr500NoMatchResponse()),
    );
    render(<PropertyLookup />);
    submitBbl("5999999999");
    await screen.findByTestId("state-unexpected-response");
    expect(screen.queryByTestId("state-no-match")).toBeNull();
    // The mismatch is inspectable: status, state, and correlation id shown.
    expect(screen.getByTestId("unexpected-state")).toHaveTextContent("no_match");
    expect(screen.getByTestId("correlation-id")).toHaveTextContent(
      "cr500nomatch00000000000000000000",
    );
    // Nothing from the untrusted body is rendered as a result.
    expect(screen.queryByText(/No PLUTO record exists/)).toBeNull();
  });

  it("S3: a 200 failing runtime validation renders the validation-failure state with NOTHING partially rendered", async () => {
    const broken = baseProfile() as unknown as Record<string, unknown>;
    delete broken.provenance;
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(broken, 200)),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-validation-failure");
    expect(screen.queryByTestId("profile-view")).toBeNull();
    expect(screen.queryByTestId("identity-card")).toBeNull();
    // No value from the invalid payload appears anywhere.
    expect(screen.queryByText("7,577,714")).toBeNull();
    expect(screen.queryByText("R3-2")).toBeNull();
  });

  it("renders the typed server-contract-error state for 500 internal_contract_error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(
          { state: "internal_contract_error", message: "refused", detail: { reason: "schema_validation_failed" } },
          500,
          "corr-contract-1",
        ),
      ),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-server-contract-error");
    expect(screen.getByTestId("correlation-id")).toHaveTextContent("corr-contract-1");
  });
});

describe("PropertyLookup — D5: previous profile survives a later invalid submit (S4)", () => {
  it("keeps the rendered profile with an inline error, and clears the error on retype", async () => {
    const fetchStub = vi.fn(async () => jsonResponse(baseProfile(), 200));
    vi.stubGlobal("fetch", fetchStub);
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");

    // Follow-up CLIENT-invalid submit: profile stays, inline error shows,
    // and no network call is made.
    submitBbl("123");
    expect(await screen.findByTestId("client-validation-error")).toHaveTextContent(
      "exactly 10 digits",
    );
    expect(screen.getByTestId("profile-view")).toBeInTheDocument();
    expect(screen.getByTestId("identity-card")).toHaveTextContent("BBL 1000010010");
    expect(fetchStub).toHaveBeenCalledTimes(1);

    // D5 second part: the inline error clears as soon as the user edits.
    fireEvent.change(screen.getByLabelText("BBL"), { target: { value: "1000" } });
    expect(screen.queryByTestId("client-validation-error")).toBeNull();
    expect(screen.getByTestId("profile-view")).toBeInTheDocument();
  });

  it("supersession: a rapid resubmit aborts the stale request and only the newest result renders", async () => {
    // First request hangs until aborted; second resolves with the profile.
    let call = 0;
    const fetchStub = vi.fn((_url: unknown, init?: RequestInit) => {
      call += 1;
      if (call === 1) {
        return new Promise<Response>((resolve, reject) => {
          init?.signal?.addEventListener("abort", () =>
            reject(new DOMException("aborted", "AbortError")),
          );
        });
      }
      return Promise.resolve(jsonResponse(baseProfile(), 200));
    });
    vi.stubGlobal("fetch", fetchStub);
    render(<PropertyLookup />);
    submitBbl("1000010100"); // stale request (hangs)
    submitBbl("1000010010"); // supersedes and aborts it
    await screen.findByTestId("profile-view");
    expect(screen.getByTestId("identity-card")).toHaveTextContent("BBL 1000010010");
    expect(fetchStub).toHaveBeenCalledTimes(2);
    // The first request was actively cancelled.
    const firstInit = fetchStub.mock.calls[0][1] as RequestInit;
    expect((firstInit.signal as AbortSignal).aborted).toBe(true);
  });
});

describe("PropertyLookup — coverage legend (M2-T002 D3)", () => {
  it("shows the always-visible legend with the gloss for every status present", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(baseProfile(), 200)),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");
    const legend = screen.getByTestId("coverage-legend");
    expect(legend).toHaveTextContent("What the coverage labels mean");
    // The F05 profile carries only `conditional` facts: its gloss is
    // visible WITHOUT hover; no status badge exists for absent statuses.
    expect(legend).toHaveTextContent(
      "Official source fact, not yet professionally reviewed.",
    );
    expect(legend.querySelectorAll(".status-badge.status-verified").length).toBe(0);
  });
});

describe("PropertyLookup — honesty affordances (S7)", () => {
  it("shows the disabled address entry with honest copy", () => {
    vi.stubGlobal("fetch", vi.fn());
    render(<PropertyLookup />);
    const addressInput = screen.getByLabelText(/Address \(not yet available\)/);
    expect(addressInput).toBeDisabled();
    expect(screen.getByTestId("address-disabled-copy")).toHaveTextContent(
      "credentials are still pending",
    );
  });
});

/**
 * M2-T005 D1 (scenarios S1/S2): every failure state and the success
 * arrival is announced EXACTLY ONCE through the persistent live region,
 * and focus lands deterministically on the outcome heading — never body.
 */

/** All live regions currently containing `text` (exactly-once check). */
function liveRegionsContaining(text: string): Element[] {
  return Array.from(
    document.querySelectorAll('[aria-live], [role="alert"], [role="status"]'),
  ).filter((el) => (el.textContent ?? "").includes(text));
}

const FAILURE_ANNOUNCEMENT_CASES: Array<{
  name: string;
  bbl: string;
  stubImpl: () => Promise<Response>;
  testId: string;
  announcement: string;
  heading: string;
}> = [
  {
    name: "no_match",
    bbl: "5999999999",
    stubImpl: async () =>
      jsonResponse({ state: "no_match", bbl: "5999999999", message: "none" }, 404),
    testId: "state-no-match",
    announcement: "Lookup complete: no property record found in the official dataset.",
    heading: "No property record found",
  },
  {
    name: "validation_error",
    bbl: "1000000000",
    stubImpl: async () =>
      jsonResponse(
        {
          state: "validation_error",
          message: "BBL tax block must be 1-99999; got '00000'",
          detail: { code: "invalid_block", raw_value: "'1000000000'" },
        },
        422,
      ),
    testId: "state-validation-error",
    announcement: "Lookup rejected: the API rejected this BBL.",
    heading: "The API rejected this BBL",
  },
  {
    name: "upstream rate_limited",
    bbl: "1000010010",
    stubImpl: async () => jsonResponse({ state: "rate_limited", message: "m" }, 503),
    testId: "state-rate_limited",
    announcement: "Lookup failed: the official data source is throttling requests.",
    heading: "The official data source is throttling requests",
  },
  {
    name: "upstream source_unavailable",
    bbl: "1000010010",
    stubImpl: async () => jsonResponse({ state: "source_unavailable", message: "m" }, 503),
    testId: "state-source_unavailable",
    announcement: "Lookup failed: the official data source is unavailable.",
    heading: "The official data source is unavailable",
  },
  {
    name: "upstream timeout",
    bbl: "1000010010",
    stubImpl: async () => jsonResponse({ state: "timeout", message: "m" }, 504),
    testId: "state-timeout",
    announcement: "Lookup failed: the official data source timed out.",
    heading: "The official data source timed out",
  },
  {
    name: "upstream schema_drift",
    bbl: "1000010010",
    stubImpl: async () => jsonResponse({ state: "schema_drift", message: "m" }, 502),
    testId: "state-schema_drift",
    announcement: "Lookup failed: the official dataset changed shape.",
    heading: "The official dataset changed shape",
  },
  {
    name: "internal_error",
    bbl: "1000010010",
    stubImpl: async () => jsonResponse({ state: "internal_error", message: "m" }, 500),
    testId: "state-internal-error",
    announcement: "Lookup failed: something went wrong on our side.",
    heading: "Something went wrong on our side",
  },
  {
    name: "server_contract_error",
    bbl: "1000010010",
    stubImpl: async () =>
      jsonResponse({ state: "internal_contract_error", message: "refused" }, 500),
    testId: "state-server-contract-error",
    announcement: "Lookup failed: the server refused to deliver an invalid profile.",
    heading: "The server refused to deliver an invalid profile",
  },
  {
    name: "validation_failure",
    bbl: "1000010010",
    stubImpl: async () => {
      const broken = baseProfile() as unknown as Record<string, unknown>;
      delete broken.provenance;
      return jsonResponse(broken, 200);
    },
    testId: "state-validation-failure",
    announcement: "Lookup failed: the response did not match the published data contract.",
    heading: "The response did not match the published data contract",
  },
  {
    name: "network_error",
    bbl: "1000010010",
    stubImpl: async () => {
      throw new TypeError("fetch failed");
    },
    testId: "state-network-error",
    announcement: "Lookup failed: the platform API could not be reached.",
    heading: "Could not reach the platform API",
  },
  {
    name: "unexpected_response (recorded 500+no_match)",
    bbl: "5999999999",
    stubImpl: async () => cr500NoMatchResponse(),
    testId: "state-unexpected-response",
    announcement: "Lookup failed: unexpected response from the platform API.",
    heading: "Unexpected response from the platform API",
  },
];

describe("PropertyLookup — a11y announcement + focus on every failure state (M2-T005 S1/S2)", () => {
  it.each(FAILURE_ANNOUNCEMENT_CASES)(
    "$name is announced exactly once and focuses the failure heading",
    async ({ bbl, stubImpl, testId, announcement, heading }) => {
      vi.stubGlobal("fetch", vi.fn(stubImpl));
      render(<PropertyLookup />);
      submitBbl(bbl);
      await screen.findByTestId(testId);

      // Announcement: emitted by the persistent announcer, exactly once.
      expect(screen.getByTestId("outcome-announcer")).toHaveTextContent(announcement);
      expect(liveRegionsContaining(announcement)).toHaveLength(1);

      // The failure card itself is NOT a second live source.
      const card = screen.getByTestId(testId);
      expect(card).not.toHaveAttribute("role", "alert");
      expect(card).not.toHaveAttribute("aria-live");

      // Focus: lands on the outcome heading, never body.
      const headingEl = screen.getByRole("heading", { name: heading });
      expect(headingEl).toHaveAttribute("data-outcome-heading");
      await waitFor(() => expect(document.activeElement).toBe(headingEl));
      expect(document.activeElement).not.toBe(document.body);
    },
  );

  it("success arrival is announced exactly once and focuses the profile heading", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(baseProfile(), 200)));
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");

    const announcement =
      "Lookup complete: official property profile loaded for BBL 1000010010.";
    expect(screen.getByTestId("outcome-announcer")).toHaveTextContent(announcement);
    expect(liveRegionsContaining("profile loaded for BBL 1000010010")).toHaveLength(1);

    const headingEl = screen.getByRole("heading", { name: "BBL 1000010010" });
    expect(headingEl).toHaveAttribute("data-outcome-heading");
    await waitFor(() => expect(document.activeElement).toBe(headingEl));
  });

  it("retry: clears the announcement, focuses the loading card (never body), then re-announces and focuses the new outcome heading", async () => {
    let resolveSecond: ((response: Response) => void) | undefined;
    const fetchStub = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ state: "source_unavailable", message: "outage" }, 503),
      )
      .mockImplementationOnce(
        () => new Promise<Response>((resolve) => (resolveSecond = resolve)),
      );
    vi.stubGlobal("fetch", fetchStub);
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-source_unavailable");

    fireEvent.click(screen.getByRole("button", { name: "Retry lookup" }));
    const loading = await screen.findByTestId("loading-stages");
    // Focus moved to the loading card when the Retry button unmounted.
    await waitFor(() => expect(document.activeElement).toBe(loading));
    expect(document.activeElement).not.toBe(document.body);
    // Announcement cleared during loading so the repeat outcome announces.
    expect(screen.getByTestId("outcome-announcer").textContent).toBe("");

    resolveSecond?.(jsonResponse(baseProfile(), 200));
    await screen.findByTestId("profile-view");
    expect(screen.getByTestId("outcome-announcer")).toHaveTextContent(
      "profile loaded for BBL 1000010010",
    );
    const headingEl = screen.getByRole("heading", { name: "BBL 1000010010" });
    await waitFor(() => expect(document.activeElement).toBe(headingEl));
  });

  it("a client-invalid submit after a result does NOT move focus (D5 preserved)", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(baseProfile(), 200)));
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");
    const headingEl = screen.getByRole("heading", { name: "BBL 1000010010" });
    await waitFor(() => expect(document.activeElement).toBe(headingEl));

    submitBbl("123"); // client-invalid: no network call, result unchanged
    await screen.findByTestId("client-validation-error");
    // No focus steal: the arrival effect did not re-fire.
    expect(document.activeElement).toBe(headingEl);
    // The announcement did not change or re-emit a different message.
    expect(screen.getByTestId("outcome-announcer")).toHaveTextContent(
      "profile loaded for BBL 1000010010",
    );
  });
});

describe("PropertyLookup — D4 regression: Property zoning table keeps flag features", () => {
  it("still lists landmark/flood flags in the mapped-features table (filter applies to Confirm only)", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(baseProfile(), 200)));
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");
    const zoning = screen.getByTestId("zoning-section");
    expect(zoning).toHaveTextContent("Mapped features and flags");
    expect(zoning).toHaveTextContent("Landmark");
    expect(zoning).toHaveTextContent("2007 FIRM flood flag");
    expect(zoning).toHaveTextContent("2015 preliminary FIRM flood flag");
    expect(zoning).toHaveTextContent("Historic district");
  });
});
