import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AddressResolutionScreen } from "@/components/address/AddressResolutionScreen";
import { zolaLotUrl } from "@/lib/provenance-link";
import type { AddressDocumentOutcome } from "@/lib/address-api";
import { recalledAddress } from "@/lib/architect/selected-address";
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

/** M5-T023 / M5-T047: the confirm card mounts LotOutlineMap (fetches the lot
 * outline) and the record-address channel (fetches PLUTO.address). This pack is
 * about the ADDRESS confirm surface, so BOTH internal calls resolve to the
 * benign flag-off 404 (route_absent) and are served WITHOUT reaching — or
 * counting against — the address-resolution spy the tests assert on. Full
 * lot-outline coverage lives in lot-outline-map.test.tsx; record-address
 * coverage lives in the S10 block below (with its own routed stub) and in
 * record-address.test.ts. */
function lotGeometryStub(url: string): Response | null {
  if (url.includes("/lot-geometry") || url.includes("/record-address")) {
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

async function renderResolved(
  doc = resolvedDoc(),
  onConfirmLot?: (bbl: string, outcome: AddressDocumentOutcome) => void,
) {
  const fetchSpy = stubFetchOnce(jsonResponse(doc, 200));
  const view = render(<AddressResolutionScreen onConfirmLot={onConfirmLot} />);
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


describe("Optional same-page confirmation handoff", () => {
  afterEach(() => {
    sessionStorage.removeItem("nyc-buildability:confirmed-address:1000477501");
  });

  it("waits for explicit confirmation, remembers the address, and hands off without a navigation link", async () => {
    const doc = resolvedDoc();
    const onConfirmLot = vi.fn((bbl: string, outcome: AddressDocumentOutcome) => {
      // Presentation context is available before the dashboard receives the lot.
      expect(recalledAddress(bbl)?.sourceRecord).toEqual(outcome.view);
    });
    const { fetchSpy } = await renderResolved(doc, onConfirmLot);

    expect(onConfirmLot).not.toHaveBeenCalled();
    const action = screen.getByRole("button", { name: "Continue with this lot" });
    expect(action).not.toHaveAttribute("href");
    expect(screen.queryByRole("link", { name: "Continue with this lot" })).toBeNull();
    const requestsBeforeConfirm = fetchSpy.mock.calls.length;

    fireEvent.click(action);

    expect(onConfirmLot).toHaveBeenCalledOnce();
    expect(onConfirmLot).toHaveBeenCalledWith(
      doc.canonical.bbl,
      expect.objectContaining({
        kind: "document",
        correlationId: HTTP_CID,
        view: expect.objectContaining({
          status: "resolved",
          canonical: expect.objectContaining({ bbl: doc.canonical.bbl }),
        }),
      }),
    );
    expect(fetchSpy).toHaveBeenCalledTimes(requestsBeforeConfirm);
  });

  it("keeps both source warnings visible before the nonblocking callback action", async () => {
    const doc = resolvedDoc();
    doc.status = "resolved_with_warnings";
    doc.grc_message = "VERIFY HOUSE NUMBER";
    doc.grc2_message = "SECOND PASS WARNING";
    const onConfirmLot = vi.fn();
    await renderResolved(doc, onConfirmLot);

    const action = screen.getByRole("button", { name: "Continue with this lot" });
    const warnings = screen.getByTestId("address-warnings");
    expect(warnings).toHaveTextContent(doc.grc_message);
    expect(warnings).toHaveTextContent(doc.grc2_message);
    expect(warnings.compareDocumentPosition(action) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(action).not.toBeDisabled();
    expect(onConfirmLot).not.toHaveBeenCalled();
    fireEvent.click(action);
    expect(onConfirmLot).toHaveBeenCalledOnce();
  });

  it.each([null, "12345", HOSTILE_BBL])("does not offer or invoke the callback for invalid BBL %s", async bbl => {
    const doc = resolvedDoc();
    doc.canonical.bbl = bbl;
    const onConfirmLot = vi.fn();
    await renderResolved(doc, onConfirmLot);

    expect(screen.queryByTestId("confirm-continue")).toBeNull();
    expect(screen.queryByTestId("zola-link")).toBeNull();
    expect(onConfirmLot).not.toHaveBeenCalled();
  });

  it("allows Not my property to return to editing without accepting the lot", async () => {
    const onConfirmLot = vi.fn();
    const { fetchSpy } = await renderResolved(resolvedDoc(), onConfirmLot);
    const requestsBeforeEdit = fetchSpy.mock.calls.length;

    fireEvent.click(screen.getByTestId("not-my-property"));

    expect(onConfirmLot).not.toHaveBeenCalled();
    expect(screen.queryByTestId("address-confirm-card")).toBeNull();
    expect(screen.getByLabelText("Street")).toHaveValue("BROADWAY");
    await waitFor(() => expect(document.activeElement).toBe(screen.getByLabelText("Street")));
    expect(fetchSpy).toHaveBeenCalledTimes(requestsBeforeEdit);
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

  it("AS-2 (spec §5.2): the matched line carries an explicit 'City-matched address' label, distinct from the entered ('You searched for') and the PLUTO record labels", async () => {
    const doc = resolvedDoc();
    doc.input_echo.house_number = "1279";
    doc.input_echo.street = "37 street";
    doc.input_echo.borough = "Brooklyn";
    doc.canonical.bbl = "3052960043";
    doc.canonical.street_name_normalized = "37 STREET";
    doc.canonical.borough_name = "BROOKLYN";
    await renderResolved(doc);

    // The matched line is explicitly labelled, so a first-time analyst can tell
    // it apart from what they typed and from the city-record address.
    const label = screen.getByTestId("confirm-matched-label");
    expect(label.textContent).toBe("City-matched address");
    // The label sits immediately before the matched address line.
    const matched = screen.getByTestId("confirm-address");
    expect(
      label.compareDocumentPosition(matched) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    // Three DISTINCT identity vocabularies on the surface: matched vs entered.
    expect(screen.getByTestId("entered-input").textContent).toContain("You searched for");
    expect(screen.getByTestId("entered-input").textContent).toContain("1279 37 street");
    expect(matched.textContent).toContain("37 STREET");
  });

  it("AS-2: the matched-address label is absent when the city returned no printable normalized street (no line to label)", async () => {
    const doc = resolvedDoc();
    doc.input_echo.house_number = "";
    doc.input_echo.street = "raw entry";
    doc.input_echo.borough = "";
    doc.input_echo.zip = null;
    doc.canonical.street_name_normalized = null;
    doc.canonical.borough_name = null;
    doc.canonical.zip_code = null;
    await renderResolved(doc);
    expect(screen.queryByTestId("confirm-address")).toBeNull();
    expect(screen.queryByTestId("confirm-matched-label")).toBeNull();
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
        if (url.includes("/lot-geometry") || url.includes("/record-address")) {
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

    // HJ A3a: the entered-input record renders DISPLAY-TRIMMED (the visible
    // <strong> textContent is the typed string with surrounding whitespace
    // removed), while the TRUE raw string — surrounding whitespace and all — is
    // preserved verbatim in the title/aria-label attributes. Nothing the analyst
    // typed is silently rewritten; blank-looking padding just does not show.
    const entered = screen.getByTestId("entered-input");
    const enteredStrong = entered.querySelector<HTMLElement>("strong");
    expect(enteredStrong?.textContent).toBe(typed.trim());
    expect(enteredStrong?.getAttribute("title")).toBe(typed);
    expect(enteredStrong?.getAttribute("aria-label")).toBe(typed);
    // DB-033 rider b: supported, name-permitting semantics (role="img", NOT the
    // non-standard role="text") expose the entered value as the accessible NAME.
    // This is the raw-vs-display-trimmed DIFFER case: the aria-label ATTRIBUTE
    // keeps the untrimmed raw string, while the visible text and the computed
    // accessible name are the display-trimmed value (the accessible-name
    // computation normalizes the surrounding whitespace).
    expect(enteredStrong).toHaveAttribute("role", "img");
    expect(enteredStrong).toHaveAccessibleName(typed.trim());
    expect(screen.getByRole("img", { name: typed.trim() })).toBe(enteredStrong);
    expect(enteredStrong?.getAttribute("aria-label")).not.toBe(
      enteredStrong?.textContent,
    );
    expect(entered.textContent).toContain(typed.trim());
    // …distinct from the picked suggestion's city-shaped street…
    expect(entered.textContent).not.toContain("37 STREET");
    // …and distinct from the city-matched canonical address line.
    const matched = screen.getByTestId("confirm-address");
    expect(matched.textContent).toContain("37 STREET");
    expect(matched.textContent).not.toContain(typed.trim());
    // The identity carried forward is the BBL, never an address string.
    expect(screen.getByTestId("resolved-bbl").textContent).toBe("3052960043");
  });
});

/* ================================================================ *
 * S10 — DB-032 (M5-T047): the lot's PLUTO address-of-record renders as a
 * labeled CITY RECORD when it DIFFERS from the matched frontage; honest
 * no-line when equal, absent, or on error (D-073-R006 records class).
 * ================================================================ */

describe("S10 — DB-032 record-address channel on the confirm card", () => {
  const RECORD_SOURCE = {
    source_id: "nyc-dcp-pluto-soda",
    dataset_id: "64uk-42ks",
    dataset_version: "26v2",
    retrieved_at: "2026-09-19T04:00:03Z",
    request_url: "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3052960043",
  };

  function recordResponse(over: Record<string, unknown> = {}, status = 200): Response {
    const body =
      status === 200
        ? {
            document_kind: "record_address",
            bbl: "3052960043",
            outcome: "address_of_record",
            address: "3622 13 AVENUE",
            reason: null,
            source: RECORD_SOURCE,
            ...over,
          }
        : over;
    return new Response(JSON.stringify(body), {
      status,
      headers: { "content-type": "application/json", "X-Correlation-ID": HTTP_CID },
    });
  }

  /** Route by URL: the address resolution gets `doc`; the record-address
   * channel gets `record`; the lot-geometry call gets the benign flag-off 404. */
  function renderWithRecord(doc: Record<string, unknown>, record: Response) {
    const recordFetch = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/record-address")) {
          recordFetch();
          return Promise.resolve(record.clone());
        }
        if (url.includes("/lot-geometry")) {
          return Promise.resolve(
            new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 }),
          );
        }
        return Promise.resolve(jsonResponse(doc, 200));
      }),
    );
    render(<AddressResolutionScreen />);
    fillAndSubmit();
    return recordFetch;
  }

  /** The corner-lot resolved doc: matched frontage "1279 37 STREET", bbl
   * 3052960043 (whose PLUTO address-of-record is "3622 13 AVENUE"). */
  function cornerDoc() {
    const doc = resolvedDoc();
    doc.input_echo.house_number = "1279";
    doc.input_echo.street = "37 street";
    doc.input_echo.borough = "Brooklyn";
    doc.canonical.bbl = "3052960043";
    doc.canonical.street_name_normalized = "37 STREET";
    doc.canonical.borough_name = "BROOKLYN";
    doc.canonical.zip_code = "11218";
    return doc;
  }

  it("AS-1: shows 'City record address: 3622 13 AVENUE' as a record, distinct from the matched frontage", async () => {
    renderWithRecord(cornerDoc(), recordResponse());
    const card = await screen.findByTestId("address-confirm-card");
    const line = await screen.findByTestId("record-address");
    // The settled channel reports "shown" — the terminal value that renders the
    // line — distinct from the negative terminals asserted below.
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "shown"),
    );
    expect(line.textContent).toContain("3622 13 AVENUE");
    // It reads as a RECORD (no computed value implied) and names the source.
    expect(line.textContent).toContain("City record address");
    expect(line.textContent).toContain("PLUTO");
    // Distinct from the matched frontage line.
    expect(screen.getByTestId("confirm-address").textContent).toContain("37 STREET");
    expect(line.textContent).not.toContain("1279 37 STREET");
  });

  it("AS-2: when the record address equals the matched address, no duplicate record line renders", async () => {
    // Plain happy path: matched "120 BROADWAY"; record also "120 BROADWAY".
    renderWithRecord(
      resolvedDoc(),
      recordResponse({ bbl: "1000477501", address: "120 BROADWAY" }),
    );
    const card = await screen.findByTestId("address-confirm-card");
    // Observe the SETTLED response — an address_of_record present but EQUAL to
    // the matched frontage — before asserting the line is suppressed. Waiting on
    // the terminal "equal" status (set only after the fetch resolves and state
    // updates) rules out a false pass on the transient loading null.
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "equal"),
    );
    expect(screen.queryByTestId("record-address")).toBeNull();
  });

  it("AS-3: an honest absence (no address-of-record) renders no line and no placeholder", async () => {
    renderWithRecord(
      cornerDoc(),
      recordResponse({ outcome: "no_address_of_record", address: null, reason: "no address column" }),
    );
    const card = await screen.findByTestId("address-confirm-card");
    // The settled absence outcome — not the loading null — is what must produce
    // no line: wait for the terminal "absent" status, then assert no line.
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "absent"),
    );
    expect(screen.queryByTestId("record-address")).toBeNull();
  });

  it("AS-3: a connector error renders no line and never blocks the card", async () => {
    renderWithRecord(
      cornerDoc(),
      recordResponse({ state: "source_unavailable", message: "SODA down" }, 502),
    );
    // The card itself renders unaffected…
    const card = await screen.findByTestId("address-confirm-card");
    expect(screen.getByTestId("resolved-bbl").textContent).toBe("3052960043");
    // …and the SETTLED typed-error outcome (terminal "error" status, applied
    // only after the 502 is processed) renders no record line.
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "error"),
    );
    expect(screen.queryByTestId("record-address")).toBeNull();
  });
});

/* ================================================================ *
 * S11 — DB-033 (M5-T050) confirm-arc polish riders: (a) late-insert CLS,
 * (b) raw-input a11y exposure, (c) no-normalized-street copy + a11y honesty
 * (announce the full visible text), (d) corner-lot why-they-differ note. Rider
 * (i)'s original 512 title/aria length cap was SUPERSEDED by rider (c) (the
 * accessible name matches the full visible text; see the final case below), so
 * it is no longer a separate rider — DB-038(b) label hygiene.
 * ================================================================ */

describe("S11 — DB-033 confirm-arc polish riders (a-d; rider-i cap superseded by rider-c a11y honesty)", () => {
  const RECORD_SOURCE = {
    source_id: "nyc-dcp-pluto-soda",
    dataset_id: "64uk-42ks",
    dataset_version: "26v2",
    retrieved_at: "2026-09-19T04:00:03Z",
    request_url: "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3052960043",
  };

  function cornerDoc() {
    const doc = resolvedDoc();
    doc.input_echo.house_number = "1279";
    doc.input_echo.street = "37 street";
    doc.input_echo.borough = "Brooklyn";
    doc.canonical.bbl = "3052960043";
    doc.canonical.street_name_normalized = "37 STREET";
    doc.canonical.borough_name = "BROOKLYN";
    doc.canonical.zip_code = "11218";
    return doc;
  }

  function recordResponse(over: Record<string, unknown> = {}, status = 200): Response {
    const body =
      status === 200
        ? {
            document_kind: "record_address",
            bbl: "3052960043",
            outcome: "address_of_record",
            address: "3622 13 AVENUE",
            reason: null,
            source: RECORD_SOURCE,
            ...over,
          }
        : over;
    return new Response(JSON.stringify(body), {
      status,
      headers: { "content-type": "application/json", "X-Correlation-ID": HTTP_CID },
    });
  }

  /** Route resolution → `doc`; record-address → `record` (a Response, or the
   * literal "pending" to leave the fetch unresolved so the channel stays in its
   * loading state); lot-geometry → the benign flag-off 404. */
  function renderWithRecord(
    doc: Record<string, unknown>,
    record: Response | "pending",
  ) {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/record-address")) {
          return record === "pending"
            ? new Promise<Response>(() => undefined)
            : Promise.resolve(record.clone());
        }
        if (url.includes("/lot-geometry")) {
          return Promise.resolve(
            new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 }),
          );
        }
        return Promise.resolve(jsonResponse(doc, 200));
      }),
    );
    render(<AddressResolutionScreen />);
    fillAndSubmit();
  }

  // The identity + order of a card's direct element children. `data-testid` when
  // present, else the tag name — enough to prove the record note is a pure APPEND
  // (nothing above it inserted, moved, or collapsed) without depending on the
  // async LotOutlineMap child's internal markup.
  const childIds = (el: Element): string[] =>
    Array.from(el.children).map((c) => c.getAttribute("data-testid") ?? c.tagName);

  it("rider a (CLS) + rider b (reading order): the shown record note follows BOTH interactive actions and precedes the non-interactive Meta footer — out of the interactive flow, not an in-flow reservation", async () => {
    renderWithRecord(cornerDoc(), recordResponse());
    const card = await screen.findByTestId("address-confirm-card");
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "shown"),
    );
    const note = screen.getByTestId("record-address");
    const cta = screen.getByTestId("confirm-continue");
    const notMyProperty = screen.getByTestId("not-my-property");
    // DB-035 rider b: content-before-footer reading order — the metadata footer's
    // reference id is the card's LAST element.
    const metaRef = screen.getByTestId("correlation-id");
    // THE stability mechanism (not "no min-height" / "shared prose"): the record
    // note renders OUTSIDE the interactive flow — it FOLLOWS both the Continue and
    // the "Not my property" actions in the DOM. A late insert below every settled
    // interactive element cannot move any of them, for a record address of any
    // length or wrap.
    expect(
      cta.compareDocumentPosition(note) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(
      notMyProperty.compareDocumentPosition(note) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    // DB-035 rider b: the note precedes the non-interactive Meta footer (only that
    // footer, never an interactive element, shifts down on the insert). The note
    // is NO LONGER the card's last child — the Meta footer is.
    expect(
      note.compareDocumentPosition(metaRef) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(card.lastElementChild).toContainElement(metaRef);
    // The former approximate reservation (and its slot) no longer exist in any state.
    expect(screen.queryByTestId("record-address-reserved")).toBeNull();
    expect(screen.queryByTestId("record-address-slot")).toBeNull();
    // The note still reads as a RECORD and carries the rider-d why explanation.
    expect(note.querySelector("strong")?.textContent).toBe("3622 13 AVENUE");
    expect(note.textContent).toContain("City record address");
    expect(note.textContent).toContain("PLUTO");
    expect(screen.getByTestId("record-address-why").textContent).toBe(
      "A single tax lot can front on more than one street, so its address of record can differ from the frontage you searched.",
    );
  });

  it("rider a (CLS): a DELAYED address_of_record is APPENDED as the last child only — the Continue action and every element above it are byte-identical across the resolve", async () => {
    // A manually-controlled deferred record-address response: the card mounts with
    // the channel loading (no note, no reservation), then the SAME mounted card
    // receives the resolved record — a delayed response resolved IN PLACE.
    let resolveRecord: (response: Response) => void = () => undefined;
    const deferred = new Promise<Response>((resolve) => {
      resolveRecord = resolve;
    });
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/record-address")) return deferred;
        if (url.includes("/lot-geometry")) {
          return Promise.resolve(
            new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 }),
          );
        }
        return Promise.resolve(jsonResponse(cornerDoc(), 200));
      }),
    );
    render(<AddressResolutionScreen />);
    fillAndSubmit();

    const card = await screen.findByTestId("address-confirm-card");
    // Loading: the record note does NOT exist yet and there is NO reservation box —
    // the card is exactly its no-record shape (the honest as-today presentation).
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "loading"),
    );
    expect(screen.queryByTestId("record-address")).toBeNull();
    expect(screen.queryByTestId("record-address-reserved")).toBeNull();
    expect(screen.queryByTestId("record-address-slot")).toBeNull();
    // Snapshot the interactive action and the child order before the resolve, so we
    // can prove the delayed line changes NOTHING above it.
    const ctaBefore = screen.getByTestId("confirm-continue");
    const ctaHtmlBefore = ctaBefore.outerHTML;
    const childIdsBefore = childIds(card);

    // Resolve the delayed response on the SAME mounted card.
    resolveRecord(recordResponse());
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "shown"),
    );

    const note = screen.getByTestId("record-address");
    const cta = screen.getByTestId("confirm-continue");
    // The Continue action is the SAME node with byte-identical markup — it did not
    // re-mount, change, or (given the insert-below-the-actions child order below) move.
    expect(cta).toBe(ctaBefore);
    expect(cta.outerHTML).toBe(ctaHtmlBefore);
    // DB-035 rider b: the ONLY DOM change is the record note inserted immediately
    // BEFORE the non-interactive Meta footer (the card's last child). Every child
    // through the "Not my property" action keeps its identity and order; only the
    // footer shifts down one slot. The note sits after the Continue action. The
    // mechanism is structural, not a height guess.
    const idsAfter = childIds(card);
    // The Meta footer is still the last child (content-before-footer order).
    expect(idsAfter[idsAfter.length - 1]).toBe(
      childIdsBefore[childIdsBefore.length - 1],
    );
    // The record note is the new second-to-last child, immediately before the footer.
    expect(idsAfter[idsAfter.length - 2]).toBe("record-address");
    const childrenAfter = Array.from(card.children);
    expect(childrenAfter[childrenAfter.length - 2]).toBe(note);
    // Everything before the inserted note equals everything before the footer previously
    // (no interactive element inserted, moved, or collapsed).
    expect(idsAfter.slice(0, -2)).toEqual(childIdsBefore.slice(0, -1));
    expect(
      cta.compareDocumentPosition(note) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    // The arrived line reads as a RECORD (rider d why note intact).
    expect(note.querySelector("strong")?.textContent).toBe("3622 13 AVENUE");
    expect(note.textContent).toContain("can differ from the matched frontage");
  });

  it("rider a (CLS): an honest absence renders as today — no record note and no reserved box", async () => {
    renderWithRecord(
      cornerDoc(),
      recordResponse({
        outcome: "no_address_of_record",
        address: null,
        reason: "no address column",
      }),
    );
    const card = await screen.findByTestId("address-confirm-card");
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "absent"),
    );
    // No line, and — critically — no leftover reserved box: the absent presentation
    // is byte-identical to a card that never carried a record channel.
    expect(screen.queryByTestId("record-address")).toBeNull();
    expect(screen.queryByTestId("record-address-reserved")).toBeNull();
    expect(screen.queryByTestId("record-address-slot")).toBeNull();
  });

  it.each([
    {
      label: "equal",
      make: () => recordResponse({ bbl: "3052960043", address: "1279 37 STREET" }),
      settled: "equal",
    },
    {
      label: "absent",
      make: () =>
        recordResponse({
          outcome: "no_address_of_record",
          address: null,
          reason: "no address column",
        }),
      settled: "absent",
    },
    {
      label: "error",
      make: () =>
        recordResponse({ state: "source_unavailable", message: "SODA down" }, 502),
      settled: "error",
    },
    {
      label: "route-absent",
      make: () =>
        new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 }),
      settled: "route-absent",
    },
  ])(
    "rider a (CLS): a DELAYED $label outcome renders no record note and no reserved box — the card is byte-stable across the settle (honest as-today absent presentation)",
    async ({ make, settled }) => {
      // No reservation is made WHILE loading, so a delayed settle to any non-shown
      // terminal collapses nothing — the card's direct children are identical before
      // and after, the required absent-line presentation reached without a shift.
      let resolveRecord: (response: Response) => void = () => undefined;
      const deferred = new Promise<Response>((resolve) => {
        resolveRecord = resolve;
      });
      vi.stubGlobal(
        "fetch",
        vi.fn((input: RequestInfo | URL) => {
          const url = String(input);
          if (url.includes("/record-address")) return deferred;
          if (url.includes("/lot-geometry")) {
            return Promise.resolve(
              new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 }),
            );
          }
          return Promise.resolve(jsonResponse(cornerDoc(), 200));
        }),
      );
      render(<AddressResolutionScreen />);
      fillAndSubmit();

      const card = await screen.findByTestId("address-confirm-card");
      // While the delayed response is in flight there is no note and no reserved box.
      await waitFor(() =>
        expect(card).toHaveAttribute("data-record-address-status", "loading"),
      );
      expect(screen.queryByTestId("record-address")).toBeNull();
      expect(screen.queryByTestId("record-address-reserved")).toBeNull();
      expect(screen.queryByTestId("record-address-slot")).toBeNull();
      const childIdsBefore = childIds(card);

      // Resolve LATE to the non-shown terminal.
      resolveRecord(make());
      await waitFor(() =>
        expect(card).toHaveAttribute("data-record-address-status", settled),
      );

      // Still no note, no reserved box; the direct children are unchanged — nothing
      // was inserted and nothing collapsed.
      expect(screen.queryByTestId("record-address")).toBeNull();
      expect(screen.queryByTestId("record-address-reserved")).toBeNull();
      expect(childIds(card)).toEqual(childIdsBefore);
    },
  );

  it("rider b (a11y): the entered value is exposed as the accessible name (role=img + aria-label), visible text stays trimmed", async () => {
    await renderResolved();
    // input_echo → enteredInput "120 BROADWAY, Manhattan" (no surrounding
    // whitespace here; the whitespace raw-vs-trimmed DIFFER case is covered by S9).
    const raw = "120 BROADWAY, Manhattan";
    const entered = screen.getByTestId("entered-input");
    const strong = entered.querySelector<HTMLElement>("strong");
    // role="img" is a SUPPORTED, name-permitting ARIA role (unlike the
    // non-standard role="text"): it makes the otherwise name-prohibited <strong> a
    // named leaf, so the raw value is exposed to assistive tech as the accessible
    // NAME, resolvable by role + name…
    expect(strong).toHaveAttribute("role", "img");
    expect(strong).toHaveAccessibleName(raw);
    expect(screen.getByRole("img", { name: raw })).toBe(strong);
    // …the title is kept for sighted hover, the aria-label carries the raw value,
    // and the visible text stays trimmed.
    expect(strong?.getAttribute("title")).toBe(raw);
    expect(strong?.getAttribute("aria-label")).toBe(raw);
    expect(strong?.textContent).toBe(raw);
  });

  it("rider c (copy): in the no-normalized-street case the entered note does NOT reference the absent city-matched line", async () => {
    const doc = resolvedDoc();
    // No printable matched line: no house number, no normalized street, no borough
    // name → addressLine is empty and the fallback note renders instead.
    doc.input_echo.house_number = "";
    doc.input_echo.street = "my raw one-box entry";
    doc.input_echo.borough = "";
    doc.input_echo.zip = null;
    doc.canonical.street_name_normalized = null;
    doc.canonical.borough_name = null;
    doc.canonical.zip_code = null;
    await renderResolved(doc);
    // The matched line is absent (the fallback note shows in its place).
    expect(screen.queryByTestId("confirm-address")).toBeNull();
    const entered = screen.getByTestId("entered-input");
    expect(entered.textContent).toContain("my raw one-box entry");
    // The note must NOT claim to show it "alongside the city-matched address".
    expect(entered.textContent).not.toContain("city-matched address");
    // DB-035 rider d (M5-T055): the redundant "We show it as the address you
    // searched for" sentence is trimmed — "You searched for X" already states it is
    // the entered value. What remains is one clear identity sentence.
    expect(entered.textContent).not.toContain(
      "We show it as the address you searched for",
    );
    expect(entered.textContent).toContain(
      "You searched for",
    );
    expect(entered.textContent).toContain(
      "The identity we carry forward is the tax lot (BBL).",
    );
  });

  it("rider c (copy): the normal (matched present) case keeps the accepted wording byte-identical", async () => {
    await renderResolved();
    expect(screen.getByTestId("entered-input").textContent).toContain(
      "We show it alongside the city-matched address so you can compare them; the identity we carry forward is the tax lot (BBL).",
    );
  });

  it("rider d (note): when the record differs, one neutral RECORD why-they-differ note renders (no computed value implied)", async () => {
    renderWithRecord(cornerDoc(), recordResponse());
    const card = await screen.findByTestId("address-confirm-card");
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "shown"),
    );
    const why = screen.getByTestId("record-address-why");
    expect(why.textContent).toContain("more than one street");
    // It is a RECORD explanation — it states no measurement or computed value.
    expect(why.textContent).not.toMatch(/\d/);
  });

  it("rider d (note): an equal record renders no line and therefore no why-they-differ note", async () => {
    renderWithRecord(
      resolvedDoc(),
      recordResponse({ bbl: "1000477501", address: "120 BROADWAY" }),
    );
    const card = await screen.findByTestId("address-confirm-card");
    await waitFor(() =>
      expect(card).toHaveAttribute("data-record-address-status", "equal"),
    );
    expect(screen.queryByTestId("record-address-why")).toBeNull();
  });

  it("rider c (a11y honesty): an over-long entered value announces the FULL visible text — the accessible name matches what the eye sees, never a truncation the visible text does not show (supersedes the DB-033 rider-i 512 attribute cap)", async () => {
    const doc = resolvedDoc();
    const longEntry = "X".repeat(600);
    doc.input_echo.house_number = "";
    doc.input_echo.street = longEntry;
    doc.input_echo.borough = "";
    doc.input_echo.zip = null;
    await renderResolved(doc);
    const entered = screen.getByTestId("entered-input");
    const strong = entered.querySelector<HTMLElement>("strong");
    // Visible text is the full trimmed raw value (600 chars, nothing to trim).
    expect(strong?.textContent).toBe(longEntry);
    // DB-035 rider c: THE equality binding — the announced accessible NAME is the
    // full visible text, NOT a 513-char truncation. No "…" marker is announced that
    // the eye does not see; the title/aria attributes carry the full raw value.
    expect(strong?.getAttribute("title")).toBe(longEntry);
    expect(strong?.getAttribute("aria-label")).toBe(longEntry);
    expect(strong).toHaveAccessibleName(longEntry);
    // The accessible name equals the visible text exactly (announced === seen).
    expect(strong).toHaveAccessibleName(strong?.textContent ?? "");
    // No truncation marker anywhere — the former dishonest 513-char cap is gone.
    expect(strong?.getAttribute("aria-label")?.endsWith("…")).toBe(false);
  });
});
