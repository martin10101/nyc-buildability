import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AddressResolutionScreen } from "@/components/address/AddressResolutionScreen";

/**
 * M5-T016 acceptance pack — Address Confirm card + ZoLa deep-link + handoff
 * (design spec sections 1 / 2-resolved / 3 / 4, Packet 2; ZoLa URL research
 * docs/design/zola-deeplink-url-confirmation.md).
 *
 * THE HREF DISCIPLINE UNDER TEST: the ZoLa link and the Continue handoff
 * are the only two URL contexts in the address flow, and both must be
 * built EXCLUSIVELY from a canonical BBL that passed the CLIENT
 * re-validation (validateBblInput). A result whose BBL fails validation —
 * or carries hostile text — must render NO link at all (honest absence),
 * never a link assembled from reflected data.
 *
 * Harness mirrors address-resolution.test.tsx (small local copy: the two
 * packs stay independently runnable; no shared test-support file is in
 * this packet's scope). Stubbed global fetch over recorded-response-shaped
 * fixtures; no network, no Geoclient, no Supabase.
 */

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const HTTP_CID = "http-cid-0a1b2c3d4e";
const ZOLA_PREFIX = "https://zola.planning.nyc.gov/bbl/";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "X-Correlation-ID": HTTP_CID,
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

function fillAndSubmit(street = "BROADWAY") {
  fireEvent.change(screen.getByLabelText("House number"), {
    target: { value: "120" },
  });
  fireEvent.change(screen.getByLabelText("Street"), { target: { value: street } });
  fireEvent.change(screen.getByLabelText("Borough"), {
    target: { value: "Manhattan" },
  });
  fireEvent.click(screen.getByTestId("address-submit"));
}

/** Full-provenance resolved document, shaped per _success_document +
 * the connector's provenance dict (geoclient_address.py). */
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
      {
        provenance_id: "geoclient-address:conn-cid-1:firstStreetNameNormalized",
        source_id: "nyc-geoclient",
        original_field_name: "firstStreetNameNormalized",
        original_value: "BROADWAY",
        normalized_value: "BROADWAY",
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
      endpoint: "https://api.nyc.gov/geo/geoclient/v2/address",
      request_params: {
        houseNumber: "120",
        street: "BROADWAY",
        borough: "Manhattan",
      } as Record<string, string>,
      retrieved_at: "2026-09-12T00:00:00+00:00",
      http_status: 200,
      geosupport_return_code: "00",
      geosupport_return_code2: "00",
      reason_code: null,
      reason_code2: null,
      response_digest: "sha256:abc123def456",
      digest_canonicalization: "canonical-json-1",
      correlation_id: "conn-cid-1",
    },
  };
}

async function renderResolved(doc = resolvedDoc()) {
  const fetchSpy = stubFetchOnce(jsonResponse(doc, 200));
  const view = render(<AddressResolutionScreen />);
  fillAndSubmit();
  await screen.findByTestId("address-confirm-card");
  return { doc, fetchSpy, container: view.container };
}

const HOSTILE_BBL = '1000477501"><script>window.__pwned=7</script>';
const HOSTILE_TEXT =
  '<img src=x onerror="window.__pwned=8"><a href="javascript:alert(1)">x</a>';

/* ================================================================ *
 * S1 — the Confirm card is the resolved treatment
 * ================================================================ */

describe("S1 — Confirm card routing and shape", () => {
  it("renders the thin confirm card: question heading (focus target), address large, BBL, one dominant action", async () => {
    const { doc } = await renderResolved();
    const card = screen.getByTestId("address-confirm-card");
    // The dominant decision is the question.
    const heading = card.querySelector<HTMLElement>("[data-outcome-heading]");
    expect(heading?.textContent).toBe("Is this the right lot?");
    await waitFor(() => expect(document.activeElement).toBe(heading));
    // Canonical address, fixture-derived.
    const address = screen.getByTestId("confirm-address");
    expect(address.textContent).toContain(doc.canonical.street_name_normalized);
    expect(address.textContent).toContain(doc.canonical.borough_name);
    expect(address.textContent).toContain(doc.canonical.zip_code);
    // BBL fixture-derived; both actions present; placeholder honesty copy.
    expect(screen.getByTestId("resolved-bbl").textContent).toBe(
      doc.canonical.bbl,
    );
    expect(screen.getByTestId("confirm-continue")).toBeInTheDocument();
    expect(screen.getByTestId("not-my-property")).toBeInTheDocument();
    expect(
      screen.getByTestId("lot-outline-placeholder").textContent,
    ).toContain("A parcel outline is not drawn here yet");
    // HTTP reference id via the Meta idiom.
    expect(screen.getByTestId("correlation-id").textContent).toBe(HTTP_CID);
  });

  it("resolved_with_warnings: the warnings block renders ABOVE the Continue button and never gates it", async () => {
    const doc = resolvedDoc();
    doc.status = "resolved_with_warnings";
    doc.grc = "01";
    doc.grc_message = "ADDRESS RANGE CONTAINS A GAP - VERIFY HOUSE NUMBER";
    doc.grc2_message = "SECOND PASS WARNING";
    await renderResolved(doc);

    const warnings = screen.getByTestId("address-warnings");
    expect(warnings).toHaveAttribute("role", "status");
    expect(screen.getByTestId("warning-grc-message").textContent).toBe(
      doc.grc_message,
    );
    const continueLink = screen.getByTestId("confirm-continue");
    // DOM order: the warning precedes the Continue affordance (spec: beside
    // the result, above Continue, never hidden).
    expect(
      warnings.compareDocumentPosition(continueLink) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });
});

/* ================================================================ *
 * S2 — ZoLa deep-link: only from a re-validated canonical BBL
 * ================================================================ */

describe("S2 — ZoLa link discipline", () => {
  it("builds the confirmed /bbl/<canonical> URL from the fixture BBL, opening in a new tab with noopener", async () => {
    const { doc } = await renderResolved();
    const link = screen.getByTestId("zola-link");
    expect(link.getAttribute("href")).toBe(`${ZOLA_PREFIX}${doc.canonical.bbl}`);
    expect(link.getAttribute("target")).toBe("_blank");
    expect(link.getAttribute("rel")).toBe("noopener noreferrer");
    expect(screen.queryByTestId("zola-link-absent")).toBeNull();
  });

  it("a BBL that fails client re-validation yields NO ZoLa link and NO Continue — honest absence, never a guessed link", async () => {
    const doc = resolvedDoc();
    doc.canonical.bbl = "12345"; // wrong length — validateBblInput rejects
    await renderResolved(doc);
    expect(screen.queryByTestId("zola-link")).toBeNull();
    expect(screen.getByTestId("zola-link-absent")).toBeInTheDocument();
    expect(screen.queryByTestId("confirm-continue")).toBeNull();
    expect(screen.getByTestId("confirm-continue-absent")).toBeInTheDocument();
    expect(screen.getByTestId("resolved-bbl-absent")).toBeInTheDocument();
  });

  it("HOSTILE text in canonical.bbl can never reach an href: no links, no injected markup, no script", async () => {
    const doc = resolvedDoc();
    doc.canonical.bbl = HOSTILE_BBL;
    const { container } = await renderResolved(doc);
    // boundedToken strips the markup characters and the remainder fails
    // validateBblInput (wrong length) — so BOTH URL contexts must vanish.
    expect(screen.queryByTestId("zola-link")).toBeNull();
    expect(screen.queryByTestId("confirm-continue")).toBeNull();
    expect(container.querySelectorAll("script, img, iframe, style")).toHaveLength(0);
    for (const anchor of Array.from(container.querySelectorAll("a"))) {
      const href = anchor.getAttribute("href") ?? "";
      expect(href.includes("pwned"), `href ${href}`).toBe(false);
      expect(href.startsWith("javascript"), `href ${href}`).toBe(false);
    }
    expect(
      (window as unknown as Record<string, unknown>).__pwned,
    ).toBeUndefined();
  });
});

/* ================================================================ *
 * S3 — the handoff carries ONLY the canonical BBL
 * ================================================================ */

describe("S3 — Continue handoff", () => {
  it("links to /property/confirm?bbl=<canonical> (fixture-derived) and nothing else from the document", async () => {
    const { doc } = await renderResolved();
    const href = screen.getByTestId("confirm-continue").getAttribute("href");
    expect(href).toBe(`/property/confirm?bbl=${doc.canonical.bbl}`);
    // Nothing else leaks into the query string.
    expect(href).not.toContain("street");
    expect(href).not.toContain("borough");
  });
});

/* ================================================================ *
 * S4 — "Not my property" returns to entry
 * ================================================================ */

describe("S4 — Not my property", () => {
  it("clears back to idle, RETAINS the form values, focuses the street input, silences the announcer, fires no fetch", async () => {
    const { fetchSpy } = await renderResolved();
    const announcer = screen.getByTestId("address-outcome-announcer");
    expect(announcer.textContent).not.toBe("");

    fireEvent.click(screen.getByTestId("not-my-property"));

    expect(screen.queryByTestId("address-confirm-card")).toBeNull();
    const streetInput = screen.getByLabelText("Street") as HTMLInputElement;
    // Values retained for editing — back to ENTRY, not to blank.
    expect(streetInput.value).toBe("BROADWAY");
    expect(
      (screen.getByLabelText("House number") as HTMLInputElement).value,
    ).toBe("120");
    // vitest 4 / newer jsdom applies effect-driven focus after a microtask
    // flush; waitFor tolerates the timing without weakening the assertion
    // (it still FAILS if the street input is never focused).
    await waitFor(() => expect(document.activeElement).toBe(streetInput));
    // No phantom outcome announced; no new request fired.
    expect(announcer.textContent).toBe("");
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });
});

/* ================================================================ *
 * S5 — provenance disclosure + not-verified posture
 * ================================================================ */

describe("S5 — provenance disclosure", () => {
  it("is collapsed by default and discloses source, endpoint HOST, both GRCs, BOTH reference ids, digest, params, and facts", async () => {
    const { doc } = await renderResolved();
    const details = screen.getByTestId(
      "address-provenance",
    ) as HTMLDetailsElement;
    // Collapsed by default: analysts never see connector internals up front.
    expect(details.open).toBe(false);

    const body = details.textContent ?? "";
    expect(body).toContain(doc.provenance.source_id);
    // HOST only — never the full endpoint URL.
    expect(body).toContain("api.nyc.gov");
    expect(body).not.toContain("https://api.nyc.gov");
    // Retrieval timestamp: rendered via boundedToken, which drops the
    // ":"/"+" of the fixture's ISO value — assert the bounded clause so a
    // dropped retrieved-at line fails here.
    const boundedRetrievedAt = doc.provenance.retrieved_at.replace(
      /[^A-Za-z0-9._-]/g,
      "",
    );
    expect(body).toContain(`retrieved ${boundedRetrievedAt}`);
    // The in-disclosure Geosupport return-code line carries BOTH codes
    // (distinct from the warnings block's warning-grc-message element).
    expect(body).toContain(`Geosupport return codes: ${doc.grc} / ${doc.grc2}`);
    expect(body).toContain(doc.provenance.response_digest);
    // The connector's own correlation id, labeled distinctly, is NOT the
    // HTTP reference id.
    expect(
      screen.getByTestId("connector-correlation-id").textContent,
    ).toBe(doc.provenance.correlation_id);
    expect(doc.provenance.correlation_id).not.toBe(HTTP_CID);
    // Request params as escaped key/value text rows.
    const params = screen.getByTestId("request-params").textContent ?? "";
    expect(params).toContain("houseNumber: 120");
    expect(params).toContain("street: BROADWAY");
    // Source facts: original -> normalized, fixture-derived.
    const facts = screen.getByTestId("source-facts").textContent ?? "";
    expect(facts).toContain(doc.source_facts[0].original_field_name);
    expect(facts).toContain(String(doc.source_facts[0].original_value));
  });

  it("carries the not-verified posture and NEVER a 'Verified' badge (confidence 1.0 stays retrieval, not vouching)", async () => {
    const { container } = await renderResolved();
    expect(screen.getByTestId("not-verified-posture").textContent).toContain(
      "has not been through the platform",
    );
    // No coverage/verified vocabulary anywhere on the card.
    expect(container.textContent).not.toMatch(/\bVerified\b/);
  });

  it("shows the withheld-facts reason verbatim when the endpoint withheld source_facts", async () => {
    const doc = resolvedDoc();
    doc.source_facts = [];
    (doc as Record<string, unknown>).source_facts_not_emitted_reason =
      "source facts withheld: bbl failed canonical validation";
    await renderResolved(doc);
    expect(screen.getByTestId("facts-withheld").textContent).toBe(
      "source facts withheld: bbl failed canonical validation",
    );
    expect(screen.queryByTestId("source-facts")).toBeNull();
  });
});

/* ================================================================ *
 * S6 — render safety on the RESOLVED surface (hostile fixture)
 * ================================================================ */

describe("S6 — hostile resolved fixture renders inert", () => {
  it("hostile normalized street/borough, param values, and fact values render as escaped text; no element or href materializes", async () => {
    const doc = resolvedDoc();
    doc.canonical.street_name_normalized = HOSTILE_TEXT;
    doc.canonical.borough_name = `BOROUGH${HOSTILE_TEXT}`;
    doc.provenance.request_params.street = HOSTILE_TEXT;
    doc.source_facts[1].original_value = HOSTILE_TEXT;
    const { container } = await renderResolved(doc);

    // Visible as inert text where rendered…
    expect(screen.getByTestId("confirm-address").textContent).toContain(
      HOSTILE_TEXT,
    );
    expect(screen.getByTestId("request-params").textContent).toContain(
      HOSTILE_TEXT,
    );
    expect(screen.getByTestId("source-facts").textContent).toContain(
      HOSTILE_TEXT,
    );
    // …and never as markup or an attribute.
    expect(container.querySelectorAll("script, img, iframe, style")).toHaveLength(0);
    for (const anchor of Array.from(container.querySelectorAll("a"))) {
      const href = anchor.getAttribute("href") ?? "";
      expect(
        href === "#bbl-input" ||
          href.startsWith(ZOLA_PREFIX) ||
          href.startsWith("/property/confirm?bbl="),
        `unexpected anchor href ${href}`,
      ).toBe(true);
      expect(href.includes("onerror"), `href ${href}`).toBe(false);
    }
    expect(
      (window as unknown as Record<string, unknown>).__pwned,
    ).toBeUndefined();
  });
});
