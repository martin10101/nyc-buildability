import { describe, it, expect } from "vitest";
import { ADDRESS_SEARCH_MAX_ATTEMPTS, fetchAddressSearch, fetchAddressSuggestions, parseAddressSuggestions, GEOSEARCH_AUTOCOMPLETE, GEOSEARCH_SEARCH } from "../address-search";

// Shape recorded from NYC DCP GeoSearch v2 (M5-T029 G1). PAD BBL is intentionally never consumed.
const feature = (borough = "Manhattan") => ({ type: "Feature", properties: { source: "nycpad", housenumber: "120", street: "BROADWAY", borough, postalcode: "10271", label: "120 BROADWAY, New York, NY, USA", addendum: { pad: { bbl: "1000477501", version: "26c" } } }, geometry: { type: "Point", coordinates: [-74.010542, 40.708233] } });
const collection = (...features: unknown[]) => ({ type: "FeatureCollection", features });
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

describe("official one-box address suggestions", () => {
  it.each(["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"])("retains official parts for %s without using the candidate BBL", borough => {
    const result = parseAddressSuggestions(collection(feature(borough)));
    expect(result?.[0].query).toEqual({ houseNumber: "120", street: "BROADWAY", borough, zip: "10271" });
    expect(result?.[0]).not.toHaveProperty("bbl");
  });
  it("retains a Queens hyphenated house number and rejects missing or malformed parts", () => {
    const queens = feature("Queens"); queens.properties.housenumber = "120-55";
    expect(parseAddressSuggestions(collection(queens))?.[0].query.houseNumber).toBe("120-55");
    expect(parseAddressSuggestions(collection({ ...queens, properties: { ...queens.properties, street: "" } }))).toEqual([]);
    expect(parseAddressSuggestions(collection({ ...queens, properties: { ...queens.properties, borough: "guess" } }))).toEqual([]);
    expect(parseAddressSuggestions({ features: [] })).toBeNull();
    expect(parseAddressSuggestions({ type: "FeatureCollection", features: [null] })).toBeNull();
  });
  it("bounds suggestion count and sends typed text only to the fixed official endpoint", async () => {
    let requestUrl = "";
    const fetchImpl: typeof fetch = async input => { requestUrl = String(input); return response(collection(...Array.from({ length: 20 }, () => feature()))); };
    const result = await fetchAddressSuggestions("120 Broadway & Brooklyn", { fetchImpl });
    expect(result.kind === "suggestions" && result.suggestions).toHaveLength(8);
    const url = new URL(requestUrl);
    expect(url.origin + url.pathname).toBe(GEOSEARCH_AUTOCOMPLETE);
    expect(url.searchParams.get("text")).toBe("120 Broadway & Brooklyn");
  });
  it("keeps no-match, rate-limit and malformed responses recoverable", async () => {
    expect(await fetchAddressSuggestions("120 Broadway", { fetchImpl: async () => response(collection()) })).toEqual({ kind: "suggestions", suggestions: [] });
    expect(await fetchAddressSuggestions("120 Broadway", { fetchImpl: async () => response({}, 429) })).toEqual({ kind: "error", reason: "rate_limited" });
    expect(await fetchAddressSuggestions("120 Broadway", { fetchImpl: async () => response({ error: "bad" }) })).toEqual({ kind: "error", reason: "malformed" });
    expect(await fetchAddressSuggestions("120 Broadway", { fetchImpl: async () => { throw new Error("offline"); } })).toEqual({ kind: "error", reason: "unavailable" });
  });
  it("enforces response size and a deadline even when a transport ignores abort", async () => {
    expect(await fetchAddressSuggestions("120 Broadway", { fetchImpl: async () => response({ huge: "x".repeat(129_000) }) })).toEqual({ kind: "error", reason: "malformed" });
    expect(await fetchAddressSuggestions("120 Broadway", { fetchImpl: () => new Promise(() => undefined), timeoutMs: 5 })).toEqual({ kind: "error", reason: "timeout" });
    const controller = new AbortController();
    const pending = fetchAddressSuggestions("120 Broadway", { signal: controller.signal, fetchImpl: () => new Promise(() => undefined) });
    controller.abort();
    expect(await pending).toEqual({ kind: "aborted" });
  });
});

describe("bounded recovery and the explicit full-address action (M5-T032)", () => {
  it("AS-1: recovers a transient 503 within the bounded retry and returns suggestions (never a partial/hidden error)", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async () => { calls += 1; return calls < 2 ? response({}, 503) : response(collection(feature())); };
    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
    expect(result.kind === "suggestions" && result.suggestions).toHaveLength(1);
    expect(calls).toBe(2);
  });

  it("AS-2: stops at the retry bound on repeated 503s and returns a DISTINCT source_unavailable (not a generic 'unavailable')", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async () => { calls += 1; return response({}, 503); };
    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
    expect(result).toEqual({ kind: "error", reason: "source_unavailable" });
    expect(calls).toBe(ADDRESS_SEARCH_MAX_ATTEMPTS);
  });

  it("AS-6: never retries a 429 — rate-limit is its own reason, distinct from a 503 source failure", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async () => { calls += 1; return response({}, 429); };
    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
    expect(result).toEqual({ kind: "error", reason: "rate_limited" });
    expect(calls).toBe(1);
  });

  it("AS-4: fetchAddressSearch targets the /search endpoint (same upstream service) and shares the bounded 5xx recovery", async () => {
    let requestUrl = "";
    let calls = 0;
    const fetchImpl: typeof fetch = async input => { requestUrl = String(input); calls += 1; return calls < 2 ? response({}, 503) : response(collection(feature("Queens"))); };
    const result = await fetchAddressSearch("120-55 Queens Boulevard, Queens", { fetchImpl, backoffMs: 0 });
    expect(result.kind === "suggestions" && result.suggestions).toHaveLength(1);
    const url = new URL(requestUrl);
    expect(url.origin + url.pathname).toBe(GEOSEARCH_SEARCH);
    expect(calls).toBe(2);
  });

  it("AS-3: a VALID reply arriving AFTER the deadline is a distinct timeout — terminal, never retried, never a stacked deadline", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async () => {
      calls += 1;
      // A genuinely valid collection, but it only resolves well past the deadline.
      return new Promise<Response>(resolve =>
        setTimeout(() => resolve(response(collection(feature()))), 60),
      );
    };
    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, timeoutMs: 5, backoffMs: 0 });
    expect(result).toEqual({ kind: "error", reason: "timeout" });
    // timeout is terminal: the retry bound is spent only on 5xx, and the
    // per-attempt deadline is never re-armed on a slow reply.
    expect(calls).toBe(1);
  });

  it("aborting mid-backoff returns aborted and never emits a suggestion from the abandoned retry", async () => {
    const controller = new AbortController();
    let calls = 0;
    const fetchImpl: typeof fetch = async () => { calls += 1; controller.abort(); return response({}, 503); };
    const result = await fetchAddressSuggestions("120 Broadway", { signal: controller.signal, fetchImpl, backoffMs: 50 });
    expect(result).toEqual({ kind: "aborted" });
    expect(calls).toBe(1);
  });
});

/**
 * AS-8: one real-shape NYC address per borough — Manhattan, Brooklyn, Queens,
 * the Bronx, and Staten Island — resolves END-TO-END through the repaired fetch
 * flow (fetchAddressSuggestions / fetchAddressSearch), not only through the
 * parse helper. A Queens HYPHENATED house number is exercised through both the
 * autocomplete and the explicit full-address /search actions. Every fixture is
 * deterministic (a mocked fetch); no live network is required (AS-11 covers the
 * separate dated live smoke check). BBL-prefix assertions alone do not satisfy
 * AS-8 — these drive the flow and assert the parsed one-box query round-trips
 * while the candidate PAD BBL is never consumed.
 */
describe("AS-8: deterministic per-borough address-flow fixtures (M5-T032)", () => {
  const boroughFeature = (borough: string, houseNumber: string, street: string, zip: string) => ({
    type: "Feature",
    properties: {
      source: "nycpad",
      housenumber: houseNumber,
      street,
      borough,
      postalcode: zip,
      label: `${houseNumber} ${street}, ${borough}, NY, USA`,
      // PAD BBL is present in the real payload but must never be consumed.
      addendum: { pad: { bbl: "1000477501", version: "26c" } },
    },
    geometry: { type: "Point", coordinates: [-73.9, 40.7] },
  });

  const perBorough: Array<[string, string, string, string]> = [
    ["Manhattan", "120", "BROADWAY", "10271"],
    ["Brooklyn", "209", "JORALEMON STREET", "11201"],
    ["Queens", "120-55", "QUEENS BOULEVARD", "11424"],
    ["Bronx", "851", "GRAND CONCOURSE", "10451"],
    ["Staten Island", "10", "RICHMOND TERRACE", "10301"],
  ];

  it.each(perBorough)(
    "resolves a %s address through the repaired autocomplete flow, round-tripping the one-box query and never consuming the candidate BBL",
    async (borough, houseNumber, street, zip) => {
      let requestUrl = "";
      const fetchImpl: typeof fetch = async input => { requestUrl = String(input); return response(collection(boroughFeature(borough, houseNumber, street, zip))); };
      const result = await fetchAddressSuggestions(`${houseNumber} ${street}`, { fetchImpl, backoffMs: 0 });
      expect(result.kind).toBe("suggestions");
      expect(result.kind === "suggestions" && result.suggestions[0].query).toEqual({ houseNumber, street, borough, zip });
      expect(result.kind === "suggestions" && result.suggestions[0]).not.toHaveProperty("bbl");
      const url = new URL(requestUrl);
      expect(url.origin + url.pathname).toBe(GEOSEARCH_AUTOCOMPLETE);
    },
  );

  it("resolves the Queens HYPHENATED house number through the explicit full-address /search action too (same upstream service)", async () => {
    let requestUrl = "";
    const fetchImpl: typeof fetch = async input => { requestUrl = String(input); return response(collection(boroughFeature("Queens", "120-55", "QUEENS BOULEVARD", "11424"))); };
    const result = await fetchAddressSearch("120-55 Queens Boulevard, Queens", { fetchImpl, backoffMs: 0 });
    expect(result.kind === "suggestions" && result.suggestions[0].query).toEqual({ houseNumber: "120-55", street: "QUEENS BOULEVARD", borough: "Queens", zip: "11424" });
    const url = new URL(requestUrl);
    expect(url.origin + url.pathname).toBe(GEOSEARCH_SEARCH);
  });
});
