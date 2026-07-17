import { describe, expect, it } from "vitest";
import {
  boundedText,
  boundedToken,
  MAX_REFLECTED_TEXT_LENGTH,
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
});
