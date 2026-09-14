import { describe, expect, it } from "vitest";
import {
  DATASET_LANDING_PREFIX,
  datasetLandingUrl,
  isValidDatasetId,
} from "@/lib/provenance-link";

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
