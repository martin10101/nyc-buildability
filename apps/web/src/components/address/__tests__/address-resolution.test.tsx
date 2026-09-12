import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AddressResolutionScreen } from "@/components/address/AddressResolutionScreen";
import { PropertyLookup } from "@/components/property/PropertyLookup";

/**
 * M5-T015 acceptance pack — address entry + resolution outcomes + error
 * matrix (design spec docs/design/address-entry-confirm-design-spec.md,
 * sections 1-3, 5, 6-Packet-1; endpoint contract
 * services/api/app/api/v1/address_resolution.py).
 *
 * Every test drives the screen through a STUBBED global fetch over
 * recorded-response-SHAPED fixture bodies (the endpoint's own key set).
 * Assertions read expected values FROM the fixture object — never a
 * literal retyped on both sides — except where a spec-mandated posture
 * phrase is itself the requirement. No network, no Geoclient, no Supabase
 * is touched anywhere in this file.
 */

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

/* ---------------------------------------------------------------- *
 * Harness
 * ---------------------------------------------------------------- */

const HTTP_CID = "http-cid-0a1b2c3d4e";

function jsonResponse(
  body: unknown,
  status = 200,
  headers: Record<string, string> = {},
): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "X-Correlation-ID": HTTP_CID,
      ...headers,
    },
  });
}

function stubFetchOnce(...responses: Response[]) {
  const spy = vi.fn();
  for (const response of responses) {
    spy.mockResolvedValueOnce(response);
  }
  vi.stubGlobal("fetch", spy);
  return spy;
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((r) => {
    resolve = r;
  });
  return { promise, resolve };
}

function fillAndSubmit(
  values: { house?: string; street?: string; borough?: string; zip?: string } = {},
) {
  const { house = "120", street = "BROADWAY", borough = "Manhattan", zip } = values;
  fireEvent.change(screen.getByLabelText("House number"), {
    target: { value: house },
  });
  fireEvent.change(screen.getByLabelText("Street"), { target: { value: street } });
  fireEvent.change(screen.getByLabelText("Borough"), {
    target: { value: borough },
  });
  if (zip !== undefined) {
    fireEvent.change(screen.getByLabelText("ZIP code (alternative to borough)"), {
      target: { value: zip },
    });
  }
  fireEvent.click(screen.getByTestId("address-submit"));
}

function requestUrl(spy: ReturnType<typeof vi.fn>, call = 0): URL {
  return new URL(String(spy.mock.calls[call][0]));
}

/* ---------------------------------------------------------------- *
 * Fixtures — shaped exactly like the endpoint's _success_document /
 * error body (key set read from address_resolution.py, M2-T022).
 * ---------------------------------------------------------------- */

function resolvedDoc() {
  return {
    contract_version: "1.0.0",
    document_kind: "address_resolution",
    correlation_id: "doc-cid-11aa22bb",
    status: "resolved",
    grc: "00",
    grc_reason: null as string | null,
    grc_message: null as string | null,
    grc2: "00",
    grc2_reason: null as string | null,
    grc2_message: null as string | null,
    input_echo: {
      house_number: "120",
      street: "BROADWAY",
      borough: "Manhattan",
      zip: null as string | null,
    },
    canonical: {
      bbl: "1000477501" as string | null,
      bin: "1001234" as string | null,
      street_name_normalized: "BROADWAY" as string | null,
      borough_name: "MANHATTAN" as string | null,
      zip_code: "10271" as string | null,
      latitude: 40.708,
      longitude: -74.01,
    },
    suggestions: [] as Array<Record<string, unknown>>,
    selection_policy: "caller_selects",
    unsanitized_reflected_input: {
      fields: ["input_echo.street", "grc_message", "suggestions"],
    },
    source_facts: [
      {
        provenance_id: "geoclient-address:conn-cid-1:bbl",
        source_id: "nyc-geoclient",
        original_field_name: "bbl",
        original_value: "1000477501",
        normalized_value: "1000477501",
        retrieved_at: "2026-09-12T00:00:00+00:00",
        dataset_version: "geoclient-v2",
        effective_date: null,
        bbl: "1000477501",
        confidence: 1.0,
        user_confirmed_or_overridden: "none",
        conflict_status: "none",
      },
    ],
    provenance: {
      source_id: "nyc-geoclient",
      retrieved_at: "2026-09-12T00:00:00+00:00",
      correlation_id: "conn-cid-1",
      response_digest: "sha256:abc123",
    },
  };
}

function warningsDoc() {
  const doc = resolvedDoc();
  doc.status = "resolved_with_warnings";
  doc.grc = "01";
  doc.grc_message = "ADDRESS RANGE CONTAINS A GAP - VERIFY HOUSE NUMBER";
  doc.grc2 = "01";
  doc.grc2_message = "SECOND PASS WARNING FROM GEOSUPPORT";
  return doc;
}

function ambiguousDoc() {
  const doc = resolvedDoc();
  doc.status = "ambiguous";
  doc.canonical = {
    ...doc.canonical,
    bbl: null,
    bin: null,
    street_name_normalized: null,
  };
  doc.suggestions = [
    { street_name: "BROADWAY", street_code: "12345" },
    // Codeless slot (the connector emits name-only when the source's code
    // slot is empty) — the "gap" is a skipped empty slot upstream.
    { street_name: "BROADWAY ALLEY" },
    { street_name: "BROADWAY TERRACE", street_code: "12399" },
  ];
  return doc;
}

function notFoundDoc() {
  const doc = resolvedDoc();
  doc.status = "not_found";
  doc.grc = "EE";
  doc.grc_message = "STREET NOT IDENTICAL TO ANY STREET IN BOROUGH";
  doc.grc2 = "42";
  doc.grc2_message = "SECOND GEOSUPPORT MESSAGE FOR THIS ANSWER";
  doc.canonical = {
    ...doc.canonical,
    bbl: null,
    bin: null,
  };
  doc.source_facts = [];
  return doc;
}

function rejectedDoc() {
  const doc = notFoundDoc();
  doc.status = "rejected";
  doc.grc = "71";
  doc.grc_message = "ADDRESS REJECTED AS UNRESOLVABLE";
  return doc;
}

function errorDoc(state: string, extra: Record<string, unknown> = {}) {
  return {
    contract_version: "1.0.0",
    document_kind: "address_resolution_error",
    state,
    correlation_id: "doc-cid-err",
    error: {
      error_type: state,
      message: `connector detail for ${state} (typed, value-free)`,
      connector_correlation_id: "conn-cid-err",
      source_id: "nyc-geoclient",
      endpoint: "geoclient/v2/address",
      ...extra,
    },
  };
}

/* ================================================================ *
 * S1 — flag posture
 * ================================================================ */

describe("S1 — flag posture (off: today's UI, no address surface, no fetch)", () => {
  it("flag off renders the disabled placeholder, never mounts the address surface, and fires no fetch", () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(<PropertyLookup />);
    expect(screen.getByTestId("address-disabled-copy")).toBeInTheDocument();
    expect(screen.queryByTestId("address-resolution-screen")).toBeNull();
    expect(screen.queryByTestId("address-form")).toBeNull();
    // Flag off: the BBL card keeps the page's original h1.
    expect(
      screen.getByRole("heading", { level: 1, name: "Property lookup" }),
    ).toBeInTheDocument();
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("flag on mounts the address form above the BBL form and removes the placeholder — still no fetch until submit", () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(<PropertyLookup ruleEvalEnabled />);
    expect(screen.getByTestId("address-resolution-screen")).toBeInTheDocument();
    expect(screen.getByTestId("address-form")).toBeInTheDocument();
    expect(screen.queryByTestId("address-disabled-copy")).toBeNull();
    // The BBL form is still fully present alongside it.
    expect(screen.getByLabelText("BBL")).toBeInTheDocument();
    // G3 F1: the mounted address surface owns the page's single h1 and the
    // BBL card demotes to h2 — the document outline never opens on an h2.
    expect(
      screen.getByRole("heading", { level: 1, name: "Address lookup" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 2, name: "Property lookup" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { level: 1, name: "Property lookup" }),
    ).toBeNull();
    // Mounting alone fires nothing.
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});

/* ================================================================ *
 * S2 — resolved routes to the stub handoff
 * ================================================================ */

describe("S2 — resolved / resolved_with_warnings", () => {
  it("renders the canonical address + BBL from the fixture with an explicit Packet-2 stub", async () => {
    const doc = resolvedDoc();
    stubFetchOnce(jsonResponse(doc, 200));
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    const card = await screen.findByTestId("address-resolved");
    // Fixture-derived, never retyped: the BBL shown IS the body's BBL.
    expect(screen.getByTestId("resolved-bbl").textContent).toBe(
      doc.canonical.bbl,
    );
    expect(screen.getByTestId("resolved-address").textContent).toContain(
      doc.canonical.street_name_normalized,
    );
    expect(screen.getByTestId("resolved-address").textContent).toContain(
      doc.canonical.borough_name,
    );
    // The stub handoff is explicit about being the Packet-2 boundary: the
    // Continue affordance exists, is inert, and says why.
    const stub = screen.getByTestId("stub-continue");
    expect(stub).toBeDisabled();
    expect(screen.getByTestId("address-resolved-stub")).toBeInTheDocument();
    // No warnings block on a clean resolve.
    expect(screen.queryByTestId("address-warnings")).toBeNull();
    expect(card.textContent).toContain("resolved to a single lot");
  });

  it("resolved_with_warnings renders the warning text beside the result (role=status), never hidden and never gating", async () => {
    const doc = warningsDoc();
    stubFetchOnce(jsonResponse(doc, 200));
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    await screen.findByTestId("address-resolved");
    const warnings = screen.getByTestId("address-warnings");
    expect(warnings).toHaveAttribute("role", "status");
    // Both source messages verbatim (escaped), fixture-derived.
    expect(screen.getByTestId("warning-grc-message").textContent).toBe(
      doc.grc_message,
    );
    expect(screen.getByTestId("warning-grc2-message").textContent).toBe(
      doc.grc2_message,
    );
    // Warnings never gate: the result and its stub affordance still render.
    expect(screen.getByTestId("resolved-bbl").textContent).toBe(
      doc.canonical.bbl,
    );
    expect(screen.getByTestId("stub-continue")).toBeInTheDocument();
  });
});

/* ================================================================ *
 * S3 — ambiguous: caller_selects rendered literally
 * ================================================================ */

describe("S3 — ambiguous suggestions (caller_selects, literally)", () => {
  it("renders suggestions verbatim in slot order with NO default selection and a disabled Use button", async () => {
    const doc = ambiguousDoc();
    stubFetchOnce(jsonResponse(doc, 200));
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    await screen.findByTestId("address-ambiguous");
    const radios = screen.getAllByRole("radio");
    expect(radios).toHaveLength(doc.suggestions.length);
    // Source slot order, fixture-derived; the codeless slot renders
    // name-only (street_code is display-optional provenance).
    const items = screen
      .getByTestId("suggestion-chooser")
      .querySelectorAll("li");
    doc.suggestions.forEach((suggestion, index) => {
      expect(items[index].textContent).toContain(
        String(suggestion.street_name),
      );
    });
    expect(items[0].textContent).toContain(String(doc.suggestions[0].street_code));
    expect(items[1].textContent).not.toContain("street code");
    // The platform picks NOTHING: no radio checked, no pre-highlight, and
    // the confirm affordance is inert until an active user choice.
    for (const radio of radios) {
      expect((radio as HTMLInputElement).checked).toBe(false);
      // One labeled radio-group => native keyboard (arrow-key) selection.
      expect(radio).toHaveAttribute("name", "address-suggestion");
    }
    expect(screen.getByTestId("use-suggestion")).toBeDisabled();
  });

  it("re-resolves with the chosen suggestion's street_name VERBATIM (same house number and borough), asserted at the fetch seam", async () => {
    const doc = ambiguousDoc();
    const followUp = resolvedDoc();
    const fetchSpy = stubFetchOnce(
      jsonResponse(doc, 200),
      jsonResponse(followUp, 200),
    );
    render(<AddressResolutionScreen />);
    fillAndSubmit({ house: "120", street: "BRAODWAY", borough: "Manhattan" });

    await screen.findByTestId("address-ambiguous");
    // Active selection (radio activation == what Space does), then confirm.
    fireEvent.click(screen.getByTestId("suggestion-option-1"));
    expect(screen.getByTestId("use-suggestion")).not.toBeDisabled();
    fireEvent.click(screen.getByTestId("use-suggestion"));

    await screen.findByTestId("address-resolved");
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    const first = requestUrl(fetchSpy, 0);
    const second = requestUrl(fetchSpy, 1);
    // The re-query carries the suggestion's street_name verbatim as the
    // new street, with the ORIGINAL house number and borough.
    expect(second.searchParams.get("street")).toBe(
      String(doc.suggestions[1].street_name),
    );
    expect(second.searchParams.get("house_number")).toBe(
      first.searchParams.get("house_number"),
    );
    expect(second.searchParams.get("borough")).toBe(
      first.searchParams.get("borough"),
    );
  });
});

/* ================================================================ *
 * S4 — visible honest non-success (not_found / rejected / unrecognized)
 * ================================================================ */

describe("S4 — not_found, rejected, unrecognized_status", () => {
  it("not_found shows BOTH GRC codes and messages, the echoed input, and both recovery affordances", async () => {
    const doc = notFoundDoc();
    stubFetchOnce(jsonResponse(doc, 200));
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    await screen.findByTestId("address-not-found");
    expect(screen.getByTestId("grc-line").textContent).toContain(doc.grc);
    expect(screen.getByTestId("grc-line").textContent).toContain(
      doc.grc_message,
    );
    expect(screen.getByTestId("grc2-line").textContent).toContain(doc.grc2);
    expect(screen.getByTestId("grc2-line").textContent).toContain(
      doc.grc2_message,
    );
    expect(screen.getByTestId("input-echo").textContent).toContain(
      doc.input_echo.street,
    );
    // Never a dead end: edit refocuses the street input; the BBL
    // alternative is a constant-fragment link to the BBL form.
    expect(screen.getByTestId("bbl-instead")).toHaveAttribute(
      "href",
      "#bbl-input",
    );
    fireEvent.click(screen.getByTestId("edit-address"));
    expect(document.activeElement).toBe(screen.getByLabelText("Street"));
    expect(screen.getByTestId("correlation-id").textContent).toBe(HTTP_CID);
  });

  it("rejected renders the same honest structure under its own framing", async () => {
    const doc = rejectedDoc();
    stubFetchOnce(jsonResponse(doc, 200));
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    const card = await screen.findByTestId("address-rejected");
    expect(card.textContent).toContain("rejected");
    expect(screen.getByTestId("grc-line").textContent).toContain(
      doc.grc_message,
    );
    expect(screen.getByTestId("grc2-line").textContent).toContain(
      doc.grc2_message,
    );
    expect(screen.getByTestId("edit-address")).toBeInTheDocument();
    expect(screen.getByTestId("bbl-instead")).toBeInTheDocument();
  });

  it("an unrecognized status renders the honest not-recognized card — never coerced into not_found", async () => {
    const doc = resolvedDoc();
    doc.status = "resolved_but_shinier"; // a future/unknown form
    stubFetchOnce(jsonResponse(doc, 200));
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    await screen.findByTestId("address-unrecognized-status");
    expect(screen.queryByTestId("address-not-found")).toBeNull();
    expect(screen.queryByTestId("address-resolved")).toBeNull();
    // The raw status surfaces as a bounded plain token.
    expect(screen.getByTestId("unrecognized-status").textContent).toBe(
      "resolved_but_shinier",
    );
    expect(screen.getByTestId("correlation-id").textContent).toBe(HTTP_CID);
    expect(
      screen.getByRole("button", { name: "Retry address lookup" }),
    ).toBeInTheDocument();
  });
});

/* ================================================================ *
 * S5 — the complete documented error matrix, one scenario per pair
 * ================================================================ */

/** Every documented (HTTP, state) pair the endpoint can emit, with the
 * spec-table retry posture. request_budget_exceeded is exercised
 * separately below (documented-unreachable). */
const ERROR_MATRIX: Array<[string, number, boolean]> = [
  ["invalid_input", 422, false],
  ["key_missing", 503, false],
  ["auth_failed", 502, true],
  ["rate_limited", 503, true],
  ["source_unavailable", 503, true],
  ["timeout", 504, true],
  ["malformed_response", 502, true],
  ["internal_error", 500, true],
];

describe("S5 — documented error matrix", () => {
  it.each(ERROR_MATRIX)(
    "%s (HTTP %i) renders its typed card, correlation id, and retry=%s",
    async (state, httpStatus, retryable) => {
      const body = errorDoc(state);
      stubFetchOnce(jsonResponse(body, httpStatus));
      render(<AddressResolutionScreen />);
      fillAndSubmit();

      const card = await screen.findByTestId(`address-error-${state}`);
      // Correlation id via the Meta idiom on EVERY error card.
      expect(screen.getByTestId("correlation-id").textContent).toBe(HTTP_CID);
      // The typed pair is stated on the card.
      expect(card.textContent).toContain(`HTTP ${httpStatus}`);
      // Retry ONLY where the spec table says retrying can help.
      const retryButton = screen.queryByRole("button", {
        name: "Retry address lookup",
      });
      if (retryable) {
        expect(retryButton).not.toBeNull();
      } else {
        expect(retryButton).toBeNull();
      }
    },
  );

  it("invalid_input renders the CONNECTOR's message as the specific reason (the single validation authority)", async () => {
    const body = errorDoc("invalid_input");
    stubFetchOnce(jsonResponse(body, 422));
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    await screen.findByTestId("address-error-invalid_input");
    expect(screen.getByTestId("invalid-input-message").textContent).toBe(
      body.error.message,
    );
    // G3 F3: the one user-fixable error points back at the form.
    fireEvent.click(screen.getByTestId("edit-address"));
    expect(document.activeElement).toBe(screen.getByLabelText("Street"));
  });

  it("server-side key problems NEVER blame the user", async () => {
    stubFetchOnce(jsonResponse(errorDoc("key_missing"), 503));
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    const card = await screen.findByTestId("address-error-key_missing");
    expect(card.textContent).toContain("Nothing is wrong with your input");

    cleanup();
    vi.unstubAllGlobals();

    stubFetchOnce(jsonResponse(errorDoc("auth_failed"), 502));
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    const authCard = await screen.findByTestId("address-error-auth_failed");
    expect(authCard.textContent).toContain("not your input");
  });

  it("rate_limited surfaces a present bounded retry_after and omits the line when absent", async () => {
    // Single-source hint value: injected into the fixture AND asserted, so
    // the two sides cannot drift (TS: the errorDoc spread does not surface
    // extra keys on the inferred error type, so the value lives here).
    const retryAfterHint = "120";
    stubFetchOnce(
      jsonResponse(errorDoc("rate_limited", { retry_after: retryAfterHint }), 503),
    );
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    await screen.findByTestId("address-error-rate_limited");
    expect(screen.getByTestId("retry-after").textContent).toContain(
      retryAfterHint,
    );

    cleanup();
    vi.unstubAllGlobals();

    stubFetchOnce(jsonResponse(errorDoc("rate_limited"), 503));
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    await screen.findByTestId("address-error-rate_limited");
    expect(screen.queryByTestId("retry-after")).toBeNull();
  });

  it("request_budget_exceeded — documented as unreachable from this endpoint — still renders its own honest typed card if it ever arrives", async () => {
    // The endpoint passes no budget, so this pair is documented
    // unreachable-by-construction; the client types it anyway so an
    // arrival is honest, never an undocumented surprise.
    stubFetchOnce(jsonResponse(errorDoc("request_budget_exceeded"), 503));
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    const card = await screen.findByTestId(
      "address-error-request_budget_exceeded",
    );
    expect(card.textContent).toContain("Nothing is wrong with your input");
  });

  it("an undocumented (status,state) pair renders the distinct unexpected-response card — never a guessed match", async () => {
    stubFetchOnce(jsonResponse(errorDoc("weird_new_state"), 418));
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    await screen.findByTestId("address-unexpected-response");
    expect(screen.getByTestId("unexpected-state").textContent).toBe(
      "weird_new_state",
    );
  });

  it("a 200 body without the address_resolution document_kind is never trusted", async () => {
    stubFetchOnce(jsonResponse({ document_kind: "something_else" }, 200));
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    await screen.findByTestId("address-unexpected-response");
    expect(screen.queryByTestId("address-resolved")).toBeNull();
  });
});

/* ================================================================ *
 * S6 — render safety under hostile reflected fixtures
 * ================================================================ */

const HOSTILE_STREET =
  '<script>window.__pwned=1</script><img src=x onerror="window.__pwned=2">';
const HOSTILE_MESSAGE =
  '"/><a href="javascript:alert(1)">click</a><style>*{display:none}</style>';
const HOSTILE_SUGGESTION =
  'BROADWAY"><iframe src="https://evil.example"></iframe>';

describe("S6 — hostile reflected text renders inert", () => {
  it("script/markup in input_echo.street and grc_message renders as escaped text; nothing executes, nothing reaches an attribute", async () => {
    const doc = notFoundDoc();
    doc.input_echo.street = HOSTILE_STREET;
    doc.grc_message = HOSTILE_MESSAGE;
    stubFetchOnce(jsonResponse(doc, 200));
    const { container } = render(<AddressResolutionScreen />);
    fillAndSubmit({ street: HOSTILE_STREET });

    await screen.findByTestId("address-not-found");
    // The payloads are visible as INERT text (textContent carries them).
    expect(screen.getByTestId("input-echo").textContent).toContain(
      HOSTILE_STREET,
    );
    expect(screen.getByTestId("grc-line").textContent).toContain(
      HOSTILE_MESSAGE,
    );
    // No injected element materialized anywhere in the tree.
    expect(container.querySelectorAll("script, img, iframe, style")).toHaveLength(0);
    // No reflected value reached any href/src/attribute context: the only
    // anchor on the screen is the constant-fragment BBL affordance.
    const anchors = Array.from(container.querySelectorAll("a"));
    expect(anchors.map((a) => a.getAttribute("href"))).toEqual(["#bbl-input"]);
    expect(
      (window as unknown as Record<string, unknown>).__pwned,
    ).toBeUndefined();
  });

  it("a hostile suggestion name renders as BOUNDED text, and picking it sends the RAW name verbatim to the fetch seam", async () => {
    // raw ≠ bounded BY CONSTRUCTION (G1 D2): the 700-char tail forces
    // boundedText to truncate the DISPLAY, so this test discriminates the
    // verbatim re-query from a bounded one — a mutant that re-queries with
    // the bounded display string fails the seam equality below.
    const longHostileName = HOSTILE_SUGGESTION + "Y".repeat(700);
    const doc = ambiguousDoc();
    doc.suggestions[1] = { street_name: longHostileName };
    const fetchSpy = stubFetchOnce(
      jsonResponse(doc, 200),
      jsonResponse(notFoundDoc(), 200),
    );
    const { container } = render(<AddressResolutionScreen />);
    fillAndSubmit();

    await screen.findByTestId("address-ambiguous");
    expect(container.querySelectorAll("iframe")).toHaveLength(0);
    const chooserText = screen.getByTestId("suggestion-chooser").textContent ?? "";
    // The hostile prefix is visible (inert, under the display cap)…
    expect(chooserText).toContain(HOSTILE_SUGGESTION);
    // …but the DISPLAY is bounded: the full raw string never renders.
    expect(chooserText).not.toContain(longHostileName);

    fireEvent.click(screen.getByTestId("suggestion-option-1"));
    fireEvent.click(screen.getByTestId("use-suggestion"));
    await screen.findByTestId("address-not-found");
    // Verbatim re-query (URL-encoded transport, decoded here for equality):
    // the FULL raw name, not the truncated display form.
    expect(requestUrl(fetchSpy, 1).searchParams.get("street")).toBe(
      longHostileName,
    );
  });

  it("source scan: no dangerouslySetInnerHTML in any new file; suggestion keys are array indexes; imports stay within the existing module set", () => {
    // Paths resolve from the vitest root (apps/web — the CI job's
    // working-directory), NOT from import.meta.url: under the jsdom
    // environment vitest serves modules from a non-file scheme, so a
    // URL-relative read throws ERR_INVALID_URL_SCHEME.
    const sources: Record<string, string> = {
      "AddressResolutionScreen.tsx": readFileSync(
        resolve(process.cwd(), "src/components/address/AddressResolutionScreen.tsx"),
        "utf8",
      ),
      "AddressForm.tsx": readFileSync(
        resolve(process.cwd(), "src/components/address/AddressForm.tsx"),
        "utf8",
      ),
      "SuggestionChooser.tsx": readFileSync(
        resolve(process.cwd(), "src/components/address/SuggestionChooser.tsx"),
        "utf8",
      ),
      "address-api.ts": readFileSync(
        resolve(process.cwd(), "src/lib/address-api.ts"),
        "utf8",
      ),
      "announce.ts": readFileSync(
        resolve(process.cwd(), "src/lib/announce.ts"),
        "utf8",
      ),
      "PropertyLookup.tsx": readFileSync(
        resolve(process.cwd(), "src/components/property/PropertyLookup.tsx"),
        "utf8",
      ),
    };
    for (const [name, source] of Object.entries(sources)) {
      expect(source, name).not.toContain("dangerouslySetInnerHTML");
    }
    // React keys for suggestions are the array index, never the string.
    expect(sources["SuggestionChooser.tsx"]).toContain("<li key={index}>");
    // S8 (module half): the new modules import ONLY app-internal paths,
    // relative siblings, or react — no new package can sneak in via an
    // import (package.json itself is forbidden to this task).
    for (const name of [
      "AddressResolutionScreen.tsx",
      "AddressForm.tsx",
      "SuggestionChooser.tsx",
      "address-api.ts",
    ]) {
      const specifiers = Array.from(
        sources[name].matchAll(/from\s+"([^"]+)"/g),
        (match) => match[1],
      );
      for (const specifier of specifiers) {
        expect(
          specifier === "react" ||
            specifier.startsWith("@/") ||
            specifier.startsWith("./"),
          `${name} imports ${specifier}`,
        ).toBe(true);
      }
    }
  });
});

/* ================================================================ *
 * S7 — state-machine integrity (supersession, D5, focus, announce)
 * ================================================================ */

describe("S7 — state-machine integrity", () => {
  it("a superseded request renders nothing: the second submit owns the screen even when the first resolves late", async () => {
    const slow = deferred<Response>();
    const fast = resolvedDoc();
    const slowDoc = notFoundDoc();
    const fetchSpy = vi
      .fn()
      // First request hangs (and ignores its abort signal — the seq guard
      // must win even when the transport does not honor cancellation).
      .mockReturnValueOnce(slow.promise)
      .mockResolvedValueOnce(jsonResponse(fast, 200));
    vi.stubGlobal("fetch", fetchSpy);
    render(<AddressResolutionScreen />);

    fillAndSubmit({ street: "FIRST STREET" });
    fillAndSubmit({ street: "SECOND STREET" });

    await screen.findByTestId("address-resolved");
    // The late first response must change nothing.
    slow.resolve(jsonResponse(slowDoc, 200));
    await waitFor(() =>
      expect(screen.queryByTestId("address-not-found")).toBeNull(),
    );
    expect(screen.getByTestId("resolved-bbl").textContent).toBe(
      fast.canonical.bbl,
    );
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });

  it("D5: the last good result survives an inert (both-blank) resubmit, and no request fires", async () => {
    const doc = resolvedDoc();
    const fetchSpy = stubFetchOnce(jsonResponse(doc, 200));
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    await screen.findByTestId("address-resolved");

    // Blank both driving fields: the submit affordance goes inert…
    fireEvent.change(screen.getByLabelText("House number"), {
      target: { value: "" },
    });
    fireEvent.change(screen.getByLabelText("Street"), { target: { value: "" } });
    expect(screen.getByTestId("address-submit")).toBeDisabled();
    // …and even a programmatic submit is a no-op (guard, not validation).
    fireEvent.submit(screen.getByTestId("address-form"));
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId("address-resolved")).toBeInTheDocument();
  });

  it("focus moves to the outcome heading on arrival, and to the resolving card on retry", async () => {
    const first = errorDoc("timeout");
    const slow = deferred<Response>();
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(first, 504))
      .mockReturnValueOnce(slow.promise);
    vi.stubGlobal("fetch", fetchSpy);
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    const card = await screen.findByTestId("address-error-timeout");
    const heading = card.querySelector<HTMLElement>("[data-outcome-heading]");
    expect(heading).not.toBeNull();
    await waitFor(() => expect(document.activeElement).toBe(heading));

    // Retry: the failure card (and its button) unmounts; focus must land
    // on the loading card, never on <body>.
    fireEvent.click(screen.getByRole("button", { name: "Retry address lookup" }));
    const resolving = await screen.findByTestId("address-resolving");
    await waitFor(() =>
      expect(document.activeElement).toBe(resolving.querySelector("h2")),
    );
    slow.resolve(jsonResponse(errorDoc("timeout"), 504));
    await screen.findByTestId("address-error-timeout");
  });

  it("a suggestion pick moves focus to the resolving card while the re-query is in flight (never body)", async () => {
    // G3 F2: the "Use this address" button unmounts with the ambiguous
    // card, so the loading card must take focus — same rule as retry.
    const slow = deferred<Response>();
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(ambiguousDoc(), 200))
      .mockReturnValueOnce(slow.promise);
    vi.stubGlobal("fetch", fetchSpy);
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    await screen.findByTestId("address-ambiguous");
    fireEvent.click(screen.getByTestId("suggestion-option-0"));
    fireEvent.click(screen.getByTestId("use-suggestion"));
    const resolving = await screen.findByTestId("address-resolving");
    await waitFor(() =>
      expect(document.activeElement).toBe(resolving.querySelector("h2")),
    );
    slow.resolve(jsonResponse(resolvedDoc(), 200));
    await screen.findByTestId("address-resolved");
  });

  it("the announcer speaks each arrival exactly once: cleared while resolving, set on arrival, re-set for an identical retry outcome", async () => {
    const slow = deferred<Response>();
    const fetchSpy = vi
      .fn()
      .mockReturnValueOnce(slow.promise)
      .mockResolvedValueOnce(jsonResponse(errorDoc("timeout"), 504));
    vi.stubGlobal("fetch", fetchSpy);
    render(<AddressResolutionScreen />);

    const announcer = screen.getByTestId("address-outcome-announcer");
    expect(announcer.textContent).toBe("");
    fillAndSubmit();
    // In flight: still silent (cleared so a repeat genuinely re-announces).
    expect(announcer.textContent).toBe("");
    slow.resolve(jsonResponse(errorDoc("timeout"), 504));
    await screen.findByTestId("address-error-timeout");
    const firstMessage = announcer.textContent;
    expect(firstMessage).toContain("timed out");

    fireEvent.click(screen.getByRole("button", { name: "Retry address lookup" }));
    // While the retry is in flight the region clears…
    await waitFor(() => expect(announcer.textContent).toBe(""));
    // …then the identical outcome announces again (content change).
    await screen.findByTestId("address-error-timeout");
    await waitFor(() => expect(announcer.textContent).toBe(firstMessage));
  });

  it("transport failures render their own recoverable cards (network error / unreadable body)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("fetch failed");
      }),
    );
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    await screen.findByTestId("address-network-error");
    expect(
      screen.getByRole("button", { name: "Retry address lookup" }),
    ).toBeInTheDocument();

    cleanup();
    vi.unstubAllGlobals();

    // A 200 with an unparseable body: unexpected response, nothing trusted.
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response("not json at all", {
            status: 200,
            headers: { "X-Correlation-ID": HTTP_CID },
          }),
      ),
    );
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    await screen.findByTestId("address-unexpected-response");
    expect(screen.getByTestId("correlation-id").textContent).toBe(HTTP_CID);
  });
});
