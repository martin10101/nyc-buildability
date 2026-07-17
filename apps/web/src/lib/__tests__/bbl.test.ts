import { describe, expect, it } from "vitest";
import { validateBblInput } from "@/lib/bbl";

/**
 * S3: client-side validation mirrors the server rule (10 digits, borough
 * 1-5) and produces a typed result BEFORE any network call. The deliberate
 * gap (all-zero block/lot -> server 422) is asserted explicitly.
 */
describe("validateBblInput", () => {
  it("accepts a canonical 10-digit BBL", () => {
    expect(validateBblInput("1000010010")).toEqual({
      ok: true,
      canonical: "1000010010",
    });
  });

  it("accepts borough boundary digits 1 and 5", () => {
    expect(validateBblInput("1000010100").ok).toBe(true);
    expect(validateBblInput("5999999999").ok).toBe(true);
  });

  it("trims surrounding whitespace", () => {
    expect(validateBblInput("  1000010010  ")).toEqual({
      ok: true,
      canonical: "1000010010",
    });
  });

  it("rejects empty input", () => {
    const result = validateBblInput("   ");
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.code).toBe("empty");
  });

  it("rejects the dashed component form (server parity: non_numeric)", () => {
    const result = validateBblInput("1-00001-0100");
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.code).toBe("non_numeric");
  });

  it("rejects wrong length", () => {
    const result = validateBblInput("123");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.code).toBe("wrong_length");
      expect(result.message).toContain("3");
    }
  });

  it("rejects borough digits 0 and 6-9", () => {
    for (const bbl of ["0000010100", "6000010100", "9000010100"]) {
      const result = validateBblInput(bbl);
      expect(result.ok).toBe(false);
      if (!result.ok) expect(result.code).toBe("invalid_borough");
    }
  });

  it("DELIBERATELY passes all-zero block through to the server (documented gap)", () => {
    // The server rejects this with 422 invalid_block; the client does not
    // duplicate block/lot semantics so the server 422 path stays reachable
    // (see src/lib/bbl.ts header and scenario S3 server case).
    expect(validateBblInput("1000000000").ok).toBe(true);
  });
});
