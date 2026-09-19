import { describe, it, expect } from "vitest";
import { ADDRESS_SEARCH_MAX_ATTEMPTS, fetchAddressSearch, fetchAddressSuggestions, parseAddressSuggestions, normalizeStreetForMatch, resolveLotFromGeoSearch, GEOSEARCH_AUTOCOMPLETE, GEOSEARCH_SEARCH } from "../address-search";

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
 * DB-006: the retry/label gate. Only a transient server failure (>= 500) is the
 * retried `source_unavailable`. A 4xx the service will not accept (404/422/400)
 * is a DISTINCT `rejected` — never retried (retrying cannot change it) and never
 * folded into the transient-failure label.
 */
describe("DB-006: 4xx is a distinct, non-retried `rejected`; only >= 500 is the retried `source_unavailable`", () => {
  it("AS-1: a 404 is NOT retried and is NOT labelled source_unavailable (autocomplete)", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async () => { calls += 1; return response({ error: "not found" }, 404); };
    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
    expect(result).toEqual({ kind: "error", reason: "rejected" });
    expect(result).not.toEqual({ kind: "error", reason: "source_unavailable" });
    expect(calls).toBe(1);
  });

  it("AS-1: a 422 on the explicit full-address /search is likewise a single-attempt `rejected`", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async () => { calls += 1; return response({ error: "unprocessable" }, 422); };
    const result = await fetchAddressSearch("120 Broadway, New York", { fetchImpl, backoffMs: 0 });
    expect(result).toEqual({ kind: "error", reason: "rejected" });
    expect(calls).toBe(1);
  });

  it("AS-1: a 400 is a single-attempt `rejected` (the retry bound is untouched)", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async () => { calls += 1; return response({ error: "bad request" }, 400); };
    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
    expect(result).toEqual({ kind: "error", reason: "rejected" });
    expect(calls).toBe(1);
  });

  it("AS-1: a 500 IS the retried source_unavailable — it spends the full retry bound, unlike a 4xx", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async () => { calls += 1; return response({}, 500); };
    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
    expect(result).toEqual({ kind: "error", reason: "source_unavailable" });
    expect(calls).toBe(ADDRESS_SEARCH_MAX_ATTEMPTS);
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

/**
 * DB-026: the GeoSearch address→lot EQUALITY GATE, pinned offline from the
 * byte-faithful corpus (docs/research/db026-address-to-lot-fixture-capture.md
 * §1–§5). Every body below is the verbatim minified server response captured
 * 2026-09-19; they prove the load-bearing hazard — GeoSearch /search returns a
 * plausible WRONG lot for nonsense input at the SAME confidence:0.8 /
 * match_type:"fallback" as the true hit — so ONLY field equality can refuse it.
 */
describe("DB-026: GeoSearch address→lot equality gate (byte-faithful corpus)", () => {
  // §1 — /search size=3: true hit + GARAGE sibling (same bbl, other bin) + EAST 37 (different lot).
  const SEARCH_1279_37_STREET_SIZE3 = `{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"1279 37 street brooklyn","size":3,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"1279 37 street","housenumber":"1279","street":"37 street","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790343142},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.98522,40.641968]},"properties":{"id":"1309911","gid":"nycpad:venue:1309911","layer":"venue","source":"nycpad","source_id":"1309911","country_code":"US","name":"1279 37 STREET","housenumber":"1279","street":"37 STREET","postalcode":"11218","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3340270","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.985331,40.642037]},"properties":{"id":"1309902","gid":"nycpad:venue:1309902","layer":"venue","source":"nycpad","source_id":"1309902","country_code":"US","name":"1279 GARAGE 37 STREET","housenumber":"1279 GARAGE","street":"37 STREET","postalcode":"11218","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 GARAGE 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3123204","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.93952,40.624792]},"properties":{"id":"1632496","gid":"nycpad:venue:1632496","layer":"venue","source":"nycpad","source_id":"1632496","country_code":"US","name":"1279 EAST 37 STREET","housenumber":"1279","street":"EAST 37 STREET","postalcode":"11210","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Flatlands","neighbourhood_gid":"whosonfirst:neighbourhood:85819585","label":"1279 EAST 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3076370038","bin":"3209116","version":"26c"}}}}],"bbox":[-73.985331,40.624792,-73.93952,40.642037]}`;
  // §2 — /search "th" variant: parsed_text.street="37th street" resolves to the same canonical lot.
  const SEARCH_1279_37TH_STREET = `{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"1279 37th street brooklyn","size":1,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"1279 37th street","housenumber":"1279","street":"37th street","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790357661},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.98522,40.641968]},"properties":{"id":"1309911","gid":"nycpad:venue:1309911","layer":"venue","source":"nycpad","source_id":"1309911","country_code":"US","name":"1279 37 STREET","housenumber":"1279","street":"37 STREET","postalcode":"11218","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3340270","version":"26c"}}}}],"bbox":[-73.98522,40.641968,-73.98522,40.641968]}`;
  // §3 — /search reverse frontage "3622 13 avenue": SAME bbl 3052960043, PLUTO-canonical name "3622 13 AVENUE".
  const SEARCH_3622_13_AVENUE = `{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"3622 13 avenue brooklyn","size":1,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"3622 13 avenue","housenumber":"3622","street":"13 avenue","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790357962},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.98522,40.641968]},"properties":{"id":"1309903","gid":"nycpad:venue:1309903","layer":"venue","source":"nycpad","source_id":"1309903","country_code":"US","name":"3622 13 AVENUE","housenumber":"3622","street":"13 AVENUE","postalcode":"11218","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"3622 13 AVENUE, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3340270","version":"26c"}}}}],"bbox":[-73.98522,40.641968,-73.98522,40.641968]}`;
  // §4a — nonexistent street "zzqqxx": HTTP 200 with a WRONG real lot "1279 53 STREET" at fallback/0.8.
  const SEARCH_NONEXISTENT_STREET = `{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"1279 zzqqxx street brooklyn","size":1,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"1279 zzqqxx street","housenumber":"1279","street":"zzqqxx street","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790374793},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.994554,40.633088]},"properties":{"id":"1359602","gid":"nycpad:venue:1359602","layer":"venue","source":"nycpad","source_id":"1359602","country_code":"US","name":"1279 53 STREET","housenumber":"1279","street":"53 STREET","postalcode":"11219","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Borough Park","neighbourhood_gid":"whosonfirst:neighbourhood:420782907","label":"1279 53 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3056627501","bin":"3138712","version":"26c"}}}}],"bbox":[-73.994554,40.633088,-73.994554,40.633088]}`;
  // §4b — out-of-range house number "99999": returns "207 37 STREET" (housenumber "207" ≠ query).
  const SEARCH_OUT_OF_RANGE_HOUSE = `{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"99999 37 street brooklyn","size":1,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"99999 37 street","housenumber":"99999","street":"37 street","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790375009},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-74.008191,40.655949]},"properties":{"id":"758253","gid":"nycpad:venue:758253","layer":"venue","source":"nycpad","source_id":"758253","country_code":"US","name":"207 37 STREET","housenumber":"207","street":"37 STREET","postalcode":"11232","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Sunset Park","neighbourhood_gid":"whosonfirst:neighbourhood:85851575","label":"207 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3006950001","bin":"3336906","version":"26c"}}}}],"bbox":[-74.008191,40.655949,-74.008191,40.655949]}`;
  // §5 — /autocomplete: feature properties OMIT confidence and match_type entirely.
  const AUTOCOMPLETE_1279_37_ST = `{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"1279 37 st","parser":"pelias","parsed_text":{"subject":"1279 37 st","housenumber":"1279","street":"37 st"},"size":10,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790375218},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.98522,40.641968]},"properties":{"id":"1309911","gid":"nycpad:venue:1309911","layer":"venue","source":"nycpad","source_id":"1309911","country_code":"US","name":"1279 37 STREET","housenumber":"1279","street":"37 STREET","postalcode":"11218","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3340270","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.985331,40.642037]},"properties":{"id":"1309902","gid":"nycpad:venue:1309902","layer":"venue","source":"nycpad","source_id":"1309902","country_code":"US","name":"1279 GARAGE 37 STREET","housenumber":"1279 GARAGE","street":"37 STREET","postalcode":"11218","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 GARAGE 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3123204","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.93952,40.624792]},"properties":{"id":"1632496","gid":"nycpad:venue:1632496","layer":"venue","source":"nycpad","source_id":"1632496","country_code":"US","name":"1279 EAST 37 STREET","housenumber":"1279","street":"EAST 37 STREET","postalcode":"11210","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Flatlands","neighbourhood_gid":"whosonfirst:neighbourhood:85819585","label":"1279 EAST 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3076370038","bin":"3209116","version":"26c"}}}}],"bbox":[-73.985331,40.624792,-73.93952,40.642037]}`;
  const parse = (body: string): unknown => JSON.parse(body);

  it("AS-1: the true hit passes the gate → bbl 3052960043 + the matched city address, with match_type/confidence recorded but not tested", () => {
    const result = resolveLotFromGeoSearch(parse(SEARCH_1279_37_STREET_SIZE3));
    expect(result.kind).toBe("resolved");
    if (result.kind !== "resolved") return;
    expect(result.lot.bbl).toBe("3052960043");
    expect(result.lot.matchedName).toBe("1279 37 STREET");
    expect(result.lot.matchedHouseNumber).toBe("1279");
    expect(result.lot.matchedStreet).toBe("37 STREET");
    expect(result.lot.bin).toBe("3340270");
    expect(result.lot.padVersion).toBe("26c");
    // Recorded — but the fallback/0.8 pair is identical on the nonsense probes below,
    // so it can never be the success test.
    expect(result.lot.matchType).toBe("fallback");
    expect(result.lot.confidence).toBe(0.8);
  });

  it("AS-2: the '37th' variant matches the SAME lot under the documented ordinal normalization", () => {
    expect(normalizeStreetForMatch("37th street")).toBe("37 STREET");
    expect(normalizeStreetForMatch("37 STREET")).toBe("37 STREET");
    const result = resolveLotFromGeoSearch(parse(SEARCH_1279_37TH_STREET));
    expect(result.kind === "resolved" && result.lot.bbl).toBe("3052960043");
  });

  it("AS-3: the reverse frontage and the GARAGE sibling bind to the SAME pad.bbl — never the address string or bin", () => {
    const trueHit = resolveLotFromGeoSearch(parse(SEARCH_1279_37_STREET_SIZE3));
    const reverse = resolveLotFromGeoSearch(parse(SEARCH_3622_13_AVENUE));
    expect(trueHit.kind).toBe("resolved");
    expect(reverse.kind).toBe("resolved");
    if (trueHit.kind !== "resolved" || reverse.kind !== "resolved") return;
    // Same lot; the two frontages carry DIFFERENT address strings.
    expect(reverse.lot.bbl).toBe(trueHit.lot.bbl);
    expect(reverse.lot.bbl).toBe("3052960043");
    expect(reverse.lot.matchedName).toBe("3622 13 AVENUE");
    expect(reverse.lot.matchedName).not.toBe(trueHit.lot.matchedName);
    // The GARAGE sibling (feature 2 of §1) is the SAME bbl with a DIFFERENT bin —
    // identity is the bbl, proving the gate keys on neither bin nor address string.
    const features = (parse(SEARCH_1279_37_STREET_SIZE3) as { features: Array<{ properties: { name: string; addendum: { pad: { bbl: string; bin: string } } } }> }).features;
    const garage = features.find((f) => f.properties.name === "1279 GARAGE 37 STREET");
    expect(garage?.properties.addendum.pad.bbl).toBe("3052960043");
    expect(garage?.properties.addendum.pad.bin).not.toBe(trueHit.lot.bin);
  });

  it("AS-4: the nonsense probes are REFUSED — a wrong street and an out-of-range house number surface NO lot", () => {
    const wrongStreet = resolveLotFromGeoSearch(parse(SEARCH_NONEXISTENT_STREET));
    const outOfRange = resolveLotFromGeoSearch(parse(SEARCH_OUT_OF_RANGE_HOUSE));
    expect(wrongStreet.kind).toBe("no_match");
    expect(outOfRange.kind).toBe("no_match");
    expect("lot" in wrongStreet).toBe(false);
    expect("lot" in outOfRange).toBe(false);
  });

  it("AS-4 (never consult match_type/confidence): a top-scored feature on the WRONG street is still refused by equality", () => {
    // A feature scored confidence:1 / match_type:"exact" but on a mismatched
    // street. If the gate ever peeked at those fields it would wrongly promote
    // this — equality must still refuse it.
    const body = {
      type: "FeatureCollection",
      geocoding: { query: { parsed_text: { housenumber: "1279", street: "37 street" } } },
      features: [
        { type: "Feature", properties: { name: "1279 99 STREET", housenumber: "1279", street: "99 STREET", confidence: 1, match_type: "exact", addendum: { pad: { bbl: "3000000001", bin: "3000001", version: "26c" } } } },
      ],
    };
    expect(resolveLotFromGeoSearch(body).kind).toBe("no_match");
  });

  it("AS-5: /autocomplete features (which OMIT confidence/match_type) parse permissively AND still gate", () => {
    // [ORCH-CORRECTED per the packet's fail-closed normalization rule] The corpus
    // §5 query is the abbreviated "1279 37 st"; its parsed street "37 st" is a
    // street-TYPE abbreviation, not the contracted digit-run ordinal fold
    // ("37th" → "37"). Abbreviation expansion (ST→STREET) was never contracted,
    // and unclear cases fail closed to no-match — so the gate's honest outcome
    // for this body is no_match, while the SHAPE still parses without
    // confidence/match_type and suggestions stay permissive (the pick flow and
    // server resolution are unaffected; there is no live promotion path).
    const body = parse(AUTOCOMPLETE_1279_37_ST);
    // Suggestions stay permissive — the autocomplete shape parses as before.
    const suggestions = parseAddressSuggestions(body);
    expect(suggestions?.length ?? 0).toBeGreaterThan(0);
    // The gate tolerates the missing confidence/match_type keys and runs to an
    // honest outcome; the abbreviated input fails closed rather than being
    // loosely matched.
    const resolved = resolveLotFromGeoSearch(body);
    expect(resolved.kind).toBe("no_match");
  });

  it("AS-5b: an /autocomplete-shaped body with an equality-matching parse gates to resolved (missing keys recorded null)", () => {
    // Same corpus §5 body untouched, with the unabbreviated reference parse
    // (the form the corpus's own /search queries demonstrate) supplied through
    // the gate's explicit input parameter, so the equality gate can hold and
    // the absent confidence/match_type keys must be tolerated and recorded
    // null on the resolved lot.
    const resolved = resolveLotFromGeoSearch(parse(AUTOCOMPLETE_1279_37_ST), { houseNumber: "1279", street: "37 street" });
    expect(resolved.kind).toBe("resolved");
    if (resolved.kind !== "resolved") return;
    expect(resolved.lot.bbl).toBe("3052960043");
    expect(resolved.lot.matchType).toBeNull();
    expect(resolved.lot.confidence).toBeNull();
    expect(resolved.lot.padVersion).toBe("26c");
  });
});
