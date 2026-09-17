import { describe, expect, it } from "vitest";
import {
  DATASET_LANDING_PREFIX,
  ZOLA_LOT_PREFIX,
  datasetLandingUrl,
  isValidDatasetId,
  plutoRecordUrl,
  sourceFactLinks,
  zolaLotUrl,
} from "@/lib/provenance-link";
import type { Identity, SourceFact } from "@/lib/contract";

/** M5-T025 (D-056-R001) — strict dataset-id validation + constant-prefix URL builder. */

describe("isValidDatasetId", () => {
  it("accepts the real PLUTO dataset id (4 lowercase alnum, hyphen, 4 lowercase alnum)", () => {
    expect(isValidDatasetId("64uk-42ks")).toBe(true);
  });

  it("accepts other well-formed 4-4 ids", () => {
    expect(isValidDatasetId("abcd-1234")).toBe(true);
    expect(isValidDatasetId("0000-0000")).toBe(true);
  });

  it("rejects uppercase, wrong length, missing hyphen, and non-alnum characters", () => {
    expect(isValidDatasetId("64UK-42KS")).toBe(false);
    expect(isValidDatasetId("64uk42ks")).toBe(false);
    expect(isValidDatasetId("64u-42ks")).toBe(false);
    expect(isValidDatasetId("64ukx-42ks")).toBe(false);
    expect(isValidDatasetId("64uk-42ks-")).toBe(false);
    expect(isValidDatasetId("64uk_42ks")).toBe(false);
    expect(isValidDatasetId("64uk-42k$")).toBe(false);
  });

  it("rejects a value that merely CONTAINS a valid id as a substring (anchored match only)", () => {
    expect(isValidDatasetId("x64uk-42ks")).toBe(false);
    expect(isValidDatasetId("64uk-42ksx")).toBe(false);
    expect(isValidDatasetId("prefix/64uk-42ks")).toBe(false);
    expect(isValidDatasetId(" 64uk-42ks")).toBe(false);
    expect(isValidDatasetId("64uk-42ks\n")).toBe(false);
  });

  it("rejects a full URL / reflected request_url-shaped string outright", () => {
    expect(
      isValidDatasetId("https://data.cityofnewyork.us/resource/64uk-42ks.json"),
    ).toBe(false);
    expect(isValidDatasetId("https://evil.example.com/64uk-42ks")).toBe(false);
  });

  it("rejects non-strings and absent values", () => {
    expect(isValidDatasetId(undefined)).toBe(false);
    expect(isValidDatasetId(null)).toBe(false);
    expect(isValidDatasetId(42)).toBe(false);
    expect(isValidDatasetId({})).toBe(false);
    expect(isValidDatasetId("")).toBe(false);
  });
});

describe("current official PLUTO record links", () => {
  const sourceId = "nyc-dcp-pluto-soda";
  const datasetId = "64uk-42ks";
  const bbl = "1008350041";
  const record = { source_id: sourceId, dataset_id: datasetId, bbl };
  const source = { source_id: sourceId, dataset_id: datasetId };
  const expected = `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${bbl}`;

  // Shape checks only: these five synthetic tokens make no official-lot claim.
  it.each(["1000010010", "2000010010", "3000010010", "4000010010", "5000010010"])("supports canonical BBL %s across all five boroughs", lot => {
    expect(plutoRecordUrl(sourceId, datasetId, lot)).toBe(`https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${lot}`);
  });

  it.each([
    undefined, null, 1008350041, {}, "", "100835004", "10083500410", "0008350041", "6008350041",
    " 1008350041", "1008350041 ", "1008350041\n", "1008350041\r", "1008350041\r\n",
    "1008350041&$limit=1", "1008350041%0A", "javascript:alert(1)", "１００８３５００４１", "1".repeat(1024),
  ])("rejects malformed or hostile BBL %j without sanitizing it", lot => {
    expect(plutoRecordUrl(sourceId, datasetId, lot)).toBeNull();
  });

  it.each([undefined, null, {}, 42, "", "another-source", "nyc-dcp-pluto-soda\n", "NYC-DCP-PLUTO-SODA"])("rejects unproven source %j", value => {
    expect(plutoRecordUrl(value, datasetId, bbl)).toBeNull();
  });

  it.each([undefined, null, {}, 42, "", "abcd-1234", "64UK-42KS", "64uk-42ks\n", "64uk-42ks\r\n", "64uk-42ks?bbl=1"])("rejects unconfirmed PLUTO dataset %j", value => {
    expect(plutoRecordUrl(sourceId, value, bbl)).toBeNull();
  });

  it.each(["64uk-42ks\n", "64uk-42ks\r", "64uk-42ks\r\n"])("never appends trailing line endings from dataset %j", value => {
    expect(isValidDatasetId(value)).toBe(false);
    expect(datasetLandingUrl(value)).toBeNull();
  });

  it("rejects a wrong lot even when both BBLs are individually valid", () => {
    expect(sourceFactLinks(record, source, { bbl: "3021720001" }).currentRecordUrl).toBeNull();
    expect(sourceFactLinks(record, source, { bbl: "3021720001" }).zolaUrl).toBeNull();
    expect(sourceFactLinks(record, source, { bbl }).currentRecordUrl).toBe(expected);
    expect(sourceFactLinks(record, source, { bbl }).zolaUrl).toBe(`${ZOLA_LOT_PREFIX}${bbl}`);
  });

  it.each([undefined, null, "1008350041\n"])("rejects missing or malformed supplied profile BBL %j", value => {
    expect(sourceFactLinks(record, source, { bbl: value } as Identity).currentRecordUrl).toBeNull();
  });

  it("allows the legacy disclosure to use its captured BBL when no profile identity is supplied", () => {
    expect(sourceFactLinks(record, source).currentRecordUrl).toBe(expected);
  });

  it("uses a missing record dataset only from matching-source reproducibility", () => {
    const missingDataset = { source_id: sourceId, bbl };
    expect(sourceFactLinks(missingDataset, source, { bbl }).currentRecordUrl).toBe(expected);
    const mixed = sourceFactLinks(missingDataset, { ...source, source_id: "another-source" }, { bbl });
    expect(mixed.currentRecordUrl).toBeNull();
    expect(mixed.datasetUrl).toBeNull();
    expect(sourceFactLinks(missingDataset, undefined, { bbl }).currentRecordUrl).toBeNull();
  });

  it("never lends the profile's PLUTO dataset to a non-PLUTO fact", () => {
    const mixed = sourceFactLinks({ source_id: "another-source", bbl }, source, { bbl });
    expect(mixed.currentRecordUrl).toBeNull();
    expect(mixed.datasetUrl).toBeNull();
  });

  it.each([null, "", "bad-dataset", "abcd-1234"])("does not replace an explicitly invalid or different record dataset %j with PLUTO", dataset => {
    const fact = { ...record, dataset_id: dataset } as SourceFact;
    expect(sourceFactLinks(fact, source, { bbl }).currentRecordUrl).toBeNull();
  });

  it("fails closed on same-source dataset conflict and preserves the fact's independent About link", () => {
    const links = sourceFactLinks(record, { ...source, dataset_id: "abcd-1234" }, { bbl });
    expect(links.currentRecordUrl).toBeNull();
    expect(links.zolaUrl).toBeNull();
    expect(links.datasetUrl).toBe("https://data.cityofnewyork.us/d/64uk-42ks");
  });

  it("uses an explicit record dataset independently of another source's profile metadata", () => {
    expect(sourceFactLinks(record, { source_id: "another-source", dataset_id: "abcd-1234" }, { bbl }).currentRecordUrl).toBe(expected);
  });

  it("never uses hostile reflected request URLs from either captured record", () => {
    const fact = { ...record, request_url: "https://evil.example/steal?bbl=3021720001" };
    const metadata = { ...source, request_url: "javascript:alert(1)" };
    const links = sourceFactLinks(fact, metadata, { bbl });
    expect(links.currentRecordUrl).toBe(expected);
    expect(links.datasetUrl).toBe("https://data.cityofnewyork.us/d/64uk-42ks");
  });
});

describe("zolaLotUrl — ZoLa-first human-readable lot page (M5-T032, D-064-R005)", () => {
  it.each(["1000010010", "2000010010", "3000010010", "4000010010", "5000010010"])(
    "builds the constant-prefix ZoLa page for canonical BBL %s across all five boroughs",
    lot => {
      expect(zolaLotUrl(lot)).toBe(`https://zola.planning.nyc.gov/bbl/${lot}`);
      expect(zolaLotUrl(lot)).toBe(`${ZOLA_LOT_PREFIX}${lot}`);
    },
  );

  it.each([
    undefined, null, 1008350041, {}, "", "100835004", "10083500410", "0008350041", "6008350041",
    " 1008350041", "1008350041 ", "1008350041\n", "1008350041\r", "1008350041\r\n",
    "1008350041&$limit=1", "1008350041%0A", "javascript:alert(1)", "１００８３５００４１", "1".repeat(1024),
  ])("returns honest null (never a sanitized or reflected link) for malformed or hostile BBL %j", lot => {
    expect(zolaLotUrl(lot)).toBeNull();
  });

  it("the non-null output is ALWAYS exactly the constant prefix + the validated BBL", () => {
    const url = zolaLotUrl("1008350041");
    expect(url).toBe(`${ZOLA_LOT_PREFIX}1008350041`);
    expect(ZOLA_LOT_PREFIX).toBe("https://zola.planning.nyc.gov/bbl/");
  });

  it("sourceFactLinks exposes the ZoLa link under the SAME guard as the raw record", () => {
    const sourceId = "nyc-dcp-pluto-soda";
    const datasetId = "64uk-42ks";
    const bbl = "1008350041";
    const record = { source_id: sourceId, dataset_id: datasetId, bbl };
    const source = { source_id: sourceId, dataset_id: datasetId };
    // Valid, conflict-free lot identity → ZoLa present alongside the raw record.
    const ok = sourceFactLinks(record, source, { bbl });
    expect(ok.zolaUrl).toBe(`${ZOLA_LOT_PREFIX}${bbl}`);
    expect(ok.currentRecordUrl).not.toBeNull();
    // Non-PLUTO source → no raw record AND no ZoLa link (no borrowed identity).
    expect(sourceFactLinks({ source_id: "another-source", bbl }, source, { bbl }).zolaUrl).toBeNull();
    // Missing profile identity fails closed for both links.
    // [ORCH-CORRECTED per web CI on 3250fbc9] deliberate invalid-shape probe
    // needs the double cast under strict TS.
    expect(sourceFactLinks(record, source, { bbl: null } as unknown as Identity).zolaUrl).toBeNull();
  });
});

describe("datasetLandingUrl", () => {
  it("builds the exact landing-page URL for a valid id: constant prefix + id, nothing else", () => {
    expect(datasetLandingUrl("64uk-42ks")).toBe(
      `${DATASET_LANDING_PREFIX}64uk-42ks`,
    );
    expect(datasetLandingUrl("64uk-42ks")).toBe(
      "https://data.cityofnewyork.us/d/64uk-42ks",
    );
  });

  it("returns null (honest absence, never a guessed link) for an invalid or absent id", () => {
    expect(datasetLandingUrl(undefined)).toBeNull();
    expect(datasetLandingUrl(null)).toBeNull();
    expect(datasetLandingUrl("")).toBeNull();
    expect(datasetLandingUrl("not-a-real-id-format")).toBeNull();
    expect(datasetLandingUrl("64UK-42KS")).toBeNull();
  });

  it("NEGATIVE: a hostile/reflected request_url-shaped value never becomes a usable href, even disguised as an id", () => {
    const hostileValues = [
      "https://data.cityofnewyork.us/d/64uk-42ks/../../evil",
      "javascript:alert(1)",
      "64uk-42ks?evil=1",
      "64uk-42ks#evil",
      "  64uk-42ks  ",
      "<script>64uk-42ks</script>",
    ];
    for (const hostile of hostileValues) {
      const result = datasetLandingUrl(hostile);
      expect(result).toBeNull();
    }
  });

  it("NEGATIVE: the output, when non-null, is ALWAYS exactly the constant prefix + the validated id — never any other string content", () => {
    const url = datasetLandingUrl("64uk-42ks");
    expect(url).not.toBeNull();
    expect(url).toBe(`${DATASET_LANDING_PREFIX}64uk-42ks`);
    // The prefix itself is the one allowlisted constant — no scheme/host
    // variation is possible through this function.
    expect(DATASET_LANDING_PREFIX).toBe("https://data.cityofnewyork.us/d/");
  });
});
