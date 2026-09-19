import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AddressResolutionScreen } from "@/components/address/AddressResolutionScreen";
import { zolaLotUrl } from "@/lib/provenance-link";
import {
  ABSENT_BBL_MAP_LINK_NOTE,
  ZOLA_LOT_LINK_LABEL,
} from "@/components/architect/AddressAutocomplete";

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

/** M5-T023: the confirm card now mounts LotOutlineMap, which fetches the lot
 * outline. This pack is about the ADDRESS confirm surface, so lot-geometry calls
 * resolve to the benign flag-off 404 (route_absent) and are served WITHOUT
 * reaching — or counting against — the address-resolution spy the tests assert
 * on. Full lot-outline coverage lives in lot-outline-map.test.tsx. */
function lotGeometryStub(url: string): Response | null {
  if (url.includes("/lot-geometry")) {
    return new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 });
  }
  return null;
}

function stubFetchOnce(...responses: Response[]) {
  const spy = vi.fn();
  for (const response of responses) {
    spy.mockResolvedValueOnce(response);
  }
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const lot = lotGeometryStub(String(input));
      return lot ? Promise.resolve(lot) : spy(input, init);
    }),
  );
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
    // M5-T023: the Packet-2 placeholder is superseded by the lot-outline
    // surface (an accessibly-labeled region). Here the lot-geometry call is
    // stubbed to the flag-off 404, so the surface shows its honest "unavailable"
    // state; full outcome coverage is in lot-outline-map.test.tsx.
    expect(screen.getByTestId("lot-outline")).toBeInTheDocument();
    expect(screen.queryByTestId("lot-outline-placeholder")).toBeNull();
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

  it("DB-005: the rendered ZoLa href is exactly the shared zolaLotUrl helper output (no local template remains)", async () => {
    const { doc } = await renderResolved();
    const link = screen.getByTestId("zola-link");
    // The migration replaced this card's local ZOLA_BBL_URL_PREFIX +
    // encodeURIComponent template with the shared validated helper; the
    // rendered href is byte-identical to the helper's output for the
    // re-validated canonical BBL — the unification, proven at the surface.
    expect(link.getAttribute("href")).toBe(zolaLotUrl(doc.canonical.bbl));
    expect(zolaLotUrl(doc.canonical.bbl)).toBe(
      `${ZOLA_PREFIX}${doc.canonical.bbl}`,
    );
  });

  it("DB-005: a non-canonical BBL drives the helper's null contract — no ZoLa link renders", async () => {
    const doc = resolvedDoc();
    doc.canonical.bbl = "12345"; // fails validateBblInput AND zolaLotUrl
    await renderResolved(doc);
    expect(zolaLotUrl("12345")).toBeNull();
    expect(screen.queryByTestId("zola-link")).toBeNull();
    expect(screen.getByTestId("zola-link-absent")).toBeInTheDocument();
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

/* ================================================================ *
 * S7 — DB-024(b)/(d): the confirm surface shares the ZoLa label and
 * the absent-BBL note with ZoningContextPanel / PropertyOverview
 * ================================================================ */

describe("S7 — DB-024 shared ZoLa label and absent-BBL note on the confirm card", () => {
  it("names its ZoLa action with the shared ZOLA_LOT_LINK_LABEL — one accessible name across all three ZoLa link sites", async () => {
    await renderResolved();
    const link = screen.getByTestId("zola-link");
    // The SAME accessible name assistive tech reads on the ZoningContextPanel
    // and PropertyOverview ZoLa links (DB-024(d)) — one shared label, resolved
    // by role+name, with no per-site drift ("Open ZoLa" vs "Open in ZoLa").
    expect(screen.getByRole("link", { name: ZOLA_LOT_LINK_LABEL })).toBe(link);
    expect(link.textContent).toBe(ZOLA_LOT_LINK_LABEL);
  });

  it("renders the shared ABSENT_BBL_MAP_LINK_NOTE byte-identically when the BBL is not canonical", async () => {
    const doc = resolvedDoc();
    doc.canonical.bbl = "12345"; // fails validateBblInput -> honest absence, no link
    await renderResolved(doc);
    expect(screen.queryByTestId("zola-link")).toBeNull();
    // Exact shared constant (DB-024(b)): the confirm card's absent note is
    // byte-identical to the ZoningContextPanel and PropertyOverview notes —
    // one single source of truth, asserted through the import.
    expect(screen.getByTestId("zola-link-absent").textContent).toBe(
      ABSENT_BBL_MAP_LINK_NOTE,
    );
  });
});

/* ================================================================ *
 * S8 — DB-026: the entered input is shown VERBATIM, distinct from the
 * city-matched address (identity honesty, D-073-R006 records class)
 * ================================================================ */

describe("S8 — DB-026 entered-vs-matched identity honesty", () => {
  it("AS-1/AS-6: shows the verbatim entered input alongside the distinct city-matched address for the corner-lot case", async () => {
    // DB-026 case-1: the analyst types the 37-Street frontage; the city matches
    // it to bbl 3052960043 (whose PLUTO address-of-record is on 13 Avenue). The
    // typed input must survive VERBATIM (lower-case "37 street"), never silently
    // replaced by the normalized match.
    const doc = resolvedDoc();
    doc.input_echo.house_number = "1279";
    doc.input_echo.street = "37 street";
    doc.input_echo.borough = "Brooklyn";
    doc.canonical.bbl = "3052960043";
    doc.canonical.street_name_normalized = "37 STREET";
    doc.canonical.borough_name = "BROOKLYN";
    doc.canonical.zip_code = "11218";
    await renderResolved(doc);

    // The entered input is preserved verbatim and kept distinct from the match.
    const entered = screen.getByTestId("entered-input");
    expect(entered.textContent).toContain("1279 37 street");
    expect(entered.textContent).toContain("Brooklyn");
    // The city-matched address is the normalized canonical form (a separate line).
    const matched = screen.getByTestId("confirm-address");
    expect(matched.textContent).toContain("37 STREET");
    // The lot identity carried forward is the BBL — never the address string.
    expect(screen.getByTestId("resolved-bbl").textContent).toBe("3052960043");
  });

  it("keeps the entered-input record present on the plain resolved happy path too", async () => {
    await renderResolved();
    expect(screen.getByTestId("entered-input").textContent).toContain(
      "120 BROADWAY",
    );
  });
});

/* ================================================================ *
 * S9 — DB-026 journey: the architect autocomplete arc keeps the RAW
 * typed text distinct from BOTH the picked (city-shaped) suggestion
 * label AND the city-matched address. On this arc the server input_echo
 * carries the PICKED suggestion (Geoclient re-resolves the picked
 * components), so the raw typed text must be threaded to the card
 * explicitly or it silently collapses into the match.
 * ================================================================ */

describe("S9 — DB-026 autocomplete journey: typed text ≠ picked label ≠ matched address", () => {
  /** A GeoSearch /autocomplete FeatureCollection whose single suggestion is
   * already city-shaped ("37 STREET"), so its label differs from the raw
   * one-box text the analyst types ("1279 37 st bk"). */
  function geosearchSuggestions() {
    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: { type: "Point", coordinates: [-73.98522, 40.641968] },
          properties: {
            source: "nycpad",
            housenumber: "1279",
            street: "37 STREET",
            borough: "Brooklyn",
            postalcode: "11218",
            label: "1279 37 STREET, Brooklyn, NY, USA",
            addendum: { pad: { bbl: "3052960043", version: "26c" } },
          },
        },
      ],
    };
  }

  /** The Geoclient resolved document the PICK re-resolves to: input_echo carries
   * the PICKED (city-shaped) components, canonical is the city match. Neither
   * equals the raw typed "1279 37 st bk". */
  function resolvedForPick() {
    const doc = resolvedDoc();
    doc.input_echo.house_number = "1279";
    doc.input_echo.street = "37 STREET";
    doc.input_echo.borough = "Brooklyn";
    doc.canonical.bbl = "3052960043";
    doc.canonical.street_name_normalized = "37 STREET";
    doc.canonical.borough_name = "BROOKLYN";
    doc.canonical.zip_code = "11218";
    return doc;
  }

  /** Route by URL: the debounced type-ahead hits GeoSearch; the pick re-resolves
   * through the Geoclient address endpoint; the confirm card's lot-outline call
   * gets the benign flag-off 404. */
  function stubArchitectFetch(doc: Record<string, unknown>) {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/lot-geometry")) {
          return Promise.resolve(
            new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 }),
          );
        }
        if (url.includes("geosearch")) {
          return Promise.resolve(jsonResponse(geosearchSuggestions(), 200));
        }
        return Promise.resolve(jsonResponse(doc, 200));
      }),
    );
  }

  it("AS-1/AS-6: types a raw one-box address, picks the city-shaped suggestion, and the confirm card still shows the VERBATIM typed text — distinct from the picked label and the matched address", async () => {
    // Surrounding whitespace on the raw entry: the card must render the typed
    // string UNCHANGED (trimming decides only whether it is blank), so the exact
    // <strong> textContent below carries the leading/trailing spaces verbatim.
    const typed = "  1279 37 st bk  ";
    stubArchitectFetch(resolvedForPick());
    render(<AddressResolutionScreen architect />);

    // Type the raw one-box address into the autocomplete (labelled distinctly
    // from the manual "Street" field, so this never targets the manual form).
    fireEvent.change(screen.getByLabelText("Street address"), {
      target: { value: typed },
    });

    // The debounced type-ahead returns a suggestion whose visible label is
    // already city-shaped ("37 STREET"), NOT the raw "37 st bk" that was typed.
    const option = await screen.findByRole(
      "option",
      { name: /1279 37 STREET/i },
      { timeout: 2000 },
    );
    expect(option.textContent).not.toContain("st bk");

    // Pick it → the confirm card resolves through Geoclient.
    fireEvent.click(option);
    await screen.findByTestId("address-confirm-card");

    // The entered-input record is the RAW typed text, verbatim — the exact
    // <strong> textContent equals the typed string INCLUDING its surrounding
    // whitespace (the card renders the original, never a trimmed rewrite).
    const entered = screen.getByTestId("entered-input");
    const enteredStrong = entered.querySelector<HTMLElement>("strong");
    expect(enteredStrong?.textContent).toBe(typed);
    expect(entered.textContent).toContain(typed);
    // …distinct from the picked suggestion's city-shaped street…
    expect(entered.textContent).not.toContain("37 STREET");
    // …and distinct from the city-matched canonical address line.
    const matched = screen.getByTestId("confirm-address");
    expect(matched.textContent).toContain("37 STREET");
    expect(matched.textContent).not.toContain(typed);
    // The identity carried forward is the BBL, never an address string.
    expect(screen.getByTestId("resolved-bbl").textContent).toBe("3052960043");
  });
});
