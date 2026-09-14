import { describe, it, expect } from "vitest";
import { fetchAddressSuggestions, parseAddressSuggestions, GEOSEARCH_AUTOCOMPLETE } from "../address-search";

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
