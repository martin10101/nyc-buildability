import { describe, expect, it } from "vitest";
import {
  boundedText,
  boundedToken,
  boundedZoningDistrict,
  MAX_REFLECTED_TEXT_LENGTH,
  MAX_ZONING_DISTRICT_LENGTH,
  TRUNCATION_MARKER,
} from "@/lib/bounded";

describe("boundedText", () => {
  it("passes ordinary server copy through unchanged", () => {
    expect(boundedText("No PLUTO record exists.", "fallback")).toBe(
      "No PLUTO record exists.",
    );
  });

  it("returns the fallback for non-strings and blank strings", () => {
    expect(boundedText(undefined, "fallback")).toBe("fallback");
    expect(boundedText(42, "fallback")).toBe("fallback");
    expect(boundedText({ msg: "x" }, "fallback")).toBe("fallback");
    expect(boundedText("   ", "fallback")).toBe("fallback");
  });

  it("caps oversized text with an explicit truncation marker", () => {
    const result = boundedText("a".repeat(10_000), "fallback");
    expect(result.length).toBe(MAX_REFLECTED_TEXT_LENGTH + TRUNCATION_MARKER.length);
    expect(result.endsWith(TRUNCATION_MARKER)).toBe(true);
  });

  it("strips control characters and normalizes newlines to spaces", () => {
    const hostile = `line1\nline2\r\n${String.fromCharCode(7)}${String.fromCharCode(27)}[31mred`;
    const result = boundedText(hostile, "fallback");
    expect(result).toBe("line1 line2 [31mred");
  });
});

describe("boundedToken", () => {
  it("keeps well-formed correlation ids", () => {
    expect(boundedToken("cf859f97ab12")).toBe("cf859f97ab12");
    expect(boundedToken("CR-500.no_match")).toBe("CR-500.no_match");
  });

  it("drops characters outside the allowlist", () => {
    expect(boundedToken("abc<script>def")).toBe("abcscriptdef");
    expect(boundedToken("a b\tc")).toBe("abc");
  });

  it("caps token length", () => {
    expect(boundedToken("x".repeat(500))?.length).toBe(64);
  });

  it("returns null for non-strings and for fully-hostile input", () => {
    expect(boundedToken(null)).toBeNull();
    expect(boundedToken(undefined)).toBeNull();
    expect(boundedToken("<<<>>>")).toBeNull();
    expect(boundedToken("")).toBeNull();
  });

  // AS-1 spec-pin: boundedToken's charset is UNCHANGED and still strips the slash
  // of a mixed-use district. This is exactly why recorded zoning must NOT flow
  // through it — it is the "before" half of the DB-036(a) sanitizer-boundary
  // distinction that boundedZoningDistrict below closes.
  it("still strips the '/' in a slash mixed-use district (why boundedZoningDistrict exists)", () => {
    expect(boundedToken("M1-5/R7-2")).toBe("M1-5R7-2");
  });
});

describe("boundedZoningDistrict (DB-036(a) recorded-zoning precondition)", () => {
  it("admits plain, numbered, and suffixed districts byte-exact", () => {
    expect(boundedZoningDistrict("M1-5")).toBe("M1-5");
    expect(boundedZoningDistrict("R7-2")).toBe("R7-2");
    expect(boundedZoningDistrict("R6")).toBe("R6");
    expect(boundedZoningDistrict("R10H")).toBe("R10H");
    expect(boundedZoningDistrict("C6-4")).toBe("C6-4");
  });

  it("PRESERVES the slash of a special mixed-use district (the whole point)", () => {
    expect(boundedZoningDistrict("M1-5/R7-2")).toBe("M1-5/R7-2");
    expect(boundedZoningDistrict("M1-6/R10")).toBe("M1-6/R10");
  });

  it("strips the markup delimiters (< and >) and control/whitespace chars, keeping the district charset — including the '/' the closing tag shares with a mixed-use district", () => {
    // The '<' and '>' delimiters are dropped, so no tag can ever form (and React
    // escapes the reflected text regardless). The '/' of the "</script>" closing
    // tag survives because it is a legitimate mixed-use-district character the
    // charset MUST admit (M1-5/R7-2) — the residue "scriptM1-5/R7-2/script" is
    // inert plain text, never markup. Pinning the exact residue keeps the slash
    // behaviour (and the removal of the delimiters) mutation-sensitive.
    expect(boundedZoningDistrict("<script>M1-5/R7-2</script>")).toBe("scriptM1-5/R7-2/script");
    expect(boundedZoningDistrict(`M1-5${String.fromCharCode(7)}/R7-2`)).toBe("M1-5/R7-2");
    expect(boundedZoningDistrict("M1-5 / R7-2")).toBe("M1-5/R7-2");
  });

  it("length-caps an over-long value to the district bound", () => {
    expect(boundedZoningDistrict("R".repeat(500))?.length).toBe(MAX_ZONING_DISTRICT_LENGTH);
  });

  it("returns null for non-strings and for a fully-hostile or empty value", () => {
    expect(boundedZoningDistrict(null)).toBeNull();
    expect(boundedZoningDistrict(undefined)).toBeNull();
    expect(boundedZoningDistrict(42)).toBeNull();
    expect(boundedZoningDistrict("<<<>>>")).toBeNull();
    expect(boundedZoningDistrict("")).toBeNull();
  });
});
